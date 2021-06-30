from RDDLEnv import RDDLEnv
import numpy as np
import numpy.ctypeslib as npct
import pickle
import random
from data.metaData import get_feature_names

global env

env = RDDLEnv("wildfire_inst_mdp__2")

dataset = 'Elevators'
instances = 500000
steps = 6


'''
	---------------------------------------------------
	Variables and their encoded values:
	---------------------------------------------------



	State:

	Elevator_at_Floor
	0, 1, 2, 3

	Person_Waiting: 
	0: No
	1: Yes

	Person_in_Elevator_Going_Up: 
	0: No
	1: Yes

	Elevator_Direction: 
	0: Down
	1: Up

	Elevator_Closed:
	0: No
	1: Yes

	

	-----------------------------------------------------

	Actions:

	0: Left
	1: Open_Door_Going_Up
	2: Open_Door_Going_Down
	3: Move_Cur_Dir
	4: Close_Door


	----------------------------------------------------


'''

def cb_train():
	

	#return
	global env
	print("\n\n\n\ncb_train:")


	
	def convert_state(state):

		Elevator_at_Floor = list(state[0:3]).index(1)
		Person_Waiting = state[6]
		Person_in_Elevator_Going_Up = state[5]
		Elevator_Direction = state[4]
		Elevator_Closed = state[3]

		return [Elevator_at_Floor, Person_Waiting, Person_in_Elevator_Going_Up, Elevator_Direction, Elevator_Closed]
	

	data = list()


	for i in range(instances):

		if i%10000 ==0:
			print(i)

		state = convert_state(env.reset())
		instance = [i+1]

		instance += state
		total_reward = 0

		for j in range(steps):
			
			action = random.randint(1,4)
			state, reward, done, _ = env.doAction(action)
			total_reward += reward
			
			instance += [action] + convert_state(state)

		instance += [total_reward]

		data.append(instance)
	
	import csv
	fname = f"data/{dataset}_new.tsv"

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
