# Fifer — safety design

## Current Part 3.2 acceptance boundary

The setup-disconnect teardown regression is now corrected at the test boundary. Current evidence is 62/62 backend passes plus 25 consecutive focused passes. The focused test sends an abrupt disconnect directly to the ASGI endpoint, verifies mock-upstream close and reservation release, then verifies a fresh session separately. The earlier 60-pass/1-error result remains historical evidence, not the current status.

Fifer is a fictional coursework skills prototype, not therapy/diagnosis, a monitored service or a clinical-effectiveness demonstration. Static Support uses the owner's approved sentence, “Please contact 911 for emergency support.” Instructor approval of that specific wording remains Not verified, independently of owner-reported instructor approval for Gemini Live substitution. There is no phone handler, automatic call/message, distress classifier or risk score. Crisis-topic text retrieval returns reviewed safety wording without assessing the user.

Acceptance with FastAPI stopped opened Support from start, step, paused, unsaved/error and completion. Stop is immediate and records stopped, not completed; unfinished activity returns from Support/refresh paused. The app controls all fixed grounding steps/counts, timing and controls. Optional text/voice never replaces this flow. The old placeholder below is historical and not rendered.

Session/chat metadata and opted-in fictional messages remain until Delete/Clear; message saving is OFF by default, separate from OFF-by-default context sharing. Only completed count/latest skill/optional check-in can be shared after explicit choice. Sensory input is tab-only and excluded from storage/context; the test marker was absent from SQLite before Clear. No audio/transcripts are persisted, even with text saving ON. Clear left zero history records and reset saving OFF, retaining disclosed current-day anonymous quota counters. Schema/write-generation metadata remains; no external-backup erasure is promised.

All model observations are mocks: bounded text/HTTPX fixtures and synthetic voice events/audio. No real provider call or credential read occurred. One proposed Live model, no tools/second-model pipeline; server-owned prompt forbids medical advice/diagnosis/monitoring/invented history and control of skill/Support. Prompts alone do not prove enforcement or actual model safety. Mute stops capture but preserves playback/session; End/Support/navigation/failure cancels/cleans resources and rejects stale output. Backend/client maxima are separate. Abrupt termination and actual hardware/provider behavior remain unverified.

Text/voice quotas and time/token bounds are not dollar caps or verified per-person limits. Browser identity can be reset by clearing browser data; today's quota counters survive app history Clear. Any future real activation/test requires separate scope/cost approval plus account/billing review. No permission is implied by this report. The assignment's model-contribution demonstration remains unfinished. [Acceptance matrix](verification/part-3-2-acceptance.md) and [current requirements](assignment-3-submission-requirements.md) supersede historical status descriptions below.

## Earlier checkpoint notes (historical)

The remaining sections preserve earlier design/implementation decisions. Statements that exact model scope was unresolved or no voice existed refer to those earlier checkpoints, not current authorization. Part 3.1 research/mockup evidence is retained; no clinical benefit is established.

## Current mock-text increment — 2026-10-26

The approved optional text assistant is for fictional, non-emergency questions about existing Fifer skills/app usage. Its entire retrieval collection is the explicit curated `backend/chat_content.py`, derived from the existing app/skill/usage/privacy/safety rules. It never searches arbitrary files, private records or the web. Normal startup uses the deterministic local mock. The approved `gemini-2.5-flash` adapter is wired behind two server-only activation gates, and the key remains lazy; no real call or model output has been observed. Text is separate from Gemini Live voice and cannot perform crisis assessment.

The fixed grounding flow and static Emergency Support remain application-owned. Chat appears outside the active exercise. Stop, Support and navigation cancel/ignore pending text replies without awaiting model/storage. The backend also rejects late replies from stopped chats or after history Clear. Mock output must exactly match a retrieved paragraph; invalid output/timeout/failure uses fixed neutral fallback, with no retry. These checks do not prove future live-model safety.

Context sharing starts OFF independently of saving consent. Only actual completed-session count, latest completed skill and its optional check-in are eligible after explicit sharing. No profile exists; no sensory text, previous messages, narratives, audio or transcripts are supplied as context. Eligible fictional Chat messages follow the approved opt-in (default OFF), retain-until-deleted policy. Quota metadata is an explicitly documented operational exception: random browser identity (not verified person), backend hash/UTC date/count, 5 attempts per Chat session and 20/browser/UTC day. Today's counter survives history Clear; older counters are removed on a later day's request. Clearing browser data can reset identity. Fifteen-second requests and the future 300-output-token setting do not guarantee a dollar cap; live billing/call approval is still required.

The static support wording and unverified instructor approval below remain unchanged. No automatic calls/messages, diagnosis, treatment advice, therapist or monitoring claims are authorized.

Part 3.1 design recorded: 2026-10-15. Current implementation checkpoint added: 2026-10-22. Fifer is a coursework prototype only. It does not diagnose, provide therapy, imply human monitoring, claim clinical effectiveness, or replace emergency support. Use fictional scenarios only, never real distress disclosures.

## Current Part 3.2 implementation

The latest user approval supplied the basis for static text: “Please contact 911 for emergency support.” The frontend renders that text and the coursework notice without a phone link, network/model request, or automatic calling/messaging. Instructor approval has not been verified. The historical placeholder below is not used by the running UI. Additional crisis wording/contacts require approval.

Emergency Support is reachable on start, every category, check-in, paused, stopped, backend-error, and completion states. A browser check with FastAPI stopped opened this static panel. Returning to an unfinished activity requires explicit Resume. Stop/Leave has no confirmation gate and clears the current answers. Sensory examples are optional and unscored; no sense, action, quota, or disclosure is required.

The later storage authorization approves project-local session metadata and opted-in fictional messages. Metadata includes the optional check-in and separate clocks, but never sensory selections, personal narratives, or credentials. Message saving is OFF by default and requires explicit opt-in. Sessions and opted-in messages remain until the user deletes or clears them. Turning OFF prevents future message saves while keeping existing ones. Per-session Delete cascades linked conversations/messages. Clear all deletes all history and derived recent-skill history, discards pending tab writes, and resets opt-in to OFF. The database schema/nonpersonal write-generation counter remain; external backups are outside this action.

Only explicitly completed sessions produce saved recent-skill suggestions; Stop saves stopped status and never completion. Resume uses a saved step with empty sensory selections, opens paused, and requires explicit Resume. Setup, active, pause, and support clocks remain distinct; closed-browser downtime is excluded. Storage failure leaves the UI usable and displays unsaved status. Retry is explicit after failure; closing/reloading can lose unacknowledged snapshots, while the last saved checkpoint remains. Late writes with an old history generation are rejected after Clear/Delete.

There is no runtime model or classifier. The precise model role is still unapproved. Support opens from static content without a save/read request; its elapsed time is recorded on Return/Stop. No model failure can break the current deterministic flow because it has no model dependency. The historical planning sections below do not supersede the newly approved storage policy.

[Initial Part 3.2 evidence](part-3-2.md) records the first UI tests. [Storage verification](part-3-2-storage.md) records 16 frontend and 12 temporary-database API tests plus browser refresh/restart, failure/retry, local history, Delete, and Clear checks. Full accessibility, cross-browser, measured timing, and future model-failure verification remain pending. These checks do not establish safety or clinical effectiveness.

## User control

R3/R4 inform the ability to stop or leave at any time without consequence, explanation, or a confirmation gate. Keep Pause and Stop/Leave available throughout. Pause suspends active timing; Resume is explicit. Cancel pending model output on exit. Never force completion or auto-advance at 90 seconds or another time limit.

## Emergency Support

R2/D4 inform always-visible, frictionless Emergency Support. It opens immediately through application-controlled navigation independent of the model, any classifier, backend response, check-in, or disclosure. Model failure must not hide or delay it. Exclude support access from exercise timing; returning does not automatically resume.

Historical Part 3.1 placeholder, retained as design evidence only; instructor-approved wording remains unverified:

> EMERGENCY SUPPORT — PLACEHOLDER: Instructor-approved support information is pending. Fifer is only a coursework prototype. No one monitors this prototype. It does not replace emergency support or contact emergency services.

The placeholder is not an operational crisis resource and is not rendered by the app. No real crisis phone numbers were included in the Part 3.1 design; the current user-approved static 911 reference is described above. Do not automatically call, message, alert, or notify emergency services or contacts. Instructor confirmation of wording/jurisdiction remains a manual action.

## Deterministic flow and model failure

Application-controlled sequence: See 5 → Feel 4 → optional check-in → Hear 3 → Smell 2 → Taste 1 → completion. D1/D2 inform one category per screen; D3 informs optional input and a lightweight check-in. Do not use a distress detector. Allow unavailable/uncomfortable senses to be skipped without reordering categories or requiring touching, smelling, eating, or drinking.

An optional model may provide brief transitions, reflection, post-exercise summary, or supported-skill selection assistance. It cannot alter skill steps, diagnose, assess safety, infer distress, invent therapeutic advice, or control support access.

Model timeout, unavailable/invalid output, or stale response must not break the deterministic flow. Use fixed neutral copy and preserve Continue, Pause, Stop/Leave, and Emergency Support. Later implementation must reject out-of-scope output and ignore late responses. A prompt alone does not prove enforcement.

## Privacy and personalization

Historical Part 3.1 proposal: sessions, completed skill usage/recent skill, optional check-in response, and fictional conversation messages if needed. The current approved database/policy is described above. There are no diagnostic/risk fields or stored sensory answers.

D5/R4 inform recent-skill suggestions with Ignore/Change, never forced repetition or inferred distress. Interrupted usage must not be marked completed. The user approved local review/deletion, opt-in message retention until explicit deletion, and the bounded curated text scope described above. Real provider execution still requires separate approval. Never place credentials in frontend code, reports, screenshots, prompts, or Git.

## Verification plan and evidence

Later Parts 3.2/3.3 should verify fixed steps and optional input; one skippable after-Feel check-in; immediate Pause/Leave; support independent of model/backend; no automatic emergency contact; model timeout/invalid/stale fallback; optional recent skill; privacy controls; accessibility; and separate timing clocks.

The supplied course mapping informs these design decisions but does not prove safety or clinical effectiveness. Static Part 3.1 inspection of the manually added flow diagram found visible Pause/Stop/Leave/Support paths, model-independent support, no automatic calls/messages, and the coursework disclaimer. That was an image-content check only. At that milestone runtime evidence was not available. Current limited runtime evidence is linked above; no model or emergency-contact integration has been created.
## V2 mock voice safety boundary — 2026-10-26

The user approved a separate mock-only Live voice increment. Real Gemini text/Live calls remain unauthorized. Voice is optional outside grounding; no model controls skill order/counts, timing, completion, Pause/Resume, Stop/Leave or Emergency Support. The backend owns model/instructions and accepts no client overrides. The actual mock cannot understand speech and is labelled as returning a synthetic tone.

No audio/transcripts are saved, logged as content, or used as text context; text-message opt-in never authorizes voice storage. No profile/check-in/history sharing is implemented for voice. Stop, Support, tab hiding, navigation, timeouts and errors end capture/playback/sockets and ignore late output. Support still opens instantly from the same approved static frontend text when FastAPI is down. No contact/link/automatic calling, monitoring, diagnosis or clinical claim was added. Instructor approval of the specific support wording remains unverified.

The approved 300-second, five-turn, per-turn and two-start daily bounds are enforced in the mock path. Operational voice quota stores only browser hash/UTC date/start count, survives today's Clear and expires on a later-day voice request. It is not per-person authentication or a dollar cap. No local recording is not a promise about future provider-side data use; review that before any separately approved live activation. See [voice evidence](voice.md).
