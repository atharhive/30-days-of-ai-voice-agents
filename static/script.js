// static/script.js
document.addEventListener("DOMContentLoaded", () => {
  const recordBtn = document.getElementById("recordBtn");
  const statusDisplay = document.getElementById("statusDisplay");
  const chatLog = document.getElementById("chat-log");
  const settingsBtn = document.getElementById("settingsBtn");
  const avatarImg = document.getElementById("avatarImg");
  const settingsModal = new bootstrap.Modal(
    document.getElementById("settingsModal")
  );
  const saveKeysBtn = document.getElementById("saveKeysBtn");

  let isRecording = false;
  let ws = null;
  let audioContext;
  let mediaStream;
  let processor;
  let audioQueue = [];
  let isPlaying = false;
  let assistantMessageDiv = null;

  // Avatar state management
  const updateAvatarState = (state) => {
    avatarImg.className = 'avatar-img breathing-gentle';
    
    switch(state) {
      case 'listening':
        avatarImg.style.filter = 'brightness(1.2) saturate(1.3)';
        break;
      case 'thinking':
        avatarImg.style.filter = 'brightness(0.9) saturate(0.8) hue-rotate(20deg)';
        break;
      case 'speaking':
        avatarImg.style.filter = 'brightness(1.1) saturate(1.2) hue-rotate(-10deg)';
        break;
      case 'idle':
      default:
        avatarImg.style.filter = 'brightness(1) saturate(1)';
        break;
    }
  };

  // Enhanced status messages with cozy personality
  const updateStatus = (status, emoji = '') => {
    statusDisplay.textContent = `${status} ${emoji}`;
  };

  // Load saved API keys
  const loadSettings = () => {
    document.getElementById("murfApiKey").value =
      localStorage.getItem("murfApiKey") || "";
    document.getElementById("assemblyAiApiKey").value =
      localStorage.getItem("assemblyAiApiKey") || "";
    document.getElementById("geminiApiKey").value =
      localStorage.getItem("geminiApiKey") || "";
    document.getElementById("serpApiKey").value =
      localStorage.getItem("serpApiKey") || "";
  };

  loadSettings();

  settingsBtn.addEventListener("click", () => {
    settingsModal.show();
  });

  saveKeysBtn.addEventListener("click", () => {
    localStorage.setItem(
      "murfApiKey",
      document.getElementById("murfApiKey").value
    );
    localStorage.setItem(
      "assemblyAiApiKey",
      document.getElementById("assemblyAiApiKey").value
    );
    localStorage.setItem(
      "geminiApiKey",
      document.getElementById("geminiApiKey").value
    );
    localStorage.setItem(
      "serpApiKey",
      document.getElementById("serpApiKey").value
    );
    settingsModal.hide();
    alert("API keys saved!");
  });

  const addOrUpdateMessage = (text, type) => {
    if (type === "assistant") {
      assistantMessageDiv = document.createElement("div");
      assistantMessageDiv.className = "message assistant";
      assistantMessageDiv.textContent = text;
      chatLog.appendChild(assistantMessageDiv);
    } else {
      assistantMessageDiv = null;
      const messageDiv = document.createElement("div");
      messageDiv.className = "message user";
      messageDiv.textContent = text;
      chatLog.appendChild(messageDiv);
    }
    chatLog.scrollTop = chatLog.scrollHeight;
  };

  const playNextInQueue = () => {
    if (audioQueue.length > 0) {
      isPlaying = true;
      const base64Audio = audioQueue.shift();
      const audioData = Uint8Array.from(atob(base64Audio), (c) =>
        c.charCodeAt(0)
      ).buffer;

      audioContext
        .decodeAudioData(audioData)
        .then((buffer) => {
          const source = audioContext.createBufferSource();
          source.buffer = buffer;
          source.connect(audioContext.destination);
          source.onended = playNextInQueue;
          source.start();
        })
        .catch((e) => {
          console.error("Error decoding audio data:", e);
          playNextInQueue();
        });
    } else {
      isPlaying = false;
    }
  };

  const startRecording = async () => {
    const apiKeys = {
      murf: localStorage.getItem("murfApiKey"),
      assemblyai: localStorage.getItem("assemblyAiApiKey"),
      gemini: localStorage.getItem("geminiApiKey"),
      serpapi: localStorage.getItem("serpApiKey"),
    };

    if (
      !apiKeys.murf ||
      !apiKeys.assemblyai ||
      !apiKeys.gemini ||
      !apiKeys.serpapi
    ) {
      alert("Please set all API keys in the settings.");
      return;
    }

    try {
      mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioContext = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: 16000,
      });

      const source = audioContext.createMediaStreamSource(mediaStream);
      processor = audioContext.createScriptProcessor(4096, 1, 1);
      source.connect(processor);
      processor.connect(audioContext.destination);
      processor.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0);
        const pcmData = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          pcmData[i] = Math.max(-1, Math.min(1, inputData[i])) * 32767;
        }
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(pcmData.buffer);
        }
      };

      const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      ws = new WebSocket(`${wsProtocol}//${window.location.host}/ws`);

      ws.onopen = () => {
        ws.send(JSON.stringify({ type: "config", keys: apiKeys }));
      };

      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === "assistant") {
          updateAvatarState('thinking');
          recordBtn.classList.remove('recording');
          recordBtn.classList.add('thinking');
          updateStatus('Thinking cozy thoughts...', '💭');
          addOrUpdateMessage(msg.text, "assistant");
        } else if (msg.type === "final") {
          addOrUpdateMessage(msg.text, "user");
        } else if (msg.type === "audio") {
          updateAvatarState('speaking');
          recordBtn.classList.remove('thinking');
          recordBtn.classList.add('speaking');
          updateStatus('Purring sweet words...', '🗣️');
          audioQueue.push(msg.b64);
          if (!isPlaying) {
            playNextInQueue();
          }
        }
      };
      isRecording = true;
      updateAvatarState('listening');
      recordBtn.classList.add("recording");
      updateStatus('Listening with sleepy ears...', '👂');
    } catch (error) {
      console.error("Could not start recording:", error);
      alert("Microphone access is required to use the voice agent.");
    }
  };

  const stopRecording = () => {
    if (processor) processor.disconnect();
    if (mediaStream) mediaStream.getTracks().forEach((track) => track.stop());
    if (ws) ws.close();

    isRecording = false;
    updateAvatarState('idle');
    recordBtn.classList.remove('recording', 'thinking', 'speaking');
    updateStatus('Ready for a cozy chat!', '😴');
  };

  recordBtn.addEventListener("click", () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  });
});
