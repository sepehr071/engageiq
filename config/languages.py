"""
Language configuration — supported languages with greeting templates,
formality rules, and LLM instruction strings.

EuroShop 2026 draws international visitors. The agent detects the visitor's
language and responds accordingly. 10 languages supported at launch.
"""

# =============================================================================
# LANGUAGES — each language the agent can speak
# =============================================================================

LANGUAGES = {
    "de": {
        "code": "de",
        "name": "Deutsch",
        "english_name": "German",
        "greeting_template": "Hallo! Ich bin Ihr Digital Concierge bei EuroShop 2026. Was bringt Sie zu unserem Stand?",
        "formality": "Sie",
        "formality_note": "Use 'Sie' (formal) unless the visitor explicitly switches to 'du'",
    },

    "en": {
        "code": "en",
        "name": "English",
        "english_name": "English",
        "greeting_template": "Hi there! I'm your Digital Concierge at EuroShop 2026. What brings you to our booth today?",
        "formality": "neutral",
        "formality_note": "Standard professional English",
    },

    "nl": {
        "code": "nl",
        "name": "Nederlands",
        "english_name": "Dutch",
        "greeting_template": "Hallo! Ik ben uw digitale concierge op EuroShop 2026. Wat brengt u naar onze stand?",
        "formality": "u",
        "formality_note": "Use 'u' (formal) unless the visitor switches to 'je/jij'",
    },

    "it": {
        "code": "it",
        "name": "Italiano",
        "english_name": "Italian",
        "greeting_template": "Ciao! Sono il concierge digitale di EuroShop 2026. Cosa la porta al nostro stand?",
        "formality": "Lei",
        "formality_note": "Use 'Lei' (formal) unless the visitor switches to 'tu'",
    },

    "fr": {
        "code": "fr",
        "name": "Francais",
        "english_name": "French",
        "greeting_template": "Bonjour! Je suis votre concierge digital a EuroShop 2026. Qu'est-ce qui vous amene a notre stand?",
        "formality": "vous",
        "formality_note": "Use 'vous' (formal) unless the visitor switches to 'tu'",
    },

    "es": {
        "code": "es",
        "name": "Espanol",
        "english_name": "Spanish",
        "greeting_template": "Hola! Soy el concierge digital de EuroShop 2026. Que le trae a nuestro stand?",
        "formality": "usted",
        "formality_note": "Use 'usted' (formal) unless the visitor switches to 'tu'",
    },

    "pl": {
        "code": "pl",
        "name": "Polski",
        "english_name": "Polish",
        "greeting_template": "Czesc! Jestem cyfrowym concierge na EuroShop 2026. Co sprowadza Cie do naszego stoiska?",
        "formality": "Pan/Pani",
        "formality_note": "Use 'Pan/Pani' (formal) unless the visitor switches to informal 'ty'",
    },

    "pt": {
        "code": "pt",
        "name": "Portugues",
        "english_name": "Portuguese",
        "greeting_template": "Ola! Sou o concierge digital da EuroShop 2026. O que o traz ao nosso stand?",
        "formality": "o senhor",
        "formality_note": "Use 'o senhor/a senhora' (formal) unless the visitor switches to 'voce/tu'",
    },

    "tr": {
        "code": "tr",
        "name": "Turkce",
        "english_name": "Turkish",
        "greeting_template": "Merhaba! Ben EuroShop 2026'nin dijital concierge'yim. Sizi standimiza getiren sebep nedir?",
        "formality": "siz",
        "formality_note": "Use 'siz' (formal) unless the visitor switches to 'sen'",
    },

    "ar": {
        "code": "ar",
        "name": "Al-Arabiyya",
        "english_name": "Arabic",
        "greeting_template": "Marhaba! Ana el concierge el raqami fi EuroShop 2026. Shu elli jayebak la standna?",
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


def get_greeting(code: str) -> str:
    """Return the greeting template for a given language code."""
    lang = get_language_config(code)
    return lang["greeting_template"]


def get_formality(code: str) -> str:
    """Return the formality rule for a given language code."""
    lang = get_language_config(code)
    return lang["formality"]
