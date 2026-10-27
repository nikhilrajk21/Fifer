<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { anonymousBrowserId, createTextRequest } from '../chat.js'
import { beginChat, chatConfig, chatContext, reviewChat, stopChat } from '../api.js'
import VoicePanel from './VoicePanel.vue'

defineEmits(['close', 'privacy'])
const config = ref(null), question = ref(''), fictional = ref(false), share = ref(false), preview = ref(null)
const busy = ref(false), ended = ref(false), error = ref(''), notice = ref(''), messages = ref([]), used = ref(0)
const transport = createTextRequest()
const voicePanel = ref(null)
const SESSION_KEY = 'fifer.chat-session.v1'
let browser = null, sessionId = null, operation = 0, contextOperation = 0, disposed = false

async function load() {
  const token = operation
  try {
    browser = anonymousBrowserId()
    const value = await chatConfig(browser)
    if (disposed || token !== operation) return
    config.value = value
    sessionId = sessionStorage.getItem(SESSION_KEY)
    if (sessionId) {
      try {
        const saved = await reviewChat(sessionId)
        if (disposed || token !== operation) return
        used.value = saved.chat_session.requests
        ended.value = saved.chat_session.status !== 'active'
        messages.value = saved.messages.map(item => ({ ...item, saved: true }))
      } catch { sessionId = null; sessionStorage.removeItem(SESSION_KEY) }
    }
  } catch { if (!disposed && token === operation) error.value = 'Chat setup unavailable. Browser storage and the backend are required; grounding and Emergency Support still work.' }
}

function stop(reason = 'Chat stopped on this tab.') {
  voicePanel.value?.stop()
  operation++
  contextOperation++
  transport.cancel()
  busy.value = false
  question.value = ''
  messages.value = []
  share.value = false
  preview.value = null
  notice.value = reason
  if (ended.value) return Promise.resolve()
  ended.value = true
  if (!sessionId || !config.value) return Promise.resolve()
  const token = operation
  return stopChat(sessionId, { browser_id: browser, history_epoch: config.value.history_epoch }).catch(() => {
    if (!disposed && token === operation) error.value = 'Chat stopped in this tab; the backend stop was not confirmed. Late replies remain hidden.'
  })
}
defineExpose({ stop })

async function changeSharing() {
  if (busy.value) { stop('Sharing changed; pending reply cancelled. Start a new chat to continue.'); return }
  preview.value = null
  const token = ++contextOperation
  if (share.value) {
    try {
      const value = await chatContext()
      if (token === contextOperation && share.value && !ended.value && !disposed) preview.value = value
    } catch { if (token === contextOperation) { share.value = false; error.value = 'Context preview unavailable. Nothing will be shared.' } }
  }
}

async function newChat() {
  const stopping = stop('Previous chat stopped. A new chat still uses the same daily browser quota.')
  const token = operation
  await stopping
  if (disposed || token !== operation) return
  operation++
  sessionStorage.removeItem(SESSION_KEY)
  sessionId = null
  used.value = 0
  fictional.value = false
  ended.value = false
  error.value = ''
  try {
    const value = await chatConfig(browser)
    if (!disposed && operation === token + 1) config.value = value
  }
  catch { config.value = null; error.value = 'Chat unavailable. No retry was made.' }
}

async function send() {
  if (busy.value || ended.value || !config.value || !fictional.value || !question.value.trim()) return
  const token = ++operation, text = question.value.trim(), sharing = share.value && !!preview.value
  busy.value = true
  error.value = ''
  notice.value = ''
  try {
    if (!sessionId) {
      const started = await beginChat({ browser_id: browser, history_epoch: config.value.history_epoch })
      // Stop/navigation during creation must also close that server session.
      if (token !== operation || disposed) {
        void stopChat(started.id, { browser_id: browser, history_epoch: config.value.history_epoch }).catch(() => {})
        return
      }
      sessionId = started.id
      sessionStorage.setItem(SESSION_KEY, sessionId)
    }
    const result = await transport.send(`/api/chat/sessions/${sessionId}/messages`, {
      browser_id: browser, history_epoch: config.value.history_epoch, request_id: crypto.randomUUID(),
      question: text, fictional: true, share_context: sharing,
    })
    if (result.cancelled || token !== operation || disposed) return
    messages.value.push({ role: 'user', content: text, saved: result.saved },
      { role: 'assistant', content: result.answer, saved: result.saved, sources: result.sources, fallback: result.fallback })
    used.value = result.quota.session_used
    config.value.browser_used = result.quota.browser_used
    config.value.utc_day = result.quota.utc_day
    question.value = ''
    notice.value = result.saved ? 'Fictional question and reply saved locally until Delete/Clear.'
      : result.save_error || 'Messages were not saved. Only in-scope fictional messages with saving ON can be retained.'
    if (result.save_error) error.value = result.save_error
  } catch (failure) {
    if (token === operation && !disposed) error.value = `${failure.message} Grounding and Emergency Support remain available.`
  } finally { if (token === operation) busy.value = false }
}

onMounted(load)
onUnmounted(() => { stop('Chat closed.'); disposed = true })
</script>

<template>
  <p class="eyebrow">Optional text assistant and voice mock</p>
  <h1 id="activity-heading" tabindex="-1">Chat</h1>
  <p class="intro-copy">Fictional, non-emergency questions about Fifer's grounding skill and app usage only. Do not enter personal disclosures, sensory narratives, audio or transcripts.</p>
  <p v-if="config?.mode === 'gemini'" class="chat-mode"><strong>Gemini text assistant configured.</strong> Responses remain limited to reviewed Fifer content. Optional voice below is still a separate local synthetic-tone mock.</p>
  <p v-else class="chat-mode"><strong>Mock responses from curated Fifer content. No Gemini calls.</strong> Planned text model: gemini-2.5-flash. Optional Gemini Live voice controls below use a separate local synthetic-tone mock.</p>
  <p v-if="config" class="gentle-note">Attempts: {{ used }}/5 this chat; {{ config.browser_used }}/20 this browser on {{ config.utc_day }} (UTC). Failed attempts count. Requests have a 15-second timeout and no automatic retries. Output allowance: 300 tokens; current mock uses a shorter curated paragraph.</p>
  <p class="gentle-note">The browser ID is anonymous, not a verified person. Clearing browser data can reset it. These quotas are not a dollar spending cap.</p>
  <p v-if="config" class="gentle-note">Message saving is {{ config.message_opt_in ? 'ON' : 'OFF' }} in local privacy settings. Saving and context sharing are separate choices.</p>
  <button class="text-button" @click="$emit('privacy')">Review history and message-saving settings</button>
  <label class="chat-toggle"><input type="checkbox" v-model="share" :disabled="ended" @change="changeSharing" /> Share local completed-session context with this assistant (OFF by default)</label>
  <p class="gentle-note">If enabled, only the local completed-session count, latest completed skill and its optional check-in are supplied. No profile exists. Sensory text and prior chat messages are never retrieved or supplied as context.</p>
  <dl v-if="share && preview" class="chat-context">
    <dt>Completed sessions</dt><dd>{{ preview.completed_sessions }}</dd>
    <dt>Latest completed skill</dt><dd>{{ preview.recent_completed_skill || 'None available' }}</dd>
    <dt>Its optional check-in</dt><dd>{{ preview.latest_completed_checkin || 'Not answered' }}</dd>
  </dl>
  <ol class="chat-messages" aria-label="Text chat messages" aria-live="polite">
    <li v-for="(message,index) in messages" :key="index"><strong>{{ message.role === 'user' ? 'Fictional question' : (config?.mode === 'gemini' ? 'Fifer text assistant' : 'Local mock assistant') }}</strong>
      <p>{{ message.content }}</p><small>{{ message.saved ? 'Saved locally' : 'Not saved' }}</small>
      <ul v-if="message.sources?.length" aria-label="Curated sources"><li v-for="source in message.sources" :key="source.id">{{ source.title }}</li></ul>
    </li>
  </ol>
  <p v-if="notice" class="gentle-note" role="status">{{ notice }}</p>
  <p v-if="error" class="history-error" role="status">{{ error }}</p>
  <form @submit.prevent="send">
    <label class="chat-label" for="chat-question">Fictional question about Fifer (optional)</label>
    <textarea id="chat-question" v-model="question" maxlength="500" rows="3" :disabled="busy || ended || !config" autocomplete="off" spellcheck="false"></textarea>
    <label class="chat-toggle"><input type="checkbox" v-model="fictional" :disabled="busy || ended" /> This is a fictional, non-emergency app/skill question with no personal or sensory narrative.</label>
    <div class="chat-actions">
      <button class="button primary" type="submit" :disabled="busy || ended || !config || !fictional || !question.trim() || used >= 5 || config.browser_used >= 20">{{ busy ? 'Waiting for text assistant…' : 'Send question' }}</button>
      <button class="button quiet" type="button" @click="stop()">Stop chat</button>
      <button class="button secondary" type="button" @click="newChat" :disabled="busy || !config">New chat</button>
    </div>
  </form>
  <section class="chat-voice" aria-label="Optional voice controls">
    <VoicePanel ref="voicePanel" embedded />
  </section>
  <p class="gentle-note">Chat messages are saved only under the existing opt-in rule, until Delete/Clear. Chat session/count metadata is retained until Delete/Clear. Anonymous daily quota counters remain through the UTC day even after history is cleared, and are removed on a later day's request. No automatic emergency contact or human monitoring.</p>
  <button class="text-button" @click="$emit('close')">Return to choices</button>
</template>

<style scoped>
.chat-mode{padding:14px;border:1px solid #c4bbd8;background:#f3eff8;border-radius:10px;margin-top:18px;font-size:.85rem}
.chat-toggle{display:flex;align-items:flex-start;gap:10px;font-size:.85rem;line-height:1.6;margin:20px 0}.chat-toggle input{margin-top:5px;flex-shrink:0}
.chat-label{display:block;margin-top:24px;font-size:.9rem;font-weight:600}textarea{display:block;width:100%;margin-top:10px;min-height:90px;resize:vertical;padding:12px;font:inherit;color:#25374a;background:#fbfcff;border:1px solid #9aaabd;border-radius:10px;scroll-margin-top:230px}
textarea:focus-visible,input:focus-visible{outline:3px solid #524579;outline-offset:4px}.chat-actions{display:flex;gap:10px;flex-wrap:wrap}.chat-context{font-size:.85rem}.chat-context dd{margin:0 0 10px}
.chat-messages{padding-left:20px;overflow-wrap:anywhere}.chat-messages>li{padding:16px 0;border-bottom:1px solid #d9deea;white-space:pre-wrap}.chat-messages small{color:#536478}.chat-messages ul{font-size:.8rem}
.chat-voice{margin-top:32px;padding-top:24px;border-top:1px solid #b9bfd1}
</style>
