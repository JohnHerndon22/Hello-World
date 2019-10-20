#scoretheweek.py
#prepare the next week on the master and pickup any scores from the existing file
from common import *
import pandas as pan

# backup the master file 
if os.path.isfile(resultscsvdir+r_mastercsv): 
    copyfile(resultscsvdir+r_mastercsv, resultscsvdir+"Backup/BU-"+r_mastercsv)

# open the nflschedile master file
dfmasterfile = pan.read_csv(resultscsvdir+r_mastercsv)
masterdict = {'season' : '','weeknum' : '','sht_hometeam' : '','homepoppick' : .000,'espnhomepred' : .000,'homescore' : 0,'sht_awayteam' : '','awaypoppick' : .000,'espnawaypred' : .000,'awayscore' : 0,'gameid' : '','idx_awayteam' : 0,'idx_hometeam' : 0,'gamematch' : '','thursday' : '','selectteam' : '','mov' : 0,'poppickpred' : .000,'selectpred' : .000,'winteam' : ''}

dfgamedays = pan.DataFrame()
dfgamedays_all = pan.DataFrame()

# download and open the elo file
dleloratings()    
dfeloratings_2019 = pan.read_csv('/Users/johncyclist22/Documents/footpick/Data/nfl-elo/'+'nfl_elo_latest.csv', dtype=elodtypes) 

for weeknumber in range(1,18,1):

    dfgamedays = getpopdate(weeknumber, dfgamedays)
    dfgamedays_all = dfgamedays_all.append(dfgamedays)

dfgamedays_all = dfgamedays_all.set_index('gameday')

# loop thru elo finding schedule games not on nfl master
for index, game in dfeloratings_2019.iterrows():
    # loop thru the eloratings and add the week number to the data
    if game['date'][:4] == '2019':
        dfeloratings_2019.loc[index,'weeknumber'] = dfgamedays_all.loc[game['date'],'weeknumber']
    
    gamechecker = str(dfeloratings_2019.loc[index,'team1']).lower() + str(dfeloratings_2019.loc[index,'team2']).lower() + str(dfeloratings_2019.loc[index,'season'])+str(dfeloratings_2019.loc[index,'weeknumber'])
    dfeloratings_2019.loc[index,'gamematch'] = gamechecker
    print('Game is: '+ gamechecker)
    
    # then if the game does not exist on nfl schedule master - add it to the end 
    if dfmasterfile['gamematch'].isin([gamechecker]).any():
        pass
    else:
        masterdict['season'] = '2019'
        masterdict['weeknum'] = dfeloratings_2019.loc[index,'weeknumber']
        masterdict['sht_hometeam'] = str(dfeloratings_2019.loc[index,'team1']).lower()
        masterdict['homepoppick'] = .000
        masterdict['espnhomepred'] = .000
        masterdict['homescore'] = 0
        masterdict['sht_awayteam'] = str(dfeloratings_2019.loc[index,'team2']).lower()
        masterdict['awaypoppick'] = .000
        masterdict['espnawaypred'] = .000
        masterdict['awayscore'] = 0
        masterdict['gameid'] = ''
        masterdict['idx_awayteam'] = 0
        masterdict['idx_hometeam'] = 0
        masterdict['gamematch'] = str(dfeloratings_2019.loc[index,'team1']).lower()+str(dfeloratings_2019.loc[index,'team2']).lower()+'2019'+str(dfeloratings_2019.loc[index,'weeknumber'])
        masterdict['thursday'] = ''
        masterdict['selectteam'] = ''
        masterdict['mov'] = 0
        masterdict['poppickpred'] = .000
        masterdict['selectpred'] = .000
        masterdict['winteam'] = ''

        dfmasterfile = dfmasterfile.append(masterdict, ignore_index=True)
        masterdict = {'season' : '','weeknum' : '','sht_hometeam' : '','homepoppick' : .000,'espnhomepred' : .000,'homescore' : 0,'sht_awayteam' : '','awaypoppick' : .000,'espnawaypred' : .000,'awayscore' : 0,'gameid' : '','idx_awayteam' : 0,'idx_hometeam' : 0, 'gamematch' : '' ,'thursday' : '','selectteam' : '','mov' : 0,'poppickpred' : .000,'selectpred' : .000,'winteam' : ''}

dfeloratings_2019_gm = dfeloratings_2019.set_index('gamematch')
dfeloratings_2019_gm = dfeloratings_2019_gm.fillna(0)
dfmasterfile = dfmasterfile.fillna(0)

# loop thru the master schedule until finding unscored games 
for index, game in dfmasterfile.iterrows():

    # if the game has no score (0 to 0) - put the score, espnpred, etc into the scedule master
    if (game.homescore == 0) & (game.awayscore == 0) & (game.season == '2019') & (game.weeknum !=0):
        # then get poppick and place into the schedule master game record
        gamematch = dfmasterfile.loc[index,'gamematch']
        homescore = dfeloratings_2019_gm.loc[gamematch,'score1']
        awayscore = dfeloratings_2019_gm.loc[gamematch,'score2']
        dfmasterfile.loc[index,'homescore'] = homescore
        dfmasterfile.loc[index,'awayscore'] = awayscore

# print results
print(dfmasterfile.to_string())
if os.path.isfile(resultscsvdir+r_mastercsv): 
    copyfile(resultscsvdir+r_mastercsv, resultscsvdir+"backup/BU-"+r_mastercsv)
dfmasterfile.to_csv(resultscsvdir+r_mastercsv, index=False)
