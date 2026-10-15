# Fifer — Assignment 3.1 design specification

Updated: 2026-10-15. Design milestone only; no working application exists. The supplied course findings and complete mapping are recorded in [research.md](research.md).

## Concept and selected skill

Fifer offers 5-4-3-2-1 sensory grounding to a fictional student experiencing conflict, self-doubt, or an emotionally difficult day. Example: a disagreement over a group assignment. Begin without describing the situation. Fifer is only a coursework prototype; it does not diagnose, provide therapy, claim clinical effectiveness, imply human monitoring, or replace emergency support.

The selected skill fits D1/D2's reduced, atomic interface and D3's low-demand participation. R1 informs short pacing; R3/R4 preserve autonomy. The application, never a model, controls the counts and sequence.

## Main journey

| Screen | Proposed interaction | Research connection |
| --- | --- | --- |
| Start choice | “What would you like to do?”; Begin grounding immediately; optional Help me choose and recent-skill suggestion | R4 choice; D3 low effort; D5 no setup burden |
| See — 5 | “Notice five things you can see.” Optional selectable examples: desk, window, book, light, bag | D1/D2 one category; D3 optional input |
| Feel — 4 | “Notice four things you can feel.” Optional feet on floor, chair, sleeve, tabletop; no required touching | D2 atomic step; D3 no performance demand |
| Check-in | After Feel only: “How are you feeling right now?”; “A little better”, “About the same”, “A little harder”, “Not sure”, or Skip check-in | D3 lightweight response; R4 choice |
| Hear — 3 | “Notice three things you can hear.” Optional fan, footsteps, outside sounds | D1/D2 atomic category; D3 low effort |
| Smell — 2 | “Notice two things you can smell, if available.” Optional examples; do not seek or inhale items | D2 one category; D3 optional participation |
| Taste — 1 | “Notice one taste already present, if available.” Optional existing/no noticeable taste; no eating/drinking requirement | D2 one category; D3 optional participation |
| Completion | Neutral acknowledgement; Finish/Leave, return to choices, or optional repeat | R3/R4 user choice; D5 later recent-skill suggestion |

Each category appears alone. Sensory selections are optional, not quotas or correct answers. Continue without selecting must work. Allow skipping an unavailable/uncomfortable category without reordering the fixed sequence; label skipped steps honestly. No required typing, disclosure, scoring, or safety inference. Continue and Finish are explicit user actions.

## Persistent controls and alternate paths

Emergency Support remains visible on all main and alternate screens (R2/D4). Keep Pause and Stop/Leave in stable positions (R3). Pause indicates inactive/already-paused status when no exercise clock runs.

| Path | Required design behavior |
| --- | --- |
| Pause | Suspend active timing immediately; explicit Resume restores the same step and selections; support/leave stay available |
| Stop/Leave | Leave immediately without a reason, confirmation gate, or consequence; cancel pending model output; status stopped, not completed |
| Emergency Support | Open immediately without model/classifier/backend permission or disclosure; pause exercise timing; Return restores state without auto-resuming |
| Model failure | Use fixed neutral copy, “You can continue when you’re ready.” Keep the deterministic sequence, Continue, Pause, Stop/Leave, and support usable; ignore stale output |

Instructor-approved crisis wording is pending. Use only the clearly marked placeholder in [safety.md](safety.md); no real crisis phone numbers or automatic calls/messages.

## Personalization and proposed data

D5 motivates suggesting the most recently completed skill without configuration; R4 requires Start again, Ignore, and Change. Only 5-4-3-2-1 is currently supported: Change returns to choices rather than advertising other skills. Never force repetition or infer distress from behavior. Derive recent usage only from explicitly finished sessions, not interruptions.

Proposed SQLite records only:

| Record | Candidate data and purpose |
| --- | --- |
| Sessions | id, start/end, completed/stopped/incomplete status, setup_ms, active_ms, paused_ms, support_ms |
| Skill usage/recent skill | session_id, skill_id, completion status/time; derive latest completed skill |
| Check-in response | session_id, after-Feel marker, optional response code/time; Skip stores no response |
| Conversation messages, if used | session_id, role, fictional content, timestamp; persistence off by default pending consent/retention decisions |

No tables/database exist. Propose no accounts or stored sensory answers. Decide history persistence, deletion, retention, and whether conversation storage is necessary before implementation.

## Visual direction and mockup

D6 informs dusty blue/lavender, calm non-judgmental copy, generous whitespace, and low-stimulus surfaces. Avoid clinical, excessively cheerful, saturated, or demanding presentation, flashing, autoplay audio, and countdown pressure. R2/D4 still require clearly readable persistent controls.

Proposed palette: canvas #F5F6FA; dusty blue #D8E5EE; lavender #E5DEF0; text #263445; action #405B78. Proposed Inter, body at least 16 px, controls at least 44 × 44 px, visible focus, keyboard access, and small-width review. Contrast/accessibility are review targets, not verified results.

The [GPT-generated proposed user-flow diagram](mockups/fifer-assignment-3-1-flow.png) now exists as a 1536 × 1024 PNG manually added by the student. The student reviewed and adapted the generated design. Static inspection confirmed the eight-stage journey, after-Feel check-in (including “Not sure”), optional responses, persistent controls, and four alternate paths. The image was not replaced, regenerated, or modified. It is a flow overview, separate from the later detailed editable Figma/Figma Make screen mockup. See the existing [evidence note](mockups/fifer-assignment-3-1-flow-evidence.md).

Detailed Figma/Figma Make link, revision, exports, and review: **Not yet available**. Earlier account lookup failed twice; browser fallback showed a public page without a signed-in design session. No Figma artifact or export is currently present in this repository. [Design prompt](../prompts/assignment-3-1-design.md) is prepared but not submitted to Figma/Figma Make.

Mockup inventory: eight main screens plus Pause, Stop/Leave, Emergency Support, Help me choose, recent-skill choice, and model-failure states. Review actual navigation and layout before recording completion.

## Timing target

R1 informs approximately 60–75 seconds and a standard unpaused exercise under 90 seconds. Proposed budget: See 12 + Feel 12 + check-in 5 + Hear 12 + Smell 10 + Taste 9 + completion 5 = 65 seconds. This is an estimate, not a measured result.

Measure setup separately from entry to Begin. Active timing starts at See. Exclude user pauses and crisis-support access and record them separately. Optional model output must never block progression. Never auto-advance or force completion at a time limit; user pacing may exceed the target and must be recorded honestly.

## Model boundaries

Optional model assistance may give brief transitions, reflection, a post-exercise summary, or help choose a supported skill when asked. The model cannot change the skill instructions, counts, order, timing/control rules, or support access. It cannot diagnose, assess safety, infer distress automatically, invent therapeutic advice, or control Emergency Support. Use fictional context only. No model integration exists.

## Tradeoffs and open decisions

R4/D5 personalization can reduce setup but must remain dismissible. D3 optional input avoids narrative effort but choice sets still add reading. Model assistance adds variation but also latency/unpredictability; deterministic steps and fallback take priority. D6 calm surfaces must preserve R2/D4 control visibility.

Open: final check-in/skip wording; model inclusion/provider/failure policy; history consent/retention/deletion; palette contrast and sensory accessibility; reference-screen priority; instructor-approved crisis text; detailed rubric; actual timing and mockup evidence.

## Verification and project context

Part 3.2, after authorization: verify Vue → FastAPI → SQLite with fictional data, fixed sequence/counts, optional input, one check-in after Feel, Pause/Resume, immediate leave/support, model-failure fallback, recent-skill choice, persistence limits, and separate clocks.

Part 3.3, proposed: fictional end-to-end main/alternate walkthroughs, keyboard/focus/contrast/layout review, slow/offline/model-failure cases, timing measurement, privacy review, and reproducible evidence. Confirm the rubric first. Only the static flow image was inspected; no runtime, usability, accessibility, or detailed screen-mockup test results are claimed. Part 3.2 implementation has not started.

Fifer is independent from Expedia Lite. Reuse only Vue/FastAPI/SQLite separation, optional conversation persistence concepts, and documentation/verification practices; no copied files or travel functionality.
