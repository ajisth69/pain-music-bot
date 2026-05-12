import time
from utils.fonts import bold_sans, bold_italic, smallcaps, mono, outline, circled


def format_time(seconds: int) -> str:
    """Return mm:ss or h:mm:ss string."""
    seconds = max(0, int(seconds))
    if seconds >= 3600:
        return time.strftime("%H:%M:%S", time.gmtime(seconds))
    return time.strftime("%M:%S", time.gmtime(seconds))


def quote_block(*lines: str) -> str:
    """Render lines as a Telegram blockquote in Markdown captions/messages."""
    return "\n".join(f"> {line}" if line else ">" for line in lines)


# ── Decorative separators ────────────────────────────────────────────────
THIN_LINE   = "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈"
GLOW_LINE   = "✦ ━━━━━━━━━━━━━━━━━━━━ ✦"
SPARK_LINE  = "╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌"
BRAND_LINE  = "─── ⋆⋅☆⋅⋆ ──────── ⋆⋅☆⋅⋆ ───"
FOOTER      = f"⚡ {bold_sans('PAIN !!')}  ▸  {smallcaps('LetMe Solo Her')} 🥀"
TOP_ACCENT  = "╔══════════════════════════╗"
BOT_ACCENT  = "╚══════════════════════════╝"


def create_progress_bar(played_seconds: int, total_seconds: int, length: int = 15) -> str:
    """
    Returns a compact animated-style progress bar:
      01:23 ▰▰▰▰▰▰▰▱▱▱▱▱▱▱▱ 04:00  ⟨ 47% ⟩
    """
    if total_seconds <= 0:
        return f"` 00:00 ` ▱{'▱' * (length - 1)} ` 00:00 `  ⟨ 0% ⟩"

    played_seconds = max(0, min(int(played_seconds), total_seconds))
    pct = played_seconds / total_seconds
    filled = int(length * pct)
    filled = max(0, min(filled, length))
    empty = length - filled

    bar = "▰" * filled + "▱" * empty
    pct_str = f"{int(pct * 100)}%"
    played_str = format_time(played_seconds)
    total_str = format_time(total_seconds)

    return f"` {played_str} ` {bar} ` {total_str} `  ⟨ **{pct_str}** ⟩"


def make_now_playing_caption(song: dict, bar: str) -> str:
    title     = song.get("title", "Unknown")
    artist    = song.get("artist", "Unknown")
    duration  = format_time(song.get("duration", 0))
    requester = song.get("requester", "Admin")

    details = quote_block(
        f"💿  **{title}**",
        f"🎤  `{artist}`",
        f"⏱  `{duration}`  ┃  👤  {requester}",
    )

    return (
        f"🎧  {bold_sans('NOW PLAYING')}\n"
        f"{GLOW_LINE}\n"
        f"\n"
        f"{details}\n"
        f"\n"
        f"{THIN_LINE}\n"
        f"{quote_block(bar)}\n"
        f"{THIN_LINE}\n"
        f"\n"
        f"{FOOTER}"
    )


def make_queued_caption(song: dict, position: int) -> str:
    title     = song.get("title", "Unknown")
    artist    = song.get("artist", "Unknown")
    duration  = format_time(song.get("duration", 0))
    requester = song.get("requester", "Admin")
    pos_label = bold_sans(f"#{position}")

    details = quote_block(
        f"💿  **{title}**",
        f"🎤  `{artist}`",
        f"⏱  `{duration}`  ┃  👤  {requester}",
    )

    return (
        f"📥  {bold_sans('ADDED TO QUEUE')}  {pos_label}\n"
        f"{GLOW_LINE}\n"
        f"\n"
        f"{details}\n"
        f"\n"
        f"{THIN_LINE}\n"
        f"{FOOTER}"
    )


def make_queue_list(now: dict | None, queue_items: list) -> str:
    """Builds the full /queue display with quote sections."""
    lines = [
        f"📋  {bold_sans('QUEUE')}",
        GLOW_LINE,
    ]

    if now:
        lines.append("")
        lines.append(quote_block(
            f"▶️  {bold_sans('Now Playing')}",
            f"💿  **{now['title']}**",
            f"🎤  {now.get('artist', '?')}  ·  `{format_time(now['duration'])}`",
        ))
        lines.append(THIN_LINE)

    if queue_items:
        lines.append(f"\n🔜  {bold_sans('Up Next')}")
        for i, s in enumerate(queue_items, 1):
            icon = "⬇️" if s.get("downloading") else ("✅" if s.get("file_path") else "🕐")
            num = circled(str(i))
            lines.append(quote_block(
                f"{num}.  {icon}  **{s['title']}**",
                f"🎤  {s.get('artist','?')}  ·  `{format_time(s.get('duration',0))}`",
            ))
    else:
        lines.append("")
        lines.append(quote_block("_Queue is empty — add songs with_ `/play`"))

    lines.append(f"\n{THIN_LINE}")
    lines.append(FOOTER)
    return "\n".join(lines)


def make_stopped_caption(user_mention: str) -> str:
    return (
        f"⏹  {bold_sans('STOPPED')}\n"
        f"{THIN_LINE}\n"
        f"{quote_block(f'Stopped by {user_mention}', '_Voice chat left._')}\n"
        f"{THIN_LINE}\n"
        f"{FOOTER}"
    )


def make_skipped_caption(user_mention: str) -> str:
    return (
        f"⏭  {bold_sans('SKIPPED')}\n"
        f"{THIN_LINE}\n"
        f"{quote_block(f'Skipped by {user_mention}')}\n"
        f"{THIN_LINE}\n"
        f"{FOOTER}"
    )


def make_track_finished_caption() -> str:
    return (
        f"✅  {bold_sans('TRACK FINISHED')}\n"
        f"{THIN_LINE}\n"
        f"{quote_block('_Playing next…_')}\n"
        f"{THIN_LINE}\n"
        f"{FOOTER}"
    )
