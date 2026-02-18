"""
Entry point for the EngageIQ LiveKit voice agent.
Connects to LiveKit room, reads participant attributes (language, campaign source),
and starts the main conversational agent.

No Flask subprocess needed — all product knowledge is in the prompts.
"""

from dotenv import load_dotenv

load_dotenv()

from livekit import agents
from livekit.agents import AgentSession, room_io
from livekit.agents.voice.room_io import RoomOptions
from livekit.plugins import openai
# Note: noise_cancellation.BVC() requires LiveKit Cloud paid plan
# from livekit.plugins import noise_cancellation
from core.session_state import UserData
from agents.main_agent import EngageIQAssistant
from utils.history import save_conversation_to_file
from utils.webhook import send_session_webhook
from config.settings import RT_MODEL, LLM_TEMPERATURE
from config import DEFAULT_LANGUAGE
import asyncio
import json
import logging
import os
import re
from datetime import datetime
from config.settings import LOGS_DIR

# ══════════════════════════════════════════════════════════════════════════════
# LOGGING
# ══════════════════════════════════════════════════════════════════════════════

if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(LOGS_DIR, f"app_{timestamp}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# for noisy in ["httpx", "httpcore", "openai", "livekit.agents", "urllib3", "asyncio", "livekit"]:
#     logging.getLogger(noisy).setLevel(logging.WARNING)


# ══════════════════════════════════════════════════════════════════════════════
# TRANSCRIPT EMAIL EXTRACTION (safety net for sudden session close)
# ══════════════════════════════════════════════════════════════════════════════

_EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')


def _extract_contact_from_transcript(chat_messages, userdata) -> None:
    """Extract email from transcript if not already stored in userdata.

    Safety net for sudden session close — the visitor may have said their
    email but the LLM hadn't yet called store_partial_contact_info.
    """
    if userdata.email or userdata.partial_email:
        return

    from utils.history import normalize_messages
    from utils.smtp import is_valid_email_syntax

    for msg in normalize_messages(chat_messages):
        if msg["role"] != "user":
            continue
        match = _EMAIL_RE.search(msg["message"])
        if match and is_valid_email_syntax(match.group(0)):
            userdata.partial_email = match.group(0).lower()
            logger.info(f"Extracted email from transcript on shutdown: {userdata.partial_email}")
            break


# ══════════════════════════════════════════════════════════════════════════════
# ENTRYPOINT
# ══════════════════════════════════════════════════════════════════════════════


async def entrypoint(ctx: agents.JobContext):
    """LiveKit agent entrypoint — called when a participant joins the room."""

    # Connect to room and wait for visitor (needed to read language attribute)
    await ctx.connect(auto_subscribe=agents.AutoSubscribe.AUDIO_ONLY)
    participant = await ctx.wait_for_participant()

    # Read language from participant attributes (set by frontend dropdown)
    # In console mode, participant is a MagicMock — .get() returns a mock, not the default
    attrs = participant.attributes if isinstance(participant.attributes, dict) else {}
    language = attrs.get("user.language", DEFAULT_LANGUAGE)
    campaign_source = attrs.get("campaign_source", "euroshop_2026_qr")

    logger.info(f"Participant joined: identity={participant.identity}, language={language}, source={campaign_source}")

    # Create session state with session tracking
    user_data = UserData(
        language=language,
        campaign_source=campaign_source,
        session_id=participant.identity,
        session_start_time=datetime.now(),
    )

    # Create session with realtime model
    session = AgentSession[UserData](
        llm=openai.realtime.RealtimeModel(
            model=RT_MODEL,
            temperature=LLM_TEMPERATURE,
        ),
        userdata=user_data,
    )

    # Setup language switch handler for mid-conversation language changes
    from utils.language_switcher import LanguageSwitchHandler
    language_handler = LanguageSwitchHandler(session, ctx.room)
    language_handler.setup_listener()

    # Shutdown callback — save conversation history and send webhook
    async def on_shutdown():
        try:
            ud = session.userdata
            if ud and not ud._history_saved:
                # C2: current_agent raises RuntimeError if session isn't running
                chat_history = []
                try:
                    current_agent = session.current_agent
                    chat_history = current_agent.chat_ctx.items  # H8: use public API
                except RuntimeError:
                    pass

                # Fallback to session history if agent ctx was empty
                if not chat_history:
                    try:
                        chat_history = list(session.history.items)
                    except Exception:
                        chat_history = []

                # Safety net: extract email from transcript if not yet stored
                _extract_contact_from_transcript(chat_history, ud)

                # Save local history
                save_conversation_to_file(chat_history, ud)

                # Send webhook (will include partial contact info if present)
                session_id = ud.session_id or participant.identity
                await send_session_webhook(session_id, chat_history, ud)

                ud._history_saved = True

                # Log if partial data was captured but session ended before consent
                if ud.partial_name or ud.partial_email:
                    logger.warning(
                        f"Session ended with partial contact info (no consent): "
                        f"name={ud.partial_name}, email={ud.partial_email}"
                    )
                else:
                    logger.info("Conversation saved and webhook sent on session shutdown")
        except Exception as e:
            logger.error(f"Failed to save conversation on shutdown: {e}")

    ctx.add_shutdown_callback(on_shutdown)

    # Listen for language changes via participant attributes (backup for data channel)
    @ctx.room.on("participant_attributes_changed")
    def on_attributes_changed(changed_attrs: dict[str, str], p):
        if p == participant and "user.language" in changed_attrs:
            p_attrs = p.attributes if isinstance(p.attributes, dict) else {}
            new_lang = p_attrs.get("user.language", DEFAULT_LANGUAGE)
            asyncio.create_task(language_handler._handle_language_change(new_lang))

    # Start the main agent
    # Note: noise_cancellation.BVC() requires LiveKit Cloud paid plan
    # For now, we run without noise cancellation
    try:
        await session.start(
            room=ctx.room,
            room_options=RoomOptions(
                text_output=False,
                text_input=False,
            ),
            agent=EngageIQAssistant(
                room=ctx.room,
                userdata=user_data,
                first_message=True,
            ),
        )
    except Exception as e:
        logger.critical(f"Session start failed: {e}")
        try:
            from config.languages import get_fallback_message
            error_msg = get_fallback_message(language, "technical_error")
            await ctx.room.local_participant.send_text(
                json.dumps({"agent_response": error_msg}),
                topic="message",
            )
        except Exception:
            pass


if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(entrypoint_fnc=entrypoint),
    )
