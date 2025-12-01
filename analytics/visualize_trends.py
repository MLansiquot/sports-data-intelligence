import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cx_Oracle
import pandas as pd
import matplotlib.pyplot as plt
from config import get_connection

# Apply consistent clean style
plt.style.use('seaborn-v0_8-talk')

# Create output folder if not exists
output_dir = os.path.join(os.path.dirname(__file__), "charts")
os.makedirs(output_dir, exist_ok=True)

# Choose your team (you can change this anytime)
team_name = "Golden State Warriors"

# Connect to Oracle
conn = get_connection()
query = f"""
    SELECT SEASON, WIN_PCT
    FROM NBA_TEAM_STATS
    WHERE TEAM_NAME = '{team_name}'
    ORDER BY SEASON
"""
df = pd.read_sql(query, conn)
conn.close()

df.columns = df.columns.str.lower()

if df.empty:
    print(f"⚠️ No data found for {team_name}. Check the team name in your database.")
else:
    print(f"✅ Loaded {len(df)} records for {team_name}")
    print(df.head())

    # Plot performance trend
    plt.figure(figsize=(10, 6))
    plt.plot(df['season'], df['win_pct'], marker='o', color='royalblue', linewidth=3)

    plt.title(f"🏀 {team_name} Win Percentage Over Seasons", fontsize=18, fontweight='bold')
    plt.xlabel("Season", fontsize=14)
    plt.ylabel("Win Percentage", fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    # Save chart
    output_path = os.path.join(output_dir, f"{team_name.lower().replace(' ', '_')}_trend.png")
    plt.savefig(output_path, dpi=500)
    print(f"📊 Chart saved to: {output_path}")

    plt.show()
