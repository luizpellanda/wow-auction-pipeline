"""Fetch item names from the Blizzard Item API and store them in the items table."""

import os

import psycopg
import requests
from dotenv import load_dotenv

from app import get_access_token

ITEM_URL = 'https://us.api.blizzard.com/data/wow/item'
REQUEST_TIMEOUT = 30  # seconds without a response before giving up
DATABASE_URL = 'postgresql:///wow'
COMMIT_EVERY = 100  # save progress after this many items


def fetch_item_name(session, item_id):
    """Return the English name of one item, or None if Blizzard doesn't know it."""
    response = session.get(
        f'{ITEM_URL}/{item_id}',
        params={'namespace': 'static-us', 'locale': 'en_US'},
        timeout=REQUEST_TIMEOUT,
    )
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()['name']


def find_missing_item_ids(conn):
    """Return the ids that appear in prices but have no name in items yet."""
    rows = conn.execute(
        'SELECT DISTINCT item_id FROM prices WHERE item_id NOT IN (SELECT item_id FROM items)'
    ).fetchall()

    item_ids = []
    for row in rows:
        item_ids.append(row[0])
    return item_ids


def save_item_name(conn, item_id, name):
    """Insert one item name (ignored if the item is already there)."""
    conn.execute(
        'INSERT INTO items (item_id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING',
        (item_id, name),
    )


def main():
    """Fetch and store the names of every item that doesn't have one yet."""
    load_dotenv()
    access_token = get_access_token(
        os.getenv('BLIZZARD_CLIENT_ID'),
        os.getenv('BLIZZARD_CLIENT_SECRET'),
    )

    session = requests.Session()
    session.headers['Authorization'] = f'Bearer {access_token}'

    with psycopg.connect(DATABASE_URL) as conn:
        missing_ids = find_missing_item_ids(conn)
        print(f'Items without a name: {len(missing_ids)}')

        saved_count = 0
        for item_id in missing_ids:
            try:
                name = fetch_item_name(session, item_id)
            except requests.RequestException as e:
                print(f'Skipped item {item_id}: {e}')
                continue

            if name is None:
                name = f'Unknown item {item_id}'

            save_item_name(conn, item_id, name)
            saved_count += 1

            if saved_count % COMMIT_EVERY == 0:
                conn.commit()
                print(f'Saved {saved_count}/{len(missing_ids)}')

        conn.commit()
        print(f'Items: {saved_count} new name(s) saved')


if __name__ == '__main__':
    main()
