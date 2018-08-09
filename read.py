import pandas as pd
import numpy as np

def read_sims_result(filepath, numNode=32):
    """
    Read in simulations result data (adjacent matrix + bank balanced sheet)

    Parameters
    ----------
    filepath: str
        path to that file
    numNode: int
        number of nodes including the market node

    Returns
    ----------
    df: pandas dataFrame
        simulations result data 
    """

    # add column names
    colnames=["dot"+str(x) for x in range(numNode-1)]
    colnames.extend(["period", "theta (risk aversion)", "defaults due to interest", 
         "defaults due to negative wealth", "defaults due to deposit shock", 
         "over leverages", "wealth", "debt to pay", "credit available", 
         "debt owed", "credit issued", "deposits", "cash", "assets"])
    
    # read into dataframe
    df = pd.read_csv(
        filepath, 
        delim_whitespace=True,
        header=None,
        names=colnames,
        index_col=False
    )

    # figure out data related information
    numPeriod = max(df["period"])
    numSim = int(len(df) / numPeriod / (numNode-1))

    # insert some variable to locate observations
    df["sim#"] = pd.Series(np.repeat(np.array(range(numSim)), numPeriod*(numNode-1)))
    df["bankID"] = pd.Series(np.tile(np.array(range(numNode-1)), numPeriod*numSim))
    
    return df