import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "sessions.db")

async def init_session_db():
    """
    Initializes the SQLite database for storing conversational session data.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            '''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                history TEXT
            )
            '''
        )
        await db.commit()

async def get_session_history(session_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT history FROM sessions WHERE session_id = ?', (session_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
            return None

async def save_session_history(session_id: str, history: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            '''
            INSERT INTO sessions (session_id, history) 
            VALUES (?, ?) 
            ON CONFLICT(session_id) DO UPDATE SET history=excluded.history
            ''',
            (session_id, history)
        )
        await db.commit()
