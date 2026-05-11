import asyncio
import os


_CONVERT_LOCK = asyncio.Lock()


async def prepare_audio(file_path: str) -> str:
    """Pre-convert audio to 48 kHz stereo PCM WAV for smoother voice streaming."""
    if file_path.lower().endswith(".wav"):
        return file_path

    wav_path = os.path.splitext(file_path)[0] + ".wav"
    try:
        async with _CONVERT_LOCK:
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-nostdin",
                "-y",
                "-i",
                file_path,
                "-vn",
                "-map",
                "0:a:0",
                "-acodec",
                "pcm_s16le",
                "-ar",
                "48000",
                "-ac",
                "2",
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
