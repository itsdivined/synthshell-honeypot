# Reuse this lab: plug in a new model

This repository is a **repeatable comparison harness**. Other people can keep the same sessions, containment rules, and analysis, and only change which models answer.

Full Magazov / Ubuntu replay still needs **local** Cowrie + Ollama (or an optional OpenAI key). Google Colab is only for the small TF-IDF detector notebook.

## What stays fixed

- Same saved session list (`data/test_set/sessions.jsonl` or Magazov slice)
- Same containment rules (`127.0.0.1`, text-only, no host execution)
- Same pipeline: `04_replay.py` → JSONL → `05_analyse.py`
- Default first four rows: Cowrie, GPT-4o mini, Llama 3.1 8B, Qwen 2.5 7B

## Option A — swap a local model (no code change)

In `.env`, change the Ollama tag for an existing slot:

```env
LLAMA_MODEL=llama3.2:3b
QWEN_MODEL=gemma2:9b
```

Pull the tags, then re-run the same replay command you already use. Row names stay `llama-3.1-8b` / `qwen-2.5-7b` (study labels); only the underlying weights change. Say that clearly in any new write-up.

## Option B — add another local model (recommended)

1. Install the model in local Ollama, for example:

```powershell
ollama pull mistral:7b
```

2. Add one line to `.env` (comma-separated if you add more than one):

```env
EXTRA_OLLAMA_MODELS=mistral-7b=mistral:7b
```

Format: `short-name=ollama-tag`. Short names must not collide with `cowrie`, `gpt-4o-mini`, `llama-3.1-8b`, or `qwen-2.5-7b`.

3. Re-run the comparison on the **same** session file:

```powershell
python scripts/04_replay.py --source test-set --sessions data/test_set/sessions.jsonl --runs 1 --log data/logs/replay_with_extra.jsonl
python scripts/05_analyse.py --log data/logs/replay_with_extra.jsonl --out-dir data/analysis/extra_run
```

The new model appears as an extra column/row. Skips still leave the system in the table.

## Option C — change the OpenAI model string

```env
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
```

Leave the key blank to keep the GPT row as a recorded skip.

## Optional detector re-check

After a new replay that includes Ubuntu ground truth replies, rebuild detector rows with `scripts/06_train_detector.py` (or reuse `data/analysis/detector/colab_bundle/` for the Colab notebook). That step is optional and separate from the four-system dissertation freeze.

## Honest reuse note

Your dissertation numbers are for the frozen Magazov/Ubuntu runs with the default four systems. Anyone who plugs in a new model should treat their results as a **new comparison run**, not as a replacement for the frozen tables, unless they re-run the full protocol and report settings.
