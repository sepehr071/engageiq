"""
Webhook utility — send session data to external API endpoint.

Sends conversation transcripts, contact info, and metadata to the
Ayand AI logging endpoint for analytics and lead tracking.
"""

import logging
from datetime import datetime
from typing import List, Optional

import httpx

from config.settings import (
    WEBHOOK_URL,
    WEBHOOK_API_KEY,
    WEBHOOK_COMPANY_NAME,
    WEBHOOK_TIMEOUT,
    WEBHOOK_RETRIES,
)
from core.session_state import UserData
from utils.history import normalize_messages

logger = logging.getLogger(__name__)


async def send_session_webhook(
    session_id: str,
    chat_messages: List,
    userdata: UserData,
) -> bool:
    """Send session data to the webhook endpoint.

    Args:
        session_id: Unique identifier for this session (participant.identity).
        chat_messages: Raw chat message objects from _chat_ctx.items.
        userdata: UserData instance with all session data.

    Returns:
        True if webhook was sent successfully, False otherwise.
    """
    # Normalize transcript
    transcript = normalize_messages(chat_messages)

    # Skip if no conversation
    if not transcript:
        logger.info("No transcript to send to webhook (empty session)")
        return True

    # Calculate duration
    duration_seconds = 0
    if userdata.session_start_time:
        duration_seconds = int((datetime.now() - userdata.session_start_time).total_seconds())

    # Build contact info
    contact_info = {
        "name": userdata.name,
        "email": userdata.email,
        "phone": userdata.phone,
        "company": userdata.company,
        "role": userdata.role_title,
        # Additional fields for analytics
        "potentialScore": userdata.intent_score * 20,  # Convert 0-5 to 0-100 scale
        "conversationBrief": userdata.conversation_summary,
        "biggestChallenge": userdata.biggest_challenge,
        "visitorRole": userdata.visitor_role,
    }

    # Remove None values to keep payload clean
    contact_info = {k: v for k, v in contact_info.items() if v is not None}

    # Build session payload
    session_data = {
        "sessionId": session_id,
        "date": datetime.now().isoformat() + "Z",
        "durationSeconds": duration_seconds,
        "transcript": [
            {"role": msg["role"], "content": msg["message"]}
            for msg in transcript
        ],
        "contactInfo": contact_info,
    }

    # Build full payload
    payload = {
        "apiKey": WEBHOOK_API_KEY,
        "companyName": WEBHOOK_COMPANY_NAME,
        "sessions": [session_data],
    }

    # Send with retry logic
    for attempt in range(WEBHOOK_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=WEBHOOK_TIMEOUT) as client:
                response = await client.post(
                    WEBHOOK_URL,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code == 200 or response.status_code == 201:
                    logger.info(f"Webhook sent successfully (session: {session_id})")
                    return True
                else:
                    logger.warning(
                        f"Webhook returned status {response.status_code}: {response.text[:200]}"
                    )

        except httpx.TimeoutException:
            logger.warning(f"Webhook timeout (attempt {attempt + 1}/{WEBHOOK_RETRIES})")
        except httpx.RequestError as e:
            logger.warning(f"Webhook request error (attempt {attempt + 1}/{WEBHOOK_RETRIES}): {e}")
        except Exception as e:
            logger.error(f"Webhook unexpected error: {e}")
            break

    logger.error(f"Webhook failed after {WEBHOOK_RETRIES} attempts (session: {session_id})")
    return False
