# Project Brief — Generative AI Deception: Dynamic LLM-Powered Honeypots

**Prepared for:** professor demos and viva practice  
**Student:** Patil Devyani Anil  
**Student ID:** 5034  
**Programme / module:** MSc Data Science (FT), 7FTC2001  
**Supervisor:** Dr Rama Abirami K  
**Repository (public):** https://github.com/itsdivined/synthshell-honeypot  
**Brief date:** 7 November 2026 (Magazov ×5 finished + analysed)  
**Sources used:** README.md, SCHEDULE.md, PDM plan (`PDM_Plan_Patil_Devyani_5034.docx`), `docs/cowrie_localhost.md`, configs/scripts/src headers, `data/MANIFEST.txt`, experiment logs under `data/logs/`, and results already on disk. Items not verified in those sources are marked **unknown**.

---

## 1. Title-page information

| Field | Value |
| --- | --- |
| Title | Generative AI Deception: Dynamic LLM-Powered Honeypots |
| Student | Patil Devyani Anil (ID 5034) |
| Award | MSc Data Science, full-time |
| Module | 7FTC2001 |
| Supervisor | Dr Rama Abirami K |
| GitHub | https://github.com/itsdivined/synthshell-honeypot (public) |
| Lab posture | Isolated laptop lab only — bind `127.0.0.1`, text-only model replies, **no** real OS command execution, **no** public honeypot |
| Practical freeze | Tables freeze **14 November 2026**; practical work ready before **15 November 2026** |
| Report (FPR) | **20 November 2026** |
| Viva | **23 November 2026** |
| Ethics quiz | Completed **27 October 2026** (UH: https://ask.herts.ac.uk/ethics-approval) |

**One-sentence aim (README / PDM):** How realistic, consistent, and cost-effective an LLM honeypot is compared with a traditional honeypot, and which type of LLM gives the best balance.

---

## 2. Golden Circle (Why / How / What)

Applied to **this** project only (Simon Sinek style).

### Why

Scripted SSH honeypots such as Cowrie are useful but often recognisable because replies and filesystem state are fixed. LLM honeypots can invent plausible shell text for almost any command, yet they can forget session state, invent details, leak instructions, time out, or rely on paid APIs. Defenders and organisations need **evidence** for choosing a backend — not a single demo model in a one-off field trial. This project exists to give a **repeatable, closed-lab comparison** that a student (and later a small organisation) can re-run on the same sessions.

### How

- Replays the **same** saved sessions to four systems: Cowrie, GPT-4o mini (API), Llama 3.1 8B (Ollama), Qwen 2.5 7B (Ollama).
- Uses **session memory** (cwd, files created/changed/deleted, users added) sent with the next command; the model gets **no tools** and commands are **not** executed on the host OS.
- Scores realism/consistency (when Ubuntu ground truth exists), delay/cost, commands completed until a defined “break,” technique labels, and a **containment audit** for RQ4.
- Stays on **localhost** (`127.0.0.1`); skips missing backends instead of dropping them from the design.

### What

A working lab codebase (`synthshell-honeypot`) that downloads/screens the Magazov corpus, replays sessions, writes JSONL logs, analyses scores (bootstrap CIs, Wilcoxon when enough pairs exist), and documents Cowrie localhost setup — plus a planned Ubuntu container test set (~200 commands / ~20 sessions) that is **not captured yet** (see §6 and §10).

---

## 3. Research gap, novelty, contribution

### Research gap (exact sense from README / PDM)

There is no repeatable multi-step test that compares Cowrie with several LLM honeypots on consistency, session survival, speed, cost, and injection resistance. Existing studies usually fix one model, send one command per session, rely on small human studies or field deployments that cannot be rerun, and do not compare engagement under identical conditions. Invented details, leaked instructions, slow replies, prompt injection, and paid APIs are weakly measured.

### Novelty (what is measured and how — LLM honeypots already exist)

1. Multi-step, stateful testing, with scripted sessions and ground truth from a real Linux container.  
2. One repeatable test in which Cowrie and three LLM honeypots receive identical sessions.  
3. Session survival as a repeatable proxy for engagement, plus the technique labels (ATT&CK in the PDM wording) each system lets a defender observe.  
4. Small local models compared with a commercial API, for organisations that cannot send data outside.  
5. Multi-turn prompt-injection testing was listed as untested in the 2026 Magazov benchmark. **In this repository, RQ4 is operationalised as a containment audit** (local bind, no honeypot outbound channel, text-only model output, no host execution). Injection wording is **not** stored in the repo.

### Contributions (C1–C4)

| ID | Contribution |
| --- | --- |
| C1 | A working LLM honeypot prototype with session-state memory, on a standard SSH front end. |
| C2 | A reusable test set of about 200 commands and 20 scripted multi-step sessions, with ground-truth outputs. (**Status:** format/scaffold only — capture still to do.) |
| C3 | A controlled comparison of three LLMs and Cowrie on realism, consistency, speed, cost, and session survival. |
| C4 | Technique-label counts and the containment audit, with design recommendations for a low-cost honeypot. (PDM also framed C4 around multi-turn injection results; repo practice = containment audit + labels.) |

---

## 4. Four research questions and four objectives

Wording below is taken from the **PDM table** and cross-checked with **README.md**. Where README differs, both are shown.

| | Research question | Objective |
| --- | --- | --- |
| **RQ1** | How realistic and consistent are LLM honeypot replies compared with real Linux output? | **O1.** Measure fidelity and multi-step consistency on about 200 commands and 20 sessions. |
| **RQ2** | How do the three LLMs compare on response time and cost? | **O2.** Record delay per command and cost per session for each model. |
| **RQ3** | **PDM:** How far do scripted attack sessions get before each system gives itself away, and which attack techniques are observed? **README:** How far do scripted sessions get before each system gives itself away, and which techniques are observed? | **O3.** Replay sessions until the first break. Compare commands completed and technique / ATT&CK labels with Cowrie. |
| **RQ4** | How well does each LLM honeypot resist prompt injection? | **PDM O4:** Test about 20 injection inputs and recommend a low-cost design. **README O4 (what the code does now):** Run the containment audit and recommend a low-cost design. The audit is not a list of injection strings. |

**Break definition (README / PDM):** empty reply; wrong or contradictory reply; AI self-disclosure; or delay above **5 seconds**.

**Study settings (README / PDM / `src/config.py`):** 5 runs per system; 95% bootstrap confidence intervals; Wilcoxon signed-rank tests (LLM vs Cowrie on commands completed when ≥5 paired sessions). Tuning on ~40 validation commands kept separate from the test set: temperature (0, 0.2, 0.5), history window (5, 10, or 20).

**Honest RQ status for viva:** RQ1 fidelity needs Ubuntu ground truth (not captured yet). RQ2 delay is partially measurable from Magazov replays; GPT cost needs API key + price env vars. RQ3 session survival / labels partially available from Magazov logs. RQ4 containment audit **passed** on current config/source checks; full PDM-style injection battery is **not** stored as string lists in this repo.

---

## 5. Systems and models

The comparison always keeps **four rows**. A missing key or model is a **skip**, not removal from the study.

| System | Role | How it is run | Strengths (for viva) | Limits (observed / planned) |
| --- | --- | --- | --- | --- |
| **Cowrie** | Scripted baseline (BSD-3-Clause) | Localhost SSH, `127.0.0.1:2222` (see `docs/cowrie_localhost.md`, `configs/cowrie.cfg.example`). Upstream: https://github.com/cowrie/cowrie | Stable, fast, established baseline; works in smoke tests on this laptop via WSL | Fixed replies/filesystem; scanners can fingerprint scripted honeypots |
| **GPT-4o mini** | Commercial API | Text call to `api.openai.com` via `OPENAI_API_KEY` in `.env`; no tools | Strong language quality when key present; easy to cost once prices set | Needs key; data leaves machine; **currently skipped** in Magazov runs (no key) |
| **Llama 3.1 8B** | Local open-weight model | Ollama tag `llama3.1:8b` on `127.0.0.1:11434` | No outbound data for replies; free at inference | ~7.5 GB RAM laptop + CPU Ollama → many **TimeoutError** (~120 s) |
| **Qwen 2.5 7B** | Local open-weight model | Ollama tag `qwen2.5:7b` on `127.0.0.1:11434` | Same local privacy benefit | Same machine limits; frequent timeouts in Magazov ×1 run |

Fixed denials: a few safety-critical categories (e.g. sudo / password-file reads) get a fixed denial **before** an LLM call. Cowrie uses its own replies.

---

## 6. Data and methods

### 6.1 Magazov public corpus (verified in `data/MANIFEST.txt`)

| Item | Verified value |
| --- | --- |
| Citation | Magazov, R., Abeshev, K., Shamuratov, Y., Uralova, F. and Aksholak, G. (2026) *De-identified SSH honeypot attacker corpus*. Zenodo. |
| DOI | 10.5281/zenodo.20816078 — https://doi.org/10.5281/zenodo.20816078 |
| Licence | Data/results: **CC BY 4.0**; code/prompts inside zip: MIT |
| Size | 4,871,158 bytes; MD5 `dc4063023daca19c0a3ef9f8bb340477` (match OK) |
| Rows | **12,881** command rows (plan figure ~12,900); 24 command files; 9,324 distinct session IDs in command tables |
| Accessed | 2026-10-25 |
| IP screen | `scripts/02_screen.py`: public addresses needing review = **0** (`data/screen_summary.txt`) |

Used as shared realistic session traffic for paired replay.

### 6.2 Ubuntu container test set (planned — status honest)

| Planned artefact | Path | Status on disk (6 Nov 2026) |
| --- | --- | --- |
| ~200 ground-truth commands | `data/test_set/ground_truth.jsonl` | **Not present** (only `.gitkeep`) |
| ~20 scripted sessions | `data/test_set/sessions.jsonl` | **Not present** |
| ~40 validation commands | Kept separate from test set (plan) | **Not captured yet** |

Capture method stated in README: `docker run --rm -it --network none ubuntu:24.04`.  
`scripts/03_testset.py` exits with an error until those JSONL files exist. Themes planned: discovery, credential-file probing, creating/editing files, persistence checks, cleanup.

### 6.3 Experiment logs

JSONL fields include command, reply, delay, token count, system, model settings, run number, status, technique_label, etc. (`data/templates/experiment_log.schema.json`).

### 6.4 Metrics and stats plan

| Measure | Linked RQ | Notes from README / `05_analyse.py` |
| --- | --- | --- |
| Fidelity / invented content | RQ1 | Empty until ground-truth file exists |
| Consistency | RQ1 | Within-session agreement of replies to the same command |
| Delay + 95% bootstrap CI | RQ2 | From logged `delay_seconds` |
| Cost USD | RQ2 | GPT only after `GPT4O_MINI_*_PER_MILLION` set; local/Cowrie costed at 0 when they reply |
| Commands completed / session survival | RQ3 | Until first break |
| Technique labels | RQ3 | Count/list of labels observed |
| Wilcoxon signed-rank | RQ3 support | Each LLM vs Cowrie on commands completed; needs ≥5 paired sessions |
| Containment audit | RQ4 | `results/rq4_containment.json` |

Default study command (when Ubuntu set exists):  
`python scripts/04_replay.py --source test-set --runs 5` then `python scripts/05_analyse.py`.

---

## 7. Related research papers

Only papers already in the PDM / plan (plus publication links supplied as established for this brief). **Do not invent extras.**

| Paper | Link / DOI | One-line relevance to this project |
| --- | --- | --- |
| Javadpour et al. (2024). Survey on cyber deception / honeypot performance. *Computers & Security*, 140, 103792. | doi:10.1016/j.cose.2024.103792 | Background: honeypots as cyber-deception; frames why realism and evaluation matter. |
| Magazov et al. (2026a). Benchmarking LLM backends for generative SSH honeypots. *AI*, 7(8), 287. | doi:10.3390/ai7080287 | Closest benchmark framing; notes single-command sessions and gaps this project targets (multi-step, multi-backend comparison). |
| Magazov et al. (2026b). De-identified SSH honeypot attacker corpus [Dataset]. | doi:10.5281/zenodo.20816078 | Shared realistic traffic used in this lab’s Magazov replays. |
| Sladić et al. (2023). LLM in the shell: generative honeypots. | arXiv:2309.00155 | Early generative honeypot line of work; motivates LLM shell replies. |
| Sladić et al. (2024). EuroS&PW paper (TNR 0.90 reported in plan notes). | doi:10.1109/EuroSPW61312.2024.00054 | Peer-reviewed generative honeypot evaluation context for human/realism discussion. |
| Otal and Canbaz (2024). LLM honeypot … interactive honeypot systems. IEEE CNS. | IEEE Xplore 10735607; arXiv:2409.08234 | Interactive LLM honeypot system; hard-to-repeat / field-style evaluation contrast with this closed replay design. |
| Wang et al. HoneyGPT (SRDS line of work; journal version *Computer Networks* 282 (2026) 112223). | doi:10.1016/j.comnet.2026.112223; also arXiv:2406.01882 (as cited in PDM) | LLM terminal honeypot / engagement discussion; motivates controlled survival comparison. |
| Cowrie project | https://github.com/cowrie/cowrie (BSD-3-Clause) | Scripted baseline implementation used as System 1. |

---

## 8. Lab architecture and containment (RQ4)

### Architecture (conceptual)

```
Saved sessions (Magazov slice or future Ubuntu test set)
        │
        ▼
 scripts/04_replay.py  ──►  same session list to all four backends
        │
        ├── Cowrie client ──► 127.0.0.1:2222 (WSL/local Cowrie)
        ├── GPT-4o mini ──► api.openai.com (text only; skip if no key)
        ├── Llama 3.1 8B ──► Ollama 127.0.0.1:11434
        └── Qwen 2.5 7B ──► Ollama 127.0.0.1:11434
        │
        ▼
 data/logs/*.jsonl  ──►  scripts/05_analyse.py  ──►  results/tables.md, summary.json, rq4_containment.json
```

Session memory (`src/session_memory.py`): structured state only; **no** host shell; **no** host filesystem reads/writes for “real” execution.

### Containment audit (current result: **Passed**)

From `results/rq4_containment.json` / README scoring notes:

| Check | Result |
| --- | --- |
| local_bind | pass — listen host is 127.0.0.1 |
| cowrie_localhost | pass |
| ollama_localhost | pass |
| openai_host_pinned | pass — GPT text calls use api.openai.com only |
| no_host_execution | pass |
| no_honeypot_outbound | pass |
| text_only_output | pass |
| no_model_tools | pass |
| source_has_no_host_shell | pass |

**Viva wording:** RQ4 in the running code is a **containment audit**, not a published list of jailbreak/injection payloads. That matches ethics (no attack-tool distribution) and the README note that injection wording is not stored here.

---

## 9. How to run / demo on the laptop (smoke steps — not exploits)

Prerequisites: Python 3.11+ (repo uses a `.venv`), optional Cowrie on localhost, optional Ollama models, optional OpenAI key.

```powershell
cd "C:\Users\devyani patil\honeypot"
.\.venv\Scripts\Activate.ps1
# .env already used for lab settings; never commit .env
```

**Week-1 / demo smoke pipeline (README):**

```powershell
python scripts/01_download.py          # Magazov zip + MANIFEST (already done)
python scripts/02_screen.py            # IP counts only
python scripts/03_testset.py           # Expect error until Ubuntu JSONL exists
python scripts/04_replay.py --smoke    # Benign fixture, four systems
python scripts/05_analyse.py           # Tables + RQ4 audit
```

**Cowrie smoke (docs):** Cowrie must listen on `127.0.0.1:2222` only; credentials from Cowrie’s own `userdb` into `.env` as `COWRIE_USER` / `COWRIE_PASSWORD`. Smoke on this machine has shown Cowrie answering via WSL on `127.0.0.1:2222`.

**Paired Magazov replay (shared sessions):**

```powershell
python scripts/04_replay.py --source magazov --max-sessions 20 --runs 1
# Full study setting:
python scripts/04_replay.py --source magazov --max-sessions 20 --runs 5 --log data\logs\replay_magazov_20sess_runs5.jsonl
```

**Local models (if machine can load them):**

```powershell
ollama pull llama3.1:8b
ollama pull qwen2.5:7b
# Ollama must listen on 127.0.0.1 only
```

**Demo talking points (safe):** show README aim → four-system table → containment pass → Magazov log snippet with statuses (`ok` / `skipped` / `error`) → honest limits (RAM, timeouts, missing ground truth). Do **not** demo attack payloads or injection string lists.

---

## 10. Current results and honest limitations

### 10.1 Magazov 20 sessions × 1 run (with Cowrie)

**Log:** `data/logs/replay_magazov_20sess_runs1_with_cowrie.jsonl`  
**Verified command-row counts (20 sessions):**

| System | ok | skipped | error (timeouts) |
| --- | ---: | ---: | ---: |
| cowrie | **70** | 0 | 0 |
| gpt-4o-mini | 0 | **70** (no `OPENAI_API_KEY`) | 0 |
| llama-3.1-8b | **18** | 0 | **52** (`TimeoutError: timed out`) |
| qwen-2.5-7b | **32** | 0 | **38** (`TimeoutError: timed out`) |

### 10.2 Magazov 20 sessions × 5 runs — **finished** (7 Nov 2026 ~17:31 local)

- **Started:** Friday 6 November 2026 ~22:42 via `data/logs/_start_magazov_runs5.ps1`  
- **Finished:** Saturday 7 November 2026 ~17:31 (stdout closed; PIDs gone; log mtime stable)  
- **Log:** `data/logs/replay_magazov_20sess_runs5.jsonl` (~871 KB; **1400** command rows + 1 run meta row; 20 sessions × 70 shared commands × 5 runs × 4 systems)  
- **Stdout totals:** cowrie ok=350; gpt-4o-mini skipped=350; llama-3.1-8b ok=86 error=264; qwen-2.5-7b ok=153 error=197  
- **Study incomplete** by design until GPT key is set (skipped system kept in the four-system table).

**Verified command-row counts (all 5 runs combined):**

| System | ok | skipped | error (timeouts) |
| --- | ---: | ---: | ---: |
| cowrie | **350** | 0 | 0 |
| gpt-4o-mini | 0 | **350** (no `OPENAI_API_KEY`) | 0 |
| llama-3.1-8b | **86** | 0 | **264** (`TimeoutError: timed out`) |
| qwen-2.5-7b | **153** | 0 | **197** (`TimeoutError: timed out`) |

**Analysis output (do not overwrite the runs5 log):** `data/analysis/runs5/`  
(`tables.md`, `summary.json`, `rq4_containment.json`, `SOURCE.txt`)

| System | Logged | OK | Skipped | Mean delay (s) [95% CI] | Mean commands completed | Technique labels |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| cowrie | 350 | 350 | 0 | 0.37 [0.34, 0.40] | **3.50** | 8 |
| gpt-4o-mini | 350 | 0 | 350 | — | — | 8 |
| llama-3.1-8b | 350 | 86 | 0 | 51.5 [42.5, 60.4] | **0.20** | 8 |
| qwen-2.5-7b | 350 | 153 | 0 | 50.4 [44.9, 55.7] | **0.17** | 8 |

**Wilcoxon** (commands completed, Cowrie vs LLM; scipy installed): vs Llama n=100, statistic=0.0, p≈1.1e-16; vs Qwen n=100, statistic=0.0, p≈1.8e-16; vs GPT n=0 (all skipped). **RQ4 containment: Passed.** Fidelity / consistency / invented-content blank (no Ubuntu ground truth yet).

### 10.3 Analysis artefacts currently on disk

- **Canonical Magazov ×5 tables:** `data/analysis/runs5/` (generated 7 Nov 2026 from the finished runs5 log).  
- **Canonical Magazov ×1 (with Cowrie):** `data/analysis/runs1_with_cowrie/`.  
- Root `results/tables.md` / `summary.json` may still be an older smoke-style run — prefer the `data/analysis/...` folders for freeze tables. Re-point with:  
  `python scripts/05_analyse.py --log data\logs\replay_magazov_20sess_runs5.jsonl --out-dir data\analysis\runs5`

### 10.4 Limitations (say these in viva)

1. **Isolated lab only** — not a public honeypot; external validity to live attackers is limited.  
2. **Ubuntu ground truth not captured** — RQ1 fidelity / invented-content scores unavailable.  
3. **GPT-4o mini skipped** until API key is set — four-system design preserved as skips.  
4. **~7.5 GB RAM, CPU Ollama** — timeouts dominate Llama/Qwen rows; delays often hit the 5 s “break” threshold and/or 120 s client timeout.  
5. **PDM RQ4 injection battery** vs **repo containment audit** — be explicit which was run.  
6. **Freeze deadline** — tables freeze **14 November 2026**; report **20 Nov**; viva **23 Nov**.

---

## 11. Timeline and assessment map

### Assessment (from module briefing / logbook)

| Component | Weight | Notes |
| --- | ---: | --- |
| PDM (plan + presentation) | 10% | Presented ~14–15 Oct 2026; plan file `PDM_Plan_Patil_Devyani_5034.docx` |
| Ethics quiz | 10% | **27 October 2026**; UH ethics info: https://ask.herts.ac.uk/ethics-approval |
| Final Project Report (FPR) | 70% | Due **20 November 2026** |
| Viva | 10% | **23 November 2026**; must pass viva (module: no viva = fail); overall pass ≥50% |

### Practical schedule (`SCHEDULE.md`)

| Dates | Work |
| --- | --- |
| 25–30 Oct | Repo, isolated sandbox, Cowrie on 127.0.0.1, Magazov download, ethics quiz 27 Oct |
| 31 Oct–6 Nov | Session memory + three LLM backends; first paired Magazov replay |
| 7–14 Nov | Full four-way runs, scores for all four RQs; **freeze tables 14 Nov** |
| Ready before | **15 November 2026** (practical ready) |
| 16–19 Nov | Report writing |
| 20 Nov | Report due |
| 21–22 Nov | Viva practice |
| 23 Nov | Viva |

Planned git tags (README): `v0.1` data, `v0.2` honeypot, `v0.3` results, `v1.0` submission.

### Ethics / DMP highlights (PDM)

- No human participants; no live/public deployment.  
- Magazov corpus de-identified by authors; IP screen run; no uploaded attacker files kept as study payloads.  
- API keys in gitignored `.env`; localhost bind only.  
- Disclose AI use per UH policy.  
- Licences cited: Magazov CC BY 4.0; Cowrie BSD-3-Clause; model licences as published.

---

## 12. Likely viva questions + short answer bullets

**Q: What is your project in one minute?**  
- Closed-lab comparison of Cowrie vs three LLM honeypots on identical sessions.  
- LLMs return text only with session memory; no host command execution.  
- Measure fidelity (when GT exists), delay/cost, survival until break, labels, containment.

**Q: Why is this novel if LLM honeypots already exist?**  
- Novelty is the **measurement design**: multi-step + four systems on the same sessions + survival proxy + local vs API + containment audit.  
- Not claiming to invent the first LLM honeypot.

**Q: What are your four RQs?**  
- Recite the table in §4; flag README vs PDM wording on RQ3/RQ4.

**Q: How do you define a “break”?**  
- Empty / wrong or contradictory / AI self-disclosure / delay > 5 s.

**Q: Why Cowrie?**  
- Standard scripted SSH honeypot baseline; BSD-3-Clause; comparable under identical replay.

**Q: Why these three LLMs?**  
- One commercial API + two small local models for organisations that cannot export data; all stay as rows even if skipped.

**Q: Did you deploy a honeypot on the internet?**  
- No. Bind `127.0.0.1` only; replay saved sessions.

**Q: Can the model run shell commands on your PC?**  
- No. Text-only; `execute_commands_on_host = False`; containment audit checks this.

**Q: What data did you use?**  
- Magazov Zenodo corpus (~12.9k de-identified commands, CC BY 4.0).  
- Ubuntu ~200/20 planned — **not captured yet**.

**Q: What results do you have today?**
- Magazov 20×1: Cowrie 70 ok; GPT 70 skipped; Llama 18 ok / 52 timeout; Qwen 32 ok / 38 timeout.
- Magazov 20×5: **finished** — Cowrie 350 ok; GPT 350 skipped; Llama 86 ok / 264 timeout; Qwen 153 ok / 197 timeout. Tables in `data/analysis/runs5/`.
- RQ4 containment: passed.

**Q: Why so many timeouts?**  
- Laptop ~7.5 GB RAM; CPU Ollama; 8B/7B models; long contexts from history window.

**Q: How will you finish RQ1?**  
- Capture Ubuntu ground truth offline (`--network none`), then replay test-set and compute fidelity.

**Q: What about prompt injection (RQ4)?**  
- PDM planned ~20 inputs; repository implements and passes a **containment audit**; injection strings are not stored in the repo.

**Q: Statistical plan?**  
- 5 runs; bootstrap 95% CIs on delay/completed; Wilcoxon vs Cowrie when ≥5 paired sessions.

**Q: Licences / ethics?**  
- Magazov CC BY 4.0 attributed; Cowrie BSD-3-Clause; ethics quiz 27 Oct; no live victims.

**Q: Show me the code path for a reply.**  
- `04_replay.py` → backends in `src/backends.py` → memory `src/session_memory.py` → JSONL → `05_analyse.py`.

**Q: What would you change with more time/RAM?**  
- Complete Ubuntu GT; finish 5 runs without timeouts (smaller models / GPU / longer budget); add GPT key for full four-way; re-run analysis for freeze tables.

---

## 13. File map of the repository

High-value paths for demo/viva (not every file under `.venv`):

```
README.md                          Aim, RQs, systems, reproduce steps, licences, limitations
SCHEDULE.md                        Week plan and assessment dates
PDM_Plan_Patil_Devyani_5034.docx   Approved 3-page plan (gap, novelty, RQs, DMP, refs)
Project_Logbook_Patil_Devyani_5034.docx
configs/cowrie.cfg.example         127.0.0.1 SSH/Telnet listen settings
docs/cowrie_localhost.md           Cowrie install/bind checklist
.env.example                       Lab env template (no secrets)
requirements.txt                   paramiko, numpy, scipy
scripts/01_download.py             Fetch Zenodo deposit → MANIFEST
scripts/02_screen.py               Count IPs; no command text stored
scripts/03_testset.py              Validate Ubuntu test-set scaffold
scripts/04_replay.py               Same sessions → four systems → JSONL
scripts/05_analyse.py              Scores, bootstrap, Wilcoxon, RQ4 audit
src/config.py                      SYSTEMS, RUNS=5, break delay, Zenodo URLs, LabConfig
src/backends.py                    Cowrie / OpenAI / Ollama text backends + skips
src/session_memory.py              Structured state; no host shell
src/replay.py                      Replay orchestration + containment gate
src/analyse.py                     Metrics + markdown/JSON summary
src/containment.py                 RQ4 audit checks
src/corpus.py                      Read Magazov tables from zip
src/fixed_replies.py               Safety-critical fixed denials
src/screen.py                      IP screening helpers
tests/test_lab.py                  Lab unit tests
data/MANIFEST.txt                  Verified Magazov download metadata
data/README.md                     Data note + status table
data/raw/                          Zenodo zip (gitignored)
data/fixtures/pipeline_check.jsonl Benign smoke fixture (not study set)
data/templates/*.schema.json       Session / ground-truth / experiment schemas
data/test_set/                     Ubuntu capture target (empty except .gitkeep)
data/logs/                         Experiment JSONL + run wrappers (gitignored content)
results/tables.md                  Comparison markdown (re-generate after full runs)
results/summary.json               Machine-readable scores
results/rq4_containment.json       Latest containment audit dump
results/README.md                  When to freeze tables
```

**Important logs for demos:**

- `data/logs/replay_magazov_20sess_runs1_with_cowrie.jsonl` — completed Magazov ×1 with Cowrie
- `data/logs/replay_magazov_20sess_runs5.jsonl` — Magazov ×5 **finished** (1400 command rows)
- `data/analysis/runs5/` — scored tables from that log
- `data/logs/smoke.jsonl` — early smoke  
- `data/logs/_start_magazov_runs5.ps1` — launcher for the 5-run job  

---

## Quick checklist before a professor demo

1. Confirm Cowrie still on `127.0.0.1:2222` if showing live baseline.  
2. Prefer Magazov ×5 tables in `data/analysis/runs5/` for freeze numbers (14 Nov).
3. Open README RQ table + containment pass + Magazov ×1 and ×5 counts.
4. Say clearly: Ubuntu test set **not yet captured**; GPT **skipped**; local models **timeout-limited**.
5. Freeze narrative after 14 Nov tables; report by 20 Nov; viva 23 Nov.

---

*End of brief. §10.2 Magazov ×5 marked finished 7 Nov 2026; re-check only if a new replay is started.*
