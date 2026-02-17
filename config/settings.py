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
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")  # Fallback text model
LLM_TEMPERATURE = 0.6                          # Temperature for realtime model
# =============================================================================
# 2. SMTP SETTINGS
# =============================================================================

SMTP_CONFIG = {
    "host": "smtp.gmail.com",
    "port": 587,
    "timeout": 10,
}

# =============================================================================
# 3. INTENT SCORING THRESHOLDS
# =============================================================================

INTENT_THRESHOLD_QUALIFY = 4    # Score >= 4: start asking qualification questions
INTENT_THRESHOLD_CAPTURE = 5   # Score >= 5: attempt to capture contact info
INTENT_THRESHOLD_HIGH = 7      # Score >= 7: high intent — push for meeting/call
INTENT_SCORE_MIN = 1            # Minimum intent score
INTENT_SCORE_MAX = 10           # Maximum intent score

# =============================================================================
# 4. CONVERSATION LIMITS
# =============================================================================

MAX_CONVERSATION_TURNS = 50     # Safety limit on conversation length
MAX_RESPONSE_WORDS = 60         # Trade show context: keep responses short
GREETING_TIMEOUT_SECONDS = 30   # How long to wait before re-greeting an idle visitor
SILENCE_TIMEOUT_SECONDS = 120   # How long before the session times out on silence

# =============================================================================
# 5. DEBUG & LOGGING
# =============================================================================

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
SAVE_CONVERSATION_HISTORY = True
LOGS_DIR = "docs"               # Directory for log files and conversation history

# =============================================================================
# 6. LIVEKIT SETTINGS
# =============================================================================

LIVEKIT_URL = os.getenv("LIVEKIT_URL", "")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")

# =============================================================================
# 7. OPENAI API
# =============================================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# =============================================================================
# 8. IMAGE CDN
# =============================================================================

IMAGE_CDN_BASE_URL = "https://image.ayand.cloud/Images/"

# =============================================================================
# 9. WEBHOOK CONFIGURATION
# =============================================================================

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://ayand-log.vercel.app/api/webhooks/ingest")
WEBHOOK_API_KEY = os.getenv("WEBHOOK_API_KEY", "ayand-secret-key-3dcSDSfgcGsasdcvg3235fvsaacv1")
WEBHOOK_COMPANY_NAME = os.getenv("WEBHOOK_COMPANY_NAME", "Ayand AI")
WEBHOOK_TIMEOUT = 10  # seconds
WEBHOOK_RETRIES = 3

