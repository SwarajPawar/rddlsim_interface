import argparse
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from tools import ensure_directory_exists, weights_init, normalized_columns_initializer
from a2c import ActorCritic
from RDDLEnv import RDDLEnv
import numpy.ctypeslib as npct
import pwd
import sys
import traceback

global ac_net, ac_algo, _env


class A2CNet(nn.Module):
    def __init__(self, input_size, actions):
        super(A2CNet, self).__init__()
        self.fc0 = nn.Linear(input_size, 256)
        self.fc1 = nn.Linear(256, 64)
        self.actor_linear = nn.Linear(64, actions)
        self.critic_linear = nn.Linear(64, 1)

        self.apply(weights_init)
        self.actor_linear.weight.data = normalized_columns_initializer(self.actor_linear.weight.data, 0.01)
        self.actor_linear.bias.data.fill_(0)
        self.critic_linear.weight.data.fill_(0)
        self.critic_linear.bias.data.fill_(0)

    def forward(self, input):
        x = F.relu(self.fc0(input))
        x = F.relu(self.fc1(x))
        return self.actor_linear(x), self.critic_linear(x)


def cbtest(state):
    """Returns the greedy deterministic action for the given state"""
    global ac_net, ac_algo, _env
    state = npct.as_array(state, (_env.num_state_vars,))
    ac_net.eval()
    action = ac_algo.predict(ac_net, state)
    return action


def cbtrain():
    global ac_net, ac_algo, _env
    try:
        ac_net = A2CNet(_env.num_state_vars, _env.num_enum_actions)
        homedir = pwd.getpwuid(os.getuid()).pw_dir
        net_path = os.path.join(homedir, args.env + '_a2cmodel.p')
        plots_dir = ensure_directory_exists(os.path.join(homedir, args.env + '_plots'))
        if args.cuda:
            ac_net = ac_net.cuda()
        if os.path.exists(net_path) and not args.scratch:
            ac_net.load_state_dict(torch.load(net_path))
        ac_algo = ActorCritic(args.gamma, args.critic_loss_coef, args.entropy_coef)
        ac_net.train()
        ac_net = ac_algo.train(ac_net, _env, net_path, plots_dir, args)
        ac_net.load_state_dict(torch.load(net_path))
    except KeyboardInterrupt as ki:
        print(''.join(traceback.format_exception(etype=type(ki), value=ki, tb=ki.__traceback__)))
        response = input('Press "Enter" to continue to Evaluation Phase or "q" to Quit: ')
        if response == 'q':
            sys.exit(0)
    except Exception as ex:
        print(''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__)))
        sys.exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A2C')
    parser.add_argument('--gamma', type=float, default=0.99, metavar='G', help='discount factor (default: 0.99)')
    parser.add_argument('--entropy-coef', type=float, default=0.3, help='entropy term coefficient (default: 0.01)')
    parser.add_argument('--critic-loss-coef', type=float, default=1, help='value loss coefficient (default: 0.5)')
    parser.add_argument('--seed', type=int, default=10, metavar='N', help='random seed (default: 10)')
    parser.add_argument('--batch_size', type=int, default=10, help='Batch Size(No. of Episodes) for Training')
    parser.add_argument('--beta', type=float, default=0.01, help='Rate for Entropy')
    parser.add_argument('--log-interval', type=int, default=5,
                        help='interval between training status logs (default: 5)')
    parser.add_argument('--no_cuda', action='store_true', default=True, help='Disables Cuda Usage')
    parser.add_argument('--train', action='store_true', default=True, help='Train the network')
    parser.add_argument('--test', action='store_true', default=True, help='Test the network')
    parser.add_argument('--train_episodes', type=int, default=200, help='Episode count for training')
    parser.add_argument('--test_episodes', type=int, default=100, help='Episode count for testing')
    parser.add_argument('--lr', type=float, default=0.01, help='Learning Rate for Training (Adam Optimizer)')
    parser.add_argument('--scratch', action='store_true', default=False,
                        help='Train the network from scratch ( or Does not load pre-trained model)')
    parser.add_argument('--env', default=None, metavar='ENV', help='environment to train')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default=2323)

    args = parser.parse_args()
    args.cuda = torch.cuda.is_available() and (not args.no_cuda)
    vis = None

    _env = RDDLEnv(args.env)
    _env.connectToServer(args.host, args.port, cbtrain, cbtest)
