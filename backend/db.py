import sqlite3

import config

DB_PATH = str(config.DB_PATH)


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(messages)")
    columns = {row[1] for row in cursor.fetchall()}
    if "user_id" not in columns:
        cursor.execute(
            "ALTER TABLE messages ADD COLUMN user_id TEXT DEFAULT ?",
            (config.DEFAULT_USER_ID,),
        )
    conn.commit()


def init_db() -> None:
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT '{config.DEFAULT_USER_ID}',
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_summary (
            user_id TEXT PRIMARY KEY,
            summary TEXT
        )
    """)

    conn.commit()
    _migrate(conn)
    conn.close()


def save_message(user_id: str, session_id: str, role: str, content: str) -> None:
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO messages (user_id, session_id, role, content)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, session_id, role, content),
    )
    conn.commit()
    conn.close()


def get_recent_messages(session_id: str, limit: int = config.RECENT_MESSAGES_LIMIT) -> list[sqlite3.Row]:
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT role, content
        FROM messages
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (session_id, limit),
    ).fetchall()
    conn.close()
    return list(reversed(rows))


def get_message_count(session_id: str) -> int:
    conn = get_conn()
    row = conn.execute(
        "SELECT COUNT(*) AS cnt FROM messages WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    conn.close()
    return row["cnt"]


def get_session_history_for_summary(
    session_id: str,
    limit: int = config.SUMMARY_HISTORY_LIMIT,
) -> str:
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT role, content
        FROM messages
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (session_id, limit),
    ).fetchall()
    conn.close()

    lines = [f"{row['role']}: {row['content']}" for row in reversed(rows)]
    return "\n".join(lines)


def get_summary(user_id: str) -> str:
    conn = get_conn()
    row = conn.execute(
        "SELECT summary FROM memory_summary WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    return row["summary"] if row and row["summary"] else ""


def update_summary(user_id: str, summary: str) -> None:
    conn = get_conn()
    conn.execute(
        """
        INSERT OR REPLACE INTO memory_summary (user_id, summary)
        VALUES (?, ?)
        """,
        (user_id, summary),
    )
    conn.commit()
    conn.close()


def get_recent_history(session_id: str | None = None, limit: int = 20) -> list[dict]:
    conn = get_conn()
    if session_id:
        rows = conn.execute(
            """
            SELECT role, content, created_at
            FROM messages
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT role, content, created_at
            FROM messages
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    conn.close()

    rows = list(reversed(rows))
    return [
        {
            "role": row["role"],
            "content": row["content"],
            "time": row["created_at"],
        }
        for row in rows
    ]
