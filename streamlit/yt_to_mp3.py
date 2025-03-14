import streamlit as st
import yt_dlp
import os

# Set up Streamlit app
def setup_streamlit_app():
    st.set_page_config(page_title="Youtube to MP3 Converter", page_icon="🎵", layout="wide")
    st.title("▶️ Youtube to MP3 Converter")

    # Input for YouTube URL
    video_url = st.text_input("🔗 Enter Youtube URL:")

    if st.button("🎵 Convert to MP3"):
        st.write("⏳ Converting...")

        # Download settings
        output_dir = "downloads"
        os.makedirs(output_dir, exist_ok=True)  # Ensure the downloads folder exists

        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "outtmpl": f"{output_dir}/%(title)s.%(ext)s",  # Save with video title
        }

        # Download audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            output_file = f"{output_dir}/{info['title']}.mp3"

        # Confirm conversion
        st.session_state['converted'] = output_file
        st.success("✅ Converted! You can download the MP3 now.")

    # Show download button
    if st.session_state.get('converted'):
        with open(st.session_state['converted'], 'rb') as file:
            st.download_button("📥 Download MP3", file, file_name=os.path.basename(st.session_state['converted']), mime="audio/mp3")

        # Remove file after download
        os.remove(st.session_state['converted'])
        st.session_state['converted'] = None

if __name__ == "__main__":
    setup_streamlit_app()
