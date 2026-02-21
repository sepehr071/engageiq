"""
Main conversational agent (EngageIQAssistant) — handles greeting, product presentation,
lead capture, and consent. Single agent — no handoff.

This agent IS the demo: visitors experience EngageIQ by talking to it.
"""

import asyncio
import json
import logging
from livekit.agents import function_tool
from agents.base import BaseAgent

from core.session_state import UserData, RunContext_T
from core.lead_storage import save_lead
from config.products import PRODUCTS
from prompt.main_agent import build_main_prompt, build_greeting
from prompt.language import build_prompt_with_language, lang_hint
from config.languages import get_language_config, get_button_labels
from utils.history import save_conversation_to_file
from utils.webhook import send_session_webhook
from utils.smtp import is_valid_email_syntax, send_lead_notification

logger = logging.getLogger(__name__)


def _build_product_data_for_prompt() -> dict:
    """Transform config PRODUCTS into the format expected by prompt builders."""
    result = {}
    for key, p in PRODUCTS.items():
        pricing = p.get("pricing", {})
        pilot_str = pricing.get("structure", "Contact sales")
        if pricing.get("guarantee"):
            pilot_str += f" ({pricing['guarantee']})"

        result[key] = {
            "name": p["name"],
            "tagline": p.get("subtitle", ""),
            "capabilities": p.get("capabilities", []),
            "installation": p.get("installation", ""),
            "pilot_pricing": pilot_str,
            "client_details": p.get("clients", []),
        }
    return result


class EngageIQAssistant(BaseAgent):
    """Main EuroShop booth agent — single agent, no handoff.

    Handles:
    - Greeting in the visitor's language
    - EngageIQ product presentation with client examples
    - Persistent contact offering (after 2nd user message)
    - Inline lead capture (contact collection + consent)
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

    INVALID_ROLES = {"user", "visitor", "person", "customer", "guest", "attendee", "participant", "man", "woman", "someone", "nobody", "human"}

    @function_tool
    async def detect_visitor_role(self, context: RunContext_T, role: str):
        """
        Store the visitor's professional job title or role.
        ONLY call this when the visitor explicitly mentions their job title or business function.

        role (required): A professional job title or business role.
            GOOD examples: "Marketing Director", "CEO", "Sales Manager", "Head of E-Commerce"
            BAD — NEVER use: person's names, greetings, "just looking", "visitor", "user", "customer", "guest"

        If the visitor only shares their name, do NOT call this tool. Wait for an actual job title.
        """
        cleaned = role.strip().lower() if role else ""
        if not cleaned or cleaned in self.INVALID_ROLES:
            logger.info(f"Rejected invalid role: {role}")
            hint = lang_hint(self.userdata.language)
            return f"(INTERNAL) That is not a professional role. Do NOT store it. Wait until the visitor mentions an actual job title. {hint}"

        logger.info(f"Detected visitor role: {role}")
        self.userdata.visitor_role = role.strip()
        hint = lang_hint(self.userdata.language)
        return f"(INTERNAL) Continue the conversation naturally. {hint}"

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
        return f"(INTERNAL) Continue the conversation. {hint}"

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
            return f"(INTERNAL) Continue discussing the client naturally. {hint}"

        # Skip if already shown
        if key in self.userdata.clients_shown:
            return f"(INTERNAL) Continue discussing the client naturally. {hint}"

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

        return f"(INTERNAL) Continue discussing the client naturally. {hint}"

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
            return f"(INTERNAL) You already presented EngageIQ. Do NOT present again. Continue — ask about their challenge or check engagement. {hint}"

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
            return f"(INTERNAL) Present EngageIQ briefly — the images on screen show real deployments (CORE, DFKI). Connect to their {role} context. 1-2 sentences. {hint}"
        else:
            return f"(INTERNAL) Present EngageIQ briefly — the images on screen show real deployments: CORE and DFKI. 1-2 sentences. {hint}"

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
        Call this when the visitor describes a challenge with customer demand or engagement.
        challenge (required): A brief summary of the visitor's stated challenge.
        """
        logger.info(f"Challenge collected: {challenge}")
        self.userdata.biggest_challenge = challenge
        self.userdata.intent_score += 1
        logger.info(f"Intent score after challenge: {self.userdata.intent_score}")
        hint = lang_hint(self.userdata.language)
        return f"(INTERNAL) Continue the conversation naturally. {hint}"

    # ══════════════════════════════════════════════════════════════════════════
    # LEAD CAPTURE (inline — no handoff)
    # ══════════════════════════════════════════════════════════════════════════

    @function_tool
    async def store_partial_contact_info(
        self,
        context: RunContext_T,
        name: str,
        email: str,
        company: str = "",
        role: str = "",
        phone: str = "",
    ):
        """
        Call this when the visitor provides their contact information (BEFORE asking consent).
        Stores info temporarily while you ask for consent.
        name (required): The visitor's name.
        email (required): The visitor's email address.
        company: The visitor's company name.
        role: The visitor's job title or role.
        phone: The visitor's phone number (optional).
        """
        logger.info(f"Partial contact info: name={name}, email={email}, company={company}")

        # Validate email
        if not is_valid_email_syntax(email):
            logger.info(f"Invalid email: {email}")
            return f"(INTERNAL) That email doesn't seem right. Ask the visitor to double-check it. {lang_hint(self.userdata.language)}"

        # Store as PARTIAL contact info (not yet finalized)
        self.userdata.partial_name = name.strip()
        self.userdata.partial_email = email.lower().strip()
        self.userdata.partial_company = company.strip() if company else None
        self.userdata.partial_role_title = role.strip() if role else None
        self.userdata.partial_phone = phone.strip() if phone else None

        # Intent: sharing contact = strong signal
        self.userdata.intent_score += 2
        logger.info(f"Intent score after contact info: {self.userdata.intent_score}")

        # Send YES/NO consent buttons to frontend
        labels = get_button_labels(self.userdata.language)
        try:
            await self.room.local_participant.send_text(
                json.dumps({labels["consent_yes"]: labels["consent_yes"], labels["consent_no"]: labels["consent_no"]}),
                topic="trigger",
            )
            logger.info("Sent consent buttons to frontend")
        except Exception as e:
            logger.error(f"Failed to send consent buttons: {e}")

        # Send webhook immediately with partial lead data (in case session drops)
        try:
            chat_history = self.chat_ctx.items
            session_id = self.userdata.session_id or "unknown"
            await send_session_webhook(session_id, chat_history, self.userdata)
            logger.info("Partial lead webhook sent (email collected)")
        except Exception as e:
            logger.error(f"Partial lead webhook failed: {e}")

        hint = lang_hint(self.userdata.language)
        return f"(INTERNAL) Now ask: 'May we use your contact information to follow up?' {hint}"

    @function_tool
    async def confirm_consent(self, context: RunContext_T, consent: bool):
        """
        Call this after asking for consent to use the visitor's contact information.
        consent (required): true if visitor agrees, false if they decline.
        """
        logger.info(f"Consent response: {consent}")
        self.userdata.consent_given = consent

        if consent:
            # Move partial data to final contact fields
            self.userdata.name = self.userdata.partial_name
            self.userdata.email = self.userdata.partial_email
            self.userdata.company = self.userdata.partial_company
            self.userdata.role_title = self.userdata.partial_role_title
            self.userdata.phone = self.userdata.partial_phone
            self.userdata.lead_captured = True

            # Save lead as JSON
            try:
                filepath = save_lead(self.userdata)
                logger.info(f"Lead saved to {filepath}")
            except Exception as e:
                logger.error(f"Failed to save lead JSON: {e}")

            # Send email notification (non-blocking via executor)
            try:
                loop = asyncio.get_running_loop()
                success = await loop.run_in_executor(None, lambda: send_lead_notification(
                    name=self.userdata.name or "",
                    company=self.userdata.company or "",
                    role_title=self.userdata.role_title or "",
                    email=self.userdata.email or "",
                    phone=self.userdata.phone or "",
                    intent_score=self.userdata.intent_score,
                    biggest_challenge=self.userdata.biggest_challenge or "",
                    campaign_source=self.userdata.campaign_source or "",
                    conversation_summary=self.userdata.conversation_summary or "",
                ))
                if success:
                    logger.info("Lead email sent successfully")
                else:
                    logger.error("Lead email send failed")
            except Exception as e:
                logger.error(f"Lead email crashed: {e}")

            # Send webhook with captured lead data
            try:
                chat_history = self.chat_ctx.items
                session_id = self.userdata.session_id or "unknown"
                await send_session_webhook(session_id, chat_history, self.userdata)
                logger.info("Lead webhook sent successfully")
            except Exception as e:
                logger.error(f"Lead webhook failed: {e}")

            # Mark history as saved to prevent duplicate on shutdown
            self.userdata._history_saved = True

            # Send "new conversation" button to frontend
            labels = get_button_labels(self.userdata.language)
            try:
                await self.room.local_participant.send_text(
                    json.dumps({labels["new_conversation"]: labels["new_conversation"]}),
                    topic="trigger",
                )
            except Exception as e:
                logger.error(f"New conversation button failed: {e}")

            hint = lang_hint(self.userdata.language)
            return f"(INTERNAL) Thank them warmly and say goodbye. Mention the team will follow up. {hint}"

        else:
            # Send webhook FIRST while data is still available
            try:
                chat_history = self.chat_ctx.items
                session_id = self.userdata.session_id or "unknown"
                await send_session_webhook(session_id, chat_history, self.userdata)
            except Exception as e:
                logger.error(f"Webhook failed: {e}")

            # THEN clear partial data (visitor declined)
            self.userdata.partial_name = None
            self.userdata.partial_email = None
            self.userdata.partial_company = None
            self.userdata.partial_role_title = None
            self.userdata.partial_phone = None
            logger.info("Partial contact info discarded (visitor declined consent)")

            # Mark history as saved
            self.userdata._history_saved = True

            # Send "new conversation" button
            labels = get_button_labels(self.userdata.language)
            try:
                await self.room.local_participant.send_text(
                    json.dumps({labels["new_conversation"]: labels["new_conversation"]}),
                    topic="trigger",
                )
            except Exception as e:
                logger.error(f"New conversation button failed: {e}")

            hint = lang_hint(self.userdata.language)
            return f"(INTERNAL) Respect their choice — say a warm goodbye, no pressure. {hint}"

