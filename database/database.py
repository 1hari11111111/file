import pymongo
from config import DB_URL, DB_NAME

dbclient = pymongo.MongoClient(DB_URL)
database = dbclient[DB_NAME]

user_data = database['users']
premium_col = database['premium_users']
fsub_col = database['fsub_channels']
shortener_col = database['shorteners']
analytics_col = database['analytics']


# ─── User Functions ────────────────────────────────────────────────────────────

async def present_user(user_id: int) -> bool:
    found = user_data.find_one({'_id': user_id})
    return bool(found)


async def add_user(user_id: int):
    user_data.insert_one({'_id': user_id})


async def full_userbase() -> list:
    return [doc['_id'] for doc in user_data.find()]


async def del_user(user_id: int):
    user_data.delete_one({'_id': user_id})
