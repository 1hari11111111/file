"""
Premium Users Helper
Manages premium access with expiry-based checks.
"""
from datetime import datetime, timedelta
from database.database import premium_col


async def is_premium(user_id: int) -> bool:
    """Return True if user has a valid (non-expired) premium subscription."""
    doc = premium_col.find_one({"user_id": user_id})
    if not doc:
        return False
    if doc["expiry"] < datetime.utcnow():
        # Auto-clean expired entries
        premium_col.delete_one({"user_id": user_id})
        return False
    return True


async def add_premium(user_id: int, days: int) -> datetime:
    """
    Grant premium to a user for `days` days.
    If already premium, extends from current expiry.
    Returns the new expiry datetime.
    """
    existing = premium_col.find_one({"user_id": user_id})
    if existing and existing["expiry"] > datetime.utcnow():
        new_expiry = existing["expiry"] + timedelta(days=days)
    else:
        new_expiry = datetime.utcnow() + timedelta(days=days)

    premium_col.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, "expiry": new_expiry}},
        upsert=True
    )
    return new_expiry


async def remove_premium(user_id: int) -> bool:
    """Remove premium from a user. Returns True if removed, False if not found."""
    result = premium_col.delete_one({"user_id": user_id})
    return result.deleted_count > 0


async def get_premium_info(user_id: int) -> dict | None:
    """Return premium doc or None."""
    return premium_col.find_one({"user_id": user_id}, {"_id": 0})


async def list_premium_users() -> list:
    """Return all premium users with user_id and expiry."""
    now = datetime.utcnow()
    return [
        doc for doc in premium_col.find({}, {"_id": 0})
        if doc["expiry"] > now
    ]
