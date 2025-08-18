# Meyme - Modern AI Voice Agent Backend

from fastapi import FastAPI, UploadFile, File, Request, Path, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import requests
import os
import assemblyai as aai
from assemblyai.streaming.v3 import (
    BeginEvent,
    StreamingClient,
    StreamingClientOptions,
    StreamingError,
    StreamingEvents,
    StreamingParameters,
    StreamingSessionParameters,
    TerminationEvent,
    TurnEvent,
)
import google.generativeai as genai
from typing import Dict, List, Any
import logging
import asyncio

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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established.")

    if not ASSEMBLY_KEY:
        logger.error("ASSEMBLYAI_API_KEY is not set. Cannot start streaming transcription.")
        await websocket.close(code=1011)  # Internal Error
        return

    streaming_client = None
    websocket_ref = websocket  # Keep reference for event handlers
    
    # Get the current event loop to schedule tasks from threads
    main_loop = asyncio.get_running_loop()
    
    # Queue to pass transcripts from thread to main loop
    transcript_queue = asyncio.Queue()

    def on_begin(client, event: BeginEvent):
        """Called when the streaming session begins"""
        logger.info(f"Session started: {event.id}")

    def on_turn(client, event: TurnEvent):
        """Called when a turn (transcript) is received"""
        if event.transcript:
            logger.info(f"🎯 TRANSCRIPT RECEIVED: '{event.transcript}' (end_of_turn: {event.end_of_turn})")
            
            # Use call_soon_threadsafe to schedule task from thread
            main_loop.call_soon_threadsafe(
                transcript_queue.put_nowait, 
                {"transcript": event.transcript, "end_of_turn": event.end_of_turn}
            )
        else:
            logger.debug(f"Turn event received but no transcript: end_of_turn={event.end_of_turn}")

    def on_terminated(client, event: TerminationEvent):
        """Called when the session is terminated"""
        logger.info(f"Session terminated: {event.audio_duration_seconds} seconds of audio processed")

    def on_error(client, error: StreamingError):
        """Called when an error occurs"""
        logger.error(f"Streaming error: {error}")

    async def send_transcript_to_client(transcript: str, end_of_turn: bool):
        """Send transcript back to client via WebSocket"""
        try:
            await websocket_ref.send_json({
                "type": "transcript",
                "transcript": transcript,
                "end_of_turn": end_of_turn
            })
        except Exception as e:
            logger.error(f"Error sending transcript to client: {e}")

    try:
        # Initialize AssemblyAI v3 StreamingClient
        streaming_client = StreamingClient(
            StreamingClientOptions(
                api_key=ASSEMBLY_KEY,
                api_host="streaming.assemblyai.com",
            )
        )

        # Set up event handlers
        streaming_client.on(StreamingEvents.Begin, on_begin)
        streaming_client.on(StreamingEvents.Turn, on_turn)
        streaming_client.on(StreamingEvents.Termination, on_terminated)
        streaming_client.on(StreamingEvents.Error, on_error)

        # Connect to AssemblyAI streaming service
        streaming_client.connect(
            StreamingParameters(
                sample_rate=16000,  # 16kHz as required
                format_turns=True,  # Enable turn formatting
            )
        )
        logger.info("AssemblyAI v3 StreamingClient connected.")

        # Create a simple audio forwarder
        import queue
        import threading
        
        # Queue to pass audio data between async WebSocket and AssemblyAI
        audio_queue = queue.Queue(maxsize=100)
        keep_running = asyncio.Event()
        keep_running.set()  # Initially set to True
        
        # Create synchronous iterator for audio streaming (AssemblyAI v3 expects sync iterator)
        class AudioStreamIterator:
            def __init__(self, audio_queue, keep_running_event):
                self.audio_queue = audio_queue
                self.keep_running = keep_running_event
                self.chunk_size = int(16000 * 0.1 * 2)  # 100ms chunks, 3200 bytes
            
            def __iter__(self):
                return self
            
            def __next__(self):
                if not self.keep_running.is_set():
                    raise StopIteration
                    
                try:
                    # Get audio data from queue with timeout
                    audio_data = self.audio_queue.get(timeout=0.1)
                    
                    # Ensure minimum size for AssemblyAI (at least 50ms)
                    if len(audio_data) < self.chunk_size:
                        audio_data = audio_data + b'\x00' * (self.chunk_size - len(audio_data))
                    
                    return audio_data
                    
                except queue.Empty:
                    # Return silence if no audio available - this keeps the stream alive
                    return b'\x00' * self.chunk_size
                except Exception as e:
                    logger.error(f"Error in audio iterator: {e}")
                    raise StopIteration
        
        # Create the audio iterator
        audio_iterator = AudioStreamIterator(audio_queue, keep_running)
        
        # Start AssemblyAI streaming in a background task using executor
        def run_streaming_client():
            try:
                # Use the synchronous iterator - this runs in a separate thread
                streaming_client.stream(audio_iterator)  # Note: removed await since this might be sync
            except Exception as e:
                logger.error(f"Error in streaming_client.stream: {e}")
        
        # Start the AssemblyAI streaming task in a thread executor
        import concurrent.futures
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        streaming_task = asyncio.get_event_loop().run_in_executor(executor, run_streaming_client)
        
        # Task to process transcript queue and send to WebSocket
        async def process_transcripts():
            try:
                while True:
                    transcript_data = await transcript_queue.get()
                    await send_transcript_to_client(
                        transcript_data["transcript"], 
                        transcript_data["end_of_turn"]
                    )
            except asyncio.CancelledError:
                pass
        
        # Start transcript processing task
        transcript_task = asyncio.create_task(process_transcripts())
        
        # Main WebSocket loop - receive audio and put in queue
        try:
            while True:
                audio_data = await websocket.receive_bytes()
                logger.info(f"Received {len(audio_data)} bytes of audio data")
                
                # Put audio data in queue for AssemblyAI
                if not audio_queue.full():
                    audio_queue.put(audio_data)
                else:
                    logger.warning("Audio queue full, dropping audio data")
                    
        except WebSocketDisconnect:
            logger.info("Client disconnected")
            keep_running.clear()
        except Exception as e:
            logger.error(f"Error in WebSocket audio loop: {e}")
            keep_running.clear()
        finally:
            # Stop the audio generator
            keep_running.clear()
            
            # Cancel both tasks
            streaming_task.cancel()
            transcript_task.cancel()
            
            try:
                await streaming_task
            except asyncio.CancelledError:
                pass
                
            try:
                await transcript_task
            except asyncio.CancelledError:
                pass

    except WebSocketDisconnect:
        logger.info("Client disconnected from WebSocket.")
    except Exception as e:
        logger.error(f"WebSocket endpoint error: {e}")
    finally:
        if streaming_client:
            try:
                streaming_client.disconnect(terminate=True)
                logger.info("AssemblyAI StreamingClient disconnected.")
            except Exception as e:
                logger.error(f"Error disconnecting streaming client: {e}")


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
