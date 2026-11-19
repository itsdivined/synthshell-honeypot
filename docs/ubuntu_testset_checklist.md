# Ubuntu test-set checklist (C2 / RQ1 fidelity)

**Status (11 Nov 2026):** captured. `data/test_set/sessions.jsonl` and `data/test_set/ground_truth.jsonl` exist (~20 sessions / ~200 commands). Method: clean **Ubuntu-24.04 WSL** as user `ubuntu` (not the Cowrie WSL; Docker Desktop was not installed / cloud-images pull timed out). Validate with `python scripts/03_testset.py`.  
**Do not start Docker/containers while a heavy Ollama Magazov replay is running or RAM is tight.**

Freeze reminder: tables **14 Nov 2026**; report **20 Nov**; viva **23 Nov**.

## What `scripts/03_testset.py` needs

1. Valid schemas in `data/templates/*.json` (already present).
2. Pipeline fixture `data/fixtures/pipeline_check.jsonl` (already present).
3. Captured study files (still missing):
   - `data/test_set/sessions.jsonl` — about **20** sessions / about **200** commands (`TEST_SESSIONS` / `TEST_COMMANDS` in `src/config.py`).
   - `data/test_set/ground_truth.jsonl` — matching real Ubuntu outputs for fidelity scoring.
4. Keep about **40** validation commands separate from the test set (`VALIDATION_COMMANDS`).

Until (3) exists, `python scripts/03_testset.py` exits with **TEST SET MISSING** (expected).

## Capture steps (offline container)

1. Free RAM: stop unused Ollama models / other heavy processes if the laptop is tight.
2. Start a clean Ubuntu with **no network** (preferred Docker), **or** a fresh Ubuntu-24.04 WSL distro that does **not** host Cowrie:

```text
docker run --rm -it --network none ubuntu:24.04
```

Alternate used 11 Nov 2026 (Docker missing): `winget install Canonical.Ubuntu.2404`, then `ubuntu2404 install --root`, capture as user `ubuntu` via `scripts/capture_ubuntu_testset.py`.

3. Inside the container, run each planned command; record cwd, exit behaviour, and stdout/stderr text.
4. Write session scripts to `data/test_set/sessions.jsonl` (one JSON object per line; each row needs `session_id`).
5. Write matching ground truth to `data/test_set/ground_truth.jsonl` (same `session_id` linkage; follow `data/templates/ground_truth.schema.json`).
6. Validate:

```text
python scripts/03_testset.py
```

7. Replay and analyse (after Magazov freeze numbers are locked, or if you still have time before 14 Nov). Fidelity joins on `(session_id, step)`, so Magazov logs will not fill fidelity cells — replay the Ubuntu test set itself:

```text
python scripts/04_replay.py --source test-set --runs 5 --log data\logs\replay_ubuntu_testset_runs5.jsonl
python scripts/05_analyse.py --log data\logs\replay_ubuntu_testset_runs5.jsonl --truth data\test_set\ground_truth.jsonl --out-dir data\analysis\ubuntu_runs5
```

## Honest viva line

Magazov public corpus is the completed multi-run comparison. Ubuntu ground truth is still the planned C2 capture for RQ1 fidelity — not invented, not claimed done.
