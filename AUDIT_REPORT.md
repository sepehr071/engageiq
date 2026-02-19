# EngageIQ Voice Agent — Comprehensive Audit

## Context

Full audit of the EngageIQ LiveKit voice agent for Ayand AI's EuroShop 2026 booth. Examined from three dimensions: (1) natural conversation flow, (2) multilingual implementation, (3) LiveKit SDK correctness. Findings verified against LiveKit Agents SDK 1.4.x docs and changelog.

**Frontend confirmed**: livekit-client JS (web) using `registerTextStreamHandler` (new text streams API).

---

## CRITICAL (2 findings)

### C1. Language switcher uses legacy `data_received` — won't receive text streams
**File**: `utils/language_switcher.py:40-41`
**Problem**: The language switcher listens via `@self._room.on("data_received")`, which is the legacy data packets API. Your frontend uses `registerTextStreamHandler` (text streams). If the frontend sends language changes via `sendText(topic="language")`, the agent will **never receive them** — the `data_received` event only fires for `publishData`, not `sendText`.
**Impact**: Mid-conversation language switching silently broken.
**Fix**: Either (a) switch to `room.register_text_stream_handler("language", handler)` on the agent side, or (b) ensure the frontend sends language changes via the legacy `publishData` API. Option (a) is recommended. The backup `participant_attributes_changed` listener in `agent.py:160` still works.

### C2. `session.current_agent` raises RuntimeError, not returns None
**File**: `agent.py:131-132`
**Problem**: `on_shutdown` accesses `session.current_agent` with a null check, but the SDK property **raises RuntimeError** if the session isn't running — it never returns `None`. The `try/except Exception` catches it, but the entire shutdown callback aborts, losing conversation data and the webhook.
**Fix**: Use `session.history.items` instead (always available), or wrap `current_agent` access in its own `try/except RuntimeError`.

---

## HIGH (8 findings)

### H1. AVATAR_NAME and BOOTH_LOCATION placeholders unfilled
**File**: `prompt/main_agent.py:75-76`
**Problem**: `AVATAR_NAME = "[AVATAR_NAME_TBD]"` and `BOOTH_LOCATION = "[BOOTH TBD]"`. The agent will literally say "I'm [AVATAR_NAME_TBD]" to visitors.
**Fix**: Fill before launch. Consider making them env vars.

### H2. Webhook API key hardcoded as default in source
**File**: `config/settings.py:80`
**Problem**: `WEBHOOK_API_KEY = os.getenv("WEBHOOK_API_KEY", "ayand-secret-key-3dcSDSfgcGsasdcvg3235fvsaacv1")` — committed to git.
**Fix**: Remove default value. Require env var. Log warning if missing.

### H3. Tool return strings cause "instruction stacking"
**Files**: `agents/main_agent.py`, `agents/lead_capture_agents.py`
**Problem**: Every tool returns English instruction strings that accumulate in chat context. By tool #4-5, the LLM sees multiple paragraphs of stale instructions from prior tool calls. The convention documented in CLAUDE.md is "tools return `None` for silent behavior", but `detect_visitor_role`, `save_conversation_summary`, and `collect_challenge` all return instruction strings instead.
**Impact**: Increased language drift (English tool returns pull the model toward English), context pollution, reduced instruction-following reliability.
**Fix**: Make `detect_visitor_role`, `save_conversation_summary`, and `collect_challenge` return `None`. Keep instruction returns only for tools that genuinely need to alter behavior (`check_intent_and_proceed`, `present_engageiq`, `connect_to_lead_capture`).

### H4. Tool chaining via return strings is unreliable
**File**: `agents/main_agent.py:245`
**Problem**: `collect_challenge` returns "Now call check_intent_and_proceed" — relying on the Realtime model to read a tool return and immediately call another tool. At temperature 0.6, the model may speak first and forget, or never call it.
**Fix**: Either merge `collect_challenge` + `check_intent_and_proceed` into one tool, or make `collect_challenge` return `None` and trust the system prompt flow guide.

### H5. Vague challenge keywords only cover English and German
**File**: `agents/main_agent.py:25-28`
**Problem**: `_VAGUE_CHALLENGE` list only has English/German phrases. For 8 other languages, vague answers ("je ne sais pas", "no estoy seguro", "bilmiyorum") score +3 instead of +1, inflating intent scores and prematurely pushing non-English/German visitors toward lead capture.
**Fix**: Add vague-challenge phrases for all 10 languages.

### H6. Missing language validation at session start
**File**: `agent.py:99`
**Problem**: Language read from `participant.attributes` without validation. Unsupported codes (e.g., "zh") pass through, causing: generic English directive (weak), German fallback buttons, German lang_hint in tool returns.
**Fix**: Validate against `SUPPORTED_LANGUAGES` immediately after reading, fallback to `DEFAULT_LANGUAGE`.

### H7. `participant_attributes_changed` handler lacks validation
**File**: `agent.py:160-165`
**Problem**: The backup language listener calls `_handle_language_change(new_lang)` without checking `SUPPORTED_LANGUAGES`. The data channel path validates (line 56 of `language_switcher.py`), but this path doesn't.
**Fix**: Add validation before the `create_task` call, or move validation into `_handle_language_change` itself.

### H8. Accessing private `_chat_ctx` throughout codebase
**Files**: `agent.py:132`, `agents/main_agent.py:342`, `agents/lead_capture_agents.py:100,157,191,249`
**Problem**: Code accesses `self._chat_ctx.items` (private) instead of `self.chat_ctx.items` (public property) or `session.history.items` (documented API). Will break on SDK updates.
**Fix**: Replace all `_chat_ctx` references with `self.chat_ctx` or `session.history`.

---

## MEDIUM (18 findings)

### M1. `EngageIQAssistant.__init__` crashes if `userdata` is None
**File**: `agents/main_agent.py:77-84`
`self.userdata` only set if `userdata` is truthy, but `self.userdata.language` accessed unconditionally. Same pattern in `agents/base.py:67-68`.
**Fix**: `self.userdata = userdata or UserData()`.

### M2. Main agent `restart_session` doesn't save history or send webhook
**File**: `agents/main_agent.py:144-155`
Compare with `LeadCaptureAgent.restart_session` (lines 233-268) which does save. Restart during main agent phase = lost data.

### M3. `restart_session` drops `campaign_source` and `session_id`
**Files**: `agents/main_agent.py:149-155`, `agents/lead_capture_agents.py:261-268`
Fresh `UserData` only preserves `language`. Attribution and session tracking broken for restarted sessions.

### M4. `_send_product_to_frontend` uses fire-and-forget `asyncio.create_task`
**File**: `agents/main_agent.py:214-222`
The `try/except` only catches sync exceptions from `create_task()`, not the async `send_text` failure. Product images silently fail.

### M5. Intent score max inconsistency
`settings.py` says `INTENT_SCORE_MAX = 10` with thresholds at 4/5/7. Actual max is 5. `check_intent_and_proceed` hardcodes `>= 3`. Webhook computes `potentialScore = intent_score * 20` (works for max=5 but not max=10).

### M6. `confirm_consent(false)` clears partial data before webhook
**File**: `agents/lead_capture_agents.py:181-198`
Partial data cleared on lines 182-187, then webhook sent on lines 190-194. Webhook gets empty contact info. Status is correct (`declined`) but data is lost.

### M7. `connect_to_lead_capture(false)` sets `_history_saved = True` prematurely
**File**: `agents/main_agent.py:349`
History saved + webhook sent mid-conversation. If visitor keeps talking (or changes mind), final state not captured. Shutdown handler skips.

### M8. `_history_saved` flag set in 4+ places — centralization needed
Multiple tools set this flag and do their own history save + webhook. Race conditions possible. Shutdown handler should be the single save point.

### M9. Blocking SMTP in async context
**File**: `utils/smtp.py`
`smtplib.SMTP` with `time.sleep` blocks event loop for up to 90s. Agent unresponsive during email send.
**Fix**: Use `asyncio.get_event_loop().run_in_executor(None, ...)` or `aiosmtplib`.

### M10. Greeting language mechanism inconsistency
`build_greeting()` uses weak English instruction ("Respond in German"), while system prompt has strong native directive. Three separate language instruction mechanisms: system directive, `lang_hint()`, inline `on_enter` construction.

### M11. `LeadCaptureAgent.on_enter` builds own lang instruction
**File**: `agents/lead_capture_agents.py:35-38`
Third language mechanism (inline) alongside system directive and `lang_hint()`. Slightly different format from both.

### M12. Language switching race condition — no mutex
**File**: `utils/language_switcher.py`
Both data channel and attribute change listeners can trigger `_handle_language_change` concurrently. No `asyncio.Lock`. Rapid language changes could interleave.

### M13. Chat context carries old language across handoff
**File**: `agents/main_agent.py:331-338`
Handoff passes `chat_ctx=self.chat_ctx` with conversation history in old language. New directive may not fully override.

### M14. Handoff uses `self.chat_ctx` instead of `self.session.chat_ctx`
Official LiveKit docs show `chat_ctx=self.session.chat_ctx` for context preservation. EngageIQ uses `self.chat_ctx`.

### M15. No `room_options` on `session.start()` — duplicate transcriptions
**File**: `agent.py:171-178`
Default `RoomOptions` enables built-in `lk.transcription` output AND `lk.chat` text input. Agent's `transcription_node` sends text on custom `"message"` topic. Frontend receives agent speech twice. Also, `lk.chat` input could cause unexpected interruptions.

### M16. "2-3 exchanges before presenting" vs "natural product advocacy"
**File**: `prompt/main_agent.py`
Contradictory: "always connect back to EngageIQ" vs "wait 2-3 exchanges before presenting." Distinction between mentioning and formal presentation not explicit.

### M17. Early "tell me about EngageIQ" blocks flow
If visitor asks about EngageIQ before sharing role, model explains verbally but doesn't call `present_engageiq`. `engageiq_presented` stays `False`, blocking `connect_to_lead_capture`.

### M18. `EngageIQAssistant` doesn't inherit `BaseAgent` — duplicated code
`transcription_node` duplicated. Main agent doesn't get `_safe_reply` with retry/fallback. Greeting uses raw `generate_reply` with basic try/except.

---

## LOW (11 findings)

### L1. Duplicate import in `lead_capture_agents.py` (lines 11 and 19)
### L2. Silence timeout defined but never used (`SILENCE_TIMEOUT_SECONDS = 120`)
### L3. Dead code: `on_enter` else branch calls `super().on_enter()` (no-op)
### L4. Dead code: `build_prompt_with_language` has unreachable `if not directive` check
### L5. No "visitor changes mind after declining" path
### L6. No garbled-input / "I didn't understand" fallback for noisy trade show
### L7. No interruption handling guidance in prompt
### L8. Temperature 0.6 trade-off (natural speech vs reliable tool calling)
### L9. Language names missing diacritics: "Francais", "Espanol", "Portugues", "Turkce"
### L10. Portuguese variant ambiguity (pt-BR vs pt-PT mixed register)
### L11. Arabic RTL not addressed in data payloads

---

## Priority Matrix

| Priority | Findings | Action |
|----------|----------|--------|
| **Before Launch** | C1, C2, H1, H2, H5, H6, H7 | Must fix |
| **High Impact** | H3, H4, H8, M1, M2, M3, M6, M9, M15 | Should fix |
| **Quality** | M4, M5, M7-M8, M10-M14, M16-M18 | Improve |
| **Polish** | L1-L11 | Nice to have |

---

## Architecture Recommendations

### 1. Centralize history/webhook saves in `on_shutdown`
Remove save + webhook logic from individual tools. Tools should only set `userdata` flags. `on_shutdown` handles all persistence. Eliminates: M7, M8, partially M6.

### 2. Make most tools silent (return `None`)
`detect_visitor_role`, `collect_challenge`, `save_conversation_summary` should return `None`. The system prompt already guides the flow. Eliminates: H3, reduces H4, reduces English language drift (M10).

### 3. Unify language instruction mechanism
Single function `lang_instruction(language)` used everywhere (greeting, on_enter, tool returns). Eliminates: M10, M11.

### 4. Migrate language switcher to text streams API
Replace `data_received` listener with `room.register_text_stream_handler("language", handler)`. Fixes C1.

### 5. Add `room_options` to `session.start()`
Disable built-in `lk.transcription` and `lk.chat` text input since custom topics are used. Fixes M15.

---

## Verification

To verify fixes end-to-end:
1. Run `conda activate engage && python agent.py dev`
2. Connect via LiveKit Agents Playground or the web frontend
3. Test happy path: greet -> chat -> detect role -> present -> challenge -> intent check -> lead capture -> consent
4. Test language switch mid-conversation (frontend dropdown)
5. Test decline path: say "no" to contact sharing
6. Test restart: click "New Conversation" after lead capture
7. Test edge cases: ask "what is EngageIQ" before sharing role, provide email during main conversation, give vague answer in non-English language
8. Check webhook payloads for correct status, contact info, and potentialScore
9. Check logs for errors in `docs/app_*.log`
