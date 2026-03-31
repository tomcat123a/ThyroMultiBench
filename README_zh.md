# 🌟 ThyroMultiBench 官方评测工具包

[English](README.md) | [中文版](README_zh.md)

---

## 📖 中文版：保姆级全流程教程

欢迎使用 **《ThyroMultiBench: A Comprehensive Text and Multimodal Benchmark for Thyroid Cancer》** 官方评测工具包！

本仓库旨在为初学者提供极其详细、开箱即用的评测代码。通过本教程，您将了解如何使用 ThyroMultiBench 数据集对大语言模型 (LLM) 和多模态大语言模型 (MLLM) 进行全方位的医学能力评测。

### 📑 目录
1. [环境配置](#1-环境配置)
2. [API 配置](#2-api-配置)
3. [数据集准备](#3-数据集准备)
4. [核心评测原理解析](#4-核心评测原理解析)
5. [如何运行评测](#5-如何运行评测)
6. [提示词模板说明](#6-提示词模板说明)

---

### 1. 环境配置

首先，将本代码仓库克隆到您的本地（或 Linux 服务器）：
```bash
git clone https://github.com/yourusername/ThyroMultiBench-Eval.git
cd ThyroMultiBench-Eval
```

安装运行所需的 Python 依赖包。我们使用了 `openai`、`anthropic`（用于 Claude 模型）和 `dashscope` 进行模型调用，使用 `pandas` 和 `openpyxl` 来读取 Excel 数据集：
```bash
pip install -r requirements.txt
```

### 2. API 配置

本项目遵循“零命令行参数”的极简设计，原生支持 **OpenAI**、**阿里云 Qwen**、**Anthropic Claude** 以及**任意兼容 OpenAI 格式的通用模型接口**（如本地部署的 vLLM、Ollama 等）。

您只需要在项目根目录下创建一个 `config.json` 文件，并填入您的模型 API Key 即可：

```json
{
    "openai_api_key": "sk-你的-openai-api-key",
    "dashscope_api_key": "sk-你的-阿里云qwen-api-key",
    "anthropic_api_key": "sk-ant-你的-claude-api-key",
    "general_api_key": "sk-你的-通用模型-api-key",
    "general_api_base": "https://api.your-provider.com/v1"
}
```
*原理解释：代码中的 `config_utils.py` 会自动在当前目录优先寻找配置文件，这使得在不同环境下部署变得极其简单。*

### 3. 数据集准备

在运行之前，您需要将原始的评估数据下载并放入 `dataset/` 文件夹中。建议的文件结构如下：

```text
dataset/
├── text_tasks/
│   ├── multiple_choice.json      # 纯文本选择题（如病理学基础知识）
│   ├── open_qa.json              # 开放问答题
│   └── dialogue.json             # 多轮问诊对话
├── multimodal_tasks/
│   ├── image_qa.xlsx             # 包含图片URL和题目的多模态任务
│   └── images/                   # 本地图片文件夹（可选）
└── prognosis/
    └── prognosis_eval.json       # 基于病例报告拆分的临床症状预后评估
```

#### `dataset/` 文件夹的目的是什么？需要放案例文件吗？
- `dataset/` 是默认的数据入口目录：[evaluate.py](file:///d:/tencentcloud4G/zeng_thyroid/scientific_data/project_qa_generation/repository/evaluate.py) 会从这里读取不同任务的评测文件。
- 本仓库已经自带了一套“演示用小样本数据”，用于让您快速跑通整个评测流程；实际使用时，请将演示文件替换为您下载的 ThyroMultiBench 数据（或在 `evaluate.py` 中修改数据路径）。
- 强烈建议不要把含敏感信息/真实患者信息的数据上传到 GitHub；请仅在本地或安全存储中使用。

#### 为什么这样设计？
- 选择题通常包含明确的选项和标准答案，使用 `.json` 格式读取最快。
- 多模态题目（如超声图片问答）通常需要对齐图片路径和题目文本，使用 `.xlsx`（Excel）格式更加直观，代码中通过 `pandas` 进行了完美兼容。

### 4. 核心评测原理解析

为了保证代码的可读性和模块化，所有的评测逻辑都存放在 `src/evaluators/` 目录下：

1. **文本评测器 (`text_evaluator.py`)**：
   - *选择题*：模型输出后，代码会将“自由文本输出”解析为单个选项字母，再计算最终的**正确率 (Accuracy)**。解析逻辑在 [mcq_utils.py](file:///d:/tencentcloud4G/zeng_thyroid/scientific_data/project_qa_generation/repository/src/utils/mcq_utils.py) 中，支持 `Answer: A`、`答案：A`、`(A)`、`A.` 等常见格式。
   - *开放问答*：仅负责生成答案，后续交由“裁判模型”打分。
2. **多模态评测器 (`multimodal_evaluator.py`)**：
   - 负责将文本提示词与图片 URL 拼接成标准的 Multimodal Message 格式，调用多模态模型进行视觉问答。
3. **对话评测器 (`dialogue_evaluator.py`)**：
   - 自动解析历史对话（History array），评估模型在多轮交互中的表现。
4. **临床预后评测器 (`prognosis_evaluator.py`)**：
   - **两步法评测**：首先根据复杂的病例信息，让具备强大推理能力的大模型解析并**提出预后问题**；随后，再让模型根据病例回答这些问题。
5. **大模型裁判 (`judge.py`)**：
   - **LLM-as-a-Judge 机制**：对于主观题（开放问答、预后评估），传统的方法无法自动评测。我们调用高级模型（如 GPT-4o 或 Claude-3.5-Sonnet）作为裁判，将“AI的回答”与“金标准答案(Ground Truth)”进行对比，并严格给出 0-10 分的评分及打分理由。

### 5. 如何运行评测

本仓库提供两种运行方式：
1) 一键全流程：`evaluate.py`
2) 按任务运行：`scripts/*.py`（更推荐，便于严格控制实验设置）

下面所有命令默认在仓库根目录执行。

#### 5.1 一键全流程（覆盖全部任务）
本项目的评测主入口是 `evaluate.py` 脚本。您无需输入复杂的参数，直接运行：

```bash
python3 evaluate.py
```

**运行后会发生什么？**
1. 脚本会自动初始化您配置的各类模型（支持混用，比如用 Claude 生成，用 GPT-4o 当裁判）。
2. 从 `dataset/` 目录中按格式（json/xlsx）自动加载数据。
3. 依次执行：纯文本选择题（实时打印准确率） -> 开放问答 -> 多模态评估 -> 临床预后两步法评估。
4. 针对所有生成的开放式回答，调用裁判模型进行自动打分。
5. **结果保存**：运行过程中所有的详细生成结果、模型输出、裁判打分理由，都会以 `.txt` 或 `.json` 的形式，保存在 `agent_data/` 目录下（按任务自动生成 UUID 文件夹），方便您后续分析。

#### 5.2 按任务运行（推荐）
每个任务脚本都是“可独立运行”的，并且在脚本顶部提供一组可编辑参数，方便您对模型、语言、数据路径、是否启用裁判打分进行精确控制。

**通用参数（在脚本文件内修改）**
- `GEN_PROVIDER`：生成模型的提供方。取值：`qwen`、`openai`、`claude`、`general`。
- `GEN_MODEL_NAME`：生成模型名称，例如 `qwen-plus`、`qwen-vl-plus`、`gpt-4o`、`claude-3-5-sonnet-20240620`。
- `LANG`：提示词语言。取值：`en` 或 `zh`（决定加载 `prompt/` 中的哪个版本提示词）。
- `DATASET_REL_PATH`：相对仓库根目录的数据路径。
- `RUN_JUDGE`：是否启用“裁判模型”自动打分（主观题建议开启）。
- `JUDGE_PROVIDER` / `JUDGE_MODEL_NAME`：裁判模型设置（provider 取值与 `GEN_PROVIDER` 相同）。

**纯文本选择题（Accuracy）**
```bash
python3 scripts/run_text_mcq.py
```
- 输入：`dataset/text_tasks/multiple_choice.json`
- 输出解析：使用 [mcq_utils.py](file:///d:/tencentcloud4G/zeng_thyroid/scientific_data/project_qa_generation/repository/src/utils/mcq_utils.py) 将模型自由文本输出解析为最终选项字母
- 指标：`accuracy`、`correct`、`total`，以及逐题 `details`（保存在 `agent_data/`）

**纯文本开放问答 → 裁判打分**
```bash
python3 scripts/run_text_open_qa_and_judge.py
```
- 输入：`dataset/text_tasks/open_qa.json`
- 第一步：生成每题 `ai_answer`
- 第二步（可选）：裁判模型对比 `ai_answer` 与 `ground_truth`，输出 `{score: 0-10, reason: ...}`

**多模态选择题（Accuracy）**
```bash
python3 scripts/run_multimodal_mcq.py
```
- 输入：`dataset/multimodal_tasks/image_qa.xlsx`
- 关键字段：`question`、`options`、`image_url`、`answer`
- `image_url` 支持：
  - 公网可访问 URL（`https://...`），或
  - 服务器本地图片路径
- 模型兼容性：
  - Qwen-VL：使用 `{"text": "..."} + {"image": "..."}` 结构
  - OpenAI / OpenAI-compatible：使用标准的 `image_url` message 结构
  - Claude：自动下载/读取图片并转为 base64 发送

**多轮对话 → 裁判打分**
```bash
python3 scripts/run_dialogue_and_judge.py
```
- 输入：`dataset/text_tasks/dialogue.json`
- 对话以 `dialogue_history` messages 形式送入模型，生成下一轮 assistant 回复
- 裁判打分（可选）：将生成回复与 `ground_truth` 进行对比评分

**临床预后两步法 → 裁判打分**
```bash
python3 scripts/run_prognosis_and_judge.py
```
- 输入：`dataset/prognosis/prognosis_eval.json`
- 第一步：强推理模型根据 `clinical_info` 生成预后问题
- 第二步：回答模型根据病例信息与问题进行作答
- 裁判打分（可选）：对比 `ai_answer` 与 `ground_truth` 自动给分

#### 5.3 输出保存在哪里？如何读取结果？
- 所有脚本都会把详细输出写入 `agent_data/`（按任务自动创建 UUID 子文件夹）。
- 选择题任务：逐题包含 `predicted`、`ground_truth`、`is_correct`、`raw_response`（便于错误分析与规则迭代）。
- 裁判任务：逐题包含 `score`（0–10）与 `reason`；若裁判输出不是合法 JSON，会保留 `raw_response` 以便排查提示词与模型行为。

### 6. 提示词模板说明

在大模型评测中，Prompt（提示词）至关重要。我们将所有提示词从代码中抽离，统一放在了 `prompt/` 目录下。
- 所有提示词均提供中英双语版本（如 `multiple_choice_zh.txt` 和 `multiple_choice_en.txt`）。
- **二次开发**：如果您想优化模型的表现，无需修改 Python 代码，只需直接修改 `prompt/` 目录下的 `.txt` 文件即可生效！
