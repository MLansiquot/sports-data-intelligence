import csv
import random
from datetime import datetime, timedelta

# === Config ===
output_path = r"D:\sports-data-intelligence\data\nba_game_logs\nba_game_logs.csv"

# Modern NBA teams
teams = [
    "Atlanta Hawks","Boston Celtics","Brooklyn Nets","Charlotte Hornets",
    "Chicago Bulls","Cleveland Cavaliers","Dallas Mavericks","Denver Nuggets",
    "Detroit Pistons","Golden State Warriors","Houston Rockets","Indiana Pacers",
    "LA Clippers","Los Angeles Lakers","Memphis Grizzlies","Miami Heat",
    "Milwaukee Bucks","Minnesota Timberwolves","New Orleans Pelicans",
    "New York Knicks","Oklahoma City Thunder","Orlando Magic",
    "Philadelphia 76ers","Phoenix Suns","Portland Trail Blazers",
    "Sacramento Kings","San Antonio Spurs","Toronto Raptors",
    "Utah Jazz","Washington Wizards"
]

notes_pool = [
    "Opening night matchup",
    "Close game",
    "Blowout win",
    "Overtime thriller",
    "Rivalry game",
    "Strong defensive performance",
    "High scoring duel",
    "Star player dominated",
    "Bench unit stepped up",
    "Comeback win"
]

# We'll simulate something that *looks like* the first 100 games
start_date = datetime(2023, 10, 24)  # NBA 23-24 regular season start
num_games = 100
rows = []

current_date = start_date

for i in range(num_games):
    # Spread games over the calendar
    game_date = current_date
    if i % 4 == 0:
        current_date += timedelta(days=1)

    home = random.choice(teams)
    away_choices = [t for t in teams if t != home]
    away = random.choice(away_choices)

    # Realistic NBA scores
    home_points = random.randint(98, 132)
    away_points = random.randint(95, 128)

    if home_points > away_points:
        winner = home
        loser = away
    else:
        winner = away
        loser = home

    home_streak = random.randint(0, 6)
    away_streak = random.randint(0, 6)

    note = random.choice(notes_pool)

    rows.append([
        game_date.strftime("%Y-%m-%d"),
        2024,                # season
        home,
        away,
        home_points,
        away_points,
        winner,
        loser,
        home_streak,
        away_streak,
        note
    ])

# Write to CSV
with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "GAME_DATE","SEASON","HOME_TEAM","AWAY_TEAM","HOME_POINTS",
        "AWAY_POINTS","WINNER","LOSER","HOME_STREAK","AWAY_STREAK","NOTES"
    ])
    writer.writerows(rows)

print(f"✅ Generated {num_games} realistic NBA game logs at:")
print(output_path)
