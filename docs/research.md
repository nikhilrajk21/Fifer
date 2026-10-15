# Fifer — research foundation

Updated: 2026-10-15. The supplied Assignment 3 study summary/course material is the primary research source. All observations below are attributed to that supplied summary, not an independently conducted study.

## Overall design logic

Fifer supports a fictional student experiencing conflict, self-doubt, or an emotionally difficult day through a gentle, low-demand 5-4-3-2-1 sensory grounding activity. The design maximizes user agency while minimizing cognitive and emotional effort: one atomic step at a time, optional selections, persistent frictionless safety access, and a calm, low-stimulus presentation. It does not impose clinical or forced pathways, diagnose, or infer distress automatically.

## Research-to-design mapping

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

## Why 5-4-3-2-1 was selected

The brief selects sensory grounding as Fifer's primary skill. Its five categories fit D2's atomic presentation, D3's low-demand optional responses, and D1's reduced interface content. R1 informs concise pacing. R3/R4 preserve user control over starting, pausing, skipping optional input, and leaving. These findings motivate the interaction design; they do not establish therapeutic outcomes for this skill or prototype.

The application controls See 5 → Feel 4 → check-in → Hear 3 → Smell 2 → Taste 1 → completion. The optional check-in after Feel includes “A little better”. No model can alter this sequence.

## Three overall tradeoffs

1. **Agency versus cognitive fatigue:** choice and optional answers preserve autonomy but can add decision effort. Keep a clear Begin grounding action and a small set of optional choices.
2. **Frictionless safety versus visual presence:** persistent support enables immediate access but uses space and may cause accidental taps or anxiety. Keep a stable, readable label without flashing or alarm-like decoration.
3. **Simplicity versus depth of tracking:** atomic, low-demand steps limit overload and attention demands but restrict deep reflection and detailed history. Collect only justified prototype data.

## Additional implementation-design tradeoffs

Personalization versus user control: D5 suggests using recent completed activity, while R4 requires Ignore/Change and no forced recommendation. Optional input versus emotional effort: D3 motivates no typing requirement, but examples must remain few enough to avoid adding decision burden.

Model assistance versus deterministic skill steps: optional transitions or reflections can vary wording but add latency and unpredictable output. The application owns the skill, controls, and safety access; model failure uses fixed fallback copy. This boundary is a project safety constraint, not a claimed study result.

Calm design versus persistent safety controls: D6's quiet visuals must coexist with R2/D4's readable, always-visible support. Contrast and control prominence still need actual mockup review.

## Citation note

Primary source: the supplied Assignment 3 study summary/course material, including the R1–R4/D1–D6 mapping pasted by the project owner on 2026-10-15. This is the course-source attribution; no external citation, publication title, author, or URL has been invented. The findings inform design reasoning but do not prove clinical effectiveness.

No new research participants, clinical evaluations, or test results are claimed. The exact mapping is incorporated. The student has manually added the GPT-generated proposed-flow diagram; it was statically inspected without modification. It is design evidence, not a measured study outcome. Remaining work concerns the detailed Figma/Figma Make mockup, instructor-approved support wording, rubric confirmation, and future verification.
