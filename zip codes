import pandas as pd


def preprocess():
    '''
    Import the Zip CSV file, convert into pandas dataframe, and clean the data
    
    Inputs: Nothing (assumes the csv is in our current directory)
    
    Returns: a cleaned dataframe 
    '''
    zips = pd.read_csv('uszips.csv')
    zips = zips.dropna(subset = ["zip"])
    non_states = ['AS', 'GU', 'MP', 'VI', 'PR']
    zips = zips[zips['state_id'].isin(non_states) == False]
    return zips
    

def get_zips_by_state(zips):
    '''
    Take in a cleaned data frame with zips data and return list of tuples
    
    Inputs: cleaned dataframe with data on zip, lat, lng, city, etc
    
    Returns: list of tuples. Each tuple contains state and most populated zip code in the state
    
    '''
    zips = zips.loc[zips.groupby("state_id")["population"].idxmax()][['state_id','zip']]
    records = zips.to_records(index=False)
    rv = list(records)
    return rv
    

def main():
    '''
    Take the unprocessed data frame, clean it, and return a list of tuples. 
    Each tuple consists of a state and zip code pair. The zip code 
    corresponds to the most highly populated zip code in the state.
    
    Inputs: None
    
    Returns: List of tuples with states and zip codes.
    
    '''
    zips = preprocess()
    return get_zips_by_state(zips)
