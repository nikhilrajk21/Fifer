# Fifer — Part 3.2 SQLite checkpoint

Date: 2026-10-22. Fictional coursework prototype only. This follows the [first UI checkpoint](part-3-2.md); it does not claim clinical effectiveness or a completed Part 3.3 evaluation.

## Authorization and policy

The Step 1 audit verified the application-owned sequence, optional input, Pause/Resume, immediate Stop, static support with FastAPI stopped, and coursework notices. The user then approved these previously unresolved choices:

- “Opt-in, OFF by default” for fictional message saving.
- “Until the user explicitly deletes or clears it” for saved sessions and opted-in messages.
- Clear all removes “All sessions, check-ins, durations, messages and recent-skill history; reset message opt-in to OFF.”

The implementation request authorizes fictional session IDs, skill, start/end, status including stopped versus completed, resume step, optional after-Feel check-in, and separate setup/active/pause/support durations. It forbids sensory selections, personal narratives, credentials, model calls, new unapproved dependencies, commits, and pushes. These boundaries were preserved. No dependency manifest/lockfile was changed in this step; sqlite3 is part of the existing Python runtime.

Existing static safety text remains “Please contact 911 for emergency support.” It follows the user's supplied direction, not a pasted exact instructor-approved script. No instructor approval is claimed. The old Part 3.1 placeholder is not rendered. There is no calling/messaging handler or dependency on SQLite/model/classifier for opening support.

## What is stored and where

Normal database: `backend/data/fifer.sqlite3`. It is resolved from the backend source directory, not the caller's working directory. The file and runtime sidecars are ignored by Git. `FIFER_DB_PATH` supports an explicit isolated test path. No normal database existed before this step; startup created the schema without resetting data.

| Table | Stored data |
| --- | --- |
| sessions | Random fictional UUID, fixed skill, UTC started/ended/updated timestamps, active/paused/stopped/completed status, current sensory/check-in/completion step, nullable allowed check-in label, setup_ms/active_ms/paused_ms/support_ms, revision |
| conversations | Random ID, linked session ID, created timestamp; one conversation per session, created only when saving its first eligible message |
| messages | Random message ID, conversation ID, user/assistant role, opted-in fictional content up to 1,000 characters, server UTC timestamp |
| settings | Singleton message opt-in (initially OFF) and nonpersonal history generation used to reject stale writes |
| schema_versions | Additive schema version marker (version 1) |

No account/profile, diagnostic/risk field, sensory choices, personal narrative, or credential is part of session storage. Message requests require opt-in and an explicit fictional-only flag; no distress detector or automated content/safety inference was added. The current grounding UI does not create messages and has no chat composer. Message storage is ready for the later separately approved contribution; it is not a model integration.

Sessions and opted-in messages have no automatic expiry. They remain until explicit Delete/Clear. The preference is local to this database, persists across restart, and defaults OFF on a new database and after Clear. Turning OFF prevents new message saves while retaining existing messages. Recent skill is derived only from saved sessions with `status = completed`, never from stopped/unfinished sessions.

Per-session Delete removes that session/check-in/durations and cascades its conversation/messages. It updates the derived recent suggestion, including falling back to an older remaining completed record. It does not turn off message saving. Clear all deletes every session and linked conversation/message, removes derived recent/resume history, discards this tab's pending snapshots, and resets message saving OFF. The empty tables/database, schema marker, and nonpersonal generation counter remain. SQL deletion is not a promise to erase external filesystem backups or snapshots.

## API and storage behavior

| Method / route | Purpose |
| --- | --- |
| GET /api/health | Configured persistence/model flags; model remains disabled |
| GET /api/history | Settings, saved metadata, and most recent explicitly completed session |
| PUT /api/sessions/{UUID} | Idempotent begin/update snapshots with allowlisted fields, revision, event, and expected history generation |
| GET /api/sessions/{UUID} | Review one session and its opted-in fictional conversation/messages |
| PATCH /api/settings | Explicitly change future message saving |
| POST /api/sessions/{UUID}/messages | Save an explicitly fictional message only when opt-in is ON; no model call |
| DELETE /api/sessions/{UUID} | Delete one session with cascading linked history |
| DELETE /api/history | Clear all history and reset opt-in OFF |

All SQL values use parameters. Foreign keys and transactions enforce cascades and atomic changes. Initialization uses repeatable `CREATE TABLE/INDEX IF NOT EXISTS` and insert-if-absent defaults; it never drops/reset tables or replaces the opt-in preference on restart. Tests create separate application instances whose lifespan uses temporary database paths. Importing the application does not initialize the normal database.

Input rejects unsupported fields and check-in labels, negative/decreasing counters, missing timestamp timezones, sequence jumps, premature completion, and changes to terminal sessions. A session must begin at See. Only an explicit Finish event at the final screen can mark completed. Repeating an identical acknowledged revision is safe; conflicting/stale revisions fail rather than silently replacing data. Clear/Delete advance a history-generation counter; requests already tagged with an old generation fail rather than recreating cleared records. This is not a claim of multi-user conflict resolution.

## Browser behavior and failure semantics

The fixed flow remains start → See 5 → Feel 4 → optional check-in → Hear 3 → Smell 2 → Taste 1 → explicit Finish. No selection quota/scoring, required touching, scent-finding, consumption, or disclosure. Storage never gates navigation or Stop. A saved unfinished session is optional to resume, opens paused with empty sensory selections, and requires explicit Resume. The application does not count closed-browser downtime.

Timing accumulates from monotonic browser time, separate from UTC timestamps. Setup excludes pre-exercise support; active timing excludes pause/support. Active/paused sessions checkpoint on relevant actions and approximately every five seconds while the browser runs and no earlier save is pending. Support opens from static frontend content without a storage request; elapsed support time is captured on Return/Stop. Time since the last acknowledged checkpoint can be lost on abrupt closure or browser timer throttling. The 60–75-second design target remains unmeasured; there is no forced completion after 90 seconds.

Snapshots are queued in order in tab memory and acknowledged only after a matching persisted response. Failures show a persistent Unsaved changes notice, Retry saving, and Discard unsaved changes. A failed write is never represented as saved. Retry recovers pending snapshots in order, including an offline Stop. Discard removes only pending tab snapshots; it does not delete already saved data. Reload/close can lose unsaved Stop/Finish/timing changes, while the last acknowledged record remains. Recent suggestions appear only after explicit completion is saved. Non-JSON proxy errors are reported as unconfirmed local-storage requests, not raw parse errors. Delete/Clear failures do not announce success or reset local history.

The activity and static Emergency Support remain usable with FastAPI stopped. A fresh page load still requires the frontend server. This is not an offline/service-worker deployment. The Finish button now moves focus to the heading after it disappears.

## Actual verification

Final checks passed:

- **16 frontend tests**, 0 failures: original flow invariants plus persistence allowlist, stopped snapshots, separate setup/support timing, paused restore excluding downtime, ordered failure/retry, stale acknowledgement discard, and network/non-JSON failure handling.
- **12 API/SQLite tests**, 0 failures: health/model boundaries; fixed progression/explicit completion; pause/resume and stopped status; repeatable schema/new-app restart; opt-in OFF/ON/OFF; message retention/review; per-session cascade; Clear/reset and stale write fencing; identical retry/conflict; invalid/private fields; SQL injection treated as literal fictional text; unavailable database writes/Clear returning 503 while saved data remains intact.
- Vite 8.3.4 build passed, 17 modules, final build 112 ms. No new package installed.

Commands from repository root:

```powershell
npm --prefix frontend test
npm --prefix frontend run build
git diff --check
git status --short --untracked-files=all
```

Backend test command, from `backend/`:

```powershell
.\.venv\Scripts\python.exe -B -c 'import faulthandler,unittest; faulthandler.dump_traceback_later(25,exit=True); suite=unittest.defaultTestLoader.discover("tests"); result=unittest.TextTestRunner(verbosity=1).run(suite); raise SystemExit(not result.wasSuccessful())'
```

Windows sandbox async/thread restrictions required the approved test execution outside the sandbox. Every backend test used TemporaryDirectory, not normal local history. The final run completed all 12 tests in 0.965 seconds. This is test execution time, not exercise duration.

Browser checks used the isolated ignored `.cache/verification/fifer-storage-browser.sqlite3`:

1. Empty history showed message opt-in OFF. Selected one optional See example, advanced to Feel, and paused; the stored schema/payload contains no sensory choices.
2. Refreshed and chose the saved Feel checkpoint. It opened paused and required Resume.
3. Opened static support, returned through Pause/Resume, selected “A little better,” reached completion, and explicitly finished. History showed completed status, check-in, timestamps, and all four clocks. The observed demonstration values were setup 24.2 s, active 20.4 s, pause 6.5 s, support 1.0 s. These are a fictional walkthrough, not usability/timing-study results.
4. Enabled message saving and inserted one labelled fictional fixture via the local API into this test database only. It was not model-generated. Review showed it; turning OFF retained it.
5. Created stopped sessions through immediate Stop/Leave; they did not replace the completed-session suggestion. A real FastAPI process restart against the same test database preserved the saved Feel resume offer and completed history.
6. Stopped FastAPI. Navigation remained usable and writes showed Unsaved changes. Static support opened by keyboard. After server restart, Retry saved the queued activity as stopped without duplication/completion.
7. Deleted the completed fixture session through the browser. Read-only SQLite inspection confirmed 3 remaining stopped sessions, 0 completed sessions, 0 conversations, and 0 messages.
8. Enabled opt-in again and selected Clear all in this disposable test database. Browser showed cleared history/OFF; refresh had no recent/resume suggestion. Read-only SQLite inspection confirmed 0 sessions/conversations/messages, opt-in 0, generation 2.

The normal project database was then started with `FIFER_DB_PATH` unset. No existing normal data was reset or deleted. The initial normal database contains no test sessions/messages; opt-in is OFF. Screenshots below are captures from the isolated browser checks, not generated mockups or Figma exports.

| Evidence | File |
| --- | --- |
| Initial empty history / OFF | [01-history-default-off.jpg](verification/part-3-2-storage/01-history-default-off.jpg) |
| Paused Feel after refresh | [02-resume-after-refresh.jpg](verification/part-3-2-storage/02-resume-after-refresh.jpg) |
| Completed session review | [03-completed-session-details.jpg](verification/part-3-2-storage/03-completed-session-details.jpg) |
| Metadata, separate clocks, fictional message | [04-opted-in-message-review.jpg](verification/part-3-2-storage/04-opted-in-message-review.jpg) |
| Saved resume offer after FastAPI restart | [05-resume-after-backend-restart.jpg](verification/part-3-2-storage/05-resume-after-backend-restart.jpg) |
| Unsaved notice during outage | [06-unsaved-backend-offline.jpg](verification/part-3-2-storage/06-unsaved-backend-offline.jpg) |
| Static support during outage | [07-static-support-with-unsaved-session.jpg](verification/part-3-2-storage/07-static-support-with-unsaved-session.jpg) |
| Stopped versus explicitly completed | [08-stopped-versus-completed.jpg](verification/part-3-2-storage/08-stopped-versus-completed.jpg) |
| Clear confirmation / opt-in OFF | [09-cleared-history-optin-off.jpg](verification/part-3-2-storage/09-cleared-history-optin-off.jpg) |

## Changes and remaining work

New source: `backend/storage.py`, `frontend/src/persistence.js`, `frontend/src/components/HistoryPanel.vue`.

Updated source/tests: `backend/main.py`, `backend/tests/test_api.py`, `frontend/src/App.vue`, `frontend/src/api.js`, `frontend/src/grounding.js`, `frontend/src/grounding.test.js`, `frontend/src/style.css`.

Updated documentation: `AGENTS.md`, `README.md`, `AI-USE.md`, `docs/safety.md`, `docs/part-3-2.md`, `handoffs/current.md`. New documentation: this report and the nine JPGs above. Dependency manifests/locks and Part 3.1 report/research/design/mockup artifacts were not changed in this storage step. Runtime databases, environments, caches, and build output remain ignored.

Unresolved: the precise future model contribution/provider/fallback; instructor crisis wording/jurisdiction confirmation; detailed Figma/Figma Make screens; timed usability; complete accessibility/screen-reader and cross-browser/device coverage. Multi-tab concurrent conflict recovery is not comprehensively browser-tested; stale revisions/generations are covered by API tests and produce an honest error. No clinical result, model interaction, or fresh-machine reproduction is claimed.

Repository remains on master at `003245f47958474e300920bb4b0127d275bedff4`; Part 3.1 submission remains `615ac73aaa933f8c3ce0004079f0179a133b35b1`. Nothing is staged/committed/pushed. Commit scope approval is still required.
