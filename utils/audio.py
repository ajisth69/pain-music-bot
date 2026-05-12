import asyncio
import os

from pytgcalls.types import MediaStream


MAX_PRECONVERT_SECONDS = 12 * 60


def should_stream_direct(duration: int | None) -> bool:
    return bool(duration and duration > MAX_PRECONVERT_SECONDS)


def is_remote_source(source: str | None) -> bool:
    return isinstance(source, str) and source.startswith(("http://", "https://"))


def is_ready_audio_source(source: str | None) -> bool:
    if is_remote_source(source):
        return True
    return bool(source and os.path.exists(source) and os.path.getsize(source) > 0)


def make_audio_stream(source: str) -> MediaStream:
    return MediaStream(source, video_flags=MediaStream.Flags.IGNORE)


async def prepare_audio(file_path: str, duration: int | None = None) -> str:
    """Pre-convert short tracks to WAV, but keep long mixes compressed."""
    if file_path.lower().endswith(".wav"):
        return file_path
    if duration and duration > MAX_PRECONVERT_SECONDS:
        print(f"[audio] Skipping WAV pre-convert for long track ({duration}s): {file_path}")
        return file_path

    wav_path = os.path.splitext(file_path)[0] + ".wav"
    try:
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "error",
            "-nostdin",
            "-y",
            "-threads", "2",
            "-i", file_path,
            "-vn",
            "-map", "0:a:0",
            "-acodec", "pcm_s16le",
            "-ar", "48000",
            "-ac", "2",
            wav_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode == 0 and os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
            os.remove(file_path)
            return wav_path
        if os.path.exists(wav_path):
            os.remove(wav_path)
        if stderr:
            print(f"[audio] FFmpeg failed: {stderr.decode(errors='ignore').strip()}")
    except Exception as e:
        if os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except Exception:
                pass
        print(f"[audio] FFmpeg failed: {e}")

    return file_path
