# Fifer — current handoff

Updated: 2026-10-22. This repository is independent of Expedia Lite.

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
