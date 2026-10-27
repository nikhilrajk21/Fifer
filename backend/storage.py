"""Local coursework history and anonymous quota counters; no sensory answers or credentials."""
from contextlib import contextmanager
from pathlib import Path
import sqlite3


SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_versions (
    version INTEGER PRIMARY KEY
);
INSERT OR IGNORE INTO schema_versions(version) VALUES (1);
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    message_opt_in INTEGER NOT NULL DEFAULT 0 CHECK (message_opt_in IN (0, 1)),
    history_epoch INTEGER NOT NULL DEFAULT 0
);
INSERT OR IGNORE INTO settings(id) VALUES (1);
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    skill TEXT NOT NULL CHECK (skill = '5-4-3-2-1'),
    started_at TEXT NOT NULL,
    ended_at TEXT,
    updated_at TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'paused', 'stopped', 'completed')),
    current_step TEXT NOT NULL CHECK (current_step IN ('see','feel','checkin','hear','smell','taste','complete')),
    checkin TEXT CHECK (checkin IN ('A little better','About the same','A little harder','Not sure')),
    setup_ms INTEGER NOT NULL CHECK (setup_ms >= 0),
    active_ms INTEGER NOT NULL CHECK (active_ms >= 0),
    paused_ms INTEGER NOT NULL CHECK (paused_ms >= 0),
    support_ms INTEGER NOT NULL CHECK (support_ms >= 0),
    revision INTEGER NOT NULL CHECK (revision >= 1)
);
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL UNIQUE REFERENCES sessions(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user','assistant')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS sessions_completed ON sessions(status, ended_at);
CREATE INDEX IF NOT EXISTS messages_conversation ON messages(conversation_id, created_at);
CREATE TABLE IF NOT EXISTS chat_sessions (
    id TEXT PRIMARY KEY,
    browser_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    ended_at TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','stopped')),
    requests INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS chat_requests (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK(role IN ('user','assistant')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS chat_daily_usage (
    browser_hash TEXT NOT NULL,
    utc_day TEXT NOT NULL,
    requests INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY(browser_hash, utc_day)
);
INSERT OR IGNORE INTO schema_versions(version) VALUES (2);
CREATE TABLE IF NOT EXISTS voice_daily_usage (
    browser_hash TEXT NOT NULL,
    utc_day TEXT NOT NULL,
    sessions INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY(browser_hash, utc_day)
);
INSERT OR IGNORE INTO schema_versions(version) VALUES (3);
"""


class Store:
    def __init__(self, path: Path):
        self.path = Path(path)

    @contextmanager
    def connection(self, *, write=False):
        db = sqlite3.connect(self.path, timeout=2)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        db.execute("PRAGMA secure_delete = ON")
        try:
            db.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def initialize(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            db.executescript(SCHEMA)


def settings(db):
    row = db.execute("SELECT message_opt_in, history_epoch FROM settings WHERE id = 1").fetchone()
    return {"message_opt_in": bool(row["message_opt_in"]), "history_epoch": row["history_epoch"]}


def session(db, session_id):
    row = db.execute("SELECT * FROM sessions WHERE id = ?", (str(session_id),)).fetchone()
    return dict(row) if row else None
