// Meyme - Modern AI Voice Agent JavaScript
// Modified to send 16kHz, 16-bit, mono PCM audio via Web Audio API

document.addEventListener('DOMContentLoaded', () => {
  const voiceButton = document.getElementById('voiceButton');
  const micIcon = document.getElementById('micIcon');
  const statusMessage = document.getElementById('statusMessage');
  let isRecording = false;
  let audioContext = null;
  let mediaStreamSource = null;
  let processor = null;
  let socket = null;
  let accumulatedAudioChunks = []; // 🎵 DAY 21: Array to accumulate base64 audio chunks

  const SAMPLE_RATE = 16000; // AssemblyAI required sample rate
  const BUFFER_SIZE = 4096; // Audio processing buffer size

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
      audioContext = new (window.AudioContext || window.webkitAudioContext)();
      mediaStreamSource = audioContext.createMediaStreamSource(stream);

      // Create a ScriptProcessorNode to process audio samples
      // Deprecated, but widely supported. For modern apps, AudioWorkletNode is preferred.
      processor = audioContext.createScriptProcessor(BUFFER_SIZE, 1, 1); // bufferSize, inputChannels, outputChannels

      processor.onaudioprocess = (e) => {
        if (!isRecording || !socket || socket.readyState !== WebSocket.OPEN) {
          return;
        }

        // Get the audio data from the input buffer (first channel for mono)
        const inputData = e.inputBuffer.getChannelData(0);

        // Resample and convert to 16-bit PCM
        const downsampledBuffer = downsampleBuffer(inputData, audioContext.sampleRate, SAMPLE_RATE);
        const pcm16 = to16BitPCM(downsampledBuffer);

        // Send the 16-bit PCM data over the WebSocket
        socket.send(pcm16);
      };

      mediaStreamSource.connect(processor);
      processor.connect(audioContext.destination); // Connect to destination to keep the audio graph alive

      socket = new WebSocket(`ws://${window.location.host}/ws`);

      socket.onopen = () => {
        isRecording = true;
        updateUIForRecording();
        statusMessage.textContent = '🎙️ Listening...';
        statusMessage.classList.add('show');
        
        // 🎵 DAY 21: Clear accumulated audio chunks for new session
        accumulatedAudioChunks = [];
        console.log('🔌 ✅ WebSocket connection established');
        console.log('🎵 ✅ Ready for audio streaming');
        console.log('🧹 ✅ Cleared accumulated audio chunks for new recording session');
        console.log('🎤 ✅ Microphone active and listening...');
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // 🎵 DAY 21: Handle audio chunk messages
          if (data.type === 'audio_chunk') {
            console.log(`🎵 AUDIO CHUNK RECEIVED #${data.chunk_index}`);
            console.log('🎵' + '='.repeat(50));
            console.log(`📦 Chunk Size: ${data.chunk_size} base64 characters`);
            console.log(`📊 Total Chunks Received: ${data.total_chunks_received}`);
            console.log(`🔍 Base64 Preview: ${data.base64_audio.substring(0, 80)}${data.base64_audio.length > 80 ? '...' : ''}`);
            console.log(`📄 Full Base64 Audio:`, data.base64_audio);
            console.log('🎵' + '='.repeat(50));
            
            // Accumulate the audio chunk
            accumulatedAudioChunks.push(data.base64_audio);
            console.log(`📦 ✅ ACCUMULATED AUDIO CHUNKS: ${accumulatedAudioChunks.length} chunks stored`);
            console.log(`📦 ✅ Chunk #${data.chunk_index} successfully added to array`);
            
            // Update status message to show audio streaming
            statusMessage.textContent = `🎵 Receiving audio chunk ${data.chunk_index}...`;
            statusMessage.classList.remove('turn-complete', 'processing', 'speaking', 'partial');
            statusMessage.classList.add('speaking');
            
            return; // Don't process further
          }
          
          // 🎵 DAY 21: Handle audio completion message
          if (data.type === 'audio_complete') {
            console.log(`🎉 AUDIO STREAMING COMPLETE!`);
            console.log('🎉' + '='.repeat(50));
            console.log(`✅ Total Audio Chunks: ${data.total_chunks}`);
            console.log(`✅ Total Base64 Characters: ${data.total_base64_chars}`);
            console.log(`✅ Accumulated Chunks: ${data.accumulated_chunks}`);
            console.log(`✅ Audio Format: WAV (44.1kHz, Mono)`);
            console.log(`✅ Voice: en-US-amara (Conversational)`);
            console.log(`📦 All Accumulated Chunks:`, accumulatedAudioChunks);
            console.log('🎉' + '='.repeat(50));
            console.log(`🎵 ✅ AUDIO STREAMING PIPELINE SUCCESSFUL!`);
            
            // Update status message
            statusMessage.textContent = '🎵 Audio streaming complete!';
            statusMessage.classList.remove('speaking', 'processing', 'turn-complete', 'partial');
            
            // Clear accumulated chunks for next conversation
            setTimeout(() => {
              accumulatedAudioChunks = [];
              statusMessage.textContent = '🎤 Ready to listen...';
              console.log('🧹 ✅ Cleared accumulated audio chunks for next conversation');
              console.log('🧹 ✅ Ready for new audio streaming session');
            }, 3000);
            
            return; // Don't process further
          }
          
          // Handle different types of transcript messages
          if (data.type === 'transcript' && data.transcript) {
            if (data.is_partial) {
              // Real-time partial transcript - update immediately with lighter styling
              console.log(`📝 PARTIAL TRANSCRIPT: "${data.transcript}"`);
              statusMessage.textContent = data.transcript;
              statusMessage.classList.remove('turn-complete', 'processing');
              statusMessage.classList.add('speaking', 'partial');
            } else if (data.end_of_turn) {
              // Final transcript for this turn - more solid styling
              console.log(`✅ FINAL TRANSCRIPT: "${data.transcript}"`);
              console.log(`🎯 Turn completed - triggering AI response`);
              statusMessage.textContent = data.transcript;
              statusMessage.classList.remove('speaking', 'partial');
              statusMessage.classList.add('turn-complete');
              
              // Show processing AI response indicator
              setTimeout(() => {
                statusMessage.textContent = '🤖 Meyme is responding...';
                statusMessage.classList.remove('turn-complete');
                statusMessage.classList.add('processing');
              }, 1000);
            } else {
              // Regular transcript update
              console.log(`📝 TRANSCRIPT UPDATE: "${data.transcript}"`);
              statusMessage.textContent = data.transcript;
              statusMessage.classList.remove('turn-complete', 'processing', 'partial');
              statusMessage.classList.add('speaking');
            }
          } 
          else if (data.type === 'turn_end') {
            // Handle explicit turn end messages
            if (data.transcript && data.transcript.trim()) {
              statusMessage.textContent = data.transcript;
              statusMessage.classList.remove('speaking', 'partial');
              statusMessage.classList.add('turn-complete');
              
              // Show processing AI response indicator
              setTimeout(() => {
                statusMessage.textContent = '🤖 Meyme is responding...';
                statusMessage.classList.remove('turn-complete');
                statusMessage.classList.add('processing');
              }, 1500);
              
              // Clear after processing and get ready for next input
              setTimeout(() => {
                statusMessage.textContent = '🎤 Ready to listen...';
                statusMessage.classList.remove('processing');
              }, 8000); // Longer delay to account for AI processing time
            } else {
              statusMessage.textContent = '🎤 Listening...';
              statusMessage.classList.remove('speaking', 'processing', 'turn-complete', 'partial');
            }
          }
        } catch (e) {
          console.error('Error parsing WebSocket message:', e);
        }
      };

      socket.onclose = () => {
        console.log('🔌 WebSocket connection closed');
        console.log('🛑 Audio streaming session ended');
        stopRecording();
      };

      socket.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        console.error('🛑 Audio streaming interrupted');
        stopRecording();
      };

    } catch (error) {
      console.error('Error starting recording:', error);
      statusMessage.textContent = '❌ Microphone access denied. Please allow microphone permissions.';
    }
  };

  const stopRecording = () => {
    if (isRecording) {
      isRecording = false;
      if (processor) {
        processor.disconnect();
        processor = null;
      }
      if (mediaStreamSource) {
        mediaStreamSource.disconnect();
        mediaStreamSource = null;
      }
      if (audioContext) {
        audioContext.close();
        audioContext = null;
      }
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
      updateUIForStopped();
      statusMessage.textContent = 'Press the mic button to start talking with Meyme!';
    }
  };

  // Function to downsample audio buffer
  function downsampleBuffer(buffer, originalSampleRate, newSampleRate) {
    if (newSampleRate === originalSampleRate) {
      return buffer;
    }
    const ratio = originalSampleRate / newSampleRate;
    const newLength = Math.round(buffer.length / ratio);
    const result = new Float32Array(newLength);
    let offsetResult = 0;
    let offsetBuffer = 0;
    while (offsetResult < result.length) {
      const nextOffsetBuffer = Math.round((offsetResult + 1) * ratio);
      // Use average value for downsampling
      let accum = 0;
      let count = 0;
      for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
        accum += buffer[i];
        count++;
      }
      result[offsetResult] = accum / count;
      offsetResult++;
      offsetBuffer = nextOffsetBuffer;
    }
    return result;
  }

  // Function to convert Float32Array to 16-bit PCM (Int16Array)
  function to16BitPCM(input) {
    const dataLength = input.length * 2;
    const output = new Int16Array(dataLength / 2);
    for (let i = 0; i < input.length; i++) {
      let s = Math.max(-1, Math.min(1, input[i]));
      output[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return output.buffer; // Return as ArrayBuffer for WebSocket
  }

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
