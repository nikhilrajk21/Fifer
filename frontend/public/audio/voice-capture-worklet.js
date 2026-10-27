// Self-contained local AudioWorklet; also imported by focused Node tests.
// Streaming weighted averaging preserves boundaries across device-rate chunks.
export class Downsampler {
  constructor(inputRate, outputRate = 16000) {
    if (!Number.isFinite(inputRate) || inputRate < outputRate) throw new Error('Unsupported microphone sample rate.')
    this.ratio = inputRate / outputRate
    this.weight = 0
    this.sum = 0
  }
  push(samples) {
    const result = []
    for (const value of samples) {
      let remaining = 1
      while (remaining > 1e-9) {
        const used = Math.min(remaining, this.ratio - this.weight)
        this.sum += Math.max(-1, Math.min(1, value)) * used
        this.weight += used
        remaining -= used
        if (this.weight >= this.ratio - 1e-9) {
          result.push(this.sum / this.ratio)
          this.sum = this.weight = 0
        }
      }
    }
    return Float32Array.from(result)
  }
}

export function encodePCM(samples) {
  const buffer = new ArrayBuffer(samples.length * 2), view = new DataView(buffer)
  samples.forEach((sample, index) => {
    const value = Number.isFinite(sample) ? Math.max(-1, Math.min(1, sample)) : 0
    view.setInt16(index * 2, Math.round(value * (value < 0 ? 32768 : 32767)), true)
  })
  return buffer
}

if (typeof AudioWorkletProcessor !== 'undefined') {
  class VoiceCapture extends AudioWorkletProcessor {
    constructor() {
      super()
      this.converter = new Downsampler(sampleRate)
      this.pending = []
    }
    process(inputs) {
      // Output stays silent; the microphone is never played through speakers.
      const channels = inputs[0]
      if (channels?.length) {
        const mono = new Float32Array(channels[0].length)
        for (const channel of channels) channel.forEach((x, i) => { mono[i] += x / channels.length })
        for (const value of this.converter.push(mono)) this.pending.push(value)
        while (this.pending.length >= 320) {
          const pcm = encodePCM(this.pending.splice(0, 320))
          this.port.postMessage(pcm, [pcm]) // 20 ms at 16 kHz, PCM16LE.
        }
      }
      return true
    }
  }
  registerProcessor('fifer-voice-capture', VoiceCapture)
}
