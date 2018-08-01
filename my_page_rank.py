import networkx as nx
from collections import deque # deque
from random import random # random [0,1)

#
# This file contains customized algorithms similar to the idea of Page Rank.
#

# Experimentally, performance of random_walk_single_1a, 1b, 2a, 2b are
# about the same.

def random_walk_single_1a(N, solvent, iterations=10):
	"""
	at the begining of each round, flip coin to cause one solvent bank to default
	during each round, we can add 1 multiple times
	
	This one is aggressive
	[[18054    25] ---0625/1IR
	 [  158     3]]
	[[17926    30] ---0625/2IR
	 [  160     3]]
	
	Parameters
	----------
	N: 2D numpy array [n_borrowers, n_lenders]
		debt adjacency matrices 
	solvent: list 
		solvent[solvent bank] = predicted default probability
		solvent[insolvent bank] = -1
	iterations: int
		number of iterations
	
	Returns
	----------
	result: dict {BankID : # of default}
		index for the bank's default probability
	"""
	num_bank, _ = N.shape
	G = nx.DiGraph(N)
	nextDefault = deque()
	defaulted = frozenset([i for i in range(num_bank) if solvent[i] == -1])
	tempDefault = set(defaulted)
	probDefault = {i:solvent[i] for i in range(num_bank) if solvent[i] >= 0}
	result = dict(zip(list(probDefault.keys()), [0 for _ in probDefault.keys()]))
	def coin(p=0.5):
		return random() < p
	
	for _ in range(iterations):
		for b in probDefault.keys():

			if coin(probDefault[b]): 
				nextDefault.append(b)
			while len(nextDefault) > 0: # queue not empty
				n = nextDefault.popleft() # next on the queue
				if n not in tempDefault: # not aleady defaulted
					tempDefault.add(n)
					result[n] += 1
					for s in G.successors(n): # creditors of n
						if s not in tempDefault and coin(G.edges[(n,s)]['weight']):
							nextDefault.append(s)
			tempDefault = set(defaulted)
			
	return result


def random_walk_single_1b(N, solvent, iterations=10):
	"""
	at the begining of each round, flip coin to cause one solvent bank to default
	during each round, we can add 1 multiple times
	
	This one is also aggressive
	[[18052    27] ---0625/1IR
	 [  157     4]]
	[[17927    29] ---0625/2IR
	 [  160     3]]
	
	Parameters
	----------
	N: 2D numpy array [n_borrowers, n_lenders]
		debt adjacency matrices 
	solvent: list 
		solvent[solvent bank] = predicted default probability
		solvent[insolvent bank] = -1
	iterations: int
		number of iterations
	
	Returns
	----------
	result: dict {BankID : # of default}
		index for the bank's default probability
	"""
	num_bank, _ = N.shape
	G = nx.DiGraph(N)
	nextDefault = deque()
	probDefault = {i:solvent[i] for i in range(num_bank) if solvent[i] >= 0}
	result = dict(zip(list(probDefault.keys()), [0 for _ in probDefault.keys()]))
	def coin(p=0.5):
		return random() < p
	
	for _ in range(iterations):
		for b in probDefault.keys():
			if coin(probDefault[b]): 
				nextDefault.append(b)
			while len(nextDefault) > 0: # queue not empty
				n = nextDefault.popleft() # next on the queue
				result[n] += 1 # default count ++
				for s in G.successors(n): # creditors of n
					if coin(G.edges[(n,s)]['weight']):
						nextDefault.append(s)
						
	return result

def random_walk_single_2a(N, solvent, iterations=10):
	"""
	at the begining of each round, flip multiple coins for each solvent bank to make them default
	during each round, we can add 1 multiple times
	
	This one is useless (very progressive):
	[[18079     0] ---0625/1IR
	 [  161     0]]
	[[17956     0] ---0625/2IR
	 [  163     0]]
	
	Parameters
	----------
	N: 2D numpy array [n_borrowers, n_lenders]
		debt adjacency matrices 
	solvent: list 
		solvent[solvent bank] = predicted default probability
		solvent[insolvent bank] = -1
	iterations: int
		number of iterations
	
	Returns
	----------
	result: dict {BankID : # of default}
		index for the bank's default probability
	"""
	num_bank, _ = N.shape
	G = nx.DiGraph(N)
	nextDefault = deque()
	defaulted = frozenset([i for i in range(num_bank) if solvent[i] == -1])
	tempDefault = set(defaulted)
	probDefault = {i:solvent[i] for i in range(num_bank) if solvent[i] >= 0}
	result = dict(zip(list(probDefault.keys()), [0 for _ in probDefault.keys()]))
	def coin(p=0.5):
		return random() < p
	
	for _ in range(iterations):
		for b in probDefault.keys():
			if coin(probDefault[b]): 
				nextDefault.append(b)

		while len(nextDefault) > 0: # queue not empty
			n = nextDefault.popleft() # next on the queue
			if n not in tempDefault: # not aleady defaulted
				tempDefault.add(n)
				result[n] += 1
				for s in G.successors(n): # creditors of n
					if s not in tempDefault and coin(G.edges[(n,s)]['weight']):
						nextDefault.append(s)
		tempDefault = set(defaulted)
	
	return result

def random_walk_single_2b(N, solvent, iterations=10):
	"""
	at the begining of each round, flip multiple coins for each solvent bank to make them default
	during each round, we can add 1 multiple times
	
	This one is progressive:
	[[18048    31] ---0625/1IR
	 [  157     4]]
	[[17926    30] ---0625/2IR
	 [  157     6]]
	
	Parameters
	----------
	N: 2D numpy array [n_borrowers, n_lenders]
		debt adjacency matrices 
	solvent: list 
		solvent[solvent bank] = predicted default probability
		solvent[insolvent bank] = -1
	iterations: int
		number of iterations
	
	Returns
	----------
	result: dict {BankID : # of default}
		index for the bank's default probability
	"""
	num_bank, _ = N.shape
	G = nx.DiGraph(N)
	nextDefault = deque()
	probDefault = {i:solvent[i] for i in range(num_bank) if solvent[i] >= 0}
	result = dict(zip(list(probDefault.keys()), [0 for _ in probDefault.keys()]))
	def coin(p=0.5):
		return random() < p
	
	for _ in range(iterations):
		for b in probDefault.keys():
			if coin(probDefault[b]): 
				nextDefault.append(b)
		while len(nextDefault) > 0: # queue not empty
			n = nextDefault.popleft() # next on the queue
			result[n] += 1
			for s in G.successors(n): # creditors of n
				if coin(G.edges[(n,s)]['weight']):
					nextDefault.append(s)
					
	return result