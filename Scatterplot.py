#histonfl.py
#mov added
import numpy as np
import pandas as pan
import statistics as st
from common import *
import os

def espnperformance(season, c_schdata, lowerbound, upperbound, title):

    # print(title)
    dfdict = {'title' : title, 'season': season,'wins': [0] ,'lose': [0],'totalgames':[0],'pct': [.000], 'avgmov': 0}
    
    totalgamesview = c_schdata.apply(lambda x: True if (x['espnhomepred'] > lowerbound) & (x['espnhomepred'] < upperbound) | (x['espnawaypred'] > lowerbound) & (x['espnawaypred'] < upperbound) else False , axis=1)
    gamesnum = len(totalgamesview[totalgamesview == True].index) 
    
    totalhomewinsview = c_schdata.apply(lambda x: True if (x['espnhomepred'] > lowerbound) & (x['espnhomepred'] < upperbound) & (x['sht_hometeam'] == x['winteam']) else False , axis=1)
    homewinsnum = len(totalhomewinsview[totalhomewinsview == True].index) 
    
    totalawaywinsview = c_schdata.apply(lambda x: True if (x['espnawaypred'] > lowerbound) & (x['espnawaypred'] < upperbound) & (x['sht_awayteam'] == x['winteam']) else False , axis=1)
    awaywinsnum = len(totalawaywinsview[totalawaywinsview == True].index) 
    
    winsnum = homewinsnum+awaywinsnum 
    print(c_schdata)
    mover = c_schdata.loc[(c_schdata['espnhomepred'] > lowerbound) & (c_schdata['espnhomepred'] < upperbound) | (c_schdata['espnawaypred'] > lowerbound) & (c_schdata['espnawaypred'] < upperbound)]
    mov = round(mover['mov'].mean(),2)

    print(st.stdev(mover['mov']))
    print(st.variance(mover['mov']))
    # print(stdmov)
    quit()

    print(title, '  W- ', winsnum, "  L-", str(gamesnum - winsnum), " Total: ", str(gamesnum), "  PCT: ", str(round(winsnum / gamesnum,3)))
    dfdict['wins'] = winsnum
    dfdict['lose'] = gamesnum - winsnum
    dfdict['totalgames'] = gamesnum
    dfdict['pct'] = round(winsnum / gamesnum,3)
    dfdict['mov'] = mov
    dfresults = pan.DataFrame([dfdict], columns=['title', 'season','wins','lose','totalgames','pct','mov'])
    # print(dfresults)
    # quit()
    return dfresults

dfoutcomes = pan.DataFrame(columns=['title', 'season','wins','lose','totalgames','pct','mov'])
schdata = pan.read_csv(resultscsvdir+r_mastercsv, index_col=1)
os.system("clear")

# print("2019")
season = "2019"
schdata2019 = schdata.loc["2019"]
# now reset the index to look thru by game
schdata2019 = schdata2019.set_index('index')
for index, game in schdata2019.iterrows():

    # determine who won each game
    if schdata2019.loc[index,'homescore'] > schdata2019.loc[index,'awayscore']: 
        schdata2019.loc[index, "winteam"] = schdata2019.loc[index,"sht_hometeam"]
        schdata2019.loc[index, "winpred"] = schdata2019.loc[index,"espnhomepred"]
        
    elif schdata2019.loc[index,'awayscore'] > schdata2019.loc[index,'homescore']: 
        schdata2019.loc[index, "winteam"] = schdata2019.loc[index,"sht_awayteam"]
        schdata2019.loc[index, "winpred"] = schdata2019.loc[index,"espnawaypred"]
    else:
        schdata2019.loc[index, "winteam"] = "tie"

    if schdata2019.loc[index,'winteam'] != schdata2019.loc[index,'selectteam']: 
        schdata2019.loc[index, "mov"] = schdata2019.loc[index,"mov"]*-1

dfoutcomes = dfoutcomes.append(espnperformance(season, schdata2019, .70, .99, '2019 Above 70% ESPN'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata2019, .65, .699, '2019 65% to 70% ESPN'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata2019, .60, .649, '2019 60% to 65% ESPN'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata2019, .50, .599, '2019 50% to 59% ESPN'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata2019, .65, .99, '2019 Above 65%'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata2019, .50, .99, 'Above 50%'))

#  2018
schdata2018 = schdata.loc["2018"]
season = "2018"
# now reset the index to look thru by game
schdata2018 = schdata2018.set_index('index')
for index, game in schdata2018.iterrows():

    # determine who won each game
    if schdata2018.loc[index,'homescore'] > schdata2018.loc[index,'awayscore']: 
        schdata2018.loc[index, "winteam"] = schdata2018.loc[index,"sht_hometeam"]
        schdata2018.loc[index, "winpred"] = schdata2018.loc[index,"espnhomepred"]
        
    elif schdata2018.loc[index,'awayscore'] > schdata2018.loc[index,'homescore']: 
        schdata2018.loc[index, "winteam"] = schdata2018.loc[index,"sht_awayteam"]
        schdata2018.loc[index, "winpred"] = schdata2018.loc[index,"espnawaypred"]
    else:
        schdata2018.loc[index, "winteam"] = "tie"
    
    if schdata2018.loc[index,'winteam'] != schdata2018.loc[index,'selectteam']: 
        schdata2018.loc[index, "mov"] = schdata2018.loc[index,"mov"]*-1

dfoutcomes = dfoutcomes.append(espnperformance(season, schdata2018, .70, .99, '2018 Above 70% ESPN'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata2018, .65, .699, '2018 65% to 70% ESPN'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata2018, .60, .649, '2018 60% to 65% ESPN'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata2018, .50, .599, '2018 50% to 59% ESPN'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata2018, .65, .99, '2018 Above 65%'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata2018, .50, .99, 'Above 50%'))

# 2017
season = "2017"
schdata2017 = schdata.loc["2017"]

# now reset the index to look thru by game
schdata2017 = schdata2017.set_index('index')
for index, game in schdata2017.iterrows():

    # determine who won each game
    if schdata2017.loc[index,'homescore'] > schdata2017.loc[index,'awayscore']: 
        schdata2017.loc[index, "winteam"] = schdata2017.loc[index,"sht_hometeam"]
        schdata2017.loc[index, "winpred"] = schdata2017.loc[index,"espnhomepred"]
        
    elif schdata2017.loc[index,'awayscore'] > schdata2017.loc[index,'homescore']: 
        schdata2017.loc[index, "winteam"] = schdata2017.loc[index,"sht_awayteam"]
        schdata2017.loc[index, "winpred"] = schdata2017.loc[index,"espnawaypred"]
    else:
        schdata2017.loc[index, "winteam"] = "tie"

    if schdata2017.loc[index,'winteam'] != schdata2017.loc[index,'selectteam']: 
        schdata2017.loc[index, "mov"] = schdata2017.loc[index,"mov"]*-1


dfoutcomes = dfoutcomes.append(espnperformance(season, schdata2017, .70, .99, '2017 Above 70% ESPN'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata2017, .65, .699, '2017 65% to 70% ESPN'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata2017, .60, .649, '2017 60% to 65% ESPN'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata2017, .50, .599, '2017 50% to 59% ESPN'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata2017, .65, .99, '2017 Above 65%'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata2017, .50, .99, 'Above 50%'))

# all years
season = "All Years"
schdata = schdata.set_index('index')
for index, game in schdata.iterrows():

    # determine who won each game
    if schdata.loc[index,'homescore'] > schdata.loc[index,'awayscore']: 
        schdata.loc[index, "winteam"] = schdata.loc[index,"sht_hometeam"]
        schdata.loc[index, "winpred"] = schdata.loc[index,"espnhomepred"]
        
    elif schdata.loc[index,'awayscore'] > schdata.loc[index,'homescore']: 
        schdata.loc[index, "winteam"] = schdata.loc[index,"sht_awayteam"]
        schdata.loc[index, "winpred"] = schdata.loc[index,"espnawaypred"]
    else:
        schdata.loc[index, "winteam"] = "tie"
    
    if schdata.loc[index,'winteam'] != schdata.loc[index,'selectteam']: 
        schdata.loc[index, "mov"] = schdata.loc[index,"mov"]*-1

dfoutcomes = dfoutcomes.append(espnperformance(season, schdata, .70, .99, 'All Years Above 70% ESPN'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata, .65, .699, 'All Years 65% to 70% ESPN'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata, .50, .599, 'All Years 50% to 59% ESPN'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata, .60, .649, 'All Years 60% to 65% ESPN'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata, .65, .99, 'All Years Above 65%'))
dfoutcomes = dfoutcomes.append(espnperformance(season, schdata, .50, .99, 'Above 50%'))

print(dfoutcomes.to_string())