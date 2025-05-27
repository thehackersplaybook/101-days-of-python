import streamlit as st
import yt_dlp
import os
import re
from PIL import Image
from urllib.request import urlopen

# Constants
OUTPUT_DIR = "./downloads"
os.makedirs(OUTPUT_DIR, exist_ok=True)

st.set_page_config(page_title="YouTube Downloader", page_icon="📺", layout="wide")

# Sidebar UI
st.sidebar.title("📥 YouTube Downloader")
mode = st.sidebar.selectbox("Select download type:", ["🎵 Audio (MP3)", "🎬 Video (MP4)"])

resolution = "best"
if mode == "🎬 Video (MP4)":
    resolution = st.sidebar.selectbox("Select video resolution:", ["1080p", "720p", "480p", "360p", "240p", "144p"])

st.sidebar.markdown("---")

st.title("📺 YouTube to MP3 & MP4 Downloader")
st.markdown("Enter a YouTube URL and download high-quality audio or video.")

video_url = st.text_input("🔗 Paste YouTube Video URL:")

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def get_format_string(resolution):
    return f"bestvideo[height<={resolution.replace('p', '')}]+bestaudio/best"

def fetch_video_info(video_url):
    """
    Fetches video information from YouTube using yt-dlp.
    
    Args:
        video_url (str): The URL of the YouTube video.
    
    Returns:
        dict: A dictionary containing video information, or an empty dictionary if an error occurs.
    """
    with st.spinner("⏳ Fetching video info..."):
        try:
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(video_url, download=False)
                if "entries" in info:  # Handle playlists
                    info = info["entries"][0]
                return info
        except yt_dlp.utils.DownloadError as e:
            st.error(f"❌ Error fetching video info: {e}")
        except Exception as e:
            st.error(f"⚠️ Unexpected error: {e}")
    return {}  # Return an empty dictionary if fetching fails

def format_file_size(bytes_size):
    if bytes_size is None:
        return "Unknown"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def download(video_url, is_audio, resolution):
    """
    Downloads a YouTube video or audio with ffmpeg support.
    """
    info = fetch_video_info(video_url)

    title = sanitize_filename(info.get("title", "download"))
    ext = "mp3" if is_audio else "mp4"
    out_path = f"{OUTPUT_DIR}/{title}.%(ext)s"

    ydl_opts = {
        "format": "bestaudio/best" if is_audio else get_format_string(resolution),
        "outtmpl": out_path,
        "quiet": True,
        "merge_output_format": ext,
        "ffmpeg_location": r"D:\The Hackers Playbook\101-days-of-python\ffmpeg-2025-05-05-git-f4e72eb5a3-full_build\bin\ffmpeg.exe",  # Updated path
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }] if is_audio else []
    }

    with st.spinner("⏳ Downloading... Please wait"):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

    file_path = f"{OUTPUT_DIR}/{title}.{ext}"
    return file_path, f"{title}.{ext}", info

if st.button("⬇️ Start Download"):
    if not video_url.strip():
        st.warning("⚠️ Please enter a valid YouTube URL.")
    else:
        try:
            info = fetch_video_info(video_url)
            title = info.get("title", "Unknown")
            thumbnail_url = info.get("thumbnail", "")
            duration = info.get("duration", 0)
            filesize = format_file_size(info.get("filesize") or info.get("filesize_approx"))

            # Display preview
            cols = st.columns([1, 2])
            if thumbnail_url:
                image = Image.open(urlopen(thumbnail_url))
                cols[0].image(image, use_container_width=True)
            cols[1].markdown(f"### 📌 {title}")
            cols[1].markdown(f"⏱️ Duration: {duration // 60}:{duration % 60:02d} minutes")
            cols[1].markdown(f"💾 Estimated Size: {filesize}")

            # Start download
            file_path, filename, _ = download(video_url, is_audio=(mode == "🎵 Audio (MP3)"), resolution=resolution)

            st.success(f"✅ Download complete: `{filename}`")
            with open(file_path, "rb") as f:
                st.download_button(
                    label="📥 Click to Download",
                    data=f,
                    file_name=filename,
                    mime="audio/mpeg" if filename.endswith(".mp3") else "video/mp4"
                )
            os.remove(file_path)

        except yt_dlp.utils.DownloadError as e:
            st.error(f"❌ Download error: {e}")
        except Exception as e:
            st.error(f"⚠️ Unexpected error: {e}")
