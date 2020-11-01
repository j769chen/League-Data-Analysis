import requests
import json
import os
from tabulate import tabulate
from roleReference import TIERS, DIVISIONS, LANES, BOT_ROLES, STATS_WEIGHTINGS, FORMAL_NAMES
import getData
import analysis


def main(summonerName, numGames, champion, lane, role=None):
    if role == None:
        userStats, tier, division = getData.getUsersStatsToReview(summonerName, lane, numGames, champion)
    else:
        userStats, tier, division = getData.getUsersStatsToReview(summonerName, lane, numGames, role, champion)

    if lane == LANES['Middle(Match History)']:  # Change this back so that it is 'MIDDLE' for match analysis. See roleReference line 26 for reasoning
        lane = LANES['Middle']

    if lane == LANES['Bottom']:
        importantStats = STATS_WEIGHTINGS[role]
    else:
        importantStats = STATS_WEIGHTINGS[lane]

    statNames = []
    for keys in importantStats:
        statNames.append(FORMAL_NAMES[keys])

    analysis.analyze(userStats, statNames, importantStats, tier, division, lane, role)


if __name__ == "__main__":
    numGames = 0
    print("Welcome to int.gg, an app to see if you've been running it down!")

    summonerName = input("Please enter your summoner name (case sensitive): ")

    while numGames <= 0 or numGames > 10:
        try:
            numGames = int(input("Please enter the number of games you would like reviewed (1-10): "))
            if numGames <= 0 or numGames > 10:
                print("That is not a valid number, please enter an integer between 1 and 10.")
        except ValueError:
            print("That input is not an integer!")

    champion = input("If you would like your matches on a specific champion to be reviewed, please enter that "
                     "champion's name here. If not, click enter: ")

    if champion == "":
        championNum = None
    else:
        with open("championsDict.json", "r") as infile:
            championDict = json.load(infile)
            championNum = championDict[champion]

    lane = input("Please enter which lane you would like your games to be reviewed for (Top, Jungle, Middle, Bottom): ")
    if lane == 'Bottom':
        role = input("Please enter if you play ADC or Support (ADC, Support): ")
        main(summonerName, numGames, championNum, LANES[lane], BOT_ROLES[role])
    elif lane == 'Middle':
        main(summonerName, numGames, championNum, LANES['Middle(Match History)'])
    else:
        main(summonerName, numGames, championNum, LANES[lane])