import os
import asyncio
import time
from utils.audio import is_ready_audio_source, prepare_audio, should_stream_direct
from utils.jiosaavn import download_file

queued_songs = {}
playing_chats = {}
updater_tasks = {}
download_tasks = {} # chat_id -> list of tasks

MAX_QUEUE_SIZE = 20
MAX_DOWNLOADS = 5
DOWNLOAD_WAIT_TIMEOUT = 60

def add_to_queue(chat_id, song_data):
    if chat_id not in queued_songs:
        queued_songs[chat_id] = []
    if len(queued_songs[chat_id]) >= MAX_QUEUE_SIZE:
        return False
    direct_stream = should_stream_direct(song_data.get("duration"))
    song_data["downloading"] = False
    song_data["file_path"] = song_data.get("audio_url") if direct_stream else None
    song_data["download_task"] = None
    song_data["direct_stream"] = direct_stream
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
            task = song.get("download_task")
            if task and not task.done():
                task.cancel()
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting file in queue cleanup: {e}")
        queued_songs.pop(chat_id, None)

async def _download_song(chat_id, song_data):
    if should_stream_direct(song_data.get("duration")):
        song_data["file_path"] = song_data.get("audio_url")
        song_data["direct_stream"] = True
        return

    song_data["downloading"] = True
    file_path = f"downloads/{chat_id}_{int(time.time())}_{id(song_data)}.mp3"
    os.makedirs("downloads", exist_ok=True)
    
    try:
        downloaded = await download_file(song_data["audio_url"], file_path)
        if downloaded:
            file_path = await prepare_audio(file_path, song_data.get("duration"))
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
        if song_data.get("download_task") is asyncio.current_task():
            song_data["download_task"] = None

async def wait_for_song_file(song_data, timeout=DOWNLOAD_WAIT_TIMEOUT):
    file_path = song_data.get("file_path")
    if is_ready_audio_source(file_path):
        return file_path

    task = song_data.get("download_task")
    if task and not task.done():
        try:
            await asyncio.wait_for(asyncio.shield(task), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    file_path = song_data.get("file_path")
    if is_ready_audio_source(file_path):
        return file_path
    return None

async def resolve_song_file(chat_id, song_data):
    if should_stream_direct(song_data.get("duration")):
        source = song_data.get("audio_url")
        if not source:
            raise Exception(f"Audio URL missing: {song_data['title']}")
        song_data["file_path"] = source
        song_data["direct_stream"] = True
        return source

    file_path = song_data.get("file_path")
    if is_ready_audio_source(file_path):
        return file_path

    if song_data.get("download_task") or song_data.get("downloading"):
        file_path = await wait_for_song_file(song_data)
        if not file_path:
            raise Exception(f"Download timed out: {song_data['title']}")
        return file_path

    file_path = f"downloads/{chat_id}_{int(time.time())}_{id(song_data)}.mp3"
    os.makedirs("downloads", exist_ok=True)
    if not await download_file(song_data["audio_url"], file_path):
        raise Exception(f"Download failed: {song_data['title']}")
    return await prepare_audio(file_path, song_data.get("duration"))

def _remove_download_task(chat_id, task):
    tasks = download_tasks.get(chat_id)
    if not tasks:
        return
    try:
        tasks.remove(task)
    except ValueError:
        pass
    if not tasks:
        download_tasks.pop(chat_id, None)

def process_queue_downloads(chat_id):
    if chat_id not in queued_songs:
        return

    download_tasks[chat_id] = [task for task in download_tasks.get(chat_id, []) if not task.done()]
    downloaded_count = sum(
        1
        for song in queued_songs[chat_id]
        if is_ready_audio_source(song.get("file_path")) or song.get("downloading") or song.get("download_task")
    )
    
    while downloaded_count < MAX_DOWNLOADS:
        next_to_download = None
        for song in queued_songs[chat_id]:
            if (
                not is_ready_audio_source(song.get("file_path"))
                and not song.get("downloading")
                and not song.get("download_task")
            ):
                next_to_download = song
                break
                
        if not next_to_download:
            break
            
        task = asyncio.create_task(_download_song(chat_id, next_to_download))
        next_to_download["download_task"] = task
        download_tasks[chat_id].append(task)
        task.add_done_callback(lambda done_task, cid=chat_id: _remove_download_task(cid, done_task))
        downloaded_count += 1
