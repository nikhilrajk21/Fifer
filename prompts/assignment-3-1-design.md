# Assignment 3.1 — Fifer design prompt

Updated: 2026-10-15. Prepared by Codex; exact model/version/effort not verified. This Figma/Figma Make prompt has not been submitted. A separate GPT image-generation prompt and resulting flow diagram now exist.

## Research context

Use the supplied Assignment 3 study summary/course material as the primary source:

- R1: around 60 seconds was comfortable; attention declined beyond 90–100 seconds → concise 60–75-second target, standard unpaused flow under 90.
- R2: frictionless crisis access → immediately accessible, visible Emergency Support.
- R3: permission to stop without consequence → Pause and Stop/Leave throughout.
- R4: options and self-directed journey → simple start choice, optional input, no forced recommendation.
- D1: less interface content as emotional load rises, without an established detector → low-stimulus single-category screens; no automatic distress detection.
- D2: one atomic action per screen → one sensory category at a time.
- D3: minimize demands to feel/disclose/type/perform → optional selections and lightweight after-Feel check-in.
- D4: persistently visible safety → support on every main/alternate screen.
- D5: personalization without configuration → optional recently completed skill suggestion.
- D6: low-stimulus, non-judgmental, non-clinical language → dusty blue/lavender and restrained copy.

Full observations, responses, and tradeoffs: [research.md](../docs/research.md). These findings inform design reasoning, not clinical effectiveness. Do not invent external citations.

## Existing flow-diagram reference

GPT image generation was used to create the [proposed user-flow diagram](../docs/mockups/fifer-assignment-3-1-flow.png), manually added by the student. The student reviewed and adapted the generated design. The image shows start choice → See 5 → Feel 4 → check-in → Hear 3 → Smell 2 → Taste 1 → completion, plus Pause, Stop/Leave, Emergency Support, and model-failure paths. The check-in includes “Not sure” alongside the other documented options.

The existing [generation prompt](fifer-assignment-3-1-flow-imagegen.md) records its creation brief. This is a static flow overview, not a detailed Figma mockup or application behavior. Preserve the PNG; do not replace, regenerate, or modify it. Use it as reference for the later detailed screen design.

## Prompt for the later Figma/Figma Make mockup

Create editable design screens/prototype navigation for “Fifer — Assignment 3.1”, a coursework prototype for a fictional student experiencing conflict, self-doubt, or an emotionally difficult day. This is a design artifact, not a working application. Do not create backend routes, application components, SQLite tables, model integrations, or install dependencies.

Use dusty blue/lavender, generous whitespace, short calm non-judgmental copy, and no clinical/overly cheerful/saturated/demanding presentation. Avoid flashing, autoplay audio, decorative motion, and countdown pressure. Proposed colors: #F5F6FA canvas, #D8E5EE blue, #E5DEF0 lavender, #263445 text, #405B78 action. Review contrast, readable text, keyboard focus, targets, and small-width layout before claiming accessibility.

Create eight main screens:

1. Start choice: “What would you like to do?”; Begin grounding immediately; optional Help me choose and recently completed skill suggestion. No login, disclosure, or model wait.
2. See: notice five visible things; optional selectable desk/window/book/light/bag examples.
3. Feel: notice four things felt; optional feet on floor/chair/sleeve/tabletop; no required touching.
4. One lightweight check-in after Feel: “A little better”, “About the same”, “A little harder”, “Not sure”, or Skip check-in. No safety score.
5. Hear: notice three sounds; optional selections.
6. Smell: notice two smells if available; do not require seeking/inhaling an item.
7. Taste: notice one taste already present if available; no eating/drinking requirement.
8. Completion: neutral acknowledgement, Finish/Leave, return to choices, or optional repeat; never automatic restart.

Keep the sequence/counts application-controlled. Show one category per screen. Optional input is not a quota; Continue without selecting works. Allow unavailable/uncomfortable categories to be skipped without reordering. No required typing, disclosure, or performance scoring.

Keep Emergency Support always visible and immediately accessible, independent of model/classifier/backend/disclosure. Keep Pause and Stop/Leave available in stable locations. Indicate inactive/already-paused Pause when no clock runs.

Create alternate states: Pause with explicit Resume restoring the same step; immediate Stop/Leave without consequence/reason/confirmation gate; support that pauses timing and does not auto-resume on return; and model failure with fixed neutral copy and working controls. Cancel/ignore stale model output after navigation.

Use this placeholder until the instructor approves crisis wording:

“EMERGENCY SUPPORT — PLACEHOLDER: Instructor-approved support information is pending. Fifer is only a coursework prototype. No one monitors this prototype. It does not replace emergency support or contact emergency services.”

Do not add real crisis phone numbers, automatic emergency calls/messages, diagnostic claims, therapy claims, or real distress disclosures.

Recent-skill suggestion: Start again, Ignore, and Change. Only 5-4-3-2-1 is supported; Change returns to choices. No forced recommendation, profile configuration, or automatic distress inference.

Optional model role: brief transitions/reflection/summary or supported-skill choice when asked. It cannot change skill steps, diagnose, assess safety, invent therapeutic advice, or control support. Primary flow must work without it.

Annotate timing: See 12 + Feel 12 + check-in 5 + Hear 12 + Smell 10 + Taste 9 + completion 5 = 65 seconds; target 60–75 and standard unpaused flow under 90. Setup, user pauses, and support access are measured separately. Never force completion or auto-advance when time expires.

Annotate proposed data only: sessions, completed skill usage/recent skill, optional check-in response, and fictional conversation messages only if model interaction is used. No schema implementation; consent, retention, deletion, and message-storage need are unresolved.

Annotate tradeoffs: agency/cognitive fatigue; frictionless safety/visual presence; simplicity/tracking depth; personalization/control; optional input/emotional effort; model assistance/deterministic steps; calm visuals/persistent controls.

Keep Fifer independent from Expedia Lite. Conceptual reuse only: Vue/FastAPI/SQLite separation, optional conversation persistence, documentation/verification. No copied files or travel functionality.

## Evidence after actual tool use

Record actual tool/model shown, prompt revision, file/prototype URL, screen names/IDs, review date, human edits, and verified exports. Do not invent versions, links, timing, test results, or clinical evidence. Update the report, design document, and AI disclosure only after evidence exists.
