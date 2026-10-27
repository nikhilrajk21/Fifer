<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import EmergencySupport from './components/EmergencySupport.vue'
import HistoryPanel from './components/HistoryPanel.vue'
import GroundingPrompt from './components/GroundingPrompt.vue'
import ChatPanel from './components/ChatPanel.vue'
import VoicePanel from './components/VoicePanel.vue'
import { CHECKINS, STEPS, createExperience, transition } from './grounding.js'
import { loadHistory, reviewSession, saveSession, setMessageOptIn, deleteSession, clearHistory, reviewChat, deleteChat } from './api.js'
import { newSessionRecord, sessionSnapshot, sessionPayload, restoreExperience, createSaveQueue } from './persistence.js'

const experience = ref(createExperience(performance.now()))
const connection = ref('checking')
const helpOpen = ref(false)
const heading = ref(null)
const history = ref(null)
const historyOpen = ref(false)
const chatOpen = ref(false)
const chatPanel = ref(null)
const voiceOpen = ref(false)
const voicePanel = ref(null)
const historyDetail = ref(null)
const historyBusy = ref(false)
const historyError = ref('')
const storageNotice = ref('')
const recentDismissed = ref(false)
const sync = ref({ status: 'idle', pending: 0, error: null })
let currentRecord = null
let historyRequest = 0
let checkpointTimer
let overlayReturnFocus = null
let disposed = false
const writer = createSaveQueue(async record => {
  try {
    if (record.history_epoch === null) {
      const loaded = history.value || await readHistory()
      record.history_epoch = loaded.settings.history_epoch
    }
    const saved = await saveSession(record.id, sessionPayload(record, record.history_epoch))
    if (saved.id !== record.id || saved.revision !== record.revision || saved.status !== record.status) {
      throw new Error('The local save acknowledgement did not match this activity. No save was confirmed.')
    }
    connection.value = 'ready'
    if (['completed', 'stopped'].includes(record.status)) {
      if (record.status === 'completed') recentDismissed.value = false
      try { await readHistory() } catch { /* Write succeeded; a failed history read is separate. */ }
    }
  } catch (error) {
    if (!error.status || error.status >= 500) connection.value = 'unavailable'
    throw error
  }
}, value => { sync.value = value })

const step = computed(() => STEPS.find(item => item.id === experience.value.screen))
const stepNumber = computed(() => STEPS.findIndex(item => item.id === experience.value.screen) + 1)
const selected = computed(() => step.value ? experience.value.selections[step.value.id] || [] : [])
const inActivity = computed(() => experience.value.started && !experience.value.finished)
const resumable = computed(() => history.value?.sessions.find(item => ['active', 'paused'].includes(item.status)))
const activeIndex = computed(() => experience.value.screen === 'checkin' ? 1 : STEPS.findIndex(item => item.id === experience.value.screen))
const nextLabel = computed(() => {
  const labels = { see: 'Continue to Feel', feel: 'Continue to check-in', checkin: 'Continue to Hear',
    hear: 'Continue to Smell', smell: 'Continue to Taste', taste: 'Continue to completion' }
  return labels[experience.value.screen] || ''
})

function act(type, value) {
  if (['SUPPORT', 'STOP', 'HOME', 'BEGIN', 'PAUSE'].includes(type)) voicePanel.value?.stop()
  if (['STOP', 'HOME', 'BEGIN'].includes(type)) voiceOpen.value = false
  if (['SUPPORT', 'STOP', 'HOME', 'BEGIN'].includes(type)) chatPanel.value?.stop('Chat stopped; pending replies will be ignored.')
  if (['STOP', 'HOME', 'BEGIN'].includes(type)) chatOpen.value = false
  const before = experience.value
  const now = performance.now()
  if ((type === 'SUPPORT' || type === 'PAUSE') && !experience.value.overlay) overlayReturnFocus = document.activeElement
  if (type === 'HOME' && inActivity.value) capture('STOP', before, transition(before, { type: 'STOP' }, now))
  const after = transition(before, { type, value }, now)
  if (type === 'BEGIN') currentRecord = newSessionRecord(crypto.randomUUID(), new Date().toISOString())
  experience.value = after
  // Support opens from static content immediately, without a save/read request.
  // Its elapsed time is captured on Return, Stop, or a later checkpoint.
  if (!['SELECT', 'WRITE', 'SUPPORT', 'HOME', 'DISMISS_RECENT'].includes(type)) capture(type, before, after)
  if (type === 'HOME') currentRecord = null
  if (type === 'DISMISS_RECENT') recentDismissed.value = true
  if (type === 'HOME' || type === 'BEGIN') helpOpen.value = false
  if (!['SUPPORT', 'CLOSE_SUPPORT'].includes(type)) historyOpen.value = false
  if (type === 'FINISH') nextTick(() => document.getElementById('activity-heading')?.focus())
}

function capture(type, before, after) {
  if (!currentRecord || ['completed', 'stopped'].includes(currentRecord.status)) return
  currentRecord = sessionSnapshot(currentRecord, before, after, type, new Date().toISOString())
  writer.enqueue({ ...currentRecord, history_epoch: history.value?.settings.history_epoch ?? null })
}

function checkpoint() {
  if (!inActivity.value || experience.value.overlay === 'support') return
  const before = experience.value
  experience.value = transition(before, { type: 'SNAPSHOT' }, performance.now())
  capture('CHECKPOINT', before, experience.value)
}

async function readHistory() {
  const number = ++historyRequest
  const result = await loadHistory()
  if (!disposed && number === historyRequest) history.value = result
  return result
}

async function refreshConnection() {
  connection.value = 'checking'
  try {
    await readHistory()
    if (!disposed) connection.value = 'ready'
    if (writer.pending) { checkpoint(); await writer.retry() }
  }
  catch { if (!disposed) connection.value = 'unavailable' }
}

function discardUnsaved() {
  writer.clear()
  currentRecord = null
  experience.value = createExperience(performance.now())
  historyOpen.value = false
  storageNotice.value = 'Pending tab-only changes discarded. No deletion of saved history was requested.'
  void refreshConnection()
}

function resumeSaved(record) {
  if (writer.pending) return
  currentRecord = { ...record }
  experience.value = restoreExperience(record, performance.now())
  historyOpen.value = false
  capture('PAUSE', experience.value, experience.value)
}

async function openHistory() {
  voicePanel.value?.stop()
  voiceOpen.value = false
  const stopping = chatPanel.value?.stop('History opened; pending replies will be ignored.')
  chatOpen.value = false
  historyOpen.value = true
  historyDetail.value = null
  historyError.value = ''
  try { await stopping; await readHistory(); connection.value = 'ready' }
  catch { historyError.value = 'History unavailable. No change was made to saved data.'; connection.value = 'unavailable' }
}

async function historyAction(type, value) {
  if (!history.value) return
  historyBusy.value = true
  historyError.value = ''
  storageNotice.value = ''
  try {
    const epoch = history.value.settings.history_epoch
    if (type === 'review') historyDetail.value = await reviewSession(value)
    if (type === 'review-chat') historyDetail.value = await reviewChat(value)
    if (type === 'delete-chat') {
      await deleteChat(value, epoch)
      historyDetail.value = null
      await readHistory()
      storageNotice.value = 'Chat metadata and its saved messages deleted. Daily anonymous quota counters remain for this UTC day.'
    }
    if (type === 'optin') {
      const settings = await setMessageOptIn(value, epoch)
      history.value = { ...history.value, settings }
      storageNotice.value = `Message saving is now ${settings.message_opt_in ? 'ON' : 'OFF'}.`
    }
    if (type === 'delete') {
      if (writer.pending) throw new Error('Save or discard pending activity before deleting a session.')
      const settings = await deleteSession(value, epoch)
      writer.clear()
      historyDetail.value = null
      if (currentRecord?.id === value) currentRecord = null
      historyRequest++
      const sessions = history.value.sessions.filter(item => item.id !== value)
      history.value = { ...history.value, settings, sessions,
        recent_completed: sessions.filter(item => item.status === 'completed').sort((a,b) => b.ended_at.localeCompare(a.ended_at))[0] || null }
      storageNotice.value = 'Session and its linked conversations/messages deleted.'
    }
    if (type === 'clear') {
      const settings = await clearHistory(epoch)
      historyRequest++
      writer.clear()
      currentRecord = null
      experience.value = createExperience(performance.now())
      history.value = { settings, sessions: [], chats: [], recent_completed: null }
      historyDetail.value = null
      storageNotice.value = 'All session/message history cleared. Message saving is OFF; today’s anonymous text and voice quota counters remain.'
      nextTick(() => document.getElementById('activity-heading')?.focus())
    }
  } catch (error) {
    historyError.value = error.status === 409 ? 'History changed in another request. Close and reopen history before retrying.'
      : error.message || 'Request failed. No deletion or preference change was confirmed.'
  } finally { historyBusy.value = false }
}

watch([() => experience.value.screen, () => historyOpen.value, () => chatOpen.value, () => voiceOpen.value], async () => {
  await nextTick()
  document.getElementById('activity-heading')?.focus()
})
watch(() => experience.value.overlay, async value => {
  await nextTick()
  if (value) document.querySelector('[data-dialog-heading]')?.focus()
  else if (overlayReturnFocus?.isConnected && experience.value.screen !== 'stopped') overlayReturnFocus.focus()
  else heading.value?.focus()
})

function handleKeys(event) {
  if (!experience.value.overlay) return
  if (event.key === 'Escape' && experience.value.overlay === 'support') { event.preventDefault(); act('CLOSE_SUPPORT'); return }
  if (event.key !== 'Tab') return
  const dialog = document.querySelector('[role="dialog"]')
  const elements = [...dialog.querySelectorAll('button:not([disabled]), a[href], [tabindex="0"]')]
  const first = elements[0], last = elements.at(-1)
  if (event.shiftKey && (document.activeElement === first || !elements.includes(document.activeElement))) {
    event.preventDefault(); last?.focus()
  } else if (!event.shiftKey && (document.activeElement === last || !elements.includes(document.activeElement))) {
    event.preventDefault(); first?.focus()
  }
}

onMounted(() => {
  refreshConnection()
  window.addEventListener('keydown', handleKeys)
  checkpointTimer = setInterval(() => { if (writer.pending === 0) checkpoint() }, 5000)
})
onUnmounted(() => { disposed = true; clearInterval(checkpointTimer); window.removeEventListener('keydown', handleKeys) })
</script>

<template>
  <div class="application-shell" :inert="experience.overlay ? true : undefined">
    <a class="skip-link" href="#main-content">Skip to activity</a>
    <header class="site-header">
      <a class="brand" href="#" aria-label="Fifer start choices" @click.prevent="act('HOME')">
        <svg class="brand-mark" viewBox="0 0 40 40" aria-hidden="true">
          <path d="M8 24c5-13 19-13 24 0M12 28c4-9 12-9 16 0M16 32c2-4 6-4 8 0" />
        </svg>
        <span>fifer<span class="brand-dot">.</span><small class="brand-subtitle">Coursework prototype</small></span>
      </a>
      <span class="header-note">A moment, at your pace.</span>
      <button class="button support-button" @click="act('SUPPORT')">
        <span aria-hidden="true" class="support-symbol">+</span> Emergency Support
      </button>
    </header>

    <main id="main-content" class="workspace">
      <aside class="journey-panel">
        <p class="eyebrow">5–4–3–2–1 grounding</p>
        <h2>One thing<br />at a time.</h2>
        <p class="aside-copy">Notice what is already around you.<br />There is nothing to get right.</p>
        <ol class="journey-list" aria-label="Sensory categories">
          <li v-for="(item, index) in STEPS" :key="item.id"
              :class="{ current: activeIndex === index, passed: activeIndex > index || experience.screen === 'complete' }"
              :aria-current="activeIndex === index ? 'step' : undefined">
            <span class="step-number">{{ item.count }}</span>
            <span>{{ item.name }}</span>
            <span class="step-line" aria-hidden="true"></span>
          </li>
        </ol>
        <div class="aside-footer"><span class="small-orbit" aria-hidden="true"></span> Sensory selections are never stored.</div>
      </aside>

      <div class="activity-column">
        <div v-if="connection === 'unavailable'" class="connection-message" role="status">
          <div><strong>Connection unavailable.</strong> The activity and Emergency Support still work.</div>
          <button class="text-button" @click="refreshConnection">Retry connection</button>
        </div>

        <div class="save-message" :class="{ 'save-pending': sync.status === 'unsaved' }" role="status" aria-live="polite">
          <span v-if="sync.status === 'saving'">Saving session metadata…</span>
          <span v-else-if="sync.status === 'saved'">Session metadata saved locally at the last checkpoint.</span>
          <span v-else-if="sync.status === 'unsaved'"><strong>Unsaved changes.</strong> {{ sync.error?.status === 409 ? 'History changed or was cleared; these updates were not saved.' : 'Keep this tab open and retry. Reloading can lose unsaved changes.' }}</span>
          <span v-else>Session metadata is stored locally when available. Sensory selections are never saved.</span>
          <div v-if="sync.status === 'unsaved'" class="history-actions">
            <button class="text-button" @click="refreshConnection">Retry saving</button>
            <button class="text-button" @click="discardUnsaved">Discard unsaved changes</button>
          </div>
        </div>
        <p v-if="storageNotice" class="storage-notice" role="status">{{ storageNotice }}</p>

        <section class="activity-card" aria-labelledby="activity-heading">
          <HistoryPanel v-if="historyOpen" :history="history" :detail="historyDetail" :busy="historyBusy" :pending="sync.pending" :error="historyError"
            @close="historyOpen = false" @review="historyAction('review', $event)" @resume="resumeSaved"
            @delete="historyAction('delete', $event)" @clear="historyAction('clear')" @optin="historyAction('optin', $event)"
            @review-chat="historyAction('review-chat', $event)" @delete-chat="historyAction('delete-chat', $event)" />
          <ChatPanel v-else-if="chatOpen" ref="chatPanel" @close="chatOpen = false" @privacy="openHistory" />
          <VoicePanel v-else-if="voiceOpen" ref="voicePanel" @close="voiceOpen = false" />
          <template v-else-if="experience.screen === 'start'">
            <p class="eyebrow">A place to begin</p>
            <h1 id="activity-heading" ref="heading" tabindex="-1">What would you<br class="desktop-break" /> like to do?</h1>
            <p class="intro-copy">Choose a short sensory activity, or take a moment before you begin.</p>
            <button class="start-choice" @click="act('BEGIN')">
              <span class="choice-icon" aria-hidden="true">5</span>
              <span><strong>Begin grounding</strong><small>Five senses. One category at a time.</small></span>
              <span class="choice-arrow" aria-hidden="true">↗</span>
            </button>
            <button class="help-choice" :aria-expanded="helpOpen" aria-controls="help-description" @click="helpOpen = !helpOpen">
              <span>Help me choose</span><span aria-hidden="true">{{ helpOpen ? '−' : '+' }}</span>
            </button>
            <div v-if="helpOpen" id="help-description" class="help-description">
              Fifer offers one guided activity: 5–4–3–2–1 sensory grounding.
              You can notice each category, skip any answers, pause, or leave at any time.
            </div>
            <div v-if="history?.recent_completed && !recentDismissed" class="recent-card">
              <p class="eyebrow">Recently completed · Saved locally</p>
              <p>5–4–3–2–1 grounding</p>
              <div><button class="text-button" @click="act('BEGIN')">Use again</button>
                <button class="text-button" @click="act('DISMISS_RECENT')">Ignore suggestion</button></div>
            </div>
            <div v-if="resumable" class="recent-card">
              <p class="eyebrow">Unfinished saved activity · {{ resumable.current_step }}</p>
              <button class="text-button" :disabled="sync.pending > 0" @click="resumeSaved(resumable)">Resume saved activity</button>
              <p class="gentle-note">Opens paused. Time while this page was closed is not counted.</p>
            </div>
            <p class="gentle-note">No typing or personal disclosure is needed.</p>
            <button class="button secondary wide" @click="chatOpen = true">Chat · optional text assistant</button>
            <button class="button secondary wide" @click="voiceOpen = true">Voice · optional local mock</button>
            <button class="text-button" @click="openHistory">Local history and privacy</button>
          </template>

          <template v-else-if="step">
            <div class="step-heading-row"><p class="eyebrow">Category {{ stepNumber }} of 5 · {{ step.name }}</p>
              <span class="sense-count" aria-hidden="true">{{ step.count }}</span></div>
            <h1 id="activity-heading" ref="heading" tabindex="-1">{{ step.title }}</h1>
            <GroundingPrompt :step="step" :selected="selected" :response="experience.responses[step.id] || ''"
              @select="act('SELECT', $event)" @write="act('WRITE', $event)" />
          </template>

          <template v-else-if="experience.screen === 'checkin'">
            <p class="eyebrow">An optional check-in · After Feel</p>
            <h1 id="activity-heading" ref="heading" tabindex="-1">How are you feeling<br class="desktop-break" /> right now?</h1>
            <p class="intro-copy">Choose an answer if you like, or skip this check-in.</p>
            <div class="choices" role="group" aria-label="Optional check-in">
              <button v-for="choice in CHECKINS" :key="choice" class="sensory-choice"
                      :aria-pressed="experience.checkin === choice" @click="act('CHECKIN', choice)">
                <span class="selection-mark" aria-hidden="true">{{ experience.checkin === choice ? '✓' : '' }}</span>{{ choice }}
              </button>
            </div>
            <button class="text-button skip-checkin" @click="act('SKIP')">Skip check-in</button>
          </template>

          <template v-else-if="experience.screen === 'complete'">
            <div class="completion-orbit" aria-hidden="true">✓</div>
            <p class="eyebrow">{{ experience.finished ? 'Activity finished' : 'At the end of the sequence' }}</p>
            <h1 id="activity-heading" ref="heading" tabindex="-1">What would you<br class="desktop-break" /> like to do next?</h1>
            <p class="intro-copy">You reached the end. You can finish here or return to your choices.</p>
            <button v-if="!experience.finished" class="button primary wide" @click="act('FINISH')">Finish activity</button>
            <button class="button secondary wide" @click="act('HOME')">Return to choices</button>
            <button v-if="experience.finished" class="text-button" @click="chatOpen = true">Chat · optional text assistant</button>
            <button v-if="experience.finished" class="text-button" @click="voiceOpen = true">Voice · optional local mock</button>
            <p v-if="experience.finished" class="gentle-note">A recent-skill suggestion appears after completion is saved locally. It is always optional.</p>
            <button v-if="experience.finished" class="text-button" @click="openHistory">Local history and privacy</button>
          </template>

          <template v-else-if="experience.screen === 'stopped'">
            <p class="eyebrow">Activity stopped</p>
            <h1 id="activity-heading" ref="heading" tabindex="-1">You can leave<br class="desktop-break" /> it here.</h1>
            <p class="intro-copy">No explanation is needed. You can close this tab or return to your choices.</p>
            <button class="button secondary wide" @click="act('HOME')">Return to choices</button>
            <button class="text-button" @click="openHistory">Local history and privacy</button>
          </template>

          <div class="card-tail" aria-hidden="true"><span></span><span></span><span></span></div>
        </section>

        <div class="control-bar">
          <div class="user-controls">
            <button class="button quiet" :disabled="!inActivity" @click="act('PAUSE')">Pause</button>
            <button class="button quiet leave-button" @click="act('STOP')">Stop/Leave</button>
          </div>
          <div v-if="step || experience.screen === 'checkin'" class="advance-controls">
            <button v-if="step" class="text-button continue-empty" @click="act('SKIP')">Skip this step</button>
            <button class="button primary" @click="act('NEXT')">{{ nextLabel }} <span aria-hidden="true">→</span></button>
          </div>
        </div>
        <footer class="prototype-note">Coursework prototype · Fictional scenarios only</footer>
      </div>
    </main>
  </div>

  <div v-if="experience.overlay" class="dialog-backdrop">
    <EmergencySupport v-if="experience.overlay === 'support'" @close="act('CLOSE_SUPPORT')" @stop="act('STOP')" />
    <section v-else class="dialog" role="dialog" aria-modal="true" aria-labelledby="pause-title">
      <p class="eyebrow">Paused · Your place is kept</p>
      <h2 id="pause-title" tabindex="-1" data-dialog-heading>Take your time.</h2>
      <p class="intro-copy">Return to the same step whenever you choose.</p>
      <div class="dialog-actions">
        <button class="button primary" @click="act('RESUME')">Resume</button>
        <button class="button quiet" @click="act('STOP')">Stop/Leave</button>
      </div>
      <button class="button support-button dialog-support" @click="act('SUPPORT')">Emergency Support</button>
      <p class="prototype-note">Coursework prototype · Fictional scenarios only</p>
    </section>
  </div>
</template>

