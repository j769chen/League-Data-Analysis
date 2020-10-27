import requests
import json
import os
from roleReference import TIERS, DIVISIONS, LANES, BOT_ROLES

"""Module with all data fetching/dumping functions"""

API_KEY= "RGAPI-1547ed9c-ca4a-4587-9572-0981e7bd76c9"
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
    baseURL = "https://{}.api.riotgames.com/lol/match/v4/matchlists/by-account/".format(REGION)
    if champion == None:
        URL = baseURL + "{}?api_key={}".format(accountID, API_KEY)
    else:
        URL = baseURL + "{}?champion={}&api_key={}".format(accountID, champion, API_KEY)
    response = requests.get(URL)

    return response.json()['matches']


def getMatchById(matchId): # Fetch one match's data from its match ID
    URL = "https://{}.api.riotgames.com/lol/match/v4/matches/{}?api_key={}".format(REGION, matchId,
                                                                                                 API_KEY)
    response = requests.get(URL)

    return response.json()


def getPlayerMatchStats(summonerName, matchId): # Get important stats from one match for a player
    match = getMatchById(matchId)
    playerStats = {}
    gameTime = match['gameDuration']/60
    for participants in match['participantIdentities']:
        if participants['player']['summonerName'] == summonerName:
            playerId = participants['participantId']

    for players in match['participants']:
        if players['participantId'] == playerId:
            # playerStats['kills'] = players['stats']['kills']
            # playerStats['deaths'] = players['stats']['deaths']
            # playerStats['assists'] = players['stats']['assists']
            # playerStats['damage'] = players['stats']['totalDamageDealt']
            # playerStats['DPM'] = round(playerStats['damage']/gameTime, 2)
            # playerStats['CS'] = players['stats']['totalMinionsKilled'] + players['stats']['neutralMinionsKilled']
            # playerStats['CSPM'] = round(playerStats['CS']/gameTime, 2)
            # playerStats['wardsPlaced'] = players['stats']['wardsPlaced']
            # playerStats['wardsKilled'] = players['stats']['wardsKilled']
            # playerStats['VisionScore'] = players['stats']['visionScore']
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

    print(matchList)
    for matches in matchList:
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

generateFiles()

def recordMatchStats(tier, division, matchId): # Dump stats from a match to the corresponding division/role JSON file
    match = getMatchById(matchId)
    print(match)
    for players in match['participants']:
        players['gameDuration'] = round(match['gameDuration']/60)
        print(players['gameDuration'])
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
        recordMatchStats(tier, division, histories['matches'][0]['gameId'])

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


