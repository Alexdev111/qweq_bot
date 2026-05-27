import yt_dlp
import uuid
from config import DOWNLOAD_DIR
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
            "format": f"bv*[height<={quality}]+ba/b",
            "outtmpl": str(out_path) + ".mp4",

            # SPEED BOOST
            "concurrent_fragment_downloads": 8,
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