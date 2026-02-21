"""
Application settings — LLM, infrastructure, thresholds, debug flags.
Product metadata lives in config/products.py.
User-facing messages live in config/messages.py.
"""

import os
from dotenv import load_dotenv
load_dotenv()

# =============================================================================
# 1. LLM & REALTIME MODEL SETTINGS
# =============================================================================

RT_MODEL = "gpt-realtime-mini-2025-10-06"       # Realtime voice model
# =============================================================================
# 2. SMTP SETTINGS
# =============================================================================

SMTP_CONFIG = {
    "host": "smtp.gmail.com",
    "port": 587,
    "timeout": 10,
}

# =============================================================================
# 4. DEBUG & LOGGING
# =============================================================================

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
SAVE_CONVERSATION_HISTORY = True
LOGS_DIR = "docs"               # Directory for log files and conversation history

# =============================================================================
# 5. LIVEKIT SETTINGS
# =============================================================================

LIVEKIT_URL = os.getenv("LIVEKIT_URL", "")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")

# =============================================================================
# 6. OPENAI API
# =============================================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# =============================================================================
# 7. IMAGE CDN
# =============================================================================

IMAGE_CDN_BASE_URL = "https://image.ayand.cloud/Images/"

# =============================================================================
# 8. WEBHOOK CONFIGURATION
# =============================================================================

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://ayand-log.vercel.app/api/webhooks/ingest")
WEBHOOK_API_KEY = os.getenv("WEBHOOK_API_KEY", "ayand-secret-key-3dcSDSfgcGsasdcvg3235fvsaacv1")
WEBHOOK_COMPANY_NAME = os.getenv("WEBHOOK_COMPANY_NAME", "Ayand AI")
WEBHOOK_TIMEOUT = 10  # seconds
WEBHOOK_RETRIES = 3

# =============================================================================
# 9. AGENT IDENTITY
# =============================================================================

AVATAR_NAME = "johanna"       # Change before launch
BOOTH_LOCATION = "A1"          # e.g. "C4" — appended to webhook company name

