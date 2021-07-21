"""
Created on March 21, 2018

@author: Alejandro Molina
"""
import logging
import numpy as np
from scipy.special import logsumexp

from spn.structure.Base import Product, Sum, eval_spn_bottom_up, Max

from spn.structure.Base import InterfaceSwitch

logger = logging.getLogger(__name__)

EPSILON = np.finfo(float).eps


def leaf_marginalized_likelihood(node, data=None, dtype=np.float64):
	assert len(node.scope) == 1, node.scope
	probs = np.ones((data.shape[0], 1), dtype=dtype)
	assert data.shape[1] >= 1
	data = data[:, node.scope]
	marg_ids = np.isnan(data)
	observations = data[~marg_ids]
	assert len(observations.shape) == 1, observations.shape
	return probs, marg_ids, observations


def prod_log_likelihood(node, children, data=None, dtype=np.float64):
	llchildren = np.concatenate(children, axis=1)
	assert llchildren.dtype == dtype
	pll = np.sum(llchildren, axis=1).reshape(-1, 1)
	pll[np.isinf(pll)] = np.finfo(pll.dtype).min
	return pll


def prod_likelihood(node, children, data=None, dtype=np.float64):
	if None in children:
		return None
	llchildren = np.concatenate(children, axis=1)
	assert llchildren.dtype == dtype
	return np.prod(llchildren, axis=1).reshape(-1, 1)


def max_log_likelihood(node, children, data=None, dtype=np.float64):
	llchildren = np.concatenate(children, axis=1)
	assert llchildren.dtype == dtype
	if llchildren.shape[1] == 1:  # if only one child, then it is max.
		return llchildren
	assert data is not None, "data must be passed through to max nodes for proper evaluation."
	decision_value_given = data[:, node.dec_idx]
	max_value = np.argmax(llchildren, axis=1)
	d_given = np.full(decision_value_given.shape[0], np.nan)
	if type(node.dec_values) == list:
		mapd = {tuple(node.dec_values[i]):i for i in range(len(node.dec_values))}
	else:
		mapd = {node.dec_values[i]:i for i in range(len(node.dec_values))}
	for k, v in mapd.items(): 
		if type(k) == tuple:
			d_given[decision_value_given in list(k)] = v
		else:
			d_given[decision_value_given == k] = v
	# if data contains a decision value use that otherwise use max
	
	child_idx = np.select([np.isnan(d_given), True],
						  [max_value, d_given]).astype(int)

	mll = llchildren[np.arange(llchildren.shape[0]), child_idx].reshape(-1, 1)

	# if decision value given is not in children, assign 0 probability
	missing_dec_branch = np.logical_and(np.logical_not(np.isnan(decision_value_given)),np.isnan(d_given))
	mll[missing_dec_branch] = np.finfo(mll.dtype).min

	return mll

def max_likelihood(node, children, data=None, dtype=np.float64):
	if None in children:
		return None
	llchildren = np.concatenate(children, axis=1)
	assert llchildren.dtype == dtype
	# print("node and llchildren", (node,llchildren))
	assert data is not None, "data must be passed through to max nodes for proper evaluation."
	decision_value_given = data[:,node.dec_idx]
	max_value = np.argmax(llchildren, axis=1)
	# if data contains a decision value use that otherwise use max
	child_idx = np.select([np.isnan(decision_value_given), True],
						  [max_value, decision_value_given]).astype(int)

	try:
		return llchildren[np.arange(llchildren.shape[0]), child_idx].reshape(-1, 1)
	except:
		return None


def sum_log_likelihood(node, children, data=None, dtype=np.float64):
	llchildren = np.concatenate(children, axis=1)
	assert llchildren.dtype == dtype

	assert np.isclose(np.sum(node.weights), 1.0), "unnormalized weights {} for node {}".format(node.weights, node)

	b = np.array(node.weights, dtype=dtype)

	sll = logsumexp(llchildren, b=b, axis=1).reshape(-1, 1)

	return sll


def sum_likelihood(node, children, data=None, dtype=np.float64):
	if None in children:
		return None
	llchildren = np.concatenate(children, axis=1)
	assert llchildren.dtype == dtype

	assert np.isclose(np.sum(node.weights), 1.0), "unnormalized weights {} for node {}".format(node.weights, node)

	b = np.array(node.weights, dtype=dtype)

	return np.dot(llchildren, b).reshape(-1, 1)

def interface_switch_log_likelihood(node, children, data=None, dtype=np.float64):
	llchildren = np.concatenate(children, axis=1)
	assert llchildren.dtype == dtype
	# print("node and llchildren", (node, llchildren))
	mll = np.max(llchildren, axis=1).reshape(-1, 1)
	return mll


_node_log_likelihood = {Sum: sum_log_likelihood, Product: prod_log_likelihood, Max: max_log_likelihood, InterfaceSwitch: interface_switch_log_likelihood}
_node_likelihood = {Sum: sum_likelihood, Product: prod_likelihood, Max: max_likelihood}


def log_node_likelihood(node, *args, **kwargs):
	probs = _node_likelihood[type(node)](node, *args, **kwargs)
	with np.errstate(divide="ignore"):
		nll = np.log(probs)
		nll[np.isinf(nll)] = np.finfo(nll.dtype).min
		assert not np.any(np.isnan(nll))
		return nll


def add_node_likelihood(node_type, lambda_func, log_lambda_func=None):
	_node_likelihood[node_type] = lambda_func
	if log_lambda_func is None:
		log_lambda_func = log_node_likelihood
	_node_log_likelihood[node_type] = log_lambda_func


def likelihood(node, data, dtype=np.float64, node_likelihood=_node_likelihood, lls_matrix=None, debug=False):
	all_results = {}

	if debug:
		assert len(data.shape) == 2, "data must be 2D, found: {}".format(data.shape)
		original_node_likelihood = node_likelihood

		def exec_funct(node, *args, **kwargs):
			assert node is not None, "node is nan "
			funct = original_node_likelihood[type(node)]
			ll = funct(node, *args, **kwargs)
			assert ll.shape == (data.shape[0], 1), "node %s result has to match dimensions (N,1)" % node.id
			assert not np.any(np.isnan(ll)), "ll is nan %s " % node.id
			return ll

		node_likelihood = {k: exec_funct for k in node_likelihood.keys()}

	result = eval_spn_bottom_up(node, node_likelihood, all_results=all_results, debug=debug, dtype=dtype, data=data)

	if lls_matrix is not None:
		for n, ll in all_results.items():
			if ll is None:
				lls_matrix[:, n.id] = None
			else:
				lls_matrix[:, n.id] = ll[:, 0]

	return result


def log_likelihood(
	node, data, dtype=np.float64, node_log_likelihood=_node_log_likelihood, lls_matrix=None, debug=False
):
	return likelihood(node, data, dtype=dtype, node_likelihood=node_log_likelihood, lls_matrix=lls_matrix, debug=debug)


def conditional_log_likelihood(node_joint, node_marginal, data, log_space=True, dtype=np.float64):
	result = log_likelihood(node_joint, data, dtype) - log_likelihood(node_marginal, data, dtype)
	if log_space:
		return result

	return np.exp(result)