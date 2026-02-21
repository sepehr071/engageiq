"""
Lead storage — save and load lead data as JSON files.

Leads are persisted to the leads/ directory with timestamped filenames.
Each lead captures contact info, intent score, qualification answers,
and conversation summary from the session.
"""

import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

LEADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "leads")


def save_lead(userdata) -> str:
    """Save lead data as JSON file.

    Args:
        userdata: UserData instance from the session.

    Returns:
        Filepath of the saved lead JSON file.
    """
    os.makedirs(LEADS_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"lead_{timestamp}.json"
    filepath = os.path.join(LEADS_DIR, filename)

    lead = {
        "captured_at": datetime.now().isoformat(),
        "contact": {
            "name": userdata.name,
            "email": userdata.email,
            "company": userdata.company,
            "role_title": userdata.role_title,
            "phone": userdata.phone,
        },
        "intent": {
            "score": userdata.intent_score,
            "signals": userdata.intent_signals,
        },
        "visitor": {
            "language": userdata.language,
        },
        "qualification": {
            "biggest_challenge": userdata.biggest_challenge,
        },
        "campaign_source": userdata.campaign_source,
        "conversation_summary": userdata.conversation_summary,
    }

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(lead, f, indent=2, ensure_ascii=False)
        logger.info(f"Lead saved to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save lead: {e}")
        raise

    return filepath


def load_lead(filepath: str) -> dict:
    """Load a lead from JSON file.

    Args:
        filepath: Absolute or relative path to a lead JSON file.

    Returns:
        dict with the lead data.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
