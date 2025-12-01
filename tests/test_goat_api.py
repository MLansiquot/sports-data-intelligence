import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

BASE_URL = "https://mcp.balldontlie.io/mcp"
API_KEY  = "081aceca-0dd3-40f8-a617-bf5ce7212364"   # replace with real key

headers = {
    "Authorization": API_KEY,           # NO "Bearer" unless docs require it
    "Content-Type": "application/json"
}

response = requests.get(f"{BASE_URL}/teams", headers=headers)

print("\nSTATUS:", response.status_code)
print("RESPONSE (first 500 chars):\n", response.text[:500])

