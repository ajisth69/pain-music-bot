import time


def format_time(seconds: int) -> str:
    """Return mm:ss or h:mm:ss string."""
    seconds = max(0, int(seconds))
    if seconds >= 3600:
        return time.strftime("%H:%M:%S", time.gmtime(seconds))
    return time.strftime("%M:%S", time.gmtime(seconds))


def create_progress_bar(played_seconds: int, total_seconds: int, length: int = 17) -> str:
    """
    Returns a sleek progress bar line like:
      01:23 ━━━━━━━━●───────── 04:00  ·  34%
    """
    if total_seconds <= 0:
        return f"`00:00` ○{'─' * length} `00:00`  ·  0%"

    played_seconds = max(0, min(int(played_seconds), total_seconds))
    pct = played_seconds / total_seconds
    filled = int(length * pct)
    filled = max(0, min(filled, length - 1))
    empty = length - filled - 1

    bar = "━" * filled + "●" + "─" * empty
    pct_str = f"{int(pct * 100)}%"
    played_str = format_time(played_seconds)
    total_str = format_time(total_seconds)

    return f"`{played_str}` {bar} `{total_str}`  ·  **{pct_str}**"


def make_now_playing_caption(song: dict, bar: str) -> str:
    """
    Builds the full NOW PLAYING caption block used by all player messages.
    """
    title    = song.get("title", "Unknown")
    artist   = song.get("artist", "Unknown")
    duration = format_time(song.get("duration", 0))
    requester = song.get("requester", "Admin")

    return (
        f"🎵  **Now Playing**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"**🎼  {title}**\n"
        f"🎤  `{artist}`\n"
        f"⏱  `{duration}`    👤  {requester}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bar}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✦  **PAIN !!**  ·  _LᴇᴛMᴇ Sᴏʟᴏ Hᴇʀ_ 🥀"
    )


def make_queued_caption(song: dict, position: int) -> str:
    title    = song.get("title", "Unknown")
    artist   = song.get("artist", "Unknown")
    duration = format_time(song.get("duration", 0))
    requester = song.get("requester", "Admin")

    return (
        f"🎶  **Added to Queue**  `#{position}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"**🎼  {title}**\n"
        f"🎤  `{artist}`\n"
        f"⏱  `{duration}`    👤  {requester}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✦  **PAIN !!**  ·  _LᴇᴛMᴇ Sᴏʟᴏ Hᴇʀ_ 🥀"
    )
