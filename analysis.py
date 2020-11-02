import json
from tabulate import tabulate
from roleReference import LANES, BOT_ROLES, LETTER_GRADES, FORMAL_NAMES
from getData import getFilepath


def readMultipleJSONS(tier, division, lane, role=None): # Read JSONs from file into a list
    statsList = []
    jsonName = getFilepath(tier, division, lane, role)

    with open(jsonName, 'r') as infile:
        for lines in infile:
            statsList.append(json.loads(lines))

    return statsList


def getAverageRecordedStats(tier, division, lane, role=None, toFile=True, fromFile=True, *args): # Gets data from JSON Dump for a tier and role and outputs average stats to another file
    averageStats = {}
    if fromFile:
        statsList = readMultipleJSONS(tier, division, lane, role)
    else:
        statsList = args[0]

    for i in statsList:
        for key in i:
            if key not in averageStats:
                averageStats[key] = i[key]
            else:
                averageStats[key] += i[key]

    for keys in averageStats:
        averageStats[keys] = round(averageStats[keys]/len(statsList), 2)

    if toFile:
        averageFileName = getFilepath(tier, division, lane, role, True)

        with open(averageFileName, 'w') as outfile:
            json.dump(averageStats, outfile)

    return averageStats


def insertionSort(list1): # Simple, O(n^2) sorts better for smaller datasets since you don't perform unecessary recursion
    for i in range(1, len(list1)):
        j = i - 1
        key = list1[i]
        while j >= 0 and key < list1[j]:
            list1[j+1] = list1[j]
            j -= 1
        list1[j+1] = key


def getPivot(list1, low, high): # Implement "median of three" pivot selection rule to account for worst case of near sorted list
    sorted([list1[(high + low) // 2], low, high])
    return int(sorted([list1[(high + low) // 2], low, high])[1])


def partition(list1, low, high):
    pivotIndex = getPivot(list1, low, high)
    list1[pivotIndex], list1[low] = list1[low], list1[pivotIndex] # Swap pivot into index 0
    pivotValue = list1[low]
    i = low - 1
    j = high + 1

    while True:
        i = i + 1
        j = j - 1
        while list1[i] < pivotValue:
            i = i + 1
        while list1[j] > pivotValue:
            j = j - 1
        if i >= j:
            return j
        list1[i], list1[j] = list1[j], list1[i]


def quickSortHelper(list1, low, high):
    if len(list1) <= 20: # If small list, avoid unnecessary recursion w/ quicksort by using insertion sort
        insertionSort(list1)
    elif low < high:

        p = partition(list1, low, high)

        quickSortHelper(list1, low, p)
        quickSortHelper(list1, p + 1, high)


def negateList(list1):
    for i in range(len(list1)):
        list1[i] *= -1
    return list1


def quickSort(list1, ascending=True):  # Quicksort function with option to sort in ascending or descending order.
    if not ascending:  # Negate list at beginning and at end so that it is sorted in opposite order
        list1 = negateList(list1)
    low = 0
    high = len(list1) - 1
    quickSortHelper(list1, low, high)

    if not ascending:
        list1 = negateList(list1)


def calculatePercentile(list1, userStat, statName): # Takes in a list of stats from JSON dump and gets percentile of the user's stat
    list1.append(userStat)

    if statName == 'deaths':  # For deaths, less is better
        ascending = False
    else:
        ascending = True

    quickSort(list1, ascending)

    return round((list1.index(userStat)+1)/len(list1) * 100, 2) # Generally if you are good, we say "you are among the top 1%", not top 100%, so return 100 - percentile of player


def getSpecificStatList(tier, division, lane, stat, role=None): # Gets the list of all values in a JSON dump for a specific stat (i.e. kills)
    statsList = readMultipleJSONS(tier, division, lane, role)
    returnList = []

    for entries in statsList:
        returnList.append(entries[stat])

    return returnList


def filterImportantStats(statsDict, importantStats): # Filters out non important stats based on respective STATS_WEIGHTINGS dict
    unwantedKeys = set(statsDict.keys()) - set(importantStats.keys())
    for keys in unwantedKeys:
        del statsDict[keys]


def getUserAndAverageTables(statNames, userStats, averageUserStats, averageELOStats): # Get tables for user's recent matches and comparison of average stats
    statTableValues = []

    for gameStats in userStats:
        statTableValues.append(gameStats.values())

    averageTableValues = [averageUserStats.values(), averageELOStats.values()]

    return tabulate(statTableValues, statNames), tabulate(averageTableValues, statNames)


def evaluatePlayerStatsPercentiles(tier, division, lane, averageUserStats, importantStats, role=None): # Returns a dictionary where the keys are stats and the values are the players percentile compared to players of the same ELO
    statsPercentiles = {}

    for stats in importantStats:
        statsPercentiles[stats] = calculatePercentile(getSpecificStatList(tier, division, lane, stats, role), averageUserStats[stats], stats)

    return statsPercentiles


def calculateLetterGrade(statsPercentiles, importantStats):
    """
    Letter grade calculation done as follows:
    For each role, different stats have different weigtings as outlined in the STATS_WEIGHTINGS dictionary in roleReference.

    For all roles, excluding deaths, all stat weightings add up to a total of 1, i.e. a perfect score with 0 deaths = 1/1 = 100%.

    Your score for each stat is determined by your percentile in that stat compared to average players in your elo:
        Example: I am in the top 20% of players for kills as an ADC, then my score out of 0.2 for kills is 80/100 * 0.2 = 0.16
    (If your stat is greater than 80% of players, generally say you are in top 20%)

    These values are calculated for each stat, and summed to get your raw total score.

    Your total score is then calculated by subtracting your percentile in deaths multiplied by the weighting of deaths for
    your respective role from your raw total score for N stats:
        Score = ((stat1 * weighting1 + stat2 * weigthing2 ... statN * weightingN) / 1) - (deaths * deathweighting)
    """

    percentage = 0

    for stats in statsPercentiles:
        percentage += (statsPercentiles[stats]/100)*importantStats[stats] # Multiply the weighting of each stat by user's performance, measured by percentile where higher is better

    for grades in LETTER_GRADES:
        if percentage >= LETTER_GRADES[grades]:
            return grades

    return -1  # In case something goes wrong, return -1 to indicate error


def getExcellentStats(statsPercentiles):  # Inform user about areas that they excel in to show them their strengths
    excellentStats = []

    for stats in statsPercentiles:
        if statsPercentiles[stats] >= 80:
            excellentStats.append(stats)

    return excellentStats


def getBelowAverageStats(statsPercentiles):  # Inform user about stats that they performed below average in
    belowAverageStats = []
    for stats in statsPercentiles:
        if statsPercentiles[stats] < 50:
            belowAverageStats.append(stats)

    return belowAverageStats


def congratulateUser(excellentStats, averageUserStats, tier, division, lane, role):  # Generates sentences to congratulate user for good stats and passes array of these sentences
    congratulations = []

    for stats in excellentStats:
        if lane == LANES['Bottom']:
            congratulations.append(
                "You are among the top 20% of {} {} {} {} players in terms of {}, with an average of {} "
                "per game.".format(tier, division, lane, role, FORMAL_NAMES[stats], averageUserStats[stats]))
        else:
            congratulations.append(
                "You are among the top 20% of {} {} {} players in terms of {}, with an average of {} "
                "per game.".format(tier, division, lane, FORMAL_NAMES[stats], averageUserStats[stats]))
    return congratulations


def generateTips(belowAverageStats, averageUserStats, lane, role):  # Generates tips for user to improve
    listOfTips = []

    # General Advice
    if 'deaths' in belowAverageStats:
        if 'visionScore' in belowAverageStats:
            listOfTips.append("You seem to be dying a lot and consistently have low vision scores, averaging {} deaths "
                              "and a vision score of only {} per game. Try placing more wards to prevent ganks."
                              .format(averageUserStats['deaths'], averageUserStats['visionScore']))
        elif 'earlyGameXp' in belowAverageStats: # When you die, you miss xp, so if you die alot your early game xp will be lower
            listOfTips.append("You seem to be dying a lot in lane, averaging {} deaths per game. try to learn how to "
                              "play around waves, trade at optimal times, and understand your matchups better"
                              .format(averageUserStats['deaths']))
        else: # If none of the above factors stand out too much, player may need to improve late game decisions
            listOfTips.append("You seem to be dying a lot later in the game, averaging {} deaths per game. You should try "
                              "and improve your macro game and map awareness to avoid getting caught out. Additionally, "
                              "you may need to improve your team-fighting".format(averageUserStats['deaths']))

    if role != BOT_ROLES['Support']: # Last hitting creeps is not important for supports
        if 'CS' in belowAverageStats:
            listOfTips.append("You are averaging {} CS per game, which is below average. This may be a result of "
                              "consistently losing lane. you should try and improve your last-hitting, and try playing safer "
                              "in lane".format(averageUserStats['CS']))

        if 'CS/M' in belowAverageStats:
            listOfTips.append("Your CS/M is quite low at around {} per game. This generally indicates that you are not "
                              "continuing to CS effectively after laning phase. In the mid/late game, make sure to catch"
                              "incoming waves that are not already taken by another laner.".format(averageUserStats['CS/M']))

    # Role specific advice
    if lane == LANES['Top']:
        if 'visionScore' in belowAverageStats:
            listOfTips.append("You are averaging around {} vision score and {} wards placed per game. As a top laner,"
                              "wards are essential for preventing ganks and for split pushing safely. You should "
                              "actively think about buying more wards.".format(averageUserStats['visionScore'], averageUserStats['wardsPlaced']))

        if 'timeCCingOthers' in belowAverageStats:
            listOfTips.append("You are not providing alot of CC to your team. In teamfights, try to engage onto the enemy"
                              "backline, or protect your own backline and peel for them")
    elif lane == LANES['Jungle']:
        if 'visionScore' in belowAverageStats:
            listOfTips.append("You are averaging around {} vision score and {} wards placed per game. As a jungler,"
                              "you should theoretically be placing the 2nd most wards on your team in order to gain map"
                              "and objective control. Additionally, wards will help you to track the opposing jungler."
                              "You should actively think about buying more wards.".format(averageUserStats['visionScore'], averageUserStats['wardsPlaced']))
    elif lane == LANES['Middle']:
        if 'visionScore' in belowAverageStats:
            listOfTips.append("You are averaging around {} vision score and {} wards placed per game. As a mid laner,"
                              "you should be warding around your lane to help your jungler fight for crabs, initiate roams,"
                              "and you track your lane opponent's movements. You should actively think about buying more "
                              "wards.".format(averageUserStats['visionScore'], averageUserStats['wardsPlaced']))

        if 'DPM' in belowAverageStats:
            listOfTips.append("Your DPM is quite low for a mid laner, at only {}. Mid laners are generally supposed to serve"
                              "as either the primary or secondary damage source. You may need to improve your mechanics "
                              "and team fighting".format(averageUserStats['DPM']))
    elif lane == LANES['Bottom']:
        if role == BOT_ROLES['ADC']:
            if 'visionScore' in belowAverageStats:
                listOfTips.append(
                    "You are averaging around {} vision score and {} wards placed per game. While ADCs ward less, it is still"
                    "important that you buy pinks in order to set up your jungler for ganks and for dragon control."
                    "wards.".format(averageUserStats['visionScore'], averageUserStats['wardsPlaced']))

            if 'DPM' in belowAverageStats:
                listOfTips.append("Your DPM is very low at only {}. As and AD carry, it is your job to be a primary damage dealer for"
                                  "your team. You should try to play more aggresive in lane, and be less afraid in "
                                  "teamfights. ".format(averageUserStats['DPM']))
        else:
            if 'visionScore' in belowAverageStats:
                listOfTips.append("You are averaging around {} vision score and {} wards placed per game. Supports should"
                                  "be warding around the map the most out of any role. In lane, make time to leave your ADC"
                                  "to ward around dragon and in the enemy's botside. Later in the game, you should be "
                                  "moving around with your jungler in order to get vision near important objectives such "
                                  "as baron or dragon.".format(averageUserStats['visionScore'], averageUserStats['wardsPlaced']))

            if 'visionWardsBoughtInGame' in belowAverageStats:
                listOfTips.append("You are only buying an average of {} pink wards per game. As a support, pink wards"
                                  "are one of the most useful tools for you to gain vision control around the map."
                                  "Every time you go to base, try to think about buying a pink ward"
                                  .format(averageUserStats['visionWardsBoughtInGame']))
    return listOfTips


def generateTakeaways(statsPercentiles, averageUserStats, tier, division, lane, role):

    excellentStats = getExcellentStats(statsPercentiles)
    belowAverageStats = getBelowAverageStats(statsPercentiles)

    goodPerformances = congratulateUser(excellentStats, averageUserStats, tier, division, lane, role)

    userCongratulations = congratulateUser(excellentStats, averageUserStats, tier, division, lane, role)

    listOfTips = generateTips(belowAverageStats, averageUserStats, lane, role)

    return userCongratulations, listOfTips


def analyze(userStats, statNames, importantStats, tier, division, lane, role):
    for gameStats in userStats:
        filterImportantStats(gameStats, importantStats)

    averageUserStats = getAverageRecordedStats(tier, division, lane, role, False, False, userStats) # Get average user stats

    averageELOStats = getAverageRecordedStats(tier, division, lane, role, False, True) # Get average stats for ELO from JSON dump
    filterImportantStats(averageELOStats, importantStats)
    userStatsTable, comparisonStatsTable = getUserAndAverageTables(statNames, userStats, averageUserStats, averageELOStats)

    statsPercentiles = evaluatePlayerStatsPercentiles(tier, division, lane, averageUserStats, importantStats, role)

    letterGrade = calculateLetterGrade(statsPercentiles, importantStats)

    congratsMsg, listOfTips = generateTakeaways(statsPercentiles, averageUserStats, tier, division, lane, role)

    return userStatsTable, comparisonStatsTable, statsPercentiles, letterGrade, congratsMsg, listOfTips
