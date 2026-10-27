# Part 3.2 — verified acceptance evidence

This record transcribes the actual preceding evidence-only acceptance in this conversation. Tests exercised the uncommitted working tree on master with baseline HEAD `a8edc32df96170bed09cd233cc3a5c2248e0adca`, not that clean commit. It is not a live-model evaluation or a claim that every assignment requirement is finished. No source edits/provider calls/commits/pushes occurred in that acceptance turn. The later documentation update preserves these observations rather than inventing a new run.

## Later teardown regression and correction

The documentation-time backend run completed 61 tests with **60 passing and 1 error**: `test_disconnect_during_setup_closes_wire_and_allows_fresh_session` raised `concurrent.futures.CancelledError` at Starlette TestClient's WebSocket context exit. That result prompted a focused revision: the abrupt setup disconnect is now driven directly against the ASGI WebSocket endpoint, where the test verifies upstream close and anonymous-browser reservation release; a separate fresh TestClient session verifies restart. The revised complete suite passed **62/62**, and the focused case passed **25 additional consecutive runs**. This verifies the exercised mock teardown path without claiming real-provider cleanup. The existing Starlette warning about TestClient's deprecated HTTPX integration remains; no unapproved `httpx2` dependency was added.

Focused command, from backend/: `.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_voice.py -k disconnect_during_setup -v`.

## Evidence scope and commands

Backend tests use disposable databases. Browser actions used a new ignored database under `.cache/verification/`, not normal history. Read-only sqlite3 inspection used URI `mode=ro`; the runtime database/logs/cache are excluded from submission. The acceptance browser tab was closed to remove injected test overrides; temporary viewport settings were reset and the normal mock-only backend restored.

From backend/:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

From root:

```powershell
npm --prefix frontend test
npm --prefix frontend run build
.\backend\.venv\Scripts\python.exe -m pip check
npm --prefix frontend ls --depth=0
git diff --check
git status --short
git check-ignore backend/.env backend/data/fifer.sqlite3 frontend/dist/index.html
git ls-files -- backend/.env
```

Observed: **61 backend tests and 49 frontend tests passed**; Vite build, pip check, npm ls and whitespace check passed. No dedicated lint/browser-E2E/accessibility scripts were found by inspecting package.json and `rg --files` for test/config names. Starlette emitted its existing HTTPX deprecation warning; nothing was installed. A read-only SQLite command initially failed from shell quoting; a PowerShell single-quoted here-string piped into the project Python interpreter succeeded. No data was modified by that query.

## Browser, SQLite and automated-mock acceptance matrix

| Action | Expected | Observed | Result / evidence type |
| --- | --- | --- | --- |
| Inspect See image and examples; select a window | Actual image/description matches examples; selection optional | Loaded 800-pixel original SVG with window, clock, blue book, desk, plant; matching examples and alt text; Space toggled aria-pressed | Pass — browser/source/tests |
| Enter fictional sensory marker | Tab-only, excluded from SQLite | Entered marker; read-only dump search before Clear found no marker | Pass — browser/SQLite |
| Feel skip, empty Hear/Taste Continue, Smell None then Skip | No quota/disclosure required; preserve counts/order | Reached each expected category without required selections; optional/comfortable/imagined wording present | Pass — browser/tests |
| After-Feel check-in | Optional, includes A little better | Check-in appeared after Feel; chosen value persisted separately | Pass — browser/SQLite; Skip also unit-tested |
| Reach completion, then press Finish | No completed status until explicit Finish | Final screen still showed Finish; queued recovery persisted completed/complete | Pass — browser/SQLite/tests |
| Pause, Resume, Support return | Keep place and require explicit Resume | Pause dialog shown; Support return opened paused; Resume restored step | Pass — browser/tests |
| Stop from saved paused Feel | Immediate stopped status, never completed | Exited without confirmation; SQL stored stopped/feel; no additional completed suggestion | Pass — browser/SQLite |
| Stop FastAPI; open Support from start, step, paused, unsaved/error and completion | Static route remains usable | All five contexts opened the same static dialog while backend was stopped | Pass — browser; no model was active |
| Check safety copy and notice | Approved copy, no automatic contact | User-approved 911 sentence and coursework/fictional notices visible; no phone link/call/message | Pass for user copy; instructor wording approval Not verified |
| Offline writes then Retry saving | Honest unsaved status, ordered recovery | Unsaved changes displayed; after reconnect, Retry acknowledged the queued completed session | Pass — browser/SQLite |
| Refresh at Feel, choose saved activity | Restore paused with no sensory inputs | Offered unfinished Feel; restored Feel paused with empty sensory input | Pass — browser |
| Recent skill, delete completed session | Completed only; deletion removes recommendation | Completion created optional Use again/Ignore; stopped run did not; deleting completed record removed suggestion | Pass — browser/SQLite |
| Text with saving/sharing OFF | Curated response, no saved messages/context | Both defaults OFF; fictional question returned reviewed skill paragraph; first chat had zero saved messages | Pass — mock browser/SQLite |
| Opt into saving and sharing | Only approved actual context; eligible fictional pair saved | Preview showed 1 completed session, skill and A little better; second chat had 2 saved messages | Pass — mock browser/SQLite |
| Turn saving OFF, review/delete chat | Existing messages remain until deletion | Pair remained reviewable after opt-out; Delete removed selected chat | Pass — browser/SQLite |
| Clear all test history | Delete history/reset OFF, preserve daily counters | Zero sessions/conversations/messages/chat sessions/messages/request IDs; OFF; one daily row per feature remained | Pass — browser/SQLite |
| Mock microphone denial inside Chat | Voice fails without disabling text/Support | Permission-denied message; composer remained enabled; no socket/live provider started | Pass — mocked browser |
| Synthetic Start/Unmute/Mute | Confirm setup; Mute preserves session | Active/muted appeared after mock acknowledgement; synthetic capture toggled active; after Mute returned active/muted at 1/5 | Pass — mocked browser/tests |
| End during capture, then inspect tracks | Stop media/session; text remains available | Both synthetic tracks eventually reported ended; UI closed and composer enabled | Pass — mocked browser/tests; no hardware microphone used |
| Provider interruption, late results, duplicates and failure/timeouts | Clear playback, no stale revival/retry, finite release | Automated voice tests cover interruption, bounded queues, late media/setup/output, duplicate Start/End, cleanup faults and independent maxima | Pass — automated mocks; real provider Not verified |
| Text missing key/provider error/invalid output/timeout/late response | Fixed safe fallback and cancellation, no retries/leaks | Temporary key fixtures/HTTPX mock transports and chat tests passed | Pass — automated mocks; browser provider-failure response not claimed |
| Keyboard/focus | Operable controls, visible focus and dialog containment | Enter/Space worked; See input outline approximately 2.67 CSS px; modal Shift+Tab/Tab wrapped; Escape restored Support button focus | Pass — browser smoke check |
| 390×844 responsive viewport | No horizontal overflow, image/control accessibility | Page/client widths both 375 CSS px (scrollbar excluded); image width about 291 px; Support/control layout reachable | Pass — browser viewport, not physical phone |
| Prototype honesty | No real/clinical/monitoring claim | Coursework/fictional notices and explicit mock labels; voice says it cannot understand speech | Pass — inspected UI |
| Current source/build credential-pattern scan | No recognizable credential/private-key literals | No flags across 56 source/build files; real .env ignored/untracked; no tracked secret/runtime-path flags | Pass within inspected scope, not forensic history audit |
| Prohibited storage fields | No sensory/audio/transcript persistence | No such named schema columns; marker absent before Clear; approved text pair only in content table | Pass for exercised data/write paths, not an audit of all historic normal data |

No application/test failure was observed in this exercised scope. Qualification: actual contextual model contribution remains unfinished and is a Part 3.2 requirement. **Explicitly authorized paid/live observations: none.** Hardware, actual Gemini VAD/speech/latency/account access/billing, abrupt process death, full five-minute browser run, full contrast/screen-reader/cross-browser and clean-checkout verification are Not verified.

## Measured exercise timing

Read-only SQL for the explicitly finished session returned setup_ms=32528, active_ms=31021, paused_ms=5941, support_ms=109. The second, stopped Feel session recorded active_ms=309 and paused_ms=298; it never contributed a completion. The timed completed run included optional See input, skipped categories, the after-Feel check-in, offline app delays and explicit Finish.

The first run therefore measured **31.021 s active**, **32.528 s setup**, **5.941 s paused**, **0.109 s Support**. These are separated, not added together to claim a 90-second skill failure/success. Active was below the assignment's intended-pace ceiling, but automation was fast and did not study student reading/pacing. It does not demonstrate comfort at the proposed 60–75 seconds or guarantee all users finish under 90. No forced completion is implemented; the unit test after 90 seconds preserved user control.

## Screenshot provenance and links

![Actual mobile See acceptance screenshot](part-3-2-acceptance/mobile-see.png)

The PNG above is copied byte-for-byte from the already captured acceptance screenshot; no generation, new screenshot, cropping, replacement or redaction was performed during documentation. It contains the fictional Fifer UI, not personal information. SHA-256: `20422d4b1c15f78af7e45cc299ba6a09c1f588d9580a8b6224e01cd5cad75d7b`. The screenshot demonstrates the actual image and mobile layout; it does not prove live audio or clinical behavior.

Related source/checks: [grounding](../../frontend/src/grounding.js), [grounding tests](../../frontend/src/grounding.test.js), [storage](../../backend/storage.py), [API tests](../../backend/tests/test_api.py), [text tests](../../backend/tests/test_chat.py), [offline adapter tests](../../backend/tests/test_gemini_text.py), [voice tests](../../backend/tests/test_voice.py), [frontend voice tests](../../frontend/src/voice.test.js).

Links to new files are working-tree review links until an approved commit/push publishes them. Do not label the baseline HEAD as the tested submitted version. No runtime database, logs, audio, cache, node_modules, venv, .env or build output belongs in the submitted package.
