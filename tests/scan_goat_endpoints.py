import requests

API_KEY = "081aceca-0dd3-40f8-a617-bf5ce7212364"   # <-- replace with your actual key

BASES = [
    "https://mcp.balldontlie.io",
    "https://mcp.balldontlie.io/mcp",
    "https://api.balldontlie.io",
    "https://api.balldontlie.io/v1",
    "https://api.balldontlie.io/api"
]

ENDPOINTS = [
    "players", "teams", "games", "stats", "season_averages",
    "standings", "boxscores", "schedule", "search","leagues",
    "", "/", "nba", "v1/players", "v1/teams"
]

headers = {"Authorization": API_KEY}

print("\n🔍 SCANNING AVAILABLE ENDPOINTS...\n")

for base in BASES:
    for ep in ENDPOINTS:
        url = f"{base}/{ep}".rstrip("/")
        try:
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code in [200, 401, 403]:
                print(f"✅ Found valid endpoint → {url}  (STATUS {r.status_code})")
        except:
            pass

print("\n🔎 Scan complete — send me everything printed above.")
