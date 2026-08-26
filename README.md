# wow-auction-pipeline

A data pipeline that collects hourly auction house snapshots from the
World of Warcraft API and stores them to build a price history over time.

Blizzard exposes the current state of a realm's auction house and refreshes
it roughly once an hour, but keeps no history. This project captures those
snapshots as they are published so the historical data actually exists.

## Status

Work in progress. Currently building the collector.

- [x] Repository setup
- [x] Blizzard API authentication (OAuth2 client credentials)
- [ ] Download and store a raw snapshot
- [ ] Hourly scheduling
- [ ] Parse into PostgreSQL
- [ ] REST API for price history

## Stack

Python, `requests`. PostgreSQL and FastAPI planned.