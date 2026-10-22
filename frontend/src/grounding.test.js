import test from 'node:test'
import assert from 'node:assert/strict'
import { CHECKINS, SEQUENCE, STEPS, createExperience, transition } from './grounding.js'
import { createSaveQueue, newSessionRecord, sessionSnapshot, sessionPayload, restoreExperience } from './persistence.js'
import { request } from './api.js'

const send = (state, type, now = state.lastAt + 100, value) => transition(state, { type, value }, now)
const started = () => send(createExperience(0), 'BEGIN', 1000)

test('fixed five categories/counts and after-Feel check-in; zero selections always advance', () => {
  assert.deepEqual(STEPS.map(step => [step.id, step.count]), [['see',5],['feel',4],['hear',3],['smell',2],['taste',1]])
  let state = started()
  for (const screen of SEQUENCE) {
    assert.equal(state.screen, screen)
    assert.deepEqual(state.selections, {})
    if (screen !== 'complete') state = send(state, 'NEXT')
  }
  assert.equal(state.recentCompleted, false)
  state = send(state, 'FINISH')
  assert.equal(state.recentCompleted, true)
  assert.equal(state.finished, true)
})

test('optional selections toggle, unknown answers ignored, no quota required', () => {
  let state = started()
  state = send(state, 'SELECT', 1100, STEPS[0].choices[0])
  assert.equal(state.selections.see.length, 1)
  state = send(state, 'SELECT', 1200, STEPS[0].choices[0])
  assert.equal(state.selections.see.length, 0)
  state = send(state, 'SELECT', 1300, 'unrecognized')
  assert.equal(state.selections.see.length, 0)
  assert.equal(send(state, 'NEXT').screen, 'feel')
})

test('check-in is optional, includes exact label, can be skipped even after selection', () => {
  assert.ok(CHECKINS.includes('A little better'))
  let state = send(send(started(), 'NEXT'), 'NEXT')
  state = send(state, 'CHECKIN', 1400, 'A little better')
  assert.equal(state.checkin, 'A little better')
  state = send(state, 'SKIP')
  assert.equal(state.screen, 'hear')
  assert.equal(state.checkin, null)
})

test('Pause blocks advancement and selections; explicit Resume restores state', () => {
  let state = send(started(), 'SELECT', 1100, STEPS[0].choices[0])
  state = send(state, 'PAUSE', 2000)
  assert.equal(send(state, 'NEXT', 3000).screen, 'see')
  assert.equal(send(state, 'SELECT', 3000, STEPS[0].choices[1]).selections.see.length, 1)
  state = send(state, 'RESUME', 5000)
  assert.equal(state.screen, 'see')
  assert.equal(state.selections.see.length, 1)
  assert.equal(state.activeMs, 1000)
  assert.equal(state.pausedMs, 3000)
})

test('support is available at every main state; activity return requires Resume', () => {
  for (const screen of ['start', ...SEQUENCE, 'stopped']) {
    const state = { ...started(), screen, started: !['start','stopped'].includes(screen) }
    const opened = send(state, 'SUPPORT')
    assert.equal(opened.overlay, 'support')
    const closed = send(opened, 'CLOSE_SUPPORT')
    assert.equal(closed.screen, screen)
    assert.equal(closed.overlay, state.started ? 'pause' : null)
  }
})

test('support opens from Pause, excludes support duration, and does not auto-resume', () => {
  let state = send(started(), 'PAUSE', 2000)
  state = send(state, 'SUPPORT', 4000)
  state = send(state, 'CLOSE_SUPPORT', 9000)
  assert.equal(state.overlay, 'pause')
  assert.equal(state.activeMs, 1000)
  assert.equal(state.pausedMs, 2000)
  assert.equal(state.supportMs, 5000)
  state = send(state, 'RESUME', 10000)
  assert.equal(state.pausedMs, 3000)
})

test('Stop is immediate from activity, Pause and Support; no completion or answers retained', () => {
  for (const overlay of [null, 'pause', 'support']) {
    const state = { ...started(), overlay, selections: { see: ['A window'] }, checkin: 'A little better' }
    const stopped = send(state, 'STOP')
    assert.equal(stopped.screen, 'stopped')
    assert.equal(stopped.overlay, null)
    assert.equal(stopped.recentCompleted, false)
    assert.deepEqual(stopped.selections, {})
    assert.equal(stopped.checkin, null)
  }
})

test('90 seconds never forces completion; active timing excludes overlays', () => {
  const state = send(started(), 'SELECT', 151000, STEPS[0].choices[0])
  assert.equal(state.screen, 'see')
  assert.equal(state.activeMs, 150000)
})

test('only explicit Finish creates a dismissible recent-skill suggestion', () => {
  let state = started()
  for (let index = 0; index < 6; index++) state = send(state, 'NEXT')
  assert.equal(send(state, 'HOME').recentCompleted, false)
  state = send(state, 'FINISH')
  state = send(state, 'HOME')
  assert.equal(state.recentCompleted, true)
  assert.equal(send(state, 'DISMISS_RECENT').recentCompleted, false)
  assert.equal(state.screen, 'start')
})

test('setup excludes pre-exercise support; active clock remains separate', () => {
  let state = send(createExperience(0), 'SUPPORT', 1000)
  state = send(state, 'CLOSE_SUPPORT', 6000)
  state = send(state, 'BEGIN', 7000)
  assert.equal(state.setupMs, 2000)
  assert.equal(state.supportMs, 5000)
  assert.equal(state.activeMs, 0)
})

test('persistence allowlist excludes all sensory selections and narratives', () => {
  const before = createExperience(0)
  let state = send(before, 'BEGIN', 1000)
  state = send(state, 'SELECT', 1200, STEPS[0].choices[0])
  state.personalNarrative = 'Not a supported stored field'
  const record = sessionSnapshot(newSessionRecord('fictional-id','2026-10-22T12:00:00Z'), before, state, 'BEGIN')
  const payload = sessionPayload(record, 3)
  assert.deepEqual(Object.keys(payload).sort(), ['skill','started_at','ended_at','status','current_step','checkin',
    'setup_ms','active_ms','paused_ms','support_ms','revision','event','history_epoch'].sort())
  assert.equal(payload.history_epoch, 3)
  assert.equal(JSON.stringify(payload).includes('A window'), false)
})

test('Stop snapshot persists stopped status and allowed check-in, not completion or sensory choices', () => {
  const before = { ...started(), screen: 'hear', checkin: 'A little better', selections: { see: ['A window'] } }
  const after = send(before, 'STOP', 2000)
  const saved = sessionSnapshot(newSessionRecord('fictional-id','2026-10-22T12:00:00Z'),before,after,'STOP','2026-10-22T12:01:00Z')
  assert.equal(saved.status, 'stopped')
  assert.equal(saved.current_step, 'hear')
  assert.equal(saved.checkin, 'A little better')
  assert.equal(saved.event, 'stop')
  assert.equal(saved.active_ms, 1000)
  assert.equal('selections' in saved, false)
})

test('restoring a saved step opens paused, never counts closed-browser downtime or restores choices', () => {
  const restored = restoreExperience({ current_step:'feel',checkin:null,setup_ms:1000,
    active_ms:2000,paused_ms:3000,support_ms:4000 },500000)
  assert.equal(restored.screen,'feel')
  assert.equal(restored.overlay,'pause')
  assert.deepEqual(restored.selections,{})
  const resumed = send(restored,'RESUME',500100)
  assert.equal(resumed.activeMs,2000)
  assert.equal(resumed.pausedMs,3100)
  assert.equal(resumed.supportMs,4000)
})

test('failed saves stay visibly unsaved, retain order, and retry without losing snapshots', async () => {
  const saved = [], changes = []
  let unavailable = true
  const queue = createSaveQueue(async record => {
    if (unavailable) throw new Error('offline')
    saved.push(record.revision)
  }, change => changes.push(change.status))
  queue.enqueue({revision:1})
  await queue.settled()
  assert.equal(queue.status,'unsaved')
  assert.equal(queue.pending,1)
  queue.enqueue({revision:2})
  assert.equal(queue.pending,2)
  assert.equal(changes.includes('saved'),false)
  unavailable = false
  await queue.retry()
  assert.deepEqual(saved,[1,2])
  assert.equal(queue.pending,0)
  assert.equal(queue.status,'saved')
})

test('clearing pending state ignores an old in-flight acknowledgement', async () => {
  let finish
  const changes = []
  const queue = createSaveQueue(() => new Promise(resolve => { finish = resolve }), change => changes.push(change.status))
  queue.enqueue({revision:1})
  queue.clear()
  finish()
  await queue.settled()
  assert.equal(queue.pending,0)
  assert.equal(queue.status,'idle')
  assert.equal(changes.at(-1),'idle')
})

test('proxy/network failures never become a successful or raw JSON-parse acknowledgement', async t => {
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => new Response('proxy unavailable', {status:502}))
  await assert.rejects(request('/api/history'), error => error.status === 502 && error.message.includes('No change was confirmed'))
  fetchMock.mock.mockImplementation(async () => { throw new TypeError('network failure') })
  await assert.rejects(request('/api/history'), /No change was confirmed/)
})

