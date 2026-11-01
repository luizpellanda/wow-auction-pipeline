#!/usr/bin/env bash
# Hourly job: collect the latest snapshot, load it into PostgreSQL, fetch any new item names.
set -e

cd "$(dirname "$0")"

echo "=== $(date -u) ==="
venv/bin/python -u app.py
venv/bin/python -u loader.py
venv/bin/python -u items.py
