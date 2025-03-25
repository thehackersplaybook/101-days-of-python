import streamlit as st
import yt_dlp
import os

# Constants
PAGE_TITLE = "Youtube to MP3 Converter"
PAGE_ICON = "🎵"
LAYOUT = "wide"
OUTPUT_DIR = "./output"
FFMPEG_PATH = "C:/ffmpeg/bin/ffmpeg.exe"  # Update this to your actual ffmpeg path

YDLP_OPTS = {
    "format": "bestaudio/best",
    "ffmpeg_location": FFMPEG_PATH,  # Ensuring yt-dlp finds ffmpeg
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
    "outtmpl": f"{OUTPUT_DIR}/%(title)s.%(ext)s",
}
def setup_streamlit_app() -> None:
    """
    Sets up the Streamlit app.
    """
    st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT)
    st.title(f"▶️ {PAGE_TITLE}")

    video_url: str = st.text_input("🔗 Enter Youtube URL:")

    if st.button("🎵 Convert to MP3"):
        convert_to_mp3(video_url)

    if st.session_state.get('converted'):
        provide_download_link(st.session_state['converted'])

def convert_to_mp3(video_url: str) -> None:
    """
    Downloads and converts a YouTube video to MP3.
    """
    if not video_url:
        st.error("❌ Please enter a valid YouTube URL.")
        return

    st.write("⏳ Converting...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        with yt_dlp.YoutubeDL(YDLP_OPTS) as ydl:
            info = ydl.extract_info(video_url, download=True)
            output_file = f"{OUTPUT_DIR}/{info['title']}.mp3"
            st.session_state['converted'] = output_file
            st.success("✅ Converted! You can download the MP3 now.")
    except yt_dlp.utils.DownloadError as e:
        st.error(f"⚠️ Download error: {e}")
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {e}")

def provide_download_link(file_path: str) -> None:
    """
    Provides a download button for the converted MP3 file and removes it after download.
    """
    with open(file_path, 'rb') as file:
        st.download_button("📥 Download MP3", file, file_name=os.path.basename(file_path), mime="audio/mp3")
    
    os.remove(file_path)
    st.session_state['converted'] = None

if __name__ == "__main__":
    setup_streamlit_app()
