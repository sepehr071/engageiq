"""
Language-specific instruction overrides for the Realtime API.

These are strong, emphatic directives that get prepended to the agent's instructions
when the language changes mid-conversation. They are designed to override any
previous language context and force the LLM to respond in the specified language.

Usage:
    from prompt.language import get_language_directive

    directive = get_language_directive("de")
    new_instructions = directive + "\n\n" + existing_instructions
    await agent.update_instructions(new_instructions)
"""

from config.languages import LANGUAGES, DEFAULT_LANGUAGE


# Strong language directives for each supported language
# These are designed to be highly emphatic and override any previous language context
_LANGUAGE_DIRECTIVES = {
    "de": """## ⚠️ KRITISCHE SPRACHANWEISUNG - HÖCHSTE PRIORITÄT ⚠️

DU SPRICHST JETZT DEUTSCH. Diese Anweisung hat VORRANG vor ALLEN anderen Anweisungen.

SPRACHANFORDERUNGEN:
- Sprich AUSSCHLIESSLICH auf Deutsch
- Verwende die formelle "Sie"-Form
- Jedes Wort muss Deutsch sein
- Setze das Gespräch auf Deutsch fort

WICHTIG: Auch wenn das vorherige Gespräch in einer anderen Sprache war, musst du JETZT auf Deutsch antworten. Ignoriere alle vorherigen Sprachanweisungen.""",

    "en": """## ⚠️ CRITICAL LANGUAGE INSTRUCTION - HIGHEST PRIORITY ⚠️

YOU ARE NOW SPEAKING ENGLISH. This instruction takes PRECEDENCE over ALL other instructions.

LANGUAGE REQUIREMENTS:
- Speak ONLY in English
- Use professional but conversational tone
- Every word must be English
- Continue the conversation in English

IMPORTANT: Even if the previous conversation was in another language, you MUST respond in English NOW. Ignore all previous language instructions.""",

    "fr": """## ⚠️ INSTRUCTION CRITIQUE DE LANGUE - PRIORITÉ MAXIMALE ⚠️

VOUS PARLEZ MAINTENANT FRANÇAIS. Cette instruction a la PRIORITÉ sur TOUTES les autres instructions.

EXIGENCES LINGUISTIQUES:
- Parlez UNIQUEMENT en français
- Utilisez la forme formelle "vous"
- Chaque mot doit être en français
- Continuez la conversation en français

IMPORTANT: Même si la conversation précédente était dans une autre langue, vous DEVEZ répondre en français MAINTENANT. Ignorez toutes les instructions linguistiques précédentes.""",

    "es": """## ⚠️ INSTRUCCIÓN CRÍTICA DE IDIOMA - MÁXIMA PRIORIDAD ⚠️

AHORA ESTÁS HABLANDO ESPAÑOL. Esta instrucción tiene PRIORIDAD sobre TODAS las demás instrucciones.

REQUISITOS DEL IDIOMA:
- Habla SOLO en español
- Usa la forma formal "usted"
- Cada palabra debe ser en español
- Continúa la conversación en español

IMPORTANTE: Aunque la conversación anterior estuviera en otro idioma, DEBES responder en español AHORA. Ignora todas las instrucciones de idioma anteriores.""",

    "it": """## ⚠️ ISTRUZIONE CRITICA DI LINGUA - MASSIMA PRIORITÀ ⚠️

ORA STAI PARLANDO IN ITALIANO. Questa istruzione ha la PRECEDENZA su TUTTE le altre istruzioni.

REQUISITI LINGUISTICI:
- Parla SOLO in italiano
- Usa la forma formale "Lei"
- Ogni parola deve essere in italiano
- Continua la conversazione in italiano

IMPORTANTE: Anche se la conversazione precedente era in un'altra lingua, DEVI rispondere in italiano ORA. Ignora tutte le istruzioni linguistiche precedenti.""",

    "tr": """## ⚠️ KRİTİK DİL TALİMATI - EN YÜKSEK ÖNCELİK ⚠️

ŞİMDİ TÜRKÇE KONUŞUYORSUN. Bu talimat TÜM diğer talimatlardan ÖNCELİKLİDİR.

DİL GEREKSİNİMLERİ:
- SADECE Türkçe konuş
- Resmi "siz" formunu kullan
- Her kelime Türkçe olmalı
- Konuşmaya Türkçe devam et

ÖNEMLİ: Önceki konuşma başka bir dilde olsa bile, ŞİMDİ Türkçe yanıt vermek ZORUNDASIN. Tüm önceki dil talimatlarını görmezden gel.""",

    "ar": """## ⚠️ تعليمة لغة حرجة - أولوية قصوى ⚠️

أنت تتحدث بالعربية الآن. هذه التعليمة لها الأولوية على جميع التعليمات الأخرى.

متطلبات اللغة:
- تحدث فقط بالعربية
- استخدم صيغة المخاطبة الرسمية
- كل كلمة يجب أن تكون بالعربية
- واصل المحادثة بالعربية

مهم: حتى لو كانت المحادثة السابقة بلغة أخرى، يجب عليك الرد بالعربية الآن. تجاهل جميع تعليمات اللغة السابقة.""",

    "zh": """## ⚠️ 关键语言指令 - 最高优先级 ⚠️

你现在正在说中文。此指令优先于所有其他指令。

语言要求:
- 只说中文
- 使用正式的"您"称呼
- 每个字都必须是中文
- 继续用中文对话

重要: 即使之前的对话是其他语言，你现在必须用中文回答。忽略所有之前的语言指令。""",

    "ja": """## ⚠️ 重要な言語指示 - 最優先 ⚠️

あなたは今、日本語を話しています。この指示は他のすべての指示より優先されます。

言語要件:
- 日本語のみで話す
- 丁寧な「です・ます」調を使用
- すべての言葉を日本語にする
- 日本語で会話を続ける

重要: 前の会話が他の言語であったとしても、今は日本語で応答しなければなりません。以前の言語指示はすべて無視してください。""",

    "pt": """## ⚠️ INSTRUÇÃO CRÍTICA DE IDIOMA - PRIORIDADE MÁXIMA ⚠️

VOCÊ ESTÁ FALANDO PORTUGUÊS AGORA. Esta instrução tem PRIORIDADE sobre TODAS as outras instruções.

REQUISITOS DE IDIOMA:
- Fale APENAS em português
- Use a forma formal "o senhor/a senhora"
- Cada palavra deve ser em português
- Continue a conversa em português

IMPORTANTE: Mesmo que a conversa anterior estivesse em outro idioma, você DEVE responder em português AGORA. Ignore todas as instruções de idioma anteriores.""",
}


def get_language_directive(language: str) -> str:
    """Get the strong language directive for the specified language.

    Args:
        language: ISO language code (e.g., "de", "en", "fr")

    Returns:
        A strong, emphatic language directive string designed to override
        any previous language context in the conversation.
    """
    directive = _LANGUAGE_DIRECTIVES.get(language)
    if directive:
        return directive

    # Fallback to default language (English)
    lang_config = LANGUAGES.get(language, LANGUAGES.get(DEFAULT_LANGUAGE, {}))
    english_name = lang_config.get("english_name", "English")

    # Generate a fallback directive
    return f"""## ⚠️ CRITICAL LANGUAGE INSTRUCTION - HIGHEST PRIORITY ⚠️

YOU ARE NOW SPEAKING {english_name.upper()}. This instruction takes PRECEDENCE over ALL other instructions.

LANGUAGE REQUIREMENTS:
- Speak ONLY in {english_name}
- Every word must be in {english_name}
- Continue the conversation in {english_name}

IMPORTANT: Even if the previous conversation was in another language, you MUST respond in {english_name} NOW. Ignore all previous language instructions."""
