import requests
from requests.auth import HTTPBasicAuth

# Intuit Developer App Credentials
client_id = "ABdFFhCIDRPZ02OFZKsHKZ08o6YWrjuHrir4uLkwKW69Re8A03"
client_secret = "QgoejwTxpMo1ntEYB77AoOFRvEMGUDxLAHdHyBab"
redirect_uri = "http://localhost:8000/callback"
auth_code = "XAB11746672444b1Od8Ea34fIdeq1shmTJdL7xyX4DBO6jYH3l"
realm_id = "4620816365320749920"

# QuickBooks OAuth token endpoint
url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"
}

payload = {
    "grant_type": "authorization_code",
    "code": auth_code,
    "redirect_uri": redirect_uri
}

# Make request for token
response = requests.post(
    url,
    headers=headers,
    data=payload,
    auth=HTTPBasicAuth(client_id, client_secret)
)

print("Status Code:", response.status_code)
try:
    data = response.json()
    print("Response JSON:")
    print(data)
except Exception as e:
    print("Could not parse JSON. Raw response:")
    print(response.text)
    print("Error:", e)
