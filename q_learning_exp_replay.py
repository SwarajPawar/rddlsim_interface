# Dependencies ##################################################################
import os
import sys
import math
import argparse
import random
import numpy as np
import numpy.ctypeslib as npct
from collections import namedtuple
import matplotlib
import traceback

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tools import ensure_directory_exists

# RDDL
from RDDLEnv import RDDLEnv

# Py-torch 0.3.1 dependencies
import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.nn.functional as F
from torch.optim import Adam

# #################################################################################


# globals
global qnet, target_net, env
Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward'))
hidden_unit_factor = 3


class QNet(nn.Module):
    """ Create network with 2 hidden layers """

    def __init__(self):
        super(QNet, self).__init__()
        global env

        # hidden layers
        self.h1 = nn.Linear(env.num_state_vars, env.num_state_vars * hidden_unit_factor)
        self.h2 = nn.Linear(env.num_state_vars * hidden_unit_factor, env.num_state_vars * hidden_unit_factor)

        # q-values layer
        self.final = nn.Linear(env.num_state_vars * hidden_unit_factor, env.num_enum_actions)

    def forward(self, input):
        x = F.relu(self.h1(input))
        x = F.relu(self.h2(x))
        return self.final(x)


def init_model():
    """Initializes the model and other configuration"""
    global qnet, target_net, env, model_path, plots_dir
    qnet = QNet()
    target_net = QNet()
    result_dir = ensure_directory_exists(os.path.join(os.getcwd(), 'results', args.inst.split('_inst')[0]))
    env_dir = os.path.join(result_dir, args.inst,
                           'ExpReplay_QLearning' + ('_' if len(args.path_suffix) > 0 else '') + args.path_suffix)
    env_dir = ensure_directory_exists(env_dir)
    model_path = os.path.join(env_dir, args.inst + '_model.p')
    plots_dir = ensure_directory_exists(os.path.join(env_dir, 'Plots'))
    if not args.scratch and os.path.exists(model_path):
        print('Loading Existing Model...')
        qnet.load_state_dict(torch.load(model_path))
        target_net.load_state_dict(torch.load(model_path))


class ReplayMemory(object):
    """
    Reference: https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html
    """

    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.position = 0

    def push(self, *args):
        """Saves a transition."""
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        self.memory[self.position] = Transition(*args)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)


def cb_train():
    """Training : initialize and train the model (Callback function)"""
    try:
        init_model()
        q_learning()
    except KeyboardInterrupt as ki:
        print(''.join(traceback.format_exception(etype=type(ki), value=ki, tb=ki.__traceback__)))
        response = input('Press Enter to continue to Evaluation Phase or "q" to Quit')
        if response == 'q':
            sys.exit(0)
    except Exception as ex:
        print(''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__)))
        sys.exit(0)


def cb_test(state):
    """ Testing : returns predicted action for the given state (Callback function) """
    global qnet, env
    qnet.eval()
    state = npct.as_array(state, (env.num_state_vars,))
    state = Variable(torch.Tensor(state.tolist())).unsqueeze(0)
    qvalues = qnet(state)
    action = np.argmax(qvalues[0].data.numpy())
    return action


def q_learning():
    """ train network using qlearning """
    global qnet, target_net, env
    optim = Adam(qnet.parameters(), lr=args.lr)
    loss_fn = nn.MSELoss()

    # used for plotting and saving the best model
    loss_data, train_perf_data, test_perf_data = [], [], []
    best = None
    memory = ReplayMemory(args.capacity)

    for e in range(args.train_episodes):

        state = env.reset()
        done = False  # marks end of the episode

        ep_reward = 0
        while not done:
            qnet.train()  # important to set when using Batch Normalization and/or Dropout
            _state = Variable(torch.Tensor(state.tolist())).unsqueeze(0)
            state_qvalues = qnet(_state)

            # (exploit-explore) strategy
            sample = random.random()
            if not args.eps_decay:
                eps_threshold = args.eps  # constant epsilon approach
            else:
                eps_threshold = args.eps + (0.9 - args.eps) * math.exp(-1. * e / 200)  # epsilon-decay  approach

            if sample < eps_threshold:
                action = np.random.randint(env.num_enum_actions)
            else:
                action = np.argmax(state_qvalues[0].data)
            next_state, reward, done, _ = env.doAction(action)
            ep_reward += reward

            # Reward Normalization
            if args.norm_reward:
                # Unit Normalize reward by range
                # reward = (reward - env.min_reward) / (env.max_reward - env.min_reward)

                # Normalization by range
                reward /= (env.max_reward - env.min_reward)

            # experience-replay
            memory.push(state.tolist(), [action], next_state.tolist(), reward)
            if len(memory) >= args.batch_size:
                transitions = memory.sample(args.batch_size)
                batch = Transition(*zip(*transitions))

                state_batch = Variable(torch.Tensor(list(batch.state)), requires_grad=True)
                action_batch = Variable(torch.LongTensor(list(batch.action)))
                reward_batch = Variable(torch.Tensor(list(batch.reward)))
                next_state_batch = Variable(torch.Tensor(list(batch.next_state)))

                state_action_values = qnet(state_batch)
                state_action_values = state_action_values.gather(1, action_batch)  # get q-values of selected action
                next_state_action_values = target_net(next_state_batch).max(1)[0].detach()
                expected_state_action_values = (next_state_action_values * args.gamma) + reward_batch

                # estimate target
                loss = loss_fn(state_action_values, expected_state_action_values.unsqueeze(1))
                loss_data.append(loss.data[0])
                optim.zero_grad()
                loss.backward()
                optim.step()

            state = next_state

        # test, log and plot
        train_perf_data.append(ep_reward)
        if e % 20 == 0:
            test_reward = test(qnet, env, args.test_episodes)
            test_perf_data.append(test_reward)
            print('Train Episode:', e, 'Test Performance:', test_reward)
            if best is None or best <= test_reward:
                torch.save(qnet.state_dict(), model_path)
                best = test_reward
                print('Model Saved!')
            if len(test_perf_data) % 10 == 0:
                plot_data(loss_data, train_perf_data, test_perf_data, plots_dir)

        # Update the target network
        if e % args.target_update == 0:
            target_net.load_state_dict(qnet.state_dict())

    plot_data(loss_data, train_perf_data, test_perf_data, plots_dir)
    qnet.load_state_dict(torch.load(model_path))  # load best model so it is ready for use in testing


def test(net, env, episodes):
    """ Test the model using deterministic greedy policy"""
    net.eval()  # important to set when using Batch Normalization and/or Dropout
    all_episode_rewards = 0
    for _ in range(episodes):
        done = False
        episode_reward = 0
        state = env.reset()
        steps = 0
        while not done:
            state = Variable(torch.Tensor(state.tolist())).unsqueeze(0)
            state_qvalues = net(state)
            action = np.argmax(state_qvalues[0].data.numpy())  # greedy policy
            state, reward, done, info = env.doAction(action)
            episode_reward += reward
            steps += 1
        all_episode_rewards += episode_reward
    return round(all_episode_rewards / episodes, 3)


def plot_data(loss_data, train_data, test_data, plots_dir_path):
    """ Plot Train and Test Performance data"""

    title = 'Loss_vs_Batch'
    plt.plot(loss_data)
    plt.grid(True)
    plt.title(title + '(best: ' + str(min(loss_data)) + ')')
    plt.ylabel('Loss')
    plt.xlabel('Batch')
    plt.savefig(os.path.join(plots_dir_path, title + ".png"))
    plt.clf()

    title = 'Train_Performance'
    plt.plot(train_data)
    plt.grid(True)
    plt.title(title + '(best: ' + str(max(train_data)) + ')')
    plt.ylabel('Reward')
    plt.xlabel('Episode')
    plt.savefig(os.path.join(plots_dir_path, title + ".png"))
    plt.clf()

    title = 'Test_Performance'
    plt.plot(test_data)
    plt.grid(True)
    plt.title(title + '(best: ' + str(max(test_data)) + ')')
    plt.ylabel('Reward')
    plt.xlabel('Episode( X 20)')
    plt.savefig(os.path.join(plots_dir_path, title + ".png"))
    plt.clf()

    print('Plot Saved!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Q- Learning with Experiance Replay')
    parser.add_argument('--gamma', type=float, default=0.99, help='discount factor')
    parser.add_argument('--train_episodes', type=int, default=1000,
                        help='total no. of training episodes (default : 1000)')
    parser.add_argument('--test_episodes', type=int, default=30, help='total no. of training episodes (default : 1000)')
    parser.add_argument('--eps', type=float, default=0.3, help='exploration prob. rate (default : 0.3)')
    parser.add_argument('--eps_decay', action='store_true', default=False,
                        help='Turns on decay of exploration rate (default: False)')
    parser.add_argument('--lr', type=float, default=0.0001, help='learning rate (default: 0.0001)')
    parser.add_argument('--inst', default='wildfire_inst_mdp__1',
                        help='problem instance (environment) (default: wildfire_inst_mdp__1)')
    parser.add_argument('--scratch', action='store_true', default=False,
                        help='train model from scratch (default: False)')
    parser.add_argument('--host', default='localhost', help='rddl-server host address (default: localhost)')
    parser.add_argument('--port', default=2323, help='rddl-server port number (default: 2323)')
    parser.add_argument('--batch_size', type=int, default=32,
                        help='Sample Batch Size for Experiance Replay (default: 32)')
    parser.add_argument('--capacity', type=int, default=100, help='Capacity of Experiance Replay (default : 100)')
    parser.add_argument('--test', action='store_true', default=False,
                        help='Performs only testing over RDDL server (default: False)')
    parser.add_argument('--path_suffix', default='',
                        help='Adds given suffix to the results directory (deafult: '' // empty)')
    parser.add_argument('--norm_reward', action='store_true', default=False,
                        help='Normalize rewards while training (default: False)')
    parser.add_argument('--target_update', default=1, type=int,
                        help='Episode interval after which the target network is updated(default : 1)')
    args = parser.parse_args()

    random.seed(0)
    env = RDDLEnv(args.inst)  # initialize environment - call functions from RDDLEnv class

    if not args.test:
        print('Training the Model...')
        env.connectToServer(args.host, args.port, cb_train, cb_test)
    else:
        print('Testing the Model...')
        env.connectToServer(args.host, args.port, init_model, cb_test)
