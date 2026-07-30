import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import build_prompt, load_knowledge, retrieve_context


class ChatbotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.knowledge = load_knowledge(Path("data/synthetic_knowledge.json"))

    def test_retrieve_context_for_tracking_question(self) -> None:
        context = retrieve_context("How do I track my package?", self.knowledge)
        self.assertTrue(context)
        self.assertIn("track", context[0]["question"].lower())

    def test_build_prompt_contains_context_and_style(self) -> None:
        context = retrieve_context("What if my delivery is delayed?", self.knowledge)
        prompt = build_prompt("What if my delivery is delayed?", context, "few-shot")
        self.assertIn("Example 1", prompt)
        self.assertIn("Context:", prompt)
        self.assertIn("delayed", prompt.lower())

    def test_retrieve_context_for_capstone_question(self) -> None:
        context = retrieve_context("How should I compare open-source models for my capstone?", self.knowledge)
        self.assertTrue(context)
        self.assertTrue(any("capstone" in item["question"].lower() for item in context))


if __name__ == "__main__":
    unittest.main()
