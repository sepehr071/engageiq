"""
Service configuration — next steps, qualification questions, and engagement flow.
Tailored for EuroShop 2026 trade show context.

Company -> config/company.py
Products -> config/products.py
"""

# =============================================================================
# NEXT STEPS — post-qualification actions based on visitor intent level
# Intent score 1-10 from EngageIQ quality scoring
# =============================================================================

NEXT_STEPS = {
    "high": {
        # Intent score 7-10: Visitor is actively evaluating, ready to engage
        "threshold": 7,
        "label": "High Intent",
        "description": "Visitor shows strong buying signals — actively evaluating solutions",
        "actions": {
            "meet_team": {
                "label": "Meet the team at the booth",
                "description": "Connect visitor with Ayand AI team member for live demo",
                "priority": 1,
            },
            "book_followup": {
                "label": "Book a follow-up call",
                "description": "Schedule a dedicated call after EuroShop for deeper discussion",
                "priority": 2,
            },
            "send_proposal": {
                "label": "Send pilot proposal",
                "description": "Email a tailored pilot proposal with pricing and timeline",
                "priority": 3,
            },
        },
        "agent_instruction": (
            "This visitor is highly interested. Suggest meeting the team at the booth NOW. "
            "If they can't stay, offer to book a follow-up call. Use assumptive language: "
            "'When works best for you?' not 'Would you maybe be interested?'"
        ),
    },
    "medium": {
        # Intent score 4-6: Visitor is interested but not yet committed
        "threshold": 4,
        "label": "Medium Intent",
        "description": "Visitor is interested but still exploring options",
        "actions": {
            "send_info": {
                "label": "Send product information",
                "description": "Email detailed product info and case studies",
                "priority": 1,
            },
            "book_demo": {
                "label": "Book a demo call",
                "description": "Schedule a product demo after the trade show",
                "priority": 2,
            },
            "connect_linkedin": {
                "label": "Connect on LinkedIn",
                "description": "Offer to connect for ongoing updates",
                "priority": 3,
            },
        },
        "agent_instruction": (
            "This visitor is interested but not ready to commit. Offer to send product "
            "information via email. If they engage well, suggest a demo call. Keep it "
            "low-pressure — they are still evaluating."
        ),
    },
    "low": {
        # Intent score 1-3: Visitor is browsing or just curious
        "threshold": 1,
        "label": "Low Intent",
        "description": "Visitor is browsing or curious — not actively looking for a solution",
        "actions": {
            "explore_booth": {
                "label": "Explore the booth",
                "description": "Encourage them to look around and try the demo",
                "priority": 1,
            },
            "take_card": {
                "label": "Take a business card",
                "description": "Offer contact details for future reference",
                "priority": 2,
            },
            "nice_meeting": {
                "label": "Nice meeting you",
                "description": "Friendly farewell with open invitation to return",
                "priority": 3,
            },
        },
        "agent_instruction": (
            "This visitor is just browsing. Be warm and welcoming, answer their questions, "
            "but do NOT push for a meeting or call. Invite them to explore the booth and "
            "let them know the team is here if they have questions later."
        ),
    },
}

# =============================================================================
# QUALIFICATION QUESTIONS — discovery questions to understand visitor needs
# Used in the conversational flow to qualify intent and route to the right product
# =============================================================================

QUALIFICATION_QUESTIONS = {
    "challenge": (
        "What's your biggest challenge with customer engagement or "
        "demand visibility right now?"
    ),
    "evaluating": (
        "Are you evaluating solutions currently, or exploring "
        "what's out there for the future?"
    ),
    "role": "What's your role?",
    "industry": "What industry or type of business are you in?",
    "company_size": "How large is your organization — roughly how many locations or employees?",
    "current_tools": "What tools or processes are you using today to capture customer demand?",
    "timeline": "Do you have a timeline in mind for implementing something like this?",
    "budget_owner": "Are you the person who makes the decision on tools like this, or is there someone else involved?",
}

# Ordered question flow — which questions to ask and in what order
# The agent should adapt based on conversation context, not rigidly follow the order
QUALIFICATION_FLOW = [
    "industry",       # First: route to the right product
    "challenge",      # Second: understand the pain point
    "role",           # Third: tailor the pitch
    "evaluating",     # Fourth: assess urgency
]

# =============================================================================
# INTENT CLASSIFICATION — rules for scoring visitor intent (1-10)
# =============================================================================

INTENT_SIGNALS = {
    "high_intent": [
        "Asks about pricing or pilot details",
        "Asks about implementation timeline",
        "Mentions a specific pain point that EngageIQ solves",
        "Asks to speak with someone from the team",
        "Requests a demo or follow-up call",
        "Mentions budget or approval process",
        "Compares EngageIQ to a competitor by name",
    ],
    "medium_intent": [
        "Asks how the product works",
        "Asks about a specific feature or capability",
        "Mentions their industry or business context",
        "Asks about case studies or results",
        "Asks about integration or technical requirements",
    ],
    "low_intent": [
        "General 'what do you do?' questions",
        "Browsing without specific questions",
        "Asks about the company but not the product",
        "Small talk or trade show chatter",
    ],
}

# =============================================================================
# EXPERT HANDOFF — titles and transitions for handing off to the booth team
# =============================================================================

EXPERT_HANDOFF = {
    "expert_title": "Product Specialist",          # Who gets connected to the visitor
    "expert_title_alt": "Solutions Consultant",     # Alternate for phrase variety
    "team_reference": "our team here at the booth", # How to refer to the booth team
    "handoff_phrases": [
        "Our team is right here — they can dive deeper into the specifics for your business.",
        "Let me connect you with our product specialist — they can show you a live demo.",
        "Our solutions team is just a few steps away and would love to chat with you directly.",
    ],
}

# =============================================================================
# FALLBACK VALUES — defaults when visitor data is not provided
# =============================================================================

FALLBACK_NOT_PROVIDED = "Not provided"
FALLBACK_INDUSTRY = "Not specified"
FALLBACK_INTENT_SCORE = 5  # Default to medium if scoring fails
