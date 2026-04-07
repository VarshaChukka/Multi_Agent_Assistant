import sqlite3
from pathlib import Path
from typing import Dict, List


DB_PATH = Path(__file__).resolve().parents[2] / "app.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _get_conn() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS tasks ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "description TEXT NOT NULL, "
            "completed BOOLEAN NOT NULL DEFAULT 0"
            ")"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS events ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "description TEXT NOT NULL, "
            "completed BOOLEAN NOT NULL DEFAULT 0"
            ")"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS notes ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "content TEXT NOT NULL"
            ")"
        )

        columns = conn.execute("PRAGMA table_info(events)").fetchall()
        column_names = {column[1] for column in columns}
        if "completed" not in column_names:
            conn.execute("ALTER TABLE events ADD COLUMN completed BOOLEAN NOT NULL DEFAULT 0")


def insert_task(description: str) -> Dict:
    with _get_conn() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (description, completed) VALUES (?, 0)",
            (description,),
        )
        task_id = cursor.lastrowid
    return {"id": task_id, "description": description, "completed": False}


def get_tasks() -> List[Dict]:
    with _get_conn() as conn:
        rows = conn.execute("SELECT id, description, completed FROM tasks").fetchall()
    return [
        {
            "id": row["id"],
            "description": row["description"],
            "completed": bool(row["completed"]),
        }
        for row in rows
    ]


def update_task(task_id: int, completed: bool) -> Dict | None:
    with _get_conn() as conn:
        cursor = conn.execute(
            "UPDATE tasks SET completed = ? WHERE id = ?",
            (1 if completed else 0, task_id),
        )
        if cursor.rowcount == 0:
            return None
        row = conn.execute(
            "SELECT id, description, completed FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
    if row is None:
        return None
    return {
        "id": row["id"],
        "description": row["description"],
        "completed": bool(row["completed"]),
    }


def delete_completed_tasks() -> int:
    with _get_conn() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE completed = 1")
        removed = cursor.rowcount
    return removed


def delete_tasks(task_ids: List[int]) -> List[int]:
    if not task_ids:
        return []
    placeholders = ",".join("?" for _ in task_ids)
    with _get_conn() as conn:
        rows = conn.execute(
            f"SELECT id FROM tasks WHERE id IN ({placeholders})",
            task_ids,
        ).fetchall()
        existing = [row["id"] for row in rows]
        if existing:
            conn.execute(
                f"DELETE FROM tasks WHERE id IN ({placeholders})",
                task_ids,
            )
    return existing


def insert_event(description: str) -> Dict:
    with _get_conn() as conn:
        cursor = conn.execute(
            "INSERT INTO events (description, completed) VALUES (?, 0)",
            (description,),
        )
        event_id = cursor.lastrowid
    return {"id": event_id, "description": description, "completed": False}


def get_events() -> List[Dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT id, description, completed FROM events"
        ).fetchall()
    return [
        {
            "id": row["id"],
            "description": row["description"],
            "completed": bool(row["completed"]),
        }
        for row in rows
    ]


def update_event(event_id: int, completed: bool) -> Dict | None:
    with _get_conn() as conn:
        cursor = conn.execute(
            "UPDATE events SET completed = ? WHERE id = ?",
            (1 if completed else 0, event_id),
        )
        if cursor.rowcount == 0:
            return None
        row = conn.execute(
            "SELECT id, description, completed FROM events WHERE id = ?",
            (event_id,),
        ).fetchone()
    if row is None:
        return None
    return {
        "id": row["id"],
        "description": row["description"],
        "completed": bool(row["completed"]),
    }


def delete_event(event_id: int) -> bool:
    with _get_conn() as conn:
        cursor = conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
        return cursor.rowcount > 0


def delete_events(event_ids: List[int]) -> List[int]:
    if not event_ids:
        return []
    placeholders = ",".join("?" for _ in event_ids)
    with _get_conn() as conn:
        rows = conn.execute(
            f"SELECT id FROM events WHERE id IN ({placeholders})",
            event_ids,
        ).fetchall()
        existing = [row["id"] for row in rows]
        if existing:
            conn.execute(
                f"DELETE FROM events WHERE id IN ({placeholders})",
                event_ids,
            )
    return existing


def insert_note(content: str) -> Dict:
    with _get_conn() as conn:
        cursor = conn.execute(
            "INSERT INTO notes (content) VALUES (?)",
            (content,),
        )
        note_id = cursor.lastrowid
    return {"id": note_id, "content": content}


def get_notes() -> List[Dict]:
    with _get_conn() as conn:
        rows = conn.execute("SELECT id, content FROM notes").fetchall()
    return [{"id": row["id"], "content": row["content"]} for row in rows]


def delete_notes(note_ids: List[int]) -> List[int]:
    if not note_ids:
        return []
    placeholders = ",".join("?" for _ in note_ids)
    with _get_conn() as conn:
        rows = conn.execute(
            f"SELECT id FROM notes WHERE id IN ({placeholders})",
            note_ids,
        ).fetchall()
        existing = [row["id"] for row in rows]
        if existing:
            conn.execute(
                f"DELETE FROM notes WHERE id IN ({placeholders})",
                note_ids,
            )
    return existing
