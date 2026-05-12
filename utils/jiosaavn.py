import asyncio
import time
from urllib.parse import quote_plus

import aiohttp

from config import JIOSAAVN_API_PRIMARY, JIOSAAVN_API_SECONDARY, IMG_DEFAULT


# Persistent session: reused across requests to avoid TCP handshake overhead.
_session: aiohttp.ClientSession | None = None
_REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=30, sock_connect=8, sock_read=20)
_CACHE_TTL_SECONDS = 300
_SECONDARY_FALLBACK_DELAY = 1.2
_QUALITY_ORDER = ("96kbps", "160kbps", "320kbps", "48kbps", "12kbps")
_song_cache = {}
_artist_cache = {}


def _get_session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        connector = aiohttp.TCPConnector(limit=50, limit_per_host=20, ttl_dns_cache=300)
        _session = aiohttp.ClientSession(timeout=_REQUEST_TIMEOUT, connector=connector)
    return _session


def _cache_get(cache, key):
    cached = cache.get(key)
    if not cached:
        return None
    expires_at, value = cached
    if expires_at <= time.monotonic():
        cache.pop(key, None)
        return None
    if isinstance(value, list):
        return [dict(item) for item in value]
    return dict(value)


def _cache_set(cache, key, value):
    cache[key] = (time.monotonic() + _CACHE_TTL_SECONDS, value)


def _pick_audio_url(audio_urls):
    if not audio_urls:
        return None
    quality_map = {item.get("quality"): item.get("url") for item in audio_urls}
    for quality in _QUALITY_ORDER:
        if quality_map.get(quality):
            return quality_map[quality]
    return audio_urls[-1].get("url")


def _parse_song(song):
    audio_url = _pick_audio_url(song.get("downloadUrl", []))
    if not audio_url:
        return None

    images = song.get("image", [])
    image_url = images[-1].get("url") if images else IMG_DEFAULT

    artists_data = song.get("artists", {})
    primary_artists = artists_data.get("primary", [])
    if primary_artists:
        artist = primary_artists[0].get("name", "Unknown Artist")
    else:
        artist = song.get("singers", "Unknown Artist")

    return {
        "title": song.get("name", "Unknown Title"),
        "artist": artist,
        "audio_url": audio_url,
        "thumbnail": image_url,
        "duration": int(song.get("duration", 0)),
    }


async def fetch_song_from_api(session, api_url):
    try:
        async with session.get(api_url) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            results = data.get("data", {}).get("results", []) if data else []
            if results:
                return _parse_song(results[0])
    except Exception as e:
        print(f"API Fetch Error ({api_url}): {e}")
    return None


async def fetch_song(query):
    cache_key = query.strip().lower()
    cached = _cache_get(_song_cache, cache_key)
    if cached:
        return cached

    session = _get_session()
    encoded_query = quote_plus(query)
    primary_task = asyncio.create_task(
        fetch_song_from_api(session, f"{JIOSAAVN_API_PRIMARY}{encoded_query}")
    )

    try:
        result = await asyncio.wait_for(asyncio.shield(primary_task), _SECONDARY_FALLBACK_DELAY)
        if result:
            _cache_set(_song_cache, cache_key, result)
            return dict(result)
    except asyncio.TimeoutError:
        pass

    secondary_task = asyncio.create_task(
        fetch_song_from_api(session, f"{JIOSAAVN_API_SECONDARY}{encoded_query}")
    )

    if primary_task.done():
        result = primary_task.result()
        if result:
            _cache_set(_song_cache, cache_key, result)
            return dict(result)

    pending = {task for task in (primary_task, secondary_task) if not task.done()}

    while pending:
        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            result = task.result()
            if result:
                for pending_task in pending:
                    pending_task.cancel()
                _cache_set(_song_cache, cache_key, result)
                return dict(result)

    for task in (primary_task, secondary_task):
        if task.done():
            result = task.result()
            if result:
                _cache_set(_song_cache, cache_key, result)
                return dict(result)

    print("Both JioSaavn APIs failed.")
    return None


async def _fetch_artist_songs_from_api(session, api_url, limit):
    try:
        async with session.get(api_url) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            results = data.get("data", {}).get("results", []) if data else []
            songs = []
            seen_titles = set()

            for song in results:
                if len(songs) >= limit:
                    break

                title = song.get("name", "Unknown Title")
                title_key = title.lower()
                if title_key in seen_titles:
                    continue
                seen_titles.add(title_key)

                parsed = _parse_song(song)
                if parsed:
                    songs.append(parsed)
            return songs
    except Exception as e:
        print(f"[jiosaavn] fetch_artist_songs error: {e}")
    return []


async def fetch_artist_songs(query, limit=5):
    cache_key = (query.strip().lower(), limit)
    cached = _cache_get(_artist_cache, cache_key)
    if cached:
        return cached

    session = _get_session()
    encoded_query = quote_plus(query)
    songs = await _fetch_artist_songs_from_api(
        session, f"{JIOSAAVN_API_PRIMARY}{encoded_query}", limit
    )
    if not songs:
        songs = await _fetch_artist_songs_from_api(
            session, f"{JIOSAAVN_API_SECONDARY}{encoded_query}", limit
        )
    _cache_set(_artist_cache, cache_key, songs)
    return [dict(song) for song in songs]


async def download_file(url: str, file_path: str, chunk_size: int = 1024 * 1024) -> bool:
    """Stream-download url to file_path in chunks to avoid buffering the whole file."""
    session = _get_session()
    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                return False
            with open(file_path, "wb") as f:
                async for chunk in resp.content.iter_chunked(chunk_size):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"[jiosaavn] download_file error: {e}")
        return False
