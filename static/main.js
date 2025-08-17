// Meyme - Modern AI Voice Agent JavaScript

document.addEventListener('DOMContentLoaded', () => {
  const voiceButton = document.getElementById('voiceButton');
  const micIcon = document.getElementById('micIcon');
  const statusMessage = document.getElementById('statusMessage');
  let isRecording = false;
  let recorder = null;
  let socket = null;

  const toggleRecording = async () => {
    if (isRecording) {
      stopRecording();
    } else {
      await startRecording();
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      socket = new WebSocket(`ws://${window.location.host}/ws`);

      socket.onopen = () => {
        recorder = new MediaRecorder(stream);
        recorder.ondataavailable = (event) => {
          if (event.data.size > 0 && socket.readyState === WebSocket.OPEN) {
            socket.send(event.data);
          }
        };
        recorder.start(250); // Send data every 250ms
        isRecording = true;
        updateUIForRecording();
        statusMessage.textContent = '🎙️ Listening...';
      };

      socket.onclose = () => {
        console.log('WebSocket connection closed');
        stopRecording();
      };

      socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        stopRecording();
      };

    } catch (error) {
      console.error('Error starting recording:', error);
      statusMessage.textContent = '❌ Microphone access denied. Please allow microphone permissions.';
    }
  };

  const stopRecording = () => {
    if (recorder && isRecording) {
      recorder.stop();
      recorder.stream.getTracks().forEach(track => track.stop());
    }
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.close();
    }
    isRecording = false;
    updateUIForStopped();
    statusMessage.textContent = 'Press the mic button to start talking with Meyme!';
  };

  const updateUIForRecording = () => {
    voiceButton.classList.add('recording');
    micIcon.className = 'fas fa-stop';
  };

  const updateUIForStopped = () => {
    voiceButton.classList.remove('recording');
    micIcon.className = 'fas fa-microphone';
  };

  voiceButton.addEventListener('click', toggleRecording);
});