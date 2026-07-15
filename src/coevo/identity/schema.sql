PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS identity_metadata (
  singleton INTEGER PRIMARY KEY CHECK(singleton = 1), store_id TEXT NOT NULL UNIQUE, schema_version TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS organizations (
  organization_id TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE, name TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1 CHECK(version > 0)
);
CREATE TABLE IF NOT EXISTS users (
  user_id TEXT PRIMARY KEY, organization_id TEXT NOT NULL REFERENCES organizations(organization_id), display_name TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1 CHECK(version > 0)
);
CREATE TABLE IF NOT EXISTS clients (
  client_id TEXT PRIMARY KEY, organization_id TEXT NOT NULL REFERENCES organizations(organization_id), assigned_user_id TEXT NOT NULL REFERENCES users(user_id), display_name TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1 CHECK(version > 0)
);
CREATE TABLE IF NOT EXISTS trusted_certificates (
  certificate_id TEXT PRIMARY KEY, owner_user_id TEXT NOT NULL REFERENCES users(user_id), bound_client_id TEXT NOT NULL REFERENCES clients(client_id),
  certificate_der BLOB NOT NULL, public_key_spki_der BLOB NOT NULL, fingerprint_sha256 TEXT NOT NULL UNIQUE,
  valid_from TEXT NOT NULL, valid_to TEXT NOT NULL, serial_number TEXT NOT NULL, public_key_algorithm_oid TEXT NOT NULL,
  revoked INTEGER NOT NULL DEFAULT 0 CHECK(revoked IN (0,1)), version INTEGER NOT NULL DEFAULT 1 CHECK(version > 0)
);
CREATE TABLE IF NOT EXISTS project_role_bindings (
  project_id TEXT NOT NULL, user_id TEXT NOT NULL REFERENCES users(user_id), role_code TEXT NOT NULL CHECK(role_code IN ('project_owner','project_member')),
  PRIMARY KEY(project_id,user_id,role_code)
);
CREATE TABLE IF NOT EXISTS identity_commands (
  request_id TEXT PRIMARY KEY, payload_digest TEXT NOT NULL, result_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS identity_audit_events (
  sequence_no INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL UNIQUE, occurred_at TEXT NOT NULL, actor_id TEXT NOT NULL,
  action TEXT NOT NULL, request_id TEXT NOT NULL, result TEXT NOT NULL, target_summary TEXT NOT NULL,
  payload_digest TEXT, prev_hash TEXT NOT NULL, event_hash TEXT NOT NULL UNIQUE
);
