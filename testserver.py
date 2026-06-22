import requests
import time
import pytest


BASE_URL = "http://flask_app:5000"
URL = f"{BASE_URL}/add"

data = {
    "title": "Is FixAI working?"
}

def test_add_and_check_db():
    for attempt in range(10):
        try:
            print(f"Attempt {attempt + 1}: Connecting to {URL}...")
            response = requests.post(URL, data=data, timeout=5)

            if response.status_code == 200:
                print("✅ TEST PASSED:")
                is_DB_updated = requests.get(BASE_URL)
                assert "Is FixAI working?" in is_DB_updated.text, "The DB is not updated"
                return

        except Exception as e:
            print(f"⚠️ Service not ready yet... Retrying in 3 seconds. ({e})")
            time.sleep(3)

    print("🚨 TEST FAILED: Max retries reached. Service is down.")
    pytest.fail("Service is down")