#getespnpicks.py
#v23 - bypass games in progress
#v24 - change methodology using ESPN 538 as starter

# from selenium import webdriver  

from bs4 import BeautifulSoup, Comment
# from urllib.request import urlopen as uReq 
import os
from os import path
import sys
from datetime import datetime 
import csv
import codecs
from decimal import *
from shutil import copyfile
from operator import itemgetter, attrgetter
from common import *
# from getpoppick import *
import pandas as pan
import numpy as np
import PySimpleGUI as sg

# local variables needed 
# gameid = ""
# baseurl = "https://www.espn.com/nfl/game/_/gameId/"
    
def getweekpredictions(dfsched, weeknumber, dfpoppicks, dfteams, window, dfeloratings):
    
    c_dfsched = dfsched.copy()
    # loop here thru
    for index, gameid in c_dfsched.iterrows():   
        
        homepred = .000
        awaypred = .000
        # game_url = url + str(gameid['gameid'])

        # open and grab the web page - to be deleted
        # response = uReq(game_url) 
        # html_source = response.read()
        # response.close()										# close the page - dont be rude
        # soup = BeautifulSoup(html_source, "lxml")    
        # game_predictor = soup.find("div", {"class": "chart-container"})

        #### instead - download the file from 538 - https://data.fivethirtyeight.com/#nfl-elo
        #### invoke the subroutine
        #### also go and get the popular pick % from yahpoo - https://football.fantasysports.yahoo.com/pickem/22481/52
        #### see get poppick for example #####

        # determine what the HOME & AWAY team is based on the game id - gets the shortname
        hometeam = c_dfsched.loc[index,'sht_hometeam'].lower() 
        awayteam = c_dfsched.loc[index,'sht_awayteam'].lower()  
        
        # espnhomepred = game_predictor.find("span", {"class": "value-home"}).text.strip()
        h_dfeloratings = dfeloratings.set_index('team1')
        espnhomepred = h_dfeloratings.loc[hometeam.upper(),'qbelo_prob1']
        # espnawaypred = game_predictor.find("span", {"class": "value-away"}).text.strip()
        a_dfeloratings = dfeloratings.set_index('team2')
        espnawaypred = a_dfeloratings.loc[awayteam.upper(),'qbelo_prob2']


        ##### for some reason this is picking the wrong team (always the home team) - no pick category % ties in points

        hometeam = hometeam.lower()
        awayteam = awayteam.lower()

        c_dfsched.loc[index,'espnhomepred'] = espnhomepred 
        c_dfsched.loc[index,'espnawaypred'] = espnawaypred 
        output = "Analyzing game: " + str(gameid['gamematch']) + "-> " + awayteam + "(" + str(espnawaypred) + ") @ " + hometeam + "(" + str(espnhomepred) + ")"
        outputtowindow(output, window)

        # use the shortnames and get the index from the dfteams file for both home and away
        c_dfsched.loc[index,'idx_hometeam'] = dfteams.loc[hometeam,'idx_num']
        c_dfsched.loc[index,'idx_awayteam'] = dfteams.loc[awayteam,'idx_num']
        
        idx_home = c_dfsched.loc[index,'idx_hometeam'] 
        idx_away = c_dfsched.loc[index,'idx_awayteam']

        # set the popular picks
        c_dfsched.loc[index,'homepoppick'] = dfpoppicks.loc[idx_home,'poppick']
        c_dfsched.loc[index,'awaypoppick'] = dfpoppicks.loc[idx_away,'poppick']

    return c_dfsched

def gameanalyzer(dfsched, weeknumber, dfpoppicks, dfteams, window):
    ### takes the predictions and parses according to the rules set out 
    # make a copy gets rid of the warnings
    c_dfsched = dfsched.copy()
    
    # calculate groups 1 & 2 (7 and 6) & create espn largest & smallest pick columns
    c_dfsched["espnmaxpick"] = c_dfsched[["espnhomepred","espnawaypred"]].max(axis=1)
    c_dfsched["popmaxpick"] = c_dfsched[["homepoppick","awaypoppick"]].max(axis=1)        

    # determine catagory level - use conditonals for each game
    c_dfsched['pickcat'] = np.where(c_dfsched['espnmaxpick']>=.65, 7, 1)    
    c_dfsched['pickcat'] = np.where((c_dfsched['espnhomepred'] >= .60) & (c_dfsched['espnhomepred']<.65),6,c_dfsched['pickcat'])
    c_dfsched['pickcat'] = np.where((c_dfsched['espnhomepred'] == .000),0,c_dfsched['pickcat'])      # FOR games in progresss
    
    # if poppick (both home and away): make category 5 
    c_dfsched["espnmaxpick"] = np.where((c_dfsched['pickcat']==1) & (c_dfsched["homepoppick"] >.849), c_dfsched["espnhomepred"],c_dfsched["espnmaxpick"])
    c_dfsched["pickcat"] = np.where((c_dfsched['pickcat']==1) & (c_dfsched["homepoppick"] >.849),5,c_dfsched["pickcat"])
    c_dfsched["espnmaxpick"] = np.where((c_dfsched['pickcat']==1) & (c_dfsched["awaypoppick"] >.849), c_dfsched["espnawaypred"],c_dfsched["espnmaxpick"])
    c_dfsched["pickcat"] = np.where((c_dfsched['pickcat']==1) & (c_dfsched["awaypoppick"] >.849),5,c_dfsched["pickcat"])

    # now sort and assign points - post processing - 
    # determine selected espn % (could be espnbigpick) & determine the selected team based onthe pick selected
    c_dfsched['teamselected'] = np.where(c_dfsched['espnhomepred']==c_dfsched['espnmaxpick'],c_dfsched['sht_hometeam'],c_dfsched['sht_awayteam'])
    c_dfsched['espnselected'] = np.where((c_dfsched['sht_awayteam']==c_dfsched['teamselected']),c_dfsched['espnawaypred'],c_dfsched['espnhomepred'])
    
    # sort by catagory number+espn selected percentage - group by weeknumber - assign ranks
    c_dfsched = c_dfsched.sort_values(['weeknumber','pickcat'],ascending=True)
    c_dfsched['popranktb'] = c_dfsched["popmaxpick"]/1000
    c_dfsched["t_ranker"] = c_dfsched["pickcat"]+c_dfsched["espnselected"]+c_dfsched['popranktb']
    c_dfsched["ptsalloc"] = c_dfsched.groupby("weeknumber")["t_ranker"].rank("dense", ascending=True)
    c_dfsched = c_dfsched.sort_values(['ptsalloc'],ascending=False)
    
    # return the schedule back to the main function
    return c_dfsched

def outputtowindow(output, window):
    print(output)
    window.Refresh()
    return True

def yesnoanswer(question):

    answer = '' 
    layout = [[sg.Text(question)],      
                 [sg.InputText()],      
                 [sg.Submit()]]
                #  , sg.Cancel()]]            
    window = sg.Window('Fantasy Analysis', layout)            
    event, values = window.Read()    
    window.Close()        
    answer = values[0]    

    return answer

def getweektoprocess():

    retweek = 0 
    layout = [[sg.Text('Which Week to Process?')],      
                 [sg.InputText()],      
                 [sg.Submit(), sg.Cancel()]]            
    window = sg.Window('Fantasy Analysis', layout)            
    event, values = window.Read()    
    window.Close()        
    retweek = int(values[0])    

    return retweek

def writepickresults(dfsched, weeknumber):
    dfmasterfile = pan.read_csv(resultscsvdir+r_mastercsv)
    i_dfsched = dfsched.set_index('gamematch')
    print(dfmasterfile)
    for index, game in dfmasterfile.iterrows():
        if (game.weeknum == weeknumber) & (str(game.season) == currentseason):
            gamematch = dfmasterfile.loc[index,'gamematch']
            # dfmasterfile.loc[index,'homescore'] = dfsched.loc[gamematch,'score1']
            # dfmasterfile.loc[index,'awayscore'] = dfsched.loc[gamematch,'score2']
            dfmasterfile.loc[index,'homepoppick'] = i_dfsched.loc[gamematch,'homepoppick']
            dfmasterfile.loc[index,'espnhomepred'] = i_dfsched.loc[gamematch,'espnhomepred']	
            dfmasterfile.loc[index,'awaypoppick'] = i_dfsched.loc[gamematch,'awaypoppick']	
            dfmasterfile.loc[index,'espnawaypred'] = i_dfsched.loc[gamematch,'espnawaypred']	
            dfmasterfile.loc[index,'gameid'] = i_dfsched.loc[gamematch,'gameid']	
            dfmasterfile.loc[index,'idx_awayteam'] = i_dfsched.loc[gamematch,'idx_awayteam']	
            dfmasterfile.loc[index,'idx_hometeam'] = i_dfsched.loc[gamematch,'idx_hometeam']
    
    # now write back to csv & return
    if os.path.isfile(resultscsvdir+r_mastercsv): 
        copyfile(resultscsvdir+r_mastercsv, resultscsvdir+"backup/BU-"+r_mastercsv)
    dfmasterfile.to_csv(resultscsvdir+r_mastercsv, index=False)
    return

def main():

    # ask for the week to cover - weeknumber - get the popular picks - set the index
    # weeknumber=int(input('What is the NFL week? ')
    os.system('clear')                                      # clear the sscreen
    #### create a dataframe with the keyhome teams #####

    # get latest ratings and scores from the 538 website
    dleloratings()      
    weeknumber = getweektoprocess()

    picksetcsv = year19 + "-pickset-" + str(weeknumber) + "-" + "week" +".csv"
    dfpoppicks = pan.DataFrame()
    dfgamedays = pan.DataFrame()
    dfeloratings_wk = pan.DataFrame()

    # open the nfl master schedule and place into dataframe

    dfpoppicks = getpoppicks(weeknumber)            # get the yahoo pop picks for the week
    dfeloratings_2019 = pan.read_csv('/Users/johncyclist22/Documents/footpick/Data/nfl-elo/'+'nfl_elo_latest.csv', index_col=0) 

    # get the scheduled dates for the week - will need for pulling that week's games
    dfgamedays = getpopdate(weeknumber, dfgamedays)
    dfeloratings_wk = dfeloratings_2019.loc[dfgamedays['gameday']]
    dfpoppicks = dfpoppicks.set_index(['idx_team'])
    
    # get the teams with indexes for each te
    dfteams = pan.read_csv(loadcsvdir+"NFL_Teams.csv", index_col=2)

    # does a prediction already exist - ask "do you want to overwrite with new one?"
    if os.path.isfile(resultscsvdir+picksetcsv): 
        result = yesnoanswer("Pickset " + picksetcsv + " already exists - overwrite [Y/n]? ")
        if result == "Y":
            ##### read the current file and place into a data frame extdfsched ######
            copyfile(resultscsvdir+picksetcsv, resultscsvdir+"backup/BU-"+picksetcsv)
            # os.remove(resultscsvdir+picksetcsv)
        else:
            ##### put this in a window with an ok button - see the example above #####
            sg.Popup('Ended.....')
            quit()

    #setup output window
    layout = [[sg.Text('Schedule for week: ' + str(weeknumber), size=(40, 1),font='Courier 12')],[sg.Output(size=(225, 70))],[sg.Button("Process"), sg.Button('EXIT')]]
    window = sg.Window('Fantasy Analysis', layout)      

    while True:      
        
        (event, value) = window.Read()      
        # write to result set - name the result set by day
        if event == 'EXIT'  or event is None:    
            break # exit button clicked
        else:    
            # open the file - build the dataframe - dfsched
            dfschedfull = pan.read_csv(resultscsvdir+"NFL Schedule 2019.csv", index_col=0)
            dfsched = dfschedfull[(dfschedfull['weeknumber'] == weeknumber)]
            c_dfsched = dfsched.copy()        
            dfsched = getweekpredictions(c_dfsched, weeknumber, dfpoppicks, dfteams, window, dfeloratings_wk)
            # print(dfsched)
            # go thru the gameanalyzer to parse and ranK each game
            c_dfsched = dfsched.copy()        
            dfsched = gameanalyzer(c_dfsched, weeknumber, dfpoppicks, dfteams, window)

            print("at end....\n\n")            
            print(dfsched.to_string())
            window.Refresh()

            dfsched.to_csv(resultscsvdir+picksetcsv)
    
    window.Close()
    writepickresults(dfsched, weeknumber)
            
main()
quit()
