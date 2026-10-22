# Fifer — safety design

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

D5/R4 inform recent-skill suggestions with Ignore/Change, never forced repetition or inferred distress. Interrupted usage must not be marked completed. The user has now approved local review/deletion and opt-in message retention until explicit deletion; exact model use remains unresolved. Never place credentials in frontend code, reports, screenshots, prompts, or Git.

## Verification plan and evidence

Later Parts 3.2/3.3 should verify fixed steps and optional input; one skippable after-Feel check-in; immediate Pause/Leave; support independent of model/backend; no automatic emergency contact; model timeout/invalid/stale fallback; optional recent skill; privacy controls; accessibility; and separate timing clocks.

The supplied course mapping informs these design decisions but does not prove safety or clinical effectiveness. Static Part 3.1 inspection of the manually added flow diagram found visible Pause/Stop/Leave/Support paths, model-independent support, no automatic calls/messages, and the coursework disclaimer. That was an image-content check only. At that milestone runtime evidence was not available. Current limited runtime evidence is linked above; no model or emergency-contact integration has been created.
