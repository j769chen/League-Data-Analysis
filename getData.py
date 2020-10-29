import requests
import json
import os
import math
from roleReference import TIERS, DIVISIONS, LANES, BOT_ROLES

"""Module with all data fetching/dumping functions"""

API_KEY= "RGAPI-e02d0107-3dfb-422f-9776-a5177876b6b9"
REGION = 'na1'
QUEUE = 'RANKED_SOLO_5x5' # Only interested in ranked solo queue data


def requestSummonerData(summonerName): # Get a summoner's profile based on their username
    URL = "https://{}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key={}".format(REGION, summonerName, API_KEY)
    response = requests.get(URL)

    return response.json()


def requestRankedData(summonerDict): # Get a summoner's ranked stats from their ID
    summonerID = summonerDict['id']
    URL = "https://{}.api.riotgames.com/lol/league/v4/entries/by-summoner/{}?api_key={}".format(REGION, summonerID, API_KEY)
    response = requests.get(URL)

    return response.json()


def getRankedTier(tier, division=None): # Get random players from a specific division
    baseURL = "https://{}.api.riotgames.com/lol/league/v4".format(REGION)
    if tier == TIERS['Challenger'] or tier == TIERS['Grandmaster'] or tier == TIERS['Master']:
        URL = baseURL + "/{}leagues/by-queue/{}?api_key={}".format(tier.lower(), QUEUE, API_KEY)
    else:
        URL = baseURL + "/entries/{}/{}/{}?api_key={}".format(QUEUE, tier, division, API_KEY)

    response = requests.get(URL)

    return response.json()


def getMatchHistory(accountID, champion=None): # Get a user's match history with option of filtering by champion
    baseURL = "https://{}.api.riotgames.com/lol/match/v4/matchlists/by-account/{}?queue=420&queue=430&queue=440".format(REGION, accountID)

    if champion:
        URL = baseURL + "&champion={}&api_key={}".format(champion, API_KEY)
    else:
        URL = baseURL + "&api_key={}".format(API_KEY)
    response = requests.get(URL)

    return response.json()['matches']


def getMatchById(matchId): # Fetch one match's data from its match ID
    URL = "https://{}.api.riotgames.com/lol/match/v4/matches/{}?api_key={}".format(REGION, matchId,
                                                                                                 API_KEY)
    response = requests.get(URL)

    return response.json()


def preprocessStats(player): # Function to get other calculated stats before analysis
    if player['stats']['deaths'] != 0:
        player['stats']['KDA'] = round((player['stats']['kills'] + player['stats']['assists'])/player['stats']['deaths'], 2)
    else:
        player['stats']['KDA'] = math.inf
    player['stats']['CS'] = player['stats']['totalMinionsKilled'] + player['stats']['neutralMinionsKilled']
    player['stats']['CS/M'] = round(player['stats']['CS']/player['stats']['gameDuration'], 2)
    player['stats']['DPM'] = round(player['stats']['totalDamageDealtToChampions']/player['stats']['gameDuration'], 2)


def getPlayerMatchStats(summonerName, matchId): # Get important stats from one match for a player
    match = getMatchById(matchId)
    for participants in match['participantIdentities']:
        if participants['player']['summonerName'] == summonerName:
            playerId = participants['participantId']

    for players in match['participants']:
        if players['participantId'] == playerId:
            players['stats']['gameDuration'] = round(match['gameDuration']/60, 2)
            preprocessStats(players)
            playerStats = players['stats']

    return playerStats


def filterMatchList(matchList, lane, role, numGames): # Filters match history by either lane or role if lane is "BOTTOM"
    filteredMatchList = []
    if lane == LANES['Bottom']:
        filterParam = role
        query = 'role'
    else:
        filterParam = lane
        query = 'lane'

    for matches in matchList:
        if filterParam == BOT_ROLES['Support']: # Error handling for other lanes having DUO_SUPPORT role tag
            if matches['lane'] == lane and matches[query] == filterParam:
                filteredMatchList.append(matches)
        else:
            if matches[query] == filterParam:
                filteredMatchList.append(matches)

        if len(filteredMatchList) == numGames:
            break

    if len(filteredMatchList) < numGames:
        print("Not enough games, we managed to find {} games in your recent match history as {}".
              format(len(filteredMatchList), filterParam))

    return filteredMatchList


def getUsersStatsToReview(summonerName, lane, numGames, role=None, champion=None): # Gets users stats for last numGames games from their summoner name, filtering by role and optionally filtering by champions
    summonerInfo = requestSummonerData(summonerName)
    rankedInfo = requestRankedData(summonerInfo)

    for leagues in rankedInfo:
        if leagues['queueType'] == QUEUE:
            tier, division = leagues['tier'], leagues['rank']

    matchHistory = getMatchHistory(summonerInfo['accountId'], champion)
    userStats = []

    filteredMatchList = filterMatchList(matchHistory, lane, role, numGames)

    for matches in filteredMatchList:
        userStats.append(getPlayerMatchStats(summonerName, matches['gameId']))  # Returns list of user stats

    return userStats, tier, division


def getFilepath(tier, division, lane, role='', average=False):
    baseDirectory = 'AverageData' + '/' + tier + '/' + division + '/'

    if lane == LANES['Bottom']:
        jsonName = '{}_{}_{}_{}'.format(tier, division, lane, role)
    else:
        jsonName = '{}_{}_{}'.format(tier, division, lane)

    if average:
        jsonName += '_average'

    jsonName += '.json'

    return baseDirectory + jsonName


def generateFiles(): # Reset/Regenerate comparison data directories and create new files
    for keys in TIERS:
        if keys == 'Master' or keys == 'Grandmaster' or keys == 'Challenger':
            divisions = {1: 'I'}
        else:
            divisions = DIVISIONS
        for division in divisions:
            for lanes in LANES:
                if lanes != 'Middle(Match History)': # Ensures only one mid files is created
                    if lanes == 'Bottom':
                        for roles in BOT_ROLES:
                            try: # Try except so that if filepath doesn't exist, generate directories before generating file
                                with open(getFilepath(TIERS[keys], DIVISIONS[division], LANES[lanes],
                                                      BOT_ROLES[roles]), 'w') as f:
                                    f.write('')
                            except:
                                os.makedirs('AverageData' + '/' + TIERS[keys] + '/' + DIVISIONS[division], exist_ok=True)
                                with open(getFilepath(TIERS[keys], DIVISIONS[division], LANES[lanes],
                                                      BOT_ROLES[roles]), 'w') as f:
                                    f.write('')
                    else:
                        try:
                            with open(getFilepath(TIERS[keys], DIVISIONS[division], LANES[lanes]), 'w') as f:
                                f.write('')
                        except:
                            os.makedirs('AverageData' + '/' +TIERS[keys] + '/' + DIVISIONS[division], exist_ok=True)
                            with open(getFilepath(TIERS[keys], DIVISIONS[division], LANES[lanes]), 'w') as f:
                                f.write('')


def recordMatchStats(tier, division, matchId): # Dump stats from a match to the corresponding division/role JSON file
    match = getMatchById(matchId)

    for players in match['participants']:
        players['stats']['gameDuration'] = round(match['gameDuration']/60, 2)
        preprocessStats(players)
        print(players)
        if players['timeline']['lane'] != 'NONE' and (players['timeline']['lane'] != 'BOTTOM' or
                                                      (players['timeline']['role'] != 'DUO' and
                                                       players['timeline']['role'] != 'SOLO')):  # Error handling since some bugs with role assignments in API
            jsonName = getFilepath(tier, division, players['timeline']['lane'], players['timeline']['role'])

            with open(jsonName, 'a') as outfile:
                json.dump(players['stats'], outfile)
                outfile.write('\n')


def getDataForDivision(tier, division='I'): # Get ~10 random matches from players that are in a specific tier and division, excluding those with deprecated roles
    rankedTier = getRankedTier(tier, division)
    matchHistories = []

    for i in range(10): # Get match histories from 10 random players in the current tier
        if tier == TIERS['Master'] or tier == TIERS['Grandmaster'] or tier == TIERS['Challenger']:
            summonerData = requestSummonerData(rankedTier['entries'][i]['summonerName'])
        else:
            summonerData = requestSummonerData(rankedTier[i]['summonerName'])

        matchHistories.append(getMatchHistory(summonerData['accountId']))

    for histories in matchHistories: # Get one match from each players match history and dump to file
        recordMatchStats(tier, division, histories[0]['gameId'])

# generateFiles()
# getDataForDivision('PLATINUM', 'IV')
# def getDataForAllDivisions():
# getDataForDivision('PLATINUM', 'IV')
# testMatch = getMatchById(3630630530)
# print(testMatch)
#
# print(getPlayerMatchStats('xTheChosenWon', testMatch))
#
# recordMatchStats('PLATINUM', 'IV', testMatch)
# summoner = requestSummonerData('xTheChosenWon')
#
# print(summoner)
#
# print(requestRankedData(summoner))



# print(getMatchHistory(summoner['accountId'], APIKey))

# championMatches = getMatchHistory(summoner['accountId'], 236)
# print(championMatches)
#
# matchList = []
# for i in range(10):
#     matchList.append(getMatchById(championMatches['matches'][i]['gameId']))

# print(matchList)

# totalDeaths = 0
# for match in matchList:
#     for player in match['participants']:
#         if player['championId'] == 236:
#             print
#             totalDeaths += player['stats']['deaths']
#
# print(totalDeaths/10)

# match = getMatchById(3628818602)


