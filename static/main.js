// Meyme - Modern AI Voice Agent JavaScript

class MeymeVoiceAgent {
  constructor() {
    this.isRecording = false;
    this.isProcessing = false;
    this.recorder = null;
    this.audioChunks = [];
    this.sessionId = null;
    this.audioContext = null;
    this.analyser = null;
    this.dataArray = null;
    this.animationId = null;
    
    this.initializeElements();
    this.initializeSession();
    this.bindEvents();
    this.showInitialStatus();
  }

  initializeElements() {
    this.voiceButton = document.getElementById('voiceButton');
    this.micIcon = document.getElementById('micIcon');
    this.voiceRipples = document.getElementById('voiceRipples');
    this.audioVisualizer = document.getElementById('audioVisualizer');
    this.statusMessage = document.getElementById('statusMessage');
    this.responseAudio = document.getElementById('responseAudio');
    this.avatarGlow = document.getElementById('avatarGlow');
    this.meymeAvatar = document.getElementById('meymeAvatar');
    this.visualizerBars = document.querySelectorAll('.visualizer-bar');
  }

  initializeSession() {
    const urlParams = new URLSearchParams(window.location.search);
    this.sessionId = urlParams.get('session_id');
    if (!this.sessionId) {
      this.sessionId = crypto.randomUUID();
      window.history.replaceState({}, '', `?session_id=${this.sessionId}`);
    }
  }

  bindEvents() {
    this.voiceButton.addEventListener('click', () => this.toggleRecording());
    this.responseAudio.addEventListener('ended', () => this.onAudioResponseEnded());
    this.responseAudio.addEventListener('loadstart', () => this.onAudioLoadStart());
    this.responseAudio.addEventListener('canplay', () => this.onAudioCanPlay());
  }

  showInitialStatus() {
    this.updateStatus('Press the mic button to start talking with Meyme!', '');
  }

  async toggleRecording() {
    // Don't allow interaction when processing
    if (this.isProcessing) {
      return;
    }
    
    if (this.isRecording) {
      this.stopRecording();
    } else {
      await this.startRecording();
    }
  }

  async startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      this.setupAudioAnalysis(stream);
      this.setupMediaRecorder(stream);
      
      this.recorder.start();
      this.isRecording = true;
      
      this.updateUIForRecording();
      this.updateStatus('🎙️ Listening...', 'listening');
      this.startAudioVisualization();
      
    } catch (error) {
      console.error('Error starting recording:', error);
      this.updateStatus('❌ Microphone access denied. Please allow microphone permissions.', 'error');
    }
  }

  setupAudioAnalysis(stream) {
    this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    this.analyser = this.audioContext.createAnalyser();
    const source = this.audioContext.createMediaStreamSource(stream);
    
    source.connect(this.analyser);
    this.analyser.fftSize = 256;
    const bufferLength = this.analyser.frequencyBinCount;
    this.dataArray = new Uint8Array(bufferLength);
  }

  setupMediaRecorder(stream) {
    this.recorder = new MediaRecorder(stream);
    this.audioChunks = [];
    
    this.recorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        this.audioChunks.push(event.data);
      }
    };
    
    this.recorder.onstop = () => this.handleRecordingStop();
  }

  stopRecording() {
    if (this.recorder && this.isRecording) {
      this.recorder.stop();
      this.isRecording = false;
      this.updateUIForStopped();
      this.stopAudioVisualization();
      
      // Stop all tracks to release microphone
      if (this.recorder.stream) {
        this.recorder.stream.getTracks().forEach(track => track.stop());
      }
    }
  }

  async handleRecordingStop() {
    const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
    await this.sendAudioToServer(audioBlob);
  }

  startProcessing() {
    this.isProcessing = true;
    this.voiceButton.classList.add('processing');
    this.voiceButton.disabled = true;
    this.meymeAvatar.classList.add('processing');
    // Keep the microphone icon but add processing class for animation
    this.micIcon.classList.add('processing');
  }

  stopProcessing() {
    this.isProcessing = false;
    this.voiceButton.classList.remove('processing');
    this.voiceButton.disabled = false;
    this.meymeAvatar.classList.remove('processing');
    this.micIcon.classList.remove('processing');
    // Reset to normal mic icon
    this.micIcon.className = 'fas fa-microphone';
  }

  async sendAudioToServer(audioBlob) {
    // Start processing state
    this.startProcessing();
    this.updateStatus('🧠 Meyme is thinking<span class="loading-dots"></span>', 'thinking');
    
    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'recording.webm');
    
    try {
      const response = await fetch(`/agent/chat/${this.sessionId}`, {
        method: 'POST',
        body: formData
      });
      
      if (response.headers.get('X-Error') === 'true') {
        // Fallback audio handling
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        this.responseAudio.src = audioUrl;
        this.responseAudio.play();
        this.updateStatus('I\'m having trouble connecting right now.', 'error');
        this.stopProcessing();
        return;
      }
      
      const data = await response.json();
      
      if (response.ok && data.audio_url) {
        this.updateStatus(`💬 "${data.text}"`, '');
        this.responseAudio.src = data.audio_url;
        this.responseAudio.play();
        this.activateAvatarGlow();
        this.stopProcessing();
      } else {
        this.updateStatus('❌ Sorry, something went wrong. Please try again.', 'error');
        this.stopProcessing();
      }
      
    } catch (error) {
      console.error('Error sending audio:', error);
      this.updateStatus('❌ Connection error. Please check your internet and try again.', 'error');
      this.stopProcessing();
    }
  }


  updateUIForRecording() {
    this.voiceButton.classList.add('recording');
    this.micIcon.className = 'fas fa-stop';
    this.voiceRipples.style.display = 'block';
    this.audioVisualizer.classList.add('active');
  }

  updateUIForStopped() {
    this.voiceButton.classList.remove('recording');
    this.micIcon.className = 'fas fa-microphone';
    this.voiceRipples.style.display = 'none';
    this.audioVisualizer.classList.remove('active');
  }

  startAudioVisualization() {
    const animate = () => {
      if (!this.isRecording) return;
      
      this.analyser.getByteFrequencyData(this.dataArray);
      
      // Update visualizer bars based on frequency data
      this.visualizerBars.forEach((bar, index) => {
        const dataIndex = Math.floor((index / this.visualizerBars.length) * this.dataArray.length);
        const value = this.dataArray[dataIndex];
        const height = Math.max(20, (value / 255) * 60);
        bar.style.height = `${height}px`;
      });
      
      this.animationId = requestAnimationFrame(animate);
    };
    
    animate();
  }

  stopAudioVisualization() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
    
    // Reset visualizer bars
    this.visualizerBars.forEach(bar => {
      bar.style.height = '20px';
    });
    
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
  }

  activateAvatarGlow() {
    this.avatarGlow.classList.add('active');
    setTimeout(() => {
      this.avatarGlow.classList.remove('active');
    }, 3000);
  }

  onAudioResponseEnded() {
    // Auto-start listening after Meyme finishes speaking
    setTimeout(() => {
      if (!this.isRecording) {
        this.updateStatus('🎙️ Ready for your next message!', '');
        // Optional: Auto-restart recording
        // this.startRecording();
      }
    }, 1000);
  }

  onAudioLoadStart() {
    this.updateStatus('🔊 Playing response...', '');
  }

  onAudioCanPlay() {
    // Audio is ready to play
  }

  updateStatus(message, type = '') {
    this.statusMessage.innerHTML = message;
    this.statusMessage.className = `status-message show ${type}`;
    
    // Auto-hide status after delay (except for persistent messages)
    if (!message.includes('Press the mic') && !message.includes('Ready for')) {
      setTimeout(() => {
        if (!this.isRecording && !this.responseAudio.duration) {
          this.showInitialStatus();
        }
      }, 5000);
    }
  }

  // Utility method for adding visual feedback
  addRippleEffect(x, y) {
    const ripple = document.createElement('div');
    ripple.className = 'click-ripple';
    ripple.style.left = `${x}px`;
    ripple.style.top = `${y}px`;
    document.body.appendChild(ripple);
    
    setTimeout(() => {
      ripple.remove();
    }, 600);
  }
}

// Initialize the Meyme Voice Agent when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.meymeAgent = new MeymeVoiceAgent();
  
  // Add click ripple effect to voice button
  const voiceButton = document.getElementById('voiceButton');
  voiceButton.addEventListener('click', (e) => {
    const rect = voiceButton.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    window.meymeAgent.addRippleEffect(x, y);
  });
  
  // Add some Easter eggs
  const avatar = document.getElementById('meymeAvatar');
  let clickCount = 0;
  avatar.addEventListener('click', () => {
    // Add bounce animation
    avatar.classList.add('clicked');
    setTimeout(() => {
      avatar.classList.remove('clicked');
    }, 600);
    
    clickCount++;
    if (clickCount === 5) {
      window.meymeAgent.updateStatus('🐱 Meow! You found the secret! 🌸', '');
      clickCount = 0;
    }
  });
});

// Add some global keyboard shortcuts
document.addEventListener('keydown', (e) => {
  if (e.code === 'Space' && e.target === document.body) {
    e.preventDefault();
    if (window.meymeAgent) {
      window.meymeAgent.toggleRecording();
    }
  }
});
