"""Download the current WoW commodities auction snapshot and save it gzip-compressed to disk."""

import gzip
import os
import sys
from email.utils import parsedate_to_datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

TOKEN_URL = 'https://oauth.battle.net/token'
AUCTIONS_URL = 'https://us.api.blizzard.com/data/wow/auctions/commodities'
RAW_DIR = Path('data/raw')
REQUEST_TIMEOUT = 30  # seconds without a response before giving up

load_dotenv()

client_id = os.getenv('BLIZZARD_CLIENT_ID')
client_secret = os.getenv('BLIZZARD_CLIENT_SECRET')

# Get an access token (OAuth2 client credentials)
try:
    token_response = requests.post(
        TOKEN_URL,
        auth=(client_id, client_secret),
        data={'grant_type': 'client_credentials'},
        timeout=REQUEST_TIMEOUT,
    )
    token_response.raise_for_status()
except requests.RequestException as e:
    sys.exit(f'Token request failed: {e}')
print(f'Token status: {token_response.status_code}')

token_data = token_response.json()
access_token = token_data['access_token']
print(f'Token expires in: {token_data["expires_in"]}s')

# Download the commodities snapshot
try:
    auctions_response = requests.get(
        AUCTIONS_URL,
        headers={'Authorization': f'Bearer {access_token}'},
        params={'namespace': 'dynamic-us', 'locale': 'en_US'},
        timeout=REQUEST_TIMEOUT,
    )
    auctions_response.raise_for_status()
except requests.RequestException as e:
    sys.exit(f'Auction data download failed: {e}')
print(f'Auctions status: {auctions_response.status_code}')
print(f'Auctions size: {len(auctions_response.content)} bytes')

# Name the file by Blizzard's publication time, not the local clock
last_modified = auctions_response.headers['Last-Modified']
snapshot_time = parsedate_to_datetime(last_modified)
snapshot_stamp = snapshot_time.strftime('%Y%m%dT%H%M%SZ')
print(f'Snapshot: {snapshot_stamp}')

# Save the raw bytes, gzip-compressed (lossless)
RAW_DIR.mkdir(parents=True, exist_ok=True)
raw_path = RAW_DIR / f'commodities_{snapshot_stamp}.json.gz'

with gzip.open(raw_path, 'wb') as f:
    f.write(auctions_response.content)

print(f'Saved to: {raw_path}')
