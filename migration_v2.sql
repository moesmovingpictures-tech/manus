DROP TABLE IF EXISTS conv_turn;
DROP TABLE IF EXISTS concept;
DROP TABLE IF EXISTS concept_link;
DROP TABLE IF EXISTS debug_log;
DROP TABLE IF EXISTS lessons; -- Drop the old lessons table if it exists

CREATE TABLE conv_turn(
id          INTEGER PRIMARY KEY AUTOINCREMENT,
ts          INTEGER NOT NULL DEFAULT (CAST(strftime("%s", "now") AS INTEGER)),
role        TEXT CHECK (role IN (
    "user",
    "assistant",
    "system",
    "self"
)),
text        TEXT NOT NULL,
meta        TEXT,
embedding   TEXT -- Changed from BLOB to TEXT
);

CREATE TABLE concept(
id          INTEGER PRIMARY KEY AUTOINCREMENT,
name        TEXT UNIQUE,
aliases     TEXT,
summary     TEXT,
meta        TEXT,
embedding   TEXT -- Changed from BLOB to TEXT
);

CREATE TABLE concept_link(
src_id  INTEGER,
dst_id  INTEGER,
rel     TEXT,
PRIMARY KEY (src_id, dst_id, rel),
FOREIGN KEY (src_id) REFERENCES concept(id),
FOREIGN KEY (dst_id) REFERENCES concept(id)
);

CREATE TABLE debug_log(
id      INTEGER PRIMARY KEY AUTOINCREMENT,
ts      INTEGER NOT NULL DEFAULT (CAST(strftime("%s", "now") AS INTEGER)),
source  TEXT,
level   TEXT CHECK (level IN (
    "info",
    "warn",
    "error",
    "fix"
)),
msg     TEXT,
patch   TEXT
);

-- SQLite does not support custom functions in triggers directly like PostgreSQL.
-- Embedding will need to be handled in the application layer before insertion.


