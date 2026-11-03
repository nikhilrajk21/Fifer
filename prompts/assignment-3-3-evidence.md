# Assignment 3.3 — curated AI and verification evidence

Date: 2026-11-02. This is a concise, redacted project evidence log. It does not reproduce private chat exports, credentials, personal information, course UI content, or research-participant material. Scenarios and test data are fictional.

## Assistance and approved change

Codex assisted with code, mock tests, documentation, and evidence organization. The exact Codex model identifier and effort are not available, so neither is asserted. The approved text-contract change allows a brief plain-language paraphrase based on one retrieved curated Fifer source; only the app-supplied completed-session count, most recent completed skill, and optional check-in may be used when context sharing is explicitly ON. No model controls the grounding sequence, Stop/Leave, or static Emergency Support. The default remains mock, and no provider call was made for this update.

GPT image generation was used earlier for the proposed flow diagram; the student reviewed/adapted that artifact. Figma/Figma Make is planned for detailed screens; no completed Figma mockup is claimed. No exact image-generation model/version or Codex model/effort is asserted.

## Revised approach and surprising limitation

The initial exact-paragraph response contract was changed only after explicit approval to permit concise paraphrase. One-source retrieval, source attribution, output limits, consent, quotas, timeout, no retry, and fallback remain in place. Focused mock cases cover a valid paraphrase and failures such as mismatched source ID, malformed/oversized output, provider errors, context OFF versus explicitly shared fields, and sanitized diagnostic logging.

Surprising finding: a deliberately unsupported sentence can have valid structure and the correct source ID and still pass. The validator proves structural constraints and citation identity, not semantic entailment. The prompt expresses a boundary but does not guarantee it. This is recorded as an untested/unsolved semantic-grounding limitation; no keyword filter is represented as comprehensive safety validation.

## Verification evidence

Historical bounded checks at the prior mock-test checkpoint:

- Backend: 74 passed, 0 failed using the existing unittest suite, fictional fixtures, HTTPX mock transports, and temporary databases. The Windows Proactor async setup stalled before async setup in the ordinary sandbox; a bounded socketpair reproduction stalled there too. The full suite completed in an outside-sandbox run. No production workaround was added. An earlier run had one fixture-isolation failure (73 passed, 1 failed); after resetting the mock override, the latest run passed.
- Frontend: 51 passed, 0 failed.
- Production build: passed; 28 modules transformed.
- No provider call, package install, environment-file read, or database reset occurred in this documentation update.

Live events are kept separate: an earlier fictional request showed the fallback `upstream_model_unavailable`; a metadata-only request returned no HTTP status; the first post-configuration generation request returned HTTP 200 but failed as `invalid_output` before the `thoughtSignature` parser fix. The owner reports exactly one subsequent successful generated Gemini text response after that fix. Its answer and visible source title are not in the retained evidence, so content/source review is unavailable. No additional live call was made during this update. Do not infer broad provider access, billing, or semantic grounding from this single owner-reported response or from mocks/configuration.

Owner-supplied targeted retests: S03 context OFF Pass; S04 context ON Pass; S11 same-tab Pause/Resume intermittent/Partial before the focused snapshot fix and pending manual retest; S11 recovery after refresh Pass; S13 completed-session review Pass. Previously recorded browser/mock evidence for M04, M12, M18, I2 and keyboard-only remains in the evaluation plan. The owner says a video was recorded; its link is unavailable. The recording's coverage of both a finished-app demo and the failure/evidence/decision process cannot be verified. **Video link:**

This revision adds an explicit in-memory Pause snapshot/Resume restoration for screen, transient optional selections/responses and check-in, while persistence still excludes sensory data; Stop clears the snapshot. Focused regression tests cover all sequence positions, repeated cycles, stale state, Support return and Stop/privacy boundaries. The updated implementation was not manually retested after this change, so S11 remains Partial. Full frontend tests/build passed in this revision; the bounded backend suite timed out at Windows async setup, while 12 synchronous Gemini diagnostic/contract tests passed. No provider call, dependency installation or environment-file read occurred during this update.

## Evidence links

- [Assignment 3.3 evaluation plan](../docs/assignment-3-3-evaluation-plan.md)
- [Current report](../report.md)
- [Part 3.2 historical report](../report-3-2.md)
- [Part 3.2 acceptance evidence](../docs/verification/part-3-2-acceptance.md)
- [Text adapter notes](../docs/text-chat.md)

No commit, push, or course submission was made in this update.
