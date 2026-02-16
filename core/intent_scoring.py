"""
DEPRECATED: Intent scoring is now handled inline in main_agent.py tool functions.
This module is kept for reference but is no longer called by any agent code.

Original purpose: detect buying signals from visitor messages via regex.

Scoring tiers (from EuroShop brief):
  High   (7-10): pricing, pilots, ROI, integration, timeline
  Medium (4-6):  technical details, references, GDPR, comparisons
  Low    (1-3):  general curiosity, browsing, accidental scan
"""

import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Each entry: (compiled regex pattern, human-readable label)
# Patterns are case-insensitive and support both German and English

HIGH_INTENT_PHRASES: list[tuple[re.Pattern, str]] = [
    # Pricing / cost
    (re.compile(r"\b(pric|cost|budget|how much|was kostet|preis|kosten)\b", re.IGNORECASE), "pricing_inquiry"),
    # Pilot / trial
    (re.compile(r"\b(pilot|trial|proof of concept|poc|testphase|pilotprojekt)\b", re.IGNORECASE), "pilot_interest"),
    # ROI / business case
    (re.compile(r"\b(roi|return on investment|business case|amortis)\b", re.IGNORECASE), "roi_discussion"),
    # Integration / technical fit
    (re.compile(r"\b(integrat|anbindung|schnittstelle|connect to our|einbinden)\b", re.IGNORECASE), "integration_question"),
    # Timeline / urgency
    (re.compile(r"\b(timeline|when can we start|wann.*start|zeitplan|how soon|wie schnell)\b", re.IGNORECASE), "timeline_inquiry"),
    # Direct buying signals
    (re.compile(r"\b(we need this|wir brauchen|das brauchen wir|genau das)\b", re.IGNORECASE), "direct_need"),
    # Meet the team
    (re.compile(r"\b(meet the team|team kennenlernen|speak.*expert|mit.*sprechen)\b", re.IGNORECASE), "meet_team"),
    # Implementation
    (re.compile(r"\b(implement|einführ|rollout|deployment|go.?live)\b", re.IGNORECASE), "implementation"),
    # Demo / contract
    (re.compile(r"\b(demo|contract|vertrag|angebot|proposal|offer)\b", re.IGNORECASE), "demo_or_contract"),
]

MEDIUM_INTENT_PHRASES: list[tuple[re.Pattern, str]] = [
    # Technical depth
    (re.compile(r"\b(how.*work.*technical|wie funktioniert.*technisch|architektur|architecture)\b", re.IGNORECASE), "technical_deep_dive"),
    # References / case studies
    (re.compile(r"\b(referenc|case stud|referenz|fallstudi|erfolgsgeschicht|success stor)\b", re.IGNORECASE), "references"),
    # Competitor comparison
    (re.compile(r"\b(competitor|vergleich|comparison|alternativ|vs\.?|compared to)\b", re.IGNORECASE), "competitor_comparison"),
    # GDPR / data protection
    (re.compile(r"\b(gdpr|dsgvo|data protect|datenschutz|compliance|konformität)\b", re.IGNORECASE), "data_protection"),
    # Features / capabilities
    (re.compile(r"\b(feature|funktionalität|capabilit|can it|kann es|what.*support)\b", re.IGNORECASE), "feature_inquiry"),
    # API / technical interface
    (re.compile(r"\b(api|sdk|webhook|endpoint|rest|graphql)\b", re.IGNORECASE), "api_inquiry"),
    # Technical details (generic)
    (re.compile(r"\b(technical detail|technische detail|specification|spezifikation)\b", re.IGNORECASE), "technical_details"),
]

LOW_INTENT_PHRASES: list[tuple[re.Pattern, str]] = [
    # General curiosity
    (re.compile(r"\b(what is this|was ist das|was macht ihr|what do you do|tell me about)\b", re.IGNORECASE), "general_curiosity"),
    # Just browsing
    (re.compile(r"\b(just browsing|nur schauen|just looking|nur mal gucken|mal sehen)\b", re.IGNORECASE), "browsing"),
    # Accidental / unclear
    (re.compile(r"\b(qr.*code|scanned|gescannt|by accident|aus versehen|zufällig)\b", re.IGNORECASE), "accidental_scan"),
]

# Default score assigned per tier when matched
_TIER_SCORES = {
    "high": 8,
    "medium": 5,
    "low": 2,
}


def detect_intent_signals(message: str, existing_signals: list[str]) -> Dict:
    """Analyze a message for intent signals.

    Args:
        message: The visitor's latest message text.
        existing_signals: Previously accumulated signal labels.

    Returns:
        dict with:
          - score: int (1-10, max of current message and previous max)
          - level: str ("high", "medium", "low")
          - new_signals: list[str] (newly detected signal phrases)
          - all_signals: list[str] (accumulated signals including new ones)
    """
    new_signals: List[str] = []
    current_score = 0

    existing_set = set(existing_signals)

    # Check high intent first (highest priority)
    for pattern, label in HIGH_INTENT_PHRASES:
        if pattern.search(message) and label not in existing_set:
            new_signals.append(label)
            current_score = max(current_score, _TIER_SCORES["high"])

    # Check medium intent
    for pattern, label in MEDIUM_INTENT_PHRASES:
        if pattern.search(message) and label not in existing_set:
            new_signals.append(label)
            current_score = max(current_score, _TIER_SCORES["medium"])

    # Check low intent
    for pattern, label in LOW_INTENT_PHRASES:
        if pattern.search(message) and label not in existing_set:
            new_signals.append(label)
            current_score = max(current_score, _TIER_SCORES["low"])

    # Intent only goes up, never down — take running max
    # Infer previous max from existing signals
    previous_max = _infer_max_score(existing_signals)
    final_score = max(previous_max, current_score)

    # Clamp to 1-10 range (minimum 1 if any signal ever detected)
    all_signals = existing_signals + new_signals
    if all_signals and final_score < 1:
        final_score = 1
    final_score = min(final_score, 10)

    # Determine level from final score
    if final_score >= 7:
        level = "high"
    elif final_score >= 4:
        level = "medium"
    else:
        level = "low"

    if new_signals:
        logger.info(f"Intent signals detected: {new_signals} → score={final_score} ({level})")

    return {
        "score": final_score,
        "level": level,
        "new_signals": new_signals,
        "all_signals": all_signals,
    }


def _infer_max_score(signals: list[str]) -> int:
    """Infer the historical max score from accumulated signal labels."""
    if not signals:
        return 0

    high_labels = {label for _, label in HIGH_INTENT_PHRASES}
    medium_labels = {label for _, label in MEDIUM_INTENT_PHRASES}

    max_score = 0
    for signal in signals:
        if signal in high_labels:
            max_score = max(max_score, _TIER_SCORES["high"])
        elif signal in medium_labels:
            max_score = max(max_score, _TIER_SCORES["medium"])
        else:
            max_score = max(max_score, _TIER_SCORES["low"])

    return max_score
