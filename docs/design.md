# Design plan — Part 3.1

Status: planning only; no mockup has been created.

## Tool and evidence

Use Figma or Figma Make. Record the actual design link, revision/date, and reviewed exports in `mockups/` when available.

## Proposed interaction

- Entry screen: explain coursework boundaries and fictional use.
- Guided screens: show the prescribed 5-4-3-2-1 sequence using application-controlled steps; confirm source and wording during research.
- Keep user control, Stop/Leave, Pause, and Emergency Support available throughout the experience.
- Define and review pause/resume, leave, and completion behavior before implementation.
- Emergency Support must remain accessible independently of any model or classifier. No real crisis phone number or emergency-contact integration is included in this stage.

## Review checklist

- Review readable text, contrast, keyboard access, focus order, and understandable control labels.
- Use fictional content and avoid diagnostic, effectiveness, or human-monitoring claims.
- Record actual mockup reviews and unresolved decisions; do not claim unperformed accessibility or usability tests.

## Planned implementation

Vue with JavaScript → FastAPI with Python → SQLite on localhost. This document does not authorize implementation or dependencies.
