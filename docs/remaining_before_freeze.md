# What remains before 14 November 2026 (1-page note)

**Student:** Patil Devyani Anil (5034)  
**Date:** 10 November 2026  
**Status:** Magazov ×5 tables are frozen in `data/freeze_2026-11-10/`. Report draft exists. The items below are **optional extras**, not blockers for using the Magazov freeze numbers in the FPR.

---

## Already locked for the report

- Magazov 20 sessions × 5 runs log: `data/logs/replay_magazov_20sess_runs5.jsonl`
- Analysis: `data/analysis/runs5/` and freeze copy `data/freeze_2026-11-10/`
- RQ4 containment: **Passed**
- Report draft: `Report_Patil_Devyani_5034.docx` / `.md` (edit in own words before Turnitin)

Do **not** restart `--runs 5` Magazov replay for freeze purposes.

---

## Optional A — GPT-4o mini row (RQ2 cost / commercial delay)

| Item | Detail |
| --- | --- |
| Blocker today | No `OPENAI_API_KEY` in lab `.env` during Magazov ×5 → **350 skips** |
| If key available before 14 Nov | Small GPT-only replay of the **same** 20 Magazov sessions (keep a separate log; do not overwrite runs5) |
| Report if still missing | Keep GPT as a skipped row; state no commercial delay/cost numbers; do not drop the system from the design |

---

## Optional B — Ubuntu ground-truth test set (C2 / RQ1 fidelity)

| Item | Detail |
| --- | --- |
| Planned files | `data/test_set/sessions.jsonl`, `data/test_set/ground_truth.jsonl` (~20 sessions / ~200 commands) |
| Status 10 Nov 2026 | **Missing** (folder has scaffold / `.gitkeep` only) |
| Checklist | `docs/ubuntu_testset_checklist.md` |
| Why not captured today | **Docker not installed / not on PATH** on this Windows host. WSL Ubuntu is running, but the planned capture path is `docker run --rm -it --network none ubuntu:24.04`. A full ~200-command capture would also need careful session scripting and schema validation via `scripts/03_testset.py`. |
| Effect on claims | Fidelity, consistency-vs-Linux, and invented-content cells stay **blank**. Magazov session-survival / delay / labels / RQ4 remain valid. |
| If Docker (or a clean offline Ubuntu) becomes available | Follow the checklist; validate with `python scripts/03_testset.py`; optional later replay `--source test-set` into a **new** log — do not overwrite Magazov freeze. |

---

## Optional C — Local-model timeouts (hardware)

Llama/Qwen timeouts on ~7.5 GB RAM CPU Ollama understate session survival. Improving this needs more RAM/GPU or smaller models — **not** required before freeze. Report the error counts honestly.

---

## Suggested student actions before Turnitin (16–19 Nov writing)

1. Read and rewrite the report draft in your own voice; check word count ≤ ~7500.  
2. Put the GitHub URL on the front page.  
3. Paste freeze tables; keep four systems.  
4. Say clearly: GPT skipped; Ubuntu GT missing; RQ4 = containment audit.  
5. Practice viva from `PROJECT_BRIEF` §12.
