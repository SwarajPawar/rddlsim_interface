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
steps = 5
models = 5
batches = 10
batch_size = 1000
interval_size = 250
'''


dataset = 'Navigation'
steps = 5
batches = 10
batch_size = 1000
interval_size = 250


path = 'output'



env = get_env(dataset)
sequence_for_policy = get_sequence_for_policy(dataset)

# Get reward by simulating policy in the environment
def get_reward(spmn):

	global env

	state = env.reset()
	complete_sequence = sequence_for_policy.reset()
	total_reward = 0
	for i in range(steps):
		output = best_next_decision(spmn, complete_sequence)
		action = int(output[0][0])
		state, reward, done, _ = env.doAction(action)
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

	

	
	file = open(f"models/{dataset}/spmn_original.pkle","rb")
	spmn = pickle.load(file)
	file.close()


	#Initialize parameters for computing rewards
	total_reward = 0
	reward_batch = list()

	pool = multiprocessing.Pool()

	#Get the rewards parallely for each batch
	intervals = int(batch_size/interval_size)
	for x in range(batches):
		rewards = list()
		for y in range(batch_size):
			rewards.append(get_reward(spmn))
			printProgressBar(x*batch_size + y+1, batches*batch_size, prefix = f'Average Reward Evaluation :', suffix = 'Complete', length = 50)
		reward_batch.append(sum(rewards) / batch_size)
		

	#get the mean and std dev of the rewards    
	avg_rewards = np.mean(reward_batch)
	reward_dev = np.std(reward_batch)


	print(f"\n\nModel LearnSPMN")
	print(f"\tAverage Reward : {avg_rewards}")
	print(f"\tReward Deviation : {reward_dev}")


	#Save the reward stats
	f = open(f"{path}/{dataset}/stats_original.txt", "w")
	f.write(f"\n\tAverage Reward : {avg_rewards}")
	f.write(f"\n\tReward Deviation : {reward_dev}")
	f.close()

		
	



def cb_test(state):
	exit(1)
	
	global env
	state = npct.as_array(state, (env.num_state_vars,))
	print("\n\nstate:\t"+str(state)+"\n\n")
	action = np.random.randint(5)
	print("action:\t"+str(action))
	return action
	

env.connectToServer("localhost", 2323, cb_train, cb_test)


