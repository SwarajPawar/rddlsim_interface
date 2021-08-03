
import numpy as np

'''
	---------------------------------------------------
	Variables and their encoded values:
	---------------------------------------------------



	State:

	Running Systems
	Running_1, Running_2, Running_3, Running_4, Running_5 
	
	0: Not running
	1: Running



	-----------------------------------------------------

	Actions:

	1: Reboot 1
	2: Reboot 2
	3: Reboot 3
	4: Reboot 4
	5: Reboot 5


	----------------------------------------------------


'''

def convert_state_variables_SysAdmin(state):


	Running_1 = state[0]
	Running_2 = state[1]
	Running_3 = state[2]
	Running_4 = state[3]
	Running_5 = state[4]

	Running = [Running_1, Running_2, Running_3, Running_4, Running_5]
	return Running
	


class SysAdmin:

	def __init__(self):
		self.decisions = 4
		self.info_set_size = 5


	def reset(self):
		self.actions = [np.nan for i in range(self.decisions)]
		self.cur_action = 0
		return self.get_sequence()


	def next_complete_sequence(self, action):

		self.actions[self.cur_action] = action

		self.cur_action += 1

		return self.get_sequence()

	def get_sequence(self):
		sequence = list()
		for i in range(self.decisions):
			sequence += [np.nan]*self.info_set_size + [self.actions[i]]

		sequence += [np.nan]*(self.info_set_size + 1)

		return [sequence]