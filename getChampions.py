"""
Updates dictionary of champion names and their respective keys, use if new champion added in last patch
Separate from other module as this uses the riotwatcher library, since it can get the most recent patch easily
"""

import json
from riotwatcher import LolWatcher

lol_watcher = LolWatcher('RGAPI-1547ed9c-ca4a-4587-9572-0981e7bd76c9')

my_region = 'na1'

versions = lol_watcher.data_dragon.versions_for_region(my_region)
champions_version = versions['n']['champion']

current_champ_list = lol_watcher.data_dragon.champions(champions_version)

championDict = {}

for champs in current_champ_list['data']:
    championDict[current_champ_list['data'][champs]['id']] = current_champ_list['data'][champs]['key']

with open("championsDict.json", "w") as outfile:
    json.dump(championDict, outfile)

