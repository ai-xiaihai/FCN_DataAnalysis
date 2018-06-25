import pandas as pd

# read in simulations result data (adjacent matrix output)
# filepath: path to that file
# numNode: number of nodes including the market node
def read_sims_result(filepath, numNode=32):
    # add column names
    colnames=["dot"+str(x) for x in range(1,numNode)]
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
    
    return df