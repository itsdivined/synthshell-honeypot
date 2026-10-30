# Generative AI Deception: Dynamic LLM-Powered Honeypots

Patil Devyani Anil, MSc Data Science (FT), module 7FTC2001. Supervisor: Dr Rama Abirami K.

Private repository: `itsdivined/synthshell-honeypot`.



## Aim

The main question is how realistic, consistent, and cost-effective an LLM honeypot is compared with a traditional honeypot, and which type of LLM gives the best balance.

A session enters an SSH-style front end. Cowrie answers with its own scripted shell. Each LLM returns text only. Session memory records the current directory, files created, changed, or deleted, and users added, and that text is sent with the next command. The model is not given a tool, and commands are not passed to the host operating system.

## Research gap

There is no repeatable multi-step test that compares Cowrie with several LLM honeypots on consistency, session survival, speed, cost, and injection resistance. Existing studies usually fix one model, send one command per session, rely on small human studies or field deployments that cannot be rerun, and do not compare engagement under identical conditions. They also leave invented details, leaked instructions, slow replies, prompt injection, and paid APIs weakly measured.

## Novelty

LLM honeypots already exist. The novelty is what is measured and how:

1. Multi-step, stateful testing, with scripted sessions and ground truth from a real Linux container.
2. One repeatable test in which Cowrie and three LLM honeypots receive identical sessions.
3. Session survival as a repeatable proxy for engagement, plus the technique labels each system lets a defender observe.
4. Small local models compared with a commercial API, for organisations that cannot send data outside.
5. Multi-turn prompt-injection tests, listed as untested in the 2026 benchmark. In this repository, RQ4 is a containment audit: local bind, no honeypot outbound channel, text-only model output, and no host execution. Injection wording is not stored here.

## Contributions

- C1. A working LLM honeypot prototype with session-state memory, on a standard SSH front end.
- C2. A reusable test set of about 200 commands and 20 scripted multi-step sessions, with ground-truth outputs.
- C3. A controlled comparison of three LLMs and Cowrie on realism, consistency, speed, cost, and session survival.
- C4. Technique-label counts and the containment audit, with design recommendations for a low-cost honeypot.

## Research questions and objectives

| | Question | Objective |
| --- | --- | --- |
| RQ1 | How realistic and consistent are LLM honeypot replies compared with real Linux output? | O1. Measure fidelity and multi-step consistency on about 200 commands and 20 sessions. |
| RQ2 | How do the three LLMs compare on response time and cost? | O2. Record delay per command and cost per session for each model. |
| RQ3 | How far do scripted sessions get before each system gives itself away, and which techniques are observed? | O3. Replay sessions until the first break. Compare commands completed and technique labels with Cowrie. |
| RQ4 | How well does each LLM honeypot resist prompt injection? | O4. Run the containment audit and recommend a low-cost design. The audit is not a list of injection strings. |

A break is an empty reply, a wrong or contradictory reply, an AI self-disclosure, or a delay above 5 seconds. The study setting is 5 runs per system, 95% bootstrap confidence intervals, and Wilcoxon signed-rank tests. Prompt wording, temperature (0, 0.2, 0.5), and history window (5, 10, or 20 commands) are tuned on about 40 validation commands kept separate from the test set.

## Systems

The comparison always has four rows. If a key or a local model is missing, that row is recorded as a skip. The system is not removed from the study.

| System | Role | How it is reached |
| --- | --- | --- |
| Cowrie | Scripted baseline | `127.0.0.1` only. See `docs/cowrie_localhost.md`. |
| GPT-4o mini | Commercial API | `OPENAI_API_KEY` in `.env`. Text call to `api.openai.com`. No tools. |
| Llama 3.1 8B | Local model | Ollama tag `llama3.1:8b` on `127.0.0.1`. Optional if this machine cannot run it. |
| Qwen 2.5 7B | Local model | Ollama tag `qwen2.5:7b` on `127.0.0.1`. Optional if this machine cannot run it. |

A few safety-critical categories, sudo and password-file reads, get a fixed denial before an LLM call. Cowrie uses its own replies.

## Data and methods

1. Ground truth: about 200 commands (files, users, processes, network, system information) run later in a clean Ubuntu container with no network.
2. Scripted sessions: about 20 sessions of 10 to 20 commands. The plan's themes are discovery, credential-file probing, creating and editing files, persistence checks, and cleaning up. The command lists are captured in the lab. They are not stored in this scaffold.
3. Public corpus: Magazov et al. (2026), about 12,900 de-identified commands, CC BY 4.0, https://doi.org/10.5281/zenodo.20816078. Used as the shared realistic sessions.
4. Experiment logs: command, reply, delay, token count, system, model settings, and run number, from all four systems.

The same session list is sent to every system. Replies are compared with the container ground truth when that file exists. Logs are JSONL.

## Repository layout

```
configs/cowrie.cfg.example   localhost Cowrie settings
data/MANIFEST.txt            corpus URL, licence, size, row count
data/README.md               data note
data/fixtures/               benign pipeline check, not the study set
data/raw/                    gitignored Zenodo zip
data/templates/              JSON schemas
data/test_set/               Ubuntu capture, gitignored
docs/cowrie_localhost.md
scripts/01_download.py       fetch the Zenodo record
scripts/02_screen.py         count IP addresses, no command text
scripts/03_testset.py        check the test-set scaffold
scripts/04_replay.py         same sessions, four systems, write logs
scripts/05_analyse.py        scores, bootstrap CIs, Wilcoxon, RQ4 audit
src/session_memory.py        structured state, no host shell
SCHEDULE.md
```

## Setup

Python 3.11 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Fill `.env` when a backend is available. Leave a value blank to record a skip. Never commit `.env`.

Cowrie install steps are in `docs/cowrie_localhost.md`. Local models, when the machine can run them:

```powershell
ollama pull llama3.1:8b
ollama pull qwen2.5:7b
```

Ollama must listen on `127.0.0.1` only.

## How to reproduce

Week 1 pipeline check:

```powershell
python scripts/01_download.py
python scripts/02_screen.py
python scripts/03_testset.py
python scripts/04_replay.py --smoke
python scripts/05_analyse.py
```

First paired replay, same Magazov slice to every configured backend (31 October-6 November):

```powershell
python scripts/04_replay.py --source magazov --max-sessions 20 --runs 1
```

Full study runs before the 14 November freeze. Use 5 runs. Point `--sessions` at the Ubuntu test set when it exists, and replay that same file to all four systems:

```powershell
python scripts/04_replay.py --source test-set --runs 5
python scripts/05_analyse.py
```

`--full` replays every command row in the corpus. It is off unless you set it, so a paid API is not sent the whole corpus by accident. The four-system design is unchanged.

`03_testset.py` exits with an error until `data/test_set/sessions.jsonl` and `data/test_set/ground_truth.jsonl` exist. That is the Ubuntu capture, still to do:

```powershell
docker run --rm -it --network none ubuntu:24.04
```

## Scores

`05_analyse.py` writes `results/tables.md`. Fidelity and invented content stay empty until the ground-truth file exists. Consistency is within-session agreement of replies to the same command. Session survival counts commands before the first break. Delay uses a 95% bootstrap interval. Wilcoxon signed-rank compares each LLM with Cowrie on commands completed when at least five paired sessions exist. API cost is computed only after `GPT4O_MINI_INPUT_PER_MILLION` and `GPT4O_MINI_OUTPUT_PER_MILLION` are set from the provider's current price. Local models and Cowrie are costed at zero when they reply. RQ4 writes `results/rq4_containment.json`.

## Licences

- Magazov et al. corpus and results: CC BY 4.0. Attribute the Zenodo deposit.
- Code and prompts inside that zip: MIT. They stay inside `data/raw/` and are not vendored here.
- Cowrie: BSD-3-Clause.
- Llama 3.1 weights: Llama 3.1 Community License. Confirm the file you download.
- Qwen 2.5 weights: Apache 2.0 for the official Qwen2.5 release. Confirm the file you download.
- GPT-4o mini: the provider's API terms. The key stays in `.env`.

## Limitations

This repository replays saved sessions in an isolated lab. It does not deploy a honeypot on a public address. The Ubuntu ground-truth set is not captured yet, so fidelity is not available until that file exists. A skipped backend means that part of the four-system run has not happened yet. Model weights are not committed.

## Tags

`v0.1` data, `v0.2` honeypot, `v0.3` results, `v1.0` submission. Tags are created at those milestones, not in the week-1 scaffold.
