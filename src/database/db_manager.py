import sqlite3
import os
from contextlib import contextmanager
from src.config import DB_PATH, SRC_DIR

SCHEMA_PATH = os.path.join(SRC_DIR, "database", "schema.sql")

@contextmanager
def get_db_connection():
    """
    Context manager for SQLite connections. 
    Enforces foreign keys and handles auto-commit/auto-rollback.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Returns rows as dictionary-like objects
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def initialize_database():
    """
    Executes the schema.sql file to set up all tables and indices.
    Safe to run repeatedly (uses CREATE TABLE IF NOT EXISTS).
    """
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)
    
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")
        
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()
        
    with get_db_connection() as conn:
        conn.executescript(schema_sql)
    print(f"[DB] Database initialized/verified at: {DB_PATH}")
