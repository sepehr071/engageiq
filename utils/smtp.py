"""
SMTP utilities — email notifications for EngageIQ leads.

Sends lead notification emails to the sales team when a visitor
qualifies and provides contact information at EuroShop.
"""

import os
import re
import time
import logging
import ssl
from email.message import EmailMessage
import smtplib

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

email_sender: str = os.getenv("EMAIL_SENDER", "")
email_password: str = os.getenv("EMAIL_PASSWORD", "")

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_TIMEOUT = 30

# Default notification recipient
DEFAULT_RECIPIENT = "info@ayand.ai"

_NOT_PROVIDED = "Not provided"


def is_valid_email_syntax(email: str) -> bool:
    """Check if an email address has valid syntax.

    Basic RFC 5322 compliance — checks structure, not deliverability.
    """
    if not email or not isinstance(email, str):
        return False
    pattern = re.compile(
        r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"
        r"@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
        r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$"
    )
    return bool(pattern.match(email))


def _send_via_smtp(em: EmailMessage, recipient: str, retries: int = 3) -> bool:
    """Send an email via Gmail SMTP with retry. Returns True on success."""
    context = ssl.create_default_context()
    for attempt in range(retries):
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT) as smtp:
                smtp.ehlo()
                smtp.starttls(context=context)
                smtp.ehlo()
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, recipient, em.as_string())
            return True
        except Exception as e:
            logger.warning(f"SMTP attempt {attempt + 1}/{retries} failed: {e}")
            if attempt < retries - 1:
                time.sleep(1 * (attempt + 1))

    logger.error(f"SMTP send to {recipient} failed after {retries} attempts")
    return False


def send_lead_notification(
    name: str,
    company: str,
    role_title: str,
    email: str,
    phone: str,
    intent_score: int,
    biggest_challenge: str,
    campaign_source: str,
    conversation_summary: str,
    recipient: str | None = None,
) -> bool:
    """Send lead notification email to the sales team.

    Args:
        name: Visitor's name.
        company: Visitor's company.
        role_title: Visitor's job title / role.
        email: Visitor's email address.
        phone: Visitor's phone number.
        intent_score: Intent score 0-5.
        biggest_challenge: Their stated biggest challenge.
        campaign_source: How they found us (QR code, referral, etc).
        conversation_summary: AI-generated summary of the conversation.
        recipient: Override email recipient (defaults to DEFAULT_RECIPIENT).

    Returns:
        True if the email was sent successfully.
    """
    to_address = recipient or DEFAULT_RECIPIENT

    subject = f"EuroShop Lead: {name or 'Unknown'} from {company or 'Unknown'} — Intent {intent_score}/5"

    body = _build_lead_body(
        name=name,
        company=company,
        role_title=role_title,
        email=email,
        phone=phone,
        intent_score=intent_score,
        biggest_challenge=biggest_challenge,
        campaign_source=campaign_source,
        conversation_summary=conversation_summary,
    )

    em = EmailMessage()
    em["subject"] = subject
    em["from"] = email_sender
    em["to"] = to_address
    em.set_content(body)

    return _send_via_smtp(em, to_address)


def _build_lead_body(
    name: str,
    company: str,
    role_title: str,
    email: str,
    phone: str,
    intent_score: int,
    biggest_challenge: str,
    campaign_source: str,
    conversation_summary: str,
) -> str:
    """Build the plain-text email body for a lead notification."""
    # Intent level label (simplified scoring: 0-5)
    if intent_score >= 4:
        intent_label = "HIGH"
    elif intent_score >= 2:
        intent_label = "MEDIUM"
    else:
        intent_label = "LOW"

    return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  EUROSHOP LEAD NOTIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONTACT INFORMATION
  Name:       {name or _NOT_PROVIDED}
  Company:    {company or _NOT_PROVIDED}
  Role:       {role_title or _NOT_PROVIDED}
  Email:      {email or _NOT_PROVIDED}
  Phone:      {phone or _NOT_PROVIDED}

INTENT
  Score:      {intent_score}/5 ({intent_label})
  Source:     {campaign_source or _NOT_PROVIDED}

QUALIFICATION
  Challenge:  {biggest_challenge or _NOT_PROVIDED}

CONVERSATION SUMMARY
{conversation_summary or 'No summary available.'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""".strip()
