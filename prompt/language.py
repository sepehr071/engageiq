"""
Language directive for mid-conversation language switching.

Generates an English-only directive that tells the realtime model
which language to speak. No need for native-script directives —
the model handles translation natively.
"""

from config.languages import LANGUAGES, DEFAULT_LANGUAGE


def get_language_directive(language: str) -> str:
    """Get a language directive for the specified language.

    Args:
        language: ISO language code (e.g., "de", "en", "fr")

    Returns:
        An English language directive string. Empty string for English.
    """
    if language == "en":
        return ""

    lang_config = LANGUAGES.get(language, LANGUAGES.get(DEFAULT_LANGUAGE, {}))
    english_name = lang_config.get("english_name", "English")
    native_name = lang_config.get("name", "English")
    formality_note = lang_config.get("formality_note", "Use professional tone")

    return f"""## LANGUAGE INSTRUCTION — HIGHEST PRIORITY

You MUST respond in {english_name} ({native_name}) for ALL responses from now on.
{formality_note}
Even if the previous conversation was in another language, respond in {english_name} now.
Do not acknowledge the language change — just speak in {english_name}."""
