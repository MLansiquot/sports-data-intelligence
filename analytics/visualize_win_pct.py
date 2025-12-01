import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cx_Oracle
import pandas as pd
import matplotlib.pyplot as plt
from config import get_connection

# Apply a clean style and font scaling
plt.style.use('seaborn-v0_8-talk')

# Create the output folder if it doesn't exist
output_dir = os.path.join(os.path.dirname(__file__), "charts")
os.makedirs(output_dir, exist_ok=True)

# Connect to Oracle
conn = get_connection()
query = """
    SELECT TEAM_NAME, WIN_PCT
    FROM NBA_TEAM_STATS
    ORDER BY WIN_PCT DESC
    FETCH FIRST 10 ROWS ONLY
"""
df = pd.read_sql(query, conn)
conn.close()

# Normalize column names
df.columns = df.columns.str.lower()

print("✅ Data loaded successfully from Oracle!")
print(df.head())

# Plot chart
plt.figure(figsize=(10, 6))
bars = plt.barh(df['team_name'], df['win_pct'], color='dodgerblue', edgecolor='black')

plt.xlabel("Win Percentage", fontsize=14)
plt.ylabel("Team", fontsize=14)
plt.title("🏀 Top 10 NBA Teams by Win Percentage", fontsize=18, fontweight='bold')
plt.gca().invert_yaxis()

# Add value labels on bars
for bar in bars:
    plt.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2,
             f"{bar.get_width():.3f}", va='center', fontsize=10)

plt.tight_layout()

# Save chart as PNG
output_path = os.path.join(output_dir, "team_win_pct_chart.png")
plt.savefig(output_path, dpi=500)
print(f"📊 Chart saved to: {output_path}")

# Display chart
plt.show()