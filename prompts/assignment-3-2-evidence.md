# Assignment 3.2 — selected redacted prompt and decision evidence

Convention follows the existing prompts/assignment-3-1-design.md: selected requests, purpose, boundaries, output used and verified evidence. This is a curated excerpt log, not a full chat export. Credentials, machine/user paths and unrelated/private third-party/course UI content are excluded. Excerpts below came from the owner's actual requests; attribution of instructor feedback/Live substitution is owner-reported, not an independent approval artifact. Codex model/version/effort is not verified. No real model call was made for these tests.

## Sensory feedback → actual picture and optional examples

Selected verbatim request excerpt:

> For See 5, show one locally bundled self-created or properly licensed/attributed classroom, coffee shop, bookstore, or similar scene with useful alt text; ask for five things visible IN that actual image, allowing typed answers and optional examples verified against it.

Related requested revisions: comfortable tactile observations without touching; plausible imagined/present sounds; optional smell/taste text, None/Not sure/Skip; no sensed-surroundings claim or saved sensory narratives. These are summaries of the remaining request, not fabricated instructor quotations.

Output used: [classroom.svg](../frontend/src/assets/classroom.svg), [grounding.js](../frontend/src/grounding.js), [GroundingPrompt.vue](../frontend/src/components/GroundingPrompt.vue). Decision: replace generic choices with five objects visibly present in the bundled original artwork. [Tests](../frontend/src/grounding.test.js) and [acceptance matrix](../docs/verification/part-3-2-acceptance.md) verify correspondence/alt text/optional input and absence of the sensory marker from SQLite.

## Approved bounded text → curated mock, not free-form therapy

Selected verbatim excerpt:

> I choose the **bounded text chatbot/RAG scope**, not completion-only reflection. Put an optional text assistant in the existing Chat screen; do not interrupt or replace the fixed grounding exercise.

Approved follow-up boundaries: gemini-2.5-flash target; fictional non-emergency app-help; reviewed content only; 300 output tokens, 5 attempts/session, 20/anonymous browser/UTC day, 15-second timeout, no retries. Saving opt-in OFF; context sharing OFF separately; retention until Delete/Clear. Anonymous identity is bypassable by browser-data clearing, not verified per-person enforcement or a dollar cap.

Output used: [chat_content.py](../backend/chat_content.py), [ChatPanel.vue](../frontend/src/components/ChatPanel.vue), [text evidence](../docs/text-chat.md). Decision: deterministic paragraph selection plus an HTTPX adapter wired through FastAPI/Chat behind two explicit server-process gates; normal mode remains mock and no real call/activation occurred. Missing-key/provider-error/invalid-output/timeout/late-response/runtime-gate tests pass; actual Gemini contribution remains unverified.

## Approved Live substitution → separate mock audio lifecycle

Selected verbatim excerpt:

> I approve the proposed **mock-only Gemini Live voice increment** using `gemini-3.8-live`, separate from the `gemini-2.5-flash` text chatbot.

The owner approved 300 seconds, five turns, 20-second utterance/15-second output audio limits, timeouts/no retries and two accepted starts/browser/day. Exact WebSocket dependency was approved only after CHECK. No live call was approved. Subsequent requests put voice alongside text in Chat and separated Mute/Unmute from End.

Output used: [FastAPI instructions/mock](../backend/live_voice.py), [relay](../backend/voice.py), [client](../frontend/src/voice.js), [audio adapter](../frontend/src/audio/pcm.js). Decision: one proposed Live model via WebSocket/PCM, no tools/second-model pipeline, credentials/instructions backend-only. Real connector remains fail-closed. Mute sends manual activityEnd without closing playback/session; End clears resources. [Voice evidence](../docs/voice.md) distinguishes synthetic tone/permission injection from real speech and lists approved bounds.

## Evidence-only acceptance → no clinical/live conclusion

Selected verbatim excerpt:

> Run evidence-only acceptance on CURRENT Fifer with fictional scenarios; do not edit.

Output used: [acceptance record](../docs/verification/part-3-2-acceptance.md), existing unchanged mobile screenshot and read-only SQLite observations. Decision: qualified pass for implemented mock scope; no full Live/clinical/a11y claim. Active 31.021 s is one automated run, with setup/pause/support separate; 61 backend and 49 frontend tests passed. Current changes are not represented by a submitted-version commit yet.

## One revised approach and one actual failed command

Revised code approach: provider setup originally awaited acknowledgement before checking local End/disconnect. Inspection identified delayed shutdown risk. The relay now races setup against local receive, cancels setup and closes its acquired wire; tests `test_end_during_provider_setup_cancels_setup_and_closes_wire` and `test_end_cancels_pending_provider_connect_without_late_ready` pass. This was an inspection-led revision; no failed live call or old failing test result is invented.

Actual failed verification approach: a read-only SQLite inspection command embedded in a shell string produced SyntaxError from quoting. Re-running a single-quoted PowerShell here-string through Python stdin succeeded with mode=ro. No database contents were modified by the failed/corrected query. The decision was to keep shell quoting simple and report only observed counts/fields, never credentials or personal data.

Student review, the submitted-version commit, published evidence links and any later live observations must be recorded when they actually exist. This log does not claim this documentation package has already been approved or submitted.

Documentation review outcome: the later full backend rerun produced 60 passes/1 CancelledError at TestClient socket teardown in the setup-disconnect case; one focused rerun passed. In the subsequent authorized implementation task, the test was revised so the abrupt disconnect drives the ASGI endpoint directly and validates cleanup/release, while a fresh TestClient session checks restart. The revised suite passed 62/62 and the focused case passed 25 consecutive reruns. This is a corrected test boundary for mock teardown, not evidence of a live-provider call.
