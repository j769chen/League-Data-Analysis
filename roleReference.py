# Dictionaries to store correct values that Riot API uses to classify tiers, divisions, roles and lanes

TIERS = {
    'Iron': 'IRON',
    'Bronze': 'BRONZE',
    'Silver': 'SILVER',
    'Gold': 'GOLD',
    'Platinum': 'PLATINUM',
    'Diamond': 'DIAMOND',
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
    'Middle(Match History)': 'MID',  # Riot uses 'MID' in their match history API, but 'MIDDLE' for match stats
    'Bottom': 'BOTTOM'
}

BOT_ROLES = {
    'ADC': 'DUO_CARRY',
    'Support': 'DUO_SUPPORT'
}

# Dictionaries to represent which stats to display for each role and their weightings
# Some stats are simply calculated using others, or vice versa, but are still useful to show, so they
# have a weighting of 0, for example, KDA is (kills + assists)/deaths

STATS_WEIGHTINGS = {
    LANES['Top']: {
        "kills": 0.15,
        "deaths": -0.025,
        "assists": 0.1,
        "totalDamageDealtToChampions": 0,
        "damageDealtToTurrets": 0.05,
        "visionScore": 0.2,
        "timeCCingOthers": 0.05,
        "visionWardsBoughtInGame": 0,
        "wardsPlaced": 0,
        "wardsKilled": 0,
        "KDA": 0,
        "CS": 0,
        "CS/M": 0.25,
        "DPM": 0.2
    },
    LANES['Jungle']: {
        "kills": 0.05,
        "deaths": -0.025,
        "assists": 0.15,
        "totalDamageDealtToChampions": 0,
        "visionScore": 0.3,
        "timeCCingOthers": 0.15,
        "visionWardsBoughtInGame": 0,
        "wardsPlaced": 0,
        "wardsKilled": 0,
        "KDA": 0,
        "CS": 0,
        "CS/M": 0.2,
        "DPM": 0.25
    },
    LANES['Middle']:  {
        "kills": 0.2,
        "deaths": -0.05,
        "assists": 0.1,
        "totalDamageDealtToChampions": 0,
        "visionScore": 0.2,
        "visionWardsBoughtInGame": 0,
        "wardsPlaced": 0,
        "wardsKilled": 0,
        "KDA": 0,
        "CS": 0,
        "CS/M": 0.25,
        "DPM": 0.25
    },
    BOT_ROLES['ADC']:  {
        "kills": 0.2,
        "deaths": -0.05,
        "assists": 0.1,
        "totalDamageDealtToChampions": 0,
        "visionScore": 0.1,
        "goldEarned": 0.05,
        "visionWardsBoughtInGame": 0,
        "wardsPlaced": 0,
        "wardsKilled": 0,
        "KDA": 0,
        "CS": 0,
        "CS/M": 0.3,
        "DPM": 0.25
    },
    BOT_ROLES['Support']:  {
        "kills": 0.025,
        "deaths": -0.025,
        "assists": 0.25,
        "totalDamageDealtToChampions": 0,
        "visionScore": 0.4,
        "timeCCingOthers": 0.25,
        "visionWardsBoughtInGame": 0,
        "wardsPlaced": 0,
        "wardsKilled": 0,
        "KDA": 0,
        "CS": 0,
        "DPM": 0.075
    }
}

FORMAL_NAMES = {
    "kills": "Kills",
    "deaths": "Deaths",
    "assists": "Assists",
    "KDA": "KD/A",
    "DPM": "DPM",
    "totalDamageDealtToChampions": "Damage to Champions",
    "CS": "CS",
    "CS/M": "CS/M",
    "visionScore": "Vision Score",
    "visionWardsBoughtInGame": "Pink Wards Bought",
    "wardsPlaced": "Wards Placed",
    "wardsKilled": "Wards Killed",
    "timeCCingOthers": "CC Score",
    "goldEarned": "GP",
    "damageDealtToTurrets": "Damage to Towers"
}

# Any percentage above letter's value corresponds to that letter grade
LETTER_GRADES = {
    "S": 0.8,
    "A": 0.6,
    "B": 0.4,
    "C": 0.2,
    "D": 0
}
