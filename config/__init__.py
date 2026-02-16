"""
Config package — re-exports all configuration symbols.
Usage: from config import COMPANY, PRODUCTS, MAIN_AGENT, etc.
"""

from config.company import COMPANY
from config.products import PRODUCTS, ACTIVE_PRODUCTS
from config.agents import MAIN_AGENT, BASE_AGENT, SUB_AGENTS
from config.services import (
    NEXT_STEPS,
    QUALIFICATION_QUESTIONS,
    QUALIFICATION_FLOW,
    INTENT_SIGNALS,
    EXPERT_HANDOFF,
    FALLBACK_NOT_PROVIDED,
    FALLBACK_INDUSTRY,
    FALLBACK_INTENT_SCORE,
)
from config.messages import (
    GREETING_MESSAGES,
    AGENT_MESSAGES,
    UI_BUTTONS,
    UI_BUTTONS_DE,
    CONVERSATION_RULES,
    EMAIL_TEMPLATES,
    EMAIL_SUMMARY_PROMPT,
)
from config.settings import (
    RT_MODEL,
    LLM_MODEL,
    LLM_TEMPERATURE,
    SMTP_CONFIG,
    INTENT_THRESHOLD_QUALIFY,
    INTENT_THRESHOLD_CAPTURE,
    INTENT_THRESHOLD_HIGH,
    SAVE_CONVERSATION_HISTORY,
    LOGS_DIR,
    DEBUG,
)
from config.languages import (
    LANGUAGES,
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    get_language_config,
    get_greeting,
    get_instruction,
    get_formality,
)
