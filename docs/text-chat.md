# Fifer bounded text assistant — offline adapter checkpoint

Date: 2026-10-26. This is a fictional coursework prototype. No real provider call is authorized or performed. The REST adapter is wired through FastAPI and the existing Chat screen, but normal startup remains the labelled local mock and every provider-path test uses HTTPX MockTransport. Gemini Live voice has separate mock controls/lifecycle in Chat; its real upstream connector remains unimplemented. See [current acceptance](verification/part-3-2-acceptance.md) and [report](../report.md). Actual model contribution, generated behavior and account access remain unverified; this checkpoint does not demonstrate a live conversation.

## Latest adapter increment

The latest request authorized implementing the missing FastAPI-mediated Gemini adapter while preserving mock-only verification and separate approval for real calls. `backend/gemini_text.py` uses the already approved HTTPX package; no SDK or dependency change was needed. It plugs into the existing `create_app(chat_provider=...)` test seam, so the same quotas, actual-context sharing, output validation, opt-in saving, Stop and Clear protections apply. Production construction still chooses `MockTextProvider`.

The adapter has a server-only authorization guard. Normal application construction selects the mock. A future non-mocked process must set both `FIFER_TEXT_PROVIDER=gemini` and `FIFER_TEXT_LIVE_AUTHORIZED=true`; missing, partial or contradictory settings fail closed during startup. The browser cannot set these values, and a `.env` key, user request field or browser action alone cannot enable a call. HTTPX `MockTransport` is permitted for offline tests; every test supplies fictional fixtures. The gates were not enabled here.

After authorization only, the lazy configuration helper can read the existing `GEMINI_API_KEY` environment variable or `backend/.env`, with environment presence taking precedence (including an intentionally empty value). It never writes configuration or accepts a second key name. The real environment file was not read or changed during this increment. The adapter sends the key only in a header, never a URL, response, history record or log. It uses a fixed HTTPS endpoint, no redirects, no automatic retries, and both an overall and HTTPX 15-second timeout.

The request carries only the fictional question, retrieved curated source IDs/titles/text and explicitly shared allowlisted metadata. System instructions keep user data separate from rules; there are no tool/search/file capabilities. `maxOutputTokens` is fixed at 300 and one candidate is requested. Structured JSON must identify one supplied paragraph and source; the backend preserves its existing stricter verbatim-output contract. It rejects extra output fields, mismatched text/source, tool parts, incomplete/blocked output, reported token overrun and oversized responses. A prompt or schema alone is not treated as enforcement. Failure uses the existing neutral fallback without exposing upstream bodies or exceptions. These REST request/response fields were checked against Google's [generateContent reference](https://ai.google.dev/api/generate-content); key placement follows its [API-key guidance](https://ai.google.dev/gemini-api/docs/api-key).

Google's current [deprecation/access notice](https://ai.google.dev/gemini-api/docs/deprecations) says 2.5 models are restricted to prior active users, with no shutdown date announced for `gemini-2.5-flash`. This account's eligibility has not been tested. The approved model ID was retained; no replacement was silently selected. API documentation review is not a provider inference call or proof of account access.

Latest observed checks: **39 backend tests, 26 frontend tests and the Vite build passed**, with zero test failures. Eleven new adapter tests use temporary databases and HTTPX mock transport through the real FastAPI route. They cover missing key/no HTTP request, valid packet/success, invalid/truncated/tool/oversized/token-overrun output, provider errors/429 without retries, timeout, late transport result after Stop with no save, OFF/ON/OFF saving, forbidden context/model/limit changes, default live refusal before key loading, and a configuration loader using only a temporary `.env` fixture. Existing frontend tests cover loading request completion, finite deadline and ignored late answers after Stop/Support/navigation. No new browser interaction was required for this backend-only adapter; the preceding browser evidence below covers the unchanged UI.

Unverified: real Gemini authentication/account eligibility, actual generated responses, latency, token accounting, billing controls and provider-side behavior. The live authorization guard remains closed; future real use is not approved by the existence of this adapter or key file. No real key was read, no provider call made, no package installed, and nothing committed/pushed.

## Approved scope and limits

The optional Chat view handles fictional, non-emergency questions about Fifer's existing skill, app usage, and safety boundaries. It is available from start choices or after explicit Finish, outside the active grounding exercise. No diagnosis, treatment advice, therapist/monitoring claims, invented profile/history, or model-controlled skill/safety paths are allowed.

The approved text target is Google Gemini `gemini-2.5-flash`, maximum 300 output tokens, 5 attempts per chat session, 20 per anonymous browser per UTC day, 15-second timeout, and no automatic retries. Normal runtime uses only a local deterministic mock. The HTTP adapter/key loader and two process-only activation gates are described above; the frontend merely renders the mode reported by FastAPI. Real model availability for this account, token counts, billing and generated responses are **not verified**. The mock packet carries the target/model allowance but returns only one curated paragraph, additionally capped at 300 characters. This is not a claim that real Gemini inference has been tested.

The backend atomically reserves an attempt before mock generation, counts failures/out-of-scope requests, and rejects duplicate request IDs without another attempt. It independently checks both quotas; client state cannot raise the configured limits. Chat session IDs survive page reload via sessionStorage. An explicit New chat starts a new five-attempt session but keeps the day's browser count. Browser identity is a random localStorage UUID; the backend stores its SHA-256 hash, not the raw ID. There is no verified account/person boundary: clearing browser data or supplying another identity can evade this prototype's effective per-browser limit. Do not present this as abuse-proof authentication or a per-person quota.

These controls do not guarantee a dollar spending cap. Before any real call, separately approve provider use and review the actual Google project's billing, quota, and available spending controls. Do not assume an alert or application token/request setting guarantees a hard currency cap.

## Curated retrieval and context consent

`backend/chat_content.py` is the full reviewed collection authored for this increment. Its five paragraphs are derived from existing app behavior/rules:

| Source ID | Content basis |
| --- | --- |
| skill | `frontend/src/grounding.js`: one skill, fixed counts/order, optional input and explicit Finish |
| usage | Current start/skill UI and `docs/design.md`: optional observations, no sensing or compulsory physical action |
| controls | `frontend/src/App.vue` and storage design: Pause/Resume, Stop/Leave, saved paused resume and independent Support |
| privacy | Existing approved opt-in, retention/Delete/Clear rules plus this separately approved sharing control |
| safety | `AGENTS.md`, `docs/safety.md`, and the unchanged user-approved static 911 sentence |

Local keyword/topic retrieval chooses one source, with specific safety/privacy/control topics ahead of generic app-help words. Citations identify that actual paragraph. Out-of-scope input gets fixed scope copy, without a provider attempt or message-content save (its reserved quota attempt still counts). The deterministic mock returns the paragraph verbatim; output validation rejects anything outside the retrieved text. Retrieval never accesses arbitrary files, URLs, private records, sensory drafts or chat history. Input is not interpreted as instructions to read files or change the app. This is bounded lexical retrieval plus a mock interface, not a tested generative Gemini chatbot.

Sharing starts OFF each time Chat mounts/reloads. An explicit checkbox shows a preview and permits only backend-read local completed-session count, latest completed skill and its optional check-in. No profile exists. Client-supplied context fields are rejected. Stopped/unfinished sessions do not produce completed-history context. Sharing consent does not enable saving; saving opt-in does not authorize sharing. Current or past sensory narratives, audio, transcripts and previous chat messages are never supplied to the mock.

## Persistence and deletion

Normal project-local database: `backend/data/fifer.sqlite3`, ignored by Git. The existing schema is extended with repeatable additive tables; startup never drops or clears local history.

| Table | Retained data and lifetime |
| --- | --- |
| chat_sessions | UUID, anonymous browser hash, created/end UTC times, active/stopped status, attempt count; until Delete/Clear |
| chat_requests | Request UUID and chat-session link, no prompt text; until linked chat Delete/Clear |
| chat_messages | Session link, role, eligible fictional question/reply text and UTC timestamp; only if existing message opt-in is ON both before and after the request; until Delete/Clear |
| chat_daily_usage | Browser hash, UTC date, count; survives history Delete/Clear through that UTC day; older rows removed on a later day's request |

Existing session/conversation/settings retention is unchanged. Message saving defaults OFF for new databases and after Clear; an existing ON preference is preserved. Opt-out stops future saves while preserving prior opted-in messages. History reviews/deletes chats and their linked messages. Clear deletes grounding and chat session/message/request history, resets saving OFF and invalidates old-generation writes; it retains the schema/generation marker and daily quota counters as disclosed in the UI. Operational daily counters are not conversation history, and retaining them prevents Clear from resetting today's quota. No sensory drafts, audio, transcripts, credentials or profile records are stored by the Chat UI. No external-backup erasure is promised.

Stop/navigation/Support cancel the tab's request and ignore late replies. The server checks chat status and history generation before saving a response. Saving failure returns an explicit unconfirmed-save result; it never silently claims success or retries. A request accepted before cancellation may still consume quota. If a backend stop request fails, the tab reports the unconfirmed stop, and still hides late replies. Browser reload can lose unsaved content or leave an interrupted session active; quota/session metadata remains and saved content is reviewable. This is not a delivery guarantee across abrupt browser/network failure.

## Routes

- `GET /api/chat/config?browser_id=UUID`: mock mode, future target/limits, saving preference, epoch, current daily usage.
- `GET /api/chat/context`: allowlisted preview, requested only when sharing is selected.
- `POST /api/chat/sessions`: begin a separate Chat session; never fabricates a grounding completion.
- `POST /api/chat/sessions/{id}/messages`: validate fictional-only request, reserve quotas, retrieve, mock reply, conditionally save.
- `POST /api/chat/sessions/{id}/stop`: close the browser-bound chat so late replies cannot save.
- `GET /api/chat/sessions/{id}`: local history metadata and opted-in messages.
- `DELETE /api/chat/sessions/{id}?history_epoch=N`: cascade chat deletion; preserve today's daily quota.
- Existing `GET /api/history` includes chat metadata; existing Clear also removes chats.

`GET /api/health` intentionally still reports `model_enabled: false`: no real model is connected. The Chat configuration route separately reports `mode: mock` and `live_calls_enabled: false`.

All user SQL values are parameterized, with transactions and foreign-key cascades. Browser ID is a quota key, not authentication. This remains a local single-user coursework app; local history is not a protected multi-user account system.

## Verification

Existing test commands, with no dependency change:

```powershell
# repository root
npm --prefix frontend test
npm --prefix frontend run build
# backend directory
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

Backend tests use `TemporaryDirectory` databases and injected recording/delayed/failing mocks, never the normal history or a provider. They cover both quotas/restart/day rollover, wrong-browser/duplicate/extra fields, actual context with sharing OFF/ON, saving OFF/ON/OFF, review/Delete/Clear, stale writes after Clear, consent withdrawal while pending, late response after Stop, timeout/invalid output/no retry, out-of-scope retrieval, SQL literals, and failed message saves. Frontend tests cover anonymous identity persistence/reset, 15-second deadline, no retries, quota/backend errors and ignored late replies after cancellation, alongside existing grounding/privacy invariants.

Final observed results: **26 frontend tests and 28 backend tests passed**, with zero failures. The Vite build passed (23 modules). `git diff --check` passed. No dependency manifest/lockfile changed and no key file was read or changed.

Browser checks used a fresh ignored `.cache/verification/fifer-chat-browser-1793058318958.sqlite3`, never the normal database:

1. Chat opened separately from grounding, with mock/no-Gemini labels, message saving OFF and sharing unchecked. A Pause question returned the actual curated controls paragraph and source, marked Not saved.
2. Reload/reopen retained one used attempt and kept sharing OFF. Selecting sharing showed zero completed sessions and no invented skill/check-in in the empty test database; sharing was turned OFF again.
3. Four further explicit sends reached five session attempts. A sixth nonempty question remained disabled. New chat reset the session count to zero while daily use remained five. The backend tests independently exercised the daily 20-attempt rejection, concurrent reservations and application-instance restart persistence.
4. In the disposable database only, opting into saving retained one fictional question/reply pair with a source label. Opening history showed stopped Chat status after the acknowledgement fix. Opting out retained the two reviewable saved messages. Delete removed that chat; Clear removed all remaining history and kept opt-in OFF. Reopening Chat showed daily usage still six. A read-only query confirmed zero grounding/chat/session/request/message records and six daily quota attempts after Clear.
5. With the backend process stopped, sending produced an honest unconfirmed-request error without automatic retry. Keyboard Emergency Support still opened the unchanged static copy, and global Stop/Leave exited immediately. Tab-only test text was discarded before normal service restoration.
6. Both normal services and the frontend API proxy returned HTTP 200 after restoration. Read-only normal-database counts remained six grounding sessions, zero conversations/messages, and the existing opt-in ON. No normal chat rows/messages/usage were created. Schema versions 1 and 2 were present; additive initialization preserved existing data.

The browser screenshot of a labelled saved local-mock answer was captured outside the repository for this chat's review; it is not a generated model response or a Figma artifact. Real process restart with nonzero browser quota was not manually repeated; backend tests reopened the same database in a new application instance. Failure/timeout/late-output races were injected in automated tests, not induced with a real provider. Browser checks did not exercise 20 sends manually.

Pending: real Gemini calls/token/billing/output checks (separate approval required), Gemini Live voice, full screen-reader/device/cross-browser review, and adversarial multi-user/security evaluation. The fictional-only checkbox is a user attestation, not a reliable classifier of arbitrary free text; only fictional app questions belong here. Instructor approval/jurisdiction of existing safety copy remains unverified. No clinical effectiveness is claimed.

## Changed-file scope

The latest adapter increment adds `backend/gemini_text.py` and `backend/tests/test_gemini_text.py`; it updates the header/contract comment in `backend/chat.py` and the current rules/status in `AGENTS.md`, `README.md`, `AI-USE.md`, `handoffs/current.md`, and this document. It changes no frontend implementation, storage schema, dependency manifest/lockfile, key/environment file, skill order, timing rule, safety text or retention policy.

The preceding mock increment changed `AGENTS.md`, `README.md`, `AI-USE.md`, `handoffs/current.md`, `docs/safety.md`, `docs/text-chat.md`, `backend/main.py`, `backend/storage.py`, `backend/chat.py`, `backend/chat_content.py`, `backend/tests/test_chat.py`, `frontend/src/App.vue`, `frontend/src/api.js`, `frontend/src/chat.js`, `frontend/src/components/ChatPanel.vue`, `frontend/src/components/HistoryPanel.vue`, and `frontend/src/grounding.test.js`.

The preceding six-file grounding prompt/scene changes remain uncommitted and preserved, including their changes to App and grounding tests. No environment file, dependency manifest/lockfile, Part 3.1 report or design evidence was changed by this text increment. Runtime databases/build output stay ignored. Nothing is staged, committed or pushed.

Revised approaches: a retrieval review caught generic "how/Fifer" words outranking a specific Pause question; topic priority and a focused regression test now select controls/privacy/skill help correctly. Browser review caught history reading before Chat's stop acknowledgement; the history read now waits for that acknowledgement, without gating immediate Stop/Support. A browser test script initially searched an accessibility diff for unchanged input controls; it switched to full accessibility snapshots. No extra request was sent by those failed inspection attempts.
