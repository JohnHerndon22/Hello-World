#common.py
import os
from os import path
from datetime import datetime 
import csv
import codecs
import decimal
import pandas as pan
from shutil import copyfile
from operator import itemgetter, attrgetter
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import numpy as np
from urllib.request import urlopen as uReq 
import os


#https://www.espn.com/nfl/schedule/_/week/2
sch_url = "https://www.espn.com/nfl/schedule/_/week/"
weeknumber = 0
sch_tablename="schedule has-team-logos align-left"

csvglue = ","
loadcsvdir = "/users/johncyclist22/documents/footpick/data/csv/"
resultscsvdir = "/users/johncyclist22/documents/footpick/data/csv/"
dbdir = "/users/johncyclist22/documents/footpick/data/db/"
csvfilepre = "Yahoo Pickem - "
csvfilepost = " Results.csv"
csvfilepost12 = " Results wk12.csv"
csvfile2019 = " Results 19.csv"
csvfile2018 = " Results.csv"
mastercsv = "NFL Results Master - 171819.csv"
r_mastercsv = "NFL Results Master - 171819.csv"
plotfile = "NFL Test Plot.csv"
year = "2018"
year18 = "2018"
year19 = "2019"
currentseason = year19
year17 = "2017"
csvoutput = "-resdetails.csv"
today = datetime.today()
processdate = str(today.year) + "-" + str(today.month).zfill(2) + "-" + str(today.day).zfill(2)
elodtypes = {'season' : pan.Int64Dtype(),'neutral' : pan.Int64Dtype(), 'playoff' : object, 'team1' : object, 'team2' : object, 'elo1_pre' : np.float64, 'elo2_pre' : np.float64, 'elo_prob1' : np.float64, 'elo_prob2' : np.float64, 'elo1_post' : np.float64, 'elo2_post' : np.float64, 'qbelo1_pre' : np.float64, 'qbelo2_pre' : np.float64, 'qb1' : object, 'qb2' : object, 'qb1_value_pre' : np.float64, 'qb2_value_pre' : np.float64, 'qb1_adj' :np.float64, 'qb2_adj' :np.float64, 'qbelo_prob1' : np.float64, 'qbelo_prob2' : np.float64, 'qb1_game_value' :np.float64, 'qb2_game_value' :np.float64, 'qb1_value_post' : np.float64, 'qb2_value_post' :np.float64, 'qbelo1_post' : np.float64, 'qbelo2_post' : np.float64, 'score1' : pan.Int64Dtype(), 'score2' : pan.Int64Dtype() } 

def writevartofile(var, sendfile):
    v = open(sendfile,"w")
    v.write(str(var))
    print("contents written to file.... ")
    return True

# create a subroutine
def dleloratings():
    print("downloading elo file on " + processdate)

    # if an existing nflelo file exists - remove it
    if os.path.isfile('/Users/johncyclist22/Downloads'+'nfl_elo_latest.csv'):
        os.remove('/Users/johncyclist22/Downloads'+'nfl_elo_latest.csv')
 
    # hit the web address - download the file into download - https://projects.fivethirtyeight.com/nfl-api/nfl_elo_latest.csv
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    driver = webdriver.Chrome(options=options)
    url = 'https://projects.fivethirtyeight.com/nfl-api/nfl_elo_latest.csv'
    driver.get(url)
    driver.close()

    # copy the new file into the data directory - create new subdirectory elommdd - and backup into that directory
    copyfile('/Users/johncyclist22/Downloads/'+'nfl_elo_latest.csv', '/Users/johncyclist22/Documents/footpick/Data/nfl-elo/'+'nfl_elo_latest.csv')
    if os.path.isdir('/Users/johncyclist22/Documents/footpick/Data/nfl-elo/nfl-elo-'+processdate):
        pass
    else:
        os.mkdir('/Users/johncyclist22/Documents/footpick/Data/nfl-elo/nfl-elo-'+processdate)

    # backup the file
    copyfile('/Users/johncyclist22/Documents/footpick/Data/nfl-elo/'+'nfl_elo_latest.csv', '/Users/johncyclist22/Documents/footpick/Data/nfl-elo/nfl-elo-'+processdate+'/nfl_elo_latest.csv')


def getpopdate(weeknumber, gamedays):

    # g_url = "https://football.fantasysports.yahoo.com/pickem/62991/19/picks?week="
    # # weeknumber = str(7)     # this will be a paramater 
    # y_url = g_url + str(weeknumber)
    weekdict = {'weeknumber': '', 'gameday': ''}
    gamedays = pan.DataFrame(columns={'weeknumber', 'gameday'})    
    
    year = '2019'

    # response = uReq(y_url) 
    # html_source = response.read()
    # response.close()										# close the page - dont be rude
    # soup = BeautifulSoup(html_source, "lxml")
    # dte_table = soup.find("table", {"id": "ysf-picks-table"})
    # gamesdte = dte_table.findAll("tr")
    # for row in gamesdte:
    #     for cell in row.findAll('td', {'class' : 'l'}):
    #         gameday = cell.text.strip()
    #         slashpos = gameday.find("/")
    dfnflschedule = pan.read_csv(loadcsvdir+"NFL_Gamedays_2019.csv")
    for index, games in dfnflschedule.iterrows():
        if dfnflschedule.loc[index,'Week'] == weeknumber:
            weekdict['gameday'] = dfnflschedule.loc[index,'Date']
            weekdict['weeknumber'] = str(weeknumber)
            gamedays = gamedays.append(weekdict, ignore_index=True)
    
    gamedays = gamedays.drop_duplicates()
    # print(gamedays)
    return gamedays

def getpoppicks(weeknumber):

    
    ybase_url = "https://football.fantasysports.yahoo.com/pickem/62991/19/picks?week="
    # weeknumber = str(3)
    y_url = ybase_url+str(weeknumber)
    ypopick = pan.DataFrame() 

    response = uReq(y_url) 
    html_source = response.read()
    response.close()										# close the page - dont be rude
    soup = BeautifulSoup(html_source, "lxml")
    pick_table = soup.find("table", {"class": "yspNflPickGroupPickTable"})
    games = pick_table.findAll("tr")
    gamedict = {'team1': '', 'poppick1': '', 'team2': '', 'poppick2': '', 'idx_team1': 0, 'idx_team2': 0}
    gamestrung = {'idx_team': 0, 'poppick': ''}
    poppicktable = pan.DataFrame()
    poppickstrung = pan.DataFrame()
    dfteams = pan.read_csv(loadcsvdir+"NFL_Teams.csv", index_col=1)
    
    os.system("clear")
    x=0
    for passer in games:
        # print("pass number: " + str(x))
        # print(passer)
        if passer.contents[0] == '\n':
            pass
        else:
            for picker in passer.contents:
                
                if str(picker).find("number pick-") > -1:
                    poppick = picker.text.strip()
            # print(poppick)
            if poppick[0] != "@": 
                if gamedict['poppick1'] == "":
                    gamedict['poppick1'] = float(poppick.strip('%')) / 100.0 
                else:
                    gamedict['poppick2'] = float(poppick.strip('%')) / 100.0 

            atag = passer.findAll('a', href=True)    
            if atag[0].contents != []: 
                team=str(atag[0].contents[0])
                if "<" in team: 
                    team=team[3:]
                    team=team.rstrip('</b>') 
            if gamedict['team1'] == "":
                gamedict['team1'] = team
                gamedict['idx_team1'] = dfteams.loc[team].idx_num
            else:
                gamedict['team2'] = team
                gamedict['idx_team2'] = dfteams.loc[team].idx_num

        if gamedict['team2'] != '':
            poppicktable = poppicktable.append(gamedict, ignore_index=True)
            gamestrung['idx_team'] = gamedict['idx_team1']
            gamestrung['poppick'] = gamedict['poppick1']
            poppickstrung = poppickstrung.append(gamestrung, ignore_index=True)
            gamestrung['idx_team'] = gamedict['idx_team2']
            gamestrung['poppick'] = gamedict['poppick2']
            poppickstrung = poppickstrung.append(gamestrung, ignore_index=True)
            gamedict = {'team1': '', 'poppick1': '', 'team2': '', 'poppick2': '', 'idx_team1': 0, 'idx_team2': 0}
        x+=1

    return poppickstrung
