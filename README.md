# Student Carrier Assistance Chatbot

## Repository Summary
- Purpose: Build and evaluate a local student carrier assistance chatbot that provides knowledge assistance using open-source LLMs via Ollama.
- App: Lightweight Python CLI and Streamlit UI for testing model responses across prompt strategies.
- Experimentation: A small batch runner to compare prompt styles on a carrier-assistance evaluation set.
- Evaluation Artifacts: Auto-generated logs, a model comparison matrix, and documentation files for capstone reporting.
- Outcome: A reproducible workflow from local inference to evidence-backed project documentation.

## Report Section Details

### 1. Problem Statement
This project demonstrates a local student carrier assistance chatbot that provides knowledge assistance for carrier-related questions without depending on a closed hosted inference API. The main objective is to compare prompt strategies and models in a reproducible local setup while keeping the workflow transparent and cost-effective.

### 2. Dataset Source
The evaluation dataset is stored in [data/raw/student_support_eval.csv](data/raw/student_support_eval.csv). It contains a small set of public-safe, synthetic student carrier-assistance questions used to test common scenarios such as tracking, delays, returns, and address updates. The dataset is consumed by [src/experiment_runner.py](src/experiment_runner.py) to run simple prompt-style comparisons.

### 3. Model Comparison
The repository compares common open-source options that are practical for local execution, including Llama 3.2, Phi-3, Mistral, and Gemma. The comparison is documented in [docs/02_model_comparison_matrix.csv](docs/02_model_comparison_matrix.csv), with notes on quality, latency, and suitability for local use.

### 4. Selection Justification with Scoring
The final model choice is justified using lightweight evidence from the comparison matrix and the experiment logs. In this version, the project uses a simple scoring framework based on expected response quality, local practicality, and latency notes. The selected model is Llama 3.2 3B because it offers a strong balance of local usability, response quality, and lower hardware demand.

### 5. Demo Results
The chatbot can be run directly through [app.py](app.py) with a sample question such as a tracking or delay inquiry. The live output is produced by the local Ollama connection, and the prompt strategy can be switched between zero-shot, few-shot, and chain-of-thought.

### 6. Limitations and Future Work
The current evaluation is lightweight and mostly heuristic. Results depend on Ollama availability and local hardware, and the scoring is simple rather than full benchmark-based. Future work could include more test questions, richer evaluation metrics, and broader domain coverage beyond carrier support.

### 7. Documentation of Prompts used
The prompt styles used in the project are documented in [src/prompts.py](src/prompts.py). The repository also records the experiment history in [docs/03_prompt_experiment_log.csv](docs/03_prompt_experiment_log.csv), including zero-shot, few-shot, and chain-of-thought examples.

## Project Structure
- [app.py](app.py): Main chatbot logic and CLI entry point.
- [src/prompts.py](src/prompts.py): Prompt templates for the different prompt strategies.
- [src/experiment_runner.py](src/experiment_runner.py): Simple experiment runner for local prompt comparisons.
- [data/synthetic_knowledge.json](data/synthetic_knowledge.json): Synthetic knowledge base for support responses.
- [data/raw/student_support_eval.csv](data/raw/student_support_eval.csv): Small evaluation dataset.
- [docs/01_capstone_report_template.md](docs/01_capstone_report_template.md): Report template structure.
- [docs/02_model_comparison_matrix.csv](docs/02_model_comparison_matrix.csv): Model comparison notes.
- [docs/03_prompt_experiment_log.csv](docs/03_prompt_experiment_log.csv): Prompt experiment log.

## **Local Run Steps**
1. Install Ollama from https://ollama.com/ and make sure it is available in your terminal.
2. Pull the primary local model used by the project:
   ```bash
   ollama pull llama3.2:3b
   ```
3. Start the local Ollama server in a separate terminal:
   ```bash
   ollama serve
   ```
4. In a second terminal, run the CLI chatbot from the project folder:
   ```bash
   python app.py --message "How should I compare open-source models for my capstone?"
   ```
5. In a third terminal, start the Streamlit UI on port 8501:
   ```bash
   python -m streamlit run app_streamlit.py --server.port 8501 --server.headless true
   ```
6. Open the app in your browser at:
   ```text
   http://localhost:8501
   ```

### Model selector note
The Streamlit UI includes a "Model" dropdown in the sidebar. Friendly names are mapped to Ollama model identifiers in `app_streamlit.py`:

```text
llama3 -> llama3.2:3b
mistral -> mistral:latest
phi3   -> phi3:latest
gemma  -> gemma:latest
```

If port 8501 is already in use, either stop the conflicting process or run Streamlit on a different port by changing the `--server.port` value.

## Example usage
```bash
python app.py --message "How should I compare open-source models for my capstone?"
python app.py --prompt-style few-shot --message "What should I include in the evaluation section?"
```

## Streamlit UI
Run the web interface locally:
```bash
python -m streamlit run app_streamlit.py --server.port 8502 --server.headless true
```

## Notes
- The project uses local open-source inference through Ollama.
- No private, confidential, or proprietary customer data is used.
- The knowledge base and evaluation set are synthetic and public-safe for demonstration purposes.
