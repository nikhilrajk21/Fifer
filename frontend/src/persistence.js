import { createExperience, SEQUENCE } from './grounding.js'

export function newSessionRecord(id, startedAt) {
  return { id, skill: '5-4-3-2-1', started_at: startedAt, ended_at: null,
    status: 'active', current_step: 'see', checkin: null,
    setup_ms: 0, active_ms: 0, paused_ms: 0, support_ms: 0, revision: 0 }
}

// Deliberate allowlist: sensory choices and narratives never cross this boundary.
export function sessionSnapshot(record, before, after, type, endedAt = null) {
  const stopping = type === 'STOP'
  const finished = type === 'FINISH'
  const current = SEQUENCE.includes(after.screen) ? after.screen
    : SEQUENCE.includes(before.screen) ? before.screen : record.current_step
  const events = { BEGIN: 'begin', NEXT: 'progress', SKIP: 'progress', CHECKIN: 'progress',
    PAUSE: 'pause', CLOSE_SUPPORT: 'pause', RESUME: 'resume', FINISH: 'finish', STOP: 'stop' }
  return {
    id: record.id, skill: record.skill, started_at: record.started_at,
    ended_at: stopping || finished ? endedAt : null,
    status: stopping ? 'stopped' : finished ? 'completed' : after.overlay ? 'paused' : 'active',
    current_step: current, checkin: stopping ? before.checkin : after.checkin,
    setup_ms: Math.floor(after.setupMs), active_ms: Math.floor(after.activeMs),
    paused_ms: Math.floor(after.pausedMs), support_ms: Math.floor(after.supportMs),
    revision: record.revision + 1, event: events[type] || 'checkpoint',
  }
}

export function sessionPayload(record, epoch) {
  const { id, ...payload } = record
  return { ...payload, history_epoch: epoch }
}

export function restoreExperience(record, now = 0) {
  return { ...createExperience(now), screen: record.current_step, overlay: 'pause',
    started: true, checkin: record.checkin, setupMs: record.setup_ms,
    activeMs: record.active_ms, pausedMs: record.paused_ms, supportMs: record.support_ms }
}

// Ordered, idempotent snapshots remain in memory on failure. No silent local cache.
export function createSaveQueue(save, onChange = () => {}) {
  let items = [], running = false, blocked = false, generation = 0, task = Promise.resolve()
  let status = 'idle', error = null
  const notify = value => { status = value; onChange({ status, pending: items.length, error }) }
  async function drain() {
    if (running || blocked || !items.length) return task
    running = true
    const token = generation
    notify('saving')
    task = (async () => {
      try {
        while (items.length && token === generation) {
          try { await save(items[0]) }
          catch (failure) {
            if (token === generation) { blocked = true; error = failure; notify('unsaved') }
            return
          }
          if (token !== generation) return
          items.shift()
        }
        if (token === generation) { error = null; notify('saved') }
      } finally {
        running = false
        if (items.length && !blocked) void drain()
      }
    })()
    return task
  }
  return {
    enqueue(record) { items.push({ ...record }); if (blocked) notify('unsaved'); else void drain() },
    retry() { blocked = false; error = null; return drain() },
    clear() { generation++; items = []; blocked = false; error = null; notify('idle') },
    get pending() { return items.length },
    get status() { return status },
    settled() { return task },
  }
}
