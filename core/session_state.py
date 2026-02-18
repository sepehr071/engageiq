"""
Session state — the UserData dataclass that holds all per-session runtime state.
Shared across all agents via LiveKit's AgentSession.

Not configuration — this is runtime state (visitor info, intent, contact, flow flags).
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from livekit.agents import RunContext
from config.languages import DEFAULT_LANGUAGE


@dataclass
class UserData:
    # Language (from participant attributes, defaults to German)
    language: str = DEFAULT_LANGUAGE

    # Session tracking (for webhook)
    session_id: Optional[str] = None
    session_start_time: Optional[datetime] = None

    # Intent tracking
    intent_score: int = 0                    # 0-5 (simplified scoring)
    intent_signals: List[str] = field(default_factory=list)

    # Qualification answers (simplified - just one question)
    biggest_challenge: Optional[str] = None

    # Visitor role (detected early for personalization)
    visitor_role: Optional[str] = None

    # Contact info (finalized after consent)
    name: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    role_title: Optional[str] = None
    phone: Optional[str] = None

    # Partial contact info (before consent is given)
    partial_name: Optional[str] = None
    partial_email: Optional[str] = None
    partial_company: Optional[str] = None
    partial_role_title: Optional[str] = None
    partial_phone: Optional[str] = None

    # Consent tracking
    consent_given: Optional[bool] = None  # True/False/None (not yet asked)

    # Campaign attribution
    campaign_source: Optional[str] = None

    # Flow control
    engageiq_presented: bool = False
    qualification_started: bool = False
    lead_captured: bool = False
    next_step_offered: Optional[str] = None
    response_count: int = 0

    # Conversation
    conversation_summary: Optional[str] = None
    _history_saved: bool = False


RunContext_T = RunContext[UserData]
