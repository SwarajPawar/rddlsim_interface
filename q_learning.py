# Dependencies ##################################################################
import os
import sys
import math
import argparse
import random
import numpy as np
import numpy.ctypeslib as npct
import traceback
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tools import ensure_directory_exists

# RDDL
from RDDLEnv import RDDLEnv

# Py-torch 0.3 dependencies
import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.nn.functional as F
from torch.optim import Adam

# #################################################################################


# globals
global qnet, env
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


# class QNet(nn.Module):
#     """ Create network with 0 hidden layers """
#
#     def __init__(self):
#         super(QNet, self).__init__()
#         global env
#
#         # q-values layer
#         self.final = nn.Linear(env.num_state_vars, env.num_enum_actions)
#
#     def forward(self, input):
#         return self.final(input)


def init_model():
    """Initializes the model and other configuration"""
    global qnet, env, model_path, plots_dir
    qnet = QNet()
    result_dir = ensure_directory_exists(os.path.join(os.getcwd(), 'results', args.inst.split('_inst')[0]))
    env_dir = os.path.join(result_dir, args.inst,
                           'QLearning' + ('_' if len(args.path_suffix) > 0 else '') + args.path_suffix)
    env_dir = ensure_directory_exists(env_dir)
    model_path = os.path.join(env_dir, args.inst + '_model.p')
    plots_dir = ensure_directory_exists(os.path.join(env_dir, 'Plots'))
    if not args.scratch and os.path.exists(model_path):
        print('Loading Existing Model...')
        qnet.load_state_dict(torch.load(model_path))


def cb_train():
    """Training : initialize and train the model (Callback function)"""
    try:
        init_model()
        q_learning()
    except KeyboardInterrupt as ki:
        print(''.join(traceback.format_exception(etype=type(ki), value=ki, tb=ki.__traceback__)))
        response = input('Press "Enter" to continue to Evaluation Phase or "q" to Quit: ')
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
    state = Variable(torch.FloatTensor(state.tolist())).unsqueeze(0)
    qvalues = qnet(state)
    action = np.argmax(qvalues[0].data.numpy())
    return action


def q_learning():
    """ train network using qlearning """
    global qnet, env
    optim = Adam(qnet.parameters(), lr=args.lr)
    loss_fn = nn.MSELoss()

    # used for plotting and saving the best model
    train_perf_data, test_perf_data = [], []
    best = None

    for e in range(args.train_episodes):
        qnet.train()  # important to set when using Batch Normalization and/or Dropout

        state = env.reset()
        done = False  # marks end of the episode

        ep_reward = 0
        while not done:
            _state = Variable(torch.FloatTensor(state.tolist())).unsqueeze(0)
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

            # estimate target
            _next_state = Variable(torch.FloatTensor(next_state.tolist())).unsqueeze(0)
            next_state_qvalues = qnet(_next_state)
            expected_state_qvalues = reward + args.gamma * np.max(next_state_qvalues.data.numpy())

            # compute loss and update network
            optim.zero_grad()
            loss = loss_fn(state_qvalues[0][action], Variable(torch.FloatTensor([expected_state_qvalues])))
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
                plot_data(train_perf_data, test_perf_data, plots_dir)

    plot_data(train_perf_data, test_perf_data, plots_dir)
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
            state = Variable(torch.FloatTensor(state.tolist())).unsqueeze(0)
            state_qvalues = net(state)
            action = np.argmax(state_qvalues[0].data.numpy())  # greedy policy
            state, reward, done, info = env.doAction(action)
            episode_reward += reward
            steps += 1
        all_episode_rewards += episode_reward
    return round(all_episode_rewards / episodes, 3)


def plot_data(train_data, test_data, plots_dir_path):
    """ Plot Train and Test Performance data"""

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
    parser = argparse.ArgumentParser(description=' Q-Learning')
    parser.add_argument('--gamma', type=float, default=0.99, help='discount factor')
    parser.add_argument('--train_episodes', type=int, default=1000,
                        help='total no. of training episodes (default : 1000)')
    parser.add_argument('--test_episodes', type=int, default=30, help='total no. of test episodes (default : 30)')
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
    parser.add_argument('--test', action='store_true', default=False,
                        help='Performs only testing over RDDL server (default: False)')
    parser.add_argument('--path_suffix', default='',
                        help='Adds given suffix to the results directory (deafult: '' // empty)')
    parser.add_argument('--norm_reward', action='store_true', default=False,
                        help='Normalize rewards while training (default: False)')
    args = parser.parse_args()

    random.seed(0)
    env = RDDLEnv(args.inst)  # initialize environment - call functions from RDDLEnv class

    if not args.test:
        print('Training the Model...')
        env.connectToServer(args.host, args.port, cb_train, cb_test)
    else:
        print('Testing the Model...')
        env.connectToServer(args.host, args.port, init_model, cb_test)
