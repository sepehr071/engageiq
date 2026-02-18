"""
Language switching utility for mid-conversation language changes.

Receives language updates from frontend via LiveKit data channel (topic: "language").
Dynamically updates the active agent's instructions with a strong language directive.

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


class LanguageSwitchHandler:
    """Handles mid-conversation language switching for voice agents.

    Listens for data packets on the "language" topic from the frontend,
    prepends a strong language directive to the agent's ORIGINAL instructions,
    and updates the realtime session silently (no agent response).

    Important: Stores the original instructions on first switch to prevent
    accumulating multiple language directives on subsequent switches.
    """

    def __init__(self, session: "AgentSession", room: "rtc.Room"):
        """Initialize the language switch handler.

        Args:
            session: The AgentSession managing the conversation
            room: The LiveKit room for data reception
        """
        self._session = session
        self._room = room
        self._original_instructions: str | None = None  # Stores original, unmodified instructions

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
        """Execute the language switch silently.

        Stores the original instructions on first switch, then always prepends
        the new language directive to the ORIGINAL instructions (not the modified ones).
        This prevents accumulating multiple conflicting language directives.

        Args:
            new_language: The new language code (e.g., "de", "en")
        """
        userdata = self._session.userdata
        old_language = userdata.language

        if old_language == new_language:
            logger.info(f"Language already set to {new_language}, skipping")
            return

        logger.info(f"Language switch requested: {old_language} -> {new_language}")

        # Update userdata (persists across handoffs)
        userdata.language = new_language

        # Get current agent
        current_agent = self._session.current_agent
        if not current_agent:
            logger.warning("No current agent to update instructions")
            return

        try:
            # Store original instructions on FIRST switch only
            # This prevents accumulating multiple language directives
            if self._original_instructions is None:
                self._original_instructions = current_agent.instructions
                logger.info("Stored original instructions for language switching")

            # Build strong language override directive
            language_override = self._build_language_override(new_language)

            # Always prepend to ORIGINAL instructions (not current modified ones)
            # This ensures only ONE language directive is present at a time
            new_instructions = language_override + "\n\n" + self._original_instructions

            # Update the agent's instructions (this also updates the realtime session)
            await current_agent.update_instructions(new_instructions)
            logger.info(f"Language switched: {old_language} -> {new_language} (no agent response)")

        except Exception as e:
            logger.error(f"Failed to update agent instructions: {e}")

    def _build_language_override(self, language: str) -> str:
        """Build a language directive to prepend to instructions."""
        from prompt.language import get_language_directive
        return get_language_directive(language)
