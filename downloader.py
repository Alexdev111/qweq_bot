from pathlib import Path
import yt_dlp
from app.config import DOWNLOAD_DIR

# Ensure download directory exists
DOWNLOAD_DIR = Path(DOWNLOAD_DIR)
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def download_video(job: dict) -> str:
    """
    Downloads video using yt-dlp and returns BASE file path (without extension)
    """

    url = job["url"]
    fmt = job.get("format", "mp4")
    quality = job.get("quality", "720")

    file_id = job.get("id")

    # Base output path (NO extension here, yt-dlp will append it)
    out_path = DOWNLOAD_DIR / file_id

    ydl_opts = {
        # Best mp4 + audio merge
        "format": f"bv*[height<={quality}]+ba/best[height<={quality}]",

        # Output template
        "outtmpl": str(out_path) + ".%(ext)s",

        # Merge to mp4
        "merge_output_format": "mp4",

        # Performance tuning
        "concurrent_fragment_downloads": 4,
        "retries": 10,
        "fragment_retries": 10,
        "noplaylist": True,

        # Stability
        "quiet": True,
        "no_warnings": True,
    }

    # Run download
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Return BASE path (without extension)
    return str(out_path)