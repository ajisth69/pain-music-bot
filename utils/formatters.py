import time

def format_time(seconds):
    if seconds >= 3600:
        return time.strftime('%H:%M:%S', time.gmtime(seconds))
    return time.strftime('%M:%S', time.gmtime(seconds))

def create_progress_bar(played_seconds, total_seconds, length=20):
    if total_seconds == 0:
        return f"**00:00** 🔘{'—' * (length - 1)} **00:00**"
    percentage = played_seconds / total_seconds
    played_blocks = int(length * percentage)
    remaining_blocks = length - played_blocks - 1
    played_blocks = max(0, min(played_blocks, length - 1))
    remaining_blocks = max(0, min(remaining_blocks, length - 1))
    played_time_str = format_time(played_seconds)
    total_time_str = format_time(total_seconds)
    bar = "▬" * played_blocks + "🔘" + "─" * remaining_blocks
    return f"**{played_time_str}** ▕{bar}▏ **{total_time_str}**"
