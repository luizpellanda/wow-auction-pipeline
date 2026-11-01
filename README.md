# wow-auction-pipeline

A data pipeline that collects hourly auction house snapshots from the
World of Warcraft API and stores them to build a price history over time.

Blizzard exposes the current state of the region-wide commodities auction house
and refreshes it roughly once an hour, but keeps no history. This project
captures those snapshots as they are published so the historical data actually exists.

## How it works

- Authenticates with Blizzard (OAuth2 client credentials).
- Downloads the current commodities snapshot.
- Names the file by Blizzard's publication time, so re-running never creates duplicates.
- Saves the raw data gzip-compressed to `data/raw/`.
- Loads an hourly summary per item (lowest price, total quantity) into PostgreSQL.
- Fetches item names from the Blizzard Item API.

## Setup

```bash
git clone https://github.com/luizpellanda/wow-auction-pipeline.git
cd wow-auction-pipeline
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with your Blizzard API credentials
(get them at https://develop.battle.net):

```
BLIZZARD_CLIENT_ID=your_client_id_here
BLIZZARD_CLIENT_SECRET=your_client_secret_here
```

Create the database and tables (requires PostgreSQL):

```bash
createdb wow
psql wow -f schema.sql
```

Run:

```bash
./run.sh
```

## Status

- [x] Repository setup
- [x] Blizzard API authentication (OAuth2 client credentials)
- [x] Python implementation of the collector
- [x] Gzip compression
- [x] Error handling
- [x] Refactor into functions
- [x] Hourly scheduling
- [x] Parse into PostgreSQL
- [x] Item names
- [ ] REST API for price history
- [ ] Web UI with price charts

## Stack

Python, `requests`, `python-dotenv`, `psycopg`, PostgreSQL.
Runs hourly via cron on an Ubuntu VPS (DigitalOcean). FastAPI planned.
