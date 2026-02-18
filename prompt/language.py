"""
Language directives for the Realtime API — single source of truth.

Native-language directives that get prepended to agent instructions.
Written IN the target language for maximum salience with the OpenAI Realtime model.

Usage:
    from prompt.language import build_prompt_with_language

    base = build_main_prompt(product_data)
    full_prompt = build_prompt_with_language(base, "de")
"""

from config.languages import LANGUAGES, DEFAULT_LANGUAGE


# Native-language directives — written IN each language for strongest signal.
# Ported from the working main branch + added nl, pl for 10-language support.
_LANGUAGE_DIRECTIVES = {
    "de": """## KRITISCHE SPRACHANWEISUNG - HÖCHSTE PRIORITÄT

DU SPRICHST JETZT DEUTSCH. Diese Anweisung hat VORRANG vor ALLEN anderen Anweisungen.

SPRACHANFORDERUNGEN:
- Sprich AUSSCHLIESSLICH auf Deutsch
- Verwende die formelle "Sie"-Form
- Jedes Wort muss Deutsch sein
- Setze das Gespräch auf Deutsch fort

WICHTIG: Auch wenn das vorherige Gespräch in einer anderen Sprache war, musst du JETZT auf Deutsch antworten. Ignoriere alle vorherigen Sprachanweisungen.""",

    "en": """## CRITICAL LANGUAGE INSTRUCTION - HIGHEST PRIORITY

YOU ARE NOW SPEAKING ENGLISH. This instruction takes PRECEDENCE over ALL other instructions.

LANGUAGE REQUIREMENTS:
- Speak ONLY in English
- Use professional but conversational tone
- Every word must be English
- Continue the conversation in English

IMPORTANT: Even if the previous conversation was in another language, you MUST respond in English NOW. Ignore all previous language instructions.""",

    "nl": """## KRITIEKE TAALINSTRUCTIE - HOOGSTE PRIORITEIT

JE SPREEKT NU NEDERLANDS. Deze instructie heeft VOORRANG op ALLE andere instructies.

TAALVEREISTEN:
- Spreek UITSLUITEND Nederlands
- Gebruik de formele "u"-vorm
- Elk woord moet in het Nederlands zijn
- Ga verder met het gesprek in het Nederlands

BELANGRIJK: Zelfs als het vorige gesprek in een andere taal was, MOET je NU in het Nederlands antwoorden. Negeer alle eerdere taalinstructies.""",

    "fr": """## INSTRUCTION CRITIQUE DE LANGUE - PRIORITÉ MAXIMALE

VOUS PARLEZ MAINTENANT FRANÇAIS. Cette instruction a la PRIORITÉ sur TOUTES les autres instructions.

EXIGENCES LINGUISTIQUES:
- Parlez UNIQUEMENT en français
- Utilisez la forme formelle "vous"
- Chaque mot doit être en français
- Continuez la conversation en français

IMPORTANT: Même si la conversation précédente était dans une autre langue, vous DEVEZ répondre en français MAINTENANT. Ignorez toutes les instructions linguistiques précédentes.""",

    "es": """## INSTRUCCIÓN CRÍTICA DE IDIOMA - MÁXIMA PRIORIDAD

AHORA ESTÁS HABLANDO ESPAÑOL. Esta instrucción tiene PRIORIDAD sobre TODAS las demás instrucciones.

REQUISITOS DEL IDIOMA:
- Habla SOLO en español
- Usa la forma formal "usted"
- Cada palabra debe ser en español
- Continúa la conversación en español

IMPORTANTE: Aunque la conversación anterior estuviera en otro idioma, DEBES responder en español AHORA. Ignora todas las instrucciones de idioma anteriores.""",

    "it": """## ISTRUZIONE CRITICA DI LINGUA - MASSIMA PRIORITÀ

ORA STAI PARLANDO IN ITALIANO. Questa istruzione ha la PRECEDENZA su TUTTE le altre istruzioni.

REQUISITI LINGUISTICI:
- Parla SOLO in italiano
- Usa la forma formale "Lei"
- Ogni parola deve essere in italiano
- Continua la conversazione in italiano

IMPORTANTE: Anche se la conversazione precedente era in un'altra lingua, DEVI rispondere in italiano ORA. Ignora tutte le istruzioni linguistiche precedenti.""",

    "pt": """## INSTRUÇÃO CRÍTICA DE IDIOMA - PRIORIDADE MÁXIMA

VOCÊ ESTÁ FALANDO PORTUGUÊS AGORA. Esta instrução tem PRIORIDADE sobre TODAS as outras instruções.

REQUISITOS DE IDIOMA:
- Fale APENAS em português
- Use a forma formal "o senhor/a senhora"
- Cada palavra deve ser em português
- Continue a conversa em português

IMPORTANTE: Mesmo que a conversa anterior estivesse em outro idioma, você DEVE responder em português AGORA. Ignore todas as instruções de idioma anteriores.""",

    "pl": """## KRYTYCZNA INSTRUKCJA JĘZYKOWA - NAJWYŻSZY PRIORYTET

TERAZ MÓWISZ PO POLSKU. Ta instrukcja ma PIERWSZEŃSTWO przed WSZYSTKIMI innymi instrukcjami.

WYMAGANIA JĘZYKOWE:
- Mów WYŁĄCZNIE po polsku
- Używaj formy grzecznościowej "Pan/Pani"
- Każde słowo musi być po polsku
- Kontynuuj rozmowę po polsku

WAŻNE: Nawet jeśli poprzednia rozmowa była w innym języku, MUSISZ teraz odpowiadać po polsku. Zignoruj wszystkie poprzednie instrukcje językowe.""",

    "tr": """## KRİTİK DİL TALİMATI - EN YÜKSEK ÖNCELİK

ŞİMDİ TÜRKÇE KONUŞUYORSUN. Bu talimat TÜM diğer talimatlardan ÖNCELİKLİDİR.

DİL GEREKSİNİMLERİ:
- SADECE Türkçe konuş
- Resmi "siz" formunu kullan
- Her kelime Türkçe olmalı
- Konuşmaya Türkçe devam et

ÖNEMLİ: Önceki konuşma başka bir dilde olsa bile, ŞİMDİ Türkçe yanıt vermek ZORUNDASIN. Tüm önceki dil talimatlarını görmezden gel.""",

    "ar": """## تعليمة لغة حرجة - أولوية قصوى

أنت تتحدث بالعربية الآن. هذه التعليمة لها الأولوية على جميع التعليمات الأخرى.

متطلبات اللغة:
- تحدث فقط بالعربية
- استخدم صيغة المخاطبة الرسمية
- كل كلمة يجب أن تكون بالعربية
- واصل المحادثة بالعربية

مهم: حتى لو كانت المحادثة السابقة بلغة أخرى، يجب عليك الرد بالعربية الآن. تجاهل جميع تعليمات اللغة السابقة.""",
}


def get_language_directive(language: str) -> str:
    """Get the native-language directive for the specified language.

    Returns a strong directive written IN the target language.
    Falls back to a generated English directive for unknown languages.
    """
    directive = _LANGUAGE_DIRECTIVES.get(language)
    if directive:
        return directive

    # Fallback for unknown languages
    lang_config = LANGUAGES.get(language, LANGUAGES.get(DEFAULT_LANGUAGE, {}))
    english_name = lang_config.get("english_name", "English")

    return f"""## CRITICAL LANGUAGE INSTRUCTION - HIGHEST PRIORITY

YOU ARE NOW SPEAKING {english_name.upper()}. This instruction takes PRECEDENCE over ALL other instructions.

LANGUAGE REQUIREMENTS:
- Speak ONLY in {english_name}
- Every word must be in {english_name}
- Continue the conversation in {english_name}

IMPORTANT: Even if the previous conversation was in another language, you MUST respond in {english_name} NOW. Ignore all previous language instructions."""


def lang_hint(language: str) -> str:
    """Return a short English-language reminder for tool return strings.

    This is an instruction to the LLM (not user-facing text), so it stays in English.
    The system prompt's native-language directive is the primary language mechanism;
    this hint reinforces compliance after tool calls.
    """
    lang_config = LANGUAGES.get(language, LANGUAGES.get(DEFAULT_LANGUAGE, {}))
    english_name = lang_config.get("english_name", "German")
    formality = lang_config.get("formality", "")

    if language == "en":
        return "Respond in English."
    return f"Respond in {english_name} (formal {formality})."


def build_prompt_with_language(base_prompt: str, language: str) -> str:
    """Combine a base prompt with a language directive at the TOP.

    The directive is prepended for maximum salience with the OpenAI Realtime model.
    For the default case, the directive is still included to ensure language consistency.

    Args:
        base_prompt: English-only base prompt (from build_main_prompt or build_lead_capture_prompt).
        language: ISO language code (e.g., "de", "en", "fr").

    Returns:
        Combined prompt: language directive at top + base prompt.
    """
    directive = get_language_directive(language)
    if not directive:
        return base_prompt
    return f"{directive}\n\n{base_prompt}"
