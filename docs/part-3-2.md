# Fifer — Part 3.2 implementation checkpoint

This is the historical first UI/environment checkpoint. The subsequent approved SQLite, retention, history, and deletion implementation is recorded in [the storage checkpoint](part-3-2-storage.md). Its current evidence supersedes the no-persistence statements below.

Date: 2026-10-22. Local coursework prototype; fictional scenarios only. This record describes actual work, not clinical effectiveness or a completed Part 3.3 evaluation.

## Scope and repository

Implemented the user-authorized smallest Vue/JavaScript + FastAPI/Python slice. Application content controls start choice → See 5 → Feel 4 → optional check-in → Hear 3 → Smell 2 → Taste 1 → completion. Each category has neutral optional selectable examples and Continue without selecting; there is no quota or score. Feel does not require touching, Smell does not require finding anything, and Taste does not require consumption. No disclosure is requested.

Pause retains the current screen/answers and requires explicit Resume. Stop/Leave exits immediately, clears current answers, and does not mark completion. Only explicit Finish creates a dismissible recent-skill suggestion in this tab. Help me choose is fixed explanatory text, not model output. One skill is currently supported.

Emergency Support renders static frontend content: “Please contact 911 for emergency support.” This follows the user's supplied wording direction. It is text only, with no phone link, calling, messaging, model/classifier, or backend prerequisite. Instructor approval is not verified. Coursework-prototype notices remain visible. Returning from support to an unfinished activity leaves it paused.

FastAPI exposes only `GET /api/health`. The request sends no answers. No SQLite file/tables, stored sessions/messages, or model calls were created. Responses/check-in and recent completion exist only in memory; reload clears them. Conversation retention/deletion and the exact model contribution remain future approval decisions. SQLite remains planned, rather than implemented in this slice.

Verified repository: `master`, origin `https://github.com/nikhilrajk21/Fifer.git`, HEAD `003245f47958474e300920bb4b0127d275bedff4`, Part 3.1 submission `615ac73aaa933f8c3ce0004079f0179a133b35b1`. No commit/push occurred. Part 3.1 report/research/design and mockup PNGs were preserved. Earlier environment-only rules were updated to reflect the latest authorization.

## Dependency CHECK → TAKE ACTION → VERIFY

The user approved project-local pip 26.2 remediation after the pip 25.0.1 advisory pause. The approved seven direct versions stayed unchanged:

| Frontend | Backend |
| --- | --- |
| vue 3.5.44 | fastapi 0.156.0 |
| vite 8.3.4 | uvicorn 0.54.0 |
| @vitejs/plugin-vue 6.0.10 | pydantic 2.14.1 |
| | httpx 0.28.1 |

Runtime: CPython 3.12.14 AMD64, SQLite library 3.53.1, Node 24.20.0, npm 11.19.0. The base Python is Codex-managed; only `backend/.venv` was changed, including its pip upgrade. No global package was installed. README explains recreation with a normal compatible CPython installation.

Before installation, registry artifact inspection checked 17 Python wheel digests and 35 applicable Windows npm archives against their recorded hashes. Python's native Pydantic Core wheel matched CPython 3.12/Windows x64; Rolldown and Lightning CSS bindings matched Windows x64. All npm engine constraints checked against the installed Node version. The cross-platform npm lock contains 60 dependency entries; inapplicable platform binaries were not installed.

PyPI advisory metadata listed no advisories for the inspected resolved packages or pip 26.2; the npm bulk advisory response was empty for the lock graph at inspection. Registry advisory data is a point-in-time signal, not proof of absence of vulnerabilities. Sources queried were [PyPI](https://pypi.org/) and the [npm registry](https://registry.npmjs.org/).

Package-content inspection found no applicable preinstall/install/postinstall hooks or implicit binding.gyp install. The optional macOS-only fsevents 2.3.3 install hook was inapplicable and not executed. An initial inspector also counted csstype's publishing-only prepublish hook; it was corrected after checking npm's dependency-rebuild source and [npm lifecycle documentation](https://docs.npmjs.com/cli/v11/using-npm/scripts/). npm installation used `--ignore-scripts`; no dependency install script was run. No additional direct package or silent upgrade was introduced.

Install commands below use repository-relative paths; the npm invocation used the equivalent absolute project-local paths:

```powershell
.\backend\.venv\Scripts\python.exe -m pip --isolated --disable-pip-version-check install --only-binary=:all: --cache-dir .cache/pip --index-url https://pypi.org/simple -r backend/requirements.txt -c .cache/dependency-check/constraints.txt --report backend/.venv/installed-report.json
npm ci --prefix frontend --ignore-scripts --cache .cache/npm --registry https://registry.npmjs.org/ --no-audit --no-fund
```

Pip 26.2 was installed in that venv under the separate explicit approval. `backend/requirements.lock.txt` was then generated from the 17 actually installed application packages, not a proposed resolution. Ignored local inspection/cache/report files are not repository deliverables. The lockfile does not contain wheel hashes; inspect/advisory-check again before a later install.

## Checks and results

| Check | Actual result |
| --- | --- |
| Project interpreter imports | FastAPI 0.156.0, Uvicorn 0.54.0, Pydantic 2.14.1, HTTPX 0.28.1, sqlite3 imported successfully |
| `backend/.venv/Scripts/python.exe -m pip check` | No broken requirements |
| `npm ls --prefix frontend --depth=0` | All three frontend direct pins present at approved versions |
| `npm --prefix frontend test` | 9 tests passed, 0 failed |
| Backend `tests/test_api.py` using project Python | 2 tests passed, 0 failed |
| `npm --prefix frontend run build` | Passed; final Vite 8.3.4 build transformed 15 modules in 223 ms |
| `git diff --check` | Passed; Git emitted Windows LF/CRLF conversion notices |

Tests use Node's built-in runner and Python unittest with the already approved HTTPX ASGI transport. No test framework was added. API tests verify stateless health flags and missing model/emergency/session action endpoints. The first synchronous TestClient attempt was replaced after sandbox/runtime issues. Async API checks also required an approved run outside the Windows sandbox; direct ASGI transport then passed. The successful test invocation from `backend/` was:

```powershell
.\.venv\Scripts\python.exe -B -c 'import faulthandler,runpy; faulthandler.dump_traceback_later(8,exit=True); runpy.run_path("tests/test_api.py",run_name="__main__")'
```

The Node tests exercise the fixed sequence/counts, advancing with no selection, selectable toggles, skippable after-Feel check-in, Pause blocking advancement, explicit Resume, support access across states, independent pause/support counters, immediate Stop/answer clearing, no forced completion after 90 seconds, and explicit completed-skill suggestions/dismissal.

## Actual browser evidence

Local in-app browser at `http://127.0.0.1:5173/`. Screenshots are browser captures, not Figma exports or generated mockups. All interactions used fictional examples. Earlier full-page captures clipped the right edge; the final files were recaptured with the complete visible viewport. The narrow viewport request was 390 × 844, but the browser measured 340 CSS pixels; that measured width is the evidence reported here. Temporary viewport overrides were reset.

| State / interaction | Evidence |
| --- | --- |
| Start choices and persistent support | [01-start.jpg](verification/part-3-2/01-start.jpg) |
| See: optional answers, both continuation controls, Pause/Stop | [02-see.jpg](verification/part-3-2/02-see.jpg) |
| Keyboard Enter opened Pause; visible focus on Resume | [03-paused.jpg](verification/part-3-2/03-paused.jpg) |
| After Feel: one optional check-in, “A little better,” Skip | [04-checkin.jpg](verification/part-3-2/04-checkin.jpg) |
| Hear → Smell → Taste → completion without sensory selections | [05-completion.jpg](verification/part-3-2/05-completion.jpg) |
| Stop/Leave from Pause exited without confirmation | [06-stopped.jpg](verification/part-3-2/06-stopped.jpg) |
| FastAPI stopped; nonblocking connection failure | [07-backend-unavailable.jpg](verification/part-3-2/07-backend-unavailable.jpg) |
| Static support opened with FastAPI stopped | [08-support-backend-offline.jpg](verification/part-3-2/08-support-backend-offline.jpg) |
| Narrow support layout | [09-support-narrow.jpg](verification/part-3-2/09-support-narrow.jpg) |
| Narrow See layout with persistent controls | [10-see-narrow.jpg](verification/part-3-2/10-see-narrow.jpg) |

Additional observed results: Pause → Support → Return stayed paused; explicit Resume returned to the same category. Tab focus cycled within the paused dialog. Headings received focus on step changes. Emergency Support was visibly reachable on each category, check-in, completion, paused, stopped, and connection-error screens. Explicit Finish produced a recent-skill card; Ignore removed it without preventing a new activity. No sensory choice was required to reach completion. Retry cleared the connection error after FastAPI restarted.

For narrow See and support samples, document width and client width were both 340 CSS pixels; support dialog width was approximately 304.6 CSS pixels. No horizontal overflow was measured in those samples. This is a targeted check, not a full accessibility or device review.

## Timing, limitations, and pending decisions

Design target: approximately 60–75 active seconds, remaining under 90 where comfortable. No measured user timing study was performed, and this target is not claimed as achieved. User pacing takes priority: no automatic advance, forced completion, countdown, or timeout gate. State transitions accumulate setup, active, paused, and support milliseconds separately; pause/support time is excluded from active exercise duration. Counters are in memory only and settle on actions. They are not clinical measures.

This slice has no model contribution. Future output must not control steps, safety access, safety assessment, diagnosis, or advice. Precise role/provider/fallback still requires approval. Retention/deletion/consent must be decided before SQLite sessions/conversations or persistent recent-skill history. Instructor confirmation of crisis wording and jurisdiction remains pending. Detailed Figma/Figma Make screens are not claimed to exist.

Unverified: participant usability/clinical outcomes, 60–75-second timing, full WCAG/screen-reader review, cross-browser/device coverage, a fresh-machine installation, and any later persistence/model integration. The frontend dev server must remain available for a fresh page load; backend-independent operation is not a service-worker/offline deployment claim. No model-failure runtime test is possible because no model integration exists. A performance-API request-count probe was unavailable; support independence is evidenced by static source structure and the backend-off browser walkthrough, not a fabricated network trace.

## Changed file inventory

Five tracked documents changed:

- `AGENTS.md`
- `README.md`
- `AI-USE.md`
- `docs/safety.md`
- `handoffs/current.md`

New documentation/evidence:

- `docs/part-3-2.md`
- `docs/verification/part-3-2/01-start.jpg`
- `docs/verification/part-3-2/02-see.jpg`
- `docs/verification/part-3-2/03-paused.jpg`
- `docs/verification/part-3-2/04-checkin.jpg`
- `docs/verification/part-3-2/05-completion.jpg`
- `docs/verification/part-3-2/06-stopped.jpg`
- `docs/verification/part-3-2/07-backend-unavailable.jpg`
- `docs/verification/part-3-2/08-support-backend-offline.jpg`
- `docs/verification/part-3-2/09-support-narrow.jpg`
- `docs/verification/part-3-2/10-see-narrow.jpg`

Backend:

- `backend/requirements.txt` (prepared during the earlier setup checkpoint)
- `backend/requirements.lock.txt`
- `backend/main.py`
- `backend/tests/test_api.py`

Frontend:

- `frontend/package.json` (existing approved pins; runnable scripts added)
- `frontend/package-lock.json` (prepared during the earlier setup checkpoint)
- `frontend/index.html`
- `frontend/vite.config.js`
- `frontend/src/main.js`
- `frontend/src/App.vue`
- `frontend/src/style.css`
- `frontend/src/grounding.js`
- `frontend/src/grounding.test.js`
- `frontend/src/api.js`
- `frontend/src/safety-content.js`
- `frontend/src/components/EmergencySupport.vue`

Ignored local artifacts: `backend/.venv/`, `frontend/node_modules/`, `frontend/dist/`, caches, Python bytecode, and temporary inspection data. No credentials/environment files or SQLite runtime files are included. Nothing is staged; no commit/push was performed. Development servers were restored and the browser left on start choices at handoff.
