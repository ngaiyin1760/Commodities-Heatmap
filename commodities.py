###################################################
########### Import all commodities data ###########
###################################################

import os
import pandas as pd

path = 'world/' # data downloaded from US Geological survey's mineral commodities report 2022
countries_list = [] # list to hold all countries names

# Select specific commodities to check the data
commodities_list = ['alumi', 'cemen', 'coppe', 'diamo', 'gold', 
                    'heliu', 'lead', 'lithi', 'nicke', 'plati',
                    'raree', 'selen', 'silve', 'titan', 'zinc']

for file in os.listdir(path): # import all csv files in the folder
    
    if file.endswith('csv'): # Only read the csv file
               
        # Store the countries into the list
        try:
            df = pd.read_csv(path + file, encoding='utf-8')
        except:
            df = pd.read_csv(path + file, encoding='unicode_escape')
        
        if file.split('_')[0].split('-')[-1] in commodities_list:
            
            for country in list(df['Country']):
                if country not in countries_list:
                    countries_list.append(country)
            

################################################################
########### Create a DataFrame to store all the data ###########
################################################################

import numpy as np

# Create an empty dataframe to store all the data
df_final = pd.DataFrame(columns = commodities_list,
                        index = sorted(countries_list[:-1]))

for file in os.listdir(path):
    
    if file.endswith('csv'): # only read the csv file
            
        commodity = file.split('_')[0].split('-')[-1]
        
        if commodity in commodities_list:
        
            try:
                df = pd.read_csv(path + file, encoding='utf-8')
                df = df.set_index('Country')
            except:
                df = pd.read_csv(path + file, encoding='unicode_escape')
                df = df.set_index('Country')
                
            column = df.columns[-1] # get the latest year's numbers
            
            if 'Unnamed' in column:
                column = df.columns[-2] # ensure to capture the latest year's numbers
            
            for country in list(df.index):
                
                if type(country) == str:
                                
                    tot_value = 0
                    
                    # to check if the dataframe has more than one value for a country
                    if type(df.loc[country][column]) == np.int64 or type(df.loc[country][column]) == str:
                        value_list = [df.loc[country][column]]
                        #print(value_list)
                    else:
                        value_list = list(df.loc[country][column])
                        #print(value_list)
                    
                    # add all the values in the value list by country
                    for value in value_list:
                        try:
                            value = value.replace(',', '')
                            tot_value += int(value)
                        except:
                            try:
                                tot_value += int(value)
                            except:
                                tot_value += 0
                    
                    # Put value back to corresponding cells
                    
                    df_final.loc[country, commodity] = tot_value


##############################################################################
########### Post-processing and calculate the % and average column ###########
##############################################################################

# replace all nan in the dataframe as 0
df_final = df_final.fillna(0)

# calculate the % by dividing world total
df_percent = df_final / df_final.loc['World total (rounded)', :]

# combine some duplicates for country
df_percent = df_percent.rename(index={"Other countries (rounded)":"Other countries",
                                      "United States (extracted from natural gas)":"United States",
                                      "United States (from Cliffside Field)":"United States",
                                      "United States (includes Puerto Rico)":"United States"})

df_percent = df_percent.groupby(level=0).sum()

# drop the total row 
df_percent.drop(['World total (rounded)'], inplace=True)
                
# change the dataframe column names to full names
df_percent.columns = ['aluminum', 'cement', 'copper', 'diamond', 'gold', 
                    'helium', 'lead', 'lithium', 'nickel', 'platinum',
                    'rare_earth', 'selenium', 'silver', 'titanium', 'zinc']

df_percent['average'] = df_percent.mean(axis=1)

average_column = df_percent.pop('average')
df_percent.insert(0, 'average', average_column)
df_percent = df_percent.sort_values(by='average',
                                    ignore_index=False,
                                    ascending=False)


######################################
########### Generate Heatmap #########
######################################

import seaborn as sns
import matplotlib.pyplot as plt
from  matplotlib.colors import LinearSegmentedColormap

# Set color code
wg = LinearSegmentedColormap.from_list('wg', ["w", "g"], N=256)

# Plot top 20 rows of the heatmap
fig, ax = plt.subplots(figsize=(22, 14))
heatmap = sns.heatmap(df_percent.head(20), annot=True, annot_kws={"size":10}, fmt=".1%", cmap=wg)
plt.tick_params(axis='both', which='major', labelsize=10,
                labelbottom=False, bottom=False, top=False, labeltop=True)

# Save the heatmap
output = 'heatmap.png' 
fig.savefig(output, bbox_inches='tight', dpi=300)
plt.show()
    