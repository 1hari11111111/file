"""
Analytics Helper
Tracks file access events per user with premium flag.
"""
from datetime import datetime
from database.database import analytics_col, user_data, premium_col


async def save_click(user_id: int, file_id: int, is_premium: bool):
    """Record a file access event."""
    analytics_col.insert_one({
        "user_id": user_id,
        "file_id": file_id,
        "is_premium": is_premium,
        "time": datetime.utcnow()
    })


async def get_stats() -> dict:
    """Return aggregate analytics stats."""
    total_clicks = analytics_col.count_documents({})
    premium_clicks = analytics_col.count_documents({"is_premium": True})
    free_clicks = total_clicks - premium_clicks

    total_users = user_data.count_documents({})
    now = datetime.utcnow()
    active_premium = premium_col.count_documents({"expiry": {"$gt": now}})

    # Most accessed files (top 5)
    pipeline = [
        {"$group": {"_id": "$file_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    top_files = list(analytics_col.aggregate(pipeline))

    return {
        "total_clicks": total_clicks,
        "premium_clicks": premium_clicks,
        "free_clicks": free_clicks,
        "total_users": total_users,
        "active_premium_users": active_premium,
        "top_files": top_files
    }
