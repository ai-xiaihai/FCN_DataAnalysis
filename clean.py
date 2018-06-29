import pandas as pd
import numpy as np
from random import choices

def cleanup_0IR_single(sim, numNode):
	"""
	Clean up data for a single simulation w/ no interest rate

	Parameters
	----------
	sim: pandas dataFrame
		data relating to a single simulation
	numNode: int
		number of nodes including the market node

	Returns
	----------
	sim: pandas dataFrame
		data relating to the simulation w/ selected variables
	"""

	# a dictionary containing the columns and its corresponding new names
	# we copy some variables to its previous period observation
	old_to_new = {
		# new column: defaults due to negative wealth next period
		"defaults due to negative wealth": "default-next-wealth",
		# new column: defaults due to deposit shock next period
		"defaults due to deposit shock": "default-next-deposit",
		# new column: defaults due to interest next period
		"defaults due to interest": "default-next-interest"
	}

	# add new columns
	for k,v in old_to_new.items():
		newcol = np.append(sim[k].values[numNode-1:],[2 for _ in range(numNode-1)])
		newcol = pd.Series(newcol)
		sim[v] = newcol

	# add new column: leverage = debt / equity on the book 
	sim["leverage"] = ((sim["debt to pay"] + sim["deposits"]) 
		/ (sim["assets"] + sim["cash"] + sim["debt owed"] 
			- sim["debt to pay"] - sim["deposits"]))

	# add new column: dummy variable for zero leverage
	sim["dummy-0-leverage"] = np.where(sim["leverage"]==0, 1, 0)

	# add new column: over-leverage-frequency = over leverages / period
	sim["over-leverage-frequency"] = sim["over leverages"] / sim["period"]

	# a dictionary containing the columns and its corresponding new names
	# we copy some variables to its subsequent period observation
	lag_name = {
		"wealth": "wealth-lag",
		"deposits": "deposits-lag",
		"cash": "cash-lag",
		"assets": "assets-lag",
		"leverage": "leverage-lag",
		"credit available": "credit-available-lag",
		"credit issued": "credit-issued-lag",
		"dummy-0-leverage": "dummy-0-leverage-lag"
	}

	# add new columns
	for k,v in lag_name.items():
		newcol = np.append([-8888 for _ in range(numNode-1)], sim[k].values[:-(numNode-1)])
		newcol = pd.Series(newcol)
		sim[v] = newcol

	# add new column: defaults next period
	sim["default-next"] = (sim["default-next-wealth"] + 
							sim["default-next-deposit"] +
							sim["default-next-interest"])

	# filter out cases where banks defaulted in the previous periods
	sim = sim[sim["defaults due to negative wealth"]
				+sim["defaults due to deposit shock"]
				+sim["defaults due to interest"]
				+sim["default-next"] < 2]

	# filter out first period observations
	sim = sim[sim["period"] != 1]

	return sim[["sim#", "period", "bankID", "theta (risk aversion)",  
		 "wealth", "deposits", "cash", "assets", "leverage",
		 "credit available", "credit issued", "dummy-0-leverage",
		 "wealth-lag", "deposits-lag", "cash-lag", "assets-lag", "leverage-lag",
		 "credit-available-lag", "credit-issued-lag", "dummy-0-leverage-lag",
		 "over-leverage-frequency",
		 "default-next-wealth", "default-next-deposit", "default-next-interest",
		 "default-next"]]

def cleanup_0IR_exp(exp, numNode, numPeriod, numSim, balanced=False):
	"""
	Clean up data for an experiment w/ no interest rate

	Parameters
	----------
	exp: pandas dataFrame
		data relating to an experiment (multiple simulations w/ the same parameter)
	numNode: int
		number of nodes including the market node
	numPeriod: int
		number of periods in each simulation
	numSim: int
		output # simulations (<= total simulations # in the experiment)
	balanced: boolean, default=False
		whether # of default cases = # of non-default cases

	Returns
	----------
	df: pandas dataFrame
		data relating to the experiment w/ selected variables
	"""

	# insert some variable to locate observations
	exp["sim#"] = pd.Series(np.repeat(np.array(range(numSim)), numPeriod*(numNode-1)))
	exp["bankID"] = pd.Series(np.tile(np.array(range(numNode-1)), numPeriod*numSim))

	# apply function cleanup_0IR_single to result data of each simulation
	cleaned_sims_data = [cleanup_0IR_single(
		exp.loc[i*(numNode-1)*numPeriod : (i+1)*(numNode-1)*numPeriod-1].copy().reset_index(drop=True)
		, numNode) for i in range(numSim)]

	# Concatenate the simulation results together
	df = pd.concat(cleaned_sims_data).reset_index(drop=True)

	if (balanced):
		# randomly discard non-default cases 
		# so that # of default cases = # of non-default cases
		numDefault = len(df[df['default-next']==1])
		indexDefault = df.index[df['default-next']==1].values
		indexGood = df.index[df['default-next']==0].values
		indexChosen = choices(indexGood, k=numDefault) + list(indexDefault)
		df = df.take(indexChosen).reset_index(drop=True)

	return df

def cleanup_network(df, numNode=32, numPeriod=15, numSim=50):
	"""
	Clean up data to get the adjacency matrices from simulation result

	Parameters
	----------
	df: pandas dataFrame
		simulation result
	numNode: int
		number of nodes including the market node
	numPeriod: int
		number of periods in each simulation
	numSim: int
		number of simulations in the experiment

	Returns
	----------
	result: 4D numpy array 
		containing adjacency matrices of every simulation
	"""

	N = numNode-1
	P = numPeriod
	result = np.empty([numSim, numPeriod, N, N])
	for i in range(numSim):
		for j in range(numPeriod):
			result[i,j] = df.loc[i*P*N + j*N : i*P*N + j*N + (N-1),
								 "dot0" : "dot30"
								].values
	return result
