"""
Language configuration — supported languages with formality rules.

EuroShop 2026 draws international visitors. The agent detects the visitor's
language and responds accordingly. 10 languages supported at launch.

No hardcoded multilingual messages — the realtime model handles translation
natively when given a simple English language directive.
"""

# =============================================================================
# LANGUAGES — each language the agent can speak
# =============================================================================

LANGUAGES = {
    "de": {
        "code": "de",
        "name": "Deutsch",
        "english_name": "German",
        "formality": "Sie",
        "formality_note": "Use 'Sie' (formal) unless the visitor explicitly switches to 'du'",
    },

    "en": {
        "code": "en",
        "name": "English",
        "english_name": "English",
        "formality": "neutral",
        "formality_note": "Standard professional English",
    },

    "nl": {
        "code": "nl",
        "name": "Nederlands",
        "english_name": "Dutch",
        "formality": "u",
        "formality_note": "Use 'u' (formal) unless the visitor switches to 'je/jij'",
    },

    "it": {
        "code": "it",
        "name": "Italiano",
        "english_name": "Italian",
        "formality": "Lei",
        "formality_note": "Use 'Lei' (formal) unless the visitor switches to 'tu'",
    },

    "fr": {
        "code": "fr",
        "name": "Francais",
        "english_name": "French",
        "formality": "vous",
        "formality_note": "Use 'vous' (formal) unless the visitor switches to 'tu'",
    },

    "es": {
        "code": "es",
        "name": "Espanol",
        "english_name": "Spanish",
        "formality": "usted",
        "formality_note": "Use 'usted' (formal) unless the visitor switches to 'tu'",
    },

    "pl": {
        "code": "pl",
        "name": "Polski",
        "english_name": "Polish",
        "formality": "Pan/Pani",
        "formality_note": "Use 'Pan/Pani' (formal) unless the visitor switches to informal 'ty'",
    },

    "pt": {
        "code": "pt",
        "name": "Portugues",
        "english_name": "Portuguese",
        "formality": "o senhor",
        "formality_note": "Use 'o senhor/a senhora' (formal) unless the visitor switches to 'voce/tu'",
    },

    "tr": {
        "code": "tr",
        "name": "Turkce",
        "english_name": "Turkish",
        "formality": "siz",
        "formality_note": "Use 'siz' (formal) unless the visitor switches to 'sen'",
    },

    "ar": {
        "code": "ar",
        "name": "Al-Arabiyya",
        "english_name": "Arabic",
        "formality": "hadretak",
        "formality_note": "Use formal Arabic address forms (hadretak/hadretik)",
    },
}

# =============================================================================
# DEFAULT LANGUAGE — fallback when detection is uncertain
# =============================================================================

DEFAULT_LANGUAGE = "de"  # German is the default language

# =============================================================================
# SUPPORTED LANGUAGE CODES — for validation
# =============================================================================

SUPPORTED_LANGUAGES = list(LANGUAGES.keys())

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_language_config(code: str) -> dict:
    """Return language config by code, falling back to default language."""
    return LANGUAGES.get(code, LANGUAGES[DEFAULT_LANGUAGE])


def get_formality(code: str) -> str:
    """Return the formality rule for a given language code."""
    lang = get_language_config(code)
    return lang["formality"]


# =============================================================================
# BUTTON LABELS — localized UI text for frontend buttons
# =============================================================================

BUTTON_LABELS = {
    "de": {
        "yes": "Ja",
        "no": "Nein",
        "new_conversation": "Neues Gespräch",
    },
    "en": {
        "yes": "Yes",
        "no": "No",
        "new_conversation": "New Conversation",
    },
    "nl": {
        "yes": "Ja",
        "no": "Nee",
        "new_conversation": "Nieuw gesprek",
    },
    "fr": {
        "yes": "Oui",
        "no": "Non",
        "new_conversation": "Nouvelle conversation",
    },
    "es": {
        "yes": "Sí",
        "no": "No",
        "new_conversation": "Nueva conversación",
    },
    "it": {
        "yes": "Sì",
        "no": "No",
        "new_conversation": "Nuova conversazione",
    },
    "pt": {
        "yes": "Sim",
        "no": "Não",
        "new_conversation": "Nova conversa",
    },
    "pl": {
        "yes": "Tak",
        "no": "Nie",
        "new_conversation": "Nowa rozmowa",
    },
    "tr": {
        "yes": "Evet",
        "no": "Hayır",
        "new_conversation": "Yeni konuşma",
    },
    "ar": {
        "yes": "نعم",
        "no": "لا",
        "new_conversation": "محادثة جديدة",
    },
}


# =============================================================================
# FALLBACK MESSAGES — localized user-facing fallback text
# =============================================================================

FALLBACK_MESSAGES = {
    "de": {
        "patience": "Einen Moment bitte...",
        "technical_error": "Es tut mir leid, es gibt ein technisches Problem. Bitte besuchen Sie uns direkt an unserem Stand.",
    },
    "en": {
        "patience": "One moment please...",
        "technical_error": "Sorry, I'm having a technical issue. Please visit us directly at our booth.",
    },
    "nl": {
        "patience": "Een moment alstublieft...",
        "technical_error": "Sorry, ik heb een technisch probleem. Bezoek ons alstublieft direct bij onze stand.",
    },
    "fr": {
        "patience": "Un instant s'il vous plaît...",
        "technical_error": "Désolé, j'ai un problème technique. Veuillez nous rendre visite directement à notre stand.",
    },
    "es": {
        "patience": "Un momento por favor...",
        "technical_error": "Lo siento, tengo un problema técnico. Por favor, visítenos directamente en nuestro stand.",
    },
    "it": {
        "patience": "Un momento per favore...",
        "technical_error": "Mi scusi, ho un problema tecnico. La prego di visitarci direttamente al nostro stand.",
    },
    "pt": {
        "patience": "Um momento, por favor...",
        "technical_error": "Desculpe, estou com um problema técnico. Por favor, visite-nos diretamente no nosso stand.",
    },
    "pl": {
        "patience": "Chwileczkę proszę...",
        "technical_error": "Przepraszam, mam problem techniczny. Proszę odwiedzić nas bezpośrednio na naszym stoisku.",
    },
    "tr": {
        "patience": "Bir dakika lütfen...",
        "technical_error": "Üzgünüm, teknik bir sorun yaşıyorum. Lütfen bizi doğrudan standımızda ziyaret edin.",
    },
    "ar": {
        "patience": "لحظة من فضلك...",
        "technical_error": "عذراً، أواجه مشكلة تقنية. يرجى زيارتنا مباشرة في جناحنا.",
    },
}


# =============================================================================
# TRANSLATION HELPERS
# =============================================================================


def get_button_labels(code: str) -> dict:
    """Return button labels for a given language code, falling back to default."""
    return BUTTON_LABELS.get(code, BUTTON_LABELS[DEFAULT_LANGUAGE])


def get_fallback_message(code: str, key: str) -> str:
    """Return a fallback message for a given language and key."""
    messages = FALLBACK_MESSAGES.get(code, FALLBACK_MESSAGES[DEFAULT_LANGUAGE])
    return messages.get(key, FALLBACK_MESSAGES[DEFAULT_LANGUAGE].get(key, ""))
