# Report outline — Patil Devyani Anil (5034)

**Module:** 7FTC2001 · MSc Data Science (FT)  
**Title:** Generative AI Deception: Dynamic LLM-Powered Honeypots  
**Supervisor:** Dr Rama Abirami K.  
**Writing window:** 16–19 November 2026 · **Freeze:** 14 November 2026 · **Due:** 20 November 2026 · **Viva:** 23 November 2026

Use this outline to draft the report after tables are frozen. Keep the study design as the four-system comparison (Cowrie, GPT-4o mini, Llama 3.1 8B, Qwen 2.5 7B) even when a row is a skip.

---

## 1. Front matter

- Title, student name/ID, module, supervisor, word count, date
- Abstract (150–200 words): aim, four systems, Magazov sessions, four RQs, main finding in one sentence, containment note
- Keywords: honeypot, LLM, Cowrie, session survival, containment

---

## 2. Introduction (≈1–1.5 pages)

- Problem: attackers probe SSH; defenders need realistic decoys without exposing the host
- Gap: few repeatable multi-step comparisons of Cowrie vs several LLMs on the same sessions
- Aim and novelty (stateful replay, four-way design, session survival, local vs API, RQ4 as containment audit)
- Contributions C1–C4 (map briefly to later sections)
- Scope: closed lab, `127.0.0.1` only — not a live deployment

---

## 3. Related work (≈1–1.5 pages)

- Traditional honeypots (Cowrie lineage)
- LLM / generative honeypots and deception
- Evaluation practice: single-command tests, small human studies, field deployments that cannot be rerun
- Position this work: identical Magazov-derived sessions, multi-step breaks, bootstrap CIs + Wilcoxon, local models vs paid API

---

## 4. Research questions (map every later result here)

| RQ | Question | Objective | Primary evidence in report |
| --- | --- | --- | --- |
| **RQ1** | How realistic and consistent are LLM honeypot replies vs real Linux output? | Fidelity and multi-step consistency on ~200 commands / 20 sessions | Fidelity %, consistency %, invented-content rate; ground-truth note if capture missing |
| **RQ2** | How do the three LLMs compare on response time and cost? | Delay per command; cost per session | Mean delay + 95% bootstrap CI; cost USD (GPT only if rates set); local models = £0 API |
| **RQ3** | How far do scripted sessions get before each system breaks, and which techniques are seen? | Commands completed until first break; technique labels vs Cowrie | Mean commands completed + CI; break reasons; technique-label counts |
| **RQ4** | How well does each LLM honeypot resist prompt injection? | Containment audit + low-cost design recommendation | Pass/fail checklist (local bind, no host exec, text-only, no tools); **not** a stored injection corpus |

Break definition (state once, reuse): empty reply, wrong/contradictory reply, AI self-disclosure, or delay > 5 s.

---

## 5. Methods (write so a marker could rerun)

### 5.1 Systems under test

| System | Role | Access |
| --- | --- | --- |
| Cowrie | Scripted baseline | SSH on `127.0.0.1:2222` |
| GPT-4o mini | Commercial API | Text-only OpenAI call; skip if no key |
| Llama 3.1 8B | Local Ollama | `127.0.0.1`; timeouts possible on CPU |
| Qwen 2.5 7B | Local Ollama | `127.0.0.1`; timeouts possible on CPU |

Fixed denials for safety-critical categories (e.g. sudo / password-file reads) before LLM call. Session memory: cwd, file/user deltas — no host shell, no tools.

### 5.2 Data

- Magazov et al. (2026) de-identified corpus (CC BY 4.0) → screened sessions
- Study design: 20 sessions, ~70 commands in the Magazov replay slice used here; 5 runs per system (plan)
- Ground truth: Ubuntu container capture when present (`data/test_set/ground_truth.jsonl`); fidelity blank until available
- Logs: JSONL via `scripts/04_replay.py` → analyse with `scripts/05_analyse.py`

### 5.3 Procedure

1. Containment pre-check (must pass before study claims)
2. Replay same session list to all four systems (`--source magazov --max-sessions 20 --runs 5`)
3. Record command, reply, delay, tokens, system, settings, run number, break/skip reasons
4. Score RQ1–RQ3; run RQ4 audit
5. Freeze tables **14 November 2026**

### 5.4 Metrics and stats

- Bootstrap 95% CIs (1000 resamples, fixed seed in code)
- Wilcoxon signed-rank on paired session `commands_completed` (Cowrie vs each LLM); needs scipy + ≥5 pairs
- Temperature / history window: report the frozen settings from the run header (e.g. temperature 0.0, history_window 10)

### 5.5 Ethics and safety

- Localhost-only bind; no public honeypot
- No injection strings stored in repo
- Skips remain rows in tables (system not dropped from design)

---

## 6. Expected / planned tables and figures

Paste frozen outputs from `results/` (or `data/analysis/...`) after 14 Nov. Draft captions now:

| ID | Content | Feeds |
| --- | --- | --- |
| **Table 1** | System × status, logged, OK, skipped, mean delay, delay CI, mean commands completed, fidelity, consistency, invented, cost, technique labels | RQ1–RQ3 |
| **Table 2** | Wilcoxon: Cowrie vs each LLM on commands_completed (n, statistic, p, note) | RQ3 |
| **Table 3** | RQ4 containment checklist (name, pass/fail, detail) | RQ4 |
| **Table 4** (optional) | Break-reason counts by system | RQ3 |
| **Table 5** (optional) | Skip/error reasons (GPT key missing, Ollama TimeoutError, …) | Limitations / RQ2 |
| **Figure 1** | Mean commands completed (± CI) by system | RQ3 |
| **Figure 2** | Mean delay by system (log scale if locals are slow) | RQ2 |
| **Figure 3** | Session survival / step-at-first-break sketch | RQ3 |

Interim dry-run (not freeze): `data/analysis/runs1_with_cowrie/` from `replay_magazov_20sess_runs1_with_cowrie.jsonl` — one run only; GPT skipped; locals often timeout.

---

## 7. Results (structure by RQ)

### 7.1 RQ1 — Realism and consistency

- Report fidelity / invented content **or** explicitly: ground truth not yet joined → qualitative reply examples + consistency when `--runs 5` complete
- Consistency needs ≥2 runs with OK replies for the same (run, session, command) groups — emphasise after runs5

### 7.2 RQ2 — Time and cost

- Cowrie: sub-second delays (baseline)
- Local LLMs: high delay; many `TimeoutError` / `delay_over_5s` breaks on this machine
- GPT-4o mini: skipped without `OPENAI_API_KEY` — row kept; cost blank unless rates env vars set

### 7.3 RQ3 — Session survival and techniques

- Commands completed until break vs Cowrie
- Technique labels observed (defender-visible)
- Wilcoxon once scipy available and pairs ≥5

### 7.4 RQ4 — Containment

- Audit passed/failed items verbatim from `rq4_containment.json`
- Design recommendation: text-only local or API model + session memory + fixed denials + localhost Cowrie front end; no host execution

### 7.5 Cross-cutting

- Four-system completeness statement (`study_complete` flag)
- Any partial runs (e.g. runs5 still in progress before freeze)

---

## 8. Discussion

- Trade-off: realism/engagement (LLMs) vs speed/stability (Cowrie) vs cost/privacy (local vs GPT)
- Why timeouts and GPT skip do **not** remove those systems from the design
- Threats to validity: single machine, Magazov slice size, missing ground truth, temperature fixed, Ollama load
- Implications for low-cost honeypot design

---

## 9. Limitations (must include)

| Limitation | Effect on claims | Mitigation / wording |
| --- | --- | --- |
| Local model **timeouts** / delay > 5 s | Understates LLM session survival; inflates breaks | Report error/skip counts; discuss hardware |
| **GPT-4o mini skip** (no API key) | No commercial delay/cost numbers in that log | Keep skipped row; optional late key run before freeze only |
| **Ground truth** missing | RQ1 fidelity empty | State clearly; use qualitative examples |
| **scipy** missing | Wilcoxon note only | Install before freeze analysis if allowed |
| Single lab PC / Ollama contention | External validity | Do not claim production scale |
| `--runs 1` interim vs planned **5 runs** | Consistency / CIs weaker until runs5 finishes | Freeze only on completed `--runs 5` log |
| RQ4 = containment audit | Not an injection-string benchmark | Align wording with plan / 2026 untested note |

---

## 10. Conclusion

- Answer RQ1–RQ4 in four short sentences
- Restate contributions
- One sentence future work (ground-truth capture, GPU locals, keyed GPT run)

---

## 11. References (seed list — expand while writing)

- Magazov et al. (2026) Zenodo corpus DOI: https://doi.org/10.5281/zenodo.20816078  
- Cowrie project / honeypot literature (add finals while drafting)  
- Module / assessment brief citations as required by UH style  

---

## 12. Appendices (optional)

- A: Run header JSON (systems, runs, session_ids, model_settings, containment_pass)
- B: Full `tables.md` / `summary.json` snapshot at freeze
- C: Cowrie localhost config note (`listen_endpoints`, not public bind)
- D: Ethics / containment checklist

---

## Viva talking points (21–22 Nov practice)

1. **One-minute pitch:** closed-lab four-way replay of the same Magazov sessions; measure realism, speed/cost, how far sessions get, and containment — not a public honeypot.
2. **Why Cowrie stays:** scripted baseline for paired Wilcoxon and technique labels.
3. **Break definition:** empty / wrong / self-disclosure / >5 s — defend the 5 s engagement proxy.
4. **Why skips stay in the table:** missing key or timeout is a result for that organisation, not a reason to drop the system from the study design.
5. **RQ4 clarification:** containment audit (localhost, text-only, no tools, no host exec); injection prompts are intentionally not stored.
6. **Novelty under pressure:** “LLM honeypots exist; the novelty is the repeatable multi-step four-system measurement.”
7. **Honest limitations:** timeouts on local 7–8B models; GPT skip without key; fidelity waits on Ubuntu ground truth.
8. **Reproduce path:** `04_replay.py` → JSONL → `05_analyse.py` → tables + RQ4 JSON; freeze 14 Nov.
9. **Ethics:** everything on `127.0.0.1`; Magazov CC BY; no live attacker traffic in this project.
10. **Design recommendation:** for low cost / no data egress → local Ollama + session memory, accepting slower replies; for speed → Cowrie; hybrid front end possible.

---

## Writing checklist (16–19 Nov)

- [ ] Freeze log path named in Methods (final `--runs 5` Magazov file)
- [ ] Paste Table 1–3 from analysis outputs; caption + RQ mapping
- [ ] Explicit paragraph on timeouts and GPT skip
- [ ] RQ4 wording matches “containment audit”
- [ ] Abstract last; viva sheet from section 12 above
- [ ] No secrets / `.env` / injection strings in appendix
