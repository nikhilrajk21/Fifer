# Fifer — AI use and evidence record

## Assignment 3.3 evidence update — 2026-11-02

Codex assisted with the approved concise-paraphrase response contract, bounded diagnostic categories/logging, mock tests, the Pause/Resume state snapshot, history review UI, and evaluation/report curation. Exact Codex model identifier and effort are not available and are not asserted. The owner supplied AI Studio quota screenshots for project “fifer” and confirmed the configured key is local; this update did not inspect `.env` or the key. The default application mode remains Mock. A pre-fix authorized fictional request returned HTTP 200 but failed output validation (`invalid_output`), so Chat showed the fixed fallback. After the parser fix, the owner reports exactly one later generated Gemini text answer. The answer and visible source title are not retained, so semantic grounding cannot be independently reviewed. No retry or new provider call was made for this update.

Current checks for this revision: frontend 58/58 tests passed; production build passed with 28 modules; Python syntax compilation and `git diff --check` passed; local report links resolve; 12 synchronous Gemini diagnostic/response-contract tests passed. The full backend unittest suite was stopped at the 30-second bound with no test results; Windows async setup remains unverified. Mock transports and temporary databases are not live-provider evidence. Historical live events include the earlier `upstream_model_unavailable` fallback, a no-HTTP-status metadata check, the pre-fix `invalid_output` response, and the later owner-reported single generated response after the parser fix. These are distinct observations and do not establish semantic grounding. No provider call or package install occurred in this update. See [text-chat evidence](docs/text-chat.md), [the 3.3 evaluation record](docs/assignment-3-3-evaluation-plan.md) and [curated redacted evidence log](prompts/assignment-3-3-evidence.md).

The evaluation exposed an important boundary: schema, size, and matching-source-ID checks reject malformed output but cannot prove the paraphrase is semantically supported by the cited source. A structurally valid unsupported mock output passes. No keyword filter is described as comprehensive validation. Owner-reported S03/S04, S11 refresh, and S13 results are recorded in the evaluation plan; S11 same-tab Pause/Resume remains Partial pending post-fix manual retest. The owner says a video was recorded, but its link is unavailable and its coverage of both required sections cannot be verified. `**Video link:**` remains blank for the owner to fill.

## Historical Part 3.2 submission disclosure (recorded at that milestone)

The later implementation pass corrected the intermittent setup-disconnect test boundary. Current results are 62/62 backend tests plus 25 consecutive focused passes, 49/49 frontend tests, and a successful production build. The earlier 60-pass/1-error result is retained as the failed approach that prompted the direct-ASGI teardown test; no live model call was involved.

Codex acted as coding/documentation and verification assistant: revised sensory prompts/original classroom SVG, app-owned flow, SQLite/history/consent/deletion, bounded curated mock text/offline HTTPX adapter, mock voice/WebSocket lifecycle, tests, browser/SQLite inspection and this report. Exact Codex model identifier/effort is Not verified; it is not inferred from available-model lists. The original 3.1 disclosure remains below and the previous report is preserved in report-3-1.md.

| Tool/model | Actual role and evidence boundary |
| --- | --- |
| Codex | Code/docs/test assistance; no independent clinical study or efficacy evidence |
| gemini-3.5-flash-lite | Current approved text target; adapter is wired to FastAPI/Chat behind two server-only gates; the single authorized request returned HTTP 200 but output validation failed, producing the fixed fallback |
| gemini-3.8-live | Approved separate Live target/instructor substitution relayed by owner; mock setup/events/synthetic tone only; real connector disabled/unimplemented |
| Browser/Web Audio and Python SQLite/unittest, Node tests/Vite | Fictional acceptance and deterministic checks; not AI models or live provider evidence |
| GPT image generation | Earlier 3.1 proposed flow image; no new image generation here; exact image model/version unknown |
| Figma/Figma Make | Planned detailed screens; no actual artifact claimed |

Verified acceptance: 61 backend and 49 frontend tests, build/pip/npm/whitespace checks; browser/SQLite main/alternate paths; mobile/keyboard smoke; separated timing 31.021 s active, 32.528 s setup, 5.941 s pause, 0.109 s Support. No paid/live observation, actual speech or hardware capture result exists. Voice browser tests used injected permission denial or synthetic oscillator media, not room audio. Only the previously captured fictional mobile screenshot was copied unchanged into submission evidence.

Actual course submission/overview requirements were read from Canvas, summarized in [requirements](docs/assignment-3-submission-requirements.md), not exported wholesale. [Selected redacted prompts and revised/failed approach](prompts/assignment-3-2-evidence.md) connect requests → changes → tests → decisions. Setup/End cancellation was an inspection-led revision; the SQLite shell-quoting SyntaxError was an actual failed command corrected via stdin. Neither is represented as a failed live call. No keys, real distress disclosures, recordings or private third-party content are included.

Current package is for student review, not approved/committed/submitted. The model-contribution requirement and publication/commit evidence remain unfinished. [Acceptance evidence](docs/verification/part-3-2-acceptance.md) distinguishes current observations from the historical checkpoint counts below; old no-database/unapproved-scope/uncommitted-milestone statements describe their earlier dates.

## Offline Gemini adapter follow-up — 2026-10-26

Codex inspected the approved text scope and implemented its HTTPX Gemini REST adapter, retaining the strict curated-output contract and existing FastAPI quota/consent/retention boundary. It later wired that adapter to normal application construction and mode-aware Chat labels through two explicit server-process gates. Official Google REST/key/access documentation was reviewed; no inference endpoint was called. Temporary-database tests use HTTPX MockTransport with fictional key fixtures only, covering missing key, success, invalid output, provider error, timeout, late reply, consent, runtime gating and safe refusal before live authorization. Current totals are 62 backend tests, 49 frontend tests and a successful build. Normal runtime remains the local mock. No real key was read or changed, dependency installed, provider call made, or commit/push performed. The provider model's account eligibility and real behavior remain unverified; see [adapter evidence and sources](docs/text-chat.md).

## Mock text assistant checkpoint — 2026-10-26

The user approved a bounded fictional app-help/skill chatbot, separate from Gemini Live voice, and an anonymous browser quota identity. Codex implemented local curated retrieval and a deterministic mock provider, backend quota reservations, optional context preview/sharing, cancellation, consent-aware saving, and history/Delete/Clear integration using existing dependencies. No Gemini/provider call, SDK installation, key read, credential change, or live-call switch was used. `gemini-2.5-flash` and 300 output tokens are the approved future request target/allowance, not evidence of a running model. Exact Codex model/effort is not independently asserted.

The original classroom SVG and optional sensory text fields were created in the preceding grounding increment. Those fields stay out of storage and Chat context. Mock answers are reviewed app-content fixtures, not AI-generated runtime responses or clinical evidence. Final checks passed: 26 frontend tests, 28 temporary-database backend tests, Vite build, browser quota/reload/context/saving/review/Delete/Clear and backend-off Support checks. Normal history counts and existing opt-in were preserved. Live provider availability, generated output safety, token usage, costs, voice, full accessibility and cross-browser behavior remain unverified. See [text-chat evidence](docs/text-chat.md) for actual checks, revised approaches and limitations. Existing uncommitted grounding changes were preserved; no commit/push occurred.

Part 3.1 record: 2026-10-15. Part 3.2 checkpoint: 2026-10-22.

## Part 3.2 implementation disclosure

Subsequent SQLite checkpoint: the user explicitly chose “Opt-in, OFF by default,” “Until the user explicitly deletes or clears it,” and Clear all removing sessions/check-ins/durations/messages/recent history and resetting opt-in OFF. Codex implemented those policies using Python's existing sqlite3, parameterized SQL, repeatable additive schema initialization, an ordered metadata save queue, and local review/Delete/Clear controls. No dependencies were added/changed and no model was called. A single clearly labelled fictional message fixture was inserted through the API only in the isolated browser-test database, to verify history rendering; it was not model-generated.

Latest results: 16 Node tests, 12 API/SQLite tests using temporary databases, production build, browser refresh and process-restart persistence, stopped-versus-completed history, opt-in review/opt-out, Delete/Clear, and offline save/support/retry checks passed. See [storage evidence](docs/part-3-2-storage.md). Initial inspection caught a notice that could scroll out of view; the unsaved notice was made sticky. Non-JSON proxy failures were normalized into honest failure messages. Finish now moves focus to the activity heading. No clinical/timed-user-study or complete accessibility result is claimed. Existing safety wording is unchanged and is not claimed as instructor-approved. No commit/push occurred.

The remaining paragraphs in this section describe the earlier first UI checkpoint; its no-database and pending-retention statements are historical.

Codex implemented the bounded Vue + FastAPI slice, dependency inspection/setup, tests, and documentation after user authorization. Exact model identifier/effort was not independently verified and is not asserted. The shell ran project-local package checks/build/tests; the browser-control tool exercised the localhost UI and captured actual screenshots. No GPT image generation or Figma design generation was used in this implementation turn. Existing Part 3.1 design artifacts remain intact; detailed Figma/Figma Make screens remain planned.

The user approved project-local pip 26.2 to resolve the earlier bootstrap advisory pause. The exact approved application pins were installed after artifact/advisory/binary/script inspection. No global package or additional direct dependency was added. The user supplied the 911 support direction; Codex rendered static text only, preserving the prohibition on automatic calling/messaging. Instructor approval is not claimed.

The app makes no model calls. Sensory steps and transitions are fixed application content. Responses and recent completion remain in memory only; no database or conversation persistence was created. Only fictional choices were used in testing. Retention/deletion and the precise future model role still need approval.

Actual evidence: 9 Node tests, 2 API tests, Vite build, import checks, pip check, npm ls, browser flow/keyboard checks, and support access while FastAPI was stopped. [Part 3.2 verification record](docs/part-3-2.md) links screenshots and commands. No clinical, measured completion-time, full accessibility, or cross-browser result is claimed. No commit/push occurred in this turn.

Revised approaches: the earlier environment pause was resolved by explicit pip-upgrade approval; a dependency inspector initially counted publishing-only hooks as install hooks, then distinguished them using npm's dependency-install lifecycle and source. No such hook was executed. Initial synchronous API tests hit sandbox/runtime limitations; tests switched to existing HTTPX ASGI transport and passed outside the sandbox. No extra test dependency was installed. A requested narrow viewport measured 340 CSS pixels in the browser, which is the width reported as evidence. A browser performance-API request-count probe was unavailable; no request-count measurement is claimed. Static support code and the backend-off walkthrough are the recorded evidence instead.

The sections below retain the Part 3.1 disclosure as historical evidence. Its statement that the final design commit did not yet exist was true at preparation; Git now confirms Part 3.1 commit `615ac73aaa933f8c3ce0004079f0179a133b35b1` and HEAD `003245f47958474e300920bb4b0127d275bedff4` on master.

## Tools and contributions

| Tool | Status and contribution | Model/version/effort |
| --- | --- | --- |
| Codex | Coding/documentation assistant; created scaffold, drafted documents, incorporated the course mapping, linked/inspected the existing flow image, checked files/Git/Markdown | Exact model, version, and effort not verified; not asserted |
| GPT image generation | Used to create the proposed user-flow diagram, according to the student disclosure and existing generation record; PNG manually added by the student | Exact model/version not verified; not asserted |
| Figma/Figma Make | Planned detailed mockup tool; written prompt prepared, no design file or generation output created | No tool version or generation model asserted |
| Figma connector/browser | Earlier access attempts only; account lookup failed twice; public homepage showed no signed-in design session | Not applicable to design generation |

The primary research source is the supplied Assignment 3 study summary/course material and R1–R4/D1–D6 mapping pasted by the project owner on 2026-10-15. Codex organized that material; it did not conduct the study or independently verify its observations. Findings inform design reasoning, not clinical effectiveness.

## Revised and failed approaches

The initial design draft left the research crosswalk pending. This revision replaces that approach with the complete supplied mapping and its tradeoffs. All seven permitted documentation files now treat the course findings as supplied.

Earlier Figma account lookup returned INVALID_ARGUMENT on two attempts. Browser fallback showed the public homepage without a signed-in design session. No Figma file was created. A written specification and ready-to-use prompt were prepared instead; they must not be presented as a completed mockup.

The GPT-generated flow diagram and later detailed Figma mockup are distinct artifacts. The student reviewed and adapted the generated design and manually added the PNG. The diagram now exists and was inspected without replacement, regeneration, or modification. This revision did not invoke image generation. The [recorded image-generation prompt](prompts/fifer-assignment-3-1-flow-imagegen.md) and [evidence note](docs/mockups/fifer-assignment-3-1-flow-evidence.md) already exist; no Figma Make prompt execution or completed Figma artifact is claimed.

## Evidence and limitations

Existing initial scaffold commit: 6ba3f7920c6e9daaf20a6ac2560a9ee3b5201408. Final design-package commit does not yet exist.

Actual work: repository inspection, course mapping incorporation, PNG existence/signature/dimensions and visual inspection, image-hash preservation check, and local heading/link/scope/whitespace checks. The flow diagram is 1536 × 1024 pixels and 1,674,030 bytes. The visual check confirmed the main journey and alternate paths; it did not test application behavior. Student review/adaptation is disclosed by the student; this is not participant testing. Runtime, measured timing, accessibility/usability review, detailed Figma exports, and final package approval remain pending. Documentation checks do not establish application or clinical results.

Prepared prompt: [assignment-3-1-design.md](prompts/assignment-3-1-design.md). Record later prompts, actual tool/model shown, output used, human edits, and verified artifact links when they exist.

## Data and scope

Use fictional scenarios only. Never include real distress disclosures or credentials in prompts, reports, screenshots, frontend code, or Git. No application code, dependencies, routes, components, tables, model integrations, or emergency contacts were created during this documentation revision. No commit or push was performed.
## V2 voice disclosure — 2026-10-26

Codex implemented the user-approved mock-only Gemini Live increment, local AudioWorklet/PCM handling, mock WebSocket relay, quota controls, tests and documentation. The target Live model is `gemini-3.8-live`; this is separate from text `gemini-2.5-flash`. No Gemini text or Live inference call was made, and no key was read or changed. No exact assistant model version/effort is asserted here.

Official Google Live model/API/audio/session docs and public package/advisory metadata were consulted. The only added dependency was the approved `websockets==17.3`, installed project-locally after wheel/hash/binary/entry-point/advisory checks. A synthetic oscillator replaced the microphone only in a disposable browser verification tab; no hardware audio, transcript or recording was saved. The mock returns a synthetic tone, not model speech. The tab was closed to remove the test override. See [V2 evidence and failed/corrected checks](docs/voice.md). No commit/push was made. Real transport, account access, costs and speech behavior remain unverified.
