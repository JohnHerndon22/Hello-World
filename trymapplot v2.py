import numpy as np
from numpy import linalg
import matplotlib.pyplot as plt
import pandas as pan
from common import *

plotfile = "NFL Plot Test.csv"

def createplotfile():

    if os.path.isfile(resultscsvdir+plotfile): 
        copyfile(resultscsvdir+plotfile, resultscsvdir+"BU-"+plotfile)
        # os.remove(resultscsvdir+r_mastercsv)
        
    schdata = pan.read_csv(resultscsvdir+r_mastercsv, index_col=0)
    os.system("clear")

    for index, game in schdata.iterrows():
        
        if game["espnhomepred"] > .5:
            schdata.loc[index, "selectteam"] = game['sht_hometeam']
            schdata.loc[index,"selectpred"] = game['espnhomepred']

        else:
            schdata.loc[index, "selectteam"] = game['sht_awayteam']
            schdata.loc[index,"selectpred"] = game['espnawaypred']

        if game["homepoppick"] > .5:
            schdata.loc[index, "poppickteam"] = game['sht_hometeam']
            schdata.loc[index,"poppickpred"] = game['homepoppick']
            
        else:
            schdata.loc[index, "poppickteam"] = game['sht_awayteam']
            schdata.loc[index,"poppickpred"] = game['awaypoppick']
            

        if game['homescore'] > game['awayscore']:
            schdata.loc[index, "winteam"] = game['sht_hometeam']
        elif game['homescore'] < game['awayscore']:
            schdata.loc[index, "winteam"] = game['sht_awayteam']
        else:
            schdata.loc[index, "winteam"] = "tie"
            
        schdata.loc[index, "mov"] = abs(schdata.loc[index,'homescore'] - schdata.loc[index,'awayscore'])
    #### run this - then in the other program - if the select team = winteam - + otherwise - 
    
    schdata.to_csv(resultscsvdir+plotfile)


def plot_results(title, year, predcolumn, df, xlab, actmov):
    plt.title(title)
    dfresults = df.loc[f'{year}']    ### eeror here - how to send a moniker thru 
    # dfresults = dfresults.set_index('index')   
    dfresults = dfresults.reset_index()   
    mov = dfresults[f'{actmov}']
    # print(dfresults)
    pred = dfresults[f'{predcolumn}']
    plt.xlabel(xlab)
    plt.ylabel('MOV')
    plt.text(0.5, 38,'Std Dev')
    #  ,     transform = ax.transAxes)
    A = np.vstack([pred, np.ones(len(pred))]).T
    m, c = np.linalg.lstsq(A, mov, rcond=None)[0]
    _ = plt.plot([.5, 1], [.5, 1], 'k-', lw=1, label='Win/Loss')
    _ = plt.plot(pred, mov, 'o', label='Original data', markersize=5)
    _ = plt.plot(pred, m*pred + c, 'r', label='Fitted line')
    _ = plt.legend()
    plt.show()
    
    fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)
    axs.hist(mov, len(mov))
    plt.show()



def main():
    # first build the revised file - NFL PLot Test.csv
    createplotfile()

    dfstart = pan.read_csv(resultscsvdir+plotfile,index_col=0)
    for index, game in dfstart.iterrows():
        if game['winteam'] != game['selectteam']:
            dfstart.loc[index,'e_actmov'] = game['mov']*-1
        else:
            dfstart.loc[index,'e_actmov'] = game['mov']

        if game['winteam'] != game['poppickteam']:
            dfstart.loc[index,'p_actmov'] = game['mov']*-1
        else:
            dfstart.loc[index,'p_actmov'] = game['mov']

    dfstart = dfstart.set_index('season')
    
    years = ("2017", "2018", "2019")

    for year in years:
        plot_results(year + " - Season - ESPN", year, 'selectpred', dfstart, 'ESPN Prediction', 'e_actmov')
        plot_results(year + " - Season - Popular", year, 'poppickpred', dfstart, 'Popular Prediction', 'p_actmov')
        

        # regression from example numpy

main()
quit()





