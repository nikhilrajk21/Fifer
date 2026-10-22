// Application-owned content and transitions. No model, storage, network, or timers.
export const STEPS = Object.freeze([
  { id: 'see', name: 'See', count: 5, title: 'Notice five things you can see.',
    hint: 'Notice what is already around you. Selecting an answer is optional.',
    choices: ['A window', 'A book', 'A light', 'A desk', 'A bag'] },
  { id: 'feel', name: 'Feel', count: 4, title: 'Notice four things you can feel.',
    hint: 'You can notice an existing sensation. You do not need to touch anything.',
    choices: ['Feet resting on the floor', 'The chair beneath you', 'Clothing against your skin', 'Air around you'] },
  { id: 'hear', name: 'Hear', count: 3, title: 'Notice three things you can hear.',
    hint: 'Notice sounds already present, or continue without an answer.',
    choices: ['A fan or steady background sound', 'Footsteps', 'An outside sound'] },
  { id: 'smell', name: 'Smell', count: 2, title: 'Notice two things you can smell, if available.',
    hint: 'There is no need to find a smell or move to another place.',
    choices: ['A familiar scent already present', 'No noticeable smell'] },
  { id: 'taste', name: 'Taste', count: 1, title: 'Notice one taste already present, if available.',
    hint: 'There is no need to eat or drink anything.',
    choices: ['A taste already present', 'No noticeable taste'] },
].map(step => Object.freeze({ ...step, choices: Object.freeze(step.choices) })))

export const CHECKINS = Object.freeze(['A little better', 'About the same', 'A little harder', 'Not sure'])
export const SEQUENCE = Object.freeze(['see', 'feel', 'checkin', 'hear', 'smell', 'taste', 'complete'])
const ACTIVITY = new Set(SEQUENCE)

export function createExperience(now = 0, recentCompleted = false) {
  return {
    screen: 'start', overlay: null, selections: {}, checkin: null,
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
    return { ...next, screen: 'stopped', overlay: null, started: false, finished: false, selections: {}, checkin: null }
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
  if (action.type === 'CHECKIN' && state.screen === 'checkin' && CHECKINS.includes(action.value)) {
    return { ...next, checkin: state.checkin === action.value ? null : action.value }
  }
  if ((action.type === 'NEXT' || action.type === 'SKIP') && SEQUENCE.includes(state.screen) && state.screen !== 'complete') {
    const screen = SEQUENCE[SEQUENCE.indexOf(state.screen) + 1]
    if (state.screen === 'checkin' && action.type === 'SKIP') next.checkin = null
    return { ...next, screen }
  }
  if (action.type === 'FINISH' && state.screen === 'complete' && !state.finished) {
    return { ...next, finished: true, started: false, recentCompleted: true }
  }
  return next
}

