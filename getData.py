import requests
import json
import sys
import os
import math
import time
from roleReference import TIERS, DIVISIONS, LANES, BOT_ROLES

"""Module with all data fetching/dumping functions"""

API_KEY= "RGAPI-75e1e9cd-80a2-4be5-b69f-60f91e4ccbc6"
REGION = 'na1'
QUEUE = 'RANKED_SOLO_5x5'  # Only interested in ranked solo queue data

numrequests = 0


def tooManyRequestsError(jsonResponse):  # Function to inform user if they cap out on API requests
    if jsonResponse == {'status': {'message': 'Gateway timeout', 'status_code': 504}}:
        print('ERROR: You have exceeded the maximum number of requests to the Riot API')
        print(jsonResponse)
        sys.exit(-1)
    return 0


def summonerNotFoundError(jsonResponse):  # Error handling to inform user if they entered an invalid summoner name
    if jsonResponse == {'status': {'message': 'Data not found - summoner not found', 'status_code': 404}}:
        print('ERROR: You have entered an invalid summoner name, please try again')
        print(jsonResponse)
        sys.exit(-1)
    return 0


def matchesNotFoundError(jsonResponse):  # Error handling for champion/lane/role combinations that the player has 0 matches on
    if jsonResponse == {'status': {'status_code': 404, 'message': 'Not found'}}:
        print('ERROR: You have played 0 games of that champion/lane')
        print(jsonResponse)
        sys.exit(-1)
    return 0


def requestSummonerData(summonerName):  # Get a summoner's profile based on their username
    URL = "https://{}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key={}".format(REGION, summonerName, API_KEY)
    response = requests.get(URL)

    global numrequests
    numrequests += 1

    jsonResponse = response.json()
    tooManyRequestsError(jsonResponse)
    summonerNotFoundError(jsonResponse)
    return jsonResponse


def requestRankedData(summonerDict):  # Get a summoner's ranked stats from their ID
    summonerID = summonerDict['id']
    URL = "https://{}.api.riotgames.com/lol/league/v4/entries/by-summoner/{}?api_key={}".format(REGION, summonerID, API_KEY)
    response = requests.get(URL)

    global numrequests
    numrequests += 1

    jsonResponse = response.json()
    tooManyRequestsError(jsonResponse)
    return jsonResponse


def requestRankedTier(tier, division=None):  # Get random players from a specific division
    baseURL = "https://{}.api.riotgames.com/lol/league/v4".format(REGION)
    if tier == TIERS['Challenger'] or tier == TIERS['Grandmaster'] or tier == TIERS['Master']:
        URL = baseURL + "/{}leagues/by-queue/{}?api_key={}".format(tier.lower(), QUEUE, API_KEY)
    else:
        URL = baseURL + "/entries/{}/{}/{}?api_key={}".format(QUEUE, tier, division, API_KEY)

    response = requests.get(URL)

    global numrequests
    numrequests += 1

    jsonResponse = response.json()
    tooManyRequestsError(jsonResponse)
    return jsonResponse


def requestMatchHistory(accountID, champion=None):  # Get a user's match history with option of filtering by champion
    baseURL = "https://{}.api.riotgames.com/lol/match/v4/matchlists/by-account/{}?queue=420&queue=430&queue=440".format(REGION, accountID)
    if champion:
        URL = baseURL + "&champion={}&api_key={}".format(champion, API_KEY)
    else:
        URL = baseURL + "&api_key={}".format(API_KEY)
    response = requests.get(URL)

    global numrequests
    numrequests += 1

    jsonResponse = response.json()
    tooManyRequestsError(jsonResponse)
    matchesNotFoundError(jsonResponse)
    return jsonResponse['matches']


def requestMatchById(matchId):  # Fetch one match's data from its match ID
    URL = "https://{}.api.riotgames.com/lol/match/v4/matches/{}?api_key={}".format(REGION, matchId,
                                                                                                 API_KEY)
    response = requests.get(URL)

    global numrequests
    numrequests += 1

    jsonResponse = response.json()
    tooManyRequestsError(jsonResponse)
    return jsonResponse


def preprocessStats(player):  # Function to get other calculated stats before analysis
    if player['stats']['deaths'] != 0:
        player['stats']['KDA'] = round((player['stats']['kills'] + player['stats']['assists'])/player['stats']['deaths'], 2)
    else:
        player['stats']['KDA'] = math.inf
    player['stats']['CS'] = player['stats']['totalMinionsKilled'] + player['stats']['neutralMinionsKilled']
    player['stats']['CS/M'] = round(player['stats']['CS']/player['stats']['gameDuration'], 2)
    player['stats']['DPM'] = round(player['stats']['totalDamageDealtToChampions']/player['stats']['gameDuration'], 2)
    player['stats']['earlyGameXp'] = player['timeline']['xpPerMinDeltas']['0-10']


def getPlayerMatchStats(summonerName, matchId):  # Get important stats from one match for a player
    match = requestMatchById(matchId)
    for participants in match['participantIdentities']:
        if participants['player']['summonerName'] == summonerName:
            playerId = participants['participantId']

    for players in match['participants']:
        if players['participantId'] == playerId:
            players['stats']['gameDuration'] = round(match['gameDuration']/60, 2)
            preprocessStats(players)
            playerStats = players['stats']

    return playerStats


def filterMatchList(matchList, lane, role, numGames):  # Filters match history by either lane or role if lane is "BOTTOM"
    filteredMatchList = []
    if lane == LANES['Bottom']:
        filterParam = role
        query = 'role'
    else:
        filterParam = lane
        query = 'lane'

    for matches in matchList:
        if filterParam == BOT_ROLES['Support']:  # Error handling for other lanes having DUO_SUPPORT role tag
            if matches['lane'] == lane and matches[query] == filterParam:
                filteredMatchList.append(matches)
        else:
            if matches[query] == filterParam:
                filteredMatchList.append(matches)

        if len(filteredMatchList) == numGames:
            break

    if len(filteredMatchList) == 0:
        print("There you have played 0 games of {} in your recent match history, exiting program.".format(filterParam))
        sys.exit()
    if len(filteredMatchList) < numGames:
        print("Not enough games, we managed to find {} games in your recent match history as {}".
              format(len(filteredMatchList), filterParam))

    return filteredMatchList


def getUsersStatsToReview(summonerName, lane, numGames, role=None, champion=None):  # Gets users stats for last numGames games from their summoner name, filtering by role and optionally filtering by champions
    summonerInfo = requestSummonerData(summonerName)
    summonerName = summonerInfo['name']  # This corrects any errors in case sensitivity that the user may have entered, since the summoner API is not case sensitive but the ranked data API is.

    rankedInfo = requestRankedData(summonerInfo)

    for leagues in rankedInfo:
        if leagues['queueType'] == QUEUE:
            tier, division = leagues['tier'], leagues['rank']

    matchHistory = requestMatchHistory(summonerInfo['accountId'], champion)
    print(matchHistory)
    userStats = []

    filteredMatchList = filterMatchList(matchHistory, lane, role, numGames)
    print(filteredMatchList)
    for matches in filteredMatchList:
        userStats.append(getPlayerMatchStats(summonerName, matches['gameId']))  # Returns list of user stats

    return userStats, tier, division, len(filteredMatchList)


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


def generateFiles():  # Reset/Regenerate comparison data directories and create new files
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
                            try:  # Try except so that if filepath doesn't exist, generate directories before generating file
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


def recordMatchStats(tier, division, matchId):  # Dump stats from a match to the corresponding division/role JSON file
    match = requestMatchById(matchId)
    for players in match['participants']:
        players['stats']['gameDuration'] = round(match['gameDuration']/60, 2)
        print(players)
        preprocessStats(players)
        if players['timeline']['lane'] != 'NONE' and (players['timeline']['lane'] != 'BOTTOM' or
                                                      (players['timeline']['role'] != 'DUO' and
                                                       players['timeline']['role'] != 'SOLO')):  # Error handling since some bugs with role assignments in API
            jsonName = getFilepath(tier, division, players['timeline']['lane'], players['timeline']['role'])

            with open(jsonName, 'a') as outfile:
                json.dump(players['stats'], outfile)
                outfile.write('\n')


def getDataForDivision(tier, division='I'):  # Get ~10 random matches from players that are in a specific tier and division, excluding those with deprecated roles
    rankedTier = requestRankedTier(tier, division)
    matchHistories = []

    for i in range(10): # Get match histories from 10 random players in the current tier
        if tier == TIERS['Master'] or tier == TIERS['Grandmaster'] or tier == TIERS['Challenger']:
            summonerData = requestSummonerData(rankedTier['entries'][i]['summonerName'])
        else:
            summonerData = requestSummonerData(rankedTier[i]['summonerName'])

        matchHistories.append(requestMatchHistory(summonerData['accountId']))

    for histories in matchHistories:  # Get one match from each players match history and dump to file
        recordMatchStats(tier, division, histories[0]['gameId'])


def getDataForTier(tier):
    if tier == TIERS['Master'] or tier == TIERS['Grandmaster'] or tier == TIERS['Challenger']:
        print("Getting data for {}".format(tier))
        getDataForDivision(tier)
    else:
        for i in range(1, 4):
            print("Getting data for {} {}".format(tier, DIVISIONS[i]))
            getDataForDivision(tier, DIVISIONS[i])

        print('Waiting 2 min for rate cap to reset...')
        time.sleep(120)  # Need to do this to avoid rate cap for API requests, which is 100/2min

        print("Getting data for {} {}".format(tier, DIVISIONS[4]))
        getDataForDivision(tier, DIVISIONS[4])


def getDataForAllTiers():  # Fetches data for all tiers, due to rate limits on API requests, takes relatively long amount of time due to needing to break for two minutes every ~100 requests
    for tier in TIERS:
        getDataForTier(TIERS[tier])
        if tier != TIERS['Master'] or tier != TIERS['Grandmaster'] or tier != TIERS['Challenger']:  # Since only 1 division for top 3 tiers, do not need to wait as we can run all three without hitting the cap
            time.sleep(120)


# start_time = time.time()
# getDataForAllTiers()
# print(time.time() - start_time())


# getDataForTier('PLATINUM')
# generateFiles()

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


