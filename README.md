# 🌸 Meyme - AI Voice Agent

> A cozy, modern AI voice companion with personality — built for the 30 Days of AI Voice Agents Challenge by Murf AI

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://javascript.com)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://html.spec.whatwg.org)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)](https://www.w3.org/Style/CSS)

## 🎯 What is Meyme?

Meet **Meyme** — she's not just another AI assistant. She's a fiercely loyal, cozy, and cunning cat companion with a lethal streak of sass. Built with cutting-edge voice AI technology, Meyme brings personality to every conversation. She's warm and affectionate with her owner Athar, but everyone else? Well, let's just say you're probably wasting her precious nap time.

Think of her as your personal AI cat who happened to master human speech — and she's got *opinions*.

## 🏗️ Architecture & Tech Stack

### Core Technologies

| Technology | Purpose | Why We Chose It |
|------------|---------|----------------|
| ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=FastAPI&logoColor=white) | Backend API Framework | Lightning-fast async performance, automatic OpenAPI docs, and modern Python features |
| ![AssemblyAI](https://img.shields.io/badge/AssemblyAI-FF6B35?style=flat-square&logo=ai&logoColor=white) | Speech-to-Text | Industry-leading accuracy and speed for real-time transcription |
| ![Google Gemini](https://img.shields.io/badge/Google_Gemini-4285F4?style=flat-square&logo=google&logoColor=white) | Large Language Model | Advanced conversational AI with personality customization |
| ![Murf AI](https://img.shields.io/badge/Murf_AI-7B68EE?style=flat-square&logo=soundcloud&logoColor=white) | Text-to-Speech | High-quality, natural-sounding voice synthesis |
| ![WebSockets](https://img.shields.io/badge/WebSockets-000000?style=flat-square&logo=websockets&logoColor=white) | Real-time Communication | For building interactive, bidirectional communication between the client and server |
| ![Vanilla JS](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black) | Frontend Interactions | Real-time audio recording, visualization, and seamless UX |

## 🏆 30 Days of AI Voice Agents Challenge

This project is part of the **30 Days of AI Voice Agents Challenge** by **Murf AI**! 🎉

### Challenge Progress

| Day | Task | Submission |
|-----|------|-----------|
| 1 | Set up Python backend with Flask/FastAPI and a basic HTML+JS frontend served from the server.| [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_buildwithmurf-30daysofvoiceagents-python-activity-7357411756417175552-kYRF?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 2 | Build a REST endpoint to call Murf TTS API and return generated audio URL, keeping API keys secure. | [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_30daysofvoiceagents-murfai-fastapi-activity-7357808735894818816-Vh51?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 3 | Add UI input and button to send text to TTS endpoint, play returned audio in <audio> element. | [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_30daysofvoiceagents-murfai-tts-activity-7357996900974800896-WFVP?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 4 | Create Echo Bot using MediaRecorder API to record and play back audio in browser. | [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_30daysofvoiceagents-30daysofvoiceagents-voiceai-activity-7358453708705185792-sYig?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 5 | Upload recorded audio to server, store temporarily, and return file details in response| [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_30daysofvoiceagents-murfai-fastapi-activity-7358808304430567424-2FaS?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 6 | Transcribe uploaded audio using AssemblyAI (or similar) and show text in UI. | [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_30daysofvoiceagents-voiceai-speechtotext-activity-7359230721216892931-1eYM?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 7 | Echo Bot v2 — transcribe audio, send to Murf for voice output, and play back Murf’s voice. | [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_30daysofvoiceagents-murfai-assemblyai-activity-7359591228415361024-qhg_?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 8 | Create /llm/query endpoint to accept text, send to LLM API (Gemini), and return response. | [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_voicetech-murfai-geminiapi-activity-7360044310966255616-AHC-?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 9 | Build full non-streaming pipeline: audio → STT → LLM → TTS → play voice output.| [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_30daysofvoiceagents-murfai-assemblyai-activity-7360363702354694145-BP_W?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 10 | Add chat history with session IDs so LLM remembers past conversation context. | [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_day-10-30-days-of-ai-voice-agents-with-activity-7360741552324820994-CzqX?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 11 | Implement error handling & fallbacks for STT, LLM, and TTS failures. | [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_ai-voiceai-errorhandling-activity-7361058707163525120-EEJH?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 12 | Revamp conversational UI with improved styling, animations, and better recording controls.| [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_buildwithmurf-30daysofvoiceagents-activity-7361366706272833536-PBcT?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 13 | Create README.md with project details, architecture, features, and run instructions. | [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_buildwithmurf-30daysofvoiceagents-activity-7361685305843765248-PiS4?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 14 | cleaned up and refactored my code for better readability, added Pydantic models, organized services, and improved logging | [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_buildwithmurf-30daysofvoiceagents-activity-7362147757945442304-NxAL?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 15 | **Websockets** - Implemented WebSocket connection for real-time bidirectional communication between client and server | [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_30daysofaivoiceagents-30daysofaivoiceagents-activity-7362414163047927808-Ts0p?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 16 | **Real-time Audio Streaming** - Implemented WebSocket audio streaming from browser to server with FastAPI handler | [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_30daysofvoiceagents-murfai-assemblyai-activity-7362861675886071808-xjY0?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 17 | **Streaming Transcription Fix** - Fixed AssemblyAI v3 streaming issues, achieved real-time word-by-word transcription | [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_30daysofvoiceagents-30daysofvoiceagents-buildwithmurf-activity-7363234086234025985-gQP8?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 18 | **Turn Detection** - Implemented real-time turn detection with AssemblyAI's streaming API, smart transcript handling, and UI updates | [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_30daysofvoiceagents-30daysofai-voiceai-activity-7363483074040385537-bJG-?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 19 | **Streaming LLM Responses** - Integrated streaming LLM responses with real-time console output. When final transcript received from AssemblyAI → sends to Gemini streaming API → prints response chunks live to console | [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_30daysofvoiceagents-murfai-assemblyai-activity-7363948006980677632-kKs5?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 20 | **Murf WebSocket TTS Integration** - Integrated Murf WebSocket API for real-time text-to-speech with base64 audio streaming and console output | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 21 | **Streaming Audio Data to Client** - Stream base64 audio chunks from Murf TTS to client via WebSocket, accumulate chunks in array, and print client acknowledgments | [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_day-21-of-my-30-days-of-ai-voice-agents-activity-7364722864282853376-WViK?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 22 | **Seamless Audio Streaming** - Implemented seamless audio streaming playback, Murf-style WAV chunk assembly, professional UI with audio controls, real-time streaming + complete playback, error handling and fallbacks, and memory-efficient blob management. | [LinkedIn Post](https://www.linkedin.com/posts/md-athar-jamal-makki-165b67246_buildwithmurf-30daysofai-voice-agents-activity-7365069188362670080-Aq9C?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD0KOh0BF8MN-8IUUp-M20P5OqViogEHdJc) |
| 22 | soon | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 23 | soon | [LinkedIn Post](https://linkedin.com/in/your-profile) |



### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   🎤 Frontend   │────│  🚀 FastAPI     │────│ 🧠 AI Services  │
│                 │    │                 │    │                 │
│ • Audio Record  │    │ • Session Mgmt  │    │ • AssemblyAI    │
│ • Visualizations│    │ • Audio Pipeline│    │ • Google Gemini │
│ • Real-time UI  │    │ • Error Handling│    │ • Murf AI TTS   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Pipeline Flow:**
1. **Audio Capture** → Browser records user speech via MediaRecorder API
2. **Speech Recognition** → AssemblyAI transcribes audio to text
3. **AI Processing** → Gemini generates personality-driven responses  
4. **Voice Synthesis** → Murf AI converts response to natural speech
5. **Real-time Playback** → Browser plays AI response with visual feedback

## ✨ Features

🎙️ **Real-time Voice Conversations** - Talk naturally with Meyme, no typing required  
🎭 **Unique Personality** - Sassy, loyal cat with distinct conversational style  
📱 **Modern UI/UX** - Glassmorphic design with smooth animations and audio visualizations  
🔄 **Session Persistence** - Remembers conversation context throughout your chat  
⚡ **Fast Response Times** - Optimized pipeline for near real-time interactions  
🛡️ **Error Handling** - Graceful fallbacks when services are unavailable  
🎵 **Audio Visualizations** - Beautiful real-time audio feedback during recording and playback  
🔌 **WebSocket Streaming** - Real-time websocket connection for bi-directional communication  
🎯 **Turn Detection** - Smart detection of when users finish speaking with confidence indicators  
🚀 **Streaming LLM Responses** - Real-time LLM response streaming with live console output as AI "thinks"  
🎵 **Streaming Audio to Client** - Real-time base64 audio streaming from Murf TTS to client with chunk accumulation

## 🚀 Getting Started

### Prerequisites

Make sure you have these installed:
- **Python 3.8+** 
- **pip** (Python package manager)
- **Modern web browser** with microphone access

### Environment Variables

You'll need API keys for these services. Create a `.env` file in your project root:

```bash
# Required API Keys
MURF_API_KEY=your_murf_api_key_here
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here  
GEMINI_API_KEY=your_gemini_api_key_here
```

**Where to get these keys:**
- **Murf AI**: [murf.ai](https://murf.ai) → Sign up → API Access
- **AssemblyAI**: [assemblyai.com](https://assemblyai.com) → Dashboard → API Keys
- **Google Gemini**: [ai.google.dev](https://ai.google.dev) → Get API Key

### Installation & Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd murf-ai
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Run the application**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access Meyme**
```
Open your browser and go to: http://localhost:8000
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serve the main UI |
| `POST` | `/agent/chat/{session_id}` | Process voice chat |
| `GET` | `/health` | Check service status |
| `WEBSOCKET` | `/ws` | Real-time websocket connection |

### Project Structure

```
murf-ai/
├── main.py              # FastAPI backend server
├── requirements.txt     # Python dependencies
├── .env                # Environment variables (create this)
├── templates/
│   └── index.html      # Main UI template
├── static/
│   ├── main.js         # Frontend JavaScript
│   ├── style.css       # Modern styling & animations
│   └── fallback.mp3    # Backup audio for errors
└── uploads/            # Temporary audio storage
```

## 🛠️ Development

### Running in Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag automatically restarts the server when you make code changes.

### Testing the Health Check
```bash
curl http://localhost:8000/health
```

Should return status info for all connected AI services.

## 🐛 Troubleshooting

### Common Issues

**"Microphone access denied"**
- Grant microphone permissions in your browser
- Try using `https://` or `localhost` (required by some browsers)

**"API Key missing" errors**
- Double-check your `.env` file exists and contains all required keys
- Restart the server after adding environment variables

**Audio not playing**
- Check browser audio permissions
- Ensure Murf API key is valid and has credits
- Look for CORS issues in browser console

### Logs & Debugging

The application logs helpful information to the console. Key things to watch:
- API key loading status on startup
- Speech transcription results  
- AI response generation
- TTS audio URL generation

---

**Challenge by:** [Murf AI](https://murf.ai) 🎵  
**Built by:** Athar  
**Challenge Hashtags:** `#30DaysOfAIVoiceAgents` `#MurfAI` `#VoiceAI` `#BuildInPublic`

## 📝 License

This project is part of the 30 Days of AI Voice Agents Challenge. Feel free to fork, modify, and build upon it for your own learning journey!

---

*Ready to chat with Meyme? Fire up the server and let the sass begin! 🐱✨*
