"""
Company configuration — identity, locale, contact info.
Ayand AI GmbH — EuroShop 2026 booth deployment.

Products  -> config/products.py
Services  -> config/services.py
Languages -> config/languages.py
"""

# =============================================================================
# COMPANY — identity, locale, contact
# =============================================================================

COMPANY = {
    "name": "Ayand AI",                        # Short company name
    "full_name": "Ayand AI GmbH",              # Full legal/display name
    "description": "Conversational AI that makes invisible customer demand visible",
    "website": "https://ayand.ai",
    "language": "English",                      # Default response language (overridden by participant language)
    "formality": "professional-casual",            # English default: professional but approachable
    "timezone": "Europe/Berlin",
    "lead_emails": [                            # Internal emails that receive lead notifications
        "moniri@ayand.ai",
    ],
    "booth_location": "[BOOTH TBD]",            # EuroShop 2026 booth number — fill when assigned
    "event": {
        "name": "EuroShop 2026",
        "city": "Duesseldorf",
        "dates": "22-26 February 2026",
        "venue": "Messe Duesseldorf",
    },
    "email_closing": "Kind regards,\nThe Ayand AI Team",
    "greetings": {                              # Time-of-day greetings (English default)
        "morning": "Good morning!",             # 05:00-11:59
        "afternoon": "Good afternoon!",         # 12:00-17:59
        "evening": "Good evening!",             # 18:00-21:59
        "night": "Good night!",                 # 22:00-04:59
    },
}
