# System Architecture & Workflow

This document provides a detailed look into the architecture of the Meyme AI Voice Agent and the technical workflow that powers its real-time conversational abilities.

## 1. High-Level Architecture

The system is composed of three main layers:

1.  **Frontend (Client):** A web-based user interface responsible for capturing user audio, rendering visualizations, and playing back the AI's spoken responses.
2.  **Backend (Server):** A FastAPI application that acts as the central nervous system, orchestrating the flow of data between the frontend and the various AI services.
3.  **AI Services:** A suite of third-party APIs that provide the core AI functionalities: Speech-to-Text (STT), Large Language Model (LLM), and Text-to-Speech (TTS).

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   🎤 Frontend   │◄───►│  🚀 FastAPI     │◄───►│ 🧠 AI Services  │
│ (HTML, JS, CSS) │      │    (Python)     │      │ (AssemblyAI,    │
│                 │      │                 │      │  Gemini, Murf)  │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

## 2. Component Breakdown

### Frontend (Client)
- **Technology:** Vanilla JavaScript, HTML5, CSS3.
- **Responsibilities:**
    - **Audio Capture:** Uses the `MediaRecorder` API to capture audio from the user's microphone.
    - **WebSocket Communication:** Establishes and maintains a persistent WebSocket connection with the backend for real-time, bidirectional data transfer.
    - **Audio Playback:** Receives audio chunks (as base64 strings) from the server and uses a custom buffer to play them back seamlessly, creating a continuous audio stream.
    - **UI/UX:** Renders the user interface, including a record button and audio visualizations, to provide feedback to the user.

### Backend (Server)
- **Technology:** FastAPI (Python).
- **Responsibilities:**
    - **API Endpoints:** Provides REST endpoints for initial setup (`/`) and health checks, and a WebSocket endpoint (`/ws`) for the main conversational loop.
    - **Service Orchestration:** Manages the entire lifecycle of a user turn. It receives audio from the client, sends it to the STT service, passes the resulting text to the LLM, streams the LLM's response to the TTS service, and streams the final audio back to the client.
    - **State Management:** Manages the conversational state, including chat history, to provide context to the LLM.
    - **Error Handling:** Implements robust error handling to manage failures in any of the downstream AI services.

### AI Services
- **Speech-to-Text (STT):** **AssemblyAI** is used for its high-accuracy, real-time streaming transcription capabilities. It converts the user's spoken audio into text.
- **Large Language Model (LLM):** **Google Gemini** provides the core intelligence and personality. It generates text-based responses based on the user's query and the conversation history.
- **Text-to-Speech (TTS):** **Murf AI** converts the LLM's text response back into natural-sounding speech. Its WebSocket support is crucial for real-time audio generation and streaming.

## 3. Workflow Explained: The Shift to Streaming

The project evolved from a basic REST-based architecture to a sophisticated streaming architecture. This shift was critical for achieving a low-latency, natural-feeling conversation.

### Initial Non-Streaming Workflow (REST-based)

In the initial phase, the workflow was a series of blocking, sequential HTTP requests:

1.  User records audio. The **entire** clip is sent to the backend via a POST request.
2.  Backend sends the **entire** audio file to AssemblyAI.
3.  Backend waits for the full transcription.
4.  Backend sends the **entire** transcript to Gemini.
5.  Backend waits for the full LLM response.
6.  Backend sends the **entire** text response to Murf AI.
7.  Backend waits for the full audio file to be generated and returns the URL to the client.
8.  Client downloads and plays the audio file.

- **Problem:** This approach introduces significant delays at each step, resulting in a slow, clunky user experience. The user has to wait a long time after speaking to hear a response, making the conversation feel unnatural.

### Final Streaming Workflow (WebSocket-based)

The final architecture uses WebSockets to create a persistent, low-latency communication channel.

1.  User starts recording. Audio is streamed to the backend in **small chunks** via WebSockets.
2.  Backend simultaneously streams these audio chunks to AssemblyAI's WebSocket endpoint.
3.  AssemblyAI performs real-time transcription and sends back text as it's recognized. It detects when the user has finished speaking ("turn detection").
4.  Once a turn is detected, the final transcript is sent to Gemini's streaming endpoint.
5.  The backend receives the LLM response **token by token**.
6.  These tokens are immediately streamed to Murf AI's WebSocket endpoint for TTS conversion.
7.  Murf AI generates audio and streams it back to the backend in **small chunks** (base64 encoded).
8.  The backend immediately forwards these audio chunks to the frontend via the client's WebSocket connection.
9.  The frontend plays these audio chunks as they arrive, creating a seamless and immediate audio response.

- **Why this is better:** The streaming workflow dramatically reduces perceived latency. The AI can start speaking almost immediately after the user finishes, as there is no waiting for entire files to be processed. This creates a fluid, natural, and engaging conversational experience, which is essential for a voice-first application.
