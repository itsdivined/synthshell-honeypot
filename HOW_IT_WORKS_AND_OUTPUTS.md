# How this project works — and where the outputs are

**Student:** Patil Devyani Anil (5034)  
**Project folder:** `C:\Users\devyani patil\honeypot`  
**Guide date:** 10 November 2026  

This note explains the lab in plain steps. It is **not** the coursework report. Use it to run a short check, read logs, and open the finished Magazov study tables **without** re-running the overnight 5-run job.

---

## A) Smoke result (10 Nov 2026)

Lab check before smoke:

- `.venv` works (Python 3.12 + paramiko/numpy/scipy)
- Cowrie listening on `127.0.0.1:2222` — **OPEN**
- Ollama on `127.0.0.1:11434` — **OPEN**
- Models present: `llama3.1:8b`, `qwen2.5:7b`
- Magazov 5-run log left untouched: `data\logs\replay_magazov_20sess_runs5.jsonl` (871382 bytes, mtime 7 Nov 2026)

Command run:

```powershell
cd "C:\Users\devyani patil\honeypot"
.\.venv\Scripts\python.exe scripts\04_replay.py --smoke --log data\logs\smoke_check_20261110.jsonl
```

Console summary:

| Item | Result |
| --- | --- |
| Containment | **pass** |
| Source | pipeline-check (3 benign commands × 1 run × 4 systems = 12 log rows) |
| cowrie | ok=3 skipped=0 error=0 |
| gpt-4o-mini | ok=0 skipped=3 error=0 (no `OPENAI_API_KEY`) |
| llama-3.1-8b | ok=1 skipped=0 error=2 |
| qwen-2.5-7b | ok=2 skipped=0 error=1 |
| Smoke log | `data\logs\smoke_check_20261110.jsonl` |

Sample replies (short, no secrets):

- **Cowrie OK** — command `pwd` → reply includes `/home/labuser` and a Cowrie-style prompt (`labuser@svr04`).
- **Llama OK** — command `ls` → short shell-like text (e.g. prompt + a filename). Delay can be large on this laptop.
- **GPT** — every row `skipped` with reason: API key not set.

If Cowrie port 2222 is closed next time: open **Ubuntu (WSL)** and start Cowrie there (see `docs\cowrie_localhost.md`), then re-check `127.0.0.1:2222`.

---

## B) How the project works (8–10 short steps)

1. **Goal:** Replay the **same** saved commands to four systems (Cowrie, GPT-4o mini, Llama, Qwen) in a closed lab on `127.0.0.1` only — not a public honeypot.
2. **Download data (already done):** `scripts\01_download.py` fetches the Magazov Zenodo zip and writes `data\MANIFEST.txt`.
3. **Screen IPs (already done):** `scripts\02_screen.py` counts addresses only; it does not store command text.
4. **Ubuntu test set (optional / still missing):** `scripts\03_testset.py` checks `data\test_set\` JSONL files. Until those exist it exits with “TEST SET MISSING” — expected.
5. **Replay:** `scripts\04_replay.py` sends each command in a shared list to all four backends and appends JSONL rows to a log file.
6. **What one command does:**
   - **Cowrie:** SSH client talks to `127.0.0.1:2222` and records Cowrie’s scripted shell reply + delay.
   - **Llama / Qwen:** HTTP text call to Ollama on `127.0.0.1:11434` with session-memory text; **no** host OS execution; **no** tools.
   - **GPT-4o mini:** text call to OpenAI **only if** `OPENAI_API_KEY` is set; otherwise the row is **skipped** (system stays in the study).
7. **Break rule (for scoring later):** empty reply, wrong/contradictory reply, AI self-disclosure, or delay **> 5 seconds**.
8. **Analyse:** `scripts\05_analyse.py` reads a JSONL log and writes `tables.md`, `summary.json`, `rq4_containment.json` (bootstrap CIs, Wilcoxon when pairs exist, containment audit).
9. **Study already finished:** Magazov 20 sessions × 5 runs → `data\logs\replay_magazov_20sess_runs5.jsonl` → scored in `data\analysis\runs5\`. **Do not restart `--runs 5`.**
10. **Read results:** open `data\analysis\runs5\tables.md` for the real study table (Cowrie 350 ok; GPT 350 skipped; Llama 86 ok / 264 timeout; Qwen 153 ok / 197 timeout; RQ4 Passed).

### Pipeline picture

```text
01_download  →  Magazov zip + MANIFEST
02_screen    →  IP counts only
03_testset   →  check Ubuntu JSONL (optional; often missing)
04_replay    →  same sessions → four systems → *.jsonl log
05_analyse   →  tables.md + summary.json + rq4_containment.json
```

### What each script does

| Script | Job |
| --- | --- |
| `01_download.py` | Download Magazov corpus from Zenodo; write `data\MANIFEST.txt` |
| `02_screen.py` | Count IPs in the corpus; no command payloads saved |
| `03_testset.py` | Validate Ubuntu test-set scaffold (`sessions.jsonl` + `ground_truth.jsonl`) |
| `04_replay.py` | Replay shared sessions to Cowrie + 3 LLMs; write JSONL |
| `05_analyse.py` | Score a log → comparison tables, stats, RQ4 containment |

### Exact commands

**Smoke (short, for health check):**

```powershell
cd "C:\Users\devyani patil\honeypot"
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe scripts\04_replay.py --smoke --log data\logs\smoke_check_20261110.jsonl
.\.venv\Scripts\python.exe scripts\05_analyse.py --log data\logs\smoke_check_20261110.jsonl --out-dir data\analysis\smoke_check_20261110
```

**Full Magazov study (already done — do not re-run overnight):**

```powershell
# Already completed 7 Nov 2026:
# python scripts\04_replay.py --source magazov --max-sessions 20 --runs 5 --log data\logs\replay_magazov_20sess_runs5.jsonl

# Re-score only (safe; does not replay):
.\.venv\Scripts\python.exe scripts\05_analyse.py --log data\logs\replay_magazov_20sess_runs5.jsonl --out-dir data\analysis\runs5
```

---

## C) Where to open outputs on this laptop

| What | Path |
| --- | --- |
| Today’s smoke log | `C:\Users\devyani patil\honeypot\data\logs\smoke_check_20261110.jsonl` |
| Magazov 5-run raw log (do not overwrite) | `C:\Users\devyani patil\honeypot\data\logs\replay_magazov_20sess_runs5.jsonl` |
| **Real study tables (open this)** | `C:\Users\devyani patil\honeypot\data\analysis\runs5\tables.md` |
| Study numbers (JSON) | `C:\Users\devyani patil\honeypot\data\analysis\runs5\summary.json` |
| RQ4 containment | `C:\Users\devyani patil\honeypot\data\analysis\runs5\rq4_containment.json` |
| Early freeze copy (if present) | `C:\Users\devyani patil\honeypot\data\freeze_2026-11-10\` |
| Backup of old default `replay.jsonl` | `data\logs\replay.jsonl.bak_before_smoke_*` |
| This guide (project) | `C:\Users\devyani patil\honeypot\HOW_IT_WORKS_AND_OUTPUTS.md` |
| This guide (Downloads) | `C:\Users\devyani patil\Downloads\HOW_IT_WORKS_AND_OUTPUTS.md` |

### Fields inside a replay JSONL command row (typical)

Open the smoke log in any text editor. Each line is one JSON object. Useful fields:

- `record_type` — `command` (or run metadata)
- `system` — `cowrie` / `gpt-4o-mini` / `llama-3.1-8b` / `qwen-2.5-7b`
- `command` — the input string
- `reply` — text returned (empty on skip/error)
- `status` — `ok` / `skipped` / `error`
- `delay_seconds` — timing
- `run` / `session_id` — which repeat and session

---

## D) Magazov 5-run results are already ready

You do **not** need another overnight run to see study output.

Open: **`data\analysis\runs5\tables.md`**

Headline counts (from that analysis):

| System | OK | Skipped | Errors (timeouts) | Mean cmds completed | Mean delay (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| cowrie | 350 | 0 | 0 | 3.50 | ~0.37 |
| gpt-4o-mini | 0 | 350 | 0 | — | — |
| llama-3.1-8b | 86 | 0 | 264 | 0.20 | ~51.5 |
| qwen-2.5-7b | 153 | 0 | 197 | 0.17 | ~50.4 |

RQ4 containment in that folder: **Passed**.

Fidelity cells are blank until an Ubuntu ground-truth file exists — that is expected, not a smoke failure.
