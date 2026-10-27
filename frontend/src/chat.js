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
