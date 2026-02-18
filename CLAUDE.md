# EngageIQ Voice Agent

## What This Is

LiveKit voice agent for Ayand AI's EuroShop 2026 booth. Visitors scan a QR code, an avatar opens on their phone, the agent presents EngageIQ (Ayand AI's product), qualifies them as a lead, and captures their contact info.

**This agent IS the product** — visitors experience EngageIQ by talking to it. The agent has a **female persona** (she/her).

## Tech Stack

- **Runtime:** Python 3.9 (conda env `engage`)
- **Voice Framework:** LiveKit Agents SDK (`livekit-agents 1.4.1`)
- **Voice Model:** OpenAI Realtime API (`gpt-realtime-mini-2025-10-06`)
- **Model Temperature:** `0.7` (configured in `config/settings.py`)
- **No RAG, no search, no Flask** — all product knowledge is baked into prompts
- **Note:** Noise cancellation (BVC) requires LiveKit Cloud paid plan — currently disabled

## Agent Identity (Product Truth Alignment)

The agent embodies EngageIQ's core identity from `Product_Truth_Final.md`:

- **Product class:** Conversational Demand Interface
- **Philosophy:** "Signal, not automation" — the agent captures demand signals, not automates tasks
- **Core mechanism:** AI avatar engages visitors, guides intent clarification, records signals, outputs structured data
- **Value creation:** Converting unobserved visitor interactions into measurable intent and behavioral data
- **Live demo identity:** The agent knows it IS EngageIQ — the conversation the visitor is having IS the product in action. "You're using it right now" is the strongest proof point.

### About Ayand AI (Company Knowledge)

The agent knows Ayand AI in detail: Düsseldorf-based German AI startup (founded 2025) that develops multimodal conversational AI assistants for retail and consumer brands. Makes products "talk" to customers naturally through smart in-store displays and mobile assistants using voice, vision, and chat — 24/7, multilingual.

### Client Knowledge (Used as Social Proof)

The agent knows two real clients and uses their stories mid-conversation:

- **CORE Oldenburg** — coworking space, community hub, event venue, and street-food market hall in Oldenburg, Germany. Uses EngageIQ to capture demand from visitors exploring workspaces, events, and food market.
- **DFKI** — Germany's leading AI research institute (founded 1988), one of the world's largest independent AI research centers. Uses EngageIQ at exhibitions to make complex research accessible through conversation.

Client data is stored in `config/products.py` with `description`, `industry`, `use_case`, and `story_hook` fields. The agent drops ONE client story per conversation, matched to the visitor's context (community/hospitality → CORE; research/tech → DFKI).

### Boundaries (What the Agent Never Does)

- Never guarantees leads, bookings, or revenue — captures demand signals only
- Never says it replaces staff — it augments them with demand visibility
- Never discusses transactions, payments, or orders
- Never calls itself a chatbot, AI assistant, or virtual helper

### Chatbot Differentiation

When compared to a chatbot, the agent knows these distinctions:
- Chatbot: keyword matching → EngageIQ: AI-driven intent detection through conversation
- Chatbot: scripted decision trees → EngageIQ: natural conversation with structured outcomes
- Chatbot: contact info upfront → EngageIQ: contact only after consent + detected intent
- Chatbot: success = questions answered → EngageIQ: success = demand detected + intent score + attribution + transcript

### Pricing Behavior

The agent does NOT quote specific prices. When visitors ask about pricing, it redirects them to speak with the Ayand AI manager.

## Architecture

### Agent Flow (2 agents, single handoff)

```
EngageIQAssistant (greet → natural conversation → detect role → present EngageIQ → qualify → check intent → lead capture or goodbye)
  → LeadCaptureAgent (collect contact → ask consent → save/discard → goodbye → restart)
```

The main agent greets, has natural conversation, detects the visitor's role when it comes up naturally, presents EngageIQ personalized to their role, then asks one qualification question. After qualification, `check_intent_and_proceed` determines:
- **Score ≥3**: Offer lead capture
- **Score <3**: Try to re-engage visitor; if still disengaged, say goodbye

### Prompt Architecture

**English base prompt + native-language directive at TOP:**

```
[Native-language directive]     ← from prompt/language.py, prepended at TOP
[Identity]                      ← English base from prompt/main_agent.py
[About EngageIQ]
[Product Knowledge]
[How to Have This Conversation]
[Tools]
[Behavior Rules]
```

- **Base prompts** (`prompt/main_agent.py`, `prompt/workflow.py`) are always English-only
- **Language directives** (`prompt/language.py`) are written IN the target language (German in German, etc.) for maximum Realtime model compliance
- **Combined at runtime** via `build_prompt_with_language(base, language)` — directive at TOP for highest salience
- **Mid-conversation switching**: `LanguageSwitchHandler` rebuilds the full prompt and calls `update_instructions()`

**Key principle:** Prompts guide naturally, don't force rigid sequences. The LLM decides when to call tools based on conversation flow.

### Key Patterns

- **LLM lives on `AgentSession`**, not on individual agents. Agents only provide `instructions`.
- **Both agents extend `BaseAgent`**: `EngageIQAssistant` and `LeadCaptureAgent` both inherit from `BaseAgent` (`agents/base.py`), which provides `_safe_reply()` (retry + fallback) and `transcription_node` (streams text to frontend).
- **Tool return values**: Most tools return short directive instruction strings so the Realtime model generates a response. Only background tools (`save_conversation_summary`, `show_client`) return `None` (truly silent). Instructions are kept SHORT and directive to minimize double-message risk with the Realtime model.
- **Frontend communication** via LiveKit room topics: `message` (text), `products` (client images), `trigger` (UI buttons), `clean` (reset), `language` (language switch)
- **Intent scoring** is inline in tool functions (cumulative `+N` per tool call), max score: 5, threshold ≥3 for lead capture
- **Client images**: `show_client("core"/"dfki")` sends individual client images when discussed; `present_engageiq` sends all images during formal presentation. `clients_shown` in UserData prevents re-sending.
- **Graceful handling**: Vague answers get +1 intent (not 0), agent rephrases question once
- **Handoffs** return a new agent instance from `@function_tool` methods, passing `chat_ctx=self.session.history` for context preservation
- **Default language** is German (`config/languages.py:DEFAULT_LANGUAGE = "de"`)
- **Lead notification** sent to `info@ayand.ai` via non-blocking SMTP (`run_in_executor`)
- **Role-based personalization**: Agent detects visitor role, personalizes EngageIQ presentation
- **Consent flow**: Contact info collected → YES/NO buttons → explicit consent → save or discard
- **Partial leads**: If user gives contact info but closes session, partial data is saved
- **Transcript email extraction**: On sudden session close, `_extract_contact_from_transcript()` in `agent.py` scans the chat transcript for email addresses and populates `partial_email` if the LLM hadn't yet called `store_partial_contact_info`
- **EngageIQ guard**: `connect_to_lead_capture` requires `engageiq_presented=True` — agent must present product before lead capture
- **Natural product advocacy**: Agent always steers conversation toward EngageIQ naturally, even in casual exchanges. Mentioning EngageIQ is allowed anytime; formal presentation (calling `present_engageiq`) happens after 2-3 exchanges.
- **Client story social proof**: Agent uses CORE Oldenburg and DFKI stories mid-conversation (one per conversation, matched to visitor context)
- **Shutdown safety**: `on_shutdown` wraps `session.current_agent` in `try/except RuntimeError` and falls back to `session.history.items` — never loses data even if session isn't running
- **Session restart preserves attribution**: Both `restart_session` methods save history + send webhook before restarting, and preserve `campaign_source` in the fresh `UserData`

### Directory Structure

```
agent.py                    # Entry point — reads participant attributes, starts session
agents/
  base.py                   # BaseAgent + safe_generate_reply helper
  main_agent.py             # EngageIQAssistant (greet, detect role, present, qualify, handoff)
  lead_capture_agents.py    # LeadCaptureAgent (collect contact, consent, notify, goodbye, restart)
config/
  languages.py              # 10 languages with formality rules
  products.py               # EngageIQ config + ROLE_HOOKS for personalization
  settings.py               # LLM temperature, webhook config, thresholds
core/
  session_state.py          # UserData dataclass (includes partial contact fields)
  lead_storage.py           # JSON lead file storage
prompt/
  language.py               # Language directives (native-language, single source of truth)
  main_agent.py             # Main agent English base prompt builder
  workflow.py               # LeadCaptureAgent English base prompt builder
utils/
  language_switcher.py      # Mid-conversation language switching via data channel
  smtp.py                   # Gmail SMTP for lead notifications
  history.py                # Conversation transcript saving
  webhook.py                # Webhook integration with lead status tracking
```

## Conventions

### Agent Inheritance

Both agents extend `BaseAgent` (`agents/base.py`):

```python
class EngageIQAssistant(BaseAgent):  # NOT Agent directly
    def __init__(self, room, userdata=None, first_message=False):
        userdata = userdata or UserData()  # null safety
        # ... build prompt ...
        super().__init__(instructions=prompt, room=room, userdata=userdata)
```

`BaseAgent` provides:
- `_safe_reply(instructions)` — retry with backoff + fallback message on failure
- `transcription_node` — streams agent text to frontend via `"message"` topic

### Agent Handoffs

Return a new agent instance from a `@function_tool` to trigger handoff. Always pass `self.session.history` for context:
```python
@function_tool
async def connect_to_lead_capture(self, context: RunContext_T, confirm: bool):
    if confirm:
        await self.room.local_participant.send_text(
            json.dumps({"clean": True}), topic="clean"
        )
        base = build_lead_capture_prompt()
        instructions = build_prompt_with_language(base, self.userdata.language)
        return LeadCaptureAgent(
            instructions=instructions,
            room=self.room,
            chat_ctx=self.session.history,  # session-level history, not agent-level
            userdata=self.userdata,
        )
```

### Intent Scoring

Cumulative scoring in tool functions (max score: 5):
- `present_engageiq`: +2 (agent presents EngageIQ)
- `collect_challenge`: +3 (specific answer) or +1 (vague/don't know)

Stored in `UserData.intent_score`.

### Tools

| Tool | Purpose | Returns |
|------|---------|---------|
| `detect_visitor_role` | Store visitor's role | Short instruction to continue |
| `show_client` | Show individual client image+URL on frontend | `None` (silent — agent is already talking) |
| `present_engageiq` | Present EngageIQ with all client images | Instruction to present verbally |
| `collect_challenge` | Store visitor's challenge answer | Instruction to respond + check intent |
| `check_intent_and_proceed` | Check engagement level, send YES/NO buttons | Instructions based on score |
| `save_conversation_summary` | Save summary for webhook | `None` (silent) |
| `restart_session` | Save history + webhook, restart conversation | New agent |
| `connect_to_lead_capture` | Handoff or goodbye, send clean topic | New agent (true) or goodbye instruction (false) |

### Consent Flow (Lead Capture)

1. **Collect**: Visitor shares name and email (minimum required)
2. **Store temporarily**: `store_partial_contact_info` saves data + sends YES/NO consent buttons
3. **Ask consent**: Agent asks "May we use your contact information?"
4. **Handle response**:
   - YES → `confirm_consent(consent=true)` → save lead, send email/webhook
   - NO → `confirm_consent(consent=false)` → discard data, say goodbye

### Language Support

**10 languages** configured in `config/languages.py`:

| Code | Language | Default |
|------|----------|---------|
| `de` | German | **Yes** |
| `en` | English | |
| `nl` | Dutch | |
| `fr` | French | |
| `es` | Spanish | |
| `it` | Italian | |
| `pt` | Portuguese | |
| `pl` | Polish | |
| `tr` | Turkish | |
| `ar` | Arabic | |

**Architecture:**
- English-only base prompts in `prompt/main_agent.py` and `prompt/workflow.py`
- Native-language directives in `prompt/language.py` (written IN the target language)
- Combined via `build_prompt_with_language(base, lang)` — directive prepended at TOP
- Language read from `participant.attributes["user.language"]` at session start
- Mid-conversation switching via `LanguageSwitchHandler` (listens on `"language"` data channel topic)
- On switch: rebuilds full prompt (directive at TOP + English base) and calls `update_instructions()`

### Frontend Protocol

| Topic | Payload | Purpose |
|-------|---------|---------|
| `message` | `{"agent_response": "..."}` | Agent text to display |
| `products` | `[{"product_name": "...", "image": [...], "url": "..."}]` | Product data + images |
| `trigger` | `{"Ja, einverstanden": "Ja, einverstanden", ...}` | Consent buttons (label=key, localized) |
| `trigger` | `{"Ja, gerne": "Ja, gerne", ...}` | Contact sharing buttons (label=key, localized) |
| `trigger` | `{"Neues Gespräch": "Neues Gespräch", ...}` | New conversation button (localized) |
| `clean` | `{"clean": true}` | Clear product images from frontend |
| `language` | `{"language": "fr"}` | Switch agent language (frontend → agent) |

### Webhook Integration

**Webhook schema** matches target format with `contactInfo` fields:
- `name`, `email`, `phone`, `reachability` — contact details
- `potentialScore` — `intent_score * 20` (0-100 scale)
- `conversationBrief` — summary + role + challenge combined
- `nextStep` — derived from flow state (e.g., "Team will follow up via email")
- `status` — `hot_lead` / `warm_lead` / `declined` / `no_contact`

**Webhook company name**: `WEBHOOK_COMPANY_NAME` with `BOOTH_LOCATION` appended (e.g., `"Ayand AI-C4"`). Configured in `config/settings.py`.

**Webhook triggers**:
- Session shutdown (always — `on_shutdown` in `agent.py`)
- After consent confirmation (`confirm_consent`)
- When visitor declines consent (`confirm_consent(false)`) — webhook sent BEFORE clearing partial data
- **Immediately when email is collected** (`store_partial_contact_info`) — ensures partial lead data is sent even if session drops before consent
- On session restart (both agents save history + webhook before restarting)

**Note**: `connect_to_lead_capture(confirm=false)` does NOT save/webhook — it lets `on_shutdown` handle it since the visitor may continue talking.

### Role-Based Personalization

| Role | Keywords | Value Proposition |
|------|----------|-------------------|
| Marketing | marketing, cmo, demand generation | "Know which campaigns drive real demand, not just clicks" |
| Sales | sales, vp sales, business development | "Your best leads are the ones you never see" |
| Executive | ceo, cto, founder, managing director | "Turn invisible demand into measurable pipeline" |
| Operations | operations, customer experience, cx | "Every visitor interaction contains a signal" |
| Digital | e-commerce, digital, it director | "Your website works 24/7. Now it can qualify demand too" |

## Running

```bash
conda activate engage
python agent.py dev       # Development mode (connects to LiveKit Cloud)
python agent.py start     # Production mode
```

**Note:** `dev` mode with livekit-agents 1.4.1 may show no terminal logs (Rich console logging issue). The agent IS running — connect via LiveKit Agents Playground to test.

## Environment Variables

```
OPENAI_API_KEY=        # OpenAI API key for Realtime model
LIVEKIT_URL=           # wss://your-project.livekit.cloud
LIVEKIT_API_KEY=       # LiveKit API key
LIVEKIT_API_SECRET=    # LiveKit API secret
EMAIL_SENDER=          # Gmail address for sending lead notifications
EMAIL_PASSWORD=        # Gmail app password
WEBHOOK_URL=           # Webhook endpoint
WEBHOOK_API_KEY=       # Webhook API key
WEBHOOK_COMPANY_NAME=  # Company name for webhook
```

## Agent Identity Config (fill before launch)

Configured in `config/settings.py` (section 10):
- `AVATAR_NAME = "Leila"` — avatar's display name used throughout prompts
- `BOOTH_LOCATION = ""` — e.g., `"C4"` — appended to webhook company name (e.g., `"Ayand AI-C4"`)

Imported by `prompt/main_agent.py` from `config.settings`.

## Recent Changes (Feb 2026)

- **Language switching fixed**: Native-language directives prepended at TOP of prompt for Realtime model compliance
- **Prompt architecture**: English-only base prompts + separate `prompt/language.py` for language directives
- **`build_prompt_with_language()`**: Single function to combine base prompt + language directive at TOP
- **`LanguageSwitchHandler`**: Rebuilds full prompt on language change, detects agent type for correct base
- **Natural conversation**: Prompts guide rather than force rigid step sequences
- **Consent flow**: Explicit YES/NO consent buttons after collecting contact info
- **Partial leads**: Contact info saved even if session closes before consent
- **10 languages**: German (default), English, Dutch, French, Spanish, Italian, Portuguese, Polish, Turkish, Arabic
- **Temperature**: Set to 0.7 for more natural, varied responses
- **Frontend clean**: Product images cleared when entering lead capture
- **Lead status**: Webhook `status` field: `hot_lead`/`warm_lead`/`declined`/`no_contact`
- **Webhook on email**: Webhook fires immediately when email is collected (partial lead), not just on session end
- **EngageIQ presentation guard**: `engageiq_presented` flag in UserData; `connect_to_lead_capture` blocks until product is presented
- **Conversation naturalness**: Agent doesn't over-pitch; mentions EngageIQ selectively (every 3-4 exchanges max), uses visitor's name, never repeats talking points
- **Stronger language directives**: "Ignore ALL previous messages" + "from this point forward" + repeated emphasis in native language
- **Female persona**: Agent identity is female (she/her)
- **Ayand AI company knowledge**: Agent knows Ayand AI in detail (Düsseldorf startup, multimodal conversational AI for retail)
- **Rich client knowledge**: CORE Oldenburg (coworking/community hub) and DFKI (AI research institute) with detailed descriptions, use cases, and story hooks in `config/products.py`
- **Client story guidance**: Agent uses one client story per conversation as social proof, matched to visitor context
- **Live demo identity**: Agent strongly knows it IS EngageIQ — "you're using it right now" framing throughout prompt
- **Transcript email extraction**: Safety net in `on_shutdown()` — scans transcript for email if `partial_email` is empty before sending webhook

### Audit Fixes (Feb 2026)

- **Critical shutdown fix**: `on_shutdown` wraps `session.current_agent` in `try/except RuntimeError`, falls back to `session.history.items` — no more data loss on session close
- **EngageIQAssistant extends BaseAgent**: Inherits `_safe_reply()` and `transcription_node` — no more duplicated code
- **Handoff uses `session.history`**: `connect_to_lead_capture` passes `self.session.history` (session-level) instead of `self.chat_ctx` (agent-level)
- **Public `chat_ctx` API**: All `_chat_ctx` references replaced with public `chat_ctx` property or `session.history`
- **Avatar config centralized**: `AVATAR_NAME` and `BOOTH_LOCATION` in `config/settings.py`, imported by prompt builder
- **Booth location in webhook**: `BOOTH_LOCATION` appended to webhook `companyName` (e.g., `"Ayand AI-C4"`)
- **Intent constants aligned**: `INTENT_SCORE_MAX=5`, thresholds `3/4/5` (was `10` and `4/5/7`)
- **Null safety**: `userdata or UserData()` in both `EngageIQAssistant` and `BaseAgent` constructors
- **Restart saves data**: Both `restart_session` methods save history + send webhook before restarting, and preserve `campaign_source`
- **Webhook data ordering**: `confirm_consent(false)` sends webhook BEFORE clearing partial data
- **Decline doesn't save prematurely**: `connect_to_lead_capture(false)` no longer saves/webhooks mid-conversation — `on_shutdown` handles it
- **Non-blocking SMTP**: `send_lead_notification` wrapped in `run_in_executor` to avoid blocking the event loop
- **Async product send**: `_send_product_to_frontend` is now `async` and properly `await`ed
- **Prompt clarifications**: "Mentioning vs Presenting" distinction; `present_engageiq` allowed without role detection when visitor asks directly

### Conversation Smoothness (Feb 2026)

- **`show_client` tool**: New lightweight tool sends individual client images+URL when agent discusses CORE or DFKI — no need for full `present_engageiq`
- **`clients_shown` tracking**: UserData tracks which client images have been sent to avoid duplicates
- **Reduced over-pitching**: "Natural product advocacy" replaced with "less is more" — mention EngageIQ every 3-4 exchanges max, not every response
- **Anti-repetition rules**: Agent never repeats client stories, talking points, or transition phrases
- **Name usage**: Agent uses visitor's name when shared ("Nice to meet you, Bibi!")
- **Buying signal recognition**: Agent moves forward when visitor says "I want it" instead of continuing to pitch
- **Simplified tool returns**: `check_intent_and_proceed` returns concise instructions instead of re-pitching EngageIQ
- **Self-introduction variety**: Self-intro examples vary — some mention EngageIQ, some don't, avoiding robotic bridges
- **Answer-the-question rule**: Agent doesn't redirect to questions the visitor already answered
- **Tool return values (balanced approach)**: Most tools return short directive instruction strings to ensure the Realtime model responds after tool calls. Only background tools (`save_conversation_summary`, `show_client`) return `None` (truly silent). Instructions are kept SHORT and directive to minimize double-message risk. Previous all-`None` approach caused complete agent silence after tool calls.
- **One-message-per-turn rule**: Prompt rule 17 tells agent to follow tool instructions and respond in one message — never announce tool calls ("let me show you", "one moment")
- **Temperature 0.7**: Increased from 0.6 for more varied responses

## LiveKit SDK Patterns (Critical)

- **Seamless handoffs**: Return just the Agent instance for silent handoff
- **`chat_ctx` for handoffs**: Always pass `chat_ctx=self.session.history` (session-level context, not agent-level) when creating handoff agents
- **Public API**: Use `self.chat_ctx` (public property) never `self._chat_ctx` (private). For session-level history, use `session.history.items`.
- **`session.current_agent`**: Raises `RuntimeError` if session isn't running — always wrap in `try/except RuntimeError`
- **`update_instructions()`**: Sends `session.update` to OpenAI Realtime API — language directive must be at TOP of prompt for the model to follow it
- **`generate_reply(instructions=...)`**: Triggers immediate speech — do NOT use for silent language switching
- **Console mode**: `participant.attributes` is a MagicMock in console mode
- **SMTP in async context**: `smtplib` is blocking — always wrap in `asyncio.get_running_loop().run_in_executor(None, ...)` when calling from async code

## Language Switching (Important)

Language directives MUST be:
1. **At the TOP** of the system prompt (highest salience position for OpenAI Realtime)
2. **Written in the target language** (German directive in German, etc.) — English-only directives are ignored by the model
3. **Strong and emphatic** — UPPERCASE, "HIGHEST PRIORITY", "IGNORE all previous messages", repeated emphasis at end

The `prompt/language.py` file is the single source of truth. Never add language directives to base prompts. Always use `build_prompt_with_language(base, language)` to compose.
