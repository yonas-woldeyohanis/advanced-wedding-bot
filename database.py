import aiosqlite
import os

DB_PATH = "wedding.db"

async def init_db():
    """Creates the tables if they don't exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                username TEXT,
                remind_me INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS wishes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                full_name TEXT,
                wish_text TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def add_user(user_id, full_name, username):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users (user_id, full_name, username) VALUES (?, ?, ?)",
            (user_id, full_name, username)
        )
        await db.commit()

async def toggle_reminder(user_id, status: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET remind_me = ? WHERE user_id = ?", (status, user_id))
        await db.commit()

async def save_wish(user_id, full_name, wish_text):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO wishes (user_id, full_name, wish_text) VALUES (?, ?, ?)",
            (user_id, full_name, wish_text)
        )
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
        

async def get_all_wishes():
    """Returns all wishes from the database for the report."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT full_name, wish_text, timestamp FROM wishes") as cursor:
            return await cursor.fetchall()


async def count_users():
    """Returns the total number of users in the database."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0



async def get_detailed_users():
    """Returns all users with their IDs and Names for the list command."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id, full_name, username FROM users") as cursor:
            return await cursor.fetchall()