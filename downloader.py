import yt_dlp
import uuid
from app.config import DOWNLOAD_DIR
from pathlib import Path

Path(DOWNLOAD_DIR).mkdir(exist_ok=True)


async def download_video(job):
    url = job["url"]
    fmt = job["format"]
    quality = job["quality"]

    file_id = str(uuid.uuid4())
    out_path = Path(DOWNLOAD_DIR) / file_id

    if fmt == "mp4":
        ydl_opts = {
    "format": "bv*+ba/best",
    "merge_output_format": "mp4",

    "concurrent_fragment_downloads": 4,
    "http_chunk_size": 10 * 1024 * 1024,

    "retries": 10,
    "fragment_retries": 10,

    "noplaylist": True,
    "quiet": True,
}

    else:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(out_path) + ".mp3",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality,
            }],
            "quiet": True,
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return str(out_path)