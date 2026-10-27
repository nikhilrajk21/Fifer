// Application-owned content and transitions. No model, storage, network, or timers.
export const SEE_SCENE = Object.freeze({
  src: new URL('./assets/classroom.svg', import.meta.url).href,
  alt: 'Illustrated classroom: a large window on the left, a round wall clock above a desk, a blue book on the desk, and a leafy plant in a pot on the right.',
  credit: 'Original Fifer classroom illustration, created for this project. No external image source.',
  examples: Object.freeze([
    { id: 'window', label: 'A window' },
    { id: 'clock', label: 'A wall clock' },
    { id: 'book', label: 'A blue book' },
    { id: 'desk', label: 'A desk' },
    { id: 'plant', label: 'A potted plant' },
  ].map(Object.freeze)),
})

export const STEPS = Object.freeze([
  { id: 'see', name: 'See', count: 5, title: 'What five things can you see in this picture?',
    hint: 'Explore the classroom picture or its description. Type a few visible things, choose examples, or skip. Five is a prompt, not a required total.',
    image: SEE_SCENE,
    choices: SEE_SCENE.examples.map(item => item.label) },
  { id: 'feel', name: 'Feel', count: 4, title: 'Imagine up to four comfortable things you could feel.',
    hint: 'Use the imagined classroom or your present surroundings. You might imagine a smooth desktop or soft fabric, or notice an existing comfortable sensation. You do not need to touch anything.',
    choices: ['An imagined smooth desktop', 'Imagined soft fabric', 'Clothing already resting against your skin', 'Feet already resting on the floor'] },
  { id: 'hear', name: 'Hear', count: 3, title: 'Imagine or notice up to three sounds.',
    hint: 'If you like, imagine a garden or open area: birds calling, wind rustling leaves, or footsteps on a path. Or use sounds already in your present surroundings. These are possibilities, not sounds the app has detected.',
    choices: ['Imagined birds calling', 'Imagined wind rustling leaves', 'Imagined footsteps on a path'] },
  { id: 'smell', name: 'Smell', count: 2, title: 'Imagine or notice up to two scents, if comfortable.',
    hint: 'You can imagine a familiar scent, use one already present, choose none or not sure, or skip. There is no need to seek out or smell anything.',
    choices: ['Imagined fresh coffee', 'Imagined flowers', 'None', 'Not sure'] },
  { id: 'taste', name: 'Taste', count: 1, title: 'Imagine or notice one taste, if comfortable.',
    hint: 'You can imagine a familiar taste, use one already present, choose none or not sure, or skip. There is no need to eat, drink, or try anything.',
    choices: ['An imagined familiar taste', 'None', 'Not sure'] },
].map(step => Object.freeze({ ...step, choices: Object.freeze(step.choices) })))

export const CHECKINS = Object.freeze(['A little better', 'About the same', 'A little harder', 'Not sure'])
export const SEQUENCE = Object.freeze(['see', 'feel', 'checkin', 'hear', 'smell', 'taste', 'complete'])
const ACTIVITY = new Set(SEQUENCE)

export function createExperience(now = 0, recentCompleted = false) {
  return {
    screen: 'start', overlay: null, selections: {}, responses: {}, checkin: null,
    started: false, finished: false, recentCompleted,
    setupStartedAt: now, lastAt: now, setupMs: 0,
    activeMs: 0, pausedMs: 0, supportMs: 0,
  }
}

function settle(state, now) {
  const next = { ...state, lastAt: now }
  const delta = Math.max(0, now - state.lastAt)
  if (state.overlay === 'support') next.supportMs += delta
  else if (state.overlay === 'pause') next.pausedMs += delta
  else if (state.started && !state.finished && ACTIVITY.has(state.screen)) next.activeMs += delta
  return next
}

export function transition(state, action, now = 0) {
  let next = settle(state, now)
  if (action.type === 'SUPPORT') return { ...next, overlay: 'support' }
  if (action.type === 'STOP') {
    return { ...next, screen: 'stopped', overlay: null, started: false, finished: false, selections: {}, responses: {}, checkin: null }
  }
  if (action.type === 'CLOSE_SUPPORT' && state.overlay === 'support') {
    return { ...next, overlay: state.started && !state.finished ? 'pause' : null }
  }
  if (action.type === 'RESUME' && state.overlay === 'pause') return { ...next, overlay: null }
  if (action.type === 'PAUSE' && state.started && !state.finished && !state.overlay) return { ...next, overlay: 'pause' }
  if (state.overlay) return next

  if (action.type === 'HOME') return createExperience(now, state.recentCompleted)
  if (action.type === 'DISMISS_RECENT') return { ...next, recentCompleted: false }
  if (action.type === 'BEGIN' && state.screen === 'start') {
    return {
      ...createExperience(now, state.recentCompleted),
      screen: 'see', started: true,
      setupMs: Math.max(0, now - state.setupStartedAt - state.supportMs),
      supportMs: state.supportMs,
    }
  }
  if (action.type === 'SELECT') {
    const step = STEPS.find(item => item.id === state.screen)
    if (!step?.choices.includes(action.value)) return next
    const selected = state.selections[step.id] || []
    return { ...next, selections: {
      ...state.selections,
      [step.id]: selected.includes(action.value)
        ? selected.filter(value => value !== action.value)
        : [...selected, action.value],
    } }
  }
  if (action.type === 'WRITE' && STEPS.some(step => step.id === state.screen) && typeof action.value === 'string') {
    return { ...next, responses: { ...state.responses, [state.screen]: action.value.slice(0, 500) } }
  }
  if (action.type === 'CHECKIN' && state.screen === 'checkin' && CHECKINS.includes(action.value)) {
    return { ...next, checkin: state.checkin === action.value ? null : action.value }
  }
  if ((action.type === 'NEXT' || action.type === 'SKIP') && SEQUENCE.includes(state.screen) && state.screen !== 'complete') {
    const screen = SEQUENCE[SEQUENCE.indexOf(state.screen) + 1]
    if (state.screen === 'checkin' && action.type === 'SKIP') next.checkin = null
    if (action.type === 'SKIP') {
      next.selections = { ...state.selections }
      next.responses = { ...state.responses }
      delete next.selections[state.screen]
      delete next.responses[state.screen]
    }
    return { ...next, screen }
  }
  if (action.type === 'FINISH' && state.screen === 'complete' && !state.finished) {
    return { ...next, finished: true, started: false, recentCompleted: true, responses: {} }
  }
  return next
}

