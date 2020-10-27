import requests
import json
import os
from roleReference import TIERS, DIVISIONS, LANES, BOT_ROLES
import getData
import analysis


def main(summonerName, numGames, champion):
    print(getData.getUsersStatsToReview(summonerName, numGames, champion))


if __name__ == "__main__":
    numGames = ""
    print("Welcome to int.gg, an app to see if you've been running it down!")

    summonerName = input("Please enter your summoner name: ")
    numGames = int(input("Please enter the number of games you would like reviewed (max 100): "))
    champion = input("If you would like your matches on a specific champion to be reviewed, please enter that "
                     "champion's name here, if not, click enter: ")

    if champion == "":
        championNum = None
    else:
        with open("championsDict.json", "r") as infile:
            championDict = json.load(infile)
            championNum = championDict[champion]

    main(summonerName, numGames, championNum)