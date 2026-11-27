# Data note

The public corpus is Magazov, R., Abeshev, K., Shamuratov, Y., Uralova, F. and Aksholak, G. (2026) *De-identified SSH honeypot attacker corpus* [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.20816078

The plan uses this corpus, about 12,900 de-identified commands, to choose realistic session traffic and to check that later scripts resemble that traffic. The same saved sessions are replayed to Cowrie, GPT-4o mini, Llama 3.1 8B, and Qwen 2.5 7B.

Verified size, checksum, and row count are written by `python scripts/01_download.py` to `data/MANIFEST.txt`.

Licence, as stated by the authors:

- Data and results in the deposit: CC BY 4.0.
- Code and prompts inside the same zip: MIT.
- Zenodo record licence id: CC BY 4.0.

The authors state that public IPv4 addresses were replaced with RFC 5737 placeholders in `198.51.100.0/24`. `python scripts/02_screen.py` counts any remaining public addresses. It does not write command text. Username review of the tables is manual.

The zip stays at `data/raw/zenodo_deposit.zip` and is gitignored. Author code and prompts are not copied into this source tree.

## Other data, created later

| Data | Where it will live | Status |
| --- | --- | --- |
| About 200 ground-truth commands from a clean Ubuntu container | `data/test_set/ground_truth.jsonl` | Format only. Capture with `docker run --rm -it --network none ubuntu:24.04`. |
| About 20 sessions, with about 40 validation commands kept separate | `data/test_set/sessions.jsonl` | Format only. See `data/templates/`. |
| Experiment logs: command, reply, delay, token count, system, model settings, run number | `data/logs/replay.jsonl` | Gitignored. Produced by `scripts/04_replay.py`. |

A three-command pipeline check lives in `data/fixtures/pipeline_check.jsonl`. It is not the study set.
