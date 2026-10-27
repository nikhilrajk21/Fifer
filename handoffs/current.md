# Fifer — current handoff

## Current documentation/submission review checkpoint

Resolved test-boundary result: the documentation-time full suite's 60-pass/1-CancelledError setup-disconnect result prompted a direct-ASGI teardown test. The revised full backend suite passes 62/62; the focused disconnect/cleanup/restart test then passed 25 consecutive runs. Frontend 49/49, build, pip and npm checks pass. The direct test verifies the mock upstream closes and the browser reservation releases; it does not verify real Gemini Live cleanup. The existing Starlette TestClient/httpx deprecation warning remains, and no new dependency was added.

Root report.md now describes Part 3.2; report-3-1.md is a byte-for-byte archive of the previous root report. Existing research/3.1 mockup images remain intact. Current Canvas Part 3.2/overview instructions were actually read: one report upload, repo/submitted commit/evidence links and curated redacted AI evidence with a failed/revised approach. Model contribution is required; speech is optional. See [requirements](../docs/assignment-3-submission-requirements.md).

Use [acceptance](../docs/verification/part-3-2-acceptance.md) for verified results: 61 backend/49 frontend tests, build/pip/npm/diff checks pass; browser/SQLite fixed flow, optional responses, Stop versus completion, backend-off Support, refresh/history/consent/Delete/Clear; synthetic voice/denial/Mute/End plus automated lifecycle/failure mocks; keyboard/mobile smoke. One completed automated run: active 31.021 s, setup 32.528 s, pause 5.941 s, Support 0.109 s. Not human usability/clinical evidence. No paid/live observation exists; the actual Live connector remains disabled/unimplemented, and actual model demonstration remains unfinished.

Selected redacted requests, code/test links and revised setup/End cancellation/failed SQL quoting approach are in [prompts](../prompts/assignment-3-2-evidence.md). The actual mobile See screenshot was copied unchanged from existing fictional acceptance evidence into docs/verification/part-3-2-acceptance/mobile-see.png. No screenshot, approval, model result or submitted hash was invented. The owner relayed instructor sensory feedback and Gemini substitution approval; independent instructor support-wording approval remains unverified.

Branch master, baseline HEAD a8edc32df96170bed09cd233cc3a5c2248e0adca. These uncommitted changes are not identified by that baseline and have no submitted-version commit yet. Nothing staged/committed/pushed/submitted. Review scope first; after explicit approval record the real commit and publish/verify links before Canvas upload. Keep .env/credentials/runtime DB/logs/audio/caches/node_modules/build/venv out of Git. No real provider activation, dependency or app-feature change is authorized by this documentation update. Older sections below retain historical evidence.

## Latest: separate Mute / Unmute / End lifecycle (mock only)

Mute stops forwarding/capture and sends one activityEnd for the active manual VAD turn, preserving socket and assistant playback. Unmute starts the next turn after response completion. End invalidates generations, releases microphone/worklet/output/context/socket/timers and cannot be undone by a late callback. Duplicate Start while busy and repeated End are ignored; each accepted Start creates fresh resources. FastAPI now races provider setup against End/disconnect and cancels/closes promptly, and enforces its own maximum including setup. Empty-turn Mute no longer causes a session error. No audio/transcripts saved; no real provider call, install, commit or push.

Mock tests cover lifecycle routes, resource faults, old capture callbacks after a new turn, canceled late permissions/connect/setup, repeated controls, fresh sessions, playback preserved by Mute, and client/server duration bounds. Final results: 49 frontend tests, 61 backend tests, build and git diff --check pass. Updated normal mock-only backend restarted without resetting history. See [voice evidence](../docs/voice.md); earlier browser checks below are historical. Hardware/actual Gemini VAD/speech, abrupt process death and a full five-minute elapsed browser run remain unverified. Manual VAD documentation was checked: activityEnd, not audioStreamEnd. The existing model/limits/quotas/text/Support boundaries remain unchanged.

## Latest: voice inside Chat (mock only)

The existing text composer remains working alongside embedded VoicePanel. Explicit Start requests getUserMedia({audio:true,video:false}) before opening the local socket; tracks are muted until setup confirmation and Unmute. FastAPI adds setup_confirmed:true only after mock setupComplete. Voice reports permission/connecting/active/muted/closing/closed/failure; blocked audio has an Enable assistant audio user-gesture recovery with a one-second RAM queue. Interruption/Stop/Support clears queued and scheduled audio and closes voice; real transport remains disabled. Text sharing/saving does not apply to voice, and a voice failure does not disable text. No new dependency, provider call, credential read, commit or push.

Final checks: 42 frontend tests, 56 backend tests, production build and git diff --check pass. Disposable browser/DB verification observed text answers after mocked microphone denial; synthetic PCM round trip with explicit blocked-playback recovery; and text controls/static keyboard Support after backend loss. All browser overrides were removed by closing the test tab; normal local backend restored, normal history preserved. See [current voice evidence](../docs/voice.md) for files/commands/limitations. No real hardware microphone, actual autoplay permission policy, Gemini speech or costs were verified. The remaining content records previous checkpoints.

## Latest V2 mock-voice checkpoint — 2026-10-26

The latest user approval authorizes the proposed Gemini Live substitution and mock-only increment, including `gemini-3.8-live`, limits and conditional local `websockets==17.3` installation after CHECK. These decisions supersede historical voice-unimplemented/pending-scope statements below. Text remains separate (`gemini-2.5-flash` target). No real text/Live provider call, commit or push is authorized or performed.

Implemented optional Voice outside grounding; browser AudioWorklet PCM capture/playback; FastAPI `/api/voice` with local mock event stream, fixed backend setup/instructions, independent deadlines/quotas and cleanup. Mock output is a labelled synthetic tone, not a spoken answer. `GeminiLiveProvider` fails before any key/network access; the real transport remains deliberately unimplemented. No hardware microphone was used in verification and no audio/transcripts were stored. Existing `backend/.env` was not read or changed.

Approved bounds: 300 wall-clock seconds; five turns; 20 seconds/utterance; 15 seconds/output audio; 10-second setup/15-second response deadlines; no retries/reconnection; one concurrent session per browser in a single-worker local app; two accepted starts/browser/UTC day. Only browser hash/date/count is stored in additive `voice_daily_usage`; today's counters survive Delete/Clear, older counts are removed on a later voice start. No profile/check-in/history sharing or text-opt-in voice recording. Browser identity is bypassable by browser-data clearing, not a verified person or dollar cap.

Dependency CHECK passed exact wheel/hash/native tags/CLI-entry-point review, no runtime dependencies and empty PyPI/OSV advisories at inspection. Installed only in backend/.venv; pip check and Uvicorn/WebSocket imports pass. Pip reported sandbox temp-directory cleanup warnings; no external cleanup was attempted. Frontend deps unchanged; test script now discovers all test files. See [voice.md](../docs/voice.md) for commands, official references, evidence and limitations. Backend runner initially stalled in sandbox Windows asyncio socketpair initialization; permitted local execution passed. No dependency upgrade was made for Starlette's HTTPX deprecation warning.

Browser verification used ignored `.cache/verification/fifer-voice-browser.sqlite3`, not normal history. Keyboard mock Start reached ready, Support ended voice, backend-off voice errored while Support still opened. In a disposable tab, synthetic getUserMedia audio exercised AudioWorklet → relay → mock tone → playback → ready (1/5); Stop/Leave exited immediately and browser logs had no errors/warnings. Closing the test tab removed its override. Real model/audio quality/access/billing, hardware mic permissions, full-duration/cross-browser/screen-reader checks remain unverified. The fixed grounding tests remain regression coverage; no model-controlled steps were introduced.

Final results: 54 backend tests, 35 frontend tests, build, pip check, npm ls and git diff --check pass. Normal mock-only backend is restored on 8000 without resetting history; frontend remains on 5173. Voice config reports live_calls_enabled:false and approved limits; health reports model_enabled:false. Current branch/HEAD remain master / a8edc32df96170bed09cd233cc3a5c2248e0adca. Existing uncommitted work is preserved; nothing was staged. See docs/voice.md for full file list, evidence and limits. Historical checkpoints follow.

## Earlier checkpoints (historical)

Updated: 2026-10-26. This repository is independent of Expedia Lite.

## Current mock-text checkpoint

Latest adapter increment (2026-10-26): the user authorized the bounded FastAPI-mediated Gemini adapter with mocked verification only. `backend/gemini_text.py` and its tests use the existing HTTPX dependency. The adapter is now wired into application startup and the Chat UI, but normal startup still selects `MockTextProvider` and does not read a key. Both backend-process values `FIFER_TEXT_PROVIDER=gemini` and `FIFER_TEXT_LIVE_AUTHORIZED=true` are required to select the real transport; partial settings fail closed and the frontend cannot set them. `GEMINI_API_KEY` remains the only key name; loader tests use temporary fictional fixtures, never the real file. The request uses fixed HTTPS/header authentication, 300 output tokens, 15 seconds, one candidate, structured curated answer/source output, no tools/redirects/retries, and safe failure. Existing quotas, consent/retention, Stop/Support and late-output guards are unchanged. No real call has been authorized or made.

Final tests passed: 39 backend tests, 26 frontend tests, Vite build. New adapter tests run through FastAPI with HTTPX MockTransport and temporary databases. No real provider call/authentication/token/billing result is claimed. Official Google documentation now limits 2.5 access to prior active users; this account's access is unknown and the model ID was not changed. Any live activation, test call or model replacement still needs explicit user approval. See [current adapter evidence](../docs/text-chat.md).

Actual branch: master. Actual HEAD: `a8edc32df96170bed09cd233cc3a5c2248e0adca`, the pushed merge preserving checkpoint `0b4c453` and report update `1e52473`. The grounding scene/input changes and this mock-chat increment are uncommitted and unstaged. Historical Git/implementation statements below describe their earlier checkpoints.

The user approved bounded fictional, non-emergency text chatbot/RAG with target model `gemini-2.5-flash`, 300 output tokens, 5 attempts/chat session, 20/anonymous browser/UTC day, 15 seconds and no automatic retries. FastAPI/Chat now select the adapter only when both server-process gates are explicitly set; normal startup remains mock and a key alone is insufficient. No real provider call is authorized or observed. Gemini Live voice remains separate and its real connector is unimplemented. The user approved browser-local anonymous identity and explicitly accepted that clearing browser data can reset its effective limit; no verified person/account identity is claimed.

Chat is optional at start or after Finish. It retrieves only `backend/chat_content.py`, a curated collection derived from existing app/skill/safety rules. It displays the backend-reported mock/Gemini text mode, citations, and static fallback/scope responses. No SDK or browser-controlled real-call toggle exists. Runtime activation requires `FIFER_TEXT_PROVIDER=gemini` and `FIFER_TEXT_LIVE_AUTHORIZED=true` in the backend process; invalid/partial settings fail closed. The real key file was not read or changed. Fixed grounding, Stop and static Emergency Support remain independent.

Context sharing is a separate OFF-by-default checkbox, with a preview of actual completed-session count/latest skill/optional check-in only. No profile, sensory answer, previous chat, arbitrary file or web content is supplied. Saving follows the previously approved opt-in/retention/deletion rule; eligible fictional pairs are saved only if consent remains ON and the chat is still active at response time. History can review/delete mock chats. Clear removes chat/session/message history and resets message saving OFF. Anonymous daily quota hashes/date/counts remain through the UTC day and older buckets are removed on a later day's request, so Clear/New chat/restart cannot reset today's quota. No dollar spending cap is claimed.

New backend tables are additive/repeatable and never reset local history on startup. Mock API tests use TemporaryDirectory. Browser verification uses a separate ignored test database, not normal history. See [text-chat evidence](../docs/text-chat.md) for current results and limitations. Current support copy remains the user's static 911 text; instructor approval is not verified. Do not install dependencies, enable provider calls, commit or push without the respective approval.

The remainder is preserved historical storage-checkpoint context.

## Git and authorization

Branch: `master`. Origin: https://github.com/nikhilrajk21/Fifer.git. HEAD: `003245f47958474e300920bb4b0127d275bedff4`. Part 3.1 submission: `615ac73aaa933f8c3ce0004079f0179a133b35b1`. Part 3.1 report/research/design/mockup evidence is preserved. Current Part 3.2 work is uncommitted; nothing is staged. No commit/push is authorized by this checkpoint.

The first UI checkpoint passed before SQLite work began. The user then explicitly approved:

- Fictional message saving: “Opt-in, OFF by default.”
- Retention: “Until the user explicitly deletes or clears it.”
- Clear all: all sessions, check-ins, durations, messages, recent-skill history, and message opt-in reset to OFF. Per-session Delete removes linked conversations/messages.

The latest request also authorized fictional session IDs, skill, UTC start/end, active/paused/stopped/completed status, saved step, optional after-Feel check-in, and separate setup/active/pause/support durations. Never store sensory selections, personal narratives, or credentials. No new dependency or model call was authorized/added. Exact future model contribution remains unresolved.

## Current implementation

Vue owns start → See 5 → Feel 4 → optional check-in → Hear 3 → Smell 2 → Taste 1 → explicit Finish. Choices remain optional/unscored, and there are no touching, scent-finding, consumption, or disclosure requirements. Pause/Resume, immediate Stop/Leave, dusty blue/lavender styling, keyboard controls, and static support remain. Finish now deliberately focuses the heading.

FastAPI persists allowlisted metadata to `backend/data/fifer.sqlite3`, initialized additively without clearing existing data. The database and sidecars are ignored. Ordered, revisioned snapshots save on actions and approximately five-second checkpoints while active/paused. Support opens without a storage request; elapsed support time is captured on Return/Stop. Unsaved writes remain in tab memory with a sticky warning, Retry, and Discard. Closing/reloading can lose unacknowledged changes; it never creates an acknowledged completion. Last saved progress remains resumable and opens paused. Closed-browser downtime and sensory selections are not restored.

Only explicitly saved completed sessions produce recent-skill suggestions; stopped sessions do not. Local history reviews metadata and opted-in fictional messages. Turning OFF stops future message saving without deleting existing messages. Delete cascades one session's linked messages; Clear all deletes all application history, discards pending tab writes, resets opt-in OFF, and invalidates old-generation writes. The empty schema/database and nonpersonal generation counter remain. No external-backup erasure is promised.

Conversation/message tables and an opt-in-protected message endpoint are ready; there is no model or chat composer. The grounding UI creates no messages. Only a labelled fictional test fixture was added to the isolated browser-test database, never the normal project database.

Emergency Support remains static frontend text based on the user's direction: “Please contact 911 for emergency support.” No phone handler, automatic calling/messaging, classifier, model, or storage prerequisite. Instructor wording/jurisdiction approval has not been verified. Coursework notices remain visible.

## Evidence

[Storage checkpoint](../docs/part-3-2-storage.md): 16 Node tests and 12 API/SQLite tests passed, plus the Vite production build. Backend tests use disposable temporary databases with real lifespan initialization. They cover fixed progression, pause/resume durations, explicit completion versus Stop, additive restart persistence, opt-in OFF/ON/OFF, SQL-injection-as-literal text, forbidden fields, replay/conflict handling, cascade deletion, Clear/reset, stale-write fencing, and failed database writes/clear.

Browser tests used the isolated ignored `.cache/verification/fifer-storage-browser.sqlite3`: refresh/resume at Feel; real FastAPI restart preserving records; check-in and separate clock review; optional recent completion; stopped sessions; fictional message review after opt-out; actual backend-off unsaved navigation/support; Retry preserving stopped status; per-session Delete; and Clear with OFF/reset surviving refresh. Read-only SQLite queries confirmed cascade counts and zero application records after Clear. Normal local history was not reset; no normal database existed before this step.

The final service was restored to the default project database, newly initialized with no sessions/messages and opt-in OFF. Frontend `http://127.0.0.1:5173/`, backend `http://127.0.0.1:8000/`. README gives restart/recreation commands. These are development processes, not installed services.

## Environment and next steps

Previously approved direct versions remain Vue 3.5.44, Vite 8.3.4, plugin-vue 6.0.10, FastAPI 0.156.0, Uvicorn 0.54.0, Pydantic 2.14.1, HTTPX 0.28.1. Project CPython 3.12.14 has a Codex-managed base; local pip 26.2 was separately approved earlier. No manifest/lockfile, global installation, or package changed in this storage step. sqlite3/unittest and Node's built-in test facilities were sufficient.

Stop after reporting this checkpoint. Any commit/push needs proposed-scope approval. Future model work needs its precise role/failure policy approved. Instructor crisis wording, detailed Figma/Figma Make screens, rubric review, timed usability, full accessibility/screen-reader and cross-browser review remain pending. Earlier no-database/pending-retention statements describe historical checkpoints, not current authorization.
