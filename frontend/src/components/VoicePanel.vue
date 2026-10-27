<script setup>
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { anonymousBrowserId } from '../chat.js'
import { createBrowserAudio } from '../audio/pcm.js'
import { createVoice } from '../voice.js'

defineEmits(['close'])
defineProps({ embedded: { type: Boolean, default: false } })
const fictional = ref(false), current = ref({ state: 'off', connection: 'closed', setupConfirmed: false, microphone: 'muted', audioBlocked: false, message: '', turns: 0 })
const client = createVoice({ audioFactory: () => createBrowserAudio({ base: import.meta.env.BASE_URL }), onChange: value => { current.value = value } })
function start() {
  if (!fictional.value) return
  try {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    void client.start(`${protocol}//${location.host}/api/voice`, anonymousBrowserId())
  } catch { client.stop('Browser identity or voice is unavailable.', 'error') }
}
function stop() { client.end() }
function hidden() { if (document.hidden) stop() }
watch(() => current.value.state, async () => {
  const focused = document.activeElement
  await nextTick()
  if (!focused?.isConnected || document.activeElement === document.body) document.getElementById('voice-status')?.focus()
})
onMounted(() => { document.addEventListener('visibilitychange', hidden); window.addEventListener('pagehide', stop) })
onUnmounted(() => { stop(); document.removeEventListener('visibilitychange', hidden); window.removeEventListener('pagehide', stop) })
defineExpose({ stop })
</script>

<template>
  <p class="eyebrow">Optional voice · Local mock only</p>
  <h2 v-if="embedded">Voice in Chat</h2>
  <h1 v-else id="activity-heading" tabindex="-1">Try the voice controls</h1>
  <p class="intro-copy">No Gemini call is made. The local mock discards microphone audio and plays a short synthetic test tone. It does not understand or answer speech.</p>
  <p class="gentle-note">Future target: Gemini Live gemini-3.8-live. Text Chat stays separate. Fictional, non-emergency Fifer app-help only; no personal disclosures. No audio or transcripts are saved. Voice never runs during grounding.</p>
  <p class="gentle-note">Start requests microphone permission (audio only). The microphone stays muted until setup is confirmed and you choose Unmute. Voice context sharing is not enabled by the text sharing checkbox.</p>
  <label class="voice-consent"><input type="checkbox" v-model="fictional" :disabled="!['off','stopped','error'].includes(current.state)" /> I will use fictional, non-emergency app-help audio. Starting a mock session uses one daily voice slot.</label>
  <p id="voice-status" class="voice-status" tabindex="-1" role="status" aria-live="polite"><strong>Voice: {{ current.connection }} · Microphone: {{ current.microphone }}</strong><br />{{ current.state }} · {{ current.message || 'Microphone and playback are off.' }} Turns: {{ current.turns }}/5.</p>
  <div class="voice-actions">
    <button v-if="['off','stopped','error'].includes(current.state)" class="button primary" :disabled="!fictional" @click="start">Start mock voice</button>
    <button v-if="current.state === 'ready'" class="button primary" @click="client.unmute()">Unmute</button>
    <button v-if="current.state === 'recording'" class="button primary" @click="client.endTurn()">Send turn · microphone off</button>
    <button class="button quiet" :disabled="!current.setupConfirmed" @click="client.mute()">Mute</button>
    <button v-if="current.audioBlocked" class="button secondary" @click="client.enableAudio()">Enable assistant audio</button>
    <button class="button quiet" :disabled="['closed','failure'].includes(current.connection)" @click="stop">End</button>
    <button v-if="!embedded" class="text-button" @click="stop(); $emit('close')">Return to choices</button>
  </div>
  <p class="gentle-note">Mute stops microphone forwarding and ends the current manual input turn, not the voice session or assistant playback. Unmute begins the next turn after the response finishes. End stops microphone, playback and the connection immediately. Every accepted Start creates a fresh voice connection; there is no automatic reconnect.</p>
  <p class="gentle-note">Maximum 300 seconds, five turns, 20 seconds per utterance, 15 seconds response audio; two starts per anonymous browser per UTC day, including failed starts. No retries. Browser data clearing can bypass identity limits: this is not a per-person guarantee or dollar spending cap.</p>
  <p class="gentle-note">Only a hashed browser identity, UTC day and start count are saved for the quota. Today's count survives Clear; older counts are removed on a later day's voice start. Text saving opt-in never enables voice recording. Leaving, opening Support, or hiding the tab ends voice; restarting is explicit.</p>
</template>

<style scoped>
.voice-consent{display:flex;gap:12px;align-items:flex-start;line-height:1.6;margin:24px 0}.voice-consent input{margin-top:6px;flex-shrink:0}.voice-status{padding:16px;border:1px solid #a7abc6;border-radius:12px;background:#f1eef8;overflow-wrap:anywhere}.voice-actions{display:flex;gap:12px;flex-wrap:wrap}input:focus-visible{outline:3px solid #524579;outline-offset:4px}
</style>
