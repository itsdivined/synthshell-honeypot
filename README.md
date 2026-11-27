# Generative AI Deception: Dynamic LLM-Powered Honeypots

Patil Devyani Anil, MSc Data Science (FT), module **7FTC2001**. Supervisor: Dr Rama Abirami K.

Private repository: [`itsdivined/synthshell-honeypot`](https://github.com/itsdivined/synthshell-honeypot).

**Final Project Report (FPR):** [`Patil_Devyani_5034YVIH_Report.docx`](Patil_Devyani_5034YVIH_Report.docx)

## Aim

Closed-lab evaluation of how **realistic, consistent, and cost-effective** an LLM honeypot is compared with a traditional scripted honeypot (Cowrie), and which backend gives the best balance for a defender.

A session hits an SSH-style front end. **Cowrie** answers with its scripted shell. Each **LLM** returns **text only**. **Session memory** records cwd, file/user deltas and sends that text with the next command. Models are **not** given tools; commands are **not** passed to the host OS. All services bind to **`127.0.0.1` only**.

## Research gap

There was no student-reproducible, multi-step, multi-backend lab that gives Cowrie and several LLMs the **same sessions** and reports **fidelity**, **delay**, **session survival**, **reply detectability**, and a known **containment** posture together. Field demos and single-command tests are hard to re-run on one laptop.

## Novelty

LLM honeypots already exist. The novelty is the **measurement design**:

1. Multi-step stateful testing with Ubuntu container ground truth.
2. One repeatable harness: Cowrie + three LLM backends on identical sessions.
3. Magazov session length as engagement context, plus Ubuntu fidelity.
4. Exploratory **char TF-IDF + logistic regression** reply-source detector (Data Science ML evidence).
5. **RQ4 as a containment audit** (localhost bind, text-only, no host execution, no model tools) — injection strings are not stored.

## Contributions

- **C1.** Working prototype with session-state memory on a standard SSH front end.
- **C2.** Ubuntu ground-truth test set joinable to replay logs (~200 commands / ~20 sessions).
- **C3.** Controlled 4-system comparison on Magazov and Ubuntu sessions (fidelity, delay, survival).
- **C4.** Exploratory TF-IDF + logistic regression reply-source detector + containment audit and design recommendations.
- **C5.** Reusable comparison lab: swap Ollama tags or add `EXTRA_OLLAMA_MODELS` in `.env` and re-run the same sessions ([docs/REUSE.md](docs/REUSE.md)).

## Research questions and objectives

| | Question | Objective |
| --- | --- | --- |
| **RQ1** | How realistic and consistent are LLM honeypot replies compared with real Linux output? | **O1.** Measure fidelity/consistency on Ubuntu GT; report Magazov session-length as engagement context. |
| **RQ2** | How do the three LLMs compare on response time and cost? | **O2.** Record delay (bootstrap CIs) and API cost when a key/prices exist. |
| **RQ3** | How well can a lightweight TF-IDF + logistic regression detector separate Ubuntu replies from Cowrie/LLM replies? | **O3.** Train/evaluate char TF-IDF (3–5) + balanced LR; report accuracy, macro-F1, AUROC, per-class F1. |
| **RQ4** | How well does each LLM honeypot resist prompt injection under a containment-first design? | **O4.** Run the containment audit (not a stored injection corpus) and recommend a low-cost design. |

**Session break** (Magazov engagement): empty reply, wrong/contradictory reply, AI self-disclosure, or delay **> 5 s**. Frozen runs used temperature **0.0**, history window **10**, bootstrap **95%** CIs (1000 resamples), Wilcoxon signed-rank on paired `commands_completed`.

## Systems

Four rows are always retained. Missing key/model → **skip** (row kept).

| System | Role | How it is reached |
| --- | --- | --- |
| Cowrie | Scripted baseline | `127.0.0.1:2222` — [docs/cowrie_localhost.md](docs/cowrie_localhost.md) |
| GPT-4o mini | Commercial API | `OPENAI_API_KEY` in `.env`; text-only; skipped if no key |
| Llama 3.1 8B | Local open-weight | Ollama `llama3.1:8b` on `127.0.0.1:11434` |
| Qwen 2.5 7B | Local open-weight | Ollama `qwen2.5:7b` on `127.0.0.1:11434` |

Safety-critical categories (e.g. sudo / password-file reads) get a fixed denial before any LLM call.

## Headline results (frozen lab)

| Evidence | Location | Headline |
| --- | --- | --- |
| Magazov ×5 engagement/delay | `data/analysis/runs5/` | Cowrie mean cmds **3.50**, delay ~**0.37 s**; Llama **0.20** / Qwen **0.17** cmds, ~**50 s** delay; GPT skipped |
| Ubuntu ×1 fidelity | `data/analysis/ubuntu_runs1/` | Fidelity: Qwen **0.40**, Llama **0.32**, Cowrie **0.00** |
| Detector (RQ3) | `data/analysis/detector/`, [RESULTS_DETECTOR.md](RESULTS_DETECTOR.md) | Binary acc **0.758** / macro-F1 **0.750** / AUROC **0.875**; 3-way **0.694** / **0.682** / OvR-AUROC **0.888** |
| Containment (RQ4) | `data/analysis/*/rq4_containment.json` | All checks **passed** |

**Takeaway:** prefer **Qwen** for closer Ubuntu-like text on this laptop; prefer **Cowrie** for speed/persistence on modest hardware; always **containment-first**. Higher fidelity ≠ fooling a live attacker.

## Data and methods

1. **Magazov et al. (2026b)** de-identified SSH commands, CC BY 4.0, [Zenodo](https://doi.org/10.5281/zenodo.20816078) (~12.9k command rows). Screened slice: **20 sessions × ~70 shared commands**, Magazov ×5 freeze.
2. **Ubuntu ground truth** from offline `ubuntu:24.04` (`--network none`) → `ground_truth.jsonl` / test-set sessions.
3. **Logs:** command, reply, delay, tokens, system, settings, run, break/skip → JSONL.
4. **Detector:** nonempty Ubuntu stdout joined with matching Cowrie/Llama/Qwen OK replies; ANSI/prompt chrome stripped; `GroupShuffleSplit` by `session_id` (seed 25).

## Repository layout

```
Patil_Devyani_5034YVIH_Report.docx   submitted FPR
configs/cowrie.cfg.example
data/MANIFEST.txt                    corpus URL, licence, size, rows
data/analysis/runs5/                 Magazov ×5 tables
data/analysis/ubuntu_runs1/          Ubuntu fidelity tables
data/analysis/detector/              RQ3 metrics + confusion plots
data/freeze_2026-11-10/              freeze artefacts
docs/cowrie_localhost.md
docs/REUSE.md                        plug-in another model
notebooks/detector_colab.ipynb
scripts/01_download.py
scripts/02_screen.py
scripts/03_testset.py
scripts/04_replay.py                 same sessions → backends → JSONL
scripts/05_analyse.py                metrics, CIs, Wilcoxon, RQ4 audit
scripts/06_train_detector.py         exploratory TF-IDF + LR (RQ3)
src/session_memory.py                structured state, no host shell
```

## Setup

Python 3.11+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Fill `.env` when a backend is available. Blank value → recorded skip. **Never commit `.env`.**

```powershell
ollama pull llama3.1:8b
ollama pull qwen2.5:7b
```

Ollama and Cowrie must listen on **`127.0.0.1` only**. Cowrie steps: [docs/cowrie_localhost.md](docs/cowrie_localhost.md).

### Plug in another model (C5)

```env
EXTRA_OLLAMA_MODELS=mistral-7b=mistral:7b
```

Or change `LLAMA_MODEL` / `QWEN_MODEL`. Re-run `04_replay.py` + `05_analyse.py` on the **same** session file. Details: [docs/REUSE.md](docs/REUSE.md).

## How to reproduce

Pipeline smoke:

```powershell
python scripts/01_download.py
python scripts/02_screen.py
python scripts/03_testset.py
python scripts/04_replay.py --smoke
python scripts/05_analyse.py
```

Magazov paired replay (example):

```powershell
python scripts/04_replay.py --source magazov --max-sessions 20 --runs 5
python scripts/05_analyse.py
```

Ubuntu test-set replay (when `data/test_set/` exists):

```powershell
python scripts/04_replay.py --source test-set --runs 1
python scripts/05_analyse.py
```

Detector (RQ3):

```powershell
python scripts/06_train_detector.py
```

`--full` replays the entire Magazov corpus and is **off** by default (protects paid APIs).

Frozen dissertation numbers live under `data/analysis/` and `data/freeze_2026-11-10/`. New plug-in runs are **additional** comparisons, not replacements for the freeze unless you re-run the full protocol.

## Scores (what `05_analyse.py` / detector report)

- **Fidelity** — normalised reply vs Ubuntu stdout.
- **Consistency** — agreement across runs / within protocol.
- **Session survival** — commands before first break.
- **Delay** — mean with 95% bootstrap CI.
- **Wilcoxon** — paired `commands_completed` vs Cowrie (≥5 pairs).
- **API cost** — only if price env vars + live key; local/Cowrie = £0 when they reply.
- **RQ3** — accuracy, macro-F1, AUROC, per-class F1 ([RESULTS_DETECTOR.md](RESULTS_DETECTOR.md)).
- **RQ4** — `rq4_containment.json` pass/fail checklist.

## Licences

- Magazov corpus/results: **CC BY 4.0** (attribute Zenodo).
- Code/prompts inside that zip: MIT (stay in `data/raw/`, not vendored here).
- Cowrie: BSD-3-Clause.
- Llama 3.1 / Qwen 2.5 weights: confirm the licence of the file you pull.
- GPT-4o mini: provider API terms; key stays in `.env`.

## Limitations

- Localhost replay lab only — **not** a public honeypot.
- GPT-4o mini was **skipped** in the freeze (no API key).
- Local 7–8B models on ~7.5 GB RAM CPU often hit **TimeoutError** / >5 s breaks → short Magazov survival.
- Detector is **exploratory** (small held-out LLM support).
- Higher Ubuntu fidelity than Cowrie does **not** mean live attackers are fooled.

## Tags

`v0.1` data · `v0.2` honeypot · `v0.3` results · `v1.0` submission.
