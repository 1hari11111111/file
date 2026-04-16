"""
Shortener Management Helper
CRUD operations for the shorteners collection.
Only one shortener can be active at a time.
"""
from database.database import shortener_col


async def add_shortener(name: str, api_url: str, api_key: str) -> dict:
    """
    Add or update a shortener. If a shortener with the same name exists,
    it is updated. Otherwise a new one is inserted (inactive by default).
    """
    if shortener_col.find_one({"name": name}):
        shortener_col.update_one(
            {"name": name},
            {"$set": {"api_url": api_url, "api_key": api_key}}
        )
        return {"ok": True, "action": "updated"}

    shortener_col.insert_one({
        "name": name,
        "api_url": api_url,
        "api_key": api_key,
        "active": False
    })
    return {"ok": True, "action": "added"}


async def set_active_shortener(name: str) -> dict:
    """Deactivate all shorteners, then activate the named one."""
    if not shortener_col.find_one({"name": name}):
        return {"ok": False, "error": "Shortener not found."}

    shortener_col.update_many({}, {"$set": {"active": False}})
    shortener_col.update_one({"name": name}, {"$set": {"active": True}})
    return {"ok": True}


async def remove_shortener(name: str) -> dict:
    """Delete a shortener by name."""
    result = shortener_col.delete_one({"name": name})
    if result.deleted_count:
        return {"ok": True}
    return {"ok": False, "error": "Shortener not found."}


async def list_shorteners() -> list:
    """Return all shorteners (without _id)."""
    return list(shortener_col.find({}, {"_id": 0}))


async def get_shortener_by_name(name: str) -> dict | None:
    return shortener_col.find_one({"name": name}, {"_id": 0})
