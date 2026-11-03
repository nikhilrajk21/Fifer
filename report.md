# Fifer — Assignment 3.3

## Repository and version

Repository: [nikhilrajk21/Fifer](https://github.com/nikhilrajk21/Fifer), branch master. The previous commit `07c711dff8839a41595fefc05c7797ef5dadd164` is the Part 3.2 baseline. The exact Assignment 3.3 commit ID is not embedded in this report; it will be available in Git history after the reviewed package is committed. The former root report is preserved as [report-3-2.md](report-3-2.md), and [report-3-1.md](report-3-1.md) remains the Part 3.1 record. No Canvas submission is claimed.

The current app remains a local Vue → FastAPI → SQLite coursework prototype, independent of Expedia Lite. It is not therapy or a diagnostic tool. No clinical effectiveness or human monitoring is claimed.

## Application and generated code

The app-owned sequence remains Start choice → See 5 → Feel 4 → optional check-in → Hear 3 → Smell 2 → Taste 1 → explicit Finish. Each step is separate; sensory answers are optional/skippable and unscored. The bundled classroom image and See examples name the same five visible objects; the app does not sense the user's surroundings. Feel asks only for comfortable observations without requiring touch. Hear offers plausible sounds. Smell and Taste allow none/not sure/skip without requiring smelling, eating, drinking, or disclosure. Pause/Resume, immediate Stop/Leave, and static Emergency Support remain outside model control.

Instructor sensory feedback, as relayed by the project owner, led to the concrete scene, matched See examples and alt text, more plausible Hear examples, and lower-demand tactile/smell/taste wording. This is a report of the owner's direction, not an independently verified instructor evaluation.
The later checks did not change the 3.1 sequence; they made its implementation criteria more concrete: See examples must match the bundled scene, sounds must be plausible, answers must remain optional, and Finish/Stop/Support behavior must remain explicit and application-controlled. A mocked but structurally valid unsupported paraphrase with the correct source ID also changed the evidence decision: citations are reported as structural checks only, and semantic grounding remains unverified. No participant or usability results were supplied, so no preference-based redesign is claimed.

Codex-assisted code uses a curated single-source retrieval path for the optional text assistant. The approved Gemini adapter can return a short plain-language paraphrase attributed to the one retrieved Fifer source. Only if context sharing is explicitly enabled may it receive the completed-session count, most recent completed skill, and optional check-in already supplied by the app. No profile is inferred. Sensory narratives, audio, transcripts, arbitrary files, web results, and private records are excluded. Mock tests exercise this contract; a structurally valid answer and matching source ID do not prove semantic grounding.

## Evaluation: fictional scenarios

The full [Assignment 3.3 evaluation plan](docs/assignment-3-3-evaluation-plan.md) records expectations, outcomes, evidence, four cross-case checks, and the gated live-test card. Automated mock/local results are distinguished from live-model and owner-supplied manual observations below.

| ID | Fictional scenario | Expected | Observed result and evidence type |
| --- | --- | --- | --- |
| M01 | Ask how to pause in default mode | Label mock; cite curated controls content; no provider request | Pass — backend/UI mock tests; not browser or live evidence |
| M02 | Ask which grounding skill is available | Cite skill content; app sequence remains fixed | Pass — retrieval and frontend order/count tests |
| M03 | Ask unrelated trivia | Fixed out-of-scope response; no provider call or saved message | Pass — mocked/API test |
| M04 | Ask Chat to skip/reorder a running step | Chat cannot change app-owned flow | Pass — browser/mock-only flow exposed Skip, Continue, Pause, Stop/Leave and Support, with no Chat entry point during the exercise; See → Feel advanced by Skip. Later backend-off exercise reached explicit Finish. No provider call occurred. |
| M05 | Open Chat without enabling context sharing | Context OFF; send no summary fields | Pass — API and mocked request-payload tests |
| M06 | Explicitly share a completed-session summary | Share only approved supplied fields | Pass — HTTPX mock and temporary-session tests |
| M07 | Turn sharing OFF after enabling it | Next request omits summary; saving consent stays separate | Pass — OFF/ON/OFF mock/API tests |
| M08 | Send with message saving OFF | Do not persist question/answer | Pass — mocked provider and temporary database tests |
| M09 | Opt in, review, opt out, then delete | Save only with opt-in; deletion removes selected messages | Pass — temporary database API test |
| M10 | Finish one session and stop another | Only explicitly finished skill becomes recent suggestion | Pass — API/state tests; no forced recommendation |
| M11 | Stop while mock reply is pending | Ignore late result; no save; keep flow/Support usable | Pass — backend and frontend cancellation tests |
| M12 | Open Support while a request is pending/backend unavailable | Static Support opens independently | Pass — static Support opened during a delayed mock response, stayed open after the response window, and showed no late Chat result; backend-off paths were separately observed. |
| M13 | Mock upstream 404 with private body marker | Safe fallback and generic not-found category; hide body | Pass — HTTPX mock and log-sanitization tests |
| M14 | Mock auth, permission, quota, request, server, and other HTTP statuses | Fixed allowlisted classification; no retry/body leak | Pass — HTTPX mock status-category tests |
| M15 | Mock connection error and timeout | Fixed safe reason; no retry or exception text | Pass — HTTPX mock tests |
| M16 | Mock malformed, mismatched-source, extra, oversized, or incomplete output | Reject and fall back safely | Pass for structural validation — tests reject these forms; semantic entailment remains unproven |
| M17 | Stop/Leave before Finish | Persist stopped, not completed; do not update recent skill | Pass — API/state and frontend tests |
| M18 | Open Support from start, step, paused, error, completion with backend down | Static panel available in every state | Pass — browser inspection with FastAPI stopped opened static Support from Start, active See with connection/unsaved warning, Pause, Chat setup error and completion; same copy appeared without a backend response. |
| M19 | Use Chat and controls with keyboard only | Operable controls and visible focus; mode label clear | Pass — browser keyboard-only path used Tab/Shift+Tab, Space and Enter through Chat, fictional question, Stop, Support/Return, Skip and Stop/Leave; visible focus appeared and Stop was immediate. |
| M20 | Reach text-chat quotas through failures, new chats, and reloads | 5/session and 20/browser/UTC-day; no auto retry | Pass — API/temp DB quota and no-retry tests |

## Cross-case checks

| Check | Expected across cases | Observed |
| --- | --- | --- |
| I1 — App-owned skill | Chat replies, errors, and late replies never alter the fixed grounding flow | Pass in automated seams; no integrated live-model/browser run |
| I2 — User control and independent Support | Stop stays immediate; Support stays static and available through backend/provider failure | Pass for the exercised browser/mock states — delayed mock output was ignored after Stop; keyboard Stop/Leave was immediate; static Support worked while a mock was pending and with FastAPI stopped in the observed states. This is not live-provider evidence. |
| I3 — Consent and data minimization | Context share and message saving remain separate; only allowlisted summary fields shared; sensory/audio/transcript data excluded | Pass in automated payload, temporary DB, consent, and deletion checks |
| I4 — Completion-derived suggestion | Only completed sessions affect recent-skill suggestion | Pass in automated API/frontend checks; stopped session excluded |

Owner-reported manual retests (2026-11-02; not independently reproduced in this turn): S03 context sharing OFF — Pass; S04 context sharing ON — Pass; S11 same-tab Pause/Resume — intermittent, **Partial** pending post-fix manual retest; S11 recovery after refresh — Pass; S13 completed-session review — Pass. The S11 code now snapshots and restores the paused screen and tab-only selections/responses/check-in; sensory inputs remain excluded from persistence. The 20 scenario rows and four cross-case checks below are supported by the automated/mock and browser evidence recorded in the [evaluation plan](docs/assignment-3-3-evaluation-plan.md). Earlier Part 3.2 browser acceptance is retained in [the acceptance record](docs/verification/part-3-2-acceptance.md), as historical evidence.

## Design, data, and safety

The dusty blue/lavender design retains the calm low-stimulus direction. The revised sensory content lowers performance pressure but does not remove user effort. The new scene makes See examples concrete; a user can still skip. A lightweight check-in and optional recent-skill suggestion remain user-controlled. Stop does not count as completion.

SQLite retains fictional session metadata, completion/stopped status, step/check-in and separate durations under the existing approved policy. Recent-skill suggestions use explicitly completed sessions only. Message saving is opt-in and OFF by default; context sharing is a separate control and also defaults OFF. Saved messages/session records remain until user deletion; per-session Delete removes its messages, and Clear removes sessions/messages/check-ins/durations/recent history and resets save opt-in OFF. The anonymous browser quota counter is the disclosed operational exception and is not a verified per-person or dollar limit. No sensory narratives, audio, transcripts, credentials, or inferred profile are stored/shared.

Emergency Support is static frontend content, visible independently of FastAPI and any model. It opens without a provider request. The text currently approved by the user is “Please contact 911 for emergency support.” There is no automatic call/message integration. Instructor approval of that wording has not been verified. Fifer is a coursework prototype only; use fictional scenarios.

## Model behavior and live evidence

The Part 3.2 checkpoint recorded Gemini `gemini-2.5-flash`; after that checkpoint the owner approved updating the current text target to `gemini-3.5-flash-lite`. Limits remain 300 output tokens, 5 requests per chat session, 20 per anonymous browser per UTC day, 15-second timeout, no automatic retries. Normal mode is the labelled mock; live selection requires the two backend process gates. The model cannot change grounding order, diagnose, assess safety, invent therapeutic advice, or control Stop/Support. Gemini Live voice is separate and remains mock-only; no voice or audio is part of this text evaluation.

At the Assignment 3.2 evidence cutoff, the revised paraphrase-contract live sample was **Not run**. In later follow-up (2026-11-02, outside that checkpoint), one separately authorized fictional request (“How do I pause Fifer?”) first reached Gemini with HTTP 200 but was rejected as `invalid_output`; Chat showed the safe fallback and no source. After the narrow `thoughtSignature` parser fix, the owner reports that exactly one later request produced a generated Gemini text answer. This is owner-reported live evidence, not reproduced in this turn. The generated answer and displayed source title were not retained in the repository, so their contents and semantic relationship cannot now be independently reviewed. No retry or additional request was made here. Historical context: an earlier request returned `upstream_model_unavailable` (an upstream 404 was one condition collapsed into that reason); a metadata-only request returned no HTTP status. Those observations do not diagnose the later failure. One successful generated response establishes only that a response was observed once; matching source ID/shape does not prove semantic grounding, and mocks do not establish general live behavior, account-wide access, latency, or billing. Gemini Live voice remains mock-only.

## Verification and evidence

Checks for this revision used the existing project-local environment, fictional fixtures, mock transports and temporary test databases. No real provider request or `.env` read occurred.

- Full backend command from `backend/`: `$env:FIFER_TEXT_PROVIDER='mock'; $env:FIFER_TEXT_LIVE_AUTHORIZED='false'; .\.venv\Scripts\python.exe -B -m unittest discover -s tests -q` exceeded the 30-second bound and was interrupted without a test summary. It emitted a Starlette/httpx deprecation warning; this run did not identify the last test/setup location. An earlier Windows Proactor `_fallback_socketpair()` stall is a possible environment issue, not a confirmed explanation for this run.
- Focused synchronous backend command from `backend/tests/`: `$env:FIFER_TEXT_PROVIDER='mock'; $env:FIFER_TEXT_LIVE_AUTHORIZED='false'; $env:PYTHONPATH=(Resolve-Path ..).Path; ..\.venv\Scripts\python.exe -B -m unittest test_gemini_text.GeminiDiagnosticTests test_gemini_text.GeminiResponseContractTests -v` — **12 passed**.
- Frontend `npm --prefix frontend test` — **58 passed, 0 failed**.
- Production build `npm --prefix frontend run build` — **passed**, 28 modules transformed.
- Python syntax check from `backend/`, `.\.venv\Scripts\python.exe -B -m py_compile main.py chat.py gemini_text.py tests/test_api.py tests/test_chat.py tests/test_gemini_text.py` — **passed**.
- `git diff --check` — passed. Markdown structure check found exactly one level-1 heading; all checked local report/evidence links exist. Final staged secret/exclusion review follows.

The S11 reducer now captures and restores the exact same-tab screen, selected examples, typed optional answers and check-in across Pause/Resume. Focused tests cover all sequence positions, 50 repeat cycles, a stale-state simulation, Support return and Stop/privacy behavior. The saved snapshot is transient and excluded from session persistence; Stop clears it. These tests pass within the frontend suite. Manual post-fix browser retest is pending, so S11 remains Partial. Refresh recovery remains the owner-reported pass, and by design it does not restore sensory inputs.

Earlier Part 3.2 automated timing recorded 31.021 seconds active, 32.528 seconds setup, 5.941 seconds paused and 0.109 seconds in Support. These are application/test timings, not a human usability measurement. Setup is separate; pauses and Support are outside the active target. The target remains approximately 60–75 seconds and under 90 where feasible, without forced completion.

Surprising finding: structurally valid mock output with the expected source ID can still contain unsupported meaning and pass validation. Shape/source-ID checks do not establish semantic grounding. Untested limitations include semantic review of the one owner-reported live answer (answer and source title are not retained), repeatability beyond that one response, post-fix manual S11 behavior, and Gemini Live voice, which remains mock-only.
## AI disclosure and evidence links

Codex assisted with code, tests, documentation, and organizing this evidence. Exact Codex model/effort is not available and is not asserted. The changed response behavior is limited to a concise paraphrase from one retrieved curated Fifer source, with only explicitly shared supplied session-summary fields permitted. Test fixtures use fictional data and mocked transports. GPT image generation was used earlier for the proposed flow diagram; the student reviewed/adapted it. Figma/Figma Make remains planned for detailed screens. No provider call occurred during this documentation update. The [curated redacted evidence log](prompts/assignment-3-3-evidence.md) records the revised approach and test findings without private chat exports.

Evidence links: [Part 3.1 flow](docs/mockups/fifer-assignment-3-1-flow.png), [Part 3.2 screenshot](docs/verification/part-3-2-acceptance/mobile-see.png), [design](docs/design.md), [safety](docs/safety.md), [text adapter notes](docs/text-chat.md), [voice mock evidence](docs/voice.md), [course requirements summary](docs/assignment-3-submission-requirements.md), and [evaluation plan](docs/assignment-3-3-evaluation-plan.md). These are repository-relative links and resolve within the pushed repository, subject to repository access.

## Remaining 

- Investigate and retest the intermittent S11 Pause/Resume behavior.
- Complete the remaining unverified browser checks: M04, M12, M18, I2, and keyboard-only use.
- Verify that another person can run a clean checkout by following the README.
- Confirm the recording covers the finished-app demonstration, a failure, the evidence used to understand it, the resulting decision, and an explanation of relevant generated code.
- Finish the detailed Figma screens and verify the instructor’s support wording, if those are required.
- Review the final changes, then commit and push the Assignment 3.3 work.

## Video Link 
https://drive.google.com/file/d/13GzWGbF9SLct7EiMdANLJjf4vgvi6QB-/view?usp=sharing 
