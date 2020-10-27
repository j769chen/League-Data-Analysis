import requests
import json
import os
from statistics import median
from roleReference import TIERS, DIVISIONS, LANES, BOT_ROLES
from getData import getFilepath


def readMultipleJSONS(tier, division, lane, role=''): # Read JSONs from file into a list
    statsList = []
    jsonName = getFilepath(tier, division, lane, role)

    with open(jsonName, 'r') as infile:
        for lines in infile:
            statsList.append(json.loads(lines))

    return statsList


def getAverageRecordedStats(tier, division, lane, role='', toFile=True): # Gets data from JSON Dump for a tier and role and outputs average stats to another file
    averageStats = {}

    statsList = readMultipleJSONS(tier, division, lane, role)

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

    firstQuartile = median(firstHalf)
    secondQuartile = median(list1)
    thirdQuartile = median(secondHalf)

    return firstQuartile, secondQuartile, thirdQuartile


def getSpecificStatList(tier, division, lane, stat, role=''): # Gets the list of all values in a JSON dump for a specific stat (i.e. kills)
    statsList = readMultipleJSONS(tier, division, lane, role)
    returnList = []

    for entries in statsList:
        returnList.append(entries[stat])

    return returnList


def compareStat(statList, userAverage): #Compares user stat to quartile values and evaluates
    first, second, third = calculateQuartiles((statList))

    if userAverage > third:
        return 3
    elif userAverage > second:
        return 2
    elif userAverage > first:
        return 1
    else:
        return 0





