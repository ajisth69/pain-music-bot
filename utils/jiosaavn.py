import aiohttp
from config import JIOSAAVN_API_PRIMARY, JIOSAAVN_API_SECONDARY, IMG_DEFAULT

async def fetch_song_from_api(session, api_url):
    try:
        async with session.get(api_url) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            if data and "data" in data and "results" in data["data"] and len(data["data"]["results"]) > 0:
                song = data["data"]["results"][0]
                audio_urls = song.get("downloadUrl", [])
                
                audio_url = None
                if audio_urls:
                    # Quality preference: 96kbps -> 160kbps -> 320kbps -> 48kbps -> 12kbps
                    quality_map = {q.get("quality"): q.get("url") for q in audio_urls}
                    for q_pref in ["96kbps", "160kbps", "320kbps", "48kbps", "12kbps"]:
                        if q_pref in quality_map:
                            audio_url = quality_map[q_pref]
                            break
                    if not audio_url:
                        audio_url = audio_urls[-1].get("url") if audio_urls else None
                images = song.get("image", [])
                image_url = images[-1].get("url") if images else IMG_DEFAULT
                
                # Try to get artist
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
                    "duration": int(song.get("duration", 0))
                }
    except Exception as e:
        print(f"API Fetch Error ({api_url}): {e}")
    return None

async def fetch_song(query):
    async with aiohttp.ClientSession() as session:
        result = await fetch_song_from_api(session, f"{JIOSAAVN_API_PRIMARY}{query}")
        if result:
            return result
            
        print("Primary API failed, falling back to secondary API...")
        result = await fetch_song_from_api(session, f"{JIOSAAVN_API_SECONDARY}{query}")
        return result

async def fetch_artist_songs(query, limit=5):
    # Fetch top 5 songs for the given artist query
    async with aiohttp.ClientSession() as session:
        url = f"{JIOSAAVN_API_PRIMARY}{query}"
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    songs = []
                    seen_titles = set()
                    if data and "data" in data and "results" in data["data"]:
                        for song in data["data"]["results"]:
                            if len(songs) >= limit:
                                break
                            
                            title = song.get("name", "Unknown Title")
                            # Prevent duplicates (like multiple remix versions of same song)
                            if title.lower() in seen_titles:
                                continue
                            seen_titles.add(title.lower())
                            
                            audio_urls = song.get("downloadUrl", [])
                            audio_url = None
                            if audio_urls:
                                # Quality preference: 96kbps -> 160kbps -> 320kbps -> 48kbps -> 12kbps
                                quality_map = {q.get("quality"): q.get("url") for q in audio_urls}
                                for q_pref in ["96kbps", "160kbps", "320kbps", "48kbps", "12kbps"]:
                                    if q_pref in quality_map:
                                        audio_url = quality_map[q_pref]
                                        break
                                if not audio_url:
                                    audio_url = audio_urls[-1].get("url") if audio_urls else None
                            
                            images = song.get("image", [])
                            image_url = images[-1].get("url") if images else IMG_DEFAULT
                            
                            artists_data = song.get("artists", {})
                            primary_artists = artists_data.get("primary", [])
                            if primary_artists:
                                artist = primary_artists[0].get("name", "Unknown Artist")
                            else:
                                artist = song.get("singers", "Unknown Artist")
                                
                            if audio_url:
                                songs.append({
                                    "title": song.get("name", "Unknown Title"),
                                    "artist": artist,
                                    "audio_url": audio_url,
                                    "thumbnail": image_url,
                                    "duration": int(song.get("duration", 0))
                                })
                    return songs
        except Exception:
            pass
        return []

async def download_file(url, file_path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.read()
                def write_file():
                    with open(file_path, 'wb') as f:
                        f.write(data)
                import asyncio
                await asyncio.to_thread(write_file)
                return True
    return False

