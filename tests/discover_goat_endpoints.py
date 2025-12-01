import requests

BASE_URL = "https://mcp.balldontlie.io/mcp"
API_KEY  = "081aceca-0dd3-40f8-a617-bf5ce7212364"  # <-- replace with your real key

headers = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}

response = requests.get(BASE_URL, headers=headers)

print("\nSTATUS:", response.status_code)
print("\nRAW RESPONSE:\n", response.text[:2000])
