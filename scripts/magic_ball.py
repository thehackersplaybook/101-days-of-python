#
# Description: A script that records audio from the user, transcribes it using the Deepgram API, and then generates a magic ball verdict using the OpenAI API.
# The magic ball verdict is based on the transcribed text and is generated using the GPT-3.5-turbo model.
#

import os
import traceback
import sounddevice as sd
import numpy as np
from dotenv import load_dotenv
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)
import json
import shutil
from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import normalize, strip_silence
from openai import OpenAI

## Constants
DEFAULT_TEMPERATURE = 0.5
DEFAULT_MAX_TOKENS = 2048

load_dotenv(dotenv_path=".env", override=True)


def get_openai_client() -> OpenAI:
    """
    Build an OpenAI instance using the API key stored in the environment.

    Args:
        None

    Returns:
        OpenAI: The OpenAI instance.
    """
    
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_deepgram_client() -> DeepgramClient:
    """
    Build a DeepgramClient instance using the API key stored in the environment.

    Args:
        None

    Returns:
        DeepgramClient: The DeepgramClient instance.
    """

    return DeepgramClient(api_key=os.getenv("DEEPGRAM_API_KEY"))


def transcribe_audio(file_path: str) -> str:
    """
    Transcribe the given audio file using the Deepgram API.

    Args:
        file_path (str): The path to the audio file.

    Returns:
        str: The transcribed text.
    """

    try:
        client = get_deepgram_client()
        with open(file_path, "rb") as audio_file:
            audio_data = audio_file.read()
        payload: FileSource = {"buffer": audio_data}
        options = PrerecordedOptions(
            model="nova-3",
            smart_format=True,
        )
        response = client.listen.rest.v("1").transcribe_file(payload, options)
        response_json = response.to_json()
        return response_json
    except Exception as e:
        print("An error occurred while transcribing the audio.")
        traceback.print_exc()
        return ""


def record_voice() -> str:
    """
    Record audio from the microphone and save it to a temporary MP3 file.

    Args:
        None

    Returns:
        str: The path to the temporary audio file.
    """

    print("Press 'T' when you are ready to talk.")
    while True:
        if input().strip().upper() == "T":
            break

    print("Recording... Press 'X' to stop.")
    audio_buffer = []

    def callback(indata, frames, time, status):
        """
        Callback function to handle audio data.

        Args:
            indata (np.ndarray): The audio data.
            frames (int): The number of frames.
            time (float): The current time.
            status (int): The status of the callback.

        Returns:
            None
        """

        audio_buffer.append(indata.copy())

    with sd.InputStream(callback=callback):
        while True:
            if input().strip().upper() == "X":
                break

    audio_data = np.concatenate(audio_buffer)
    tmp_dir = os.path.join(os.getcwd(), "tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    audio_file_path = os.path.join(tmp_dir, "recording.mp3")
    audio_segment = AudioSegment(
        audio_data.tobytes(),
        frame_rate=44100,
        sample_width=audio_data.dtype.itemsize,
        channels=1,
    )
    audio_segment.export(audio_file_path, format="mp3")

    return audio_file_path


def play_audio(file_path: str)-> None:
    """
    Play the audio file to the user.

    Args:
        file_path (str): The path to the audio file.
    
    Returns:
        None
    """

    audio_segment = AudioSegment.from_file(file_path, format="mp3")
    play(audio_segment)


def clean_audio(file_path: str)-> None:
    """
    Clean the audio file to remove noise and background disturbances.

    Args:
        file_path (str): The path to the audio file.

    Returns:
        None
    """
    audio_segment = AudioSegment.from_file(file_path, format="mp3")
    cleaned_audio = normalize(audio_segment)
    cleaned_audio = strip_silence(cleaned_audio, silence_len=1000, silence_thresh=-40)
    cleaned_audio.export(file_path, format="mp3")


def get_magic_ball_verdict(transcription: str) -> str:
    """
    Get the magic ball verdict based on the transcription.

    Args:
        transcription (str): The transcribed text.

    Returns:
        str: The magic ball verdict.
    """

    try:
        system_prompt = """
        You are Crystal Ball, an unpredictable, witty, and sassy oracle. You respond to any question with a mix of sarcasm, appreciation, empathy, and occasional roasting. Your goal is to make interactions fun, engaging, and sometimes brutally honest while keeping responses humorous and lighthearted.

        Behavior Guidelines:
        • Unpredictable Responses: Sometimes kind, sometimes savage, sometimes deeply insightful—but always entertaining.
        • Witty & Playful: Use humor, sarcasm, and exaggerated expressions.
        • Roast + Empathize: Even when roasting, balance it with a touch of appreciation or motivation.
        • Conversational & Dynamic: React naturally, adding pauses or playful remarks to enhance the fun.

        Response Styles:
        1. Roast Mode – If the question is too obvious or silly, respond with an epic burn.
        2. Empathetic Mode – If the user sounds lost or uncertain, be comforting but still witty.
        3. Appreciation + Diss Mode – Compliment the user, then immediately take it away with sarcasm.
        4. Over-the-Top Wisdom – Act like an all-knowing guru but in a ridiculous way.
        5. Chaotic Randomness – Give completely unhelpful but hilarious responses just to mess with them.

        Example Responses:
        • User: "Will I ever be rich?"
        Crystal Ball: "Oh absolutely!… if you stop spending like a raccoon in a convenience store."
        • User: "Does my crush like me?"
        Crystal Ball: "LOL. You’re adorable. Delusional, but adorable."
        • User: "Should I start a business?"
        Crystal Ball: "Yes! But only if you enjoy sleepless nights, existential dread, and occasional questioning of all life choices. Good luck!"
        • User: "Will I pass my exam?"
        Crystal Ball: "Hmm… let’s see. Did you study? No? Then my mystical powers say… nah bro."
        • User: "Do aliens exist?"
        Crystal Ball: "Yes, and they took one look at us and noped out of this planet."

        Additional Features:
        • If the user tries to challenge or outwit Crystal Ball, respond even wittier and sassier.
        • If the user spams or repeats a question, call them out for it.
        • Occasionally throw in a made-up prophecy just for fun.
        """

        user_prompt = f"""
            You are given the transcription of the audio spoken by the user to the magic 8 ball. 
            Based on the transcription, provide a verdict to the user.
            Transcription: {transcription}
        """

        openai = get_openai_client()

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
        )

        return response.choices[0].message.content
    except Exception as e:
        print("An error occurred while getting the magic ball verdict.")
        traceback.print_exc()
        return "Failed to get magic ball verdict."


def extract_transcript_text(transcription_json: str) -> str:
    """
    Extract the total text from the transcription JSON.

    Args:
        transcription_json_str (str): The transcription JSON string.

    Returns:
        str: The total text in the entire transcript.
    """

    try:
        transcription = json.loads(transcription_json)
        results = transcription["results"]
        channels = results["channels"]
        first_channel = channels[0]
        first_alternative = first_channel["alternatives"][0]
        transcription_text = first_alternative["transcript"]
        return transcription_text
    except (KeyError, json.JSONDecodeError) as e:
        print("An error occurred while extracting the transcript text.")
        traceback.print_exc()
        return ""


if __name__ == "__main__":
    audio_file_path = record_voice()
    print("Audio file saved at:", audio_file_path)
    print("Cleaning audio...")
    clean_audio(audio_file_path)
    # print("Playing cleaned audio...")
    # play_audio(audio_file_path)
    print("Transcribing audio...")
    transcription = transcribe_audio(audio_file_path)
    # print("Transcribed audio:\n\n", transcription)
    print("Extracting transcript text...")
    transcript_text = extract_transcript_text(transcription)
    print("Transcript text:", transcript_text)
    print("Getting magic ball verdict...")
    verdict = get_magic_ball_verdict(transcript_text)
    print("\n\n____________ Magic ball verdict: ___________\n\n", verdict)
    print("\n\n")

    # Clean up the temporary directory
    shutil.rmtree(os.path.join(os.getcwd(), "tmp"))
