"""
Main conversational agent (EngageIQAssistant) — handles greeting, product presentation,
simplified qualification, and intent scoring.

This agent IS the demo: visitors experience EngageIQ by talking to it.
"""

import asyncio
import json
import logging
from typing import AsyncIterable
from livekit.agents import Agent, function_tool, ModelSettings

from core.session_state import UserData, RunContext_T
from config.products import PRODUCTS, get_role_hook
from prompt.main_agent import build_main_prompt, build_greeting, build_engageiq_presentation
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


class EngageIQAssistant(Agent):
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
        if userdata:
            self.userdata = userdata
        self.first_message = first_message
        self.room = room
        self._product_data = _build_product_data_for_prompt()

        prompt = build_main_prompt(self.userdata.language, self._product_data)

        super().__init__(
            instructions=prompt,
        )

    async def on_enter(self):
        logger.info(f"EngageIQAssistant on_enter (first={self.first_message}, lang={self.userdata.language})")

        if self.first_message:
            try:
                greeting = build_greeting(self.userdata.language)
                await self.session.generate_reply(instructions=greeting)
            except Exception as e:
                logger.error(f"Greeting failed: {e}")
        else:
            try:
                return await super().on_enter()
            except Exception as e:
                logger.error(f"on_enter failed: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # ROLE DETECTION
    # ══════════════════════════════════════════════════════════════════════════

    @function_tool
    async def detect_visitor_role(self, context: RunContext_T, role: str):
        """
        Call this early in the conversation to detect and store the visitor's role.
        role (required): The visitor's job title, role, or what they do at their company.
        """
        logger.info(f"Detected visitor role: {role}")
        self.userdata.visitor_role = role.strip() if role else None
        return "Role noted. Continue the conversation naturally — when the moment feels right, present EngageIQ by calling present_engageiq."

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
        return "Summary saved. Proceed with the next step in the conversation."

    # ══════════════════════════════════════════════════════════════════════════
    # SESSION RESTART
    # ══════════════════════════════════════════════════════════════════════════

    @function_tool
    async def restart_session(self, context: RunContext_T):
        """
        Call this when the visitor says "New Conversation" or wants to start fresh.
        """
        logger.info("Restarting session from main agent")
        # Restart with fresh UserData (keep language)
        lang = self.userdata.language
        return EngageIQAssistant(
            room=self.room,
            userdata=UserData(language=lang),
            first_message=True,
        )

    # ══════════════════════════════════════════════════════════════════════════
    # PRODUCT PRESENTATION
    # ══════════════════════════════════════════════════════════════════════════

    @function_tool
    async def present_engageiq(self, context: RunContext_T):
        """
        Call this after detecting visitor role to present EngageIQ with personalized value proposition.
        """
        logger.info(f"Presenting EngageIQ to visitor with role: {self.userdata.visitor_role}")

        # Intent: visitor engaged with greeting
        self.userdata.intent_score += 2
        logger.info(f"Intent score after presentation: {self.userdata.intent_score}")

        # Send EngageIQ + client images to frontend
        self._send_product_to_frontend("engageiq")

        # Use role-based presentation
        presentation = build_engageiq_presentation(
            self.userdata.language,
            self._product_data,
            visitor_role=self.userdata.visitor_role
        )
        if presentation:
            return presentation

        return "Present EngageIQ and mention clients like CORE and DFKI who use it. Personalize to their role."

    def _send_product_to_frontend(self, product_key: str) -> None:
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
            asyncio.create_task(
                self.room.local_participant.send_text(
                    json.dumps(payload),
                    topic="products",
                )
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
        return "Challenge noted. Now call check_intent_and_proceed to determine the next step based on visitor engagement."

    # ══════════════════════════════════════════════════════════════════════════
    # INTENT CHECK & RE-ENGAGEMENT
    # ══════════════════════════════════════════════════════════════════════════

    @function_tool
    async def check_intent_and_proceed(self, context: RunContext_T):
        """
        Call this AFTER collecting the visitor's challenge.
        Checks visitor engagement level and returns instructions for next step.
        """
        score = self.userdata.intent_score
        logger.info(f"Checking intent score: {score}/5")

        if score >= 3:
            # Send YES/NO contact sharing buttons to frontend
            try:
                await self.room.local_participant.send_text(
                    json.dumps({"share_contact_yes": "Yes", "share_contact_no": "No"}),
                    topic="trigger",
                )
                logger.info("Sent contact sharing buttons to frontend")
            except Exception as e:
                logger.error(f"Failed to send contact sharing buttons: {e}")

            # Good signal - have more conversation before asking for contact
            return """GOOD_SIGNAL: The visitor seems interested. Before asking for contact:

1. Acknowledge their challenge briefly with empathy
2. Share 1-2 specific ways EngageIQ can help their business engage customers better (e.g., "For someone in your role, this means you could see which visitors are actually interested, not just who clicks")
3. Then naturally ask if they'd like our team to contact them

YES/NO buttons have been sent to the frontend. The visitor can click them or say Yes/No verbally.
If they say 'Yes' (verbally or button), call connect_to_lead_capture with confirm=true.
If they say 'No' (verbally or button), call connect_to_lead_capture with confirm=false."""
        else:
            # Continue conversation - don't rush
            return f"""CONTINUE_CONVERSATION: Score is {score}/5. Don't rush to ask for contact.

Try to learn more about their situation:
- Ask what would make visitor engagement valuable for their business
- Share a brief example of how EngageIQ helped a similar company
- Keep the conversation natural, not salesy

If they show more interest, explain how EngageIQ helps engage customers and offer to have our team contact them. If they remain disengaged, say a warm goodbye and call connect_to_lead_capture with confirm=false."""

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
            return LeadCaptureAgent(
                instructions=build_lead_capture_prompt(self.userdata.language),
                room=self.room,
                chat_ctx=self.chat_ctx,
                userdata=self.userdata,
            )
        else:
            # Save conversation history and send webhook immediately when declining
            try:
                chat_history = self._chat_ctx.items if hasattr(self, "_chat_ctx") else []
                save_conversation_to_file(chat_history, self.userdata)

                # Send webhook
                session_id = self.userdata.session_id or "unknown"
                await send_session_webhook(session_id, chat_history, self.userdata)

                self.userdata._history_saved = True
                logger.info("Conversation saved and webhook sent after visitor declined contact")
            except Exception as e:
                logger.error(f"Failed to save conversation on decline: {e}")

            return "No problem at all. Say a warm goodbye in the visitor's language, wish them a great rest of EuroShop, and mention the team is at the booth if they have questions later."

    # ══════════════════════════════════════════════════════════════════════════
    # TRANSCRIPTION — streams agent text to frontend
    # ══════════════════════════════════════════════════════════════════════════

    async def transcription_node(self, text: AsyncIterable[str], model_settings: ModelSettings) -> AsyncIterable[str]:
        agent_response = ""
        async for delta in text:
            agent_response += delta
            yield delta

        # Send text to frontend
        try:
            await self.room.local_participant.send_text(
                json.dumps({"agent_response": agent_response}),
                topic="message",
            )
        except Exception as e:
            logger.error(f"Failed to send transcription: {e}")
