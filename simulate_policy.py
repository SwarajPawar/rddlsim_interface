from RDDLEnv import RDDLEnv
import numpy as np
import numpy.ctypeslib as npct
import pickle
import random
from data.metaData import get_feature_names
from data.utils import *

global env



dataset = 'Elevators'
instances = 500000
steps = 6
models = 10
batches = 15
batch_size = 10000





env = get_env(dataset)
sequence_for_policy = get_sequence_for_policy(dataset)

# Get reward by simulating policy in the environment
def get_reward(env, spmn):

	state = env.reset()
	complete_sequence = sequence_for_policy.reset()

	total_reward = 0
	while(True):
		output = best_next_decision(self.spmn, complete_sequence)
		action = output[0][0]
		state, reward, done = env.doAction(action)
		total_reward += reward
		complete_sequence = sequence_for_policy.get_complete_sequence(actiom)

		if done:
			return total_reward



def cb_train():
	

	#return
	global env
	print("\n\n\n\ncb_train:")

	avg_rewards = list()
	reward_dev = list()

	for model in range(models):
		file = open(f"models/{dataset}/spmn_{i}.pkle","rb")
		rspmn = pickle.load(file)
		file.close()


		#Initialize parameters for computing rewards
		total_reward = 0
		reward_batch = list()

		#Get the rewards parallely for each batch
		for y in range(batches):
			rewards = list()
			for z in range(batch_size):
				rewards.append(get_reward(z))
				printProgressBar(y*batch_size + z+1, batches*batch_size, prefix = f'Average Reward Evaluation :', suffix = 'Complete', length = 50)
			reward_batch.append(sum(rewards) / batch_size)
			

		#get the mean and std dev of the rewards    
		avg_rewards = np.mean(reward_batch)
		reward_dev = np.std(reward_batch)



		
		

		instance += [total_reward]

		data.append(instance)
	



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
