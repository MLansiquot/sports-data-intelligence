import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cx_Oracle
import pandas as pd
import matplotlib.pyplot as plt
from config import get_connection

# Apply a consistent modern style
plt.style.use('seaborn-v0_8-talk')

# Create output folder if not exists
output_dir = os.path.join(os.path.dirname(__file__), "charts")
os.makedirs(output_dir, exist_ok=True)

# Connect to Oracle and get data
conn = get_connection()
query = """
    SELECT TEAM_NAME, WINS, LOSSES, WIN_PCT
    FROM NBA_TEAM_STATS
    ORDER BY WIN_PCT DESC
    FETCH FIRST 30 ROWS ONLY
"""
df = pd.read_sql(query, conn)
conn.close()

df.columns = df.columns.str.lower()

print("✅ Data loaded successfully!")
print(df.head())

# Scatter plot setup
plt.figure(figsize=(10,7))
plt.scatter(df['wins'], df['losses'], color='#FFA500', s=120, edgecolors='black', alpha=0.8)

# Label each point with the team name
for i, name in enumerate(df['team_name']):
    plt.text(df['wins'][i] + 0.15, df['losses'][i] + 0.15, name, fontsize=9, fontweight='bold')

# Chart formatting
plt.xlabel("Wins", fontsize=14)
plt.ylabel("Losses", fontsize=14)
plt.title("🏀 NBA Team Performance: Wins vs Losses", fontsize=18, fontweight='bold')
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()

# Save chart
output_path = os.path.join(output_dir, "wins_vs_losses_scatter.png")
plt.savefig(output_path, dpi=500)
print(f"📊 Scatter chart saved to: {output_path}")

plt.show()
