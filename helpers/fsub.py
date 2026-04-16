"""
Multi Force Subscribe Helper
Handles up to 6 channels stored in MongoDB.
"""
from database.database import fsub_col

MAX_CHANNELS = 6


async def add_channel(chat_id: int, title: str) -> dict:
    """Add a channel to the fsub list. Returns status dict."""
    existing = list(fsub_col.find())
    if len(existing) >= MAX_CHANNELS:
        return {"ok": False, "error": f"Max {MAX_CHANNELS} channels allowed. Remove one first."}

    if fsub_col.find_one({"chat_id": chat_id}):
        return {"ok": False, "error": "Channel already in the list."}

    fsub_col.insert_one({"chat_id": chat_id, "title": title})
    return {"ok": True}


async def remove_channel(chat_id: int) -> dict:
    """Remove a channel from the fsub list."""
    result = fsub_col.delete_one({"chat_id": chat_id})
    if result.deleted_count:
        return {"ok": True}
    return {"ok": False, "error": "Channel not found."}


async def get_all_channels() -> list:
    """Return list of all fsub channel documents."""
    return list(fsub_col.find({}, {"_id": 0}))
