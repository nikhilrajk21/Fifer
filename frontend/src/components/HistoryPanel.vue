<script setup>
defineProps({ history: Object, detail: Object, busy: Boolean, pending: Number, error: String })
defineEmits(['close', 'review', 'resume', 'delete', 'clear', 'optin', 'review-chat', 'delete-chat'])
const time = value => value ? new Date(value).toLocaleString() : 'Not ended'
const seconds = value => (value / 1000).toFixed(1) + ' s'
</script>

<template>
  <p class="eyebrow">Stored on this computer</p>
  <h1 id="activity-heading" tabindex="-1">Local history</h1>
  <p class="intro-copy">Session metadata and opted-in fictional messages stay until you delete or clear them.
    Sensory selections, personal narratives, and credentials are not stored.</p>
  <p class="gentle-note">Grounding does not create conversation messages. Only fictional messages are eligible for saving.</p>
  <p v-if="error" class="history-error" role="status">{{ error }}</p>
  <template v-if="history">
    <div class="history-preferences">
      <p><strong>Fictional message saving: {{ history.settings.message_opt_in ? 'ON' : 'OFF' }}</strong></p>
      <button class="button secondary" role="switch" :aria-checked="history.settings.message_opt_in"
              :disabled="busy" @click="$emit('optin', !history.settings.message_opt_in)">
        {{ history.settings.message_opt_in ? 'Turn message saving OFF' : 'Opt in to message saving' }}
      </button>
      <p class="gentle-note">OFF by default. Turning OFF stops future message saves; existing opted-in messages remain until deleted or cleared.</p>
    </div>
    <button class="button quiet" :disabled="busy" @click="$emit('clear')">Clear all local history</button>
    <p class="gentle-note">Clear all deletes sessions, check-ins, durations, conversations/messages, and recent-skill history, and resets message opt-in to OFF. It does not delete the application.</p>
    <p class="gentle-note">This includes mock-chat sessions and saved chat messages. Anonymous daily text and voice quota counters remain through their UTC day; older counters are removed on a later request for that feature. Clearing history does not reset today's quotas. Voice audio and transcripts are never saved.</p>
    <p v-if="!history.sessions.length" class="empty-history">No saved grounding sessions.</p>
    <ul class="history-list">
      <li v-for="record in history.sessions" :key="record.id">
        <p><strong>5–4–3–2–1 · {{ record.status }}</strong></p>
        <p>{{ time(record.started_at) }} · {{ record.current_step }}</p>
        <div class="history-actions">
          <button class="text-button" :disabled="busy" @click="$emit('review', record.id)">Review session</button>
          <button v-if="['active','paused'].includes(record.status)" class="text-button" :disabled="busy || pending > 0" @click="$emit('resume', record)">Resume saved activity</button>
          <button class="text-button" :disabled="busy || pending > 0" @click="$emit('delete', record.id)">Delete session</button>
        </div>
      </li>
    </ul>
    <ul v-if="history.chats?.length" class="history-list" aria-label="Mock chat history">
      <li v-for="chat in history.chats" :key="chat.id"><p><strong>Text chat · {{ chat.status }}</strong></p>
        <p>{{ time(chat.created_at) }} · {{ chat.requests }} attempts</p>
        <div class="history-actions"><button class="text-button" :disabled="busy" @click="$emit('review-chat',chat.id)">Review chat</button>
          <button class="text-button" :disabled="busy" @click="$emit('delete-chat',chat.id)">Delete chat</button></div>
      </li>
    </ul>
    <section v-if="detail?.chat_session" class="history-detail" aria-label="Reviewed mock chat">
      <h2>Mock chat details</h2><p>{{ time(detail.chat_session.created_at) }} · {{ detail.chat_session.status }} · {{ detail.chat_session.requests }} attempts</p>
      <p v-if="!detail.messages.length">No saved messages. Saving may have been OFF.</p>
      <ol class="message-list"><li v-for="(message,index) in detail.messages" :key="index"><strong>{{ message.role }}</strong> · {{ time(message.created_at) }}<p>{{ message.content }}</p></li></ol>
    </section>
    <section v-if="detail?.session" class="history-detail" aria-label="Reviewed session">
      <h2>Session details</h2>
      <dl>
        <dt>Fictional ID</dt><dd>{{ detail.session.id }}</dd>
        <dt>Skill / status</dt><dd>{{ detail.session.skill }} / {{ detail.session.status }}</dd>
        <dt>Start</dt><dd>{{ time(detail.session.started_at) }}</dd>
        <dt>End</dt><dd>{{ time(detail.session.ended_at) }}</dd>
        <dt>Saved step</dt><dd>{{ detail.session.current_step }}</dd>
        <dt>Optional check-in</dt><dd>{{ detail.session.checkin || 'Not answered' }}</dd>
        <dt>Setup / active</dt><dd>{{ seconds(detail.session.setup_ms) }} / {{ seconds(detail.session.active_ms) }}</dd>
        <dt>Pause / support</dt><dd>{{ seconds(detail.session.paused_ms) }} / {{ seconds(detail.session.support_ms) }}</dd>
      </dl>
      <h3>Opted-in fictional messages</h3>
      <p v-if="!detail.messages.length">No saved messages.</p>
      <ol class="message-list"><li v-for="message in detail.messages" :key="message.id">
        <strong>{{ message.role }}</strong> · {{ time(message.created_at) }}<p>{{ message.content }}</p>
      </li></ol>
    </section>
  </template>
  <button class="button secondary wide" @click="$emit('close')">Return to choices</button>
</template>
