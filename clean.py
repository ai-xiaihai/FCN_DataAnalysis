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

	# add new column: leverage = debt / equity on the book 
	sim["leverage"] = sim["deposits"] / (sim["assets"]+sim["cash"]-sim["deposits"])

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

	# filter out cases where banks defaulted in the previous periods
	sim = sim[sim["defaults due to negative wealth"]+sim["defaults due to deposit shock"]
			  +sim["default-next-wealth"]+sim["default-next-deposit"] < 2]

	# filter out first period observations
	sim = sim[sim["period"] != 1]

	# add new column: defaults next period
	sim["default-next"] = sim["default-next-wealth"] + sim["default-next-deposit"]

	return sim[["period", "theta (risk aversion)",
		 "wealth", "deposits", "cash", "assets", "leverage",
		 "credit available", "credit issued", "dummy-0-leverage",
		 "default-next-wealth", "default-next-deposit", "default-next",
		 "wealth-lag", "deposits-lag", "cash-lag", "assets-lag",
		 "leverage-lag", "credit-available-lag", "credit-issued-lag",
		 "dummy-0-leverage-lag",
		 "over-leverage-frequency"]]

# Clean up data for an experiment w/ no interest rate
# exp: data relating to an experiment (multiple simulation w/ the same parameter)
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