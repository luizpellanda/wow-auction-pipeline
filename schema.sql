CREATE TABLE IF NOT EXISTS prices (
    snapshot_time timestamptz NOT NULL,
    item_id integer NOT NULL,
    min_price bigint NOT NULL,
    total_quantity bigint NOT NULL,
    PRIMARY KEY (snapshot_time, item_id)
);

CREATE TABLE IF NOT EXISTS items (
    item_id integer PRIMARY KEY,
    name text NOT NULL
);

-- Charts ask for one item over time; the primary key starts with snapshot_time, so add the other order.
CREATE INDEX IF NOT EXISTS prices_item_time_idx ON prices (item_id, snapshot_time);
