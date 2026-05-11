import re
import json
from typing import Optional
from database.db import get_connection


# ── CRUD ──────────────────────────────────────────────────────────────────────

def create_prompt(name: str, use_case: str, prompt_text: str, notes: str = "") -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO prompts (name, use_case, prompt_text, notes) VALUES (?, ?, ?, ?)",
        (name, use_case, prompt_text, notes),
    )
    conn.commit()
    prompt_id = cur.lastrowid
    conn.close()
    return prompt_id


def get_all_prompts() -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM prompts ORDER BY updated_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_prompt(prompt_id: int) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_prompt(prompt_id: int, name: str, use_case: str, prompt_text: str, notes: str):
    conn = get_connection()
    conn.execute(
        """UPDATE prompts
           SET name=?, use_case=?, prompt_text=?, notes=?,
               updated_at=CURRENT_TIMESTAMP
           WHERE id=?""",
        (name, use_case, prompt_text, notes, prompt_id),
    )
    conn.commit()
    conn.close()


def delete_prompt(prompt_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM prompt_runs WHERE prompt_id = ?", (prompt_id,))
    conn.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
    conn.commit()
    conn.close()


# ── Runs ──────────────────────────────────────────────────────────────────────

def save_run(prompt_id: int, input_vars: dict, output: str, model: str, latency_ms: int) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO prompt_runs (prompt_id, input_vars, output, model, latency_ms) VALUES (?, ?, ?, ?, ?)",
        (prompt_id, json.dumps(input_vars), output, model, latency_ms),
    )
    conn.commit()
    run_id = cur.lastrowid
    conn.close()
    return run_id


def rate_run(run_id: int, rating: int):
    conn = get_connection()
    conn.execute("UPDATE prompt_runs SET rating = ? WHERE id = ?", (rating, run_id))
    conn.commit()
    conn.close()


def get_runs(prompt_id: int) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM prompt_runs WHERE prompt_id = ? ORDER BY ran_at DESC",
        (prompt_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_runs() -> list:
    conn = get_connection()
    rows = conn.execute(
        """SELECT r.*, p.name AS prompt_name, p.use_case
           FROM prompt_runs r
           JOIN prompts p ON r.prompt_id = p.id
           ORDER BY r.ran_at DESC LIMIT 100"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_variables(prompt_text: str) -> list[str]:
    """Find all {{variable}} placeholders in a prompt."""
    return list(dict.fromkeys(re.findall(r"\{\{(\w+)\}\}", prompt_text)))


def render_prompt(prompt_text: str, variables: dict) -> str:
    """Replace {{variable}} with provided values."""
    result = prompt_text
    for key, value in variables.items():
        result = result.replace(f"{{{{{key}}}}}", value)
    return result
