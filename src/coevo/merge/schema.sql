PRAGMA foreign_keys=ON;
CREATE TABLE merge_metadata(
  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
  store_id TEXT NOT NULL UNIQUE,
  schema_version TEXT NOT NULL
);
CREATE TABLE merge_receipts(
  store_sequence INTEGER PRIMARY KEY,
  receipt_id TEXT NOT NULL UNIQUE,
  package_id TEXT NOT NULL UNIQUE,
  package_digest TEXT NOT NULL UNIQUE,
  project_id TEXT NOT NULL,
  payload BLOB NOT NULL,
  signature BLOB NOT NULL,
  receipt_hash TEXT NOT NULL UNIQUE
);
