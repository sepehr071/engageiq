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
    BOOTH_LOCATION,
)
from core.session_state import UserData
from utils.history import normalize_messages

logger = logging.getLogger(__name__)


def _determine_status(userdata: UserData) -> str:
    """Map lead state to webhook status field."""
    if userdata.lead_captured and userdata.consent_given:
        return "hot_lead"
    if userdata.consent_given is False:
        return "declined"
    if userdata.partial_email or userdata.email:
        return "warm_lead"
    if userdata.intent_score >= 3:
        return "warm_lead"
    return "no_contact"


def _determine_next_step(userdata: UserData) -> str:
    """Derive next step from current flow state."""
    if userdata.lead_captured and userdata.consent_given:
        return "Team will follow up via email"
    if userdata.consent_given is False:
        return "No follow-up requested"
    if userdata.partial_email:
        return "Awaiting consent confirmation"
    return "No contact information collected"


def _build_brief(userdata: UserData) -> Optional[str]:
    """Combine summary, role, and challenge into a conversation brief."""
    parts = []
    if userdata.conversation_summary:
        parts.append(userdata.conversation_summary)
    if userdata.visitor_role:
        parts.append(f"Role: {userdata.visitor_role}")
    if userdata.biggest_challenge:
        parts.append(f"Challenge: {userdata.biggest_challenge}")
    return " | ".join(parts) if parts else None


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

    # Build contact info — use finalized data if available, else partial data
    if userdata.lead_captured:
        name_val = userdata.name
        email_val = userdata.email
        phone_val = userdata.phone
    else:
        name_val = userdata.partial_name
        email_val = userdata.partial_email
        phone_val = userdata.partial_phone

    contact_info = {
        "name": name_val,
        "email": email_val,
        "phone": phone_val,
        "reachability": email_val,
        "potentialScore": userdata.intent_score * 20,
        "conversationBrief": _build_brief(userdata),
        "nextStep": _determine_next_step(userdata),
        "status": _determine_status(userdata),
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
    # H1: Append booth location to company name (e.g., "Ayand AI-C4")
    company_name = WEBHOOK_COMPANY_NAME
    if BOOTH_LOCATION:
        company_name = f"{WEBHOOK_COMPANY_NAME}-{BOOTH_LOCATION}"

    payload = {
        "apiKey": WEBHOOK_API_KEY,
        "companyName": company_name,
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
