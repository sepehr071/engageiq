"""
Config package — re-exports configuration symbols.
Usage: from config import PRODUCTS, DEFAULT_LANGUAGE, etc.
"""

from config.products import PRODUCTS
from config.settings import (
    RT_MODEL,
    LLM_TEMPERATURE,
    SMTP_CONFIG,
    SAVE_CONVERSATION_HISTORY,
    LOGS_DIR,
    DEBUG,
)
from config.languages import (
    LANGUAGES,
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    get_language_config,
    BUTTON_LABELS,
    FALLBACK_MESSAGES,
    get_button_labels,
    get_fallback_message,
)
