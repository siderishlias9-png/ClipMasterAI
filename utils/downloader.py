import os
import yt_dlp


def download_video(url, out_dir="downloads"):
    os.makedirs(out_dir, exist_ok=True)
    opts = {
        "format": "mp4/bestvideo+bestaudio",
        "outtmpl": f"{out_dir}/%(title).80s.%(ext)s",
        "quiet": True,
        "merge_output_format": "mp4",
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)