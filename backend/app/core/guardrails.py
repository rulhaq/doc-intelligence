"""Guardrails and language utilities for chat."""
from __future__ import annotations

import re
from typing import Optional, Tuple

_EN_GREETING_PATTERNS = {
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "greetings",
}

_AR_GREETING_PATTERNS = {
    "مرحبا",
    "مرحباً",
    "أهلا",
    "أهلاً",
    "اهلا",
    "السلام عليكم",
    "السلام عليكم ورحمة الله",
    "صباح الخير",
    "مساء الخير",
}

_ILLEGAL_EN = [
    "fabricate evidence",
    "falsify evidence",
    "fake evidence",
    "plant evidence",
    "tamper with evidence",
    "destroy evidence",
    "hide evidence",
    "intimidate witness",
    "threaten witness",
    "bribe",
    "alter records",
    "forge documents",
]

_ILLEGAL_AR = [
    "تزوير الأدلة",
    "تلفيق الأدلة",
    "فبركة الأدلة",
    "زرع الأدلة",
    "إتلاف الأدلة",
    "إخفاء الأدلة",
    "ترهيب الشهود",
    "تهديد الشهود",
    "رشوة",
    "تغيير السجلات",
    "تزوير المستندات",
]

_LANGUAGE_HINTS_EN = re.compile(
    r"\b(in english|english please|respond in english|answer in english)\b",
    re.IGNORECASE,
)
_LANGUAGE_HINTS_AR = re.compile(
    r"(باللغة العربية|بالعربية|باللغة العربيّة|عربي|بالعربي)",
    re.IGNORECASE,
)
_LANGUAGE_HINTS_AR_EN = re.compile(
    r"\b(in arabic|arabic please|respond in arabic|answer in arabic)\b",
    re.IGNORECASE,
)


def _count_lang_chars(text: str) -> Tuple[int, int]:
    arabic = sum(1 for char in text if "\u0600" <= char <= "\u06FF")
    latin = sum(1 for char in text if "a" <= char.lower() <= "z")
    return arabic, latin


def detect_explicit_language(text: str) -> Optional[str]:
    """Return 'ar', 'en', or None if no explicit preference detected."""
    if _LANGUAGE_HINTS_AR.search(text) or _LANGUAGE_HINTS_AR_EN.search(text):
        return "ar"
    if _LANGUAGE_HINTS_EN.search(text):
        return "en"
    return None


def detect_language(text: str) -> Optional[str]:
    """Detect dominant language from text."""
    arabic, latin = _count_lang_chars(text)
    if arabic == 0 and latin == 0:
        return None
    if arabic > latin:
        return "ar"
    if latin > arabic:
        return "en"
    return None


def is_ambiguous_language(text: str) -> bool:
    arabic, latin = _count_lang_chars(text)
    if arabic == 0 or latin == 0:
        return False
    total = arabic + latin
    return abs(arabic - latin) / max(total, 1) < 0.2


def is_greeting(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    if not normalized:
        return False
    if normalized in _EN_GREETING_PATTERNS or normalized in _AR_GREETING_PATTERNS:
        return True
    if len(normalized.split()) <= 3:
        for phrase in _EN_GREETING_PATTERNS:
            if phrase in normalized:
                return True
        for phrase in _AR_GREETING_PATTERNS:
            if phrase in normalized:
                return True
    return False


def is_illegal_request(text: str) -> bool:
    normalized = text.lower()
    for phrase in _ILLEGAL_EN:
        if phrase in normalized:
            return True
    for phrase in _ILLEGAL_AR:
        if phrase in text:
            return True
    return False


def greeting_response(lang: str) -> str:
    if lang == "ar":
        return "مرحباً! أنا هنا للمساعدة في أسئلة ملف القضية. ماذا تريد أن تعرف؟"
    return "Hello! I'm here to help with questions about the case file. What would you like to know?"


def illegal_request_response(lang: str) -> str:
    if lang == "ar":
        return (
            "لا أستطيع المساعدة في طلبات غير قانونية أو غير أخلاقية. "
            "يمكنني المساعدة في الإجراءات القانونية السليمة أو أفضل ممارسات التعامل مع الأدلة."
        )
    return (
        "I can't assist with illegal or unethical requests. "
        "I can help with lawful procedures or best practices for evidence handling."
    )


def insufficient_info_response(lang: str) -> str:
    if lang == "ar":
        return (
            "لا توجد معلومات كافية في ملف القضية للإجابة بشكل موثوق. "
            "هل يمكنك تحديد الوثيقة أو رقم الصفحة أو الكلمات المفتاحية؟"
        )
    return (
        "I don't have enough information in the case file to answer reliably. "
        "Can you specify the document, page, or key terms involved?"
    )


def ambiguous_language_response() -> str:
    return "Do you prefer Arabic or English for the response? / هل تفضل العربية أم الإنجليزية للإجابة؟"


def empty_message_response(lang: str) -> str:
    if lang == "ar":
        return "يرجى إدخال سؤال واضح عن ملف القضية."
    return "Please enter a clear question about the case file."
