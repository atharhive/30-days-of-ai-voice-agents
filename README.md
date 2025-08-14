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
| ![Vanilla JS](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black) | Frontend Interactions | Real-time audio recording, visualization, and seamless UX |

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

## 🏆 30 Days of AI Voice Agents Challenge

This project is part of the **30 Days of AI Voice Agents Challenge** by **Murf AI**! 🎉

### Challenge Progress

| Day | Task | Submission |
|-----|------|-----------|
| 1 | Project Setup & Basic Voice Recording | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 2 | Speech-to-Text Integration | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 3 | LLM Integration & Response Generation | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 4 | Text-to-Speech with Murf AI | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 5 | Complete Voice Pipeline | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 6 | Error Handling & Fallbacks | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 7 | Session Management | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 8 | UI/UX Improvements | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 9 | Audio Visualizations | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 10 | Personality Development | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 11 | Performance Optimization | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 12 | Advanced Features | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 13 | **Documentation** ← *You are here!* | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 14 | Testing & Quality Assurance | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 15 | Security Enhancements | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 16 | Mobile Responsiveness | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 17 | Analytics & Monitoring | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 18 | Multi-language Support | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 19 | Voice Customization | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 20 | Context Awareness | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 21 | Integration Features | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 22 | Advanced AI Features | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 23 | Real-time Enhancements | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 24 | Scalability Improvements | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 25 | Deployment Preparation | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 26 | Production Deployment | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 27 | Load Testing & Optimization | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 28 | Final Polish & Bug Fixes | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 29 | Project Showcase | [LinkedIn Post](https://linkedin.com/in/your-profile) |
| 30 | Challenge Completion & Reflection | [LinkedIn Post](https://linkedin.com/in/your-profile) |

---

**Challenge by:** [Murf AI](https://murf.ai) 🎵  
**Built by:** Athar  
**Challenge Hashtags:** `#30DaysOfAIVoiceAgents` `#MurfAI` `#VoiceAI` `#BuildInPublic`

## 📝 License

This project is part of the 30 Days of AI Voice Agents Challenge. Feel free to fork, modify, and build upon it for your own learning journey!

---

*Ready to chat with Meyme? Fire up the server and let the sass begin! 🐱✨*
