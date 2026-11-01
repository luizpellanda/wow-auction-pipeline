"""Summarize raw commodities snapshots into one row per item and load them into PostgreSQL."""

import gzip
import json
from datetime import datetime, timezone
from pathlib import Path

import psycopg

RAW_DIR = Path('data/raw')
DATABASE_URL = 'postgresql:///wow'


def read_snapshot(path):
    """Read a gzip-compressed snapshot file and return it as a dict."""
    with gzip.open(path, 'rb') as f:
        return json.load(f)


def summarize_auctions(auctions):
    """Reduce a list of auctions to the lowest price and total quantity per item."""
    summary = {}
    for auction in auctions:
        item_id = auction['item']['id']
        price = auction['unit_price']
        quantity = auction['quantity']

        if item_id not in summary:
            summary[item_id] = {'min_price': price, 'total_quantity': quantity}
        else:
            summary[item_id]['min_price'] = min(summary[item_id]['min_price'], price)
            summary[item_id]['total_quantity'] += quantity

    return summary


def snapshot_time_from_path(path):
    """Get the snapshot's UTC time from a name like commodities_20261101T013345Z.json.gz."""
    stamp = path.name.removeprefix('commodities_').removesuffix('.json.gz')
    return datetime.strptime(stamp, '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc)


def is_loaded(conn, snapshot_time):
    """Return True if this snapshot already has rows in the prices table."""
    row = conn.execute(
        'SELECT 1 FROM prices WHERE snapshot_time = %s LIMIT 1',
        (snapshot_time,),
    ).fetchone()
    return row is not None


def save_summary(conn, snapshot_time, summary):
    """Insert one row per item for this snapshot and return how many rows were sent."""
    rows = []
    for item_id, values in summary.items():
        rows.append((snapshot_time, item_id, values['min_price'], values['total_quantity']))

    with conn.cursor() as cur:
        cur.executemany(
            'INSERT INTO prices VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING',
            rows,
        )
    conn.commit()
    return len(rows)


def main():
    """Load every snapshot in data/raw that is not in the database yet."""
    loaded_count = 0
    with psycopg.connect(DATABASE_URL) as conn:
        for path in sorted(RAW_DIR.glob('*.json.gz')):
            snapshot_time = snapshot_time_from_path(path)
            if is_loaded(conn, snapshot_time):
                continue

            auctions = read_snapshot(path)['auctions']
            summary = summarize_auctions(auctions)
            row_count = save_summary(conn, snapshot_time, summary)
            print(f'Saved {row_count} items for {snapshot_time}')
            loaded_count += 1

    print(f'Loader: {loaded_count} new snapshot(s) loaded')


if __name__ == '__main__':
    main()
