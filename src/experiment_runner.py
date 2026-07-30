"""Simple experiment runner for comparing prompt strategies locally."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from app import chat_once, load_knowledge
from src.prompts import CHAIN_OF_THOUGHT, FEW_SHOT, ZERO_SHOT

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_PATH = ROOT / "data" / "synthetic_knowledge.json"
DATASET_PATH = ROOT / "data" / "raw" / "student_support_eval.csv"
OUTPUT_PATH = ROOT / "docs" / "03_prompt_experiment_log.csv"


def build_dataset() -> list[dict]:
    if not DATASET_PATH.exists():
        return [
            {"id": 1, "question": "How do I track my package?", "expected_topic": "tracking"},
            {"id": 2, "question": "What should I do if my delivery is delayed?", "expected_topic": "delay"},
        ]

    with DATASET_PATH.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def run_experiments(model: str = "llama3.2:3b", base_url: str = "http://localhost:11434") -> list[dict]:
    knowledge = load_knowledge(KNOWLEDGE_PATH)
    prompts = {
        "zero-shot": ZERO_SHOT,
        "few-shot": FEW_SHOT,
        "chain-of-thought": CHAIN_OF_THOUGHT,
    }
    rows: list[dict] = []

    for item in build_dataset():
        for style, prompt_template in prompts.items():
            question = item["question"]
            response = chat_once(question, knowledge, base_url, model, style)
            rows.append(
                {
                    "id": item["id"],
                    "question": question,
                    "prompt_style": style,
                    "prompt_template": prompt_template,
                    "response": response,
                    "model": model,
                }
            )

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "question", "prompt_style", "prompt_template", "response", "model"])
        writer.writeheader()
        writer.writerows(rows)

    return rows


if __name__ == "__main__":
    run_experiments()
