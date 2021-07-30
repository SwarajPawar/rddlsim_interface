from RDDLEnv import RDDLEnv
import numpy as np
import numpy.ctypeslib as npct
import pickle
import random
from data.metaData import get_feature_names
from data.utils import *

global env


'''
dataset = 'Navigation'
instances = 500000
steps = 5
n_actions = 4

dataset = 'Elevators'
instances = 500000
steps = 6
n_actions = 4
'''

dataset = 'GameOfLife'
instances = 500000
steps = 5
n_actions = 6

env = get_env(dataset)
convert_state = get_state_for_dataset(dataset)





def cb_train():
	

	#return
	global env
	print("\n\n\n\ncb_train:")

	

	data = list()


	for i in range(instances):

		if i%10000 ==0:
			print(i)

		state = convert_state(env.reset())
		instance = [i+1]

		instance += state
		total_reward = 0
		for j in range(steps):
			
			action = random.randint(1,n_actions)
			state, reward, done, _ = env.doAction(action)
			total_reward += reward
			instance += [action] + convert_state(state)

		instance += [total_reward]

		data.append(instance)
	
	import csv
	fname = f"data/{dataset}/{dataset}.tsv"

	with open(fname, 'w') as file:
		wr = csv.writer(file,delimiter='\t')
		columns = ["ids"] + get_feature_names(dataset)
		wr.writerow(columns)
		for row in data:
				wr.writerow(row)



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
