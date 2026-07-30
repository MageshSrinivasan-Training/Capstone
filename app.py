from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
DEFAULT_KNOWLEDGE_FILE = Path(__file__).resolve().parent / "data" / "synthetic_knowledge.json"


def load_knowledge(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def retrieve_context(question: str, knowledge: dict) -> list[dict]:
    faq_items = knowledge.get("faq", [])
    lowered_question = question.lower()
    question_tokens = set(lowered_question.replace("?", "").split())
    matches: list[tuple[int, dict]] = []

    carrier_keywords = [
        "track", "tracking", "delay", "delayed", "delivery", "return", "refund",
        "address", "payment", "claim", "damage", "damaged", "lost", "missing",
        "pickup", "support", "shipment", "carrier", "package"
    ]

    for item in faq_items:
        q = item.get("question", "").lower()
        a = item.get("answer", "").lower()
        item_text = f"{q} {a}"
        item_tokens = set(item_text.replace("?", "").split())

        if any(keyword in lowered_question for keyword in carrier_keywords) and any(keyword in item_text for keyword in carrier_keywords):
            overlap = len(question_tokens & item_tokens)
            if overlap or q in lowered_question or lowered_question in q:
                matches.append((overlap, item))
        elif q in lowered_question or lowered_question in q:
            matches.append((len(question_tokens & item_tokens), item))

    if not matches:
        return faq_items[:3]

    ranked_matches = sorted(matches, key=lambda entry: (-entry[0], entry[1].get("question", "")))
    return [item for _, item in ranked_matches[:3]]


def build_prompt(question: str, context: list[dict], style: str) -> str:
    context_text = "\n".join(
        f"Q: {item['question']}\nA: {item['answer']}"
        for item in context
    )

    if style == "zero-shot":
        return (
            "You are a helpful student carrier assistance chatbot for capstone and academic support. "
            "Answer clearly and concisely using the provided context. "
            "Focus on model comparison, evaluation sections, responsible AI documentation, and report structure. "
            "If the answer is not in the context, say that you do not know.\n\n"
            f"Context:\n{context_text}\n\nUser question: {question}\nAnswer:"
        )

    if style == "few-shot":
        return (
            "You are a helpful student carrier assistance chatbot for capstone and academic support. "
            "Follow the examples below and answer like a study assistant.\n\n"
            "Example 1:\n"
            "User: How can I track my package?\n"
            "Assistant: Use the tracking number in the carrier portal or the order confirmation email.\n\n"
            "Example 2:\n"
            "User: What if my parcel is delayed?\n"
            "Assistant: Check the latest carrier update and contact support if it remains delayed for more than 48 hours.\n\n"
            f"Context:\n{context_text}\n\nUser question: {question}\nAnswer:"
        )

    if style == "chain-of-thought":
        return (
            "You are a helpful student carrier assistance chatbot for capstone and academic support. "
            "Reason step by step internally, then provide a concise answer. "
            "Use the context carefully and avoid speculation. "
            "Focus on practical academic actions such as model comparison, evaluation sections, responsible AI documentation, and report structure.\n\n"
            f"Context:\n{context_text}\n\nUser question: {question}\nAnswer:"
        )

    raise ValueError(f"Unsupported prompt style: {style}")


def call_ollama(base_url: str, model: str, prompt: str) -> str:
    endpoint = urllib.parse.urljoin(base_url.rstrip("/") + "/", "api/generate")
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    request = urllib.request.Request(endpoint, data=payload, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Unable to reach Ollama at {base_url}. Start it with 'ollama serve' and pull the model '{model}'."
        ) from exc

    parts = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        payload_item = json.loads(line)
        parts.append(payload_item.get("response", ""))

    return "".join(parts).strip() or "No response was generated."


def chat_once(question: str, knowledge: dict, base_url: str, model: str, style: str) -> str:
    context = retrieve_context(question, knowledge)
    prompt = build_prompt(question, context, style)
    return call_ollama(base_url, model, prompt)


def run_cli() -> int:
    parser = argparse.ArgumentParser(description="Local carrier assistance chatbot powered by Ollama")
    parser.add_argument("--message", help="Single question to answer")
    parser.add_argument("--knowledge-file", default=str(DEFAULT_KNOWLEDGE_FILE), help="Path to a JSON knowledge file")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Ollama model name")
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL, help="Base URL for the Ollama server")
    parser.add_argument(
        "--prompt-style",
        choices=["zero-shot", "few-shot", "chain-of-thought"],
        default="zero-shot",
        help="Prompt strategy to use",
    )
    args = parser.parse_args()

    knowledge_path = Path(args.knowledge_file).resolve()
    knowledge = load_knowledge(knowledge_path)

    if args.message:
        response = chat_once(args.message, knowledge, args.ollama_url, args.model, args.prompt_style)
        print(response)
        return 0

    print("Carrier Assistance Chatbot ready. Type 'exit' to quit.")
    while True:
        try:
            question = input("You: ").strip()
        except EOFError:
            print("\nGoodbye!")
            return 0

        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            return 0

        if not question:
            continue

        try:
            answer = chat_once(question, knowledge, args.ollama_url, args.model, args.prompt_style)
        except RuntimeError as exc:
            print(str(exc))
            print("Install Ollama, start it, and ensure the model is available.")
            return 1

        print(f"Assistant: {answer}\n")

    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
