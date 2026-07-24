import os
import re
from typing import Optional


def normalize_title(title: Optional[str]) -> str:
    if not title:
        return ""
    return re.sub(r"[^א-תa-z0-9 ]+", " ", title.lower()).strip()


def build_local_advice(title: Optional[str], file_present: bool = False) -> str:
    text = normalize_title(title)

    if any(keyword in text for keyword in ["מסך", "screen", "display", "צג"]):
        base = "הערכת מחיר משוערת: תיקון מסך/צג — כ-800 עד 1,500 ש\"ח, תלוי בסוג הנזק."
    elif any(keyword in text for keyword in ["מקלדת", "keyboard", "קלד"]):
        base = "הערכת מחיר משוערת: תיקון מקלדת — כ-250 עד 700 ש\"ח."
    elif any(keyword in text for keyword in ["סוללה", "battery", "בטרי"]):
        base = "הערכת מחיר משוערת: החלפת סוללה — כ-200 עד 600 ש\"ח."
    elif any(keyword in text for keyword in ["עכבר", "mouse", "מופע"]):
        base = "הערכת מחיר משוערת: תיקון עכבר — כ-150 עד 400 ש\"ח."
    else:
        base = "הערכת מחיר משוערת: עבור תיקון כללי — כ-200 עד 800 ש\"ח, תלוי בסוג הבעיה."

    if file_present:
        base += " קיבלתי גם תמונה, ולכן ההערכה עשויה להיות מדויקת יותר."

    return base


def build_ai_result(title: Optional[str], api_key: Optional[str], genai_module, file=None) -> str:
    if not api_key or not getattr(api_key, "strip", lambda: api_key)():
        return build_local_advice(title, file is not None)

    if genai_module is None:
        return build_local_advice(title, file is not None)

    try:
        client = genai_module.Client(api_key=api_key)
        prompt = (
            f"תן לי הערכת מחיר קצרה מאוד (עד 3 משפטים) לפי השוק הישראלי לתיקון: "
            f"{title if title else 'המתואר בתמונה'}."
        )
        response = client.models.generate_content(model="gemini-flash-lite-latest", contents=[prompt])
        text = getattr(response, "text", None)
        if text and text.strip():
            return text.strip()
    except Exception as exc:
        print(f"AI Error: {exc}")

    return build_local_advice(title, file is not None)
