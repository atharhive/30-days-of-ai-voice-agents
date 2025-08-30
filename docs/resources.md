# 30 Days of AI Voice Agents: Tasks & Resources

This file provides a day-by-day breakdown of the tasks and resources from the "30 Days of AI Voice Agents" challenge by Murf AI.

---

### Day 1: Project Setup
**Task:** Initialize a Python backend using a framework like Flask or FastAPI. Create a basic `index.html` file and a corresponding JavaScript file for the frontend. Serve the HTML page from your Python server.

---

### Day 2: Your First REST TTS Call
**Task:** Create a server endpoint that accepts text. This endpoint will call Murf's REST TTS API (`/generate`), and return a URL pointing to the generated audio file.

---

### Day 3: Playing back TTS Audio
**Task:** On your client, create a text field that accepts an input and a submit button. Use them to send a request to the "generate audio" endpoint, which will give you an audio URL in the response. Play that audio in your webpage using an HTML `<audio>` element.

---

### Day 4: Build an Echo Bot
**Task:** Build an echo bot that will record your voice and play it back to you. Use the browser's `MediaRecorder` API to record a short audio clip. Create "Start Recording" and "Stop Recording" buttons. Play the recorded audio back using an HTML `<audio>` element.
**Resources:**
- [MDN: Using the MediaStream Recording API](https://developer.mozilla.org/en-US/docs/Web/API/MediaStream_Recording_API/Using_the_MediaStream_Recording_API)

---

### Day 5: Send Audio to the Server
**Task:** Upload the recorded audio file to your Python server once the recording is stopped. Build a new endpoint on your server that will receive the audio file, save it temporarily to an `/uploads` folder, and return the file details as a response.
**Resources:**
- [FastAPI: Request Files](https://fastapi.tiangolo.com/tutorial/request-files/)
- [FastAPI: UploadFile](https://fastapi.tiangolo.com/reference/uploadfile/)
- [GeeksforGeeks: Save UploadFile in FastAPI](https://www.geeksforgeeks.org/python/save-uploadfile-in-fastapi/)

---

### Day 6: Implement Server-Side Transcription
**Task:** Create a new endpoint `/transcribe/file` that accepts a file, transcribes it using a third-party API (like AssemblyAI), and returns the transcription. Display the result in the UI.
**Resources:**
- [AssemblyAI Signup](https://www.assemblyai.com/dashboard/signup)
- [AssemblyAI Docs: Transcribe an audio file](https://www.assemblyai.com/docs/getting-started/transcribe-an-audio-file)
- [AssemblyAI Python SDK](https://pypi.org/project/assemblyai/)

---

### Day 7: Echo Bot v2
**Task:** Update your echo bot. Instead of replaying the recording, transcribe the audio, send the text to Murf to generate a new voice, and play the Murf audio in the UI.
**Resources:**
- [Murf API Docs: Text-to-Speech](https://murf.ai/api/docs/text-to-speech/overview)

---

### Day 8: Integrating a Large Language Model (LLM)
**Task:** Create a new POST `/llm/query` endpoint that accepts text, calls an LLM API (like Google's Gemini) to generate a response, and returns it.
**Resources:**
- [Google AI: Get Gemini API key](https://ai.google.dev/gemini-api/docs/quickstart)
- [Gemini API Docs](https://ai.google.dev/gemini-api/docs)

---

### Day 9: The Full Non-Streaming Pipeline
**Task:** Update your `/llm/query` endpoint to accept audio. Transcribe the audio, send it to the LLM, send the LLM's response to Murf for TTS, and play the final audio in the UI.

---

### Day 10: Chat History
**Task:** Implement chat history. Create a new endpoint `POST /agent/chat/{session_id}` that stores and retrieves conversation history, allowing the LLM to remember past interactions.
 
---

### Day 11: Error Handling
**Task:** Make the application more robust. Add `try-except` blocks on the server and error handling on the client for API failures (STT, LLM, TTS). Provide a fallback audio response.

---

### Day 12: Revamping the UI
**Task:** Revamp the UI. Combine recording buttons, improve styling, and add animations to create a more polished user experience.

---

### Day 13: Documentation
**Task:** Create a `README.md` file. Write about the project, technologies, architecture, and features. Add instructions on how to run the code.

---

### Day 14: Refactor and Clean Up
**Task:** Refactor the code for readability and maintainability. Use Pydantic models for schemas, separate logic into a `/services` folder, and clean up unused code.

---

### Day 15: Websockets
**Task:** Establish a WebSocket connection between the client and the server using a `/ws` endpoint.
**Resources:**
- [FastAPI: WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)

---

### Day 16: Streaming Audio
**Task:** Record and stream audio data from the client to the server using WebSockets. On the server, receive the binary audio data and save it to a file.

---

### Day 17: Websockets and AssemblyAI
**Task:** Use AssemblyAI's Python SDK to transcribe the streaming audio data received via WebSockets.
**Resources:**
- [AssemblyAI Docs: Transcribe streaming audio](https://www.assemblyai.com/docs/getting-started/transcribe-streaming-audio)
- [AssemblyAI Python SDK Streaming Examples](https://github.com/AssemblyAI/assemblyai-python-sdk?tab=readme-ov-file#streaming-examples)

---

### Day 18: Turn Detection
**Task:** Use AssemblyAI's streaming API to detect when a user stops talking. Send a WebSocket message to the client to signify the end of the turn and display the transcription.
**Resources:**
- [AssemblyAI Docs: Streaming API Turn Object](https://www.assemblyai.com/docs/speech-to-text/universal-streaming#turn-object)

---

### Day 19: Streaming LLM Responses
**Task:** Once the final transcript is received, send it to the LLM API to generate a streaming response. Accumulate the response and print it to the console.
**Resources:**
- [Gemini API Docs: Streaming](https://ai.google.dev/api/generate-content#method:-models.streamgeneratecontent)

---

### Day 20: Murf Websockets
**Task:** Send the LLM's streaming response to Murf using WebSockets. Murf will return the audio in base64 format.
**Resources:**
- [Murf API Docs: WebSockets](https://murf.ai/api/docs/text-to-speech/web-sockets)

---

### Day 21: Streaming Audio Data to Client
**Task:** Stream the base64 audio data from the server to the client over WebSockets and accumulate the chunks in an array.

---

### Day 22: Playing Streaming Audio
**Task:** Play the audio data in the UI as it arrives in chunks from the server, ensuring the playback is as seamless as possible.
**Resources:**
- [Murf Cookbook: Streaming Example](https://github.com/murf-ai/murf-cookbook/blob/main/examples/text-to-speech/js/websocket/basic/index.js)

---

### Day 23: Complete Voice Agent
**Task:** Connect all the pieces together. The agent should handle the user's query, transcribe it, send it to the LLM, generate a response, save chat history, send the response to Murf, and stream the audio to the client.

---

### Day 24: Agent Persona
**Task:** Add a persona to the agent. This can be anything from a character to a role to a personality (e.g., Pirate, Cowboy, Robot).

---

### Day 25: Agent Special Skill 1
**Task:** Add a special skill to the agent, such as the ability to search the web, get the latest weather, or any other skill you can think of.
**Resources:**
- [Gemini API Docs: Function Calling](https://ai.google.dev/gemini-api/docs/function-calling?example=weather#automatic_function_calling_python_only)
- [Tavily Docs: Web Search Skill Example](https://docs.tavily.com/documentation/quickstart)

---

### Day 26: Agent Special Skill 2
**Task:** Add another special skill to the agent or improve upon an existing one.

---

### Day 27: Revamp UI and Code Cleanup
**Task:** Add a config section in the UI to allow the user to enter their API keys. Optionally, revamp the UI and clean up the code.

---

### Day 28: Deploy Your Agent
**Task:** Host your agent so that it can be accessed by the public.
**Resources:**
- [Render](https://render.com/)
- [FastAPI CLI](https://fastapi.tiangolo.com/fastapi-cli/#fastapi-run)

---

### Day 29: Final Documentation
**Task:** Update the `README.md` file to include the new features you have added to the agent. Optionally, write a blog post about the agent you built.
