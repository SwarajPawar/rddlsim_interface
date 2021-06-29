import numpy.ctypeslib as npct
from sys import platform
import numpy as np
import argparse
import ctypes
import sys
import os


class RDDLInstance(ctypes.Structure) :
    """ Structure to be filled in by the C++ RDDL Simulator library """
    _fields_ = [
            ('num_state_vars', ctypes.c_int),
            ('num_action_vars', ctypes.c_int),
            ('num_enum_actions', ctypes.c_int),
            ('horizon', ctypes.c_int),
            ('num_rounds', ctypes.c_int),
            ('remaining_time', ctypes.c_double),
            ('initial_state', ctypes.POINTER(ctypes.c_int)),
            ('min_reward', ctypes.c_double),
            ('max_reward', ctypes.c_double)
        ]

    def __init__(self) :
        self.num_state_vars = 0
        self.num_action_vars = 0
        self.num_enum_actions = 0
        self.horizon = 0
        self.num_rounds = 0
        self.remaining_time = 0
        self.initial_state = None

    def __repr__(self) :
        return '\nState variables     {} \nAction variables    {} \nEnumerated Actions  {} \nHorizon             {} \nInitial State       {} \nReward-Range        [{}, {}]'.format(
                self.num_state_vars, self.num_action_vars, self.num_enum_actions, self.horizon, npct.as_array(self.initial_state, (self.num_state_vars, )), self.min_reward, self.max_reward
        )


class RDDLEnv():
    """ RDDL Environment """
    def __init__(self, instance):
        if platform == "linux" or platform == "linux2":
            self.rddlsim = ctypes.CDLL(os.path.join(os.getcwd(), "clibxx.so"))
        elif platform == "darwin" :
            self.rddlsim = ctypes.CDLL(os.path.join(os.getcwd(), "clibxx.dylib"))
        else :
            print('Only Linux and OSX are supported'); sys.exit()
        self.problem = RDDLInstance()
        self.instance = instance
        self.rddlsim.doAction.restype = ctypes.c_double
        self.CB1 = ctypes.CFUNCTYPE(None)
        self.CB2 = ctypes.CFUNCTYPE(None)
        self.CB3 = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_double))


    def setEnvVariables(self) :
        """ Set Environment variables from the RDDLInstance object """
        self.num_state_vars = self.problem.num_state_vars
        self.num_action_vars = self.problem.num_action_vars
        self.num_enum_actions = self.problem.num_enum_actions
        self.horizon = self.problem.horizon
        self.num_rounds = self.problem.num_rounds
        self.remaining_time = self.problem.remaining_time
        self.initial_state = np.array(npct.as_array(self.problem.initial_state, (self.num_state_vars, )), dtype = np.int8)
        self.state = np.array(self.initial_state, dtype = np.int8)
        self.min_reward = self.problem.min_reward
        self.max_reward = self.problem.max_reward
        self.tstep = 0
        self.done = False
        self.reward = 0
        print(self.problem)


    def connectToServer(self, host, port, cbtrain, cbtest):
        """ Invoke the C++ RDDL Simulator library with appropriate callback functions """
        self.rddlsim.connectToServer((self.instance).encode(), host.encode(), int(port), ctypes.byref(self.problem), self.CB1(self.setEnvVariables), self.CB2(cbtrain), self.CB3(cbtest))


    def reset(self) :
        """ Reset Environment """
        self.state = self.initial_state
        self.done = False
        self.tstep = 0
        self.reward = 0
        return self.state


    def doAction(self, action):
        """ Do the action """
        s = self.state
        ss = s.tolist()
        sss = (ctypes.c_double * len(ss))(*ss)
        aref = ctypes.c_int(action)
        reward = self.rddlsim.doAction(sss, len(ss), ctypes.byref(aref))
        action = aref.value
        self.state = np.array(sss, dtype=np.int8)
        self.reward = self.reward + reward
        self.tstep = self.tstep + 1
        if self.tstep >= self.horizon:
            self.done = True
        return self.state, reward, self.done, {}
