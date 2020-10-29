import requests
import json
import os
from tabulate import tabulate
from roleReference import TIERS, DIVISIONS, LANES, BOT_ROLES, STATS_WEIGHTINGS
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


def quickSort(list1):
    low = 0
    high = len(list1) - 1
    quickSortHelper(list1, low, high)


def calculatePercentile(list1, userStat): # Takes in a list of stats from JSON dump and gets percentile of the user's stat
    list1.append(userStat)
    quickSort(list1)

    return round(100 - (list1.index(userStat)+1)/len(list1) * 100,2) # Generally if you are good, we say "you are among the top 1%", not top 100%, so return 100 - percentile of player


# def calculateQuartiles(list1): # Get the quartile values from a list
#     list1.sort()
#     mid = int(len(list1)/2)
#     firstHalf = list1[:mid]
#     if len(list1) % 2 == 0:
#         secondHalf = list1[mid:]
#     else:
#        secondHalf = list1[mid+1:]
#
#     firstQuartile = round(median(firstHalf), 2)
#     secondQuartile = round(median(list1), 2)
#     thirdQuartile = round(median(secondHalf), 2)
#
#     return firstQuartile, secondQuartile, thirdQuartile


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


# def compareStat(quartiles, userAverage): # Compares user stat to quartile values and evaluates (quartiles is tuple of 3 values)
#
#     if userAverage > quartiles[2]:
#         return 25
#     elif userAverage > quartiles[1]:
#         return 50
#     elif userAverage > quartiles[0]:
#         return 75
#     else:
#         return 100

# def tabulateStats(headers, *args):
#     rows = []
#     for i in args:
#         rows.append(i)
#
#     return tabulate(rows, headers)


def getUserAndAverageTables(statNames, userStats, averageUserStats, averageELOStats): # Get tables for user's recent matches and comparison of average stats
    statTableValues = []

    for gameStats in userStats:
        statTableValues.append(gameStats.values())


    averageTableValues = [averageUserStats.values(), averageELOStats.values()]

    return tabulate(statTableValues, statNames), tabulate(averageTableValues, statNames)


def evaluatePlayerStatsPercentiles(tier, division, lane, averageUserStats, importantStats, role=None): # Returns a dictionary where the keys are stats and the values are the players percentile compared to players of the same ELO
    statsPercentiles = {}

    for stats in importantStats:
        statsPercentiles[stats] = calculatePercentile(getSpecificStatList(tier, division, lane, stats, role), averageUserStats[stats])

    return statsPercentiles

# def generateTips():


def analyze(userStats, statNames, importantStats, tier, division, lane, role):
    for gameStats in userStats:
        filterImportantStats(gameStats, importantStats)

    averageUserStats = getAverageRecordedStats(tier, division, lane, role, False, False, userStats) # Get average user stats

    averageELOStats = getAverageRecordedStats(tier, division, lane, role, False, True) # Get average stats for ELO from JSON dump
    filterImportantStats(averageELOStats, importantStats)
    userStatsTable, comparisonStatsTable = getUserAndAverageTables(statNames, userStats, averageUserStats, averageELOStats)

    print(userStatsTable)
    print(comparisonStatsTable)
