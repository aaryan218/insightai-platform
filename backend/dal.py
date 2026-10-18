# data access layer
import os, joblib
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://localhost:5432/mlworkbench"
)
MODELS_DIR = os.environ.get("APP_MODELS_DIR", "models_storage")
os.makedirs(MODELS_DIR, exist_ok=True)

# Connection pool for PostgreSQL
_pool: Optional[pool.SimpleConnectionPool] = None


def get_connection_pool() -> pool.SimpleConnectionPool:
    global _pool
    if _pool is None:
        _pool = pool.SimpleConnectionPool(minconn=1, maxconn=20, dsn=DATABASE_URL)
    return _pool


@contextmanager
def get_db_cursor(commit: bool = False):
    p = get_connection_pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        p.putconn(conn)


def init_storage() -> None:
    """
    Initializes PostgreSQL tables: users and models.
    """
    with get_db_cursor(commit=True) as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(255) PRIMARY KEY,
            password_hash VARCHAR(255) NOT NULL,
            tokens INTEGER NOT NULL DEFAULT 0,
            models_count INTEGER NOT NULL DEFAULT 0,
            train_count INTEGER NOT NULL DEFAULT 0,
            predict_count INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS models (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL REFERENCES users(username) ON DELETE CASCADE,
            model_name VARCHAR(255) NOT NULL,
            model_type VARCHAR(100) NOT NULL,
            features TEXT NOT NULL,
            label VARCHAR(255) NOT NULL,
            path TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            train_count INTEGER NOT NULL DEFAULT 0,
            predict_count INTEGER NOT NULL DEFAULT 0
        );
        """)
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_models_username_name 
        ON models(username, model_name, created_at DESC);
        """)


# ===== Users =====
def create_user(username: str, password_hash: str) -> None:
    with get_db_cursor(commit=True) as cur:
        cur.execute(
            """INSERT INTO users(username, password_hash, tokens, created_at) 
               VALUES(%s, %s, %s, %s)""",
            (username, password_hash, 0, datetime.now(timezone.utc))
        )


def get_user(username: str) -> Optional[Dict[str, Any]]:
    with get_db_cursor() as cur:
        cur.execute(
            """SELECT username, password_hash, tokens, models_count, train_count, predict_count, created_at
               FROM users WHERE username = %s""",
            (username,)
        )
        r = cur.fetchone()
        if not r:
            return None
        return {
            "username": r[0],
            "password_hash": r[1],
            "tokens": r[2],
            "models_count": r[3],
            "train_count": r[4],
            "predict_count": r[5],
            "created_at": r[6].isoformat() if hasattr(r[6], "isoformat") else str(r[6])
        }


def delete_user(username: str) -> None:
    with get_db_cursor(commit=True) as cur:
        # ON DELETE CASCADE handles deleting child models automatically
        cur.execute("DELETE FROM users WHERE username = %s", (username,))


def add_tokens(username: str, amount: int) -> None:
    with get_db_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE users SET tokens = tokens + %s WHERE username = %s",
            (amount, username)
        )


def get_tokens(username: str) -> int:
    with get_db_cursor() as cur:
        cur.execute("SELECT tokens FROM users WHERE username = %s", (username,))
        r = cur.fetchone()
        return int(r[0]) if r else 0


def deduct_tokens(username: str, amount: int) -> bool:
    with get_db_cursor(commit=True) as cur:
        # Atomic deduction checking sufficient balance
        cur.execute(
            """UPDATE users 
               SET tokens = tokens - %s 
               WHERE username = %s AND tokens >= %s""",
            (amount, username, amount)
        )
        return cur.rowcount > 0


def inc_user(username: str, field: str, delta: int = 1) -> None:
    valid_fields = {"models_count", "train_count", "predict_count", "tokens"}
    if field not in valid_fields:
        raise ValueError(f"Invalid field: {field}")
    with get_db_cursor(commit=True) as cur:
        cur.execute(
            f"UPDATE users SET {field} = {field} + %s WHERE username = %s",
            (delta, username)
        )


def list_users_simple() -> List[Dict[str, Any]]:
    with get_db_cursor() as cur:
        cur.execute(
            """SELECT username, tokens, models_count, train_count, predict_count, created_at
               FROM users ORDER BY username"""
        )
        rows = cur.fetchall()
        return [
            {
                "username": r[0],
                "tokens": r[1],
                "models_count": r[2],
                "train_count": r[3],
                "predict_count": r[4],
                "created_at": r[5].isoformat() if hasattr(r[5], "isoformat") else str(r[5])
            }
            for r in rows
        ]


# ===== Models =====
def save_model(path: str, obj) -> None:
    joblib.dump(obj, path)


def load_model(path: str):
    return joblib.load(path)


def insert_model_meta(
    username: str,
    model_name: str,
    model_type: str,
    features: List[str],
    label: str,
    path: str
) -> Dict[str, Any]:
    created = datetime.now(timezone.utc)
    with get_db_cursor(commit=True) as cur:
        cur.execute(
            """INSERT INTO models(username, model_name, model_type, features, label, path, created_at, train_count, predict_count)
               VALUES(%s, %s, %s, %s, %s, %s, %s, 1, 0)
               RETURNING id, created_at""",
            (username, model_name, model_type, ",".join(features), label, path, created)
        )
        row = cur.fetchone()
        created_at_val = row[1].isoformat() if hasattr(row[1], "isoformat") else str(row[1])

    inc_user(username, "models_count", 1)
    inc_user(username, "train_count", 1)
    return {"created_at": created_at_val}


def list_models(username: str) -> List[Dict[str, Any]]:
    with get_db_cursor() as cur:
        cur.execute(
            """SELECT id, model_name, model_type, features, label, path, created_at, train_count, predict_count
               FROM models WHERE username = %s ORDER BY created_at DESC""",
            (username,)
        )
        rows = cur.fetchall()
        return [
            {
                "id": r[0],
                "model_name": r[1],
                "model_type": r[2],
                "features": r[3].split(","),
                "label": r[4],
                "path": r[5],
                "created_at": r[6].isoformat() if hasattr(r[6], "isoformat") else str(r[6]),
                "train_count": r[7],
                "predict_count": r[8],
            }
            for r in rows
        ]


def get_latest_model(username: str, model_name: str) -> Optional[Dict[str, Any]]:
    with get_db_cursor() as cur:
        cur.execute(
            """SELECT id, model_type, features, label, path
               FROM models
               WHERE username = %s AND model_name = %s
               ORDER BY created_at DESC LIMIT 1""",
            (username, model_name)
        )
        r = cur.fetchone()
        if not r:
            return None
        return {
            "id": r[0],
            "model_type": r[1],
            "features": r[2].split(","),
            "label": r[3],
            "path": r[4]
        }


def inc_model(model_id: int, field: str, delta: int = 1) -> None:
    valid_fields = {"train_count", "predict_count"}
    if field not in valid_fields:
        raise ValueError(f"Invalid field: {field}")
    with get_db_cursor(commit=True) as cur:
        cur.execute(
            f"UPDATE models SET {field} = {field} + %s WHERE id = %s",
            (delta, model_id)
        )
