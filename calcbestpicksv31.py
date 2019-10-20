#loadschedulev10.py
#calcbestpicks v30 - includes alternate scenario
import numpy as np
import pandas as pan
from common import *

def processresults(sc_array, schdata, results, sc_count, testinc):
    # calcuate the results - games won-loss-tie, overall pct, total pts earned, correlation between selected and results, avg mov
    print("Scenario is: " + testinc)

    wins = schdata['won'].sum()
    totalgames = schdata['sht_hometeam'].count()
    losses = totalgames - wins 
    pointsearned = schdata['ptsearned'].sum()
    print("W ", wins, "- L ", losses, " Pct: ", round(wins/totalgames,3), " total pts: " + str(pointsearned))
    print(schdata.dtypes)
    print(pan.pivot_table(schdata, values=['ptsearned', 'won', 'winteam'], index=['weeknum'], aggfunc={'ptsearned':np.sum, 'won':np.sum, 'winteam': 'count'}))
    quit()
    return results

def baseeval(schdata,testinc):
    # calculates groups 1 & 2 (7 and 6)
    # create espn largest & smallest pick columns
    schdata["espnmaxpick"] = schdata[["espnhomepred","espnawaypred"]].max(axis=1)
    schdata["popmaxpick"] = schdata[["homepoppick","awaypoppick"]].max(axis=1)        

    # determine catagory level - use conditonals for each game
    schdata['pickcat'] = np.where(schdata['espnmaxpick']>=.70, 7, 1)
    return schdata

def home65(schdata, maxpickcat, testinc):
    # schdata['pickcat'].loc[(schdata['espnhomepred'] >= .60) & (schdata['espnhomepred']<.65)] = 6
    
    # schdata["espnmaxpick"] = np.where((schdata['pickcat']==1) & (schdata['espnhomepred'] >= .65) & (schdata['espnhomepred']<.70), schdata["espnhomepred"],schdata["espnmaxpick"])
    schdata["pickcat"] = np.where((schdata['pickcat']==1) & (schdata['espnhomepred'] >= .65) & (schdata['espnhomepred']<.70),maxpickcat,schdata["pickcat"])

    return schdata

def reversechoices(schdata, testinc):
    # determine team selection for each game - see conditional
    # print("reversing lower choices")    
    schdata["espnmaxpick"] = np.where((schdata['pickcat']==1), schdata[["espnhomepred","espnawaypred"]].min(axis=1),schdata["espnmaxpick"])
    return schdata

def lowerchoices(schdata, testinc):
    # this might not be needed
    # print("keep lower choices the same")
    pass
    # schdata['teamselected'] = np.where((schdata['pickcat']==1) & (schdata['sht_hometeam']==schdata['teamselected']),schdata['sht_awayteam'],schdata['teamselected'])
    # schdata['teamselected'] = np.where((schdata['pickcat']==1) & (schdata['sht_awayteam']==schdata['teamselected']),schdata['sht_hometeam'],schdata['teamselected'])
    return schdata

def homethursday(schdata,maxpickcat, testinc):
    # this might not be needed
    # print("home thursday")
    
    schdata["espnmaxpick"] = np.where((schdata['pickcat']==1) & (schdata["thursday"]==1), schdata["espnhomepred"],schdata["espnmaxpick"])
    schdata["pickcat"] = np.where((schdata['pickcat']==1) & (schdata["thursday"]==1),maxpickcat,schdata["pickcat"])
    
    return schdata

def keyhometeams(schdata,maxpickcat, testinc):
    # this might not be needed
    keyhomers = ["gb", "ne", "pit", "bal", "sea", "den" ]
    schdata["espnmaxpick"] = np.where((schdata['pickcat']==1) & (schdata["sht_hometeam"].isin(keyhomers)), schdata["espnhomepred"],schdata["espnmaxpick"])
    schdata["pickcat"] = np.where((schdata['pickcat']==1) & (schdata["sht_hometeam"].isin(keyhomers)),maxpickcat,schdata["pickcat"])
    # print("keyhometeams")
    
    return schdata

def popick(schdata,maxpickcat, testinc):
    # this might not be needed
    # print("pop pick > 85%")   
    schdata["espnmaxpick"] = np.where((schdata['pickcat']==1) & (schdata["homepoppick"] >.849), schdata["espnhomepred"],schdata["espnmaxpick"])
    schdata["pickcat"] = np.where((schdata['pickcat']==1) & (schdata["homepoppick"] >.849),maxpickcat,schdata["pickcat"])
    schdata["espnmaxpick"] = np.where((schdata['pickcat']==1) & (schdata["awaypoppick"] >.849), schdata["espnawaypred"],schdata["espnmaxpick"])
    schdata["pickcat"] = np.where((schdata['pickcat']==1) & (schdata["awaypoppick"] >.849),maxpickcat,schdata["pickcat"])
    
    return schdata

def makeselections(sc_count, schdata, passer, dfconditionals):

    maxpickcat = 5
    testinc=""
    for test_number in passer:
        if test_number == 1:                # covers both 1 and 2 - 2 will be skipped
            # c_dfsched = dfsched.copy()        
            # dfsched = gameanalyzer(baseurl, c_dfsched, weeknumber, dfpoppicks, dfteams,dfschedext, window)
            c_schdata = schdata.copy()    
            schdata = baseeval(c_schdata,testinc)           
            testinc = "ESPN > 70%"
        elif test_number == 2:
            c_schdata = schdata.copy()    
            schdata = home65(c_schdata,maxpickcat, testinc)
            testinc += ", ESPN Home > 65"
            maxpickcat -=1
        elif test_number == 3:    
            c_schdata = schdata.copy()    
            schdata = homethursday(c_schdata,maxpickcat,testinc)
            testinc += ", Thursday Home Team"
            maxpickcat -=1
        elif test_number == 4:
            c_schdata = schdata.copy()    
            schdata = keyhometeams(c_schdata,maxpickcat,testinc)
            testinc += ", Key Home Teams"
            maxpickcat -=1
        elif test_number == 5:
            c_schdata = schdata.copy()    
            schdata = popick(c_schdata,maxpickcat,testinc)
            testinc += ", pop pick > 85%"
            maxpickcat -=1
        elif test_number == 6:
            c_schdata = schdata.copy()    
            schdata = lowerchoices(c_schdata,testinc)               # eventually this will be sent if the scenario warrants it   
            testinc += ", Cat 1 > ESPN%"    
        else:
            c_schdata = schdata.copy()    
            schdata = reversechoices(c_schdata,testinc)
            testinc += ", Cat 1 Less ESPN %"
            
    # post processing - 
    # determine selected espn % (could be espnbigpick) & determine the selected team based onthe pick selected
    schdata['teamselected'] = np.where(schdata['espnhomepred']==schdata['espnmaxpick'],schdata['sht_hometeam'],schdata['sht_awayteam'])
    schdata['espnselected'] = np.where((schdata['sht_awayteam']==schdata['teamselected']),schdata['espnawaypred'],schdata['espnhomepred'])

    # sort by catagory number+espn selected percentage - group by weeknumber - assign ranks
    schdata = schdata.sort_values(['weeknum','pickcat'],ascending=True)
    schdata['popranktb'] = schdata["popmaxpick"]/1000
    schdata["t_ranker"] = schdata["pickcat"]+schdata["espnselected"]+schdata['popranktb']
    schdata["ptsalloc"] = schdata.groupby("weeknum")["t_ranker"].rank("dense", ascending=True)

    # determine winning team
    schdata['winningteam'] = np.where((schdata['homescore'] > schdata['awayscore']),schdata['sht_hometeam'],schdata['sht_awayteam'])
    # determine how many points were earned
    schdata['ptsearned'] = np.where((schdata['teamselected'] == schdata['winningteam']),schdata['ptsalloc'],0)
    schdata['won'] = np.where((schdata['teamselected'] == schdata['winningteam']),1,0)
    
    results = processresults(passer, schdata, dfresults, sc_count, testinc)
    

    return schdata
    
data_cond = {'testnumber': [1,2,3,4,5,6,7,8],
    'desc': ["Over 70", "Home Over 65", "Home Thursday", "Pop Pick > 85%", "Home Key Teams", "Keep Lower","Reverse Lower", "Both Over 65"]}
dfconditionals = pan.DataFrame(data_cond, columns = ['testnumber', 'desc'])

scenarios = {
1:[1,2,6],
2:[1,2,4,6],
3:[1,2,5,4,6],
4:[1,2,5,6],
5:[1,2,3,4,5,6],
6:[1,4,2,6],
7:[1,2,5,6]}
# add the scenario names - build the different test conditional functions, place the scenario name into the csv, delete the results file at first
# place the results into the dataframe - write to a seperate csv at end - delete at start

data_results = {'scenario': ['1'],
    'desc': ["Plus 65 Reverse Lowers"],
    'wins': [0],
    'losses': [0],
    'pct': [.000], 
    'ptsearned': [0]}
dfresults = pan.DataFrame(data_results, columns = ['scenario', 'desc', 'wins', 'losses','pct', 'ptsearned']) 

sc_count = 1    
scncounter = 1
# loop thru the scenarios - process each
for sc_count in scenarios.keys():
    passer = scenarios.get(sc_count)
    
    print("processing records from: " + r_mastercsv)
    schdata_all = pan.read_csv(resultscsvdir+r_mastercsv)
    schdata_all.set_index('season', inplace=True)
    schdata = schdata_all.loc["2019"]
    schdata.set_index('index',inplace=True)
    totalrecs = len(schdata.index)
    schdata = makeselections(sc_count, schdata, passer, dfconditionals)
    schdata.to_csv(loadcsvdir+year+"-"+str(sc_count)+"-"+csvoutput,mode="w")
    scncounter +=1

print ("scenarios processed = " + str(scncounter))    
print ("total records in file: " + str(totalrecs))



