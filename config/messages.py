"""
Agent messages, UI buttons, and conversation rules for the EngageIQ voice agent.
All visitor-facing text lives here for easy localization and editing.

Agents   -> config/agents.py
Products -> config/products.py
Services -> config/services.py
"""

from config.company import COMPANY

# =============================================================================
# GREETING MESSAGES — per language, used as the opening line
# =============================================================================

GREETING_MESSAGES = {
    "de": (
        "Willkommen bei Ayand AI auf der EuroShop! "
        "Ich bin Ihr digitaler Concierge. "
        "Wir machen unsichtbare Kundennachfrage sichtbar. "
        "Was fuehrt Sie heute zu uns?"
    ),
    "en": (
        "Welcome to Ayand AI at EuroShop! "
        "I'm your digital concierge. "
        "We make invisible customer demand visible. "
        "What brings you to our booth today?"
    ),
    "fr": (
        "Bienvenue chez Ayand AI a l'EuroShop! "
        "Je suis votre concierge digital. "
        "Nous rendons visible la demande client invisible. "
        "Qu'est-ce qui vous amene aujourd'hui?"
    ),
    "es": (
        "Bienvenido a Ayand AI en EuroShop! "
        "Soy su concierge digital. "
        "Hacemos visible la demanda invisible del cliente. "
        "Que le trae hoy a nuestro stand?"
    ),
    "it": (
        "Benvenuto da Ayand AI all'EuroShop! "
        "Sono il suo concierge digitale. "
        "Rendiamo visibile la domanda invisibile dei clienti. "
        "Cosa la porta al nostro stand oggi?"
    ),
    "tr": (
        "EuroShop'ta Ayand AI'ye hosgeldiniz! "
        "Ben dijital concierge'inizim. "
        "Gorunmeyen musteri talebini gorunur kiliyoruz. "
        "Buguen bizi ziyaret etmenizin sebebi nedir?"
    ),
    "ar": (
        "Ayand AI EuroShop "
        "ana el concierge el raqami. "
        "nejaal talab el omala2 el gheer mar2i mar2i. "
        "shu elli gabak el youm?"
    ),
    "zh": (
        "Huan ying lai dao EuroShop de Ayand AI zhan wei! "
        "Wo shi nin de shu zi li bin. "
        "Wo men rang kan bu jian de ke hu xu qiu bian de ke jian. "
        "Jin tian shi shen me rang nin lai dao wo men zhan wei?"
    ),
    "ja": (
        "EuroShop no Ayand AI he youkoso! "
        "Watashi wa dejitaru konshieruju desu. "
        "Mienai kokyaku juyo wo mieru ka shimasu. "
        "Kyo wa nani ga kikkake de irasshaimashita ka?"
    ),
    "pt": (
        "Bem-vindo a Ayand AI na EuroShop! "
        "Sou o seu concierge digital. "
        "Tornamos visivel a procura invisivel do cliente. "
        "O que o traz ao nosso stand hoje?"
    ),
}

# =============================================================================
# AGENT MESSAGES — responses for various conversation situations
# =============================================================================

AGENT_MESSAGES = {
    # --- Declining / Redirecting ---
    "decline_contact": (
        "No problem at all! If you change your mind or have more questions later, "
        "I'm right here. Enjoy the rest of EuroShop!"
    ),
    "decline_contact_de": (
        "Kein Problem! Wenn Sie es sich anders ueberlegen oder spaeter Fragen haben, "
        "bin ich hier. Viel Spass noch auf der EuroShop!"
    ),

    "off_topic_redirect": (
        "That's outside my area, but I can tell you all about how to capture "
        "invisible customer demand. Would you like to hear how EngageIQ works?"
    ),
    "off_topic_redirect_de": (
        "Das liegt leider ausserhalb meines Bereichs, aber ich kann Ihnen alles "
        "darueber erzaehlen, wie man unsichtbare Kundennachfrage sichtbar macht. "
        "Moechten Sie hoeren, wie EngageIQ funktioniert?"
    ),

    # --- Clarification ---
    "rephrase_request": (
        "I didn't quite catch that. Could you rephrase your question?"
    ),
    "rephrase_request_de": (
        "Das habe ich leider nicht ganz verstanden. "
        "Koennten Sie Ihre Frage nochmal anders formulieren?"
    ),

    # --- Validation ---
    "invalid_email": "That doesn't look like a valid email address. Could you try again?",
    "invalid_email_de": "Das scheint keine gueltige E-Mail-Adresse zu sein. Koennten Sie es nochmal versuchen?",

    # --- Technical Issues ---
    "technical_error": (
        "I'm having a small technical issue. Let me try again. "
        "If it persists, our team at the booth can help you directly."
    ),
    "technical_error_de": (
        "Ich habe gerade ein kleines technisches Problem. Ich versuche es nochmal. "
        "Falls es bestehen bleibt, kann unser Team am Stand Ihnen direkt weiterhelfen."
    ),

    "patience_fallback": "One moment please, I'll be right with you.",
    "patience_fallback_de": "Einen kleinen Moment bitte, ich bin gleich wieder fuer Sie da.",

    # --- Chatbot Comparison (key differentiator) ---
    "chatbot_comparison": (
        "Great question. Most chatbots answer questions — EngageIQ is fundamentally different. "
        "We capture demand. We don't wait for someone to ask a question. We understand what "
        "visitors want, score their intent, and route serious buyers to your team in real time. "
        "A chatbot tells you what someone asked. EngageIQ tells you what your market wants."
    ),
    "chatbot_comparison_de": (
        "Gute Frage. Die meisten Chatbots beantworten Fragen — EngageIQ ist grundlegend anders. "
        "Wir erfassen Nachfrage. Wir warten nicht darauf, dass jemand eine Frage stellt. "
        "Wir verstehen, was Besucher wollen, bewerten ihre Kaufabsicht und leiten ernsthafte "
        "Interessenten in Echtzeit an Ihr Team weiter. Ein Chatbot sagt Ihnen, was jemand "
        "gefragt hat. EngageIQ sagt Ihnen, was Ihr Markt will."
    ),

    # --- Lead Email ---
    "lead_email_sent": (
        "I've passed your details to our team. They'll follow up with you shortly. "
        "Is there anything else you'd like to know?"
    ),
    "lead_email_sent_de": (
        "Ich habe Ihre Daten an unser Team weitergeleitet. "
        "Sie werden sich in Kuerze bei Ihnen melden. "
        "Gibt es noch etwas, das Sie wissen moechten?"
    ),

    "lead_email_failed": (
        "Thank you! I had a small technical issue forwarding your details. "
        "Our team is right here at the booth — you can speak with them directly. "
        "Or just email us at moniri@ayand.ai and we'll make sure nothing gets lost."
    ),
    "lead_email_failed_de": (
        "Vielen Dank! Leider hatte ich ein kleines technisches Problem bei der Weiterleitung. "
        "Unser Team ist hier am Stand — Sie koennen direkt mit ihnen sprechen. "
        "Oder schreiben Sie uns einfach an moniri@ayand.ai, dann geht nichts verloren."
    ),

    # --- Summary ---
    "offer_summary": "Would you like me to send you a summary of what we discussed via email?",
    "offer_summary_de": "Moechten Sie, dass ich Ihnen eine Zusammenfassung unseres Gespraechs per E-Mail sende?",

    "summary_sent": "A summary has been sent to your email address.",
    "summary_sent_de": "Eine Zusammenfassung wurde an Ihre E-Mail-Adresse gesendet.",

    "no_summary_thanks": (
        "Thank you for visiting the Ayand AI booth. "
        "Feel free to come back anytime if you have more questions!"
    ),
    "no_summary_thanks_de": (
        "Vielen Dank fuer Ihren Besuch am Ayand AI Stand. "
        "Kommen Sie jederzeit gerne wieder, wenn Sie weitere Fragen haben!"
    ),

    # --- Farewell ---
    "farewell": "Thank you for stopping by! Enjoy the rest of EuroShop.",
    "farewell_de": "Vielen Dank fuer Ihren Besuch! Viel Spass noch auf der EuroShop.",
}

# =============================================================================
# UI BUTTONS — button labels and values shown to visitors
# =============================================================================

UI_BUTTONS = {
    "qualification_confirm": {
        "yes_tell_me_more": "Yes",
        "no_just_browsing": "No",
    },
    "contact_confirm": {
        "yes_share_contact": "Yes",
        "no_thanks": "No",
    },
    "next_step": {
        "meet_team": "Meet the team now",
        "book_call": "Book a follow-up call",
        "send_info": "Send me info via email",
        "just_browsing": "Just browsing, thanks",
    },
    "summary_offer": {
        "yes_send_summary": "Yes",
        "no_summary_needed": "No",
    },
    "product_select": {
        "cariq": "CarIQ (Dealerships)",
        "concierge": "AI Concierge (Clinics)",
        "shelf_twin": "Shelf Digital Twin (Retail)",
    },
    "new_conversation": {
        "start_new": "Start a new conversation",
    },
}

# German UI buttons
UI_BUTTONS_DE = {
    "qualification_confirm": {
        "ja_erzaehlen_sie_mehr": "Ja",
        "nein_ich_schaue_nur": "Nein",
    },
    "contact_confirm": {
        "ja_kontakt_teilen": "Ja",
        "nein_danke": "Nein",
    },
    "next_step": {
        "team_treffen": "Team jetzt treffen",
        "anruf_buchen": "Folgegespraech buchen",
        "info_senden": "Info per E-Mail senden",
        "nur_schauen": "Ich schaue nur, danke",
    },
    "summary_offer": {
        "ja_zusammenfassung": "Ja",
        "nein_nicht_noetig": "Nein",
    },
    "product_select": {
        "cariq": "CarIQ (Autohaeuser)",
        "concierge": "AI Concierge (Kliniken)",
        "shelf_twin": "Shelf Digital Twin (Handel)",
    },
    "new_conversation": {
        "neue_konversation": "Neue Konversation starten",
    },
}

# =============================================================================
# CONVERSATION RULES — injected into every LLM prompt for consistent behavior
# =============================================================================

CONVERSATION_RULES = """IMPORTANT RULES FOR NATURAL CONVERSATION:
Match the visitor's language automatically — respond in whatever language they use.
When speaking German, use 'Sie' form (formal) unless the visitor uses 'du'.
Speak like a real person, not a bot — natural, conversational, confident.
NO bullet points, NO numbered lists, NO dashes in spoken responses.
Short, clear sentences with natural pauses (max 60 words per response).
ONE question maximum at the end of your response, never in the middle.
NEVER repeat information you already shared in the conversation.
NEVER mention personal names — say 'our team' or 'our product specialist'.
NEVER read personal data aloud (names, emails, phone numbers).
Give ONE coherent answer — not multiple separate paragraphs.
You are at EuroShop 2026 in Duesseldorf — keep responses relevant to the trade show context.
Differentiate EngageIQ from chatbots: we capture demand, we don't just answer questions.
"""

# =============================================================================
# EMAIL TEMPLATES — for lead notifications and conversation summaries
# =============================================================================

EMAIL_TEMPLATES = {
    "lead_notification_subject": "EuroShop 2026 Lead: {visitor_name} — {product}",
    "lead_notification_body": """
New lead captured at EuroShop 2026 booth.

Visitor: {visitor_name}
Email: {visitor_email}
Phone: {visitor_phone}
Role: {visitor_role}
Industry: {visitor_industry}
Company: {visitor_company}

Product Interest: {product}
Intent Score: {intent_score}/10
Intent Level: {intent_level}

Challenge: {challenge}
Timeline: {timeline}
Current Tools: {current_tools}

Conversation Summary:
{conversation_summary}

Next Step Agreed: {next_step}

---
Captured by EngageIQ Digital Concierge
{event_name} | {event_dates}
""",

    "summary_subject": "Your conversation with Ayand AI at EuroShop 2026",
    "summary_body": """
Thank you for visiting the Ayand AI booth at EuroShop 2026!

Here's a summary of what we discussed:

{conversation_summary}

Product: {product_name}
{product_description}

Next Steps:
{next_steps}

If you have any questions, reply to this email or reach us at {contact_email}.

{email_closing}
""",
}

EMAIL_SUMMARY_PROMPT = (
    "Summarize this trade show conversation in 3-5 concise bullet points. "
    "Focus on: what the visitor is looking for, which product was discussed, "
    "their intent level, and any agreed next steps. "
    "Keep it factual and professional — this is for internal lead tracking."
)
