#build NFL Schedule
from selenium import webdriver  

from bs4 import BeautifulSoup, Comment
from urllib.request import urlopen as uReq 
import os
from os import path
from datetime import datetime 
import csv
import codecs
from decimal import *
from shutil import copyfile
from operator import itemgetter, attrgetter
from common import *
import pandas as pan


# def writevartofile(var, sendfile):
#     v = open(sendfile,"w")
#     v.write(str(var))
#     print("contents written to file.... ")
#     return True

# class game(object):

#     def __init__(self, gameid ,hometeam ,homescore,espnhomepred,awayteam ,awayscore ,espnawaypred ,thursgame):
#         self.gameid = gameid
#         self.hometeam = hometeam
#         self.homescore = homescore
#         self.espnhomepred = espnhomepred
#         self.awayteam = awayteam
#         self.awayscore = awayscore
#         self.espnawaypred = espnawaypred
#         self.thursgame = thursgame

#     def __repr__(self):
#         return '{0.gameid} {0.hometeam} {0.homescore} {0.espnhomepred} {0.awayteam} {0.awayscore} {0.espnawaypred} {0.thursgame}'.format(self)

class webdata: 
    # merge batter class and this one - make the data about batter - this is why the sort would not work!
    def __init__(self, url, tablename, dfsched):
        self.url = sch_url
        self.tablename = sch_tablename
        self.dfsched = pan.DataFrame()

    def get_all_games(self):
        # process the html 
        weeknumber = 1
        g_url = sch_url + str(weeknumber) 
        while weeknumber<=3:

            awaytrigger = True
            byeweek = True
            
            g_url = sch_url + str(weeknumber)
            browser = webdriver.Chrome()
            browser.get(g_url)
            html_source = browser.page_source
            browser.quit()

            soup = BeautifulSoup(html_source, "lxml")
            whole_schedule = soup.find("div", {"id": "sched-container"})
            gamedict = {'weeknumber': 0, 'gameid': '', 'sht_hometeam':'', 'sht_awayteam': '', 'idx_hometeam': 0, 'idx_awayteam': 0, 'espnhomepred': .000, 'espnawaypred': .000, 'homescore': 0, 'awayscore': 0, 'homepopick':.000, 'awaypoppick': .000}
            
            for a in whole_schedule.findAll('a', href=True):
                if "gameId" in a['href']:
                    gameidloc = a['href'].find("gameId")
                    gamedict['gameid'] = a['href'][gameidloc+7:]
                    byeweek = False
                elif "/nfl/team" in a['href']:
                    teamloc = a['href'].find("/name/")
                    teambig = a.attrs['href'][teamloc+6:]
                    endslash = teambig.find("/") 
                    if awaytrigger:
                        gamedict["sht_awayteam"] = teambig[:endslash]
                        awaytrigger = False
                    else:
                        gamedict["sht_hometeam"] = teambig[:endslash]
                else:
                    if byeweek: 
                        pass
                    else:
                        gamedict["weeknumber"] = weeknumber
                        self.dfsched = self.dfsched.append(gamedict, ignore_index = True)
                        awaytrigger = True
                        byeweek = True

            weeknumber+=1
            g_url=sch_url+str(weeknumber)

        return self.dfsched

# data structure for game_schedule.db:

        # gameid - text 
        # hometeam - text
        # homescore - int
        # espnhomepred - float - .000
        # homepoppick - float - .000
        # awayteam - text
        # awayscore - int
        # espnawaypred - float - .000
        # awaypoppick - float - .000
        # thursgame - boolean


def main():    

    ##### run the entire schedule - get all remaining weeks ##### 

    os.system('clear')                                      # clear the sscreen
    print("processing NFL schedule data......\n")
    # global allgames
    # allgames = []
    dfsched = []

    #grab the data from the mlb website
    schedule=webdata(sch_url,sch_tablename,dfsched).get_all_games()
    schedule.to_csv(resultscsvdir+"NFL Schedule 2019wk1-2.csv")

    # check to see if an existing schedule exists - then copy to backup
    # if path.isfile(loadcsvdir+"NFL Schedule 2019.csv"):
    #     copyfile(loadcsvdir+"NFL Schedule 2019.csv", loadcsvdir+"BU-"+"NFL Schedule 2019.csv")
    #     copyfile(resultscsvdir+"NFL Schedule 2019.csv", loadcsvdir+"NFL Schedule 2019.csv")
    
    print(schedule)

main()
    

