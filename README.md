This file contains descriptions of each of the files we've uploaded, 
explanations of how the code in each file works, and instructions on how to run our code to
generate your desired outputs.

### uszips.csv 
This is the raw csv file from which we are generating our list of zip codes. It contains
data for every zip code in each territory and state in the US.

### generate_zip_codes.py
This file contains code for importing, cleaning, and processing the zips.csv file 
and returning a list of zip codes to use for scraping.

### scraper.py
This file contains code to navigate through listings pages on Carvana.com and collect data 
from each listing. We use selenium to click through listings and regular expressions to parse 
each listing. 

### clean_and_agg.py
This file contains code for aggregating the many dataframes that we collected individually. 
We combine these into a single dataframe, with rows representing listings and columns representing
vehicle features. This dataframe will contain all the necessary inputs for our neural net.

### agg_df_3.csv
This file contains all the data that we collected through scraping and cleaning.

### neural_net.py
This file contains code for training and testing a model. The model takes features of any car (the columns
of our dataframe) as input, and returns a predicted price. We split our data into training and testing
subsets in order to validate our model, and we end up with reasonably accurate predictions.










