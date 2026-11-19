# Reply-source detector

Trains a lightweight **TF-IDF (`char_wb` 3–5) + LogisticRegression** classifier on already-logged shell reply text.

## Labels

| Scheme | Classes | Meaning |
| --- | --- | --- |
| binary | `real_ubuntu`, `honeypot` | Ubuntu ground-truth stdout vs Cowrie+LLM replies pooled |
| 3-way | `ubuntu`, `cowrie`, `llm` | Llama 3.1 8B + Qwen 2.5 7B pooled as `llm` |
| ubuntu_vs_llm / ubuntu_vs_cowrie | pairwise | Secondary honesty checks |

4-way (separate llama/qwen) was **not** used as the primary report task: per-model OK counts on the Ubuntu replay are uneven; the cleaner story is Ubuntu vs Cowrie vs LLM-as-a-class.

## Data

- Real Ubuntu: `data/test_set/ground_truth.jsonl` nonempty `stdout` (**160**)
- Honeypot: `data/logs/replay_ubuntu_testset_runs1.jsonl` cowrie / llama-3.1-8b / qwen-2.5-7b with `status=ok` and nonempty `reply`
- Default **join-only**: same `(session_id, step)` as nonempty Ubuntu stdout → cowrie **160**, llama **83**, qwen **97**
- Magazov mixed: **off** by default (single command-distribution story)

Text is lightly normalized (ANSI / trailing shell-prompt chrome stripped) so Cowrie control sequences are not a free feature.

## How to rerun

From the repo root, with the project venv:

```bash
.venv\Scripts\python.exe -m pip install "scikit-learn>=1.4" "matplotlib>=3.8"
.venv\Scripts\python.exe scripts\06_train_detector.py
```

Flags: `--no-join-only`, `--include-magazov`, `--seed 25`, `--out-dir data/analysis/detector`.

## Main test numbers (seed=25, join-only)

**Binary** — n_test=62: accuracy=**0.758**, macro-F1=**0.750**, AUROC=**0.875**

**3-way** — n_test=62: accuracy=**0.694**, macro-F1=**0.682**, OvR-AUROC=**0.888**  
Per-class F1: ubuntu=**0.708**, cowrie=**0.739**, llm=**0.600**

**Pairwise** — ubuntu vs llm AUROC=**0.927**; ubuntu vs cowrie AUROC=**0.899**

Outputs: `metrics.json`, `tables.md`, `confusion_*_test.png`, this README.  
Report-facing summary: `RESULTS_DETECTOR.md` at the repo root.
