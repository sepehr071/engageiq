# EngageIQ Voice Agent

## What This Is

LiveKit voice agent for Ayand AI's EuroShop 2026 booth. Visitors scan a QR code, an avatar opens on their phone, the agent presents EngageIQ (Ayand AI's product), qualifies them as a lead, and captures their contact info.

**This agent IS the product** — visitors experience EngageIQ by talking to it.

## Tech Stack

- **Runtime:** Python 3.12
- **Voice Framework:** LiveKit Agents SDK (`livekit-agents 1.4.1`)
- **Voice Model:** OpenAI Realtime API (`gpt-realtime-mini-2025-10-06`)
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

### Tier Knowledge (only when asked)

- **Bronze:** Raw interaction and intent signals — proof demand exists
- **Silver:** Active intent clarification + routing (what the visitor is experiencing)
- **Gold:** Longitudinal demand analysis — patterns and shifts over time

## Architecture

### Agent Flow (2 agents, single handoff)

```
EngageIQAssistant (greet → detect role → present EngageIQ personalized → qualify → check intent → lead capture or goodbye)
  → LeadCaptureAgent (collect contact details → save lead → send email + webhook → goodbye → restart)
```

The main agent greets, detects the visitor's role, presents EngageIQ personalized to their role with client examples (CORE, DFKI), then asks one qualification question. After qualification, `check_intent_and_proceed` determines:
- **Score ≥3**: Offer lead capture
- **Score <3**: Try to re-engage visitor; if still disengaged, say goodbye

Only one handoff occurs — to LeadCaptureAgent when the visitor agrees to share contact details.

### Prompt Architecture

The main prompt (`prompt/main_agent.py`) has these sections:
1. **Identity** — avatar role, company one-liner, personality, self-awareness as product demo
2. **Core Positioning** — "Signal, not automation", mechanism, value creation, chatbot differentiation
3. **Boundaries** — never promise results, staff augmentation not replacement, no transactions
4. **Language & Formality** — per-language rules (Sie/vous/usted etc.)
5. **Product Knowledge** — EngageIQ product with client examples (CORE, DFKI)
6. **Conversation Flow** — 5-step flow with role detection (greet → detect role → present EngageIQ → qualify → lead capture/goodbye)
7. **Tools** — 5 function tools documented inline
8. **Behavior Rules** — covering response length, pricing, chatbot comparison, graceful handling

The agent engages visitors with a question, detects their role, presents EngageIQ personalized to their role, shows client images (CORE, DFKI), then asks one qualification question.

### Key Patterns

- **LLM lives on `AgentSession`**, not on individual agents. Agents only provide `instructions`.
- **`BaseAgent`** (`agents/base.py`) is the shared base for sub-agents. `EngageIQAssistant` extends `Agent` directly.
- **Frontend communication** via LiveKit room topics: `message` (text), `products` (client images), `trigger` (UI buttons), `clean` (reset).
- **Intent scoring** is inline in tool functions (cumulative `+N` per tool call), max score: 5.
- **Client images**: When explaining EngageIQ, agent calls `present_engageiq` which sends CORE/DFKI images to frontend.
- **Graceful handling**: Vague answers get +1 intent (not 0), agent rephrases question once.
- **Handoffs** return a new agent instance from `@function_tool` methods.
- **Default language** is English (`config/languages.py:DEFAULT_LANGUAGE`).
- **Lead notification** sent to `info@ayand.ai`.
- **Role-based personalization**: Agent detects visitor role early, then personalizes EngageIQ presentation with role-specific value propositions (see `ROLE_HOOKS` in `config/products.py`).
- **Webhook integration**: All sessions send data to `https://ayand-log.vercel.app/api/webhooks/ingest` for analytics.

### Directory Structure

```
agent.py                    # Entry point — reads participant attributes, starts session
agents/
  base.py                   # BaseAgent + safe_generate_reply helper
  main_agent.py             # EngageIQAssistant (greet, detect role, present, qualify, handoff)
  lead_capture_agents.py    # LeadCaptureAgent (collect contact, notify, goodbye, restart)
config/                     # All static configuration (company, products, agents, languages)
  products.py               # EngageIQ config + ROLE_HOOKS for personalization
core/
  session_state.py          # UserData dataclass (shared across all agents via AgentSession)
  lead_storage.py           # JSON lead file storage
prompt/
  main_agent.py             # Main agent prompt builder (product knowledge, behavior rules)
  workflow.py               # LeadCaptureAgent prompt builder
utils/
  smtp.py                   # Gmail SMTP for lead notifications
  history.py                # Conversation transcript saving
  webhook.py                # Webhook integration for session analytics
```

## Conventions

### Agent Handoffs

Return a new agent instance from a `@function_tool` to trigger handoff. Do NOT include a
tuple message if you want the handoff to be seamless (new agent speaks via `on_enter()`):
```python
@function_tool
async def handoff_tool(self, context: RunContext_T, ...):
    # No tuple — silent handoff, new agent's on_enter() speaks first
    return NextAgent(
        instructions=build_prompt(self.userdata.language),
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

### Role Detection

The agent uses `detect_visitor_role` tool to capture the visitor's job role early in the conversation. This role is then used to:
1. Personalize the EngageIQ value proposition (via `ROLE_HOOKS` in `config/products.py`)
2. Ask role-relevant qualification questions
3. Store in `UserData.visitor_role` for analytics

### Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `detect_visitor_role` | Detect and store visitor's role | `role` (required) |
| `present_engageiq` | Present EngageIQ with client images | none |
| `collect_challenge` | Store visitor's challenge answer | `challenge` (required) |
| `check_intent_and_proceed` | Check engagement level | none |
| `save_conversation_summary` | Save conversation summary for webhook | `summary` (required) |
| `restart_session` | Restart conversation from beginning | none |
| `connect_to_lead_capture` | Handoff or goodbye | `confirm` (required) |

After qualification, `check_intent_and_proceed` uses the score:
- **Score ≥3**: Visitor is qualified → offer lead capture
- **Score <3**: Low engagement → try one more re-engagement approach, then goodbye if still disengaged

**Graceful handling**: Vague answers ("don't know", "not sure") still get +1 intent score. Agent rephrases question once before moving on.

### Language Support

- 10 languages configured in `config/languages.py`
- Default is English (`DEFAULT_LANGUAGE = "en"`)
- Language is read from `participant.attributes["user.language"]` at session start
- Prompts are built dynamically via `_LANG` dicts in `prompt/main_agent.py` and `prompt/workflow.py`
- Only German and English have full phrase packs; other languages rely on the LLM's multilingual capability

### Frontend Protocol

| Topic | Payload | Purpose |
|-------|---------|---------|
| `message` | `{"agent_response": "..."}` | Agent text to display |
| `products` | `[{"product_name": "...", "image": [...], "url": "..."}]` | Product data + images (array format) |
| `trigger` | `{"new_conversation": "New Conversation"}` | UI button triggers (key=action, value=button text) |
| `clean` | `{"clean": true}` | Reset frontend state |

**Button Flow:**
1. Backend sends button via `send_text({"new_conversation": "New Conversation"})`
2. Button appears in frontend
3. User clicks → sends "New Conversation" as text input to LLM
4. LLM recognizes this and calls `restart_session` tool
5. Session restarts with fresh greeting

### Product & Client Images

**EngageIQ** is Ayand AI's product. The agent talks about EngageIQ and shows client examples:

| Client | Image | URL |
|--------|-------|-----|
| CORE | `https://image.ayand.cloud/euro/core.png` | `https://vimeo.com/1165136133/9930020d47?share=copy&fl=sv&fe=ci` |
| DFKI | `https://image.ayand.cloud/euro/dfki.png` | `https://vimeo.com/1165136145/062503170c?share=copy&fl=sv&fe=ci` |

Images are sent to frontend via `products` topic when `present_engageiq` tool is called. CORE and DFKI are Ayand AI clients who use EngageIQ.

### Lead Notifications

- Email sent to `info@ayand.ai` (configurable in `utils/smtp.py:DEFAULT_RECIPIENT`)
- JSON saved to `leads/lead_YYYYMMDD_HHMMSS.json`
- Conversation transcript saved to `history/conversation_YYYYMMDD_HHMMSS.txt`
- Webhook sent to `https://ayand-log.vercel.app/api/webhooks/ingest` for analytics

### Webhook Integration

Session data is sent to the webhook endpoint at these points:
1. **Session shutdown** (`agent.py:on_shutdown`) — captures ALL conversations
2. **Lead captured** (`lead_capture_agents.py:collect_lead_info`) — when contact info is collected
3. **Visitor declines** (`main_agent.py:connect_to_lead_capture`) — when visitor declines contact
4. **Session restart** (`restart_session` tool) — before restart

**Payload structure:**
```json
{
  "apiKey": "ayand-secret-key-3dcSDSfgcGsasdcvg3235fvsaacv1",
  "companyName": "Ayand AI",
  "sessions": [{
    "sessionId": "user-xxx",
    "date": "2026-02-16T15:30:00Z",
    "durationSeconds": 120,
    "transcript": [{"role": "user/assistant", "content": "..."}],
    "contactInfo": {
      "name": "...",
      "email": "...",
      "phone": "...",
      "company": "...",
      "role": "...",
      "potentialScore": 80,
      "conversationBrief": "Marketing director interested in demand attribution. High interest."
    }
  }]
}
```

Configuration in `config/settings.py`: `WEBHOOK_URL`, `WEBHOOK_API_KEY`, `WEBHOOK_COMPANY_NAME`

### Role-Based Personalization

The agent detects the visitor's role early in the conversation and personalizes the EngageIQ presentation:

| Role | Keywords | Value Proposition |
|------|----------|-------------------|
| Marketing | marketing, cmo, demand generation | "Know which campaigns drive real demand, not just clicks" |
| Sales | sales, vp sales, business development | "Your best leads are the ones you never see" |
| Executive | ceo, cto, founder, managing director | "Turn invisible demand into measurable pipeline" |
| Operations | operations, customer experience, cx | "Every visitor interaction contains a signal" |
| Digital | e-commerce, digital, it director | "Your website works 24/7. Now it can qualify demand too" |

Configuration in `config/products.py:ROLE_HOOKS` and `get_role_hook()` function.

## Running

```bash
conda activate engage
python agent.py dev       # Development mode (connects to LiveKit Cloud)
python agent.py start     # Production mode
```

**Note:** `dev` mode with livekit-agents 1.4.1 may show no terminal logs (Rich console logging issue). The agent IS running — connect via LiveKit Agents Playground to test.

**Console mode does NOT work** with RealtimeModel (audio-only). Use `dev` mode with the LiveKit Agents Playground.

## Environment Variables

```
OPENAI_API_KEY=        # OpenAI API key for Realtime model
LIVEKIT_URL=           # wss://your-project.livekit.cloud
LIVEKIT_API_KEY=       # LiveKit API key
LIVEKIT_API_SECRET=    # LiveKit API secret
EMAIL_SENDER=          # Gmail address for sending lead notifications
EMAIL_PASSWORD=        # Gmail app password
WEBHOOK_URL=           # Webhook endpoint (default: https://ayand-log.vercel.app/api/webhooks/ingest)
WEBHOOK_API_KEY=       # Webhook API key (default: ayand-secret-key-3dcSDSfgcGsasdcvg3235fvsaacv1)
WEBHOOK_COMPANY_NAME=  # Company name for webhook (default: Ayand AI)
```

## Placeholders (fill before launch)

- `prompt/main_agent.py`: `AVATAR_NAME = "[AVATAR_NAME_TBD]"` and `BOOTH_LOCATION = "[BOOTH TBD]"`
- `config/company.py`: `booth_location: "[BOOTH TBD]"`
- `config/agents.py`: `name: "[AVATAR_NAME_TBD]"`
- `prompt/workflow.py`: Booth references use `"[STAND TBD]"` (DE) / `"[BOOTH TBD]"` (EN)

## Recent Changes (Feb 2026)

- **Simplified to single product**: EngageIQ only (removed CarIQ, Concierge, Shelf Twin)
- **No industry detection**: Agent presents EngageIQ directly to all visitors
- **Client examples**: CORE and DFKI (Ayand AI clients using EngageIQ)
- **Simplified qualification**: 1 question instead of 3
- **Intent scoring**: Max 5 (was 9), threshold ≥3 for qualified
- **Graceful handling**: Vague answers get +1, agent rephrases once
- **Image timing**: Images shown when explaining EngageIQ, not at greeting
- **Lead email**: Changed to `info@ayand.ai`
- **Engaging greeting**: Asks "What brings you to our booth today?"
- **Role-based personalization**: Agent detects visitor role and personalizes presentation with role-specific value propositions
- **Webhook integration**: All sessions send data to external analytics endpoint
- **History saving**: Conversation history saved immediately on decline, not just on shutdown
- **Session tracking**: Added `session_id` and `session_start_time` to UserData for duration calculation
- **Conversation summary**: LLM generates summary via `save_conversation_summary` tool before ending, included in webhook `conversationBrief` field
- **Button payload format**: Changed to `{"new_conversation": "New Conversation"}` (key=action, value=button text)
- **Session restart**: Renamed tool to `restart_session` to prevent auto-generated duplicate buttons; LLM calls this when visitor says "New Conversation"
- **Messaging fix**: Changed "send info to email" to "our team will contact you" — we collect leads, not send info

## Based On

Adapted from the "Berta" car dealership voice agent at `E:\herbrand-main\herbrand-main`. Berta's complexity (Pinecone, TF-IDF, Flask, 40+ dependencies) was stripped down to a lean 9-dependency project with 3 static products and no RAG.

## LiveKit Resources

- **LiveKit Agents Docs**: https://docs.livekit.io/agents/
- **Agent Starter Python**: https://github.com/livekit-examples/agent-starter-python
- **AGENTS.md Guide**: https://github.com/livekit-examples/agent-starter-python/blob/main/AGENTS.md
- **LiveKit Cloud Dashboard**: https://cloud.livekit.io/

### LiveKit SDK Patterns (Critical)

These patterns prevent common bugs:

- **Tool return values**: Returning a string from `@function_tool` sends it to the LLM which generates a spoken reply. Returning `None` completes the tool silently (no LLM response). Always return a string if you want the agent to keep talking.
- **Seamless handoffs**: Return just the Agent instance (no tuple) for silent handoff — the new agent's `on_enter()` speaks first. Return `(Agent, "message")` only if the current agent should say something before handing off.
- **`on_enter()`**: Use `await self.session.generate_reply(instructions="...")` to make the agent speak proactively when it becomes active.
- **`chat_ctx`**: Always pass `chat_ctx=self.chat_ctx` when creating handoff agents to preserve conversation history.
- **Console mode**: `participant.attributes` is a MagicMock in console mode. Always check `isinstance(participant.attributes, dict)` before calling `.get()`.
- **Noise cancellation**: `noise_cancellation.BVC()` requires LiveKit Cloud paid plan. Without it, the agent works but without background noise filtering.
