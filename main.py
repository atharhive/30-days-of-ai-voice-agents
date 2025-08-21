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
    PartialTranscriptEvent,
)
import google.generativeai as genai
from typing import Dict, List, Any
import logging
import asyncio
import websockets
import json
import base64

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


async def murf_websocket_tts(text_chunks: list, context_id: str = "day20_context") -> None:
    """
    Send streaming text chunks to Murf WebSocket and print base64 audio responses.
    Uses a static context_id to avoid context limit exceeded errors.
    """
    if not MURF_KEY:
        logger.error("❌ MURF_API_KEY not set, cannot connect to Murf WebSocket")
        return
    
    try:
        # Murf WebSocket URL with parameters
        ws_url = f"wss://api.murf.ai/v1/speech/stream-input?api-key={MURF_KEY}&sample_rate=44100&channel_type=MONO&format=WAV"
        
        print(f"\n🎵 MURF WEBSOCKET TTS STARTED")
        print("=" * 80)
        logger.info(f"🎵 Connecting to Murf WebSocket for TTS...")
        
        async with websockets.connect(ws_url) as ws:
            # Send voice config first
            voice_config_msg = {
                "voice_config": {
                    "voiceId": "en-US-amara",
                    "style": "Conversational",
                    "rate": 0,
                    "pitch": 0,
                    "variation": 1
                },
                "context_id": context_id  # Use static context_id to avoid limits
            }
            logger.info(f"📤 Sending voice configuration to Murf...")
            await ws.send(json.dumps(voice_config_msg))
            
            # Send all text chunks as one message for now
            full_text = "".join(text_chunks)
            text_msg = {
                "text": full_text,
                "context_id": context_id,  # Use static context_id
                "end": True  # Mark as end to close context
            }
            logger.info(f"📤 Sending text to Murf: '{full_text[:50]}{'...' if len(full_text) > 50 else ''}'")
            await ws.send(json.dumps(text_msg))
            
            # Receive and process audio responses
            audio_chunks_received = 0
            total_base64_chars = 0
            
            while True:
                try:
                    response = await ws.recv()
                    data = json.loads(response)
                    
                    if "audio" in data:
                        audio_chunks_received += 1
                        base64_audio = data["audio"]
                        total_base64_chars += len(base64_audio)
                        
                        # Enhanced console output for screenshot
                        print(f"\n📦 MURF BASE64 AUDIO CHUNK #{audio_chunks_received}:")
                        print(f"   Size: {len(base64_audio):,} base64 characters")
                        print(f"   Preview: {base64_audio[:80]}{'...' if len(base64_audio) > 80 else ''}")
                        print("   " + "-" * 75)
                        
                        # Full base64 output (as requested for the task)
                        print(f"\n🎵 FULL BASE64 AUDIO CHUNK #{audio_chunks_received}:")
                        print(base64_audio)
                        print("\n" + "=" * 80)
                        
                        logger.info(f"📥 Received audio chunk #{audio_chunks_received}: {len(base64_audio):,} chars")
                    
                    if data.get("final"):
                        print(f"\n✅ MURF WEBSOCKET TTS COMPLETE!")
                        print(f"   📊 Total chunks received: {audio_chunks_received}")
                        print(f"   📊 Total base64 characters: {total_base64_chars:,}")
                        print(f"   🎯 Ready for audio playback!")
                        print("=" * 80)
                        
                        logger.info(f"✅ MURF TTS COMPLETE - {audio_chunks_received} chunks, {total_base64_chars:,} total chars")
                        break
                        
                except websockets.exceptions.ConnectionClosed:
                    logger.info("🔌 Murf WebSocket connection closed")
                    break
                except Exception as chunk_error:
                    logger.error(f"❌ Error processing Murf response: {chunk_error}")
                    break
                    
    except Exception as e:
        logger.error(f"❌ Error in Murf WebSocket TTS: {e}")
        print(f"❌ MURF WEBSOCKET ERROR: {e}")


async def stream_llm_response_with_murf_tts(user_text: str, session_id: str) -> str:
    """
    Stream LLM response from Gemini, send chunks to Murf WebSocket for TTS,
    and return the complete response. Prints base64 audio to console.
    """
    try:
        # Initialize history for this session
        history = chat_histories.get(session_id, [])
        model = genai.GenerativeModel(
            "gemini-1.5-flash",
            system_instruction=MEYME_SYSTEM_PROMPT
        )
        
        # Start chat with existing history
        chat = model.start_chat(history=history)
        logger.info(f"🎯 PROCESSING USER INPUT: '{user_text}'")
        
        # Stream the response from Gemini
        print(f"\n🚀 STREAMING LLM RESPONSE FOR: '{user_text}'")
        print("=" * 60)
        
        accumulated_response = ""
        text_chunks = []
        
        # Use Gemini's streaming API
        response_stream = chat.send_message(user_text, stream=True)
        
        for chunk in response_stream:
            if chunk.text:
                # Print each chunk as it arrives
                print(chunk.text, end="", flush=True)
                accumulated_response += chunk.text
                text_chunks.append(chunk.text)
        
        print()  # New line after streaming
        print("=" * 60)
        print(f"✅ COMPLETE LLM RESPONSE: '{accumulated_response.strip()}'")
        print("=" * 60)
        
        # 🎵 NEW: Send accumulated response to Murf WebSocket for TTS
        if text_chunks and MURF_KEY:
            logger.info(f"🎵 STARTING MURF WEBSOCKET TTS for {len(text_chunks)} chunks")
            # Use session_id as context to maintain consistency
            context_id = f"session_{session_id}_{hash(user_text) % 10000}"  # Create unique but predictable context
            await murf_websocket_tts(text_chunks, context_id)
        else:
            if not text_chunks:
                logger.warning("⚠️  No text chunks to send to Murf")
            if not MURF_KEY:
                logger.warning("⚠️  MURF_API_KEY missing - skipping Murf TTS")
        
        # Update chat history with the complete conversation
        chat_histories[session_id] = chat.history
        
        return accumulated_response.strip()
        
    except Exception as e:
        logger.error(f"Error in streaming LLM response with Murf TTS: {e}")
        return f"Sorry, I'm having trouble processing that right now. {str(e)}"


async def stream_llm_response(user_text: str, session_id: str) -> str:
    """
    Stream LLM response from Gemini and accumulate the full response.
    Prints streaming chunks to console and returns the complete response.
    """
    try:
        # Initialize history for this session
        history = chat_histories.get(session_id, [])
        model = genai.GenerativeModel(
            "gemini-1.5-flash",
            system_instruction=MEYME_SYSTEM_PROMPT
        )
        
        # Start chat with existing history
        chat = model.start_chat(history=history)
        logger.info(f"🎯 PROCESSING USER INPUT: '{user_text}'")
        
        # Stream the response from Gemini
        print(f"\n🚀 STREAMING LLM RESPONSE FOR: '{user_text}'")
        print("=" * 60)
        
        accumulated_response = ""
        
        # Use Gemini's streaming API
        response_stream = chat.send_message(user_text, stream=True)
        
        for chunk in response_stream:
            if chunk.text:
                # Print each chunk as it arrives
                print(chunk.text, end="", flush=True)
                accumulated_response += chunk.text
        
        print()  # New line after streaming
        print("=" * 60)
        print(f"✅ COMPLETE LLM RESPONSE: '{accumulated_response.strip()}'")
        print("=" * 60)
        
        # Update chat history with the complete conversation
        chat_histories[session_id] = chat.history
        
        return accumulated_response.strip()
        
    except Exception as e:
        logger.error(f"Error in streaming LLM response: {e}")
        return f"Sorry, I'm having trouble processing that right now. {str(e)}"


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

        # Step 2: Get streaming LLM response
        logger.info(f"User said: {user_text}")
        
        # Use our streaming LLM function
        llm_text = await stream_llm_response(user_text, session_id)

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

    def on_partial_transcript(client, event: PartialTranscriptEvent):
        """Called when partial transcript is received (real-time word-by-word updates)"""
        if event.partial_transcript:
            logger.debug(f"📝 PARTIAL: '{event.partial_transcript}'")
            
            # Send partial transcript immediately for real-time display
            main_loop.call_soon_threadsafe(
                transcript_queue.put_nowait, 
                {
                    "transcript": event.partial_transcript,
                    "end_of_turn": False,
                    "is_partial": True,
                    "turn_order": 0,
                    "turn_is_formatted": False,
                    "end_of_turn_confidence": 0.0
                }
            )

    def on_turn(client, event: TurnEvent):
        """Called when a turn (transcript) is received"""
        if event.transcript:
            logger.info(f"🎯 TRANSCRIPT RECEIVED: '{event.transcript}' (end_of_turn: {event.end_of_turn})")
            
            # Use call_soon_threadsafe to schedule task from thread
            main_loop.call_soon_threadsafe(
                transcript_queue.put_nowait, 
                {
                    "transcript": event.transcript, 
                    "end_of_turn": event.end_of_turn,
                    "is_partial": False,
                    "turn_order": event.turn_order,
                    "turn_is_formatted": event.turn_is_formatted,
                    "end_of_turn_confidence": getattr(event, 'end_of_turn_confidence', 0.0)
                }
            )
        else:
            logger.debug(f"Turn event received but no transcript: end_of_turn={event.end_of_turn}")
            # Still send end_of_turn notification even without transcript
            if event.end_of_turn:
                main_loop.call_soon_threadsafe(
                    transcript_queue.put_nowait, 
                    {
                        "transcript": "", 
                        "end_of_turn": True,
                        "is_partial": False,
                        "turn_order": getattr(event, 'turn_order', 0),
                        "turn_is_formatted": getattr(event, 'turn_is_formatted', False),
                        "end_of_turn_confidence": getattr(event, 'end_of_turn_confidence', 0.0)
                    }
                )

    def on_terminated(client, event: TerminationEvent):
        """Called when the session is terminated"""
        logger.info(f"Session terminated: {event.audio_duration_seconds} seconds of audio processed")

    def on_error(client, error: StreamingError):
        """Called when an error occurs"""
        logger.error(f"Streaming error: {error}")

    async def send_transcript_to_client(transcript_data: dict):
        """Send transcript back to client via WebSocket"""
        try:
            message = {
                "type": "transcript",
                "transcript": transcript_data["transcript"],
                "end_of_turn": transcript_data["end_of_turn"],
                "is_partial": transcript_data.get("is_partial", False),
                "turn_order": transcript_data.get("turn_order", 0),
                "turn_is_formatted": transcript_data.get("turn_is_formatted", False),
                "end_of_turn_confidence": transcript_data.get("end_of_turn_confidence", 0.0)
            }
            
            # Send turn end notification if this is the end of a turn
            if transcript_data["end_of_turn"]:
                logger.info(f"🔔 TURN DETECTION: End of turn detected with confidence {transcript_data.get('end_of_turn_confidence', 0.0):.2f}")
                
                # 🚀 NEW: Trigger streaming LLM response on final transcript
                final_transcript = transcript_data["transcript"].strip()
                if final_transcript and GEMINI_API_KEY:
                    logger.info(f"🤖 TRIGGERING STREAMING LLM for final transcript: '{final_transcript}'")
                    
                    # Generate a session ID for this WebSocket connection
                    session_id = f"ws_session_{id(websocket_ref)}"
                    
                    # 🎵 NEW DAY 20: Call streaming LLM function with Murf WebSocket TTS
                    try:
                        llm_response = await stream_llm_response_with_murf_tts(final_transcript, session_id)
                        logger.info(f"✅ LLM streaming + Murf TTS complete. Final response length: {len(llm_response)} chars")
                    except Exception as llm_error:
                        logger.error(f"❌ Error in streaming LLM with Murf TTS: {llm_error}")
                else:
                    if not final_transcript:
                        logger.info("⚠️  No final transcript to process")
                    if not GEMINI_API_KEY:
                        logger.warning("⚠️  GEMINI_API_KEY missing - skipping LLM processing")
                
                # Send a specific turn end message
                await websocket_ref.send_json({
                    "type": "turn_end",
                    "transcript": transcript_data["transcript"],
                    "turn_order": transcript_data.get("turn_order", 0),
                    "confidence": transcript_data.get("end_of_turn_confidence", 0.0),
                    "is_formatted": transcript_data.get("turn_is_formatted", False)
                })
            
            # Always send the transcript message
            await websocket_ref.send_json(message)
            
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
        streaming_client.on(StreamingEvents.PartialTranscript, on_partial_transcript)
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
                    await send_transcript_to_client(transcript_data)
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
