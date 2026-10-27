# Fifer — Assignment 3

Fifer is an independent coursework prototype using fictional scenarios. It offers an application-controlled 5-4-3-2-1 sensory activity. It does not diagnose, provide therapy, claim clinical effectiveness, or imply human monitoring.

## Part 3.2 acceptance and submission review

Current implementation rerun: **62/62 backend tests passed**, including the corrected setup-disconnect teardown test; that focused case then passed 25 additional consecutive runs. The test now drives the ASGI WebSocket endpoint directly for the abrupt setup disconnect, verifies upstream cleanup/reservation release, and uses TestClient only for the fresh follow-up session. Frontend 49/49, build, pip and npm checks pass. The earlier 60-pass/1-error run remains recorded as the trigger for this fix. See [current report](report.md).

[Current report](report.md), [acceptance matrix](docs/verification/part-3-2-acceptance.md), [actual submission requirements](docs/assignment-3-submission-requirements.md) and [redacted prompt/change/test log](prompts/assignment-3-2-evidence.md) describe the latest working-tree evidence. The previous [Part 3.1 report](report-3-1.md) is preserved byte-for-byte; its no-implementation statements are historical.

Verified fictional acceptance: 61 backend tests, 49 frontend tests, build, pip check, npm ls and git diff --check passed. Browser/SQLite checks exercised fixed flow/explicit Finish, optional sensory input, Stop versus completion, refresh/history/Delete/Clear, consent and static Support with FastAPI stopped. Mock voice denial/synthetic capture/Mute/End and automated failure/late/cleanup checks passed. A 390×844 viewport/keyboard smoke check passed, not full accessibility or physical-phone review. Active skill time was 31.021 s, separately setup 32.528 s, paused 5.941 s and Support 0.109 s: one fast automation run, not human usability evidence or a guarantee of under-90-second completion.

Normal text runtime remains a local mock, but the approved `gemini-2.5-flash` adapter is now selectable through two explicit server-side process gates; the key alone cannot activate it. All provider-path evidence is still HTTPX mock transport. The real Live voice connector remains deliberately unimplemented/disabled. No paid/live observation exists, so the assignment's actual model-contribution demonstration remains unfinished. Submitted-version commit: Not yet available; baseline HEAD does not identify current uncommitted changes. New links need publication after scope review/approved commit/push before Canvas upload. Recordings, detailed Figma screens, hardware/live-model tests and full accessibility remain pending. Nothing here grants a provider call, commit or push.

## Current implementation

The local Vue/JavaScript UI runs with FastAPI/Python and project-local SQLite. It implements start choices → See 5 → Feel 4 → optional check-in → Hear 3 → Smell 2 → Taste 1 → explicit Finish. Sensory selections and the check-in are optional, skippable, and unscored. No typing, touching, finding a smell, eating, or drinking is required.

Pause requires explicit Resume. Stop/Leave exits immediately. Emergency Support opens from static frontend content even when FastAPI is unavailable. The user approved wording based on “Please contact 911 for emergency support.” It is text only, with no calling/messaging handler. Instructor approval is not verified. The UI displays a coursework-prototype notice.

SQLite saves fictional session IDs, skill, UTC start/end/update timestamps, active/paused/stopped/completed status, saved step, optional after-Feel check-in, and separate setup/active/pause/support milliseconds. Sensory selections stay only in tab memory and are never sent or stored. No personal narratives or credentials belong in storage. Stop clears transient sensory choices and saves stopped status; its permitted check-in metadata remains until deletion. Only explicit Finish saves completed status and contributes to recent-skill suggestions. Saved unfinished sessions can be chosen after refresh/restart and always open paused; Resume is explicit. Closed-browser downtime is not added to exercise timing.

Message saving is **opt-in, OFF by default**. The approved retention policy is **until explicitly deleted or cleared**, for both session metadata and opted-in fictional messages. Local history and privacy lets the user review saved metadata/messages, toggle future message saving, Delete a session with its linked conversation/messages, or Clear all. Clear all deletes every session/check-in/duration, conversation/message, and derived recent-skill history, discards this tab's pending writes, and resets message opt-in to OFF. Turning OFF alone keeps existing messages. The empty schema/database and a nonpersonal write-generation counter remain; Clear all is an application-data deletion, not a promise to erase external backups.

The optional Chat view defaults to a **local mock**, retrieving reviewed app-help paragraphs. FastAPI can select the approved `gemini-2.5-flash` adapter only when both server-side activation gates are deliberately set; no call was enabled or made in this checkpoint. Optional Voice exercises microphone/playback and a FastAPI WebSocket with a **local synthetic-tone mock**, not speech understanding or Gemini output. The grounding UI creates no messages. There are **no observed real model calls or emergency-contact integrations**. The separate approved Live target remains `gemini-3.8-live`; its real connector is out of scope here.

The project root is this repository. Do not create another Fifer directory or copy Expedia Lite files. Only architecture and documentation practices are conceptually reused.

## Optional text assistant: mock-only checkpoint

Choose **Chat · optional text assistant** from start choices or after explicit Finish. Chat does not replace or interrupt the fixed grounding exercise. Questions must be fictional, non-emergency app/skill questions without personal or sensory narratives. The Chat screen displays the backend-reported mode: the normal mode is a labelled local mock; a separately authorized run can display the Gemini text mode. Both paths are restricted to the explicit collection in `backend/chat_content.py`. No arbitrary files, web pages, private records, prior messages or sensory answers are retrieved. There is only one supported skill. A fixed scope response handles unrelated questions, and a fixed fallback handles timeout/invalid output/failure. Stop, Support, privacy navigation and leaving Chat cancel/ignore pending replies; no automatic retry occurs.

Approved text request settings are `gemini-2.5-flash`, 300 output tokens, 15 seconds, 5 attempts per chat session and 20 per anonymous browser per UTC day. The backend reserves attempts atomically before generation, including failed/out-of-scope attempts; duplicate request IDs are rejected without another attempt. New chat resets only its five-attempt session limit; reload preserves the session ID/count. The current mock returns at most one reviewed paragraph (also capped at 300 characters), not Gemini output. The HTTPX Gemini adapter, lazy `GEMINI_API_KEY` loader, FastAPI route and Chat UI are now wired end-to-end and pass offline mock-transport tests. Normal startup remains mock and does not read the key. A real run requires **both** process environment values `FIFER_TEXT_PROVIDER=gemini` and `FIFER_TEXT_LIVE_AUTHORIZED=true`; invalid/partial combinations fail closed at startup, and the browser cannot set them. Live token usage, account/model access, provider behavior and costs remain unverified.

The browser keeps a random UUID in localStorage and only a chat-session ID in sessionStorage; neither contains message bodies. This is **not a verified per-person limit**, and clearing browser data can create a new identity. The backend stores a SHA-256 hash of the UUID with a UTC date/count, rather than the UUID itself. Today's operational counters remain after Delete/Clear so deleting history does not bypass today's quota. Older counters are removed on a later UTC day's text request, not by resetting history on startup. These request/token limits are **not a dollar spending cap**. Before any separately approved live call, review the actual Google project billing, quota and available spending controls; do not assume an alert or this app guarantees a hard currency cap.

**Context sharing starts OFF**, independently of message saving. If explicitly selected, a preview shows only the actual local completed-session count, latest completed skill and its optional check-in; the backend reads those allowlisted values itself. No profile exists, and no history is invented. Turning sharing off or opening Support while waiting cancels the tab's request; later replies are ignored. Saved chat messages are not fed back as model context.

The existing message-saving opt-in is preserved (OFF on a new database and after Clear; an existing ON choice is not reset). Eligible in-scope fictional question/reply pairs are saved only if opt-in is ON both before and after the request. Opting out keeps old messages. History reviews/deletes chat sessions and linked messages, as well as grounding history. Clear removes all session/message history and resets saving OFF, retaining only the daily quota counters, schema and generation marker described above. Chat metadata (ID, browser hash, start/end, active/stopped status, attempt count and request IDs) is retained until Delete/Clear even when message saving is OFF. No sensory narratives, audio, transcripts or credentials are stored by the Chat UI. A failed write says no save was confirmed.

Earlier offline-adapter checkpoint (historical): 26 frontend tests, 39 temporary-database backend tests and the Vite build passed. The preceding mock increment's browser quota/reload, sharing OFF, opt-in/review/Delete/Clear and backend-off Support checks passed in a separate ignored test database. The adapter adds no UI changes or live activation. See [text-chat implementation and verification](docs/text-chat.md) for the safe activation boundary, REST references, current model-access caveat, actual evidence and remaining limits.

## Optional voice: V2 mock checkpoint

Voice is available **inside the existing Chat screen**, alongside its working text composer, and through the standalone Voice choice at start/after Finish. Confirm fictional, non-emergency use, then **Start mock voice** explicitly requests audio-only microphone permission. Tracks stay muted while connecting; active status appears only after the backend confirms mock provider setup. **Unmute** begins a manual turn; **Send turn / Mute** stops capture. The local backend returns a synthetic tone, not Gemini speech. Blocked playback shows **Enable assistant audio** for an explicit recovery click. Interruption, End, Support, leaving or hiding the tab clears playback/capture and ends voice; restart is explicit. Voice failure never disables the text composer or static Support. Fixed grounding remains separate.

**Mute** stops microphone forwarding/tracks and sends one manual-VAD `activityEnd` if an input turn was active; it keeps the session and assistant playback running. **Unmute** begins the next turn once the current response finishes. **End** releases microphone, worklet, playback, AudioContext, timers and the app socket; FastAPI cancels setup/relay tasks and closes its mock upstream. Duplicate Starts/repeated Ends are ignored, late permission/setup/audio results cannot revive a closed session, and every accepted Start creates fresh audio/socket/provider resources. Both browser and backend enforce the fixed 300-second maximum independently; abrupt page/process exit cleanup remains best-effort. No audio/transcripts are saved and no real provider call is enabled.

The approved Live target is `gemini-3.8-live`. No real upstream transport is wired: `GeminiLiveProvider` refuses before reading a key or connecting. No key/environment switch enables calls. No audio or transcripts are stored, even with text saving ON. Voice shares no profile/check-in/history. Limits: 300 wall-clock seconds, five turns, 20 seconds/utterance, 15 seconds/response audio, 10-second setup/15-second response deadlines, no retries, and two accepted starts/browser/UTC day. Failed setup after reservation counts. Only browser hash/date/count are retained for quota; today's count survives Clear, older buckets are removed on a later voice start. This is not a verified per-person limit or dollar cap. See [voice implementation, dependency review and verification](docs/voice.md), including the deliberately unimplemented real transport and unverified device/provider behavior.

## Run locally (HTTP and mock WebSocket)

Use two PowerShell terminals from the repository root after the setup below:

```powershell
.\backend\.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000 --ws websockets-sansio
```

```powershell
npm --prefix frontend run dev
```

Open [Fifer locally](http://127.0.0.1:5173/). Vite proxies `/api` to localhost port 8000. SQLite initializes additively at `backend/data/fifer.sqlite3`, independently of the shell's current directory. Startup never clears history. The file and SQLite sidecars are ignored by Git. `FIFER_DB_PATH` can select a separate test database; leave it unset for normal use.

Navigation, Pause/Stop, and static support never wait for storage. A failed save shows **Unsaved changes**, with Retry saving or Discard unsaved changes. Snapshots retry in order and are acknowledged only after successful server persistence. Unsaved snapshots remain only in the open tab; reload/close can lose them, including an unsaved Stop/Finish. The last acknowledged checkpoint remains resumable. Progress is checkpointed on actions and approximately every five seconds while active/paused; support opens without a storage request and its duration is captured on Return/Stop. Background timer throttling or abrupt closure can lose time since the last acknowledgement. No closed-page downtime is inferred. Discard unsaved changes removes pending tab-only snapshots; it does not delete already saved history.

The frontend server must remain available for a fresh page load; backend-independent support is not an offline deployment claim. Stop either development server with Ctrl+C in its terminal.

## Approved dependencies and setup evidence

Checked and installed locally on 2026-10-22 using Python 3.12.14 x64, Node 24.20.0, and npm 11.19.0:

| Package | Exact direct version | Purpose |
| --- | --- | --- |
| vue | 3.5.44 | Reactive JavaScript UI |
| vite | 8.3.4 | Local server and production build |
| @vitejs/plugin-vue | 6.0.10 | Vue single-file compilation |
| fastapi | 0.156.0 | Local HTTP API |
| uvicorn | 0.54.0 | ASGI server |
| pydantic | 2.14.1 | FastAPI validation dependency |
| httpx | 0.28.1 | API tests and dormant offline-tested text adapter; no real model call |
| websockets | 17.3 | Approved V2 local WebSocket support; no real provider transport activated |

The project venv's bootstrap pip 25.0.1 advisory gate was resolved by the user's approved upgrade to pip 26.2. The Codex-managed base Python and global packages were not changed. Resolved registry artifacts were inspected before installation: 17 Python wheels and 35 applicable Windows npm packages passed digest checks; Windows native bindings matched the runtime/architecture. Registry advisory queries listed no advisories for the inspected versions at that time. This is a point-in-time check, not a security guarantee.

No applicable dependency install hooks were found. The optional macOS-only `fsevents` hook was inapplicable; publishing-only hooks were distinguished from dependency install hooks. npm installation used `--ignore-scripts`. See [Part 3.2 evidence](docs/part-3-2.md) for the CHECK → TAKE ACTION → VERIFY record and limitations.

`backend/requirements.txt` pins direct dependencies; `backend/requirements.lock.txt` records 18 application packages including the later approved websockets pin. `frontend/package-lock.json` records the npm graph, including optional other-platform entries. Local environments, dependencies, caches, and build output are ignored. No new dependency is approved by these instructions alone; follow AGENTS.md before changing versions or adding packages.

## Recreate from a clean checkout

The current `backend/.venv` was created using **Codex-managed CPython 3.12.14**. Its machine-specific base path is not required by the project and the venv is not portable or committed. A normal compatible 64-bit CPython 3.12 installation with `venv` support can recreate it. If the managed base moves, recreate the venv rather than copying it.

After the dependency CHECK/approval required by AGENTS.md, run from the repository root:

```powershell
py -3.12 -m venv backend/.venv
.\backend\.venv\Scripts\python.exe -m pip --isolated --disable-pip-version-check install --only-binary=:all: --index-url https://pypi.org/simple pip==26.2
.\backend\.venv\Scripts\python.exe -m pip --isolated --disable-pip-version-check install --only-binary=:all: --index-url https://pypi.org/simple -r backend/requirements.lock.txt
.\backend\.venv\Scripts\python.exe -m pip check
npm ci --prefix frontend --ignore-scripts --registry https://registry.npmjs.org/ --no-audit --no-fund
npm ls --prefix frontend --depth=0
```

If `py` is unavailable, replace `py -3.12` with the absolute path to that installation's `python.exe`. No activation or PATH change is required. Use the project interpreter for every pip command; install nothing globally. Other architectures/platforms need their own binary and script checks. Recheck advisories before a later installation. Do not run automatic dependency fixes or silently change the pins.

## Verify

From the repository root:

```powershell
npm --prefix frontend test
npm --prefix frontend run build
.\backend\.venv\Scripts\python.exe -m pip check
npm ls --prefix frontend --depth=0
```

From `backend/`:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

Earlier storage checkpoint (historical): **16 Node tests and 12 API/SQLite tests passed**, and the Vite build passed. Every backend test uses a disposable temporary database and runs application lifespan initialization against that database. Browser checks used a separate ignored `.cache/verification/fifer-storage-browser.sqlite3`, not normal project history: refresh/restart resume, optional check-in and separate clocks, explicit completion, stopped status, opt-in/review, Delete/Clear, unsaved failures, static support, and Retry recovery passed. See [storage verification](docs/part-3-2-storage.md) for commands, screenshots, and limits. Earlier import, `pip check`, and `npm ls` results remain recorded in the [initial UI checkpoint](docs/part-3-2.md). No dependency changed during the storage step.

The intended pace remains about 60–75 active seconds and under 90. The current automated acceptance measured 31.021 active seconds, with setup, pause and Support stored separately; no human timing study is claimed. There is no forced advance/completion or countdown pressure.

## Project documents and Git

- [AGENTS.md](AGENTS.md): project rules and approval gates.
- [Part 3.1 report archive](report-3-1.md), [research](docs/research.md), [design](docs/design.md), and [flow diagram](docs/mockups/fifer-assignment-3-1-flow.png): preserved design evidence; detailed Figma/Figma Make screens remain pending.
- [Safety](docs/safety.md), [AI use](AI-USE.md), [Part 3.2 evidence](docs/part-3-2.md), and [current handoff](handoffs/current.md).
- [SQLite storage checkpoint](docs/part-3-2-storage.md): approved policy, schema/endpoints, failure behavior, and verification.

Repository: [nikhilrajk21/Fifer](https://github.com/nikhilrajk21/Fifer). Branch: `master`. Part 3.1 submission commit: `615ac73aaa933f8c3ce0004079f0179a133b35b1`. Current HEAD: `a8edc32df96170bed09cd233cc3a5c2248e0adca`, the pushed merge preserving checkpoint `0b4c453` and report update `1e52473`. Historical milestone prose describes those earlier states. The current grounding, mock text/voice and submission-documentation increments are uncommitted and unstaged; baseline HEAD is not the submitted-version commit. No commit or push occurred in this turn; proposed-scope approval is still required.
