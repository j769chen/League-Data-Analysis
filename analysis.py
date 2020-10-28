import requests
import json
import os
from statistics import median
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


def calculateQuartiles(list1): # Get the quartile values from a list
    list1.sort()
    mid = int(len(list1)/2)
    firstHalf = list1[:mid]
    if len(list1) % 2 == 0:
        secondHalf = list1[mid:]
    else:
       secondHalf = list1[mid+1:]

    firstQuartile = round(median(firstHalf), 2)
    secondQuartile = round(median(list1), 2)
    thirdQuartile = round(median(secondHalf), 2)

    return firstQuartile, secondQuartile, thirdQuartile


def getSpecificStatList(tier, division, lane, stat, role=None): # Gets the list of all values in a JSON dump for a specific stat (i.e. kills)
    statsList = readMultipleJSONS(tier, division, lane, role)
    returnList = []

    for entries in statsList:
        returnList.append(entries[stat])

    return returnList


def compareStat(quartiles, userAverage): # Compares user stat to quartile values and evaluates (quartiles is tuple of 3 values)

    if userAverage > quartiles[2]:
        return 4
    elif userAverage > quartiles[1]:
        return 3
    elif userAverage > quartiles[0]:
        return 2
    else:
        return 1

# def evaluatePlayerStats(tier, division, lane, role=''):
#





