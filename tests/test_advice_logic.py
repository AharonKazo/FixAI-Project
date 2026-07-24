from app_helpers import build_local_advice, build_ai_result


def test_build_local_advice_uses_title_keywords():
    advice = build_local_advice("screen cracked")
    assert "הערכת מחיר משוערת" in advice
    assert "מסך" in advice or "מסך" in advice.lower()


def test_build_ai_result_returns_fallback_without_api_key():
    advice = build_ai_result(title="keyboard", api_key="", genai_module=None)
    assert "הערכת מחיר משוערת" in advice
