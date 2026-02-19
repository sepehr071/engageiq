"""
Lead capture agent — collects contact info, saves lead, sends notification, closes conversation.
This is the only sub-agent. Everything after qualification handoff happens here.

Merged responsibilities: LeadCapture + Notification + Close (previously 3 separate agents).
"""

import asyncio
import json
import logging
from livekit.agents import function_tool
from agents.base import BaseAgent
from core.session_state import UserData, RunContext_T
from core.lead_storage import save_lead
from utils.smtp import is_valid_email_syntax, send_lead_notification
from utils.history import save_conversation_to_file
from utils.webhook import send_session_webhook
from prompt.language import lang_hint
from config.languages import get_language_config, get_button_labels

logger = logging.getLogger(__name__)


class LeadCaptureAgent(BaseAgent):
    """Collects visitor contact information, sends notifications, and closes the conversation."""

    async def on_enter(self):
        """Speak immediately on entry — visitor already agreed, go straight to collecting."""
        logger.info("LeadCaptureAgent on_enter")
        language = self.userdata.language
        lang_info = get_language_config(language)
        english_name = lang_info.get("english_name", "German")
        formality_note = lang_info.get("formality_note", "Use appropriate formality.")

        if language == "en":
            lang_instruction = "Respond in English."
        else:
            lang_instruction = f"Respond in {english_name}. {formality_note}"

        await self.session.generate_reply(
            instructions=f"The visitor already agreed to share their contact details. Thank them briefly and ask for their name and email to get started. Be warm and concise — one sentence. {lang_instruction}"
        )

    @function_tool
    async def save_conversation_summary(self, context: RunContext_T, summary: str):
        """
        Call this to save a brief summary of the conversation before collecting contact info or saying goodbye.
        summary (required): A 1-2 sentence summary of what the visitor is looking for and their interest level.
        """
        logger.info(f"Conversation summary: {summary}")
        self.userdata.conversation_summary = summary.strip()
        hint = lang_hint(self.userdata.language)
        return f"Summary saved (INTERNAL — do NOT speak it aloud). Now collect their contact details. {hint}"

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
            return f"That email doesn't seem right. Ask the visitor to double-check it. {lang_hint(self.userdata.language)}"

        # Store as PARTIAL contact info (not yet finalized)
        self.userdata.partial_name = name.strip()
        self.userdata.partial_email = email.lower().strip()
        self.userdata.partial_company = company.strip() if company else None
        self.userdata.partial_role_title = role.strip() if role else None
        self.userdata.partial_phone = phone.strip() if phone else None

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
        return f"Info received. Now ask: 'May we use your contact information to follow up?' YES/NO buttons are on screen. {hint}"

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

            # Send email notification (M9: non-blocking via executor)
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
            return f"Lead saved! Thank them warmly and say goodbye. Mention the team will follow up. {hint}"

        else:
            # M6: Send webhook FIRST while data is still available
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
            return f"Data discarded. Respect their choice — say a warm goodbye, no pressure. {hint}"

    @function_tool
    async def visitor_declines_contact(self, context: RunContext_T):
        """
        Call this when the visitor declines to share their contact information.
        """
        logger.info("Visitor declined contact info")

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
        return f"Say a warm goodbye. Wish them a great time at EuroShop. {hint}"

    @function_tool
    async def restart_session(self, context: RunContext_T):
        """
        Call this when the visitor says "New Conversation" or wants to start fresh.
        """
        logger.info("Restarting session")

        # Clean frontend
        try:
            await self.room.local_participant.send_text(
                json.dumps({"clean": True}), topic="clean"
            )
        except Exception as e:
            logger.error(f"Clean message failed: {e}")

        # Save conversation history and send webhook
        try:
            chat_history = self.chat_ctx.items
            save_conversation_to_file(chat_history, self.userdata)

            # Send webhook
            session_id = self.userdata.session_id or "unknown"
            await send_session_webhook(session_id, chat_history, self.userdata)

            self.userdata._history_saved = True
            logger.info("Conversation saved and webhook sent before restart")
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")

        # Restart with fresh UserData (keep language + campaign_source)
        from agents.main_agent import EngageIQAssistant
        lang = self.userdata.language
        source = self.userdata.campaign_source
        return EngageIQAssistant(
            room=self.room,
            userdata=UserData(language=lang, campaign_source=source),
            first_message=True,
        )
