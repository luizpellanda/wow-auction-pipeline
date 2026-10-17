import os

import requests
from dotenv import load_dotenv

TOKEN_URL = 'https://oauth.battle.net/token'
AUCTIONS_URL = 'https://us.api.blizzard.com/data/wow/auctions/commodities'

load_dotenv()

client_id = os.getenv('BLIZZARD_CLIENT_ID')
client_secret = os.getenv('BLIZZARD_CLIENT_SECRET')

response = requests.post(
    TOKEN_URL,
    auth=(client_id, client_secret),
    data={'grant_type': 'client_credentials'},
)

print(f'Status: {response.status_code}')

token_data = response.json()
print(f'Keys: {token_data.keys()}')
print(f'Expires in: {token_data["expires_in"]}')

access_token = token_data['access_token']

auctions_response = requests.get(
    AUCTIONS_URL,
    headers={'Authorization': f'Bearer {access_token}'},
    params={'namespace': 'dynamic-us', 'locale': 'en_US'},
)

print(f'Auctions status: {auctions_response.status_code}')
print(f'Auctions size: {len(auctions_response.content)} bytes')