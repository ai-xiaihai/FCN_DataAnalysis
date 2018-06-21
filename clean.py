import pandas as pd
import numpy as np
from random import choices

# Clean up data for a single simulation w/ no interest rate
# sim: data relating to a single simulation
# numNode: number of nodes including the market node
# include one-period lag in the data
def cleanup_0IR_single(sim, numNode, lag_one=False):
	# a dictionary containing the columns and its corresponding new names
	# we copy some variables to its previous period observation
	old_to_new = {
		# new column: defaults due to negative wealth next period
		"defaults due to negative wealth": "default-next-wealth",
		# new column: defaults due to deposit shock next period
		"defaults due to deposit shock": "default-next-deposit"
	}

	# add new columns
	for k,v in old_to_new.items():
		newcol = np.append(sim[k].values[numNode-1:],[2 for _ in range(numNode-1)])
		newcol = pd.Series(newcol)
		sim[v] = newcol

	# filter out cases where banks defaulted in the previous period
	sim = sim[sim["defaults due to negative wealth"]+sim["defaults due to deposit shock"]
			  +sim["default-next-wealth"]+sim["default-next-deposit"] < 2]

	# add new column: defaults next period
	sim["default-next"] = sim["default-next-wealth"] + sim["default-next-deposit"]

	# add new column: leverage = debt / equity on the book 
	sim["leverage"] = sim["deposits"] / (sim["assets"]+sim["cash"]-sim["deposits"])

	return sim[["period", "theta (risk aversion)",
		 "wealth", "deposits", "cash", "assets", "leverage",
		 "credit available", "credit issued",
		 "default-next-wealth", "default-next-deposit", "default-next"]]

# Clean up data for an experiment w/ no interest rate
# exp: data relating to an experiment (multiple simulationn w/ the same parameter)
# numNode: number of nodes including the market node
# numPeriod: number of periods in each simulation
# numSim: number of simulations in the experiment
# balanced: whether # of default cases = # of non-default cases
def cleanup_0IR_exp(exp, numNode, numPeriod, numSim, balanced=False):
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