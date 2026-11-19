# Reply-source detector results

Source truth: `C:/Users/devyani patil/honeypot/data/test_set/ground_truth.jsonl`
Source honeypot log: `C:/Users/devyani patil/honeypot/data/logs/replay_ubuntu_testset_runs1.jsonl`
Join-only with nonempty Ubuntu stdout: **True**
Magazov mixed in: **False**
Text normalization: ANSI/prompt strip + whitespace cleanup
Split: GroupShuffleSplit by `session_id` (~70/15/15), seed=25

## Class counts (full set before split)

### binary

| label | n |
| --- | --- |
| honeypot | 340 |
| real_ubuntu | 160 |

### 3way

| label | n |
| --- | --- |
| cowrie | 160 |
| llm | 180 |
| ubuntu | 160 |

### ubuntu_vs_llm

| label | n |
| --- | --- |
| llm | 180 |
| real_ubuntu | 160 |

### ubuntu_vs_cowrie

| label | n |
| --- | --- |
| cowrie | 160 |
| real_ubuntu | 160 |

## Test-set metrics

| task | n_test | accuracy | macro-F1 | macro-F1 95% boot CI | AUROC |
| --- | --- | --- | --- | --- | --- |
| binary | 62 | 0.758 | 0.750 | 0.626–0.853 | 0.875 |
| 3way | 62 | 0.694 | 0.682 | 0.555–0.793 | 0.888 |
| ubuntu_vs_llm | 37 | 0.811 | 0.802 | 0.644–0.935 | 0.927 |
| ubuntu_vs_cowrie | 50 | 0.800 | 0.797 | 0.672–0.899 | 0.899 |

AUROC: binary = honeypot-positive; 3-way = OvR macro.

### Per-class F1 — binary (test)

| class | F1 | support |
| --- | --- | --- |
| real_ubuntu | 0.706 | 25 |
| honeypot | 0.795 | 37 |

Confusion matrix (rows=true, cols=pred):

| true\pred | real_ubuntu | honeypot |
| --- | --- | --- |
| real_ubuntu | 18 | 7 |
| honeypot | 8 | 29 |

### Per-class F1 — 3way (test)

| class | F1 | support |
| --- | --- | --- |
| ubuntu | 0.708 | 25 |
| cowrie | 0.739 | 25 |
| llm | 0.600 | 12 |

Confusion matrix (rows=true, cols=pred):

| true\pred | ubuntu | cowrie | llm |
| --- | --- | --- | --- |
| ubuntu | 17 | 2 | 6 |
| cowrie | 5 | 17 | 3 |
| llm | 1 | 2 | 9 |

### Per-class F1 — ubuntu_vs_llm (test)

| class | F1 | support |
| --- | --- | --- |
| real_ubuntu | 0.844 | 25 |
| llm | 0.759 | 12 |

Confusion matrix (rows=true, cols=pred):

| true\pred | real_ubuntu | llm |
| --- | --- | --- |
| real_ubuntu | 19 | 6 |
| llm | 1 | 11 |

### Per-class F1 — ubuntu_vs_cowrie (test)

| class | F1 | support |
| --- | --- | --- |
| real_ubuntu | 0.821 | 25 |
| cowrie | 0.773 | 25 |

Confusion matrix (rows=true, cols=pred):

| true\pred | real_ubuntu | cowrie |
| --- | --- | --- |
| real_ubuntu | 23 | 2 |
| cowrie | 8 | 17 |

## Interpretation notes (auto)

- 3-way test F1: ubuntu=0.708, cowrie=0.739, llm=0.600.
- Cowrie is **easier to spot** than pooled LLM replies (higher Cowrie F1 / clearer separation).
- True ubuntu predicted as: ubuntu=17, cowrie=2, llm=6
- Confusions into ubuntu: llm→ubuntu=1, cowrie→ubuntu=5.
- Honest reading: Cowrie is confused with real Ubuntu more often than LLMs in the test fold.
- Binary honeypot-vs-ubuntu test: accuracy=0.758, macro-F1=0.750, AUROC=0.875.

Caveat: group split by session leaves few sessions in val/test; treat absolute numbers as exploratory, not a large-scale claim.
