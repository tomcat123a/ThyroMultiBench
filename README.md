# 🌟 ThyroMultiBench Evaluation Toolkit

[English](README.md) | [中文版](README_zh.md)

---
![Uploading 下载.png…]()


## 📖 English Version: Comprehensive Tutorial

Welcome to the official evaluation toolkit for **"ThyroMultiBench: A Comprehensive Text and Multimodal Benchmark for Thyroid Cancer"**. 

This repository is designed to be highly beginner-friendly. It provides a complete, out-of-the-box solution to evaluate Large Language Models (LLMs) and Multimodal Large Language Models (MLLMs) using the ThyroMultiBench dataset.

### 📑 Table of Contents
1. [Environment Setup](#1-environment-setup)
2. [Configuration](#2-configuration)
3. [Dataset Preparation](#3-dataset-preparation)
4. [Understanding the Evaluation Pipeline](#4-understanding-the-evaluation-pipeline)
5. [Running the Evaluation](#5-running-the-evaluation)
6. [Prompts Explanation](#6-prompts-explanation)

---

### 1. Environment Setup

First, clone this repository to your local machine:
```bash
git clone https://github.com/yourusername/ThyroMultiBench-Eval.git
cd ThyroMultiBench-Eval
```

Install the required Python packages. We use standard libraries like `openai`, `anthropic` (for Claude), `pandas` and `openpyxl` for reading datasets, and `tqdm` for progress bars.
```bash
pip install -r requirements.txt
```

### 2. Configuration

This toolkit supports **OpenAI (GPT series)**, **Aliyun DashScope (Qwen series)**, **Anthropic (Claude series)**, and any **OpenAI-Compatible** API endpoints out of the box. 
To configure your API keys, create a `config.json` file in the root directory:

```json
{
    "openai_api_key": "sk-your-openai-api-key",
    "dashscope_api_key": "sk-your-qwen-api-key",
    "anthropic_api_key": "sk-ant-your-claude-api-key",
    "general_api_key": "sk-your-general-api-key",
    "general_api_base": "https://api.your-provider.com/v1"
}
```
*Note: The code will automatically load this configuration file. You do not need to pass API keys via command-line arguments.*

### 3. Dataset Preparation

Before running evaluations, you need to place your raw dataset into the `dataset/` directory. The expected structure is as follows:

```text
dataset/
├── text_tasks/
│   ├── multiple_choice.json      # Pure text multiple choice questions
│   ├── open_qa.json              # Open-ended QA
│   └── dialogue.json             # Multi-turn dialogue history
├── multimodal_tasks/
│   ├── image_qa.xlsx             # Multimodal tasks containing image URLs and questions
│   └── images/                   # Local image files (if applicable)
└── prognosis/
    └── prognosis_eval.json       # Clinical case reports for prognosis evaluation
```

#### What is the `dataset/` folder for?
- It is the default place where [evaluate.py](file:///d:/tencentcloud4G/zeng_thyroid/scientific_data/project_qa_generation/repository/evaluate.py) looks for evaluation files.
- This repository already ships with a small demo dataset so you can run the pipeline end-to-end. Replace the demo files with your real ThyroMultiBench data (or modify the paths in `evaluate.py`).
- Do NOT upload sensitive/private clinical data to GitHub. Keep real patient-related data local or in a secure storage.

#### Why this structure?
- **JSON for Text**: JSON is lightweight and perfect for structuring text questions, options, and answers.
- **Excel for Multimodal**: Multimodal data often contains complex metadata, image URLs, and text. `pandas` makes reading `.xlsx` seamless.
- **Prognosis**: The `prognosis_eval.json` contains raw clinical symptoms split from case reports, serving as a complex reasoning task.

### 4. Understanding the Evaluation Pipeline

This codebase is highly modular. All evaluation logic is located in the `src/evaluators/` directory:

1. **Text Evaluator (`text_evaluator.py`)**: 
   - *Multiple Choice*: Parses the model output into an option letter and calculates **Accuracy**. The parsing logic is implemented in [mcq_utils.py](file:///d:/tencentcloud4G/zeng_thyroid/scientific_data/project_qa_generation/repository/src/utils/mcq_utils.py) and supports formats like `Answer: A`, `答案：A`, `(A)`, `A.`.
   - *Open QA*: Generates detailed answers that will later be scored by a Judge.
2. **Multimodal Evaluator (`multimodal_evaluator.py`)**: 
   - Constructs messages combining text and images (via URLs or base64) to query multimodal models.
3. **Dialogue Evaluator (`dialogue_evaluator.py`)**: 
   - Passes the entire conversation history to the model to generate the next turn.
4. **Prognosis Evaluator (`prognosis_evaluator.py`)**: 
   - *Two-step process*: First, it uses an advanced reasoning model to parse the raw clinical case and generate specific prognosis questions. Second, it answers those questions.
5. **LLM-as-a-Judge (`judge.py`)**: 
   - Uses an advanced model (e.g., GPT-4o or Claude-3.5-Sonnet) to compare the AI's generated open-ended answers against the Ground Truth, assigning a score from 0 to 10.

### 5. Running the Evaluation

This repository provides two ways to run evaluations:
1) One-click full pipeline: `evaluate.py`
2) Task-specific scripts: `scripts/*.py` (recommended for controlled experiments)

All commands below assume you are in the repository root directory.

#### 5.1 Full pipeline (all tasks)
The main entry point is `evaluate.py`. You do not need to use complex command-line arguments. Simply run:

```bash
python3 evaluate.py
```

**What happens when you run this script?**
1. It initializes the generator model (e.g., Qwen/Claude/General) and the judge model (e.g., GPT-4o).
2. It automatically reads files from the `dataset/` directory using our custom `data_loader.py`.
3. It evaluates Text MCQ and prints the accuracy.
4. It evaluates Open QA and Dialogue.
5. It runs the two-step Prognosis evaluation.
6. Finally, it passes all open-ended outputs to the Judge model for scoring.
7. All results, including detailed JSON outputs, are saved automatically in the `agent_data/` directory (categorized by task UUID).

#### 5.2 Run a specific task (recommended)
Each task script is fully self-contained and has a small set of editable parameters at the top of the file.

**Common parameters (edit inside the script file)**
- `GEN_PROVIDER`: generator model provider. Values: `qwen`, `openai`, `claude`, `general`.
- `GEN_MODEL_NAME`: generator model name, e.g. `qwen-plus`, `qwen-vl-plus`, `gpt-4o`, `claude-3-5-sonnet-20240620`.
- `LANG`: prompt language. Values: `en` or `zh`. This controls which prompt file is loaded from `prompt/`.
- `DATASET_REL_PATH`: dataset path relative to repo root.
- `RUN_JUDGE`: whether to run LLM-as-a-judge scoring for open-ended tasks.
- `JUDGE_PROVIDER` / `JUDGE_MODEL_NAME`: judge model settings (same provider choices as `GEN_PROVIDER`).

**Text Multiple Choice (Accuracy)**
```bash
python3 scripts/run_text_mcq.py
```
- Input file: `dataset/text_tasks/multiple_choice.json`
- Output parsing: [mcq_utils.py](file:///d:/tencentcloud4G/zeng_thyroid/scientific_data/project_qa_generation/repository/src/utils/mcq_utils.py) extracts the final option letter from free-form model outputs.
- Metrics: `accuracy`, `correct`, `total`, plus per-case `details` in `agent_data/`.

**Text Open QA → Judge scoring**
```bash
python3 scripts/run_text_open_qa_and_judge.py
```
- Input file: `dataset/text_tasks/open_qa.json`
- Stage 1: generates `ai_answer` for each question.
- Stage 2 (optional): judge compares `ai_answer` vs `ground_truth` and outputs `{score: 0-10, reason: ...}`.

**Multimodal Multiple Choice (Accuracy)**
```bash
python3 scripts/run_multimodal_mcq.py
```
- Input file: `dataset/multimodal_tasks/image_qa.xlsx`
- Required columns: `question`, `options`, `image_url`, `answer`
- `image_url` can be:
  - a public URL (`https://...`) or
  - a local image path on your server
- Model compatibility:
  - Qwen-VL style: uses `{"text": "..."} + {"image": "..."}` blocks
  - OpenAI / OpenAI-compatible: uses standard `image_url` message blocks
  - Claude: automatically downloads/reads the image and sends base64 content

**Multi-turn Dialogue → Judge scoring**
```bash
python3 scripts/run_dialogue_and_judge.py
```
- Input file: `dataset/text_tasks/dialogue.json`
- Dialogue is passed as `dialogue_history` messages; the model generates the next assistant turn.
- Judge scoring (optional) compares the generated answer with `ground_truth`.

**Prognosis (2-step) → Judge scoring**
```bash
python3 scripts/run_prognosis_and_judge.py
```
- Input file: `dataset/prognosis/prognosis_eval.json`
- Step 1: a strong reasoning model generates prognosis questions from `clinical_info`.
- Step 2: a (possibly different) model answers those questions.
- Judge scoring (optional) scores `ai_answer` vs `ground_truth`.

#### 5.3 Where are outputs saved? How to read them?
- All scripts save detailed outputs under `agent_data/` (automatic UUID subfolders).
- For MCQ tasks, each case includes `predicted`, `ground_truth`, `is_correct`, and `raw_response`.
- For judge tasks, each case includes `score` (0–10) and `reason`. If the judge output is not valid JSON, the raw output is kept for debugging.

### 6. Prompts Explanation

All prompt templates are stored in the `prompt/` directory. They are completely decoupled from the code and provided in both English (`_en.txt`) and Chinese (`_zh.txt`).
- `multiple_choice_en.txt`: Instructs the model to output the correct option letter.
- `prognosis_gen_en.txt`: Instructs the model to parse clinical cases and generate questions.
- `judge_en.txt`: Instructs the judge model to score answers strictly based on medical accuracy.
