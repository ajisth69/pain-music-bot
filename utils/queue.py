queued_songs = {}
playing_chats = {}
updater_tasks = {}

def add_to_queue(chat_id, song_data):
    if chat_id not in queued_songs:
        queued_songs[chat_id] = []
    queued_songs[chat_id].append(song_data)

def get_next(chat_id):
    if chat_id in queued_songs and len(queued_songs[chat_id]) > 0:
        return queued_songs[chat_id].pop(0)
    return None

def clear_queue(chat_id):
    queued_songs.pop(chat_id, None)
