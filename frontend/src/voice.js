// No credentials, transcripts, file uploads, provider SDK or content persistence.
export function createVoice({ socketFactory = url => new WebSocket(url), audioFactory,
  onChange = () => {}, later = setTimeout, cancel = clearTimeout } = {}) {
  let generation = 0, socket, audio, state = 'off', timers = new Set(), turns = 0, bytesOut = 0
  let confirmed = false, audioBlocked = false, turnComplete = false, drainTimer
  let captureOperation = 0, recoveryPending = false
  const canStart = () => ['off','stopped','error','limit'].includes(state)
  const emit = (value, message = '') => {
    state = value
    const connection = value === 'closing' ? 'closing' : value === 'error' ? 'failure'
      : value === 'permission' ? 'permission' : value === 'connecting' ? 'connecting'
      : confirmed ? 'active' : 'closed'
    onChange({ state, connection, setupConfirmed: confirmed, microphone: value === 'recording' ? 'active' : 'muted', audioBlocked, message, turns })
  }
  const timer = (fn, ms) => { const id = later(() => { timers.delete(id); fn() }, ms); timers.add(id); return id }
  const untimer = id => { cancel(id); timers.delete(id) }
  let waitTimer
  function stop(message = 'Voice stopped. Microphone and playback are off.', target = 'stopped') {
    if (target === 'stopped' && canStart() && !audio && !socket && !timers.size) return
    emit('closing', 'Closing microphone, playback and voice connection…')
    generation++
    captureOperation++
    for (const id of timers) cancel(id)
    timers.clear()
    confirmed = audioBlocked = turnComplete = false
    recoveryPending = false
    const oldAudio = audio, oldSocket = socket
    audio = socket = null
    try { oldAudio?.close() } catch { /* Finish socket cleanup even if a browser resource fails. */ }
    if (oldSocket) {
      oldSocket.onmessage = oldSocket.onopen = oldSocket.onerror = oldSocket.onclose = null
      try { if (oldSocket.readyState === 1) oldSocket.send(JSON.stringify({ type: 'stop' })) } catch {}
      try { oldSocket.close() } catch {}
    }
    emit(target, message)
  }
  function fail() { stop('Voice unavailable or a limit was reached. No retry was made. Grounding and Emergency Support still work.', 'error') }
  function send(type) { if (!socket || socket.readyState !== 1) throw new Error('Voice unavailable.'); socket.send(JSON.stringify({ type })) }
  function finishPlayback(token) {
    if (audioBlocked) return
    untimer(drainTimer)
    drainTimer = timer(() => {
      if (token === generation) {
        try { send('playback_done') } catch { fail() }
      }
    }, audio.remainingMs() + 30)
  }
  return {
    get state() { return state },
    stop,
    end: stop,
    async start(url, browserId) {
      if (!canStart()) return false // Ignore double clicks during permission/setup/active use.
      stop('', 'permission')
      const token = generation
      turns = bytesOut = 0
      audio = audioFactory()
      try {
        timer(() => { if (token === generation) fail() }, 300000)
        waitTimer = timer(fail, 10000)
        await audio.open()
        if (token !== generation) return
        const allowed = await audio.prepareMicrophone()
        if (token !== generation || !allowed) return
        emit('connecting', 'Microphone permission granted; muted while awaiting confirmed mock provider setup.')
        socket = socketFactory(url)
        socket.binaryType = 'arraybuffer'
        socket.onopen = () => { if (token === generation) socket.send(JSON.stringify({ type: 'start', browser_id: browserId, fictional: true })) }
        socket.onerror = () => { if (token === generation) fail() }
        socket.onclose = event => {
          if (token !== generation) return
          if (event?.code === 1000) stop('Voice connection ended. No reconnection was attempted.')
          else fail()
        }
        socket.onmessage = event => {
          if (token !== generation) return
          try {
            if (event.data instanceof ArrayBuffer) {
              if (!['waiting', 'speaking'].includes(state)) throw new Error()
              bytesOut += event.data.byteLength
              if (bytesOut > 15 * 24000 * 2) throw new Error()
              if (state === 'waiting') { untimer(waitTimer); waitTimer = timer(fail, 15000) }
              audioBlocked = audio.play(event.data) === false || audioBlocked
              emit('speaking', audioBlocked ? 'Assistant audio is blocked. Select Enable assistant audio; the bounded timeout still applies.' : 'Synthetic mock tone playing; this is not a Gemini answer.')
              return
            }
            const value = JSON.parse(event.data)
            if (value.type === 'ready') {
              if (!confirmed && (value.mode !== 'mock' || value.setup_confirmed !== true || state !== 'connecting')) throw new Error()
              confirmed = true
              turnComplete = false
              untimer(waitTimer)
              emit(turns >= 5 ? 'limit' : 'ready', turns >= 5 ? 'Five turns used. End this voice session.' : 'Mock provider setup confirmed. Microphone is muted.')
            } else if (value.type === 'recording') {
              if (state !== 'recording') throw new Error()
            } else if (value.type === 'waiting') {
              // Acknowledge only; local Send turn already moved state to waiting.
            } else if (value.type === 'turn_complete') {
              untimer(waitTimer)
              turnComplete = true
              emit('playback', audioBlocked ? 'Playback is blocked. Select Enable assistant audio; the timeout still applies.' : 'Finishing local playback; microphone is muted.')
              finishPlayback(token)
              waitTimer = timer(fail, 15000)
            } else if (value.type === 'interrupted' || value.type === 'closed') {
              untimer(drainTimer)
              audio.clearPlayback()
              stop('Voice ended; microphone and playback are off.')
            }
            else if (value.type === 'error') {
              if (value.code === 'limit') stop('A voice limit was reached. Microphone and playback are off. No retry was made.', 'limit')
              else fail()
            }
            else throw new Error()
          } catch { fail() }
        }
      } catch (error) {
        if (token !== generation) return
        if (error?.name === 'NotAllowedError') stop('Microphone permission was denied. Text Chat and Emergency Support remain available.', 'error')
        else fail()
      }
    },
    async enableAudio() {
      if (!confirmed || !audioBlocked || recoveryPending) return
      const token = generation
      recoveryPending = true
      try {
        await audio.enablePlayback()
        if (token !== generation) return
        audioBlocked = false
        emit(state, 'Assistant audio enabled by your click. Microphone is muted.')
        if (turnComplete) finishPlayback(token)
      } catch { if (token === generation) fail() }
      finally { if (token === generation) recoveryPending = false }
    },
    async talk() {
      if (state !== 'ready' || turns >= 5) return
      const token = generation
      const capture = ++captureOperation
      emit('permission', 'Requesting microphone permission. Use only fictional app-help audio.')
      try {
        const ok = await audio.record(pcm => {
          if (token !== generation || capture !== captureOperation || state !== 'recording') return
          try {
            if (socket.bufferedAmount > 32000) throw new Error()
            socket.send(pcm)
          } catch { fail() }
        })
        if (token !== generation || capture !== captureOperation || !ok) return
        turns++; bytesOut = 0
        turnComplete = false
        send('activity_start')
        emit('recording', 'Microphone audio goes to the local mock only; it is discarded, not recorded.')
        waitTimer = timer(() => { this.endTurn() }, 20000)
      } catch { if (token === generation && capture === captureOperation) fail() }
    },
    mute() {
      captureOperation++
      if (!confirmed || !audio) return
      // Muting idle/waiting/speaking/playback never touches playback or sockets.
      if (state !== 'recording') {
        audio.stopRecording()
        if (state === 'permission') emit('ready', 'Microphone is muted. Voice session remains open.')
        return
      }
      untimer(waitTimer)
      audio.stopRecording()
      try {
        emit('waiting', 'Waiting for a local synthetic test tone. No Gemini call is made.')
        send('activity_end')
        waitTimer = timer(fail, 15000)
      } catch { fail() }
    },
    endTurn() { this.mute() },
    unmute() { return this.talk() },
  }
}
