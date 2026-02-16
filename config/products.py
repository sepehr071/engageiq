"""
Product configuration — Ayand AI's EngageIQ product.

EngageIQ is a Conversational Demand Interface that makes invisible customer demand visible.
Used by clients like CORE and DFKI.
"""

from config.settings import IMAGE_CDN_BASE_URL

# =============================================================================
# PRODUCT — EngageIQ
# =============================================================================

PRODUCTS = {
    "engageiq": {
        "key": "engageiq",
        "name": "EngageIQ",
        "subtitle": "Conversational Demand Interface",
        "what_is_it": (
            "An AI-powered system that captures invisible customer demand through "
            "natural conversation. EngageIQ engages visitors 24/7, understands their "
            "intent, and turns anonymous interactions into qualified leads with "
            "intent scoring and structured data."
        ),
        "problem_solved": (
            "Most businesses have no visibility into what their visitors actually want. "
            "98% of website visitors leave without sharing contact info. Staff can't "
            "be available 24/7. Valuable demand goes unnoticed and uncaptured."
        ),
        "value_prop": (
            "EngageIQ makes invisible demand visible. Through natural AI conversation, "
            "it captures visitor intent, scores lead quality, and delivers structured "
            "data to your team — so you know exactly who to follow up with and why."
        ),
        "capabilities": [
            "24/7 AI conversation in multiple languages",
            "Intent quality scoring (1-10 scale)",
            "Real-time hot lead alerts",
            "Campaign attribution — know which marketing drives real demand",
            "Structured lead data with conversation transcripts",
            "Works on websites, QR codes, and kiosks",
        ],
        "installation": "Web widget + QR codes + optional kiosk hardware",
        "pricing": {
            "pilot_total": None,
            "currency": "EUR",
            "structure": "Custom pricing based on use case",
            "guarantee": None,
            "pilot_duration": "Flexible",
        },
        "status": "active",
        "url": "",
        "images": [],  # EngageIQ itself has no images - only clients have images
        # Client case studies with hardware installation images
        "clients": [
            {
                "name": "CORE",
                "description": "Ayand AI client using EngageIQ for visitor engagement",
                "url": "https://vimeo.com/1165136133/9930020d47?share=copy&fl=sv&fe=ci",
                "images": [
                    "https://image.ayand.cloud/euro/core.png",
                ],
            },
            {
                "name": "DFKI",
                "description": "Ayand AI client using EngageIQ for visitor engagement",
                "url": "https://vimeo.com/1165136145/062503170c?share=copy&fl=sv&fe=ci",
                "images": [
                    "https://image.ayand.cloud/euro/dfki.png",
                ],
            },
        ],
    },
}

# =============================================================================
# ACTIVE PRODUCTS — for demo conversations
# =============================================================================

ACTIVE_PRODUCTS = {k: v for k, v in PRODUCTS.items() if v["status"] == "active"}


# =============================================================================
# ROLE-BASED VALUE PROPOSITIONS — personalize presentation by visitor role
# =============================================================================

ROLE_HOOKS = {
    # Marketing roles
    "marketing": {
        "keywords": ["marketing", "cmo", "marketing director", "marketing manager", "brand", "campaign", "demand generation", "growth"],
        "value_hook": "Know exactly which campaigns drive real demand, not just clicks. EngageIQ shows you the intent behind every visitor interaction.",
        "challenge_example": "Which of your marketing channels actually generates qualified demand, not just traffic?",
    },

    # Sales roles
    "sales": {
        "keywords": ["sales", "vp sales", "sales director", "account executive", "business development", "revenue", "sales manager"],
        "value_hook": "Your best leads are the ones you never see. EngageIQ surfaces hidden demand so your team follows up with visitors who are actually interested.",
        "challenge_example": "How many potential customers leave your website without your sales team ever knowing they were there?",
    },

    # C-Level / Executive
    "executive": {
        "keywords": ["ceo", "cto", "coo", "cfo", "founder", "owner", "managing director", "geschaeftsfuehrer"],
        "value_hook": "Turn invisible demand into measurable pipeline. EngageIQ gives you visibility into what your visitors actually want — 24/7.",
        "challenge_example": "How much demand are you missing because you can't see who's actually interested?",
    },

    # Operations / Customer Experience
    "operations": {
        "keywords": ["operations", "customer experience", "cx", "customer success", "service", "support", "operations manager"],
        "value_hook": "Every visitor interaction contains a signal. EngageIQ captures those signals so your team knows exactly what customers need.",
        "challenge_example": "Do you know what your visitors are actually looking for before they reach out?",
    },

    # Digital / E-commerce
    "digital": {
        "keywords": ["e-commerce", "ecommerce", "digital", "online", "web", "digital transformation", "it director"],
        "value_hook": "Your website works 24/7. Now it can qualify demand too. EngageIQ captures intent around the clock.",
        "challenge_example": "What happens to demand outside business hours? Are you capturing those conversations?",
    },

    # Default / Unknown
    "default": {
        "keywords": [],
        "value_hook": "EngageIQ makes invisible customer demand visible. Through natural AI conversation, it captures visitor intent and delivers structured data to your team.",
        "challenge_example": "What's your biggest challenge with understanding your customer demand?",
    },
}


def get_role_hook(role_text: str) -> dict:
    """Match a role text to the most appropriate hook configuration.

    Args:
        role_text: The visitor's stated role or job title (lowercase).

    Returns:
        The matching role hook dict, or default if no match.
    """
    role_lower = (role_text or "").lower()

    for role_key, role_config in ROLE_HOOKS.items():
        if role_key == "default":
            continue
        for keyword in role_config.get("keywords", []):
            if keyword in role_lower:
                return role_config

    return ROLE_HOOKS["default"]
