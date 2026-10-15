# Fifer — Assignment 3.1

## Repository and commit

Repository: [nikhilrajk21/Fifer](https://github.com/nikhilrajk21/Fifer).
Branch: `master`.
Initial commit: `6ba3f7920c6e9daaf20a6ac2560a9ee3b5201408` — “Initialize Fifer Assignment 3 project”.

The final design-package commit does not yet exist. These documentation changes remain uncommitted; no commit or push was performed.

## Application concept

Fifer is a local coursework prototype for a fictional student experiencing conflict, self-doubt, or an emotionally difficult day, such as disagreement about a group assignment. It offers quick access to 5-4-3-2-1 sensory grounding without requiring a personal narrative.

The selected skill provides five predictable categories suited to atomic screens and optional responses (D1–D3). R1 informs concise pacing; R3/R4 preserve autonomy. Fifer does not diagnose, provide therapy, imply human monitoring, replace emergency support, or claim clinical effectiveness. Use fictional scenarios only.

## Research foundation

The supplied Assignment 3 study summary/course material is the primary source. Its design logic maximizes agency while minimizing cognitive and emotional effort: one atomic step at a time, optional choices, frictionless persistent safety access, and calm presentation without forced clinical pathways.

| Finding | Observation in supplied course material | Fifer design response | Tradeoff or limitation |
| --- | --- | --- | --- |
| R1 | Around 60 seconds was comfortable; attention declined beyond 90–100 seconds and longer skills lost participants. | Target 60–75 seconds, budget 65 seconds, and keep the standard unpaused exercise under 90 seconds. | Concise pacing can feel rushed; users retain their own pace and may continue beyond the target. |
| R2 | Participants wanted frictionless crisis access without navigating multiple screens. | Keep Emergency Support visible and open it immediately from every state. | Persistent access uses screen space and can cause accidental taps. |
| R3 | Permission architecture: participants needed to know they could stop and leave without consequence. | Keep Pause and Stop/Leave accessible; no explanation or completion requirement. | Prominent exit options may encourage ending before completing the sequence; leaving remains valid. |
| R4 | Participants wanted options and control of their journey rather than forced routing. | Simple start choice, optional sensory answers, and dismissible recent-skill suggestions. | More choices can add cognitive load when deciding what to do. |
| D1 | Progressive interface contraction: higher distress calls for less interface content; the study does not establish a distress detector. | Use one category at a time and a low-stimulus interface without automatic distress detection. | Adaptation relies on manual pacing, not detected distress. |
| D2 | Participants responded to one atomic action per screen. | Present one sensory category per screen in a fixed sequence. | More screens require more transitions and taps. |
| D3 | Minimize emotional cost: avoid demands to feel, disclose, type, or perform. | Selectable optional answers, Continue without selecting, and one lightweight check-in after Feel. | Minimal disclosure/data limits detailed emotional reflection and long-term tracking; deep tracking is not a prototype goal. |
| D4 | Safety access should remain persistently visible during the exercise. | Keep Emergency Support visible on exercise and alternate-state screens. | Constant safety presence may heighten anxiety for some users who are not in crisis. |
| D5 | Personalization should use prior activity without configuration burden. | Suggest the recently completed skill without profiles, forced setup, or forced repetition. | The suggested skill may not be wanted today; Ignore and Change remain available. |
| D6 | Use low-stimulus, non-judgmental language; avoid clinical, cheerful, saturated, or demanding presentation. | Dusty blue/lavender surfaces, restrained visuals, and calm, non-clinical wording. | A muted interface may feel passive to someone seeking energetic motivation. |

Three overall tradeoffs:

1. **Agency versus cognitive fatigue:** choice and optional answers preserve autonomy but can add decision effort. Keep a clear Begin grounding action and a small set of optional choices.
2. **Frictionless safety versus visual presence:** persistent support enables immediate access but uses space and may cause accidental taps or anxiety. Keep a stable, readable label without flashing or alarm-like decoration.
3. **Simplicity versus depth of tracking:** atomic, low-demand steps limit overload and attention demands but restrict deep reflection and detailed history. Collect only justified prototype data.

Personalization remains subordinate to user control (R4/D5); optional input must reduce emotional effort without adding excessive choices (D3). Model assistance is optional because it adds unpredictable output/latency; deterministic skill steps remain an application safety constraint. Calm visuals must preserve prominent safety access (R2/D4/D6).

Citation note: Primary source: the supplied Assignment 3 study summary/course material, including the R1–R4/D1–D6 mapping pasted by the project owner on 2026-10-15. This is the course-source attribution; no external citation, publication title, author, or URL has been invented. The findings inform design reasoning but do not prove clinical effectiveness.

## User journey and flow

| Stage | Proposed interaction |
| --- | --- |
| Start choice | Begin grounding immediately; optional Help me choose and recent-skill suggestion |
| See | Notice five things you can see; optional selectable neutral examples |
| Feel | Notice four things you can feel; optional selections |
| Check-in | After Feel only: “A little better”, “About the same”, “A little harder”, “Not sure”, or Skip check-in |
| Hear | Notice three things you can hear; optional selections |
| Smell | Notice two things you can smell, if available; optional selections |
| Taste | Notice one taste already present, if available; optional selections |
| Completion | Neutral acknowledgement; Finish/Leave, return to choices, or optional repeat |

Present one category per screen. Continue without selecting works; no required typing, disclosure, selection quota, or safety score. Allow unavailable/uncomfortable categories to be skipped while preserving order. Do not require seeking smells or consuming items. Steps and counts are application-controlled.

Alternate paths: Pause suspends timing and explicit Resume restores the same state. Stop/Leave exits immediately without explanation or a confirmation gate and marks stopped, not completed. Emergency Support opens immediately, pauses exercise timing, and does not auto-resume on return. Model failure uses fixed neutral copy, ignores stale output, and leaves the deterministic sequence and all controls usable.

## Design and mockup

Dusty blue/lavender, generous whitespace, short non-judgmental copy, and one activity per screen follow D6. Avoid clinical, excessively cheerful, saturated, or demanding presentation, flashing, autoplay audio, and countdown pressure. Proposed colors: canvas #F5F6FA, blue #D8E5EE, lavender #E5DEF0, text #263445, action #405B78.

Pause, Stop/Leave, and Emergency Support retain stable positions. Support stays visible on every main/alternate screen. Proposed review targets: readable 16 px body text, 44 × 44 px controls, visible focus, keyboard access, and small-width layout. Contrast and accessibility remain to be reviewed.

![Fifer Assignment 3.1 proposed user flow](docs/mockups/fifer-assignment-3-1-flow.png)

This GPT-generated diagram is the proposed user flow, manually added by the student. The student reviewed and adapted the generated design. Static inspection confirmed a 1536 × 1024 PNG showing the eight-stage journey, the check-in after Feel, optional answers, persistent controls, and the four alternate paths. The existing image was not replaced, regenerated, or modified. This inspection is not usability testing, a timing measurement, or implementation evidence.

The later detailed editable Figma/Figma Make screen design is a separate next step. It will show screen layouts, controls, states, and prototype navigation. Its actual link, exports, revision, and review are **Not yet available**. Earlier Figma account lookup failed twice; browser fallback showed no signed-in design session. No Figma artifact or export is currently present in this repository.

## Model role and safety boundaries

An optional model may provide brief transitions, reflection, a post-exercise summary, or help choosing a supported skill when asked. It cannot change the grounding sequence, diagnose, assess safety, infer distress automatically, invent therapeutic advice, or control Emergency Support. The primary flow works without a model; none is integrated.

Emergency Support is always visible and opens immediately, independently of the model, any classifier, or backend response. No automatic calls/messages to emergency services or contacts.

Instructor-approved crisis wording is pending. Current design placeholder:

> EMERGENCY SUPPORT — PLACEHOLDER: Instructor-approved support information is pending. Fifer is only a coursework prototype. No one monitors this prototype. It does not replace emergency support or contact emergency services.

This placeholder is not an operational crisis resource. No real crisis phone numbers are included. Users can stop or leave at any time; model failure must not break the deterministic flow.

## Data and personalization plan

Proposed SQLite records only; no database or tables exist:

| Record | Intended data |
| --- | --- |
| Sessions | Identifier, start/end, completed/stopped/incomplete status, separate timing durations |
| Skill usage/recent skill | Session, supported skill, completion status/time; derive recent only from explicitly completed usage |
| Check-in response | Optional fixed response after Feel; Skip stores no response; no safety score |
| Conversation messages, if used | Session, role, fictional content, timestamp; persistence off pending consent/retention decisions |

Suggest the recently completed skill with Start again, Ignore, and Change. Never force a recommendation or infer distress. With only 5-4-3-2-1 supported, Change returns to choices. Propose no accounts or stored sensory answers. History persistence, retention, consent, deletion, and conversation-storage need remain open.

## Timing plan

R1 informs a target of approximately 60–75 seconds and a standard unpaused exercise under 90 seconds. Proposed budget: See 12 + Feel 12 + check-in 5 + Hear 12 + Smell 10 + Taste 9 + completion 5 = **65 seconds**.

Measure setup separately, from entry until Begin. Active timing starts at See. User pauses and crisis-support access are excluded and recorded separately. Model text must not block progress. Measured timing is **Not yet available**.

Never force completion or auto-advance at a time limit. Record user pacing beyond 90 seconds honestly and revise the design rather than imposing a deadline.

## Verification plan

Part 3.2, proposed after authorization: verify Vue → FastAPI → SQLite with fictional data; fixed steps/counts; optional zero-input progression; one after-Feel check-in; Pause/Resume; immediate Stop/Leave and independent support; model timeout/invalid/stale fallback if used; recent-skill choice; data limits; separate clocks.

Part 3.3, proposed: fictional end-to-end main/alternate walkthroughs; keyboard/focus, contrast, layout, and sensory-accessibility review; slow/offline/model-failure cases; timing measurements; privacy review; reproducible evidence tied to the tested commit.

Confirm the detailed Part 3.2/3.3 rubric. No runtime, usability, accessibility, or mockup test results are claimed. Local documentation checks cover heading structure, file scope, and whitespace only.

## AI disclosure and evidence log

Codex is the coding/documentation assistant. It prepared the scaffold and design documents, incorporated the supplied course mapping, linked the manually added flow diagram, and performed static image/file/Git/Markdown checks. Exact Codex model and effort are not verified and are not asserted.

GPT image generation was used to create the flow diagram, as disclosed by the student and recorded in the existing generation prompt/evidence note. The student reviewed and adapted the generated design and manually added the PNG. This documentation revision inspected that existing artifact without generating or editing it. Figma/Figma Make is the planned future tool for detailed screen design; no completed Figma artifact is claimed. No tool versions or image-generation model names are invented.

Revised approach: the earlier research placeholders were replaced with the supplied course mapping. Failed approach: Figma account lookup returned errors twice, and browser fallback did not reach a signed-in design session. A written design specification/prompt was prepared; the separately generated flow diagram now provides proposed-flow evidence while detailed Figma design remains pending.

Actual evidence includes repository inspection, supplied mapping review, PNG existence/signature/dimensions and visual inspection, an unchanged-image hash check, and local documentation checks. Measured timing, detailed Figma design, and application verification evidence remain pending. See [AI-USE.md](AI-USE.md), the [flow evidence note](docs/mockups/fifer-assignment-3-1-flow-evidence.md), and the [recorded generation prompt](prompts/fifer-assignment-3-1-flow-imagegen.md).

## Project context and next steps

Fifer remains independent of Expedia Lite. Reuse only Vue/FastAPI/SQLite separation, optional conversation persistence concepts, and documentation/verification practices. No files or travel-domain functionality were copied.

Existing project documents: [research](docs/research.md), [design](docs/design.md), [safety](docs/safety.md), [AI use](AI-USE.md), [handoff](handoffs/current.md), and [design prompt](prompts/assignment-3-1-design.md). Existing mockup evidence: [proposed user-flow diagram](docs/mockups/fifer-assignment-3-1-flow.png), [flow evidence note](docs/mockups/fifer-assignment-3-1-flow-evidence.md), and [recorded generation prompt](prompts/fifer-assignment-3-1-flow-imagegen.md).

The next design step is creating and reviewing the detailed Figma/Figma Make mockup. Instructor-approved crisis-support wording is still pending. Prepare Part 3.2 requirements and verification plans; Part 3.2 implementation has not started. Also resolve final check-in/skip wording, model inclusion/failure policy, contrast, data retention/consent/deletion, and timing evidence.

The application is not implemented. No dependencies, frontend components, backend routes, SQLite tables, or model integrations were created. No commit or push was performed.
