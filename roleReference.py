# Dictionaries to store correct values that Riot API uses to classify tiers, divisions, roles and lanes

TIERS = {
    'Iron': 'IRON',
    'Bronze': 'BRONZE',
    'Silver' : 'SILVER',
    'Gold' : 'GOLD',
    'Platinum': 'PLATINUM',
    'Diamond' : 'DIAMOND',
    'Master': 'MASTER',
    'Grandmaster': 'GRANDMASTER',
    'Challenger': 'CHALLENGER'
}

DIVISIONS = {
    1: 'I',
    2: 'II',
    3: 'III',
    4: 'IV'
}

LANES = {
    'Top': 'TOP',
    'Jungle': 'JUNGLE',
    'Middle': 'MIDDLE',
    'Bottom': 'BOTTOM'
}

BOT_ROLES = {
    'ADC': 'DUO_CARRY',
    'Support': 'DUO_SUPPORT'
}

# Dictionaries to represent which stats to display for each role and their weightings
# Some stats are simply calculated using others, or vice versa, but are still useful to show, so they
# have a weighting of 0, for example, KDA is (kills + assists)/deaths

TOP_STATS_WEIGHTING = {
    "kills": 0.15,
    "deaths": -0.1,
    "assists": 0.1,
    "KDA": 0,
    "totalDamageDealtToChampions": 0.2,
    "CS": 0.3,
    "visionScore": 0.2,
    "visionWardsBoughtInGame": 0,
    "wardsPlaced": 0,
    "wardsKilled": 0,
    "timeCCingOthers": 0.05,
    "damageDealtToTurrets": 0.1
}

JUNGLE_STATS_WEIGHTING = {
    "kills": 0.05,
    "deaths": -0.15,
    "assists": 0.15,
    "KDA": 0,
    "totalDamageDealtToChampions": 0.2,
    "CS": 0.3,
    "visionScore": 0.3,
    "visionWardsBoughtInGame": 0,
    "wardsPlaced": 0,
    "wardsKilled": 0,
    "timeCCingOthers": 0.15
}

MID_STATS_WEIGHTING = {
    "kills": 0.2,
    "deaths": -0.2,
    "assists": 0.1,
    "KDA": 0,
    "totalDamageDealtToChampions": 0.25,
    "CS": 0.3,
    "visionScore": 0.25,
    "visionWardsBoughtInGame": 0,
    "wardsPlaced": 0,
    "wardsKilled": 0,
    "timeCCingOthers": 0.05,
    "goldEarned": 0.05
}

ADC_STATS_WEIGHTING = {
    "kills": 0.2,
    "deaths": -0.2,
    "assists": 0.1,
    "KDA": 0,
    "totalDamageDealtToChampions": 0.3,
    "CS": 0.35,
    "visionScore": 0.15,
    "visionWardsBoughtInGame": 0,
    "wardsPlaced": 0,
    "wardsKilled": 0,
    "goldEarned": 0.1
}

SUPPORT_STATS_WEIGHTING = {
    "kills": 0.025,
    "deaths": -0.1,
    "assists": 0.25,
    "KDA": 0,
    "totalDamageDealtToChampions": 0.075,
    "CS": 0,
    "visionScore": 0.4,
    "visionWardsBoughtInGame": 0,
    "wardsPlaced": 0,
    "wardsKilled": 0,
    "timeCCingOthers": 0.3,
    "goldEarned": 0.05
}