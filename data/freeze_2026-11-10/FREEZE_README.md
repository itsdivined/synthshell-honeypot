# Freeze package — 10 November 2026

**Student:** Patil Devyani Anil (ID 5034)  
**Module:** 7FTC2001  
**Project:** Generative AI Deception: Dynamic LLM-Powered Honeypots  

These files are the **frozen comparison tables** intended for the Final Project Report (due 20 November 2026). Practical freeze date in the plan is **14 November 2026**; this package locks the Magazov 20-session × 5-run analysis already completed on **7 November 2026**.

## What is frozen

| File | Role |
| --- | --- |
| `tables.md` | Markdown comparison table + Wilcoxon notes + RQ4 summary |
| `summary.json` | Machine-readable scores (systems, bootstrap CIs, Wilcoxon, RQ4) |
| `rq4_containment.json` | Containment audit checklist (Passed) |
| `SOURCE.txt` | Pointer to the scored replay log and analyse command |

## Source log (do not re-run `--runs 5` for freeze)

- **Log path:** `data/logs/replay_magazov_20sess_runs5.jsonl`
- **Log finished:** 7 November 2026 ~17:31 (local)
- **Analysis folder (canonical):** `data/analysis/runs5/`
- **Command rows scored:** 1400 (20 sessions × shared commands × 5 runs × 4 systems)
- **Ground truth present at analysis time:** False (Ubuntu capture still missing)

Re-score without replaying (if needed):

```text
python scripts/05_analyse.py --log data\logs\replay_magazov_20sess_runs5.jsonl --out-dir data\analysis\runs5
```

## Headline numbers (verified)

| System | OK | Skipped | Errors (timeouts) | Mean cmds completed | Mean delay (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| cowrie | 350 | 0 | 0 | 3.50 | 0.37 |
| gpt-4o-mini | 0 | 350 | 0 | — (no API key) | — |
| llama-3.1-8b | 86 | 0 | 264 | 0.20 | 51.5 |
| qwen-2.5-7b | 153 | 0 | 197 | 0.17 | 50.4 |

- **RQ4 containment:** Passed  
- **Fidelity / consistency / invented content:** blank (no Ubuntu ground truth)  
- **Wilcoxon** (commands completed): Cowrie vs Llama n=100, p≈1.14e-16; Cowrie vs Qwen n=100, p≈1.80e-16; Cowrie vs GPT n=0 (all skipped)

## Report use

Paste Table 1–3 from these files into the report. Keep all four systems in every table. A skip is a missing run, not a removed system. Do **not** invent GPT delay/cost or fidelity percentages.

## Optional before 14 Nov (not required to freeze Magazov tables)

1. Set `OPENAI_API_KEY` and optionally re-run GPT rows only (separate log) — optional.  
2. Capture Ubuntu ground truth for RQ1 fidelity — optional; Docker was not available on this machine on 10 Nov 2026.
