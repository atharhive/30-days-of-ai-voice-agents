# services/tts.py
import requests
from typing import List, Dict, Any
from murf import Murf
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)

MURF_API_URL = "https://api.murf.ai/v1/speech"

# Ensure uploads folder exists
UPLOADS_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

def speak(text: str, api_key: str, output_file: str = "stream_output.wav"):
    """
    Convert text to speech using Murf API and save audio in uploads folder.
    """
    client = Murf(api_key=api_key)

    file_path = UPLOADS_DIR / output_file

    # Start with a clean file
    open(file_path, "wb").close()

    res = client.text_to_speech.stream(
        text=text,
        voice_id="en-US-ariana",  # Female voice - preferred cat-like sound
        style="Conversational"  # Natural and engaging style
    )

    audio_bytes = b""
    for audio_chunk in res:
        audio_bytes += audio_chunk
        with open(file_path, "ab") as f:
            f.write(audio_chunk)

    return audio_bytes