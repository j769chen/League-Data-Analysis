import json
from roleReference import LANES, BOT_ROLES, STATS_WEIGHTINGS, FORMAL_NAMES
import getData
import analysis


def main(summonerName, numGames, champion, lane, role=None):
    userStats, tier, division, actualNumGames = getData.getUsersStatsToReview(summonerName, lane, numGames, role, champion)

    if lane == LANES['Middle(Match History)']:  # Change this back so that it is 'MIDDLE' for match analysis. See roleReference line 26 for reasoning
        lane = LANES['Middle']

    if lane == LANES['Bottom']:
        importantStats = STATS_WEIGHTINGS[role]
    else:
        importantStats = STATS_WEIGHTINGS[lane]

    statNames = []
    for keys in importantStats:
        statNames.append(FORMAL_NAMES[keys])

    userStatsTable, comparionStatsTable, statsPercentiles, letterGrade, congratsMsg, listOfTips = analysis.analyze(userStats, statNames, importantStats, tier, division, lane, role)

    print("Here is your evaluation:")
    print("Your stats for the past {} games:".format(actualNumGames))
    print(userStatsTable + '\n')
    if lane == LANES['Bottom']:
        print("Here are your average stats compared to the average {} {} {} player".format(tier, division, role))
    else:
        print("Here are your average stats compared to the average {} {} {} player".format(tier, division, lane))
    print(comparionStatsTable + '\n')

    for stats in statsPercentiles:
        if lane == LANES['Bottom']:
            print("You are within the top {} of {} {} {} players in terms of {}".format(100-statsPercentiles[stats],
                                                                                        tier, division, role, stats))
        else:
            print("You are within the top {} of {} {} {} players in terms of {}".format(100 - statsPercentiles[stats],
                                                                                        tier, division, lane, stats))

    print("Your overall performance: {} \n".format(letterGrade))

    print("Here are some things you do well in game:")
    for comment in congratsMsg:
        print(comment)

    print("\n")
    print("Here are some things you should try to improve on: \n")
    for comment in listOfTips:
        print(comment)


if __name__ == "__main__":
    numGames = 0
    print("Welcome to int.gg, an app to see if you've been running it down!")

    summonerName = input("Please enter your summoner name: ")

    while numGames <= 0 or numGames > 10:
        try:
            numGames = int(input("Please enter the number of games you would like reviewed (1-10): "))
            if numGames <= 0 or numGames > 10:
                print("That is not a valid number, please enter an integer between 1 and 10.")
        except ValueError:
            print("That input is not an integer!")

    with open("championsDict.json", "r") as infile:
        championDict = json.load(infile)
        champion = None
        while champion not in championDict and champion != "":
            champion = input("If you would like your matches on a specific champion to be reviewed, please enter that "
                             "champion's name here. If not, click enter: ")

            if champion not in championDict and champion != "":
                print("That is not a valid champion!")

        if champion == "":
            championNum = None
        else:
            championNum = championDict[champion]

    lane = ""
    while lane != 'Top' and lane != 'Jungle' and lane != 'Middle' and lane != 'Bottom':
        lane = input("Please enter which lane you would like your games to be reviewed for (Top, Jungle, Middle, "
                     "Bottom): ")

        if lane != 'Top' and lane != 'Jungle' and lane != 'Middle' and lane != 'Bottom':
            print("That is not a valid lane!")

    if lane == 'Bottom':
        role = ""
        while role != 'ADC' and role != 'Support':
            role = input("Please enter if you play ADC or Support (ADC, Support): ")

            if role != 'ADC' and role != 'Support':
                print("That is not a valid role!")

        main(summonerName, numGames, championNum, LANES[lane], BOT_ROLES[role])
    elif lane == 'Middle':
        main(summonerName, numGames, championNum, LANES['Middle(Match History)'])
    else:
        main(summonerName, numGames, championNum, LANES[lane])