# Fifer V2 — mock-only Gemini Live increment

Current Part 3.2 browser/SQLite and mock acceptance, separated timing and submission limits are in the [acceptance matrix](verification/part-3-2-acceptance.md) and [root report](../report.md). The older increment counts below remain historical. No paid/live observation exists; real connector and actual model-contribution demonstration remain unfinished. Course requirements and owner-reported Gemini substitution do not authorize a live test or imply approval of static support wording.

## Latest Mute / Unmute / End lifecycle increment

The Chat and standalone shared panel now names separate **Mute**, **Unmute** and **End** actions. Mute fences old microphone callbacks, stops input tracks/worklet capture and sends exactly one `activity_end` only when a manual input activity was running. It never closes the socket, cancels response/playback timers or clears assistant playback. Idle/waiting/speaking/playback mute calls are idempotent for input signaling; Unmute is available after the response completes, preserving the approved manual-turn design (no new full-duplex policy). An empty input turn can be muted before the first PCM frame without the backend treating that as a session error.

Verified against [Google's current manual VAD guidance](https://ai.google.dev/gemini-api/docs/live-api/capabilities#disable-automatic-vad): with automaticActivityDetection.disabled=true, stream interruption is marked by activityEnd; audioStreamEnd is not sent in that configuration. The backend retains that exact setup and marker. This documentation check does not demonstrate actual provider behavior; real calls remain blocked.

End is immediate and idempotent: invalidate connection/capture generations, cancel every controller timer, stop microphone tracks, disconnect input/output nodes and AudioWorklet port, discard pending PCM, stop scheduled sources, close AudioContext, detach socket callbacks, send best-effort stop and close the app socket. Browser cleanup attempts the remaining resources even if one release throws. Late permission results are also fenced by the audio adapter's capture epoch, including Mute while Unmute permission is pending. Start is accepted only from terminal/off states; duplicate clicks during permission/setup/active use do not allocate another session. Every accepted Start creates fresh audio/socket resources and receives a fresh mock provider session; no audio/transcript or voice-session content is stored. Duplicate playback-enable gestures are guarded too.

FastAPI races provider setup against local End/disconnect, cancels pending setup promptly and closes the acquired wire in finally. Its wall-clock maximum includes setup and remains independent of client timers. Navigation/unmount, Support, failure, pagehide/hidden-tab and the browser's 300-second timer invoke the same End cleanup. Page exit/OS termination cannot guarantee immediate remote detection; server timeouts/maximum remain the independent fallback. Normal page return never reconnects automatically. The prototype remains single-worker, with the existing anonymous-browser quota and no dollar-cap claim.

This increment changes `frontend/src/voice.js`, `frontend/src/audio/pcm.js`, `frontend/src/components/VoicePanel.vue`, `frontend/src/voice.test.js`, `backend/voice.py`, `backend/tests/test_voice.py`, `README.md`, `docs/voice.md` and `handoffs/current.md`. No dependencies, manifests, key files, model/instructions, storage schema or text-chat logic changed. Mock verification covers muting through playback, immediate empty-turn mute, resource faults, cancellation during connect/setup/permission, stale callbacks, duplicate Start/End, fresh resources, page/navigation/Support/failure cleanup and both maximum timers. Final results: **49 frontend tests, 61 backend tests, Vite build and git diff --check passed**. The updated normal mock-only backend was restarted without resetting local history. Prior browser/synthetic checks below belong to their earlier increments; this lifecycle increment used mocked audio/socket/provider tests, not a new hardware/manual browser run. Actual provider behavior, abrupt process death and a full five-minute elapsed run remain unverified. No credential read, provider call, commit or push occurred.

## Latest Chat-screen increment

Voice controls now also appear inside the existing Chat screen without replacing its composer, text request transport, consent or quotas. The shared VoicePanel has an embedded h2 (no duplicate page h1). Chat Stop, Support and navigation stop its child voice controller; a voice-only permission/socket failure does not end or disable text Chat. The standalone Voice entry remains available outside grounding.

After explicit Start, `getUserMedia({audio:true,video:false})` runs before socket creation. Prepared tracks are disabled while connecting. First ready must include `mode:mock` and `setup_confirmed:true`, which FastAPI sends only after the mock provider's setupComplete event. Connection states report permission, connecting, active, closing, closed or failure; microphone reports active/muted separately. No socket-open event alone establishes active state. Unmute starts the existing 16 kHz PCM capture; Send turn/Mute ends it. Response PCM remains 24 kHz little-endian; no SDP, RTCPeerConnection, OpenAI endpoint or second-model pipeline was added.

AudioContext autoplay rejection no longer blocks setup. A suspended context keeps at most one second of pending PCM in RAM and displays **Enable assistant audio**. Only its user-gesture click resumes/drains playback; blocked audio never produces a false playback-done acknowledgement. Existing deadlines still apply. Interrupted/closed events clear both pending PCM and scheduled sources, cancel playback-completion timers and close the voice session; late output/recovery cannot revive it. This is conservative interruption-by-ending, not a claim of seamless full-duplex barge-in. Unexpected socket errors/non-normal closures report failure; normal close reports closed. Capture/playback cleanup is immediate; closing is emitted during cleanup, not a delayed confirmation gate.

Latest evidence: **42 frontend tests, 56 backend tests, Vite build and git diff --check passed**. Commands remain the same below; no dependency/manifest change was required. Added mock cases cover exact constraints, pre-socket permission/denial, no active state before confirmed setup, mute, closing/closed/failure, bounded autoplay queue/recovery, interruption/late audio and provider-side interruption suppression. Existing text/grounding/storage checks also pass.

Browser checks used separate ignored `.cache/verification/fifer-chat-voice-browser.sqlite3`. A disposable tab mocked microphone denial: voice showed failure, then a fictional text question received its normal curated response (not saved, opt-in OFF). A synthetic oscillator microphone then exercised Chat voice through the local backend; a simulated suspended playback state displayed Enable assistant audio, clicking it returned to active/muted (1/5 turns), with the text composer still enabled. Stopping the isolated backend closed voice while text controls stayed enabled and keyboard Emergency Support opened its static panel. The tab was closed to remove every test override, and the normal backend was restored without resetting history. No hardware audio or provider call was used. Actual browser permission prompts/autoplay policy, real Gemini speech/latency and account access remain unverified.

Changed in this follow-up: `frontend/src/components/ChatPanel.vue`, `frontend/src/components/VoicePanel.vue`, `frontend/src/voice.js`, `frontend/src/audio/pcm.js`, `frontend/src/voice.test.js`, `backend/voice.py`, `backend/tests/test_voice.py`, `README.md`, `docs/voice.md`, `handoffs/current.md`. Earlier checkpoint evidence below is retained as history.

## Authorization and boundary

The user approved the instructor's Gemini Live substitution, target `gemini-3.8-live`, the limits below, and mock-only implementation. Text Chat remains separate with `gemini-2.5-flash` as its target. No real text or Live call is authorized. No key was read or changed for this increment. The existing authentication family is Gemini Developer API/AI Studio (`GEMINI_API_KEY`, ignored `backend/.env`), not Vertex. Key validity, permissions, model access and billing remain unverified.

`GeminiLiveProvider.connect()` deliberately refuses before any key read or network connection. V2 implements the wire contract against `MockWire`; it does not implement or activate a real upstream transport. Changing that boundary requires separate approval and verification, not an environment toggle. The local mock discards microphone frames and returns a quiet 200 ms synthetic tone. It cannot understand, transcribe or answer speech, and UI labels say so.

## Flow, audio and shutdown

Optional Voice is available within Chat, from start choices or after explicit Finish, never during grounding. Native browser WebSocket connects through Vite `/api/voice` to FastAPI. The backend constructs the fixed model and instructions from reviewed app content; browser messages cannot supply models, prompts, tools, profile, check-ins, history or provider endpoints. The current increment uses manual Unmute / Send turn, not continuous listening. Start requests microphone permission and keeps tracks muted until confirmed setup and explicit Unmute. Permission denial is a finite error, not a retry.

AudioWorklet averages device input to mono, resamples across chunk boundaries to 16 kHz and encodes signed PCM16 little-endian in 20 ms frames. No microphone audio is routed to speakers. Output is PCM16LE at 24 kHz, decoded into Web Audio buffers. Playback ahead and input socket buffering are bounded to approximately one second; overflow closes voice honestly. The streaming averaging resampler is a simple prototype, not a production audio-quality claim.

The mocked Developer API contract sends setup first, waits for setupComplete, then uses realtimeInput.activityStart/audio/activityEnd with manual activity detection. Audio MIME types are fixed. It handles every audio part in serverContent.modelTurn, generationComplete versus turnComplete, interruption, goAway, invalid events and tools. No transcription configuration, search, tools, thinkingLevel, video, resumption or compression is enabled. Unexpected text/transcripts are dropped in memory. Interruption/goAway ends the session safely.

Stop/Leave, Stop voice, Support, unmount/navigation, tab hiding/pagehide, timeout, quota or connection error close capture tracks, disconnect the worklet, stop scheduled playback, close AudioContext and WebSocket, cancel timers/tasks, and ignore late frames. Explicit restart is required. Static Emergency Support opens immediately without waiting for cleanup or any backend/model response. Grounding controls/timing are unchanged. Support wording is the user's existing static sentence; instructor approval of that specific wording remains unverified. No automatic calls or messages exist.

## Limits and retained data

- 300 seconds wall-clock from the local socket's accepted start, including setup/idle time; never reset by a turn. Single-worker app: one concurrent voice session per browser.
- Five manual turns per session; maximum 20 seconds/utterance (wall-clock and PCM byte count); maximum 15 seconds/response audio (PCM bytes).
- 10-second setup timeout; 15-second first-audio and response-generation/playback deadlines. No automatic retries, reconnection or session resumption. Frontend and backend enforce independent boundaries.
- Two accepted starts per anonymous browser per UTC day. Atomic reservation occurs before mock setup; failures after reservation still count. Invalid starts, unavailable backend and rejected concurrent sockets do not create a reservation.
- Additive SQLite table `voice_daily_usage`: SHA-256 browser UUID hash, UTC date, accepted start count only. It shares the existing anonymous identity with text but has separate counters. Today's counters survive Delete/Clear and restart; older voice buckets are removed on a later day's voice start. No session/turn content or voice-session history is retained.
- No audio, transcripts, sensory responses, personal narratives, profile or credentials go into SQLite, localStorage, sessionStorage or files. Text-message opt-in never permits voice recording. Test databases are disposable; real local data is never reset on startup.

Anonymous browser identity is not verified person identity and clearing browser data can bypass its effective quota. These limits are not a dollar spending cap. Actual account quota/billing controls and provider data-use terms must be reviewed before separately approved real calls. No local recording does not imply zero provider processing/retention in a future real integration.

`VOICE_MAX_SESSION_SECONDS=300` would belong in ignored `backend/.env` if a future approved settings loader supports it. V2 enforces fixed server-side constants and does not load that variable. The safe template documents this explicitly; it does not invent a working environment switch.

## Dependency CHECK → TAKE ACTION → VERIFY

Verified Python 3.12.14 x64. Exact `websockets==17.3` requires Python >=3.11 and no runtime dependencies. Inspected `websockets-17.3-cp312-cp312-win_amd64.whl` matches CPython/OS and SHA-256 `6644eecd99c4e8cdf72e646e17b391bb70b054f44becde37dcdc48cbec7e1527`. Its sole native module is the matching speedups `.pyd`. The standard optional `websockets = websockets.cli:main` console entry point was reviewed; no install hooks, `.pth`, bundled executable scripts or runtime dependency additions were found. PyPI and OSV returned no listed advisories for 17.3 at inspection (a point-in-time result, not a security guarantee). Ignored `.cache/dependency-check/voice-dependency-check.json` records the review.

Installed only the inspected wheel into `backend/.venv`:

```powershell
.\backend\.venv\Scripts\python.exe -m pip --isolated --disable-pip-version-check install --no-index --only-binary=:all: --no-deps .cache/dependency-check/websockets-17.3-cp312-cp312-win_amd64.whl
.\backend\.venv\Scripts\python.exe -m pip check
```

Installation succeeded; pip check reported no broken requirements; `websockets.asyncio.client` and Uvicorn's `WebSocketsSansIOProtocol` imported with version 17.3. Pip warned that it could not clean several sandbox temporary directories; no global package change or cleanup outside the workspace was attempted. No frontend or Google SDK dependencies were added. Existing lock pins are preserved with one appended WebSocket pin. The frontend package script now discovers all existing `src/*.test.js` tests.

## Official specification consulted

Checked 2026-10-26:

- [Gemini 3.8 Live model](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live): stable Live target; audio response modality, no structured outputs/thinkingLevel, proactive audio cannot be disabled. Voice therefore cannot inherit the text adapter's strict verbatim JSON validation.
- [Live WebSocket reference](https://ai.google.dev/api/live): Developer API endpoint `wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent`, setup and session events.
- [Audio capabilities](https://ai.google.dev/gemini-api/docs/live-api/capabilities): PCM formats, manual activity markers, multipart audio and optional transcription.
- [Session management](https://ai.google.dev/gemini-api/docs/live-api/session-management): uncompressed audio-only 15-minute session, approximately 10-minute connection; app's five-minute cap is smaller.
- [Pricing/data use](https://ai.google.dev/gemini-api/docs/pricing) and [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits): actual tier/quota/billing is account-specific and not verified here.
- [PyPI websockets 17.3](https://pypi.org/project/websockets/17.3/): exact dependency metadata.

This differs from the described class OpenAI/WebRTC/two-model example: audio uses browser Web Audio and a FastAPI WebSocket relay; one Live model is the future audio-to-audio target, while text Chat stays independent. There is no automatic second-model pipeline or claim of WebRTC equivalence. No class handout defining its exact model roles was found in this repository.

## Verification checkpoint

Backend command from `backend/`: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`. Frontend from root: `npm --prefix frontend test` and `npm --prefix frontend run build`. Final totals are recorded after the final regression run below. Backend tests use temporary databases and mock event streams; no real credential fixture or network inference is used.

An initial backend invocation from the root failed because the existing tests import modules relative to `backend/`. A corrected restricted invocation then stalled in Windows asyncio's socketpair initialization before application code; the same suite ran successfully with local socket permission. Starlette emitted an HTTPX deprecation warning; no unapproved httpx2 replacement was installed. A frontend fake-timer test initially failed because the test clock retained fired timer IDs; fixing the test fixture resolved it.

Browser checks used separate ignored `.cache/verification/fifer-voice-browser.sqlite3`: keyboard Start reached real local WebSocket mock-ready, Support stopped it immediately, backend-off voice showed error while static Support opened. A disposable browser tab replaced getUserMedia with a generated oscillator stream: actual AudioWorklet capture → local relay → mock PCM tone → playback → ready (1/5 turns) succeeded with no browser error/warning logs. Stop/Leave exited immediately. No hardware microphone or room audio was captured. The test-only browser override was removed by closing that tab. Screenshots are ignored local evidence, not provider/audio evidence.

Unverified: real Gemini handshake/access, generated speech/latency/audio quality, actual microphone permissions/hardware compatibility, full 300-second browser run, cross-browser/screen-reader coverage, account billing and instructor-specific rubric compliance. Unit tests use shortened clocks for boundary coverage; no actual five-minute timing observation is claimed. A real provider transport remains deliberately unimplemented/disabled.

Final observed results: **54 backend tests passed (15 new voice tests), 35 frontend tests passed (9 new voice tests), Vite build passed, pip check passed, npm ls --depth=0 passed, git diff --check passed** after trimming two documentation EOF blank lines. The normal backend was restored on port 8000 without resetting local history; `/api/voice/config` reports mock mode, `live_calls_enabled:false`, the approved model/limits and no audio/transcript saving. `/api/health` reports `model_enabled:false`. Frontend remains on port 5173. Branch remains master and no staging/commit/push occurred. Real `.env`, venv, browser-test database, screenshots and dependency-review artifacts are ignored; `backend/.env` is untracked.

## Files changed in this increment

New source/test/documentation files: `backend/live_voice.py`, `backend/voice.py`, `backend/tests/test_voice.py`, `frontend/public/audio/voice-capture-worklet.js`, `frontend/src/audio/pcm.js`, `frontend/src/voice.js`, `frontend/src/voice.test.js`, `frontend/src/components/VoicePanel.vue`, `docs/voice.md`.

Modified files: `AGENTS.md`, `AI-USE.md`, `README.md`, `backend/.env.example`, `backend/main.py`, `backend/storage.py`, `backend/requirements.txt`, `backend/requirements.lock.txt`, `frontend/package.json` (test script only), `frontend/vite.config.js`, `frontend/src/App.vue`, `frontend/src/components/HistoryPanel.vue` (quota disclosure), `docs/safety.md`, `handoffs/current.md`.

Earlier uncommitted grounding/text files were preserved; their presence in Git status does not mean V2 created them. The real `.env` and frontend dependency lock were not changed. Ignored local CHECK/verification scripts, wheel/report, screenshots, logs and test database are excluded from project-source changes. No runtime audio/transcript files were created.
