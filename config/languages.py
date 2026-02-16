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
        "greeting_template": (
            "Willkommen bei Ayand AI auf der EuroShop! "
            "Ich bin Ihr digitaler Concierge. "
            "Wir machen unsichtbare Kundennachfrage sichtbar. "
            "Was fuehrt Sie heute zu uns?"
        ),
        "formality": "Sie",  # Formal by default for German
        "formality_note": "Use 'Sie' (formal) unless the visitor explicitly switches to 'du'",
        "instruction_language": (
            "Respond in German (Deutsch). Use formal 'Sie' form. "
            "Write in natural, spoken German — not written/literary style."
        ),
    },

    "en": {
        "code": "en",
        "name": "English",
        "english_name": "English",
        "greeting_template": (
            "Welcome to Ayand AI at EuroShop! "
            "I'm your digital concierge. "
            "We make invisible customer demand visible. "
            "What brings you to our booth today?"
        ),
        "formality": "neutral",  # English has no formal/informal distinction
        "formality_note": "Standard professional English",
        "instruction_language": (
            "Respond in English. Use professional but conversational tone."
        ),
    },

    "fr": {
        "code": "fr",
        "name": "Francais",
        "english_name": "French",
        "greeting_template": (
            "Bienvenue chez Ayand AI a l'EuroShop! "
            "Je suis votre concierge digital. "
            "Nous rendons visible la demande client invisible. "
            "Qu'est-ce qui vous amene aujourd'hui?"
        ),
        "formality": "vous",  # Formal by default for French
        "formality_note": "Use 'vous' (formal) unless the visitor switches to 'tu'",
        "instruction_language": (
            "Respond in French (Francais). Use formal 'vous' form. "
            "Write in natural, conversational French."
        ),
    },

    "es": {
        "code": "es",
        "name": "Espanol",
        "english_name": "Spanish",
        "greeting_template": (
            "Bienvenido a Ayand AI en EuroShop! "
            "Soy su concierge digital. "
            "Hacemos visible la demanda invisible del cliente. "
            "Que le trae hoy a nuestro stand?"
        ),
        "formality": "usted",  # Formal by default for Spanish
        "formality_note": "Use 'usted' (formal) unless the visitor switches to 'tu'",
        "instruction_language": (
            "Respond in Spanish (Espanol). Use formal 'usted' form. "
            "Write in natural, conversational Spanish."
        ),
    },

    "it": {
        "code": "it",
        "name": "Italiano",
        "english_name": "Italian",
        "greeting_template": (
            "Benvenuto da Ayand AI all'EuroShop! "
            "Sono il suo concierge digitale. "
            "Rendiamo visibile la domanda invisibile dei clienti. "
            "Cosa la porta al nostro stand oggi?"
        ),
        "formality": "Lei",  # Formal by default for Italian
        "formality_note": "Use 'Lei' (formal) unless the visitor switches to 'tu'",
        "instruction_language": (
            "Respond in Italian (Italiano). Use formal 'Lei' form. "
            "Write in natural, conversational Italian."
        ),
    },

    "tr": {
        "code": "tr",
        "name": "Turkce",
        "english_name": "Turkish",
        "greeting_template": (
            "EuroShop'ta Ayand AI'ye hosgeldiniz! "
            "Ben dijital concierge'inizim. "
            "Gorunmeyen musteri talebini gorunur kiliyoruz. "
            "Buguen bizi ziyaret etmenizin sebebi nedir?"
        ),
        "formality": "siz",  # Formal by default for Turkish
        "formality_note": "Use 'siz' (formal) unless the visitor switches to 'sen'",
        "instruction_language": (
            "Respond in Turkish (Turkce). Use formal 'siz' form. "
            "Write in natural, conversational Turkish."
        ),
    },

    "ar": {
        "code": "ar",
        "name": "Al-Arabiyya",
        "english_name": "Arabic",
        "greeting_template": (
            "Ahlan wa sahlan fi Ayand AI fi EuroShop! "
            "Ana el concierge el raqami. "
            "Nejaal talab el omala2 el gheer mar2i mar2i. "
            "Shu elli gabak el youm?"
        ),
        "formality": "hadretak",  # Formal Arabic address
        "formality_note": "Use formal Arabic address forms (hadretak/hadretik)",
        "instruction_language": (
            "Respond in Arabic. Use formal address. "
            "Write in Modern Standard Arabic or educated spoken Arabic, "
            "keeping it natural and conversational."
        ),
    },

    "zh": {
        "code": "zh",
        "name": "Zhongwen",
        "english_name": "Chinese (Mandarin)",
        "greeting_template": (
            "Huan ying lai dao EuroShop de Ayand AI zhan wei! "
            "Wo shi nin de shu zi li bin. "
            "Wo men rang kan bu jian de ke hu xu qiu bian de ke jian. "
            "Jin tian shi shen me rang nin lai dao wo men zhan wei?"
        ),
        "formality": "nin",  # Formal Chinese address
        "formality_note": "Use 'nin' (formal you) rather than 'ni'",
        "instruction_language": (
            "Respond in Mandarin Chinese. Use formal 'nin' address. "
            "Write in natural, professional Mandarin."
        ),
    },

    "ja": {
        "code": "ja",
        "name": "Nihongo",
        "english_name": "Japanese",
        "greeting_template": (
            "EuroShop no Ayand AI he youkoso! "
            "Watashi wa dejitaru konshieruju desu. "
            "Mienai kokyaku juyo wo mieru ka shimasu. "
            "Kyo wa nani ga kikkake de irasshaimashita ka?"
        ),
        "formality": "desu/masu",  # Polite Japanese form
        "formality_note": "Use desu/masu (polite) form throughout",
        "instruction_language": (
            "Respond in Japanese. Use polite desu/masu form. "
            "Write in natural, professional Japanese."
        ),
    },

    "pt": {
        "code": "pt",
        "name": "Portugues",
        "english_name": "Portuguese",
        "greeting_template": (
            "Bem-vindo a Ayand AI na EuroShop! "
            "Sou o seu concierge digital. "
            "Tornamos visivel a procura invisivel do cliente. "
            "O que o traz ao nosso stand hoje?"
        ),
        "formality": "o senhor",  # Formal Portuguese address
        "formality_note": "Use 'o senhor/a senhora' (formal) unless the visitor switches to 'voce/tu'",
        "instruction_language": (
            "Respond in Portuguese. Use formal 'o senhor/a senhora' form. "
            "Write in natural, conversational Portuguese."
        ),
    },
}

# =============================================================================
# LANGUAGE DETECTION — keyword hints for detecting visitor language
# =============================================================================

LANGUAGE_DETECTION_HINTS = {
    "de": ["hallo", "guten", "tag", "morgen", "ich", "bin", "suche", "moechte", "bitte", "danke"],
    "en": ["hello", "hi", "hey", "good", "morning", "looking", "want", "need", "please", "thanks"],
    "fr": ["bonjour", "salut", "merci", "je", "suis", "cherche", "voudrais", "s'il vous plait"],
    "es": ["hola", "buenos", "dias", "busco", "quiero", "necesito", "gracias", "por favor"],
    "it": ["ciao", "buongiorno", "salve", "cerco", "vorrei", "grazie", "per favore"],
    "tr": ["merhaba", "selam", "gunaydin", "ariyorum", "istiyorum", "tesekkurler", "lutfen"],
    "ar": ["marhaba", "ahlan", "salam", "shukran", "min fadlak", "sabah", "masaa"],
    "zh": ["nihao", "nin hao", "zaoshang", "xiexie", "qingwen", "wo xiang", "xuyao"],
    "ja": ["konnichiwa", "ohayo", "sumimasen", "arigatou", "hajimemashite", "yoroshiku"],
    "pt": ["ola", "bom dia", "boa tarde", "obrigado", "obrigada", "preciso", "por favor"],
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


def get_instruction(code: str) -> str:
    """Return the LLM instruction string for a given language code."""
    lang = get_language_config(code)
    return lang["instruction_language"]


def get_formality(code: str) -> str:
    """Return the formality rule for a given language code."""
    lang = get_language_config(code)
    return lang["formality"]
