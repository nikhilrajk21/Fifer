import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import * as Vue from 'vue'
import { parse, compileScript } from 'vue/compiler-sfc'
import { renderToString } from 'vue/server-renderer'
import { CHECKINS, SEQUENCE, SEE_SCENE, STEPS, createExperience, transition } from './grounding.js'
import { createSaveQueue, newSessionRecord, sessionSnapshot, sessionPayload, restoreExperience } from './persistence.js'
import { request } from './api.js'
import { anonymousBrowserId, createTextRequest, TEXT_TIMEOUT_MS } from './chat.js'

const send = (state, type, now = state.lastAt + 100, value) => transition(state, { type, value }, now)
const started = () => send(createExperience(0), 'BEGIN', 1000)

test('anonymous quota identity survives reload and changes only when browser storage is cleared', () => {
  const data = new Map()
  const storage = { getItem:key=>data.get(key), setItem:(key,value)=>data.set(key,value) }
  const first='11111111-1111-4111-8111-111111111111', second='22222222-2222-4222-8222-222222222222'
  assert.equal(anonymousBrowserId(storage,()=>first),first)
  assert.equal(anonymousBrowserId(storage,()=>second),first)
  assert.deepEqual([...data.values()],[first]) // No questions or message bodies in browser storage.
  data.clear()
  assert.equal(anonymousBrowserId(storage,()=>second),second)
  assert.throws(()=>anonymousBrowserId({ getItem(){ throw new Error('blocked') } }),/blocked/)
})

test('chat cancellation ignores a late mock reply after Stop, Support or navigation', async () => {
  for (const reason of ['Stop','Support','navigation']) {
    let release, calls=0
    const transport=createTextRequest(async()=>{
      calls++
      return new Promise(resolve=>{ release=()=>resolve(new Response(JSON.stringify({answer:'late'}),{status:200})) })
    })
    const pending=transport.send('/api/chat/mock',{question:'Fictional app question'})
    transport.cancel(reason)
    release()
    assert.deepEqual(await pending,{cancelled:true})
    assert.equal(calls,1)
  }
})

test('text requests time out without retries and normalize backend/quota failures', async () => {
  assert.equal(TEXT_TIMEOUT_MS,15000)
  let calls=0
  const timeout=createTextRequest(async(_path,options)=>{
    calls++
    return new Promise((_resolve,reject)=>options.signal.addEventListener('abort',()=>reject(new DOMException('aborted','AbortError'))))
  },5)
  await assert.rejects(timeout.send('/api/chat/mock',{}),/No retry was made/)
  assert.equal(calls,1)
  const limited=createTextRequest(async()=>new Response(JSON.stringify({detail:'Quota reached'}),{status:429}))
  await assert.rejects(limited.send('/api/chat/mock',{}),/Quota reached/)
  const offline=createTextRequest(async()=>new Response('proxy unavailable',{status:502}))
  await assert.rejects(offline.send('/api/chat/mock',{}),/No reply or save was confirmed/)
})

// Render the actual prompt SFC with the compiler/renderer shipped with approved Vue.
// No browser emulation package, test-only component copy, or new dependency.
const promptSource = readFileSync(new URL('./components/GroundingPrompt.vue', import.meta.url), 'utf8')
const { descriptor } = parse(promptSource)
const compiled = compileScript(descriptor, { id: 'grounding-prompt-test', inlineTemplate: true })
const componentCode = compiled.content.replace(/import \{([^}]+)\} from ["']vue["'];?/g,
  (_, bindings) => `const {${bindings.replace(/\bas\b/g, ':')}} = Vue;`)
  .replace('export default', 'return')
const GroundingPrompt = new Function('Vue', componentCode)(Vue)
const renderPrompt = (step, response = '') => renderToString(Vue.createSSRApp(GroundingPrompt, { step, selected: [], response }))

test('See examples correspond to five drawn objects in the single local original scene', () => {
  assert.equal(STEPS.filter(step => step.image).length, 1)
  assert.equal(STEPS[0].image, SEE_SCENE)
  const picture = readFileSync(new URL(SEE_SCENE.src), 'utf8')
  assert.deepEqual(STEPS[0].choices, SEE_SCENE.examples.map(item => item.label))
  assert.deepEqual(SEE_SCENE.examples.map(item => item.id), ['window','clock','book','desk','plant'])
  for (const { id, label } of SEE_SCENE.examples) {
    const group = picture.match(new RegExp(`<g id="${id}" aria-label="${label}">([\\s\\S]*?)</g>`))
    assert.ok(group, `${label} must have its own drawn object`)
    assert.match(group[1], /<(rect|circle|path)\b/)
    assert.ok(SEE_SCENE.alt.toLowerCase().includes(id))
  }
  assert.doesNotMatch(picture, /<script|<image|<foreignObject|\bhref=|url\(/i)
  assert.match(SEE_SCENE.credit, /Original Fifer/)
})

test('actual See prompt renders descriptive local image and an optional labelled keyboard input', async () => {
  const html = await renderPrompt(STEPS[0])
  assert.match(html, /<img[^>]+alt="Illustrated classroom:/)
  assert.match(html, /width="800" height="440"/)
  assert.match(html, /<label[^>]+for="see-response"/)
  assert.match(html, /<textarea[^>]+id="see-response"[^>]+aria-describedby="see-boundary see-privacy"/)
  assert.doesNotMatch(html.match(/<textarea\b[^>]*>/)[0], /\brequired(?:=|\s|>)/)
  assert.match(html, /Fifer does not sense your surroundings/)
  assert.match(html, /not saved or sent/)
  assert.match(html, /Optional examples visible in the picture/)
  assert.match(promptSource, /textarea:focus-visible\{outline:3px solid/)
})

test('Feel/Hear offer optional imagined or present observations; sounds are plausible', () => {
  assert.match(STEPS[1].hint, /imagined classroom or your present surroundings/)
  assert.match(STEPS[1].hint, /do not need to touch anything/)
  assert.match(STEPS[2].hint, /garden or open area/)
  assert.deepEqual(STEPS[2].choices, ['Imagined birds calling','Imagined wind rustling leaves','Imagined footsteps on a path'])
  assert.doesNotMatch(STEPS[2].choices.join(' '), /grass/i)
})

test('Smell/Taste render optional text, None and Not sure, without eating/drinking demands', async () => {
  for (const step of STEPS.slice(3)) {
    const html = await renderPrompt(step, 'Fictional sensory example')
    assert.match(html, /<textarea/)
    assert.match(html, /Fictional sensory example/)
    assert.match(html, />None<\/button>/)
    assert.match(html, />Not sure<\/button>/)
    assert.match(step.hint, /or skip/)
  }
  assert.match(STEPS[3].hint, /no need to seek out or smell anything/)
  assert.match(STEPS[4].hint, /no need to eat, drink, or try anything/)
  assert.doesNotMatch(STEPS.map(step => step.title + step.hint + step.choices.join()).join(' '), /saliva/i)
})

test('typed sensory words are optional, retained across Pause/Resume, and cleared by Skip/Stop/Finish', () => {
  let state = send(started(), 'WRITE', 1100, 'Fictional blue book')
  assert.equal(state.responses.see, 'Fictional blue book')
  const paused = send(state, 'PAUSE')
  assert.equal(send(paused, 'WRITE', 1400, 'blocked').responses.see, 'Fictional blue book')
  state = send(paused, 'RESUME')
  assert.equal(state.responses.see, 'Fictional blue book')
  state = send(state, 'SELECT', 1600, STEPS[0].choices[0])
  const skipped = send(state, 'SKIP')
  assert.equal(skipped.screen, 'feel')
  assert.deepEqual(skipped.responses, {})
  assert.deepEqual(skipped.selections, {})
  for (const overlay of [null, 'pause', 'support']) {
    const stopped = send({ ...state, overlay }, 'STOP')
    assert.equal(stopped.screen, 'stopped')
    assert.deepEqual(stopped.responses, {})
    assert.equal(stopped.finished, false)
  }
  const support = send(state, 'SUPPORT')
  assert.equal(support.overlay, 'support')
  assert.equal(support.responses.see, 'Fictional blue book')
  for (let index = 0; index < 6; index++) state = send(state, 'NEXT')
  assert.deepEqual(send(state, 'FINISH').responses, {})
})

test('Skip works at every category with no quota and keeps the fixed order/counts', () => {
  let state = started()
  for (const screen of SEQUENCE) {
    assert.equal(state.screen, screen)
    if (screen !== 'complete') state = send(state, 'SKIP')
  }
  assert.equal(state.finished, false)
  assert.equal(send(state, 'FINISH').finished, true)
})

test('typed words are escaped in rendered text and never enter session payloads or restoration', async () => {
  let state = send(started(), 'WRITE', 1100, '<script>fictional-only</script>')
  const html = await renderPrompt(STEPS[0], state.responses.see)
  assert.match(html, /&lt;script&gt;fictional-only&lt;\/script&gt;/)
  assert.doesNotMatch(html, /<script>/)
  const record = sessionSnapshot(newSessionRecord('fictional-id','2026-10-26T12:00:00Z'), state, send(state,'NEXT'), 'NEXT')
  const payload = sessionPayload(record, 0)
  assert.equal('responses' in payload, false)
  assert.equal(JSON.stringify(payload).includes('fictional-only'), false)
  assert.deepEqual(restoreExperience(record, 2000).responses, {})
})

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

