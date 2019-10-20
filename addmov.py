#histonfl.py
import numpy as np
import pandas as pan
from common import *
import os

if os.path.isfile(resultscsvdir+r_mastercsv): 
    copyfile(resultscsvdir+r_mastercsv, resultscsvdir+"BU-"+r_mastercsv)
    # os.remove(resultscsvdir+r_mastercsv)
    
schdata = pan.read_csv(resultscsvdir+r_mastercsv, index_col=0)
os.system("clear")

for index, game in schdata.iterrows():
    
    if game["espnhomepred"] > .5:
        schdata.loc[index, "selectteam"] = game['sht_hometeam']
        schdata.loc[index,"poppickpred"] = game['homepoppick']
        schdata.loc[index,"selectpred"] = game['espnhomepred']

    else:
        schdata.loc[index, "selectteam"] = game['sht_awayteam']
        schdata.loc[index,"poppickpred"] = game['awaypoppick']
        schdata.loc[index,"selectpred"] = game['espnawaypred']

    if game['homescore'] > game['awayscore']:
        schdata.loc[index, "winteam"] = game['sht_hometeam']
    elif game['homescore'] < game['awayscore']:
        schdata.loc[index, "winteam"] = game['sht_awayteam']
    else:
        schdata.loc[index, "winteam"] = "tie"
        
    schdata.loc[index, "mov"] = abs(schdata.loc[index,'homescore'] - schdata.loc[index,'awayscore'])
#### run this - then in the other program - if the select team = winteam - + otherwise - 
  
print(schdata.to_string())     
schdata.to_csv(resultscsvdir+r_mastercsv+'-new')