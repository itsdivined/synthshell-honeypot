# Detector experiment notes (for report authors)

**Date:** 18 November 2026  
**Script:** `scripts/06_train_detector.py`  
**Artifacts:** `data/analysis/detector/` (`metrics.json`, `tables.md`, `DETECTOR_README.md`, confusion PNGs)

## What was trained

A simple **char TF-IDF (3–5) + logistic regression** (`class_weight=balanced`) on **already-logged reply text only**. No Magazov mixing, no LLM fine-tuning, no Ubuntu/Magazov re-replays.

| Source | Filter | n |
| --- | --- | --- |
| Real Ubuntu | `ground_truth.jsonl` nonempty `stdout` | 160 |
| Cowrie | Ubuntu replay, `status=ok`, nonempty reply, same `(session_id, step)` | 160 |
| Llama 3.1 8B | same | 83 |
| Qwen 2.5 7B | same | 97 |

**Label choice:** primary tasks are **binary** (`real_ubuntu` vs `honeypot`) and **3-way** (`ubuntu` / `cowrie` / `llm` with llama+qwen pooled). 4-way was skipped as primary (uneven per-LLM OK counts). Split is **GroupShuffleSplit by `session_id`** (~70/15/15, seed=25) to reduce same-session leakage. ANSI/prompt chrome is stripped so Cowrie escapes are not a free giveaway.

## Key test numbers (seed=25)

| Task | n_test | Accuracy | Macro-F1 | AUROC |
| --- | --- | --- | --- | --- |
| Binary (ubuntu vs honeypot) | 62 | 0.758 | 0.750 | 0.875 |
| 3-way (ubuntu / cowrie / llm) | 62 | 0.694 | 0.682 | 0.888 (OvR macro) |
| Ubuntu vs LLM only | 37 | 0.811 | 0.802 | 0.927 |
| Ubuntu vs Cowrie only | 50 | 0.800 | 0.797 | 0.899 |

3-way per-class F1 (test): **ubuntu 0.708**, **cowrie 0.739**, **llm 0.600** (LLM test support only **12** — treat cautiously).

## Honest interpretation for the write-up

- A bag-of-character-ngrams detector **can** separate real Ubuntu stdout from honeypot replies above chance (binary AUROC ≈ **0.88**), but it is **not** near-perfect — useful as a cheap auxiliary signal, not a silver-bullet detector.
- In the 3-way fold, **Cowrie has the highest class F1 (0.739)** and **pooled LLM the lowest (0.600)**. That is consistent with Cowrie being a more stereotyped reply style once ANSI chrome is removed, while LLM text overlaps more with natural shell output *in this feature space / fold*.
- Pairwise AUROCs are close (**LLM 0.927** vs **Cowrie 0.899**); with small held-out session groups, do **not** claim a large, stable gap. Prefer: “exploratory TF-IDF+LR evidence that both backends remain partially detectable; class-level confusion depends on the label scheme.”
- Caveat for the report: only **20** Ubuntu sessions → val/test session counts are small; bootstrap CIs are wide. Cite `data/analysis/detector/tables.md` for matrices.

## Rerun

```text
.venv\Scripts\python.exe -m pip install "scikit-learn>=1.4" "matplotlib>=3.8"
.venv\Scripts\python.exe scripts\06_train_detector.py
```

Use `--no-join-only` to include honeypot replies whose Ubuntu stdout was empty; Magazov remains off unless `--include-magazov`.
