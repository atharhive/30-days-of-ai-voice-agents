# Meyme - Modern AI Voice Agent Backend

from fastapi import FastAPI, UploadFile, File, Request, Path, WebSocket, WebSocketDisconnect
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
import asyncio
import websockets
import json
import base64

# Import agent skills
from agent_skills import (
    SKILL_FUNCTION_DECLARATIONS,
    execute_skill_function,
    SKILL_FUNCTIONS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use the current AssemblyAI streaming API structure
try:
    from assemblyai.streaming import (
        StreamingClient,
        StreamingClientOptions,
        StreamingParameters,
    )
    # For compatibility with newer versions
    ASSEMBLYAI_STREAMING_AVAILABLE = True
except ImportError:
    # Fallback for older versions or if streaming not available
    ASSEMBLYAI_STREAMING_AVAILABLE = False
    logger.warning("AssemblyAI streaming not available - WebSocket features will be limited")

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


async def murf_websocket_tts(text_chunks: list, context_id: str = "day20_context", client_websocket: WebSocket = None) -> list:
    """
    Send streaming text chunks to Murf WebSocket and stream base64 audio responses to client.
    Uses a static context_id to avoid context limit exceeded errors.
    Returns list of accumulated base64 audio chunks.
    """
    if not MURF_KEY:
        logger.error("❌ MURF_API_KEY not set, cannot connect to Murf WebSocket")
        return []
    
    accumulated_audio_chunks = []
    
    try:
        # Murf WebSocket URL with parameters
        ws_url = f"wss://api.murf.ai/v1/speech/stream-input?api-key={MURF_KEY}&sample_rate=44100&channel_type=MONO&format=WAV"
        
        print(f"\n🎵 MURF WEBSOCKET TTS PROCESSING")
        print("🎵" * 40)
        print(f"🔗 Connecting to Murf WebSocket API...")
        print(f"🎤 Voice: en-US-amara (Conversational)")
        print(f"📝 Text length: {len(''.join(text_chunks))} characters")
        print(f"🆔 Context ID: {context_id}")
        print("🎵" * 40)
        logger.info(f"🎵 Connecting to Murf WebSocket for TTS...")
        
        async with websockets.connect(ws_url) as ws:
            print(f"✅ Connected to Murf WebSocket successfully!")
            
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
            print(f"📤 Sending voice configuration...")
            logger.info(f"📤 Sending voice configuration to Murf...")
            await ws.send(json.dumps(voice_config_msg))
            print(f"✅ Voice configuration sent!")
            
            # Send all text chunks as one message for now
            full_text = "".join(text_chunks)
            text_msg = {
                "text": full_text,
                "context_id": context_id,  # Use static context_id
                "end": True  # Mark as end to close context
            }
            print(f"📤 Sending text for TTS processing...")
            logger.info(f"📤 Sending text to Murf: '{full_text[:50]}{'...' if len(full_text) > 50 else ''}'")
            await ws.send(json.dumps(text_msg))
            print(f"✅ Text sent to Murf TTS!")
            
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
                        
                        # Accumulate audio chunks
                        accumulated_audio_chunks.append(base64_audio)
                        
                        # 🎵 ENHANCED: Beautiful audio chunk console output
                        print(f"\n🎵 AUDIO CHUNK #{audio_chunks_received} RECEIVED")
                        print("🎵" * 30)
                        print(f"📦 Chunk Size: {len(base64_audio):,} base64 characters")
                        print(f"📊 Total Received: {audio_chunks_received} chunks")
                        print(f"📈 Total Characters: {total_base64_chars:,}")
                        print(f"🔍 Preview: {base64_audio[:80]}{'...' if len(base64_audio) > 80 else ''}")
                        print("🎵" * 30)
                        
                        # Full base64 output (as requested for the task)
                        print(f"\n🎵 FULL BASE64 AUDIO CHUNK #{audio_chunks_received}:")
                        print("📄" * 20)
                        print(base64_audio)
                        print("📄" * 20)
                        print("=" * 80)
                        
                        logger.info(f"📥 Received audio chunk #{audio_chunks_received}: {len(base64_audio):,} chars")
                        
                        # 🎵 DAY 21: Stream audio data to client via WebSocket
                        if client_websocket and hasattr(client_websocket, 'client_state'):
                            try:
                                # Check if WebSocket is still in CONNECTED state
                                if client_websocket.client_state.name == "CONNECTED":
                                    audio_message = {
                                        "type": "audio_chunk",
                                        "chunk_index": audio_chunks_received,
                                        "base64_audio": base64_audio,
                                        "chunk_size": len(base64_audio),
                                        "total_chunks_received": audio_chunks_received
                                    }
                                    await client_websocket.send_json(audio_message)
                                    print(f"📤 ✅ STREAMED AUDIO CHUNK #{audio_chunks_received} TO CLIENT")
                                    print(f"📤 ✅ Client acknowledged receipt of {len(base64_audio):,} base64 characters")
                                    logger.info(f"📤 Streamed audio chunk #{audio_chunks_received} to client")
                                else:
                                    print(f"⚠️  Client WebSocket state: {client_websocket.client_state.name} - stopping audio streaming")
                                    logger.warning(f"Client WebSocket no longer connected ({client_websocket.client_state.name}) - stopping TTS streaming")
                                    # Break out of the TTS loop since client disconnected
                                    break
                            except Exception as stream_error:
                                if "close message has been sent" in str(stream_error) or "Connection is closed" in str(stream_error):
                                    print(f"⚠️  Client WebSocket closed - stopping audio streaming")
                                    logger.info(f"Client WebSocket closed during streaming - stopping TTS")
                                    # Break out of the loop gracefully
                                    break
                                else:
                                    print(f"❌ STREAMING ERROR: {stream_error}")
                                    logger.error(f"❌ Error streaming audio chunk to client: {stream_error}")
                        else:
                            print(f"⚠️  Client WebSocket not available - skipping audio streaming")
                            # If no client websocket, no point in continuing TTS
                            break
                    
                    if data.get("final"):
                        # 🎉 ENHANCED: Beautiful completion console output
                        print(f"\n🎉 MURF TTS PROCESSING COMPLETE!")
                        print("🎉" * 40)
                        print(f"✅ Total Audio Chunks: {audio_chunks_received}")
                        print(f"✅ Total Base64 Characters: {total_base64_chars:,}")
                        print(f"✅ Audio Format: WAV (44.1kHz, Mono)")
                        print(f"✅ Voice: en-US-amara (Conversational)")
                        print(f"✅ Ready for audio playback!")
                        print("🎉" * 40)
                        
                        # 🎵 DAY 21: Send completion message to client
                        if client_websocket and client_websocket.client_state.value == 1:
                            try:
                                completion_message = {
                                    "type": "audio_complete",
                                    "total_chunks": audio_chunks_received,
                                    "total_base64_chars": total_base64_chars,
                                    "accumulated_chunks": len(accumulated_audio_chunks)
                                }
                                await client_websocket.send_json(completion_message)
                                print(f"📤 ✅ AUDIO COMPLETION MESSAGE SENT TO CLIENT")
                                print(f"📤 ✅ Client notified of {audio_chunks_received} total chunks")
                                logger.info(f"📤 Sent audio completion message to client")
                            except Exception as completion_error:
                                print(f"❌ ERROR SENDING COMPLETION MESSAGE: {completion_error}")
                                logger.error(f"❌ Error sending completion message to client: {completion_error}")
                        else:
                            print(f"⚠️  Client WebSocket not connected - skipping completion message")
                        
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
    
    return accumulated_audio_chunks


async def stream_llm_response_with_murf_tts(user_text: str, session_id: str, client_websocket: WebSocket = None) -> str:
    """
    Stream LLM response from Gemini with function calling support, send chunks to Murf WebSocket for TTS,
    and return the complete response. Prints base64 audio to console.
    """
    try:
        # Initialize history for this session
        history = chat_histories.get(session_id, [])
        
        # Create model with function calling tools
        model = genai.GenerativeModel(
            "gemini-1.5-flash",
            system_instruction=MEYME_SYSTEM_PROMPT
        )
        
        # Start chat with existing history
        chat = model.start_chat(history=history)
        
        # 🎯 ENHANCED: Beautiful console output for user input processing
        print("\n" + "🌟" * 20)
        print("🎯 PROCESSING USER INPUT")
        print("🌟" * 20)
        print(f"📝 User said: '{user_text}'")
        print(f"🆔 Session ID: {session_id}")
        print(f"📚 Chat history: {len(history)} previous messages")
        print("🌟" * 20)
        
        logger.info(f"🎯 PROCESSING USER INPUT: '{user_text}'")
        
        # Stream the response from Gemini
        print(f"\n🚀 STREAMING LLM RESPONSE FROM GEMINI")
        print("=" * 80)
        print("🤖 Meyme is thinking and responding...")
        print("=" * 80)
        
        accumulated_response = ""
        text_chunks = []
        chunk_count = 0
        
        # Check if user message might need skills and use appropriate model
        user_lower = user_text.lower()
        needs_skills = any(keyword in user_lower for keyword in [
            'weather', 'forecast', 'temperature', 'rain', 'sunny', 'cloudy',
            'search', 'news', 'latest', 'current', 'recent', 'what\'s happening',
            'tell me about', 'find information'
        ])
        
        if needs_skills:
            print(f"\n🛠️ SKILLS DETECTED - Using function calling mode")
            
            # Create tools for function calling
            from google.generativeai.types import Tool, FunctionDeclaration
            
            # Convert our function declarations to Gemini format
            tools = []
            for func_decl in SKILL_FUNCTION_DECLARATIONS:
                tools.append(FunctionDeclaration(
                    name=func_decl['name'],
                    description=func_decl['description'],
                    parameters=func_decl['parameters']
                ))
            
            # Send message with tools
            response = chat.send_message(
                user_text,
                tools=[Tool(function_declarations=tools)]
            )
            
            # Check if the model wants to call a function
            if response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call = part.function_call
                        function_name = function_call.name
                        function_args = dict(function_call.args)
                        
                        print(f"\n🛠️ SKILL ACTIVATION: {function_name}")
                        print("🛠️" * 50)
                        print(f"📞 Function: {function_name}")
                        print(f"📋 Arguments: {function_args}")
                        print("🛠️" * 50)
                        
                        # Execute the skill function
                        skill_result = execute_skill_function(function_name, function_args)
                        
                        print(f"\n📊 SKILL RESULT:")
                        print("📊" * 30)
                        if skill_result.get('success'):
                            print(f"✅ Skill executed successfully")
                            if function_name == 'search_web' and skill_result.get('answer'):
                                print(f"🔍 Quick Answer: {skill_result['answer'][:200]}...")
                                print(f"📊 Found {skill_result.get('total_results', 0)} results")
                            elif function_name in ['get_current_weather', 'get_weather_forecast']:
                                if skill_result.get('weather'):
                                    weather = skill_result['weather']
                                    temp = skill_result.get('temperature', {})
                                    location = skill_result.get('location', {})
                                    print(f"🌤️ {location.get('name', 'Unknown')}: {weather.get('description', 'N/A')}")
                                    if temp.get('current'):
                                        print(f"🌡️ Temperature: {temp['current']}{temp.get('units', '')}")
                        else:
                            print(f"❌ Skill failed: {skill_result.get('error', 'Unknown error')}")
                        print("📊" * 30)
                        
                        # Create a simple text response incorporating the skill result
                        if skill_result.get('success'):
                            if function_name == 'get_current_weather':
                                location = skill_result['location']
                                weather = skill_result['weather']
                                temp = skill_result['temperature']
                                accumulated_response = f"The weather in {location['name']} is currently {weather['description'].lower()} with a temperature of {temp['current']}{temp['units']}. It feels like {temp['feels_like']}{temp['units']} with {skill_result['humidity']}% humidity."
                            elif function_name == 'get_weather_forecast':
                                location = skill_result['location']
                                forecast_text = f"Here's the {skill_result['days_requested']}-day forecast for {location['name']}: "
                                for day in skill_result['forecast'][:2]:  # Limit to 2 days for voice
                                    forecast_text += f"{day['day_name']}: {day['weather']['description']}, high of {day['temperature']['max']}{day['temperature']['units']}, low of {day['temperature']['min']}{day['temperature']['units']}. "
                                accumulated_response = forecast_text
                            elif function_name == 'search_web':
                                if skill_result.get('answer'):
                                    accumulated_response = f"Based on my search, {skill_result['answer']}"
                                else:
                                    accumulated_response = f"I searched for '{skill_result['query']}' and found {skill_result['total_results']} results, but couldn't get a clear answer."
                        else:
                            accumulated_response = f"I tried to help with that, but {skill_result.get('error', 'something went wrong')}."
                        
                        text_chunks = [accumulated_response]
                        
                        print(f"\n🤖 FINAL RESPONSE (with skill data):")
                        print("=" * 60)
                        print(accumulated_response)
                        print("=" * 60)
                        
                    elif part.text:
                        # Regular text response without function call
                        accumulated_response += part.text
                        text_chunks.append(part.text)
                        print(part.text, end="", flush=True)
            
            # If no function call, just use the regular response
            if not accumulated_response:
                accumulated_response = response.text or ""
                text_chunks = [accumulated_response] if accumulated_response else []
        else:
            # No skills needed - use regular streaming response
            print(f"\n💬 REGULAR RESPONSE MODE - No skills needed")
            response = chat.send_message(user_text)
            accumulated_response = response.text or ""
            text_chunks = [accumulated_response] if accumulated_response else []
            print(accumulated_response)
        
        print()  # New line after streaming
        print("=" * 80)
        print("✅ GEMINI LLM RESPONSE COMPLETE!")
        print("=" * 80)
        print(f"📊 Response Statistics:")
        print(f"   📝 Total characters: {len(accumulated_response)}")
        print(f"   📦 Text chunks: {len(text_chunks)}")
        print(f"   🎯 Final response: '{accumulated_response.strip()}'")
        print("=" * 80)
        
        # 🎵 NEW: Send accumulated response to Murf WebSocket for TTS
        if text_chunks and MURF_KEY:
            print(f"\n🎵 INITIATING MURF TTS PROCESSING")
            print("🎵" * 30)
            logger.info(f"🎵 STARTING MURF WEBSOCKET TTS for {len(text_chunks)} chunks")
            # Use session_id as context to maintain consistency
            context_id = f"session_{session_id}_{hash(user_text) % 10000}"  # Create unique but predictable context
            # 🎵 DAY 21: Pass client WebSocket for audio streaming
            accumulated_audio_chunks = await murf_websocket_tts(text_chunks, context_id, client_websocket)
            logger.info(f"🎵 DAY 21: Accumulated {len(accumulated_audio_chunks)} audio chunks for client")
            
            # 🎉 SUCCESS: Enhanced completion message
            print(f"\n🎉 PIPELINE COMPLETE!")
            print("🎉" * 30)
            print(f"✅ User Input → STT → LLM → TTS → Audio Streaming")
            print(f"✅ All processes completed successfully!")
            print(f"✅ Audio chunks streamed to client: {len(accumulated_audio_chunks)}")
            print("🎉" * 30)
        else:
            if not text_chunks:
                print("⚠️  WARNING: No text chunks to send to Murf")
                logger.warning("⚠️  No text chunks to send to Murf")
            if not MURF_KEY:
                print("⚠️  WARNING: MURF_API_KEY missing - skipping Murf TTS")
                logger.warning("⚠️  MURF_API_KEY missing - skipping Murf TTS")
        
        # Update chat history with the complete conversation
        chat_histories[session_id] = chat.history
        
        return accumulated_response.strip()
        
    except Exception as e:
        print(f"\n❌ ERROR IN LLM PROCESSING")
        print("❌" * 30)
        print(f"Error: {str(e)}")
        print("❌" * 30)
        logger.error(f"Error in streaming LLM response with Murf TTS: {e}")
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
        llm_text = await stream_llm_response_with_murf_tts(user_text, session_id)

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
    
    connected = True

    if not ASSEMBLY_KEY:
        logger.error("ASSEMBLYAI_API_KEY is not set. Cannot start streaming transcription.")
        await websocket.close(code=1011)  # Internal Error
        return
        
    if not ASSEMBLYAI_STREAMING_AVAILABLE:
        logger.warning("AssemblyAI streaming not available with current version. Using basic transcription mode.")
        # Send a message to client about limited functionality
        try:
            await websocket.send_json({
                "type": "info",
                "message": "Using basic transcription mode. Real-time streaming not available with current AssemblyAI version."
            })
        except Exception as e:
            logger.error(f"Error sending info message: {e}")
            return
    
    # Keep track of accumulated audio for basic transcription
    audio_chunks = []
    audio_chunk_count = 0
    last_transcription_time = asyncio.get_event_loop().time()
    
    try:
        while connected:
            try:
                # Check if connection is still open before receiving
                if websocket.client_state.name != "CONNECTED":
                    logger.info("WebSocket no longer connected, breaking loop")
                    break
                    
                # Try to receive as binary data first (audio)
                try:
                    audio_data = await websocket.receive_bytes()
                    audio_chunk_count += 1
                    audio_chunks.append(audio_data)
                    
                    logger.info(f"📥 Received audio chunk #{audio_chunk_count}: {len(audio_data)} bytes")
                    
                    # Send acknowledgment back to client (only if still connected)
                    if websocket.client_state.name == "CONNECTED":
                        try:
                            await websocket.send_json({
                                "type": "audio_received",
                                "chunk_count": audio_chunk_count,
                                "bytes": len(audio_data)
                            })
                        except Exception as send_error:
                            logger.error(f"Error sending audio acknowledgment: {send_error}")
                            break
                    
                    # Basic transcription every 3 seconds or when we have enough audio
                    current_time = asyncio.get_event_loop().time()
                    if (current_time - last_transcription_time > 3.0 and len(audio_chunks) > 10) or len(audio_chunks) > 100:
                        logger.info(f"🎯 Processing {len(audio_chunks)} audio chunks for transcription...")
                        
                        # Convert audio chunks to WAV format for AssemblyAI
                        try:
                            # Combine all audio chunks into a single buffer
                            combined_audio = b''.join(audio_chunks)
                            
                            # Create a WAV file in memory
                            import wave
                            import io
                            
                            # Convert PCM to WAV format
                            wav_buffer = io.BytesIO()
                            with wave.open(wav_buffer, 'wb') as wav_file:
                                wav_file.setnchannels(1)  # Mono
                                wav_file.setsampwidth(2)  # 16-bit
                                wav_file.setframerate(16000)  # 16kHz
                                wav_file.writeframes(combined_audio)
                            
                            wav_buffer.seek(0)
                            
                            # Send to AssemblyAI for transcription
                            if ASSEMBLY_KEY:
                                transcriber = aai.Transcriber()
                                transcript = transcriber.transcribe(wav_buffer)
                                
                                if transcript.status == aai.TranscriptStatus.completed and transcript.text:
                                    user_text = transcript.text.strip()
                                    logger.info(f"✅ Transcribed: {user_text}")
                                    
                                    # Send transcript to client
                                    if websocket.client_state.name == "CONNECTED":
                                        try:
                                            await websocket.send_json({
                                                "type": "transcript",
                                                "transcript": user_text,
                                                "is_partial": False,
                                                "end_of_turn": True
                                            })
                                        except Exception as transcript_error:
                                            logger.error(f"Error sending transcript: {transcript_error}")
                                            break
                                    
                                    # Generate LLM response and stream TTS audio
                                    # Use consistent session ID for memory continuity
                                    session_id = f"ws_session_{id(websocket)}"  # Unique per WebSocket connection
                                    try:
                                        llm_response = await stream_llm_response_with_murf_tts(
                                            user_text, session_id, websocket
                                        )
                                        logger.info(f"✅ Generated response: {llm_response[:100]}...")
                                    except Exception as llm_error:
                                        logger.error(f"Error generating LLM response: {llm_error}")
                                        # Send error message to client
                                        if websocket.client_state.name == "CONNECTED":
                                            try:
                                                await websocket.send_json({
                                                    "type": "transcript",
                                                    "transcript": "I'm having trouble understanding that. Could you try again?",
                                                    "is_partial": False,
                                                    "end_of_turn": True
                                                })
                                            except:
                                                pass
                                else:
                                    logger.warning(f"Transcription failed: {transcript.error if transcript.status == aai.TranscriptStatus.error else 'No speech detected'}")
                                    # Send message about no speech detected
                                    if websocket.client_state.name == "CONNECTED":
                                        try:
                                            await websocket.send_json({
                                                "type": "transcript",
                                                "transcript": "I didn't catch that. Could you speak a bit louder?",
                                                "is_partial": False,
                                                "end_of_turn": False
                                            })
                                        except:
                                            pass
                            else:
                                logger.error("AssemblyAI API key not available")
                                
                        except Exception as processing_error:
                            logger.error(f"Error processing audio chunks: {processing_error}")
                            
                        # Clear audio chunks and reset timer
                        audio_chunks = []
                        last_transcription_time = current_time
                        
                except Exception as binary_error:
                    # If bytes fails, try JSON (but check connection first)
                    if websocket.client_state.name != "CONNECTED":
                        logger.info("WebSocket disconnected during binary receive attempt")
                        break
                        
                    try:
                        data = await websocket.receive_json()
                        
                        if data.get("type") == "ping":
                            if websocket.client_state.name == "CONNECTED":
                                await websocket.send_json({"type": "pong"})
                        elif data.get("type") == "end_turn":
                            # Handle manual turn completion
                            if audio_chunks:
                                logger.info(f"🎯 End turn signal - processing accumulated audio...")
                                
                                # Process accumulated audio chunks for transcription
                                try:
                                    # Combine all audio chunks into a single buffer
                                    combined_audio = b''.join(audio_chunks)
                                    
                                    # Create a WAV file in memory
                                    import wave
                                    import io
                                    
                                    # Convert PCM to WAV format
                                    wav_buffer = io.BytesIO()
                                    with wave.open(wav_buffer, 'wb') as wav_file:
                                        wav_file.setnchannels(1)  # Mono
                                        wav_file.setsampwidth(2)  # 16-bit
                                        wav_file.setframerate(16000)  # 16kHz
                                        wav_file.writeframes(combined_audio)
                                    
                                    wav_buffer.seek(0)
                                    
                                    # Send to AssemblyAI for transcription
                                    if ASSEMBLY_KEY:
                                        transcriber = aai.Transcriber()
                                        transcript = transcriber.transcribe(wav_buffer)
                                        
                                        if transcript.status == aai.TranscriptStatus.completed and transcript.text:
                                            user_text = transcript.text.strip()
                                            logger.info(f"✅ End turn transcribed: {user_text}")
                                            
                                            # Send transcript to client
                                            if websocket.client_state.name == "CONNECTED":
                                                try:
                                                    await websocket.send_json({
                                                        "type": "transcript",
                                                        "transcript": user_text,
                                                        "is_partial": False,
                                                        "end_of_turn": True
                                                    })
                                                except Exception as transcript_error:
                                                    logger.error(f"Error sending end turn transcript: {transcript_error}")
                                                    break
                                            
                                            # Generate LLM response and stream TTS audio
                                            # Use consistent session ID for memory continuity
                                            session_id = f"ws_session_{id(websocket)}"  # Unique per WebSocket connection
                                            try:
                                                llm_response = await stream_llm_response_with_murf_tts(
                                                    user_text, session_id, websocket
                                                )
                                                logger.info(f"✅ End turn generated response: {llm_response[:100]}...")
                                            except Exception as llm_error:
                                                logger.error(f"Error generating LLM response on end turn: {llm_error}")
                                                # Send error message to client
                                                if websocket.client_state.name == "CONNECTED":
                                                    try:
                                                        await websocket.send_json({
                                                            "type": "transcript",
                                                            "transcript": "I'm having trouble understanding that. Could you try again?",
                                                            "is_partial": False,
                                                            "end_of_turn": True
                                                        })
                                                    except:
                                                        pass
                                        else:
                                            logger.warning(f"End turn transcription failed: {transcript.error if transcript.status == aai.TranscriptStatus.error else 'No speech detected'}")
                                            # Send message about no speech detected
                                            if websocket.client_state.name == "CONNECTED":
                                                try:
                                                    await websocket.send_json({
                                                        "type": "transcript",
                                                        "transcript": "I didn't catch that. Could you speak a bit louder?",
                                                        "is_partial": False,
                                                        "end_of_turn": False
                                                    })
                                                except:
                                                    pass
                                    else:
                                        logger.error("AssemblyAI API key not available for end turn processing")
                                        
                                except Exception as processing_error:
                                    logger.error(f"Error processing end turn audio chunks: {processing_error}")
                                
                                # Clear audio chunks after processing
                                audio_chunks = []
                                
                    except Exception as json_error:
                        logger.error(f"Error receiving JSON message: {json_error}")
                        break
                            
            except WebSocketDisconnect:
                logger.info("Client disconnected (WebSocketDisconnect caught)")
                connected = False
                break
            except Exception as e:
                logger.error(f"Error in WebSocket loop: {e}")
                connected = False
                break
                    
    except WebSocketDisconnect:
        logger.info("Client disconnected from WebSocket.")
    except Exception as e:
        logger.error(f"WebSocket endpoint error: {e}")
    finally:
        logger.info("WebSocket endpoint cleanup completed")


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
