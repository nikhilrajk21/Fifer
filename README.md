# Fifer — Assignment 3

Fifer is an independent coursework prototype using fictional scenarios. It offers an application-controlled 5-4-3-2-1 sensory activity. It does not diagnose, provide therapy, claim clinical effectiveness, or imply human monitoring.

## Current implementation

The local Vue/JavaScript UI runs with FastAPI/Python and project-local SQLite. It implements start choices → See 5 → Feel 4 → optional check-in → Hear 3 → Smell 2 → Taste 1 → explicit Finish. Sensory selections and the check-in are optional, skippable, and unscored. No typing, touching, finding a smell, eating, or drinking is required.

Pause requires explicit Resume. Stop/Leave exits immediately. Emergency Support opens from static frontend content even when FastAPI is unavailable. The user approved wording based on “Please contact 911 for emergency support.” It is text only, with no calling/messaging handler. Instructor approval is not verified. The UI displays a coursework-prototype notice.

SQLite saves fictional session IDs, skill, UTC start/end/update timestamps, active/paused/stopped/completed status, saved step, optional after-Feel check-in, and separate setup/active/pause/support milliseconds. Sensory selections stay only in tab memory and are never sent or stored. No personal narratives or credentials belong in storage. Stop clears transient sensory choices and saves stopped status; its permitted check-in metadata remains until deletion. Only explicit Finish saves completed status and contributes to recent-skill suggestions. Saved unfinished sessions can be chosen after refresh/restart and always open paused; Resume is explicit. Closed-browser downtime is not added to exercise timing.

Message saving is **opt-in, OFF by default**. The approved retention policy is **until explicitly deleted or cleared**, for both session metadata and opted-in fictional messages. Local history and privacy lets the user review saved metadata/messages, toggle future message saving, Delete a session with its linked conversation/messages, or Clear all. Clear all deletes every session/check-in/duration, conversation/message, and derived recent-skill history, discards this tab's pending writes, and resets message opt-in to OFF. Turning OFF alone keeps existing messages. The empty schema/database and a nonpersonal write-generation counter remain; Clear all is an application-data deletion, not a promise to erase external backups.

Conversation/message tables and an opt-in-protected API are ready for later approved model work. The grounding UI creates no messages and has no chat composer. There are **no model calls or emergency-contact integrations**. The precise model contribution remains unapproved.

The project root is this repository. Do not create another Fifer directory or copy Expedia Lite files. Only architecture and documentation practices are conceptually reused.

## Run locally

Use two PowerShell terminals from the repository root after the setup below:

```powershell
.\backend\.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000
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
| httpx | 0.28.1 | API tests; no runtime model integration |

The project venv's bootstrap pip 25.0.1 advisory gate was resolved by the user's approved upgrade to pip 26.2. The Codex-managed base Python and global packages were not changed. Resolved registry artifacts were inspected before installation: 17 Python wheels and 35 applicable Windows npm packages passed digest checks; Windows native bindings matched the runtime/architecture. Registry advisory queries listed no advisories for the inspected versions at that time. This is a point-in-time check, not a security guarantee.

No applicable dependency install hooks were found. The optional macOS-only `fsevents` hook was inapplicable; publishing-only hooks were distinguished from dependency install hooks. npm installation used `--ignore-scripts`. See [Part 3.2 evidence](docs/part-3-2.md) for the CHECK → TAKE ACTION → VERIFY record and limitations.

`backend/requirements.txt` pins direct dependencies; `backend/requirements.lock.txt` records all 17 installed application packages. `frontend/package-lock.json` records the npm graph, including optional other-platform entries. Local environments, dependencies, caches, and build output are ignored. No new dependency is approved by these instructions alone; follow AGENTS.md before changing versions or adding packages.

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

Latest storage checkpoint: **16 Node tests and 12 API/SQLite tests passed**, and the Vite build passed. Every backend test uses a disposable temporary database and runs application lifespan initialization against that database. Browser checks used a separate ignored `.cache/verification/fifer-storage-browser.sqlite3`, not normal project history: refresh/restart resume, optional check-in and separate clocks, explicit completion, stopped status, opt-in/review, Delete/Clear, unsaved failures, static support, and Retry recovery passed. See [storage verification](docs/part-3-2-storage.md) for commands, screenshots, and limits. Earlier import, `pip check`, and `npm ls` results remain recorded in the [initial UI checkpoint](docs/part-3-2.md). No dependency changed during the storage step.

The design target remains about 60–75 active seconds and under 90; it has not been demonstrated in a timing study. Setup, pauses, and support have separate in-memory counters. There is no forced advance/completion or countdown pressure.

## Project documents and Git

- [AGENTS.md](AGENTS.md): project rules and approval gates.
- [Part 3.1 report](report.md), [research](docs/research.md), [design](docs/design.md), and [flow diagram](docs/mockups/fifer-assignment-3-1-flow.png): preserved design evidence; detailed Figma/Figma Make screens remain pending.
- [Safety](docs/safety.md), [AI use](AI-USE.md), [Part 3.2 evidence](docs/part-3-2.md), and [current handoff](handoffs/current.md).
- [SQLite storage checkpoint](docs/part-3-2-storage.md): approved policy, schema/endpoints, failure behavior, and verification.

Repository: [nikhilrajk21/Fifer](https://github.com/nikhilrajk21/Fifer). Branch: `master`. Part 3.1 submission commit: `615ac73aaa933f8c3ce0004079f0179a133b35b1`; HEAD at this checkpoint: `003245f47958474e300920bb4b0127d275bedff4`. Historical Part 3.1 “uncommitted” or “no application” prose describes that milestone. Current Part 3.2 changes are uncommitted. No commit or push occurred in this implementation turn; proposed scope approval is still required.
