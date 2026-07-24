from app_helpers import build_local_advice, build_ai_result, resolve_advice_text


def test_build_local_advice_uses_title_keywords():
    advice = build_local_advice("screen cracked")
    assert "הערכת מחיר משוערת" in advice
    assert "מסך" in advice or "מסך" in advice.lower()


def test_build_ai_result_returns_fallback_without_api_key():
    advice = build_ai_result(title="keyboard", api_key="", genai_module=None)
    assert "הערכת מחיר משוערת" in advice


def test_build_local_advice_handles_phone_titles_more_specifically():
    advice = build_local_advice("iphone screen cracked")
    assert "טלפון" in advice or "מסך" in advice
    assert "כללי" not in advice


def test_build_local_advice_handles_window_titles():
    advice = build_local_advice("window broken")
    assert "חלון" in advice or "זכוכית" in advice
    assert "כללי" not in advice


def test_resolve_advice_text_uses_fallback_when_genai_errors():
    class BoomGenAI:
        def Client(self, api_key):
            raise RuntimeError("boom")

    advice = resolve_advice_text("screen", "fake-key", BoomGenAI(), file=None)
    assert "הערכת מחיר משוערת" in advice


def test_build_ai_result_ignores_placeholder_api_key():
    class FakeGenAI:
        class Client:
            def __init__(self, api_key):
                self.api_key = api_key

            @property
            def models(self):
                return type("Models", (), {"generate_content": lambda *args, **kwargs: type("Response", (), {"text": "AI output"})()})()

    advice = build_ai_result(title="keyboard", api_key="YOUR_REAL_GEMINI_API_KEY_HERE", genai_module=FakeGenAI)
    assert "הערכת מחיר משוערת" in advice


def test_build_ai_result_uses_http_gemini_when_key_is_valid(monkeypatch):
    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "candidates": [
                    {
                        "content": {
                            "parts": [{"text": "הערכת מחיר משוערת: תיקון חלון/זכוכית — כ-300 עד 1,200 ש\"ח."}]
                        }
                    }
                ]
            }

    def fake_post(url, headers=None, json=None, timeout=10):
        return FakeResponse()

    monkeypatch.setattr("app_helpers.requests.post", fake_post)
    advice = build_ai_result(title="חלון שבור", api_key="a" * 30, genai_module=None)
    assert "חלון" in advice or "זכוכית" in advice
