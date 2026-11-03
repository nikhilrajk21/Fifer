// Browser identity contains no names or message content. It is not authentication.
export const TEXT_TIMEOUT_MS = 15000
const ID_KEY = 'fifer.browser-id.v1'

export function anonymousBrowserId(storage = localStorage, makeId = () => crypto.randomUUID()) {
  const existing = storage.getItem(ID_KEY)
  if (/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(existing || '')) return existing
  const id = makeId()
  storage.setItem(ID_KEY, id)
  return id
}

const SHARED_CONTEXT_KEYS = ['completed_sessions', 'recent_completed_skill', 'latest_completed_checkin']
const SHARED_CHECKINS = new Set(['A little better', 'About the same', 'A little harder', 'Not sure'])

// App-owned note: it is not model output, and OFF never reveals history values.
export function contextNotice(context) {
  if (!context || typeof context !== 'object' || Array.isArray(context)) {
    return 'Shared context could not be confirmed, so the assistant cannot determine recent Fifer history.'
  }
  if (Object.keys(context).length === 0) {
    return 'Recent Fifer history was not shared, so the assistant cannot determine it.'
  }
  if (Object.keys(context).sort().join('|') !== [...SHARED_CONTEXT_KEYS].sort().join('|')
      || !Number.isSafeInteger(context.completed_sessions) || context.completed_sessions < 0
      || ![null, '5-4-3-2-1'].includes(context.recent_completed_skill)
      || ![null, ...SHARED_CHECKINS].includes(context.latest_completed_checkin)) {
    return 'Shared context could not be confirmed, so the assistant cannot determine recent Fifer history.'
  }
  const details = [`${context.completed_sessions} completed ${context.completed_sessions === 1 ? 'session' : 'sessions'}`]
  if (context.recent_completed_skill) details.push(`latest completed skill: ${context.recent_completed_skill}`)
  if (context.latest_completed_checkin) details.push(`latest check-in: “${context.latest_completed_checkin}”`)
  return `For this reply, you chose to share: ${details.join('; ')}.`
}

export function createTextRequest(fetcher = (...args) => fetch(...args), timeoutMs = TEXT_TIMEOUT_MS) {
  let generation = 0, controller = null
  return {
    cancel() { generation++; controller?.abort(); controller = null },
    async send(path, body) {
      const token = ++generation
      controller?.abort()
      const active = new AbortController()
      controller = active
      const timer = setTimeout(() => active.abort(), timeoutMs)
      try {
        const response = await fetcher(path, { method: 'POST', body: JSON.stringify(body),
          headers: { 'Content-Type': 'application/json' }, signal: active.signal, cache: 'no-store' })
        const value = await response.json().catch(() => null)
        if (token !== generation) return { cancelled: true }
        if (!response.ok || !value) throw new Error(value?.detail || 'Text request failed. No reply or save was confirmed.')
        return value
      } catch (error) {
        if (token !== generation) return { cancelled: true }
        throw new Error(error.name === 'AbortError'
          ? 'Text request timed out after 15 seconds. No retry was made; saving could not be confirmed.'
          : error.message || 'Text assistant unavailable. No retry or save was confirmed.')
      } finally {
        clearTimeout(timer)
        if (controller === active) controller = null
      }
    },
  }
}
