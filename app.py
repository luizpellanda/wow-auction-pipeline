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


def get_access_token(client_id, client_secret):
    """Exchange the client credentials for an OAuth2 access token."""
    try:
        response = requests.post(
            TOKEN_URL,
            auth=(client_id, client_secret),
            data={'grant_type': 'client_credentials'},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        sys.exit(f'Token request failed: {e}')
    print(f'Token status: {response.status_code}')

    token_data = response.json()
    print(f'Token expires in: {token_data["expires_in"]}s')
    return token_data['access_token']


def download_auctions(access_token):
    """Download the commodities snapshot."""
    try:
        response = requests.get(
            AUCTIONS_URL,
            headers={'Authorization': f'Bearer {access_token}'},
            params={'namespace': 'dynamic-us', 'locale': 'en_US'},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        sys.exit(f'Auction data download failed: {e}')
    print(f'Auctions status: {response.status_code}')
    print(f'Auctions size: {len(response.content)} bytes')
    return response


def build_snapshot_stamp(response):
    """Return the snapshot's publication time as a filename-safe stamp."""
    last_modified = response.headers['Last-Modified']
    snapshot_time = parsedate_to_datetime(last_modified)
    snapshot_stamp = snapshot_time.strftime('%Y%m%dT%H%M%SZ')
    print(f'Snapshot: {snapshot_stamp}')
    return snapshot_stamp


def save_raw_snapshot(content, snapshot_stamp):
    """Save the raw bytes, gzip-compressed (lossless)."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f'commodities_{snapshot_stamp}.json.gz'

    with gzip.open(raw_path, 'wb') as f:
        f.write(content)
    print(f'Saved to: {raw_path}')
    return raw_path


def main():
    """Collect one snapshot: authenticate, download, save."""
    load_dotenv()

    client_id = os.getenv('BLIZZARD_CLIENT_ID')
    client_secret = os.getenv('BLIZZARD_CLIENT_SECRET')

    access_token = get_access_token(client_id, client_secret)
    auctions_response = download_auctions(access_token)
    snapshot_stamp = build_snapshot_stamp(auctions_response)
    save_raw_snapshot(auctions_response.content, snapshot_stamp)


if __name__ == '__main__':
    main()
