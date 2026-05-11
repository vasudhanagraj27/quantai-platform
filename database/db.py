import sqlite3
import os
from pathlib import Path

DB_PATH = str(Path(__file__).parent / "quantai.sqlite")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            use_case TEXT NOT NULL,
            prompt_text TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS prompt_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_id INTEGER,
            input_vars TEXT,
            output TEXT,
            model TEXT,
            latency_ms INTEGER,
            rating INTEGER,
            ran_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS rag_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_name TEXT,
            question TEXT,
            answer TEXT,
            sources TEXT,
            asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
