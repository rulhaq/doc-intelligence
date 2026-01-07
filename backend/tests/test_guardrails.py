import unittest

from app.core.guardrails import (
    detect_explicit_language,
    detect_language,
    greeting_response,
    insufficient_info_response,
    is_greeting,
)


class GuardrailTests(unittest.TestCase):
    def test_greeting_english_shortcuts(self):
        self.assertTrue(is_greeting("hello"))
        self.assertIn("Hello", greeting_response("en"))

    def test_greeting_arabic_shortcuts(self):
        self.assertTrue(is_greeting("مرحبا"))
        self.assertIn("مرحباً", greeting_response("ar"))

    def test_language_detection_arabic(self):
        self.assertEqual(detect_language("هل يمكنك تلخيص الوقائع؟"), "ar")

    def test_language_detection_english(self):
        self.assertEqual(detect_language("Summarize the case facts."), "en")

    def test_explicit_language_request_overrides(self):
        self.assertEqual(detect_explicit_language("Summarize in Arabic."), "ar")

    def test_insufficient_info_response(self):
        response = insufficient_info_response("en")
        self.assertIn("don't have enough information", response)
        self.assertIn("specify", response)


if __name__ == "__main__":
    unittest.main()
