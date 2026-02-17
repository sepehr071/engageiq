"""
Lead capture agent — collects contact info, saves lead, sends notification, closes conversation.
This is the only sub-agent. Everything after qualification handoff happens here.

Merged responsibilities: LeadCapture + Notification + Close (previously 3 separate agents).
"""

import json
import logging
from livekit.agents import function_tool
from agents.base import BaseAgent
from core.session_state import UserData, RunContext_T
from core.lead_storage import save_lead
from utils.smtp import is_valid_email_syntax, send_lead_notification
from utils.history import save_conversation_to_file
from utils.webhook import send_session_webhook

logger = logging.getLogger(__name__)


class LeadCaptureAgent(BaseAgent):
    """Collects visitor contact information, sends notifications, and closes the conversation."""

    async def on_enter(self):
        """Speak immediately on entry — visitor already agreed, go straight to collecting."""
        logger.info("LeadCaptureAgent on_enter")
        await self.session.generate_reply(
            instructions="The visitor already agreed to share their contact details. Thank them briefly and ask for their name and email to get started. Be warm and concise — one sentence."
        )

    @function_tool
    async def save_conversation_summary(self, context: RunContext_T, summary: str):
        """
        Call this to save a brief summary of the conversation before collecting contact info or saying goodbye.
        summary (required): A 1-2 sentence summary of what the visitor is looking for and their interest level.
        """
        logger.info(f"Conversation summary: {summary}")
        self.userdata.conversation_summary = summary.strip()
        return "Summary saved. Continue with the conversation."

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
            return "That email doesn't seem right. Ask the visitor to double-check it."

        # Store as PARTIAL contact info (not yet finalized)
        self.userdata.partial_name = name.strip()
        self.userdata.partial_email = email.lower().strip()
        self.userdata.partial_company = company.strip() if company else None
        self.userdata.partial_role_title = role.strip() if role else None
        self.userdata.partial_phone = phone.strip() if phone else None

        # Send YES/NO consent buttons to frontend
        try:
            await self.room.local_participant.send_text(
                json.dumps({"consent_yes": "Yes", "consent_no": "No"}),
                topic="trigger",
            )
            logger.info("Sent consent buttons to frontend")
        except Exception as e:
            logger.error(f"Failed to send consent buttons: {e}")

        # Return instruction to ask for consent
        return "Contact details received. Now ask for explicit consent: 'May we use your contact information to reach out to you about EngageIQ?' The visitor can click Yes or No buttons, or say it verbally. If they say 'Yes', call confirm_consent with consent=true. If they say 'No', call confirm_consent with consent=false."

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

            # Send email notification
            try:
                success = send_lead_notification(
                    name=self.userdata.name or "",
                    company=self.userdata.company or "",
                    role_title=self.userdata.role_title or "",
                    email=self.userdata.email or "",
                    phone=self.userdata.phone or "",
                    intent_score=self.userdata.intent_score,
                    biggest_challenge=self.userdata.biggest_challenge or "",
                    campaign_source=self.userdata.campaign_source or "",
                    conversation_summary=self.userdata.conversation_summary or "",
                )
                if success:
                    logger.info("Lead email sent successfully")
                else:
                    logger.error("Lead email send failed")
            except Exception as e:
                logger.error(f"Lead email crashed: {e}")

            # Send webhook with captured lead data
            try:
                chat_history = self._chat_ctx.items if hasattr(self, "_chat_ctx") else []
                session_id = self.userdata.session_id or "unknown"
                await send_session_webhook(session_id, chat_history, self.userdata)
                logger.info("Lead webhook sent successfully")
            except Exception as e:
                logger.error(f"Lead webhook failed: {e}")

            # Mark history as saved to prevent duplicate on shutdown
            self.userdata._history_saved = True

            # Send "new conversation" button to frontend
            try:
                await self.room.local_participant.send_text(
                    json.dumps({"new_conversation": "New Conversation"}),
                    topic="trigger",
                )
            except Exception as e:
                logger.error(f"New conversation button failed: {e}")

            # Return confirmation — LLM will generate a natural goodbye
            return "Contact details saved with consent. Thank the visitor warmly, tell them the team will be in touch soon, and wish them a great rest of EuroShop."

        else:
            # Clear partial data (visitor declined)
            self.userdata.partial_name = None
            self.userdata.partial_email = None
            self.userdata.partial_company = None
            self.userdata.partial_role_title = None
            self.userdata.partial_phone = None
            logger.info("Partial contact info discarded (visitor declined consent)")

            # Send webhook (with partial_contact_info flag for analytics)
            try:
                chat_history = self._chat_ctx.items if hasattr(self, "_chat_ctx") else []
                session_id = self.userdata.session_id or "unknown"
                await send_session_webhook(session_id, chat_history, self.userdata)
            except Exception as e:
                logger.error(f"Webhook failed: {e}")

            # Mark history as saved
            self.userdata._history_saved = True

            # Send "new conversation" button
            try:
                await self.room.local_participant.send_text(
                    json.dumps({"new_conversation": "New Conversation"}),
                    topic="trigger",
                )
            except Exception as e:
                logger.error(f"New conversation button failed: {e}")

            return "Visitor declined consent. Data has been discarded. Say a warm goodbye and wish them a great rest of EuroShop."

    @function_tool
    async def visitor_declines_contact(self, context: RunContext_T):
        """
        Call this when the visitor declines to share their contact information.
        """
        logger.info("Visitor declined contact info")

        # Send "new conversation" button
        try:
            await self.room.local_participant.send_text(
                json.dumps({"new_conversation": "New Conversation"}),
                topic="trigger",
            )
        except Exception as e:
            logger.error(f"New conversation button failed: {e}")

        # Return farewell — LLM will generate a natural goodbye
        return "No problem at all. Say a warm goodbye, wish them a great rest of EuroShop, and mention the team is at the booth if they have questions later."

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
            chat_history = self._chat_ctx.items if hasattr(self, "_chat_ctx") else []
            save_conversation_to_file(chat_history, self.userdata)

            # Send webhook
            session_id = self.userdata.session_id or "unknown"
            await send_session_webhook(session_id, chat_history, self.userdata)

            self.userdata._history_saved = True
            logger.info("Conversation saved and webhook sent before restart")
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")

        # Restart with fresh UserData (keep language)
        from agents.main_agent import EngageIQAssistant
        lang = self.userdata.language
        return EngageIQAssistant(
            room=self.room,
            userdata=UserData(language=lang),
            first_message=True,
        )
