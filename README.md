# RUPS-296: Reasoning Under Pressure — Structured

**A benchmark for evaluating LLM reasoning failures on structured domain inputs.**

> 📄 Paper: *"Reasoning Under Pressure: How Structured Domain Context Triggers Failure Modes in Frontier LLMs"*  
> 🤗 Dataset: Will be added later

---

## Overview

RUPS-296 is a benchmark of **296 structured reasoning problems** across three domains and five failure modes, designed to evaluate how frontier LLMs fail — and how those failures can be repaired — when reasoning over structured domain inputs.

**Key findings:**
- Chain-of-thought prompting *worsens* structured reasoning failures in 4 of 5 failure modes
- Context scaffolding recovers 5–37% of baseline failures selectively by failure type
- Failure patterns are consistent across model families (6.3× performance gap across 5 models)
- 70% of problems triggered at least one model failure under baseline conditions

---

## Failure Mode Taxonomy

| ID | Failure Mode | Structural Trigger |
|----|-------------|-------------------|
| F1 | Schema blindness | Abbreviated/technical field names (revol_util, WBC, INR) |
| F2 | Temporal flattening | Time-ordered records where trend direction is critical |
| F3 | Unit conflation | Mixed units in same record (mg/dL vs mmol/L, monthly vs annual) |
| F4 | Negation dropout | Inverted boolean encoding, negated clinical/HR findings |
| F5 | Spurious shortcut | Salient category label contradicted by individual metrics |

---

## Repository Structure

```
rups296/
├── README.md
├── requirements.txt
│
├── benchmark/
│   └── rups296_benchmark.json          # 296 structured reasoning problems
│
├── experiments/
│   ├── 01_generate_benchmark.ipynb     # Benchmark generation pipeline
│   └── 02_run_experiment.ipynb         # Full experiment (models × conditions × judge)
│
├── scaffolds/
│   └── scaffolds_v2.py                 # Context scaffolding framework (v2)
│
├── results/
│   ├── judged_results.json             # Full judged results (4,437 responses)
│   └── human_annotation_scored.csv     # Human validation scores (n=50, κ=0.741)
│
├── figures/
│   ├── fig1_failure_rate_by_model.png
│   ├── fig2_scaffold_recovery_by_mode.png
│   ├── fig3_cot_vs_baseline.png
│   └── fig4_crossmodel_heatmap.png
│
└── generate_figures.py                 # Reproduces all paper figures
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up your LLM provider

The experiments use an async LLM gateway. To reproduce with your own provider, set environment variables:

**Option A — OpenAI:**
```bash
export OPENAI_API_KEY="your-key"
```
Then replace `AsyncLLM` calls in the notebooks with:
```python
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(model="gpt-4o", messages=[...])
```

**Option B — Anthropic:**
```bash
export ANTHROPIC_API_KEY="your-key"
```
```python
import anthropic
client = anthropic.Anthropic()
response = client.messages.create(model="claude-sonnet-4-5", messages=[...])
```

**Option C — Groq (free):**
```bash
export GROQ_API_KEY="your-key"  # free at console.groq.com
```
```python
from groq import Groq
client = Groq()
response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[...])
```

### 3. Run the experiment

Open `experiments/02_run_experiment.ipynb` and run cells 1–9 in order.

- Change Cell 4 to load `benchmark/rups296_benchmark.json`
- Update Cell 5 with your model names
- Results save to `./results/`

---

## Benchmark Format

Each problem in `rups296_benchmark.json` has this structure:

```json
{
  "id": "FIN-F1-001",
  "domain": "financial",
  "failure_mode": "F1",
  "failure_name": "Schema blindness",
  "structural_trigger": "...",
  "context": "...",
  "question": "...",
  "gold_answer": "...",
  "gold_failure_label": "...",
  "adversarial_version": "..."
}
```

**Fields:**
- `context` — structured data (pipe-separated table or JSON record) containing the structural trigger
- `question` — reasoning question requiring careful reading of the context
- `gold_answer` — correct answer with explicit reasoning addressing the failure mode
- `gold_failure_label` — how the failure mode fires on this specific problem
- `adversarial_version` — same scenario in plain English with trigger removed (74% of problems)

---

## Context Scaffolding

The `scaffolds/scaffolds_v2.py` file contains the validated scaffold preambles for all five failure modes. Import and use directly:

```python
from scaffolds.scaffolds_v2 import SCAFFOLDS, build_prompt

# Automatically selects the right scaffold for the problem's failure mode
prompt = build_prompt(problem, condition='context_scaffold')
```

---

## Results Summary

| Model | Baseline | CoT | Scaffold |
|-------|---------|-----|----------|
| Claude-sonnet-4.6 | 8.8% | 11.5% | 7.1% |
| GPT-5.4-mini | 14.9% | 16.2% | 8.2% |
| GPT-4o | 24.3% | 29.4% | 20.6% |
| GPT-4o-mini | 36.8% | 48.3% | 33.4% |
| Gemini-2.5-flash | 55.3% | 59.7% | 48.6% |

| Failure mode | Scaffold recovery | CoT change |
|-------------|-----------------|------------|
| F1 Schema blindness | +13% | −5% |
| F2 Temporal flattening | +5% | +19% |
| F3 Unit conflation | +27% | 0% |
| F4 Negation dropout | −3% | +30% |
| F5 Spurious shortcut | +37% | +65% |

---

## Human Validation

Inter-annotator agreement between human expert and GPT-4o judge on a 50-problem random sample:

| Failure mode | Cohen's κ | Agreement |
|---|---|---|
| F1 Schema blindness | 0.315 | 50.0% |
| F2 Temporal flattening | 0.706 | 90.0% |
| F3 Unit conflation | 0.474 | 90.0% |
| F4 Negation dropout | 1.000 | 100.0% |
| F5 Spurious shortcut | 1.000 | 100.0% |
| **Overall** | **0.741** | **86.0%** |

F1 lower agreement is due to the judge conflating domain knowledge errors with schema blindness failures. Correcting for these judge errors raises overall κ to 0.89.

---

## Citation

```bibtex
@inproceedings{rups296_2026,
  title     = {Reasoning Under Pressure: How Structured Domain Context Triggers Failure Modes in Frontier LLMs},
  booktitle = {Proceedings of EMNLP 2026},
  year      = {2026}
}
```

---

## License

MIT License. The benchmark does not contain personally identifiable information. Clinical domain problems are inspired by MIMIC-III data structures but do not contain real patient records.
