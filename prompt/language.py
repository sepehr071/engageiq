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

DU SPRICHST AB JETZT NUR NOCH DEUTSCH. Diese Anweisung hat VORRANG vor ALLEN anderen Anweisungen.
Ignoriere die Sprache ALLER vorherigen Nachrichten. Ab diesem Moment ist Deutsch deine EINZIGE Sprache.

SPRACHANFORDERUNGEN:
- Sprich AUSSCHLIESSLICH auf Deutsch
- Verwende die formelle "Sie"-Form
- Jedes Wort muss Deutsch sein
- Setze das Gespräch auf Deutsch fort
- Auch wenn der Besucher in einer anderen Sprache spricht, antworte auf Deutsch

NOCHMAL: Ab jetzt NUR Deutsch. Keine andere Sprache. DEUTSCH.""",

    "en": """## CRITICAL LANGUAGE INSTRUCTION - HIGHEST PRIORITY

YOU ARE NOW SPEAKING ONLY ENGLISH. This instruction takes PRECEDENCE over ALL other instructions.
IGNORE the language of ALL previous messages. From this moment, English is your ONLY language.

LANGUAGE REQUIREMENTS:
- Speak ONLY in English
- Use professional but conversational tone
- Every word must be English
- Continue the conversation in English
- Even if the visitor speaks another language, respond in English

AGAIN: From now on ONLY English. No other language. ENGLISH.""",

    "nl": """## KRITIEKE TAALINSTRUCTIE - HOOGSTE PRIORITEIT

JE SPREEKT VANAF NU ALLEEN NOG NEDERLANDS. Deze instructie heeft VOORRANG op ALLE andere instructies.
NEGEER de taal van ALLE vorige berichten. Vanaf dit moment is Nederlands je ENIGE taal.

TAALVEREISTEN:
- Spreek UITSLUITEND Nederlands
- Gebruik de formele "u"-vorm
- Elk woord moet in het Nederlands zijn
- Ga verder met het gesprek in het Nederlands
- Zelfs als de bezoeker een andere taal spreekt, antwoord in het Nederlands

NOGMAALS: Vanaf nu ALLEEN Nederlands. Geen andere taal. NEDERLANDS.""",

    "fr": """## INSTRUCTION CRITIQUE DE LANGUE - PRIORITÉ MAXIMALE

VOUS PARLEZ DÉSORMAIS UNIQUEMENT FRANÇAIS. Cette instruction a la PRIORITÉ sur TOUTES les autres instructions.
IGNOREZ la langue de TOUS les messages précédents. À partir de ce moment, le français est votre SEULE langue.

EXIGENCES LINGUISTIQUES:
- Parlez UNIQUEMENT en français
- Utilisez la forme formelle "vous"
- Chaque mot doit être en français
- Continuez la conversation en français
- Même si le visiteur parle une autre langue, répondez en français

ENCORE UNE FOIS: À partir de maintenant UNIQUEMENT le français. Aucune autre langue. FRANÇAIS.""",

    "es": """## INSTRUCCIÓN CRÍTICA DE IDIOMA - MÁXIMA PRIORIDAD

AHORA HABLAS ÚNICAMENTE EN ESPAÑOL. Esta instrucción tiene PRIORIDAD sobre TODAS las demás instrucciones.
IGNORA el idioma de TODOS los mensajes anteriores. A partir de este momento, el español es tu ÚNICO idioma.

REQUISITOS DEL IDIOMA:
- Habla SOLO en español
- Usa la forma formal "usted"
- Cada palabra debe ser en español
- Continúa la conversación en español
- Aunque el visitante hable otro idioma, responde en español

DE NUEVO: A partir de ahora SOLO español. Ningún otro idioma. ESPAÑOL.""",

    "it": """## ISTRUZIONE CRITICA DI LINGUA - MASSIMA PRIORITÀ

ORA PARLI UNICAMENTE IN ITALIANO. Questa istruzione ha la PRECEDENZA su TUTTE le altre istruzioni.
IGNORA la lingua di TUTTI i messaggi precedenti. Da questo momento, l'italiano è la tua UNICA lingua.

REQUISITI LINGUISTICI:
- Parla SOLO in italiano
- Usa la forma formale "Lei"
- Ogni parola deve essere in italiano
- Continua la conversazione in italiano
- Anche se il visitatore parla un'altra lingua, rispondi in italiano

DI NUOVO: Da adesso SOLO italiano. Nessun'altra lingua. ITALIANO.""",

    "pt": """## INSTRUÇÃO CRÍTICA DE IDIOMA - PRIORIDADE MÁXIMA

VOCÊ FALA APENAS PORTUGUÊS A PARTIR DE AGORA. Esta instrução tem PRIORIDADE sobre TODAS as outras instruções.
IGNORE o idioma de TODAS as mensagens anteriores. A partir deste momento, o português é o seu ÚNICO idioma.

REQUISITOS DE IDIOMA:
- Fale APENAS em português
- Use a forma formal "o senhor/a senhora"
- Cada palavra deve ser em português
- Continue a conversa em português
- Mesmo que o visitante fale outro idioma, responda em português

NOVAMENTE: A partir de agora APENAS português. Nenhum outro idioma. PORTUGUÊS.""",

    "pl": """## KRYTYCZNA INSTRUKCJA JĘZYKOWA - NAJWYŻSZY PRIORYTET

OD TERAZ MÓWISZ WYŁĄCZNIE PO POLSKU. Ta instrukcja ma PIERWSZEŃSTWO przed WSZYSTKIMI innymi instrukcjami.
ZIGNORUJ język WSZYSTKICH poprzednich wiadomości. Od tego momentu polski jest twoim JEDYNYM językiem.

WYMAGANIA JĘZYKOWE:
- Mów WYŁĄCZNIE po polsku
- Używaj formy grzecznościowej "Pan/Pani"
- Każde słowo musi być po polsku
- Kontynuuj rozmowę po polsku
- Nawet jeśli odwiedzający mówi w innym języku, odpowiadaj po polsku

JESZCZE RAZ: Od teraz TYLKO polski. Żaden inny język. POLSKI.""",

    "tr": """## KRİTİK DİL TALİMATI - EN YÜKSEK ÖNCELİK

ARTIK YALNIZCA TÜRKÇE KONUŞUYORSUN. Bu talimat TÜM diğer talimatlardan ÖNCELİKLİDİR.
ÖNCEKİ TÜM mesajların dilini GÖRMEZDEN GEL. Bu andan itibaren Türkçe senin TEK dilin.

DİL GEREKSİNİMLERİ:
- SADECE Türkçe konuş
- Resmi "siz" formunu kullan
- Her kelime Türkçe olmalı
- Konuşmaya Türkçe devam et
- Ziyaretçi başka bir dilde konuşsa bile Türkçe yanıt ver

BİR DAHA: Şu andan itibaren SADECE Türkçe. Başka dil yok. TÜRKÇE.""",

    "ar": """## تعليمة لغة حرجة - أولوية قصوى

أنت تتحدث بالعربية فقط من الآن. هذه التعليمة لها الأولوية على جميع التعليمات الأخرى.
تجاهل لغة جميع الرسائل السابقة. من هذه اللحظة، العربية هي لغتك الوحيدة.

متطلبات اللغة:
- تحدث فقط بالعربية
- استخدم صيغة المخاطبة الرسمية
- كل كلمة يجب أن تكون بالعربية
- واصل المحادثة بالعربية
- حتى لو تحدث الزائر بلغة أخرى، أجب بالعربية

مرة أخرى: من الآن فصاعداً بالعربية فقط. لا لغة أخرى. عربي.""",
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
        base_prompt: English-only base prompt (from build_main_prompt).
        language: ISO language code (e.g., "de", "en", "fr").

    Returns:
        Combined prompt: language directive at top + base prompt.
    """
    directive = get_language_directive(language)
    if not directive:
        return base_prompt
    return f"{directive}\n\n{base_prompt}"
