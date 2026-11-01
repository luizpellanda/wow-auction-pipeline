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
