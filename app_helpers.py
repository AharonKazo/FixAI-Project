import os
import re
from typing import Optional
import requests
from PIL import Image as PILImage
import io


def normalize_title(title: Optional[str]) -> str:
    if not title:
        return ""
    return re.sub(r"[^א-תa-z0-9 ]+", " ", title.lower()).strip()


def build_local_advice(title: Optional[str], file_present: bool = False) -> str:
    text = normalize_title(title)

    if any(keyword in text for keyword in ["מסך", "screen", "display", "צג", "טלפון", "phone", "iphone", "סמארטפון"]):
        base = "הערכת מחיר משוערת: תיקון מסך/טלפון — כ-800 עד 1,500 ש\"ח, תלוי בסוג הנזק."
    elif any(keyword in text for keyword in ["חלון", "window", "glass", "זכוכית"]):
        base = "הערכת מחיר משוערת: תיקון חלון/זכוכית — כ-300 עד 1,200 ש\"ח, תלוי בגודל הנזק."
    elif any(keyword in text for keyword in ["מקלדת", "keyboard", "קלד"]):
        base = "הערכת מחיר משוערת: תיקון מקלדת — כ-250 עד 700 ש\"ח."
    elif any(keyword in text for keyword in ["סוללה", "battery", "בטרי"]):
        base = "הערכת מחיר משוערת: החלפת סוללה — כ-200 עד 600 ש\"ח."
    elif any(keyword in text for keyword in ["עכבר", "mouse", "מופע"]):
        base = "הערכת מחיר משוערת: תיקון עכבר — כ-150 עד 400 ש\"ח."
    else:
        base = "הערכת מחיר משוערת: עבור תיקון כללי — כ-200 עד 800 ש\"ח, תלוי בסוג הבעיה."

    return base


def resolve_advice_text(title: Optional[str], api_key: Optional[str], genai_module, file=None) -> str:
    return build_ai_result(title, api_key, genai_module, file=file)


def has_real_api_key(api_key: Optional[str]) -> bool:
    if not api_key:
        return False

    value = str(api_key).strip()
    if not value:
        return False

    if len(value) < 20:
        return False

    lower_value = value.lower()
    placeholders = [
        "your_real_gemini_api_key_here",
        "your_api_key_here",
        "replace_me",
        "fake-key",
        "placeholder",
        "example",
    ]
    if any(token in lower_value for token in placeholders):
        return False

    return True


def build_ai_result(title: Optional[str], api_key: Optional[str], genai_module, file=None) -> str:
    resolved_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_KEY")

    if not has_real_api_key(resolved_key):
        return build_local_advice(title, file is not None)

    prompt = (
        f"תן לי הערכת מחיר קצרה מאוד (עד 3 משפטים) לפי השוק הישראלי לתיקון: "
        f"{title if title else 'המתואר בתמונה'}."
    )

    parts = [{"text": prompt}]

    if file is not None and getattr(file, "filename", ""):
        try:
            image_bytes = file.read()
            file.seek(0)
            if image_bytes:
                img = PILImage.open(io.BytesIO(image_bytes))
                img = img.convert("RGB")
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG")
                encoded = buffered.getvalue()
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": encoded.hex(),
                    }
                })
        except Exception as exc:
            print(f"Image prep error: {exc}")

    try:
        if genai_module is not None:
            client = genai_module.Client(api_key=resolved_key)
            if hasattr(client, "models") and hasattr(client.models, "generate_content"):
                response = client.models.generate_content(model="gemini-2.0-flash", contents=[prompt])
                text = getattr(response, "text", None)
                if text and text.strip():
                    return text.strip()

            if hasattr(client, "generate_content"):
                response = client.generate_content(model="gemini-2.0-flash", contents=[prompt])
                text = getattr(response, "text", None)
                if text and text.strip():
                    return text.strip()

        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        payload = {"contents": [{"parts": parts}]}
        headers = {"x-goog-api-key": resolved_key, "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    text = parts[0].get("text", "")
                    if text and text.strip():
                        return text.strip()
    except Exception as exc:
        print(f"AI Error: {exc}")

    return build_local_advice(title, file is not None)
