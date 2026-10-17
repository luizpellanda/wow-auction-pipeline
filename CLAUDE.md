# wow-auction-pipeline — working notes

Learning project, run as a class: for each step Claude explains every concept from
scratch (even ones the user already knows), the user writes the code, Claude reviews
and points out more efficient alternatives with the reasoning.
Don't write implementation code unless explicitly asked.
Step loop: explain → user codes → review → 2-3 recall questions → user commits
(Claude provides the commit message in English) → user writes `notes/NN-topic.md`
(gitignored) in their own words → Claude reviews notes → next step.

## Goal
Hourly collector of World of Warcraft auction house snapshots (Blizzard Game Data API)
to build price history. Blizzard only publishes current state and overwrites it hourly.

Final shape: hourly collector → PostgreSQL (time series) → FastAPI
(`/items/{id}/history`, top movers) → deploy.

## Environment
- Path: `~/projects/portfolio/wow-auction-pipeline` (Ubuntu on WSL2), public repo
- venv: `venv/` → `source venv/bin/activate`
- Credentials in `.env`: `BLIZZARD_CLIENT_ID`, `BLIZZARD_CLIENT_SECRET` (loaded via python-dotenv)

## API details (validated via curl)
- Token: `POST https://oauth.battle.net/token`, basic auth `id:secret`,
  body `grant_type=client_credentials`. `expires_in` 86399 (~24h).
- Data: `GET https://us.api.blizzard.com/data/wow/auctions/commodities?namespace=dynamic-us&locale=en_US`
  with header `Authorization: Bearer <token>`.
- Commodities endpoint is region-wide (US); chosen to avoid connected-realm IDs.
- Snapshot size: ~27 MB JSON, ~290k auctions. `unit_price` is in copper.

## Roadmap
- [x] Repo, venv, .gitignore, README
- [x] OAuth2 client credentials via curl
- [x] `.env` + python-dotenv validated (`test_env.py`, untracked)
- [ ] **Next:** `app.py` — translate the two curls to `requests`; print only
      `status_code` and `len(response.content)`, never the body
- [ ] Save raw to disk, untransformed (raw layer is immutable)
- [ ] gzip + filename from Blizzard's timestamp, not local clock (idempotent re-runs)
- [ ] try/except around network calls
- [ ] Refactor into functions/class + `if __name__ == '__main__'`
- [ ] VPS + cron (can't run on the user's PC 24/7)
- [ ] PostgreSQL, FastAPI, deploy

## Known pitfalls
- Blizzard docs "Try It" button returns 400 (uses authorization code flow). Ignore it.
- Never print the full response (tens of MB).
- Token expires in 24h — must renew.
- `nano` can leave `.env.save` with the secret → `.env*` in .gitignore.
- Never `git add .` — big JSON and `.env` live in the folder. `git status` first, add by name.
- `commands.txt` (gitignored) holds raw credentials in curl examples.

## Review checklist (mistakes from a previous project)
- NameError when the API call failed (variable defined only on success path)
- `json.dump` without `ensure_ascii=False`
- Filenames built from external data without sanitizing (path traversal)
- No try/except on network calls
- No functions, no `if __name__ == '__main__'`
- Output data committed to git

## Pending decisions
- AWS account deferred on purpose (free tier for accounts created after 2025-07-15
  is expiring credits, not 12 months). Open only when actually needed.
- Storage: gzipped snapshot × 24/day fills a cheap VPS disk in months. Decide in
  the Postgres phase (likely keep raw compressed + store per-item hourly aggregates).
