from pymongo import MongoClient
from datetime import datetime, timedelta
from Menfess.config import MONGO_DB_URL

client = MongoClient(MONGO_DB_URL)
db = client["menfess"]

limits = db.limits
messages = db.messages
settings = db.settings
hashtags = db.hashtags
delete_queue = db.delete_queue
banned_words = db.banned_words

def queue_deletion(chat_id, message_id, delete_at):
    delete_queue.insert_one({
        "chat_id": chat_id,
        "message_id": message_id,
        "delete_at": delete_at
    })

def get_expired_messages():
    now = datetime.utcnow()
    return list(delete_queue.find({"delete_at": {"$lte": now}}))

def remove_from_queue(chat_id, message_id):
    delete_queue.delete_one({"chat_id": chat_id, "message_id": message_id})
    
def add_banned_word(word: str):
    word = word.lower().strip()
    banned_words.update_one({"word": word}, {"$set": {"word": word}}, upsert=True)

def remove_banned_word(word: str):
    word = word.lower().strip()
    banned_words.delete_one({"word": word})

def get_banned_words():
    return [doc["word"] for doc in banned_words.find()]
    
def get_all_hashtags():
    return [tag["tag"] for tag in hashtags.find()]

def add_hashtag(tag: str):
    tag = tag.lower()
    if not tag.startswith("#"):
        tag = f"#{tag}"
    hashtags.update_one({"tag": tag}, {"$set": {"tag": tag}}, upsert=True)

def remove_hashtag(tag: str):
    tag = tag.lower()
    if not tag.startswith("#"):
        tag = f"#{tag}"
    hashtags.delete_one({"tag": tag})
    
def add_user_limit(user_id: int, amount: int):
    today = get_today_date()
    limits.update_one(
        {"user_id": user_id, "date": today},
        {"$inc": {"count": amount}},
        upsert=True
    )
    
def get_today_date():
    wib_time = datetime.utcnow() + timedelta(hours=7)
    return wib_time.strftime("%Y-%m-%d")

def get_user_limit(user_id):
    today = get_today_date()
    data = limits.find_one({"user_id": user_id, "date": today})
    return data["count"] if data else 0

def get_bonus_limit(user_id):
    today = get_today_date()
    data = limits.find_one({"user_id": user_id, "date": today})
    if not data:
        return 0
    base = data.get("count", 0)
    default = int(get_daily_limit())  # ✅ ubah di sini agar string jadi integer
    return max(0, base - default)
    
def increment_user_limit(user_id):
    today = get_today_date()
    limits.update_one(
        {"user_id": user_id, "date": today},
        {"$inc": {"count": 1}},
        upsert=True
    )

def set_target_channel(chat_id: int):
    settings.update_one(
        {"_id": "target_channel"},
        {"$set": {"chat_id": chat_id}},
        upsert=True
    )

def get_target_channel():
    data = settings.find_one({"_id": "target_channel"})
    return data["chat_id"] if data else None

def set_daily_limit(limit: int):
    settings.update_one(
        {"_id": "daily_limit"},
        {"$set": {"limit": limit}},
        upsert=True
    )

def get_daily_limit():
    data = settings.find_one({"_id": "daily_limit"})
    try:
        return int(data["limit"]) if data else 3
    except (ValueError, TypeError):
        return 3
        
def reset_user_count(user_id):
    today = get_today_date()
    limits.update_one(
        {"user_id": user_id, "date": today},
        {"$set": {"count": 0}},
        upsert=True
    )
