"""
Language switching utility for mid-conversation language changes.

Receives language updates from frontend via LiveKit data channel (topic: "language").
Dynamically updates the active agent's instructions to speak the new language.

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
    from livekit.agents import AgentSession
    from livekit import rtc

logger = logging.getLogger(__name__)


# Confirmation phrases for language switch (brief, natural)
_LANGUAGE_CONFIRMATIONS = {
    "de": "Selbstverstaendlich, ich spreche jetzt Deutsch.",
    "en": "Of course, I'll speak English now.",
    "fr": "Bien sur, je parle francais maintenant.",
    "es": "Por supuesto, ahora hablo espanol.",
    "it": "Certo, ora parlo italiano.",
    "tr": "Elbette, simdi Turkce konusuyorum.",
    "ar": "Tabaan, al-ana atakallam bi-l-arabiyya.",
    "zh": "Hao de, xianzai wo shuo zhongwen.",
    "ja": "Hai, nihongo de hanashimasu.",
    "pt": "Claro, agora falo portugues.",
}


class LanguageSwitchHandler:
    """Handles mid-conversation language switching for voice agents.

    Listens for data packets on the "language" topic from the frontend,
    updates the agent's instructions dynamically, and optionally generates
    a confirmation reply in the new language.
    """

    def __init__(self, session: "AgentSession", room: "rtc.Room"):
        """Initialize the language switch handler.

        Args:
            session: The AgentSession managing the conversation
            room: The LiveKit room for data reception
        """
        self._session = session
        self._room = room

    def setup_listener(self) -> None:
        """Register the data_received listener for language changes."""
        @self._room.on("data_received")
        def on_data_received(data: "rtc.DataPacket"):
            # Only process "language" topic
            if data.topic != "language":
                return

            try:
                # Decode payload
                payload = data.data.decode("utf-8") if isinstance(data.data, bytes) else data.data
                parsed = json.loads(payload)

                # Extract language code (support multiple key names)
                new_language = parsed.get("language") or parsed.get("lang") or parsed.get("code")

                if not new_language:
                    logger.warning("Language switch payload missing language code")
                    return

                # Validate language code
                from config.languages import SUPPORTED_LANGUAGES
                if new_language not in SUPPORTED_LANGUAGES:
                    logger.warning(f"Unsupported language code: {new_language}")
                    return

                # Process the language change asynchronously
                asyncio.create_task(self._handle_language_change(new_language))

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse language payload: {e}")
            except Exception as e:
                logger.error(f"Error processing language change: {e}")

    async def _handle_language_change(self, new_language: str) -> None:
        """Execute the language switch.

        Args:
            new_language: The new language code (e.g., "de", "en")
        """
        userdata = self._session.userdata
        old_language = userdata.language

        if old_language == new_language:
            logger.info(f"Language already set to {new_language}, skipping")
            return

        logger.info(f"Language switch requested: {old_language} -> {new_language}")

        # Update userdata
        userdata.language = new_language

        # Get current agent
        current_agent = self._session.current_agent
        if not current_agent:
            logger.warning("No current agent to update instructions")
            return

        # Build new instructions based on agent type
        new_instructions = self._build_instructions_for_agent(current_agent, new_language)

        if not new_instructions:
            logger.warning(f"Could not build instructions for agent type: {type(current_agent).__name__}")
            return

        try:
            # Update the agent's instructions (this also updates the realtime session)
            await current_agent.update_instructions(new_instructions)
            logger.info(f"Updated instructions for {current_agent.__class__.__name__} to language: {new_language}")

            # Generate a brief confirmation in the new language
            confirmation = self._get_switch_confirmation(new_language)
            await self._session.generate_reply(instructions=confirmation)
            logger.info(f"Language switch complete: {old_language} -> {new_language}")

        except Exception as e:
            logger.error(f"Failed to update agent instructions: {e}")

    def _build_instructions_for_agent(self, agent, language: str) -> str | None:
        """Build language-appropriate instructions for the given agent.

        Args:
            agent: The current agent instance
            language: The target language code

        Returns:
            The new instructions string, or None if agent type is unknown
        """
        from prompt.main_agent import build_main_prompt
        from prompt.workflow import build_lead_capture_prompt
        from agents.main_agent import EngageIQAssistant
        from agents.lead_capture_agents import LeadCaptureAgent

        if isinstance(agent, EngageIQAssistant):
            # Rebuild main agent prompt with product data
            product_data = getattr(agent, "_product_data", {})
            return build_main_prompt(language, product_data)

        elif isinstance(agent, LeadCaptureAgent):
            # Rebuild lead capture prompt
            return build_lead_capture_prompt(language)

        else:
            logger.warning(f"Unknown agent type: {type(agent).__name__}")
            return None

    def _get_switch_confirmation(self, language: str) -> str:
        """Generate a brief confirmation message in the new language.

        Args:
            language: The target language code

        Returns:
            A brief confirmation instruction for generate_reply
        """
        confirmation = _LANGUAGE_CONFIRMATIONS.get(language, _LANGUAGE_CONFIRMATIONS["en"])
        return f"Say exactly this phrase and nothing else: \"{confirmation}\""
