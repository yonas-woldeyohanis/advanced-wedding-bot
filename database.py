import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

# Initialize MongoDB Client
client = AsyncIOMotorClient(MONGO_URL)
db = client['wedding_bot_db']

# Collections
users_collection = db['users']
wishes_collection = db['wishes']

# --- USER FUNCTIONS ---

async def add_user(user_id, full_name, username):
    """Saves a new user to the database or updates existing one."""
    user_data = {
        "_id": user_id,
        "full_name": full_name,
        "username": username,
        "remind_me": False  # Default to false
    }
    # upsert=True means: If user exists, update. If not, create.
    await users_collection.update_one({"_id": user_id}, {"$set": user_data}, upsert=True)

async def toggle_reminder(user_id, status: bool):
    """Sets whether the user wants to receive reminders."""
    await users_collection.update_one({"_id": user_id}, {"$set": {"remind_me": status}})

async def get_all_users():
    """Returns a list of all user IDs (useful for Admin Broadcasts)."""
    cursor = users_collection.find({}, {"_id": 1})
    users = await cursor.to_list(length=10000)
    return [u["_id"] for u in users]

# --- WISHES (GUESTBOOK) FUNCTIONS ---

async def save_wish(user_id, full_name, message_text):
    """Saves a guestbook message."""
    wish_data = {
        "user_id": user_id,
        "full_name": full_name,
        "message": message_text,
        "timestamp": os.urandom(4).hex() # Simple way to add unique ID or use datetime
    }
    await wishes_collection.insert_one(wish_data)

async def get_all_wishes():
    """Returns a list of all guestbook messages."""
    cursor = wishes_collection.find({})
    return await cursor.to_list(length=1000)

