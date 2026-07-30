import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app_streamlit import build_chat_payload


class StreamlitAppTests(unittest.TestCase):
    def test_build_chat_payload_contains_question_model_and_style(self) -> None:
        payload = build_chat_payload("How do I track my package?", "llama3.2:3b", "few-shot")
        self.assertEqual(payload["question"], "How do I track my package?")
        self.assertEqual(payload["model"], "llama3.2:3b")
        self.assertEqual(payload["style"], "few-shot")


if __name__ == "__main__":
    unittest.main()
