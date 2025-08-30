# System Architecture & Workflow

This document provides a detailed look into the architecture of the Meyme AI Voice Agent and the technical workflow that powers its real-time conversational abilities.

## 1. Guiding Principles

- **Low Latency:** The primary goal is to minimize the time between a user finishing speaking and the agent starting its response. This is crucial for a natural-feeling conversation.
- **Modularity:** Each component (STT, LLM, TTS) is decoupled into its own service, making the system easier to maintain, debug, and upgrade.
- **Streaming First:** The entire pipeline is designed around streaming data in small chunks rather than waiting for entire files to be processed. This is the key to achieving low latency.

## 2. Architecture Diagram

This diagram illustrates the flow of data from the user's microphone, through the backend services, and back to the user's speaker.

```mermaid
graph TD
    subgraph "User Interface"
        A[User Mic]
        B{Frontend (JavaScript)}
        G[User Speaker]
    end

    subgraph "Backend Server"
        C{Backend (FastAPI) on Render}
    end

    subgraph "AI Services (Third-Party APIs)"
        D[AssemblyAI for STT]
        E[Google Gemini for LLM]
        F[Murf AI for TTS]
    end

    A -- Audio Stream --> B
    B -- WebSocket Audio Chunks --> C
    C -- Streams Audio --> D
    D -- Returns Final Transcript --> C
    C -- Sends Transcript --> E
    E -- Streams Response Text --> C
    C -- Streams Text Chunks --> F
    F -- Streams Audio Chunks --> C
    C -- WebSocket Audio Chunks --> B
    B -- Plays Audio Stream --> G
```

## 3. Component Breakdown

### Frontend (Client)
- **Technology:** Vanilla JavaScript, HTML5, CSS3.
- **Responsibilities:**
    - **Audio Capture:** Uses the `MediaRecorder` API to capture audio from the user's microphone in a specific format (e.g., 16kHz mono PCM) compatible with the STT service.
    - **WebSocket Communication:** Establishes and maintains a persistent WebSocket connection with the backend. It sends outgoing audio chunks and receives incoming audio chunks for playback.
    - **Audio Playback & Buffering:** Manages an audio buffer to seamlessly queue and play the incoming audio chunks from the server. This is critical for avoiding choppy playback.
    - **UI/UX:** Renders the user interface, including a record button that provides visual feedback on the agent's state (e.g., idle, recording, processing, speaking).

### Backend (Server)
- **Technology:** FastAPI (Python).
- **Responsibilities:**
    - **API Endpoints:** Provides a root endpoint (`/`) to serve the HTML page, a health check endpoint (`/health`), and the primary WebSocket endpoint (`/ws`) for the conversational loop.
    - **Service Orchestration:** Acts as the central controller. It manages the complex, asynchronous flow of data between all the AI services.
    - **Asynchronous Pipeline Management:** The core of the backend is an `async` function that juggles multiple tasks concurrently: receiving audio from the client, sending it to the STT service, listening for the transcript, sending the transcript to the LLM, streaming the LLM response to the TTS service, and streaming the final audio back to the client.
    - **State Management:** Manages the conversational state, including chat history, to provide context to the LLM for more coherent conversations.

### AI Services
- **Speech-to-Text (STT): AssemblyAI**
    - **Why:** Chosen for its high-accuracy, real-time streaming transcription capabilities and robust Python SDK.
    - **Role:** Converts the user's spoken audio into text in real-time. Its turn detection feature is key to knowing when the user has finished their thought.

- **Large Language Model (LLM): Google Gemini**
    - **Why:** A powerful and versatile model with a generous free tier, strong performance, and support for streaming responses and function calling.
    - **Role:** Provides the core intelligence and personality. It generates text-based responses based on the user's query and the conversation history. Its streaming capability is essential for the pipeline.

- **Text-to-Speech (TTS): Murf AI**
    - **Why:** Offers high-quality, natural-sounding voices and, most importantly, a WebSocket API for real-time audio synthesis.
    - **Role:** Converts the LLM's text response back into speech. Receiving this audio as a stream of chunks is the final piece of the low-latency puzzle.