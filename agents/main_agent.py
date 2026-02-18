"""
Main conversational agent (EngageIQAssistant) — handles greeting, product presentation,
simplified qualification, and intent scoring.

This agent IS the demo: visitors experience EngageIQ by talking to it.
"""

import json
import logging
from livekit.agents import function_tool
from agents.base import BaseAgent

from core.session_state import UserData, RunContext_T
from config.products import PRODUCTS
from prompt.main_agent import build_main_prompt, build_greeting
from prompt.language import build_prompt_with_language, lang_hint
from config.languages import get_language_config, get_button_labels
from utils.history import save_conversation_to_file
from utils.webhook import send_session_webhook

logger = logging.getLogger(__name__)

# Phrases that indicate a vague/non-specific challenge
_VAGUE_CHALLENGE = [
    "not sure", "nothing specific", "just looking", "don't know",
    "keine ahnung", "weiss nicht", "nichts bestimmtes", "nur schauen",
]


def _build_product_data_for_prompt() -> dict:
    """Transform config PRODUCTS into the format expected by prompt builders."""
    result = {}
    for key, p in PRODUCTS.items():
        pricing = p.get("pricing", {})
        pilot_str = pricing.get("structure", "Contact sales")
        if pricing.get("guarantee"):
            pilot_str += f" ({pricing['guarantee']})"

        # Build client info string
        clients = p.get("clients", [])
        clients_str = ""
        if clients:
            client_names = [c["name"] for c in clients]
            clients_str = f"Used by: {', '.join(client_names)}"

        result[key] = {
            "name": p["name"],
            "tagline": p.get("subtitle", ""),
            "problem": p.get("problem_solved", ""),
            "value_proposition": p.get("value_prop", ""),
            "capabilities": p.get("capabilities", []),
            "installation": p.get("installation", ""),
            "pilot_pricing": pilot_str,
            "clients": clients_str,
            "client_details": clients,
        }
    return result


class EngageIQAssistant(BaseAgent):
    """Main EuroShop booth agent.

    Handles:
    - Greeting in the visitor's language
    - EngageIQ product presentation with client examples
    - Simplified qualification (1 question with intent scoring)
    - Handoff to lead capture when qualified
    """

    def __init__(
        self,
        room,
        userdata: UserData | None = None,
        first_message: bool = False,
    ) -> None:
        self.first_message = first_message
        self._product_data = _build_product_data_for_prompt()
        userdata = userdata or UserData()  # M1: null safety
        base = build_main_prompt(self._product_data)
        prompt = build_prompt_with_language(base, userdata.language)
        super().__init__(instructions=prompt, room=room, userdata=userdata)

    async def on_enter(self):
        logger.info(f"EngageIQAssistant on_enter (first={self.first_message}, lang={self.userdata.language})")
        if self.first_message:
            greeting = build_greeting(self.userdata.language)
            await self._safe_reply(greeting)

    # ══════════════════════════════════════════════════════════════════════════
    # ROLE DETECTION
    # ══════════════════════════════════════════════════════════════════════════

    @function_tool
    async def detect_visitor_role(self, context: RunContext_T, role: str):
        """
        Store the visitor's professional job title or role.
        ONLY call this when the visitor explicitly mentions their job title or business function.

        role (required): A professional job title or business role.
            GOOD examples: "Marketing Director", "CEO", "Sales Manager", "Head of E-Commerce"
            BAD — NEVER use: person's names, greetings, "just looking", "visitor"

        If the visitor only shares their name, do NOT call this tool. Wait for an actual job title.
        """
        logger.info(f"Detected visitor role: {role}")
        self.userdata.visitor_role = role.strip() if role else None
        hint = lang_hint(self.userdata.language)
        return f"Role noted. Continue the conversation naturally. {hint}"

    # ══════════════════════════════════════════════════════════════════════════
    # CONVERSATION SUMMARY
    # ══════════════════════════════════════════════════════════════════════════

    @function_tool
    async def save_conversation_summary(self, context: RunContext_T, summary: str):
        """
        Call this to save a brief summary of the conversation before ending or handing off.
        summary (required): A 1-2 sentence summary of what the visitor is looking for and their interest level.
        """
        logger.info(f"Conversation summary: {summary}")
        self.userdata.conversation_summary = summary.strip()
        hint = lang_hint(self.userdata.language)
        return f"Summary saved. Continue the conversation. {hint}"

    # ══════════════════════════════════════════════════════════════════════════
    # SESSION RESTART
    # ══════════════════════════════════════════════════════════════════════════

    @function_tool
    async def restart_session(self, context: RunContext_T):
        """
        Call this when the visitor says "New Conversation" or wants to start fresh.
        """
        logger.info("Restarting session from main agent")
        # M2: Save history + webhook before restart
        try:
            chat_history = self.chat_ctx.items
            save_conversation_to_file(chat_history, self.userdata)
            session_id = self.userdata.session_id or "unknown"
            await send_session_webhook(session_id, chat_history, self.userdata)
            self.userdata._history_saved = True
            logger.info("Conversation saved and webhook sent before restart")
        except Exception as e:
            logger.error(f"Failed to save conversation on restart: {e}")
        # M3: Preserve campaign_source
        lang = self.userdata.language
        source = self.userdata.campaign_source
        return EngageIQAssistant(
            room=self.room,
            userdata=UserData(language=lang, campaign_source=source),
            first_message=True,
        )

    # ══════════════════════════════════════════════════════════════════════════
    # CLIENT IMAGE DISPLAY
    # ══════════════════════════════════════════════════════════════════════════

    @function_tool
    async def show_client(self, context: RunContext_T, client_name: str):
        """
        Call this when you mention or discuss a specific client to show their images on the visitor's screen.
        client_name (required): "core" or "dfki"
        """
        key = client_name.strip().lower()
        # Find the matching client in product data
        clients = PRODUCTS.get("engageiq", {}).get("clients", [])
        client = None
        for c in clients:
            if key in c["name"].lower():
                client = c
                break

        hint = lang_hint(self.userdata.language)
        if not client:
            logger.warning(f"show_client: unknown client '{client_name}'")
            return f"Continue discussing the client naturally. {hint}"

        # Skip if already shown
        if key in self.userdata.clients_shown:
            return f"Continue discussing the client naturally. {hint}"

        self.userdata.clients_shown.append(key)

        # Send single client image+URL to frontend
        payload = [{
            "product_name": client["name"],
            "image": client.get("images", []),
            "url": client.get("url", ""),
        }]
        try:
            await self.room.local_participant.send_text(
                json.dumps(payload),
                topic="products",
            )
            logger.info(f"Sent {client['name']} images to frontend")
        except Exception as e:
            logger.error(f"Failed to send client images: {e}")

        return f"Client images sent to screen. Continue discussing them naturally. {hint}"

    # ══════════════════════════════════════════════════════════════════════════
    # PRODUCT PRESENTATION
    # ══════════════════════════════════════════════════════════════════════════

    @function_tool
    async def present_engageiq(self, context: RunContext_T):
        """
        Call this after detecting visitor role to present EngageIQ with personalized value proposition.
        """
        # Idempotency guard — only present once per session
        if self.userdata.engageiq_presented:
            hint = lang_hint(self.userdata.language)
            logger.info("present_engageiq called again but already presented — skipping")
            return f"You already presented EngageIQ. Do NOT present again. Continue the conversation — ask about their challenge or check engagement. {hint}"

        logger.info(f"Presenting EngageIQ to visitor with role: {self.userdata.visitor_role}")

        # Mark presentation as done
        self.userdata.engageiq_presented = True

        # Mark all clients as shown (present_engageiq sends all images)
        for c in PRODUCTS.get("engageiq", {}).get("clients", []):
            key = c["name"].lower().split()[0]  # "core", "dfki"
            if key not in self.userdata.clients_shown:
                self.userdata.clients_shown.append(key)

        # Intent: visitor engaged with greeting
        self.userdata.intent_score += 2
        logger.info(f"Intent score after presentation: {self.userdata.intent_score}")

        # Send EngageIQ + client images to frontend
        await self._send_product_to_frontend("engageiq")

        hint = lang_hint(self.userdata.language)
        role = self.userdata.visitor_role
        if role:
            return f"Images are on their screen. Present EngageIQ now — connect it to their role as {role}. Keep it to 2-3 sentences. {hint}"
        else:
            return f"Images are on their screen. Present EngageIQ now — explain what it does and that they're experiencing it right now. Keep it to 2-3 sentences. {hint}"

    async def _send_product_to_frontend(self, product_key: str) -> None:
        """Send product info + client images to frontend via 'products' topic."""
        product = PRODUCTS.get(product_key)
        if not product:
            return

        # Build payload - only include EngageIQ if it has images
        payload = []

        # Add main product only if it has images
        if product.get("images"):
            payload.append({
                "product_name": product["name"],
                "image": product.get("images", []),
                "url": product.get("url", ""),
            })

        # Add client images with their URLs
        for client in product.get("clients", []):
            payload.append({
                "product_name": client["name"],
                "image": client.get("images", []),
                "url": client.get("url", ""),
            })

        try:
            await self.room.local_participant.send_text(
                json.dumps(payload),
                topic="products",
            )
        except Exception as e:
            logger.error(f"Failed to send product to frontend: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # QUALIFICATION (simplified — just one question)
    # ══════════════════════════════════════════════════════════════════════════

    @function_tool
    async def collect_challenge(self, context: RunContext_T, challenge: str):
        """
        Call this when the visitor describes their biggest challenge with customer demand or engagement.
        challenge (required): A brief summary of the visitor's stated challenge. Can be vague if they're unsure.
        """
        logger.info(f"Challenge collected: {challenge}")
        self.userdata.biggest_challenge = challenge

        # Intent: specific challenge = +3, vague/don't know = +1 (always give at least +1)
        challenge_lower = challenge.lower()
        if any(v in challenge_lower for v in _VAGUE_CHALLENGE):
            self.userdata.intent_score += 1
            logger.info(f"Intent score after vague challenge: {self.userdata.intent_score}")
        else:
            self.userdata.intent_score += 3
            logger.info(f"Intent score after specific challenge: {self.userdata.intent_score}")
        hint = lang_hint(self.userdata.language)
        if not self.userdata.engageiq_presented:
            return f"Challenge noted. Now present EngageIQ as the solution to their challenge — call present_engageiq and connect it to what they just told you. {hint}"
        return f"Challenge noted. Respond with empathy, then call check_intent_and_proceed. {hint}"

    # ══════════════════════════════════════════════════════════════════════════
    # INTENT CHECK & RE-ENGAGEMENT
    # ══════════════════════════════════════════════════════════════════════════

    @function_tool
    async def check_intent_and_proceed(self, context: RunContext_T):
        """
        Call this AFTER collecting the visitor's challenge.
        Checks visitor engagement level and returns instructions for next step.
        """
        # Guard: EngageIQ must be presented before checking intent
        if not self.userdata.engageiq_presented:
            hint = lang_hint(self.userdata.language)
            logger.info("check_intent_and_proceed blocked: EngageIQ not yet presented")
            return f"You haven't presented EngageIQ yet. Call present_engageiq first — connect it to the visitor's challenge or role. {hint}"

        score = self.userdata.intent_score
        logger.info(f"Checking intent score: {score}/5")

        if score >= 3:
            # Send YES/NO contact sharing buttons to frontend
            labels = get_button_labels(self.userdata.language)
            try:
                await self.room.local_participant.send_text(
                    json.dumps({labels["share_yes"]: labels["share_yes"], labels["share_no"]: labels["share_no"]}),
                    topic="trigger",
                )
                logger.info("Sent contact sharing buttons to frontend")
            except Exception as e:
                logger.error(f"Failed to send contact sharing buttons: {e}")

            # Good signal - have more conversation before asking for contact
            hint = lang_hint(self.userdata.language)
            return f"""GOOD_SIGNAL: The visitor seems interested.

Acknowledge their challenge with empathy, then naturally ask if they'd like our team to follow up with them.

YES/NO buttons are on their screen. They can click or say Yes/No.
If Yes → call connect_to_lead_capture(confirm=true).
If No → call connect_to_lead_capture(confirm=false).

{hint}"""
        else:
            # Continue conversation - don't rush
            return f"""CONTINUE_CONVERSATION: The visitor isn't fully engaged yet.

Keep the conversation natural — ask about their situation, listen genuinely. If they warm up, offer to have the team follow up. If they stay disengaged, say a warm goodbye and call connect_to_lead_capture(confirm=false).

{lang_hint(self.userdata.language)}"""

    # ══════════════════════════════════════════════════════════════════════════
    # HANDOFF TO LEAD CAPTURE
    # ══════════════════════════════════════════════════════════════════════════

    @function_tool
    async def connect_to_lead_capture(self, context: RunContext_T, confirm: bool):
        """
        Call this when the visitor has been qualified and you offer to collect their contact details for follow-up.
        confirm (required): true if the visitor agrees, false if they decline.
        """
        logger.info(f"connect_to_lead_capture: confirm={confirm}, intent={self.userdata.intent_score}")

        # Guard: EngageIQ must be presented before lead capture
        if confirm and not self.userdata.engageiq_presented:
            return f"You haven't presented EngageIQ yet. First call present_engageiq to show the visitor what EngageIQ does — personalize it to their role or business challenge. The visitor needs to understand the product before they'd share their contact info. {lang_hint(self.userdata.language)}"

        if confirm:
            self.userdata.qualification_started = True

            # Clean frontend (remove product images) before handoff
            try:
                await self.room.local_participant.send_text(
                    json.dumps({"clean": True}), topic="clean"
                )
                logger.info("Sent clean topic before LeadCaptureAgent handoff")
            except Exception as e:
                logger.error(f"Failed to send clean topic: {e}")

            from agents.lead_capture_agents import LeadCaptureAgent
            from prompt.workflow import build_lead_capture_prompt
            # Return just the agent — no tuple message, so the main agent
            # stays silent and LeadCaptureAgent speaks via on_enter()
            base = build_lead_capture_prompt()
            instructions = build_prompt_with_language(base, self.userdata.language)
            return LeadCaptureAgent(
                instructions=instructions,
                room=self.room,
                chat_ctx=self.session.history,
                userdata=self.userdata,
            )
        else:
            # M7: Let on_shutdown handle save/webhook — visitor may continue talking
            hint = lang_hint(self.userdata.language)
            return f"Say a warm, brief goodbye. Wish them a great time at EuroShop. {hint}"

