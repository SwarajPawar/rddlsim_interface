from RDDLEnv import RDDLEnv
import numpy as np
import numpy.ctypeslib as npct
import pickle
import random
from data.metaData import get_feature_names
from data.utils import *
#from spn.algorithms.Anytime_MEU import best_next_decision
from spn.algorithms.MEU import best_next_decision, meu
from spn.io.ProgressBar import printProgressBar
from spn.io.Graphics import plot_spn
from spn.data.domain_stats import get_original_stats, get_optimal_meu, get_random_policy_reward
from spn.data.metaData import get_partial_order, get_utilityNode, get_decNode, get_feature_names, get_feature_labels
import matplotlib.pyplot as plt
import multiprocessing
from os import path as pth
import sys, os

global env


dataset = 'CrossingTraffic'
steps = 5
models = 1
batches = 1
batch_size = 1
interval_size = 1



	
file = open(f"models/{dataset}/spmn_original.pkle","rb")
spmn = pickle.load(file)
file.close()

partial_order = get_partial_order(dataset)
utility_node = get_utilityNode(dataset)
decision_nodes = get_decNode(dataset)
feature_names = get_feature_names(dataset)
feature_labels = get_feature_labels(dataset)
	
test_data = [[np.nan]*len(feature_names)]
plot_spn(spmn, f'output/{dataset}/spmn.pdf', feature_labels=feature_labels)
#m = meu(spmn, test_data)
#print(m)
