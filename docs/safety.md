# Fifer — safety design

Updated: 2026-10-15. Fifer is a coursework prototype only. It does not diagnose, provide therapy, imply human monitoring, claim clinical effectiveness, or replace emergency support. Use fictional scenarios only, never real distress disclosures.

## User control

R3/R4 inform the ability to stop or leave at any time without consequence, explanation, or a confirmation gate. Keep Pause and Stop/Leave available throughout. Pause suspends active timing; Resume is explicit. Cancel pending model output on exit. Never force completion or auto-advance at 90 seconds or another time limit.

## Emergency Support

R2/D4 inform always-visible, frictionless Emergency Support. It opens immediately through application-controlled navigation independent of the model, any classifier, backend response, check-in, or disclosure. Model failure must not hide or delay it. Exclude support access from exercise timing; returning does not automatically resume.

Instructor-approved crisis wording is still pending. Until supplied, use this clearly marked design placeholder:

> EMERGENCY SUPPORT — PLACEHOLDER: Instructor-approved support information is pending. Fifer is only a coursework prototype. No one monitors this prototype. It does not replace emergency support or contact emergency services.

The placeholder is not an operational crisis resource. No real crisis phone numbers are included. Do not automatically call, message, alert, or notify emergency services or contacts. Approved wording, jurisdiction, and any contact details require instructor provision/approval.

## Deterministic flow and model failure

Application-controlled sequence: See 5 → Feel 4 → optional check-in → Hear 3 → Smell 2 → Taste 1 → completion. D1/D2 inform one category per screen; D3 informs optional input and a lightweight check-in. Do not use a distress detector. Allow unavailable/uncomfortable senses to be skipped without reordering categories or requiring touching, smelling, eating, or drinking.

An optional model may provide brief transitions, reflection, post-exercise summary, or supported-skill selection assistance. It cannot alter skill steps, diagnose, assess safety, infer distress, invent therapeutic advice, or control support access.

Model timeout, unavailable/invalid output, or stale response must not break the deterministic flow. Use fixed neutral copy and preserve Continue, Pause, Stop/Leave, and Emergency Support. Later implementation must reject out-of-scope output and ignore late responses. A prompt alone does not prove enforcement.

## Privacy and personalization

Proposed data only: sessions, completed skill usage/recent skill, optional check-in response, and fictional conversation messages only if model interaction is used. No database exists. No diagnostic/risk fields or stored sensory answers are proposed. Conversation persistence defaults off pending consent/retention decisions.

D5/R4 inform recent-skill suggestions with Ignore/Change, never forced repetition or inferred distress. Interrupted usage must not be marked completed. Retention, local history, deletion, and message-storage need remain unresolved. Never place credentials in frontend code, reports, screenshots, prompts, or Git.

## Verification plan and evidence

Later Parts 3.2/3.3 should verify fixed steps and optional input; one skippable after-Feel check-in; immediate Pause/Leave; support independent of model/backend; no automatic emergency contact; model timeout/invalid/stale fallback; optional recent skill; privacy controls; accessibility; and separate timing clocks.

The supplied course mapping informs these design decisions but does not prove safety or clinical effectiveness. Static inspection of the manually added flow diagram found visible Pause/Stop/Leave/Support paths, model-independent support, no automatic calls/messages, and the coursework disclaimer. This is an image-content check only. Runtime, accessibility, measured timing, and detailed Figma screen verification results are **Not yet available**. No application, model integration, or emergency-contact integration has been created.
