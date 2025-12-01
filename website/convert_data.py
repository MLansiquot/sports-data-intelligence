import pandas as pd
import json
import os

# Create website directory if it doesn't exist
os.makedirs('website', exist_ok=True)

# Read team stats CSV
print("📊 Reading team stats...")
team_stats_df = pd.read_csv('data/nba_team_stats/nba_team_stats.csv')

# Clean and prepare team stats data
team_stats_df = team_stats_df.rename(columns={
    'TEAM_NAME': 'team_name',
    'W': 'wins',
    'L': 'losses',
    'W_PCT': 'win_pct',
    'PTS': 'points',
    'AST': 'assists',
    'REB': 'rebounds',
    'STL': 'steals',
    'BLK': 'blocks'
})

# Create a simplified dataset for the website
team_stats_simple = team_stats_df[[
    'team_name', 'wins', 'losses', 'win_pct', 
    'points', 'assists', 'rebounds', 'steals', 'blocks'
]].copy()

# Convert to JSON
team_stats_json = team_stats_simple.to_dict(orient='records')

# Save team stats JSON
with open('website/team_stats.json', 'w') as f:
    json.dump(team_stats_json, f, indent=2)
print(f"✅ Saved {len(team_stats_json)} team records to website/team_stats.json")

# Read player stats CSV
print("📊 Reading player stats...")
player_stats_df = pd.read_csv('data/nba_player_stats/nba_player_stats.csv')

# Clean player stats data
player_stats_json = player_stats_df.to_dict(orient='records')

# Save player stats JSON
with open('website/player_stats.json', 'w') as f:
    json.dump(player_stats_json, f, indent=2)
print(f"✅ Saved {len(player_stats_json)} player records to website/player_stats.json")

# Create summary statistics
print("📊 Creating summary statistics...")

# Top 10 teams by win percentage
top_teams = team_stats_simple.nlargest(10, 'win_pct')[['team_name', 'win_pct', 'wins', 'losses']].to_dict(orient='records')

# Team performance summary
team_summary = {
    'total_teams': len(team_stats_simple),
    'top_10_teams': top_teams,
    'avg_win_pct': float(team_stats_simple['win_pct'].mean()),
    'avg_points': float(team_stats_simple['points'].mean()),
    'max_wins': int(team_stats_simple['wins'].max()),
    'max_points': float(team_stats_simple['points'].max())
}

# Player performance summary
player_summary = {
    'total_players': len(player_stats_df),
    'avg_points': float(player_stats_df['POINTS'].mean()) if len(player_stats_df) > 0 else 0,
    'avg_assists': float(player_stats_df['ASSISTS'].mean()) if len(player_stats_df) > 0 else 0,
    'avg_rebounds': float(player_stats_df['REBOUNDS'].mean()) if len(player_stats_df) > 0 else 0,
    'top_players': player_stats_df.nlargest(10, 'POINTS').to_dict(orient='records') if len(player_stats_df) > 0 else []
}

# Combined summary
summary = {
    'teams': team_summary,
    'players': player_summary
}

# Save summary JSON
with open('website/summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print("✅ Saved summary statistics to website/summary.json")

print("\n🎉 Data conversion complete! Ready to build the website.")

