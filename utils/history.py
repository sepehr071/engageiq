"""
Conversation history — save transcripts with lead context.

Simplified from Herbrand's history module: no product insertion logic,
instead captures intent score, qualification answers, and contact info
alongside the raw transcript.
"""

import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

HISTORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "history")


def normalize_messages(chat_messages) -> list[dict]:
    """Convert ChatMessage objects into a standardized list of dicts.

    Each dict has { "role": "user"|"assistant", "message": "..." }.
    Skips non-ChatMessage items (e.g., FunctionCall).
    Parses JSON-encoded user messages to extract the text.
    """
    normalized = []

    for msg in chat_messages:
        # Skip if not a ChatMessage (e.g., FunctionCall)
        if not hasattr(msg, "role"):
            continue

        role = msg.role

        # Extract raw content (may be list of strings or a single string)
        if isinstance(msg.content, list) and msg.content:
            raw = " ".join(msg.content)
        else:
            raw = str(msg.content)

        # User messages may contain JSON-encoded payloads
        if role == "user":
            try:
                parsed = json.loads(raw)
                message_text = parsed.get("message", raw)
            except Exception:
                message_text = raw
        else:
            message_text = raw

        normalized.append({
            "role": role,
            "message": message_text,
        })

    return normalized


def save_conversation_to_file(chat_messages, userdata) -> None:
    """Save a conversation transcript with lead context to a text file.

    Args:
        chat_messages: Raw chat message objects from _chat_ctx.items.
        userdata: UserData instance with contact, intent, and qualification data.
    """
    conversation = normalize_messages(chat_messages)

    # Don't save empty conversations
    if not conversation:
        logger.info("No conversation to save (empty session)")
        return

    os.makedirs(HISTORY_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.txt"
    filepath = os.path.join(HISTORY_DIR, filename)

    try:
        lines = []

        # Header
        lines.append("=" * 60)
        lines.append("  ENGAGEIQ CONVERSATION TRANSCRIPT")
        lines.append(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)
        lines.append("")

        # Intent summary (scale is 0-5)
        intent_level = "HIGH" if userdata.intent_score >= 4 else "MEDIUM" if userdata.intent_score >= 2 else "LOW"
        lines.append(f"Intent Score: {userdata.intent_score}/5 ({intent_level})")
        if userdata.intent_signals:
            lines.append(f"Signals: {', '.join(userdata.intent_signals)}")
        lines.append("")

        # Transcript
        lines.append("-" * 60)
        lines.append("TRANSCRIPT")
        lines.append("-" * 60)
        lines.append("")

        for msg in conversation:
            text = msg["message"].strip()
            if not text:
                continue
            if msg["role"] == "user":
                lines.append(f"Visitor: {text}")
            else:
                lines.append(f"Agent:   {text}")

        # Contact info
        _not_set = "—"
        has_contact = any([
            userdata.name, userdata.email, userdata.phone,
            userdata.company, userdata.role_title,
        ])

        # Also check for partial contact info
        has_partial_contact = any([
            userdata.partial_name, userdata.partial_email, userdata.partial_phone,
            userdata.partial_company, userdata.partial_role_title,
        ])

        if has_contact:
            lines.append("")
            lines.append("-" * 60)
            lines.append("CONTACT INFORMATION (FINALIZED)")
            lines.append("-" * 60)
            lines.append("")
            lines.append(f"Name:    {userdata.name or _not_set}")
            lines.append(f"Email:   {userdata.email or _not_set}")
            lines.append(f"Phone:   {userdata.phone or _not_set}")
            lines.append(f"Company: {userdata.company or _not_set}")
            lines.append(f"Role:    {userdata.role_title or _not_set}")
            consent_status = 'Yes' if userdata.consent_given else 'No' if userdata.consent_given is False else 'Not asked'
            lines.append(f"Consent: {consent_status}")
        elif has_partial_contact:
            lines.append("")
            lines.append("-" * 60)
            lines.append("PARTIAL CONTACT INFO (NO CONSENT)")
            lines.append("-" * 60)
            lines.append("")
            lines.append(f"Name:    {userdata.partial_name or _not_set}")
            lines.append(f"Email:   {userdata.partial_email or _not_set}")
            lines.append(f"Phone:   {userdata.partial_phone or _not_set}")
            lines.append(f"Company: {userdata.partial_company or _not_set}")
            lines.append(f"Role:    {userdata.partial_role_title or _not_set}")
            lines.append(f"Status:  Session ended before consent was given")

        # Qualification answers
        has_qualification = any([
            userdata.biggest_challenge,
            userdata.visitor_role,
        ])

        if has_qualification:
            lines.append("")
            lines.append("-" * 60)
            lines.append("QUALIFICATION")
            lines.append("-" * 60)
            lines.append("")
            lines.append(f"Biggest Challenge: {userdata.biggest_challenge or _not_set}")
            lines.append(f"Visitor Role:      {userdata.visitor_role or _not_set}")

        # Metadata
        lines.append("")
        lines.append("-" * 60)
        lines.append("METADATA")
        lines.append("-" * 60)
        lines.append("")
        lines.append(f"Language:        {userdata.language}")
        lines.append(f"Campaign Source: {userdata.campaign_source or _not_set}")
        lines.append(f"Lead Captured:   {'Yes' if userdata.lead_captured else 'No'}")

        # Conversation summary (if generated)
        if userdata.conversation_summary:
            lines.append("")
            lines.append("-" * 60)
            lines.append("AI CONVERSATION SUMMARY")
            lines.append("-" * 60)
            lines.append("")
            lines.append(userdata.conversation_summary)

        lines.append("")
        lines.append("=" * 60)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info(f"Conversation saved to {filepath}")

    except Exception as e:
        logger.error(f"Failed to save conversation history: {e}")
