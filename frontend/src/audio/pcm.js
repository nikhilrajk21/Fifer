export { Downsampler, encodePCM } from '../../public/audio/voice-capture-worklet.js'

export function decodePCM(buffer) {
  if (!(buffer instanceof ArrayBuffer) || !buffer.byteLength || buffer.byteLength % 2) throw new Error('Invalid PCM audio.')
  const view = new DataView(buffer), samples = new Float32Array(buffer.byteLength / 2)
  for (let i = 0; i < samples.length; i++) samples[i] = view.getInt16(i * 2, true) / 32768
  return samples
}

export function createBrowserAudio({ Context = globalThis.AudioContext, media = globalThis.navigator?.mediaDevices,
  Worklet = globalThis.AudioWorkletNode, base = '/' } = {}) {
  let context, stream, source, worklet, recording = false, nextTime = 0
  let captureEpoch = 0
  const playing = new Set()
  let pending = [], pendingBytes = 0
  const release = action => { try { action() } catch { /* Release the other resources too. */ } }
  return {
    async open() {
      if (!Context || !media?.getUserMedia || !Worklet) throw new Error('Browser audio is unavailable.')
      context = new Context()
      // Autoplay blocking must not prevent permission/setup. Recovery is an
      // explicit user gesture via enablePlayback(), never an automatic retry.
      void context.resume().catch(() => {})
      await context.audioWorklet.addModule(base + 'audio/voice-capture-worklet.js')
    },
    async prepareMicrophone() {
      const epoch = captureEpoch, active = context
      const acquired = await media.getUserMedia({ audio: true, video: false })
      if (!context || context !== active || context.state === 'closed' || epoch !== captureEpoch) { acquired.getTracks().forEach(track => track.stop()); return false }
      stream = acquired
      stream.getTracks().forEach(track => { track.enabled = false })
      return true
    },
    async record(onFrame) {
      if (!stream && !await this.prepareMicrophone()) return false
      if (!context || context.state === 'closed') return false
      stream.getTracks().forEach(track => { track.enabled = true })
      source = context.createMediaStreamSource(stream)
      worklet = new Worklet(context, 'fifer-voice-capture')
      recording = true
      worklet.port.onmessage = event => { if (recording) onFrame(event.data) }
      source.connect(worklet)
      worklet.connect(context.destination) // Processor output is always silence.
      return true
    },
    stopRecording() {
      captureEpoch++ // A late permission result must not re-enable capture.
      recording = false
      const oldStream = stream, oldWorklet = worklet, oldSource = source
      stream = source = worklet = null
      oldStream?.getTracks().forEach(track => release(() => track.stop()))
      if (oldWorklet) {
        oldWorklet.port.onmessage = null
        release(() => oldWorklet.disconnect())
        release(() => oldWorklet.port.close())
      }
      release(() => oldSource?.disconnect())
    },
    play(pcm) {
      if (!context || context.state === 'closed') return
      const samples = decodePCM(pcm)
      if (context.state !== 'running') {
        if (pendingBytes + pcm.byteLength > 48000) throw new Error('Blocked audio queue exceeded one second.')
        pending.push(pcm)
        pendingBytes += pcm.byteLength
        return false
      }
      const start = Math.max(context.currentTime + .02, nextTime)
      if (start - context.currentTime + samples.length / 24000 > 1) throw new Error('Audio queue exceeded one second.')
      const buffer = context.createBuffer(1, samples.length, 24000)
      buffer.copyToChannel(samples, 0)
      const node = context.createBufferSource()
      node.buffer = buffer
      node.connect(context.destination)
      playing.add(node)
      node.onended = () => { playing.delete(node); node.disconnect() }
      node.start(start)
      nextTime = start + buffer.duration
      return true
    },
    async enablePlayback() {
      const active = context
      if (!active || active.state === 'closed') throw new Error('Audio is closed.')
      await active.resume()
      if (context !== active || active.state !== 'running') throw new Error('Audio playback is blocked.')
      const queued = pending
      pending = []; pendingBytes = 0
      for (const pcm of queued) this.play(pcm)
    },
    remainingMs() { return Math.max(0, (nextTime - (context?.currentTime || 0)) * 1000) },
    clearPlayback() {
      for (const node of playing) { node.onended = null; release(() => node.stop()); release(() => node.disconnect()) }
      playing.clear()
      pending = []; pendingBytes = 0
      nextTime = 0
    },
    close() {
      this.stopRecording()
      this.clearPlayback()
      const old = context
      context = null
      if (old && old.state !== 'closed') release(() => { void old.close().catch(() => {}) })
    },
  }
}
