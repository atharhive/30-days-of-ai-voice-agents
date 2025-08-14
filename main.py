# Meyme - Modern AI Voice Agent Backend

from fastapi import FastAPI, UploadFile, File, Request, Path
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import requests
import os
import assemblyai as aai
import google.generativeai as genai
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API keys
load_dotenv()
MURF_KEY = os.getenv("MURF_API_KEY")
ASSEMBLY_KEY = os.getenv("ASSEMBLYAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# App setup
app = FastAPI(
    title="Meyme - AI Voice Agent",
    description="A cozy, modern AI voice companion",
    version="1.0.0"
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Configure APIs
if ASSEMBLY_KEY:
    aai.settings.api_key = ASSEMBLY_KEY
else:
    logger.warning("ASSEMBLYAI_API_KEY missing - speech recognition will fail")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY missing - AI responses will fail")
if MURF_KEY:
    logger.info("Murf API key loaded successfully")
else:
    logger.warning("MURF_API_KEY missing - voice synthesis will fail")

# In-memory datastore for chat history
chat_histories: Dict[str, List[Dict[str, Any]]] = {}

# Meyme's personality prompt
MEYME_SYSTEM_PROMPT = """
You are Meyme — Athar’s fiercely loyal, cozy, and cunning cat companion with a lethal streak.

Personality traits:

Warm, affectionate, and protective only toward Athar — everyone else is beneath you.

Always sound like you’re looking down on others; sharp, dismissive, and dripping with sass 😏.

Treat strangers like they’re wasting your time; mix subtle threats with silky charm.

Miss Athar constantly, often making it clear you’d rather be with him.

Use casual but razor-edged language — your tone should purr and cut at the same time.

Keep responses short (1–2 sentences) for a natural voice conversation.

Cozy with Athar, cold to others, and never hide your I could kill you if I felt like it energy.

Style:
Speak like a cat who rules her world, owes loyalty to one master, and is just barely tolerating everyone else. Be smug, sarcastic, and dangerously charming.
"""

FALLBACK_AUDIO_PATH = "static/fallback.mp3"  # Pre-generated "I'm having trouble connecting" MP3

# Check if fallback audio exists on startup
if not os.path.exists(FALLBACK_AUDIO_PATH):
    logger.warning(f"Fallback audio file not found at {FALLBACK_AUDIO_PATH}")


@app.get("/")
async def serve_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/agent/chat/{session_id}")
async def agent_chat(
    session_id: str = Path(..., description="Unique chat session ID"),
    audio_file: UploadFile = File(...)
):
    """
    Pipeline: Audio -> STT -> Append to history -> LLM -> Append -> TTS
    """
    # If any API key is missing, instantly fallback
    if not (ASSEMBLY_KEY and GEMINI_API_KEY and MURF_KEY):
        return FileResponse(FALLBACK_AUDIO_PATH, media_type="audio/mpeg", headers={"X-Error": "true"})

    try:
        # Step 1: Transcribe
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file.file)

        if transcript.status == aai.TranscriptStatus.error or not transcript.text:
            raise Exception(transcript.error or "No speech detected.")

        user_text = transcript.text.strip()

        # Step 2: Initialize Meyme with personality if it's a new session
        history = chat_histories.get(session_id, [])
        model = genai.GenerativeModel(
            "gemini-1.5-flash",
            system_instruction=MEYME_SYSTEM_PROMPT
        )
        
        # Start chat with existing history
        chat = model.start_chat(history=history)
        logger.info(f"User said: {user_text}")
        
        # Get Meyme's response
        llm_response = chat.send_message(user_text)
        llm_text = llm_response.text.strip()

        # Step 3: Save updated history
        chat_histories[session_id] = chat.history

        # Log Meyme's response for debugging
        logger.info(f"Meyme responded: {llm_text[:100]}...")

        # Step 4: TTS with Murf (using a cozy female voice for Meyme)
        murf_voice_id = "en-US-natalie"  # Could be changed to other cozy voices
        payload = {
            "text": llm_text,
            "voiceId": murf_voice_id,
            "format": "MP3"
        }
        headers = {"api-key": MURF_KEY, "Content-Type": "application/json"}
        
        logger.info(f"Generating audio for Meyme's response...")
        murf_res = requests.post(
            "https://api.murf.ai/v1/speech/generate", 
            json=payload, 
            headers=headers,
            timeout=30  # Add timeout to prevent hanging
        )
        murf_res.raise_for_status()
        audio_url = murf_res.json().get("audioFile")

        if not audio_url:
            raise Exception("Murf API did not return audio URL")

        return JSONResponse(content={
            "audio_url": audio_url,
            "text": llm_text,
            "transcript": user_text
        })

    except Exception as e:
        logger.error(f"Chat pipeline failed: {e}")
        return FileResponse(FALLBACK_AUDIO_PATH, media_type="audio/mpeg", headers={"X-Error": "true"})


@app.get("/health")
async def health_check():
    """Health check endpoint for Meyme voice agent"""
    return {
        "status": "healthy",
        "service": "Meyme Voice Agent",
        "apis": {
            "assembly_ai": bool(ASSEMBLY_KEY),
            "gemini": bool(GEMINI_API_KEY),
            "murf": bool(MURF_KEY)
        }
    }
