"""
Language switching utility for mid-conversation language changes.

Receives language updates from frontend via LiveKit data channel (topic: "language").
Rebuilds the active agent's prompt for the new language and updates the realtime session.

Usage:
    from utils.language_switcher import LanguageSwitchHandler

    handler = LanguageSwitchHandler(session, room)
    handler.setup_listener()
"""

import asyncio
import json
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from livekit.agents import AgentSession, Agent
    from livekit import rtc

logger = logging.getLogger(__name__)


class LanguageSwitchHandler:
    """Handles mid-conversation language switching for voice agents.

    Listens for data packets on the "language" topic from the frontend,
    rebuilds the current agent's prompt for the new language using
    the appropriate prompt builder, and updates the realtime session silently.
    """

    def __init__(self, session: "AgentSession", room: "rtc.Room"):
        self._session = session
        self._room = room

    def setup_listener(self) -> None:
        """Register the data_received listener for language changes."""
        @self._room.on("data_received")
        def on_data_received(data: "rtc.DataPacket"):
            if data.topic != "language":
                return

            try:
                payload = data.data.decode("utf-8") if isinstance(data.data, bytes) else data.data
                parsed = json.loads(payload)

                new_language = parsed.get("language") or parsed.get("lang") or parsed.get("code")

                if not new_language:
                    logger.warning("Language switch payload missing language code")
                    return

                from config.languages import SUPPORTED_LANGUAGES
                if new_language not in SUPPORTED_LANGUAGES:
                    logger.warning(f"Unsupported language code: {new_language}")
                    return

                asyncio.create_task(self._handle_language_change(new_language))

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse language payload: {e}")
            except Exception as e:
                logger.error(f"Error processing language change: {e}")

    async def _handle_language_change(self, new_language: str) -> None:
        """Rebuild the current agent's prompt for the new language.

        Detects which agent is active (EngageIQAssistant or LeadCaptureAgent)
        and uses the appropriate prompt builder to generate a complete new prompt.
        This avoids conflicting language directives and works across handoffs.
        """
        userdata = self._session.userdata
        old_language = userdata.language

        if old_language == new_language:
            logger.info(f"Language already set to {new_language}, skipping")
            return

        logger.info(f"Language switch requested: {old_language} -> {new_language}")

        userdata.language = new_language

        current_agent = self._session.current_agent
        if not current_agent:
            logger.warning("No current agent to update instructions")
            return

        try:
            new_instructions = self._rebuild_prompt(current_agent, new_language)
            await current_agent.update_instructions(new_instructions)
            logger.info(f"Language switched: {old_language} -> {new_language}")

        except Exception as e:
            logger.error(f"Failed to update agent instructions: {e}")

    def _rebuild_prompt(self, agent: "Agent", language: str) -> str:
        """Rebuild the full prompt: native-language directive at TOP + English base.

        Detects agent type to use the correct base prompt builder,
        then prepends the language directive from prompt/language.py.
        """
        from agents.main_agent import EngageIQAssistant
        from agents.lead_capture_agents import LeadCaptureAgent
        from prompt.language import build_prompt_with_language

        if isinstance(agent, EngageIQAssistant):
            from prompt.main_agent import build_main_prompt
            base = build_main_prompt(agent._product_data)
            return build_prompt_with_language(base, language)

        if isinstance(agent, LeadCaptureAgent):
            from prompt.workflow import build_lead_capture_prompt
            base = build_lead_capture_prompt()
            return build_prompt_with_language(base, language)

        logger.warning(f"Unknown agent type: {type(agent).__name__}, keeping current instructions")
        return agent.instructions
