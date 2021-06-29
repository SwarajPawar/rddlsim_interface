import os
import torch
import torch.nn as nn
from torch.optim import Adam
import torch.nn.functional as F
from torch.autograd import Variable
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt


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


class ActorCritic:
    def __init__(self, gamma, critic_loss_coef, entropy_coef):
        self.gamma = gamma
        self.entropy_coef = entropy_coef
        self.critic_loss_coef = critic_loss_coef

    def train(self, net, env, net_path, plots_dir, args):
        optimizer = Adam(net.parameters(), lr=args.lr)
        mse_loss = nn.MSELoss.cuda() if args.cuda else nn.MSELoss()
        test_perf_data = [];
        train_perf_data = [];
        best = None;
        n_trajectory_info = []
        for episode in range(1, args.train_episodes + 1):
            net.train()
            done = False;
            total_reward = 0;
            log_probs = [];
            ep_rewards = [];
            critic_info = [];
            ep_obs = [];
            entropies = []
            obs = env.reset();
            while not done:
                ep_obs.append(obs)
                obs = Variable(torch.FloatTensor(obs.tolist())).unsqueeze(0)
                logit, critic = net(obs)
                prob = F.softmax(logit, dim=1)
                log_prob = F.log_softmax(logit, dim=1)
                action = prob.multinomial(num_samples=1).data
                action = int(action[0])
                obs, reward, done, info = env.doAction(action)
                lprob = log_prob[0][action]
                entropy = -(log_prob * prob).sum(1)
                log_probs.append(lprob);
                ep_rewards.append(reward)
                critic_info.append(critic);
                entropies.append(entropy)
                total_reward += reward

            train_perf_data.append(total_reward)
            n_trajectory_info.append((ep_obs, ep_rewards, critic_info, log_probs, entropies))

            if episode % args.batch_size == 0:
                optimizer.zero_grad()
                critic_loss = 0
                for trajectory_info in n_trajectory_info:
                    obs, _rewards, _critic_info, _log_probs, _ = trajectory_info
                    for i, r in enumerate(_rewards):
                        critic = _critic_info[i]
                        if i != len(_rewards) - 1:
                            target_critic = r + Variable(_critic_info[i + 1].data)
                        else:
                            target_critic = Variable(torch.Tensor([[r]]))
                        critic_loss += mse_loss(critic, target_critic)
                critic_loss = critic_loss / args.batch_size
                critic_loss.backward(retain_graph=True)
                optimizer.step()
                optimizer.zero_grad()
                actor_loss = 0
                for trajectory_info in n_trajectory_info:
                    obs, _rewards, _critic_info, _log_probs, _entropies = trajectory_info
                    for i, r in enumerate(_rewards):
                        _, v_state = net(Variable(torch.FloatTensor(obs[i].tolist())).unsqueeze(0))
                        v_state = Variable(v_state.data)
                        if i != len(_rewards) - 1:
                            _, v_next_state = net(Variable(torch.FloatTensor(obs[i + 1].tolist())).unsqueeze(0))
                            v_next_state = Variable(v_next_state.data)
                        else:
                            v_next_state = 0
                        advantage = r + args.gamma * v_next_state - v_state
                        actor_loss += -_log_probs[i] * advantage - args.beta * _entropies[i]
                actor_loss = actor_loss / args.batch_size
                actor_loss.backward()
                optimizer.step()
                n_trajectory_info = []

            # test and log
            if episode % 20 == 0:
                test_reward = self.test(net, env, 10)
                test_perf_data.append(test_reward)
                print('Test:', test_reward)
                if best is None or best <= test_reward:
                    torch.save(net.state_dict(), net_path)
                    best = test_reward
                    print('Model Saved!')

            if episode % 40 == 0:
                plot_data(train_perf_data, test_perf_data, plots_dir)
        return net

    def test(self, net, env, episodes):
        net.eval()
        all_episode_rewards = 0
        for episode in range(episodes):
            done = False
            episode_reward = 0
            obs = env.reset()
            steps = 0
            while not done:
                obs = Variable(torch.FloatTensor(obs.tolist())).unsqueeze(0)
                logit, critic = net(obs)
                prob = F.softmax(logit, dim=1)
                action = int(prob.max(1)[1].data.cpu().numpy()[0])
                obs, reward, done, info = env.doAction(action)
                episode_reward += reward
                steps += 1
            all_episode_rewards += episode_reward
        return all_episode_rewards / episodes

    def predict(self, net, state):
        net.eval()
        obs = state
        obs = Variable(torch.FloatTensor(obs.tolist())).unsqueeze(0)
        logits, critic = net(obs)
        prob = F.softmax(logits, dim=1)
        action = int(prob.max(1)[1].data.cpu().numpy()[0])
        return action
