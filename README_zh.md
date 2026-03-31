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

#### 为什么这样设计？
- 选择题通常包含明确的选项和标准答案，使用 `.json` 格式读取最快。
- 多模态题目（如超声图片问答）通常需要对齐图片路径和题目文本，使用 `.xlsx`（Excel）格式更加直观，代码中通过 `pandas` 进行了完美兼容。

### 4. 核心评测原理解析

为了保证代码的可读性和模块化，所有的评测逻辑都存放在 `src/evaluators/` 目录下：

1. **文本评测器 (`text_evaluator.py`)**：
   - *选择题*：模型输出后，代码会自动使用正则表达式提取开头的选项字母（A/B/C/D），并自动计算最终的**正确率 (Accuracy)**。
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

本项目的评测主入口是 `evaluate.py` 脚本。您无需输入复杂的参数，直接运行：

```bash
python evaluate.py
```

**运行后会发生什么？**
1. 脚本会自动初始化您配置的各类模型（支持混用，比如用 Claude 生成，用 GPT-4o 当裁判）。
2. 从 `dataset/` 目录中按格式（json/xlsx）自动加载数据。
3. 依次执行：纯文本选择题（实时打印准确率） -> 开放问答 -> 多模态评估 -> 临床预后两步法评估。
4. 针对所有生成的开放式回答，调用裁判模型进行自动打分。
5. **结果保存**：运行过程中所有的详细生成结果、模型输出、裁判打分理由，都会以 `.txt` 或 `.json` 的形式，保存在 `agent_data/` 目录下（按任务自动生成 UUID 文件夹），方便您后续分析。

### 6. 提示词模板说明

在大模型评测中，Prompt（提示词）至关重要。我们将所有提示词从代码中抽离，统一放在了 `prompt/` 目录下。
- 所有提示词均提供中英双语版本（如 `multiple_choice_zh.txt` 和 `multiple_choice_en.txt`）。
- **二次开发**：如果您想优化模型的表现，无需修改 Python 代码，只需直接修改 `prompt/` 目录下的 `.txt` 文件即可生效！
