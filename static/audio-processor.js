class AudioProcessor extends AudioWorkletProcessor {
  process(inputs, outputs, parameters) {
    const input = inputs[0];
    if (input.length > 0) {
      const inputData = input[0];
      const pcmData = new Int16Array(inputData.length);
      for (let i = 0; i < inputData.length; i++) {
        // Convert float32 to int16
        pcmData[i] = Math.max(-1, Math.min(1, inputData[i])) * 32767;
      }
      // Send the buffer to the main thread
      this.port.postMessage(pcmData.buffer, [pcmData.buffer]);
    }
    return true;
  }
}

registerProcessor("audio-processor", AudioProcessor);
