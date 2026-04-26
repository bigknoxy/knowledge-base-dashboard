import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

DB_PATH = Path("kbd.db")


def get_connection(path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def db_conn(path: Path = DB_PATH):
    conn = get_connection(path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def create_tables(path: Path = DB_PATH) -> None:
    with db_conn(path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS repos (
                id              TEXT PRIMARY KEY,
                path            TEXT UNIQUE NOT NULL,
                name            TEXT NOT NULL,
                description     TEXT,
                url             TEXT,
                created_at      DATETIME,
                last_active     DATETIME,
                total_commits   INTEGER DEFAULT 0,
                branch_count    INTEGER DEFAULT 1,
                primary_lang    TEXT,
                stack_json      TEXT,
                status          TEXT DEFAULT 'active',
                scanned_at      DATETIME
            );

            CREATE TABLE IF NOT EXISTS experiments (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_id         TEXT REFERENCES repos(id),
                jsonl_path      TEXT NOT NULL,
                session_name    TEXT,
                metric_name     TEXT,
                metric_unit     TEXT,
                direction       TEXT,
                total_runs      INTEGER DEFAULT 0,
                kept_runs       INTEGER DEFAULT 0,
                discarded_runs  INTEGER DEFAULT 0,
                crashed_runs    INTEGER DEFAULT 0,
                best_metric     REAL,
                noise_floor     REAL,
                started_at      DATETIME,
                completed_at    DATETIME
            );

            CREATE TABLE IF NOT EXISTS experiment_runs (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id   INTEGER REFERENCES experiments(id),
                "commit"        TEXT,
                metric          REAL,
                status          TEXT,
                description     TEXT,
                extra_metrics   TEXT,
                duration_ms     INTEGER,
                run_order       INTEGER,
                created_at      DATETIME
            );

            CREATE TABLE IF NOT EXISTS patterns (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                trigger         TEXT NOT NULL,
                action          TEXT NOT NULL,
                frequency       INTEGER DEFAULT 1,
                confidence      REAL DEFAULT 0.0,
                first_seen      DATETIME,
                last_seen       DATETIME
            );

            CREATE TABLE IF NOT EXISTS insights (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id      INTEGER REFERENCES patterns(id),
                suggestion      TEXT NOT NULL,
                urgency         TEXT DEFAULT 'low',
                resolved        INTEGER DEFAULT 0,
                created_at      DATETIME
            );

            CREATE INDEX IF NOT EXISTS idx_repos_last_active ON repos(last_active);
            CREATE INDEX IF NOT EXISTS idx_repos_primary_lang ON repos(primary_lang);
            CREATE INDEX IF NOT EXISTS idx_experiments_repo ON experiments(repo_id);
            CREATE INDEX IF NOT EXISTS idx_runs_experiment ON experiment_runs(experiment_id);
            CREATE INDEX IF NOT EXISTS idx_runs_status ON experiment_runs(status);
        """)


# --- Repos CRUD ---

def upsert_repo(conn: sqlite3.Connection, repo: dict[str, Any]) -> None:
    conn.execute("""
        INSERT INTO repos (id, path, name, description, url, created_at, last_active,
            total_commits, branch_count, primary_lang, stack_json, status, scanned_at)
        VALUES (:id,:path,:name,:description,:url,:created_at,:last_active,
            :total_commits,:branch_count,:primary_lang,:stack_json,:status,:scanned_at)
        ON CONFLICT(id) DO UPDATE SET
            last_active=excluded.last_active,
            total_commits=excluded.total_commits,
            primary_lang=excluded.primary_lang,
            stack_json=excluded.stack_json,
            status=excluded.status,
            scanned_at=excluded.scanned_at
    """, repo)


def get_all_repos(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM repos ORDER BY last_active DESC").fetchall()


def get_repo(conn: sqlite3.Connection, repo_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM repos WHERE id=?", (repo_id,)).fetchone()


# --- Experiments CRUD ---

def insert_experiment(conn: sqlite3.Connection, exp: dict[str, Any]) -> int:
    cur = conn.execute("""
        INSERT INTO experiments (repo_id, jsonl_path, session_name, metric_name, metric_unit,
            direction, total_runs, kept_runs, discarded_runs, crashed_runs,
            best_metric, noise_floor, started_at, completed_at)
        VALUES (:repo_id,:jsonl_path,:session_name,:metric_name,:metric_unit,
            :direction,:total_runs,:kept_runs,:discarded_runs,:crashed_runs,
            :best_metric,:noise_floor,:started_at,:completed_at)
    """, exp)
    return cur.lastrowid


def insert_run(conn: sqlite3.Connection, run: dict[str, Any]) -> None:
    conn.execute("""
        INSERT INTO experiment_runs (experiment_id, commit, metric, status, description,
            extra_metrics, duration_ms, run_order, created_at)
        VALUES (:experiment_id,:commit,:metric,:status,:description,
            :extra_metrics,:duration_ms,:run_order,:created_at)
    """, run)


# --- Patterns CRUD ---

def upsert_pattern(conn: sqlite3.Connection, trigger: str, action: str,
                   confidence: float) -> int:
    existing = conn.execute(
        "SELECT id, frequency FROM patterns WHERE trigger=? AND action=?",
        (trigger, action)
    ).fetchone()
    now = datetime.utcnow().isoformat()
    if existing:
        conn.execute(
            "UPDATE patterns SET frequency=frequency+1, confidence=?, last_seen=? WHERE id=?",
            (confidence, now, existing["id"])
        )
        return existing["id"]
    cur = conn.execute(
        (
            "INSERT INTO patterns "
            "(trigger, action, confidence, first_seen, last_seen) "
            "VALUES (?,?,?,?,?)"
        ),
        (trigger, action, confidence, now, now)
    )
    return cur.lastrowid


def get_all_patterns(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM patterns ORDER BY frequency DESC").fetchall()


def insert_insight(conn: sqlite3.Connection, pattern_id: int,
                   suggestion: str, urgency: str = "low") -> None:
    conn.execute(
        "INSERT INTO insights (pattern_id, suggestion, urgency, created_at) VALUES (?,?,?,?)",
        (pattern_id, suggestion, urgency, datetime.utcnow().isoformat())
    )


def get_pending_insights(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM insights WHERE resolved=0 ORDER BY urgency DESC, created_at DESC"
    ).fetchall()
