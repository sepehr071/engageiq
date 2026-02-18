"""
Config package — re-exports configuration symbols.
Usage: from config import COMPANY, PRODUCTS, DEFAULT_LANGUAGE, etc.
"""

from config.company import COMPANY
from config.products import PRODUCTS, ACTIVE_PRODUCTS
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
    get_formality,
)
