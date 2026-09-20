# wow-auction-pipeline

A data pipeline that collects hourly auction house snapshots from the
World of Warcraft API and stores them to build a price history over time.

Blizzard exposes the current state of a realm's auction house and refreshes
it roughly once an hour, but keeps no history. This project captures those
snapshots as they are published so the historical data actually exists.

## Status

Paused — building fundamentals first (HTTP, APIs, persistence).

- [x] Repository setup
- [x] Blizzard API authentication (OAuth2 client credentials) — validated via curl
- [ ] Python implementation of the collector
- [ ] Hourly scheduling
- [ ] Parse into PostgreSQL
- [ ] REST API for price history

## Stack

Python, `requests`. PostgreSQL and FastAPI planned.