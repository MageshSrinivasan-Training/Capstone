from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from app import chat_once, load_knowledge

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
DEFAULT_OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
KNOWLEDGE_PATH = Path(__file__).resolve().parent / "data" / "synthetic_knowledge.json"


@st.cache_data(show_spinner=False)
def load_app_knowledge() -> dict:
    return load_knowledge(KNOWLEDGE_PATH)


def build_chat_payload(question: str, model: str, style: str) -> dict:
    return {"question": question, "model": model, "style": style}


st.set_page_config(page_title="Carrier Assistance Chatbot", page_icon="📦", layout="centered")
st.title("Student Carrier Assistance Chatbot")
st.caption("A simple local assistant powered by Ollama and a synthetic student-support knowledge base.")

with st.sidebar:
    st.header("Settings")
    # Present a short list of model choices for convenience (matches UI design)
    model_choice = st.selectbox(
        "Model",
        ["llama3", "mistral", "phi3", "gemma"],
        index=0,
    )
    # Map friendly names to actual Ollama model identifiers (customize as needed)
    MODEL_MAP = {
        "llama3": DEFAULT_MODEL,
        "mistral": "mistral:latest",
        "phi3": "phi3:latest",
        "gemma": "gemma:latest",
    }
    model_name = MODEL_MAP.get(model_choice, DEFAULT_MODEL)
    ollama_url = st.text_input("Ollama URL", value=DEFAULT_OLLAMA_URL)
    prompt_style = st.selectbox("Prompt style", ["zero-shot", "few-shot", "chain-of-thought"])

knowledge = load_app_knowledge()

question = st.text_area("Ask a carrier support question", placeholder="Example: How to learn AI skills?")

if st.button("Get answer"):
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        payload = build_chat_payload(question.strip(), model_name, prompt_style)
        with st.spinner("Generating response..."):
            try:
                answer = chat_once(payload["question"], knowledge, ollama_url, payload["model"], payload["style"])
            except RuntimeError as exc:
                st.error(str(exc))
            else:
                st.success("Answer")
                st.write(answer)
