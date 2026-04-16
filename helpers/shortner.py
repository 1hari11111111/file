"""
URL Shortener Helper
Fetches the active shortener from DB and calls its API.
Supports response keys: shortenedUrl / short_url / result
Falls back to the original URL on any error.
"""
import aiohttp
from database.database import shortener_col


async def get_active_shortener() -> dict | None:
    """Return the active shortener config or None."""
    return shortener_col.find_one({"active": True}, {"_id": 0})


async def get_shortlink(original_url: str) -> str:
    """
    Shorten `original_url` using the active shortener.
    Returns the shortened URL, or `original_url` if anything fails.
    """
    try:
        shortener = await get_active_shortener()
        if not shortener:
            return original_url

        api_url = shortener["api_url"].rstrip("/")
        api_key = shortener["api_key"]

        # Build request URL – common pattern used by most shortener APIs
        request_url = f"{api_url}/api?api={api_key}&url={original_url}"

        async with aiohttp.ClientSession() as session:
            async with session.get(request_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return original_url
                data = await resp.json(content_type=None)

        # Try common response key patterns
        for key in ("shortenedUrl", "short_url", "result", "shortlink", "short"):
            if key in data and data[key]:
                return str(data[key])

        return original_url

    except Exception as e:
        print(f"[Shortener] Error: {e}")
        return original_url
