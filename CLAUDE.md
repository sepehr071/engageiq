# EngageIQ Voice Agent

## What This Is

LiveKit voice agent for Ayand AI's EuroShop 2026 booth. Visitors scan a QR code, an avatar opens on their phone, the agent presents EngageIQ (Ayand AI's product), qualifies them as a lead, and captures their contact info.

**This agent IS the product** — visitors experience EngageIQ by talking to it.

## Tech Stack

- **Runtime:** Python 3.12
- **Voice Framework:** LiveKit Agents SDK (`livekit-agents 1.4.1`)
- **Voice Model:** OpenAI Realtime API (`gpt-realtime-mini-2025-10-06`)
- **Model Temperature:** `0.6` (configured in `config/settings.py`)
- **No RAG, no search, no Flask** — all product knowledge is baked into prompts
- **Note:** Noise cancellation (BVC) requires LiveKit Cloud paid plan — currently disabled

## Agent Identity (Product Truth Alignment)

The agent embodies EngageIQ's core identity from `Product_Truth_Final.md`:

- **Product class:** Conversational Demand Interface
- **Philosophy:** "Signal, not automation" — the agent captures demand signals, not automates tasks
- **Core mechanism:** AI avatar engages visitors, guides intent clarification, records signals, outputs structured data
- **Value creation:** Converting unobserved visitor interactions into measurable intent and behavioral data

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

**Simplified architecture with single English base prompt + language directive:**

The main prompt (`prompt/main_agent.py`) has these sections:
1. **Identity** — avatar role, company one-liner, personality, self-introduction rules
2. **About EngageIQ** — what it does, value, clients (CORE, DFKI), chatbot differentiation
3. **Product Knowledge** — EngageIQ product details
4. **How to Have This Conversation** — natural flow guide (not rigid steps)
5. **Tools** — function tools documented inline
6. **Behavior Rules** — covering response length, conversation style, pricing
7. **Language Instruction** — injected only for non-English languages

**Key principle:** Prompts guide naturally, don't force rigid sequences. The LLM decides when to call tools based on conversation flow.

### Key Patterns

- **LLM lives on `AgentSession`**, not on individual agents. Agents only provide `instructions`.
- **Silent tools**: Tools return `None` to avoid robotic announcements like "Let me save a quick summary"
- **Frontend communication** via LiveKit room topics: `message` (text), `products` (client images), `trigger` (UI buttons), `clean` (reset)
- **Intent scoring** is inline in tool functions (cumulative `+N` per tool call), max score: 5
- **Client images**: When explaining EngageIQ, agent calls `present_engageiq` which sends CORE/DFKI images to frontend
- **Graceful handling**: Vague answers get +1 intent (not 0), agent rephrases question once
- **Handoffs** return a new agent instance from `@function_tool` methods
- **Default language** is German (`config/languages.py:DEFAULT_LANGUAGE = "de"`)
- **Lead notification** sent to `info@ayand.ai`
- **Role-based personalization**: Agent detects visitor role, personalizes EngageIQ presentation
- **Consent flow**: Contact info collected → YES/NO buttons → explicit consent → save or discard
- **Partial leads**: If user gives contact info but closes session, partial data is saved

### Directory Structure

```
agent.py                    # Entry point — reads participant attributes, starts session
agents/
  base.py                   # BaseAgent + safe_generate_reply helper
  main_agent.py             # EngageIQAssistant (greet, detect role, present, qualify, handoff)
  lead_capture_agents.py    # LeadCaptureAgent (collect contact, consent, notify, goodbye, restart)
config/
  languages.py              # 10 languages with greetings and formality rules
  products.py               # EngageIQ config + ROLE_HOOKS for personalization
  settings.py               # LLM temperature, webhook config, thresholds
core/
  session_state.py          # UserData dataclass (includes partial contact fields)
  lead_storage.py           # JSON lead file storage
prompt/
  main_agent.py             # Main agent prompt builder (English base + language directive)
  workflow.py               # LeadCaptureAgent prompt builder
utils/
  smtp.py                   # Gmail SMTP for lead notifications
  history.py                # Conversation transcript saving
  webhook.py                # Webhook integration with lead status tracking
```

## Conventions

### Silent Tools (Important)

Tools return `None` to avoid the LLM speaking robotic messages. Only return a string if you want the LLM to announce something:

```python
@function_tool
async def save_conversation_summary(self, context: RunContext_T, summary: str):
    logger.info(f"Conversation summary: {summary}")
    self.userdata.conversation_summary = summary.strip()
    return None  # Silent — don't say "summary saved" out loud
```

### Agent Handoffs

Return a new agent instance from a `@function_tool` to trigger handoff:
```python
@function_tool
async def connect_to_lead_capture(self, context: RunContext_T, confirm: bool):
    if confirm:
        # Send clean topic to remove product images
        await self.room.local_participant.send_text(
            json.dumps({"clean": True}), topic="clean"
        )
        return LeadCaptureAgent(
            instructions=build_lead_capture_prompt(self.userdata.language),
            room=self.room,
            chat_ctx=self.chat_ctx,
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
| `detect_visitor_role` | Store visitor's role | `None` (silent) |
| `present_engageiq` | Present EngageIQ with client images | Presentation overlay |
| `collect_challenge` | Store visitor's challenge answer | `None` (silent) |
| `check_intent_and_proceed` | Check engagement level, send YES/NO buttons | Instructions |
| `save_conversation_summary` | Save summary for webhook | `None` (silent) |
| `restart_session` | Restart conversation from beginning | New agent |
| `connect_to_lead_capture` | Handoff or goodbye, send clean topic | New agent or None |

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
- Single English base prompt in `prompt/main_agent.py`
- Language directive injected at prompt build time for non-English
- Greeting templates stored in `config/languages.py`
- Language read from `participant.attributes["user.language"]` at session start

### Frontend Protocol

| Topic | Payload | Purpose |
|-------|---------|---------|
| `message` | `{"agent_response": "..."}` | Agent text to display |
| `products` | `[{"product_name": "...", "image": [...], "url": "..."}]` | Product data + images |
| `trigger` | `{"consent_yes": "Yes", "consent_no": "No"}` | YES/NO consent buttons |
| `trigger` | `{"share_contact_yes": "Yes", "share_contact_no": "No"}` | Contact sharing buttons |
| `trigger` | `{"new_conversation": "New Conversation"}` | New conversation button |
| `clean` | `{"clean": true}` | Clear product images from frontend |

### Webhook Integration

**Lead status** included in webhook payload:
- `no_contact` — no contact info collected
- `partial` — contact info collected but no consent (session ended abruptly)
- `complete` — full lead with consent
- `declined` — explicitly declined consent

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

## Placeholders (fill before launch)

- `prompt/main_agent.py`: `AVATAR_NAME = "[AVATAR_NAME_TBD]"` and `BOOTH_LOCATION = "[BOOTH TBD]"`

## Recent Changes (Feb 2026)

- **Simplified prompts**: Removed `_LANG` dictionaries, now using single English base + language directive
- **Silent tools**: Tools return `None` instead of strings to avoid robotic messages
- **Natural conversation**: Prompts guide rather than force rigid step sequences
- **Consent flow**: Explicit YES/NO consent buttons after collecting contact info
- **Partial leads**: Contact info saved even if session closes before consent
- **10 languages**: German (default), English, Dutch, French, Spanish, Italian, Portuguese, Polish, Turkish, Arabic
- **Temperature**: Set to 0.6 for more consistent responses
- **Frontend clean**: Product images cleared when entering lead capture
- **Lead status**: Webhook includes `leadStatus` field (no_contact/partial/complete/declined)

## LiveKit SDK Patterns (Critical)

- **Tool return values**: Return `None` for silent tools, return string only if LLM should speak
- **Seamless handoffs**: Return just the Agent instance for silent handoff
- **`chat_ctx`**: Always pass `chat_ctx=self.chat_ctx` when creating handoff agents
- **Console mode**: `participant.attributes` is a MagicMock in console mode
