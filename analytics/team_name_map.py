TEAM_NAME_MAP = {
    "LA Clippers": "Los Angeles Clippers",
    "Brooklyn Nets": "Brooklyn Nets",
    "New Orleans Pelicans": "New Orleans Pelicans",
    "Charlotte Hornets": "Charlotte Hornets",
    "Oklahoma City Thunder": "Oklahoma City Thunder",
    "Golden State Warriors": "Golden State Warriors",
    "San Antonio Spurs": "San Antonio Spurs",
    "New Orleans Hornets": "New Orleans Pelicans",
    "Seattle SuperSonics": "Oklahoma City Thunder",
    "New Jersey Nets": "Brooklyn Nets",
    "Vancouver Grizzlies": "Memphis Grizzlies",
    "Charlotte Bobcats": "Charlotte Hornets",
    "Washington Bullets": "Washington Wizards",
}

def normalize(name):
    return TEAM_NAME_MAP.get(name, name)
