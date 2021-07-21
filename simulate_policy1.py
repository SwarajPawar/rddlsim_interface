from RDDLEnv import RDDLEnv
import numpy as np
import numpy.ctypeslib as npct
import pickle
import random
from data.metaData import get_feature_names
from data.utils import *
from spn.algorithms.MEU import best_next_decision
from spn.io.ProgressBar import printProgressBar
from spn.data.domain_stats import get_original_stats, get_optimal_meu, get_random_policy_reward
import matplotlib.pyplot as plt
import multiprocessing
from os import path as pth
import sys, os

global env


'''
dataset = 'Elevators'
steps = 6
models = 5
batches = 10
batch_size = 5000
'''


dataset = 'Navigation'
steps = 5
models = 1
batches = 1
batch_size = 500000
interval_size = 50
'''
batch_size = 500
interval_size = 50
'''

path = 'output'



env = get_env(dataset)
sequence_for_policy = get_sequence_for_policy(dataset)
get_state = get_state_for_dataset(dataset)

# Get reward by simulating policy in the environment
def get_reward(spmn):

	global env

	actions = [1,3,3,4,4]

	state = env.reset()
	complete_sequence = sequence_for_policy.reset()
	#print(complete_sequence)
	total_reward = 0
	i = 0
	for i in range(steps):
		print(get_state(state))
		action = actions[i]
		state, reward, done, _ = env.doAction(action)
		print(reward)
		total_reward += reward
		complete_sequence = sequence_for_policy.next_complete_sequence(action)
	return total_reward



def cb_train():
	

	#return
	global env
	print("\n\n\n\ncb_train:")

	avg_rewards = list()
	reward_dev = list()

	#Create output directory
	if not pth.exists(f"{path}/{dataset}"):
		try:
			os.makedirs(f"{path}/{dataset}")
		except OSError:
			print ("Creation of the directory %s failed" % f"{path}/{dataset}")
			sys.exit()

	f = open(f"{path}/{dataset}/stats.txt", "w")
	f.close()

	#Get Baseline stats
	#original_stats = get_original_stats(dataset)
	#optimal_meu = get_optimal_meu(dataset)
	random_policy_reward = get_random_policy_reward(dataset)


	for model in range(models):
		file = open(f"models/{dataset}/spmn_{model+1}.pkle","rb")
		spmn = pickle.load(file)
		file.close()


		#Initialize parameters for computing rewards
		total_reward = 0
		reward_batch = list()

		#pool = multiprocessing.Pool()

		#Get the rewards parallely for each batch
		intervals = int(batch_size/interval_size)
		for x in range(batches):
			rewards = list()
			for y in range(batch_size):
				print("\n\n")
				rewards.append(get_reward(spmn))
				
			reward_batch.append(sum(rewards) / batch_size)
			

		#get the mean and std dev of the rewards    
		avg_rewards = np.mean(reward_batch)
		reward_dev = np.std(reward_batch)

		print(f"\n\nModel {model}")
		print(f"\tAverage Reward : {avg_rewards}")
		print(f"\tReward Deviation : {reward_dev}")


		#Save the reward stats
		f = open(f"{path}/{dataset}/stats.txt", "a")
		f.write(f"\n\tAverage Reward : {avg_rewards}")
		f.write(f"\n\tReward Deviation : {reward_dev}")
		f.close()

		#Plot the reward
		plt.close()

		rand_reward = np.array([random_policy_reward["reward"]]*len(avg_rewards))
		dev = np.array([random_policy_reward["dev"]]*len(avg_rewards))
		plt.fill_between(np.arange(len(avg_rewards)), rand_reward-dev, rand_reward+dev, alpha=0.1, color="lightgrey")
		plt.plot(rand_reward, linestyle="dashed", color ="grey", label="Random Policy")

		'''
		original_reward = np.array([original_stats["reward"]]*len(avg_rewards))
		dev = np.array([original_stats["dev"]]*len(avg_rewards))
		plt.fill_between(np.arange(len(avg_rewards)), original_reward-dev, original_reward+dev, alpha=0.3, color="red")
		plt.plot([optimal_meu]*len(avg_rewards), linewidth=3, color ="lime", label="Optimal MEU")
		plt.plot(original_reward, linestyle="dashed", color ="red", label="LearnSPMN")
		'''
		plt.errorbar(np.arange(len(avg_rewards)), avg_rewards, yerr=reward_dev, marker="o", label="Anytime")
		plt.title(f"{dataset} Average Rewards")
		plt.legend()
		plt.savefig(f"{plot_path}/rewards.png", dpi=100)
		plt.close()
		
	



def cb_test(state):
    exit(1)
    
    global env
    state = npct.as_array(state, (env.num_state_vars,))
    print("\n\nstate:\t"+str(state)+"\n\n")
    action = np.random.randint(5)
    print("action:\t"+str(action))
    return action
    

env.connectToServer("localhost", 2323, cb_train, cb_test)

#-7.8615
#-7.3568