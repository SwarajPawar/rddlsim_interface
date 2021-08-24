
import numpy as np

'''
	---------------------------------------------------
	Variables and their encoded values:
	---------------------------------------------------



	State:

	Running Systems
	
	0: Not running
	1: Running



	-----------------------------------------------------

	Actions:

	1: Reboot 1
	2: Reboot 2
	3: Reboot 3
	4: Reboot 4
	5: Reboot 5
	6: Reboot 6
	7: Reboot 7
	8: Reboot 8
	9: Reboot 9
	10: Reboot 10


	----------------------------------------------------


'''

def convert_state_variables_SysAdmin(state):

	Running = list(state)
	return Running
	


class SysAdmin:

	def __init__(self):
		self.decisions = 3
		self.info_set_size = 10


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