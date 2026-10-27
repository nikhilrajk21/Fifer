// Only whitelisted metadata or explicitly opted-in fictional messages belong here.
export async function request(path, options = {}) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 2500)
  try {
    const response = await fetch(path, { ...options, signal: controller.signal, cache: 'no-store',
      headers: options.body ? { 'Content-Type': 'application/json' } : undefined })
    const result = await response.json().catch(() => null)
    if (!response.ok) {
      const error = new Error(typeof result?.detail === 'string' ? result.detail : 'Local storage could not be reached. No change was confirmed.')
      error.status = response.status
      throw error
    }
    if (result === null) throw new Error('The local storage response could not be confirmed.')
    return result
  } catch (error) {
    if (error.name === 'AbortError' || error instanceof TypeError) {
      throw new Error('Local storage could not be reached. No change was confirmed.')
    }
    throw error
  } finally {
    clearTimeout(timeout)
  }
}

export const loadHistory = () => request('/api/history')
export const reviewSession = id => request(`/api/sessions/${encodeURIComponent(id)}`)
export const saveSession = (id, payload) => request(`/api/sessions/${encodeURIComponent(id)}`, { method: 'PUT', body: JSON.stringify(payload) })
export const setMessageOptIn = (message_opt_in, history_epoch) => request('/api/settings', { method: 'PATCH', body: JSON.stringify({ message_opt_in, history_epoch }) })
export const deleteSession = (id, epoch) => request(`/api/sessions/${encodeURIComponent(id)}?history_epoch=${epoch}`, { method: 'DELETE' })
export const clearHistory = epoch => request(`/api/history?history_epoch=${epoch}`, { method: 'DELETE' })

export const chatConfig = browser => request(`/api/chat/config?browser_id=${encodeURIComponent(browser)}`)
export const chatContext = () => request('/api/chat/context')
export const beginChat = body => request('/api/chat/sessions', { method: 'POST', body: JSON.stringify(body) })
export const reviewChat = id => request(`/api/chat/sessions/${encodeURIComponent(id)}`)
export const stopChat = (id, body) => request(`/api/chat/sessions/${encodeURIComponent(id)}/stop`, { method: 'POST', body: JSON.stringify(body) })
export const deleteChat = (id, epoch) => request(`/api/chat/sessions/${encodeURIComponent(id)}?history_epoch=${epoch}`, { method: 'DELETE' })

