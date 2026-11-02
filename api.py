"""HTTP API that serves item prices from the database."""

from typing import Annotated

import psycopg
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles

DATABASE_URL = 'postgresql:///wow'

app = FastAPI()


@app.get('/items/{item_id}')
def get_item(item_id: int):
    """Return one item's id and name."""
    with psycopg.connect(DATABASE_URL) as conn:
        row = conn.execute(
            'SELECT item_id, name FROM items WHERE item_id = %s',
            (item_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail='Item not found')

    return {'item_id': row[0], 'name': row[1]}


@app.get('/items/{item_id}/history')
def get_item_history(item_id: int, days: Annotated[int, Query(ge=1, le=365)] = 30):
    """Return the item's lowest price and total quantity over the last `days` days, oldest first."""
    with psycopg.connect(DATABASE_URL) as conn:
        rows = conn.execute(
            'SELECT snapshot_time, min_price, total_quantity FROM prices '
            'WHERE item_id = %s AND snapshot_time >= now() - make_interval(days => %s) '
            'ORDER BY snapshot_time',
            (item_id, days),
        ).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail='No prices for this item')

    history = []
    for row in rows:
        history.append({
            'time': row[0],
            'min_price': row[1],
            'total_quantity': row[2],
        })
    return history


@app.get('/items')
def search_items(search: str):
    """Return up to 20 items whose name contains the search text."""
    with psycopg.connect(DATABASE_URL) as conn:
        rows = conn.execute(
            'SELECT item_id, name FROM items WHERE name ILIKE %s ORDER BY name LIMIT 20',
            (f'%{search}%',),
        ).fetchall()

    results = []
    for row in rows:
        results.append({'item_id': row[0], 'name': row[1]})
    return results


# The website (static/index.html and friends). Mounted last so the API routes above win.
app.mount('/', StaticFiles(directory='static', html=True), name='site')
