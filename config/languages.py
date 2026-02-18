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
