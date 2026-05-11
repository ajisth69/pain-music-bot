import os
import asyncio
from utils.audio import prepare_audio
from utils.jiosaavn import download_file

queued_songs = {}
playing_chats = {}
updater_tasks = {}
download_tasks = {} # chat_id -> list of tasks

MAX_QUEUE_SIZE = 20
MAX_DOWNLOADS = 5

def add_to_queue(chat_id, song_data):
    if chat_id not in queued_songs:
        queued_songs[chat_id] = []
    if len(queued_songs[chat_id]) >= MAX_QUEUE_SIZE:
        return False
    song_data["downloading"] = False
    song_data["file_path"] = None
    queued_songs[chat_id].append(song_data)
    return True

def get_next(chat_id):
    if chat_id in queued_songs and len(queued_songs[chat_id]) > 0:
        return queued_songs[chat_id].pop(0)
    return None

def clear_queue(chat_id):
    # Cancel downloads
    if chat_id in download_tasks:
        for task in download_tasks[chat_id]:
            if not task.done():
                task.cancel()
        download_tasks.pop(chat_id, None)
        
    if chat_id in queued_songs:
        for song in queued_songs[chat_id]:
            file_path = song.get("file_path")
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting file in queue cleanup: {e}")
        queued_songs.pop(chat_id, None)

async def _download_song(chat_id, song_data):
    import time
    song_data["downloading"] = True
    file_path = f"downloads/{chat_id}_{int(time.time())}_{id(song_data)}.mp3"
    os.makedirs("downloads", exist_ok=True)
    
    try:
        downloaded = await download_file(song_data["audio_url"], file_path)
        if downloaded:
            file_path = await prepare_audio(file_path)
            song_data["file_path"] = file_path
    except asyncio.CancelledError:
        # Cleanup if cancelled
        if os.path.exists(file_path):
            os.remove(file_path)
        wav_path = file_path.replace(".mp3", ".wav")
        if os.path.exists(wav_path):
            os.remove(wav_path)
        raise
    except Exception as e:
        print(f"Download failed in background: {e}")
    finally:
        song_data["downloading"] = False

def process_queue_downloads(chat_id):
    if chat_id not in queued_songs:
        return
        
    downloaded_count = sum(1 for s in queued_songs[chat_id] if s.get("file_path") or s.get("downloading"))
    
    while downloaded_count < MAX_DOWNLOADS:
        next_to_download = None
        for song in queued_songs[chat_id]:
            if not song.get("file_path") and not song.get("downloading"):
                next_to_download = song
                break
                
        if not next_to_download:
            break
            
        task = asyncio.create_task(_download_song(chat_id, next_to_download))
        if chat_id not in download_tasks:
            download_tasks[chat_id] = []
        download_tasks[chat_id].append(task)
        downloaded_count += 1
