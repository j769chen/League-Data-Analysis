"""
Updates dictionary of champion names and their respective keys, use if new champion added in last patch
Separate from other module as this uses the riotwatcher library, since it can get the most recent patch easily
"""

import json
from riotwatcher import LolWatcher
from getData import API_KEY

lol_watcher = LolWatcher(API_KEY)

my_region = 'na1'

versions = lol_watcher.data_dragon.versions_for_region(my_region)
champions_version = versions['n']['champion']

current_champ_list = lol_watcher.data_dragon.champions(champions_version)

championDict = {}

for champs in current_champ_list['data']:
    championDict[current_champ_list['data'][champs]['id']] = current_champ_list['data'][champs]['key']

with open("championsDict.json", "w") as outfile:
    json.dump(championDict, outfile)
