"""
Base agent — shared init and transcription for all sub-agents.
Injects base prompt and streams text to frontend.

Adapted from Berta's agents/base.py — simplified for EngageIQ (no car-specific logic).
LLM is provided by AgentSession, not by individual agents.
"""

import json
import asyncio
import logging
from typing import AsyncIterable
from livekit.agents import Agent, ModelSettings
from core.session_state import UserData

logger = logging.getLogger(__name__)

REPLY_MAX_RETRIES = 3
REPLY_BACKOFF = 1.0

PATIENCE_FALLBACK = "One moment please..."


async def safe_generate_reply(session, room, instructions: str, retries: int = REPLY_MAX_RETRIES) -> bool:
    """Retry session.generate_reply up to `retries` times with backoff.
    On total failure, sends a polite fallback text to the frontend.
    Returns True on success, False on total failure.
    """
    for attempt in range(retries):
        try:
            await session.generate_reply(instructions=instructions)
            return True
        except Exception as e:
            logger.warning(f"generate_reply attempt {attempt + 1}/{retries} failed: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(REPLY_BACKOFF * (attempt + 1))

    logger.error(f"generate_reply failed after {retries} attempts")
    try:
        await room.local_participant.send_text(
            json.dumps({"agent_response": PATIENCE_FALLBACK}),
            topic="message",
        )
    except Exception:
        pass
    return False


class BaseAgent(Agent):
    """Shared base for all EngageIQ sub-agents.

    Provides:
    - Safe reply helper with retry + fallback
    - Transcription streaming to frontend via room topic "message"

    LLM is inherited from the AgentSession — agents only provide instructions.
    """

    def __init__(
        self,
        instructions: str,
        room,
        userdata: UserData | None = None,
        chat_ctx=None,
    ) -> None:
        logger.info(f"Initializing {self.__class__.__name__}")
        if userdata:
            self.userdata = userdata
        self.room = room

        super().__init__(
            instructions=instructions,
            chat_ctx=chat_ctx,
        )

    async def _safe_reply(self, instructions: str) -> bool:
        """Convenience wrapper — calls safe_generate_reply with this agent's session/room."""
        return await safe_generate_reply(self.session, self.room, instructions)

    async def transcription_node(self, text: AsyncIterable[str], model_settings: ModelSettings) -> AsyncIterable[str]:
        agent_response = ""
        async for delta in text:
            agent_response += delta
            yield delta

        try:
            await self.room.local_participant.send_text(
                json.dumps({"agent_response": agent_response}),
                topic="message",
            )
        except Exception as e:
            logger.error(f"Failed to send transcription to frontend: {e}")
