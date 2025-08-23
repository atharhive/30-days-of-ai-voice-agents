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
  let socketConnected = false;
  let accumulatedAudioChunks = []; // 🎵 DAY 21: Array to accumulate base64 audio chunks
  
  // 🎵 DAY 22: Audio playback management
  let playbackAudioContext = null;
  let audioQueue = [];
  let isPlayingAudio = false;
  let currentAudioSource = null;
  let playbackStartTime = 0;
  let totalPlaybackDuration = 0;

  const SAMPLE_RATE = 16000; // AssemblyAI required sample rate
  const BUFFER_SIZE = 4096; // Audio processing buffer size
  const PLAYBACK_SAMPLE_RATE = 44100; // Murf TTS audio sample rate

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
      statusMessage.textContent = '🎙️ Meyme is listening...';
        statusMessage.classList.add('show');
        
        // 🎵 DAY 22: Stop any ongoing audio playback when starting to record
        if (isPlayingAudio) {
          stopAudioPlayback();
          console.log('🎵 🛑 Stopped ongoing audio playback to start recording');
        }
        
        // 🎵 DAY 21: Clear accumulated audio chunks for new session
        accumulatedAudioChunks = [];
        console.log('🔌 ✅ WebSocket connection established');
        console.log('🎵 ✅ Ready for audio streaming');
        console.log('🧹 ✅ Cleared accumulated audio chunks for new recording session');
        console.log('🎙️ ✅ Microphone active and listening...');
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // 🎵 DAY 22: Handle audio chunk messages with SEAMLESS PLAYBACK
          if (data.type === 'audio_chunk') {
            console.log(`🎵 AUDIO CHUNK RECEIVED #${data.chunk_index}`);
            console.log('🎵' + '='.repeat(50));
            console.log(`📦 Chunk Size: ${data.chunk_size} base64 characters`);
            console.log(`📊 Total Chunks Received: ${data.total_chunks_received}`);
            console.log(`🔍 Base64 Preview: ${data.base64_audio.substring(0, 80)}${data.base64_audio.length > 80 ? '...' : ''}`);
            console.log('🎵' + '='.repeat(50));
            
            // Accumulate the audio chunk
            accumulatedAudioChunks.push(data.base64_audio);
            console.log(`📦 ✅ ACCUMULATED AUDIO CHUNKS: ${accumulatedAudioChunks.length} chunks stored`);
            console.log(`📦 ✅ Chunk #${data.chunk_index} successfully added to array`);
            
            // 🎵 DAY 22: SEAMLESS AUDIO PLAYBACK - Play chunk immediately as it arrives
            playAudioChunk(data.base64_audio, data.chunk_index);
            
            // Update status message to show audio streaming
            statusMessage.textContent = `🎵 Meyme is speaking...`;
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
            
            // 🎵 DAY 22: Assemble and play the complete audio from all chunks
            (async () => {
              try {
                console.log('🎵 🚀 ASSEMBLING COMPLETE AUDIO FROM ALL CHUNKS');
                statusMessage.textContent = '🎵 Meyme is speaking...';
                statusMessage.classList.remove('processing', 'turn-complete', 'partial');
                statusMessage.classList.add('speaking');
                
                if (accumulatedAudioChunks.length > 0) {
                  // Assemble all chunks into one complete audio file
                  await assembleAndPlayCompleteAudio(accumulatedAudioChunks);
                } else {
                  console.error('❌ No audio chunks to play');
                  statusMessage.textContent = '❌ No audio received';
                }
              } catch (error) {
                console.error('❌ Error playing complete audio:', error);
                statusMessage.textContent = '❌ Audio playback failed';
              }
            })();
            
            // Close WebSocket now that audio streaming is complete
            if (socket && socket.readyState === WebSocket.OPEN) {
              console.log('🔌 ✅ Closing WebSocket after audio streaming completion');
              socket.close();
            }
            
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
                statusMessage.textContent = '🤖 Meyme is thinking...';
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
                statusMessage.textContent = '🤖 Meyme is thinking...';
                statusMessage.classList.remove('turn-complete');
                statusMessage.classList.add('processing');
              }, 1500);
              
              // Clear after processing and get ready for next input
              // No longer needed - simplifying UI states
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
      
      // Signal end of turn to backend before closing
      if (socket && socket.readyState === WebSocket.OPEN) {
        try {
          socket.send(JSON.stringify({
            type: 'end_turn',
            message: 'User finished speaking'
          }));
          console.log('🎯 ✅ Sent end_turn signal to backend');
        } catch (error) {
          console.error('❌ Error sending end_turn signal:', error);
        }
        
        // Keep the WebSocket open for audio streaming response
        // We'll close it after audio streaming completes or timeout
        console.log('🔌 ℹ️ WebSocket kept open for audio streaming response');
        
        // Set a timeout to close the connection if no audio response comes
        setTimeout(() => {
          if (socket && socket.readyState === WebSocket.OPEN) {
            console.log('⏰ 🔌 Closing WebSocket after timeout (no audio response)');
            socket.close();
          }
        }, 30000); // 30 second timeout for audio response
      }
      
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
      
      updateUIForStopped();
      statusMessage.textContent = '🤖 Meyme is thinking...';
      statusMessage.classList.remove('speaking', 'partial', 'turn-complete');
      statusMessage.classList.add('processing');
      
      console.log('🎯 ✅ Recording stopped and processing initiated');
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

  // 🎵 DAY 22: SEAMLESS AUDIO PLAYBACK FUNCTIONS
  
  // Initialize playback audio context
  async function initPlaybackAudioContext() {
    if (!playbackAudioContext) {
      try {
        playbackAudioContext = new (window.AudioContext || window.webkitAudioContext)({
          sampleRate: PLAYBACK_SAMPLE_RATE
        });
        
        // Resume context if it's suspended (required for some browsers)
        if (playbackAudioContext.state === 'suspended') {
          await playbackAudioContext.resume();
        }
        
        console.log('🎵 ✅ Playback AudioContext initialized:', {
          sampleRate: playbackAudioContext.sampleRate,
          state: playbackAudioContext.state
        });
        
      } catch (error) {
        console.error('❌ Error initializing playback audio context:', error);
        throw error;
      }
    }
    return playbackAudioContext;
  }
  
  // Convert base64 audio to AudioBuffer
  async function base64ToAudioBuffer(base64Audio, chunkIndex) {
    try {
      // Decode base64 to ArrayBuffer
      const binaryString = atob(base64Audio);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      // Initialize audio context if needed
      const context = await initPlaybackAudioContext();
      
      // For debugging, let's check if this looks like a valid WAV file
      const wavHeader = binaryString.substring(0, 12);
      const isValidWav = wavHeader.startsWith('RIFF') && wavHeader.includes('WAVE');
      
      if (!isValidWav && chunkIndex > 1) {
        // This chunk might be raw audio data, not a complete WAV file
        // For now, skip non-WAV chunks (most chunks after the first seem to be raw data)
        console.log(`🎵 ⚠️ Chunk #${chunkIndex} appears to be raw audio data, skipping playback`);
        throw new Error(`Chunk #${chunkIndex} is not a valid WAV file`);
      }
      
      // Decode audio data to AudioBuffer
      const audioBuffer = await context.decodeAudioData(bytes.buffer);
      
      console.log('🎵 ✅ Audio buffer decoded:', {
        duration: audioBuffer.duration.toFixed(3) + 's',
        sampleRate: audioBuffer.sampleRate,
        channels: audioBuffer.numberOfChannels,
        length: audioBuffer.length,
        isValidWav: isValidWav
      });
      
      return audioBuffer;
      
    } catch (error) {
      console.error(`❌ Error converting base64 to AudioBuffer (chunk #${chunkIndex}):`, error);
      throw error;
    }
  }
  
  // Play a single audio chunk seamlessly
  async function playAudioChunk(base64Audio, chunkIndex) {
    try {
      console.log(`🎵 🚀 PLAYING AUDIO CHUNK #${chunkIndex}`);
      console.log('🎵' + '-'.repeat(40));
      
      // Convert base64 to audio buffer
      const audioBuffer = await base64ToAudioBuffer(base64Audio, chunkIndex);
      
      // Initialize audio context
      const context = await initPlaybackAudioContext();
      
      // Create audio source
      const source = context.createBufferSource();
      source.buffer = audioBuffer;
      
      // Connect to destination (speakers)
      source.connect(context.destination);
      
      // Calculate when to start playing this chunk
      let startTime = context.currentTime;
      
      if (isPlayingAudio) {
        // If already playing, schedule this chunk to play after the previous one
        startTime = Math.max(context.currentTime, playbackStartTime + totalPlaybackDuration);
      } else {
        // First chunk - start immediately
        isPlayingAudio = true;
        playbackStartTime = context.currentTime;
        totalPlaybackDuration = 0;
        
        console.log('🎵 ✅ STARTING SEAMLESS AUDIO PLAYBACK PIPELINE');
      }
      
      // Update total duration
      totalPlaybackDuration += audioBuffer.duration;
      
      console.log(`🎵 📅 AUDIO TIMING:`);
      console.log(`   ⏱️  Start time: ${(startTime - context.currentTime).toFixed(3)}s from now`);
      console.log(`   ⏱️  Chunk duration: ${audioBuffer.duration.toFixed(3)}s`);
      console.log(`   ⏱️  Total pipeline duration: ${totalPlaybackDuration.toFixed(3)}s`);
      
      // Start playing at the calculated time
      source.start(startTime);
      
      // Handle playback completion
      source.onended = () => {
        console.log(`🎵 ✅ CHUNK #${chunkIndex} PLAYBACK COMPLETED`);
        
        // Check if this is the last chunk playing
        if (context.currentTime >= playbackStartTime + totalPlaybackDuration - 0.1) {
          console.log('🎵 🎉 ALL AUDIO CHUNKS PLAYBACK COMPLETED!');
          isPlayingAudio = false;
          playbackStartTime = 0;
          totalPlaybackDuration = 0;
          
          // Update UI to show conversation is ready
          setTimeout(() => {
            statusMessage.textContent = '🎙️ Press the mic button to speak';
            statusMessage.classList.remove('speaking', 'processing');
          }, 500);
        }
      };
      
      // Store reference to current source
      currentAudioSource = source;
      
      console.log(`🎵 ✅ CHUNK #${chunkIndex} QUEUED FOR SEAMLESS PLAYBACK`);
      console.log('🎵' + '-'.repeat(40));
      
    } catch (error) {
      console.error(`❌ Error playing audio chunk #${chunkIndex}:`, error);
      
      // Fallback - try to continue with next chunk
      console.log('⚠️  Attempting to continue with next audio chunk...');
    }
  }
  
  // Stop current audio playback (useful for interruptions)
  function stopAudioPlayback() {
    if (currentAudioSource) {
      try {
        currentAudioSource.stop();
        currentAudioSource = null;
      } catch (error) {
        console.log('Audio source already stopped');
      }
    }
    
    isPlayingAudio = false;
    playbackStartTime = 0;
    totalPlaybackDuration = 0;
    audioQueue = [];
    
    console.log('🎵 🛑 Audio playback stopped and reset');
  }
  
  // 🎵 DAY 22: Assemble and play complete audio from all chunks (Murf-style)
  async function assembleAndPlayCompleteAudio(audioChunks) {
    try {
      console.log('🎵 🧮 ASSEMBLING COMPLETE AUDIO FROM ALL CHUNKS (MURF STYLE)');
      console.log('🎵' + '='.repeat(70));
      console.log(`📦 Total chunks to assemble: ${audioChunks.length}`);
      
      if (audioChunks.length === 0) {
        throw new Error('No audio chunks to assemble');
      }
      
      // Stop any ongoing playback first
      if (isPlayingAudio) {
        stopAudioPlayback();
      }
      
      // Use Murf's recommended approach: combine WAV chunks
      await playCombinedWavChunks(audioChunks);
      
    } catch (error) {
      console.error('❌ Error assembling complete audio:', error);
      statusMessage.textContent = '❌ Audio assembly failed - trying fallback...';
      
      // Final fallback: try to play just the first chunk
      try {
        if (audioChunks.length > 0) {
          const fallbackBuffer = await base64ToAudioBuffer(audioChunks[0], 'EMERGENCY_FALLBACK');
          await playAssembledAudio(fallbackBuffer);
        }
      } catch (fallbackError) {
        console.error('❌ Even fallback failed:', fallbackError);
        statusMessage.textContent = '❌ Audio playback failed completely';
        
        // Reset state on complete failure
        isPlayingAudio = false;
        currentAudioSource = null;
        
        setTimeout(() => {
          statusMessage.textContent = '🎬 Press the mic button to try again';
        }, 3000);
      }
    }
  }
  
  // 🎵 DAY 22: Murf-style WAV chunk combination and playback
  async function playCombinedWavChunks(base64Chunks) {
    try {
      console.log('🎵 🔨 COMBINING WAV CHUNKS (MURF COOKBOOK APPROACH)');
      console.log('🎵' + '='.repeat(60));
      
      const pcmData = [];
      const SAMPLE_RATE = 44100;
      const NUM_CHANNELS = 1;
      const BIT_DEPTH = 16;
      
      // Process each chunk according to Murf's specification
      for (let i = 0; i < base64Chunks.length; i++) {
        console.log(`  🔧 Processing chunk ${i + 1}/${base64Chunks.length}`);
        
        try {
          const bytes = base64ToUint8Array(base64Chunks[i]);
          
          if (i === 0) {
            // First chunk: complete WAV file, skip 44-byte header to get PCM data
            console.log(`    📋 First chunk: complete WAV file`);
            console.log(`    📏 Original length: ${bytes.length} bytes`);
            
            // Verify it's a valid WAV
            const wavHeader = String.fromCharCode(...bytes.slice(0, 12));
            if (wavHeader.startsWith('RIFF') && wavHeader.includes('WAVE')) {
              const pcmPortion = bytes.slice(44); // Skip 44-byte WAV header
              console.log(`    🎵 PCM data extracted: ${pcmPortion.length} bytes`);
              pcmData.push(pcmPortion);
            } else {
              console.warn(`    ⚠️  First chunk doesn't appear to be valid WAV, using as-is`);
              pcmData.push(bytes);
            }
          } else {
            // Subsequent chunks: should be raw PCM data
            console.log(`    🎵 Chunk ${i + 1}: raw PCM data (${bytes.length} bytes)`);
            pcmData.push(bytes);
          }
        } catch (chunkError) {
          console.warn(`    ⚠️  Error processing chunk ${i + 1}:`, chunkError);
          // Skip problematic chunks and continue
          continue;
        }
      }
      
      // Combine all PCM chunks
      const totalPcmLength = pcmData.reduce((sum, chunk) => sum + chunk.length, 0);
      console.log(`📊 Total PCM data length: ${totalPcmLength.toLocaleString()} bytes`);
      
      const combinedPcm = new Uint8Array(totalPcmLength);
      let offset = 0;
      
      for (const chunk of pcmData) {
        combinedPcm.set(chunk, offset);
        offset += chunk.length;
      }
      
      console.log(`✅ Combined ${pcmData.length} chunks into ${combinedPcm.length.toLocaleString()} bytes of PCM`);
      
      // Create new WAV header for the combined PCM data
      const wavHeader = createWavHeader(combinedPcm.length, SAMPLE_RATE, NUM_CHANNELS, BIT_DEPTH);
      console.log(`📋 Created new WAV header (${wavHeader.length} bytes)`);
      
      // Combine header + PCM data
      const finalWav = new Uint8Array(wavHeader.length + combinedPcm.length);
      finalWav.set(wavHeader, 0);
      finalWav.set(combinedPcm, wavHeader.length);
      
      console.log(`🎵 Final WAV file: ${finalWav.length.toLocaleString()} bytes total`);
      console.log(`⏱️  Estimated duration: ${(combinedPcm.length / (SAMPLE_RATE * NUM_CHANNELS * (BIT_DEPTH / 8))).toFixed(2)} seconds`);
      
      // Create blob and object URL
      const blob = new Blob([finalWav], { type: 'audio/wav' });
      const audioUrl = URL.createObjectURL(blob);
      
      console.log('🎵' + '='.repeat(60));
      console.log('🎵 ▶️ STARTING MURF-STYLE COMBINED AUDIO PLAYBACK');
      
      // Get the audio element and set up playback
      const audioPlayer = document.getElementById('meymeAudioPlayer');
      if (!audioPlayer) {
        throw new Error('Audio player element not found');
      }
      
      // Set up the audio player
      audioPlayer.src = audioUrl;
      audioPlayer.style.display = 'none'; // Hide the actual player element
      
      // Update status
      statusMessage.textContent = `🎵 Meyme is speaking...`;
      statusMessage.classList.remove('processing', 'turn-complete', 'partial');
      statusMessage.classList.add('speaking');
      
      // Set up event listeners
      const onLoadedData = () => {
        console.log(`🎵 ✅ Audio loaded successfully, duration: ${audioPlayer.duration.toFixed(2)}s`);
        
        // Set playback state
        isPlayingAudio = true;
        
        // Auto-play the audio
        audioPlayer.play().then(() => {
          console.log('🎵 ▶️ MURF-STYLE COMBINED AUDIO PLAYBACK STARTED!');
        }).catch(autoPlayError => {
          console.log('⚠️  Auto-play blocked, user can manually play:', autoPlayError);
          statusMessage.textContent = '🎵 Click the audio player to hear Meyme\'s complete response';
        });
      };
      
      const onEnded = () => {
        console.log('🎵 🎉 MURF-STYLE COMBINED AUDIO PLAYBACK FINISHED!');
        
        // Clean up
        isPlayingAudio = false;
        URL.revokeObjectURL(audioUrl);
        audioPlayer.removeEventListener('loadeddata', onLoadedData);
        audioPlayer.removeEventListener('ended', onEnded);
        audioPlayer.removeEventListener('error', onError);
        
        // Update UI to show conversation is complete
        setTimeout(() => {
          accumulatedAudioChunks = [];
          statusMessage.textContent = '🎙️ Press the mic button to speak';
          statusMessage.classList.remove('speaking', 'processing');
          console.log('🧹 ✅ Ready for new conversation');
        }, 500);
      };
      
      const onError = (error) => {
        console.error('❌ Audio playback error:', error);
        statusMessage.textContent = '❌ Audio playback failed';
        statusMessage.classList.remove('speaking', 'processing');
        
        // Clean up
        isPlayingAudio = false;
        audioPlayer.classList.remove('show');
        URL.revokeObjectURL(audioUrl);
        audioPlayer.removeEventListener('loadeddata', onLoadedData);
        audioPlayer.removeEventListener('ended', onEnded);
        audioPlayer.removeEventListener('error', onError);
      };
      
      // Add event listeners
      audioPlayer.addEventListener('loadeddata', onLoadedData);
      audioPlayer.addEventListener('ended', onEnded);
      audioPlayer.addEventListener('error', onError);
      
      console.log('🎵 ⏳ Loading combined WAV into audio player...');
      
    } catch (error) {
      console.error('❌ Error in playCombinedWavChunks:', error);
      throw error;
    }
  }
  
  // 🎵 Helper function to play assembled audio buffer
  async function playAssembledAudio(audioBuffer) {
    try {
      const context = await initPlaybackAudioContext();
      
      // Create audio source
      const source = context.createBufferSource();
      source.buffer = audioBuffer;
      
      // Connect to destination (speakers)
      source.connect(context.destination);
      
      // Set playback state
      isPlayingAudio = true;
      playbackStartTime = context.currentTime;
      totalPlaybackDuration = audioBuffer.duration;
      currentAudioSource = source;
      
      console.log('🎵 🎤 FINAL ASSEMBLED AUDIO PLAYBACK INFO:');
      console.log(`   ⏱️  Total duration: ${audioBuffer.duration.toFixed(3)} seconds`);
      console.log(`   🔉 Sample rate: ${audioBuffer.sampleRate} Hz`);
      console.log(`   🎧 Channels: ${audioBuffer.numberOfChannels}`);
      console.log(`   📏 Audio samples: ${audioBuffer.length.toLocaleString()}`);
      console.log('🎵' + '='.repeat(60));
      
      // Update status
      statusMessage.textContent = `🎵 Meyme is speaking...`;
      
      // Start playing immediately
      source.start(0);
      console.log('🎵 ▶️ FINAL ASSEMBLED AUDIO PLAYBACK STARTED!');
      
      // Handle playback completion
      source.onended = () => {
        console.log('🎵 🎉 COMPLETE ASSEMBLED AUDIO PLAYBACK FINISHED!');
        
        isPlayingAudio = false;
        playbackStartTime = 0;
        totalPlaybackDuration = 0;
        currentAudioSource = null;
        
        // Update UI to show conversation is complete and ready for next input
        setTimeout(() => {
          // Clear accumulated chunks for next conversation
          accumulatedAudioChunks = [];
          statusMessage.textContent = '🎙️ Press the mic button to speak';
          statusMessage.classList.remove('speaking', 'processing');
          console.log('🧹 ✅ Cleared accumulated audio chunks for next conversation');
          console.log('🧹 ✅ Ready for new audio streaming session');
        }, 500);
      };
      
    } catch (error) {
      console.error('❌ Error in playAssembledAudio:', error);
      throw error;
    }
  }
  
  // 🎵 DAY 22: Helper function to convert base64 to Uint8Array
  function base64ToUint8Array(base64) {
    const binary = atob(base64);
    const len = binary.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
  }
  
  // 🎵 DAY 22: Helper function to create WAV header
  function createWavHeader(dataLength, sampleRate = 44100, numChannels = 1, bitDepth = 16) {
    const blockAlign = (numChannels * bitDepth) / 8;
    const byteRate = sampleRate * blockAlign;
    const buffer = new ArrayBuffer(44);
    const view = new DataView(buffer);
    
    function writeStr(offset, str) {
      for (let i = 0; i < str.length; i++) {
        view.setUint8(offset + i, str.charCodeAt(i));
      }
    }
    
    // RIFF chunk descriptor
    writeStr(0, 'RIFF');
    view.setUint32(4, 36 + dataLength, true); // file size - 8
    writeStr(8, 'WAVE');
    
    // fmt sub-chunk
    writeStr(12, 'fmt ');
    view.setUint32(16, 16, true); // sub-chunk size (16 for PCM)
    view.setUint16(20, 1, true); // audio format (1 = PCM)
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, byteRate, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, bitDepth, true);
    
    // data sub-chunk
    writeStr(36, 'data');
    view.setUint32(40, dataLength, true);
    
    return new Uint8Array(buffer);
  }
  
  // 🎵 DAY 22: Legacy function (kept for compatibility)
  async function playCompleteAudio(base64Audio) {
    console.log('⚠️  Using legacy playCompleteAudio - consider using assembleAndPlayCompleteAudio instead');
    const audioBuffer = await base64ToAudioBuffer(base64Audio, 'LEGACY');
    await playAssembledAudio(audioBuffer);
  }

  voiceButton.addEventListener('click', toggleRecording);
});
