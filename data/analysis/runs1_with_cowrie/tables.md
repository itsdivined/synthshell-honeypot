# Comparison tables

All four systems stay in the table. A skip is a missing run, not a removed system.

| System | Status | Logged | OK replies | Skipped | Mean delay (s) | Delay 95% CI | Mean commands completed | Fidelity | Consistency | Invented content | Cost USD | Technique labels |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cowrie | ok | 70 | 70 | 0 | 0.3412 | [0.2972, 0.3935] | 3.5000 |  |  |  | 0.0000 | 8 |
| gpt-4o-mini | skipped | 70 | 0 | 70 |  |  |  |  |  |  |  | 8 |
| llama-3.1-8b | ok | 70 | 18 | 0 | 49.0438 | [31.1151, 66.9969] | 0.2000 |  |  |  | 0.0000 | 8 |
| qwen-2.5-7b | ok | 70 | 32 | 0 | 56.8908 | [43.7293, 70.0262] | 0.1500 |  |  |  | 0.0000 | 8 |

## Wilcoxon signed-rank

- cowrie vs gpt-4o-mini on commands_completed: n=0, statistic=None, p=None. Fewer than 5 paired sessions. Wilcoxon waits for a larger shared run.
- cowrie vs llama-3.1-8b on commands_completed: n=20, statistic=None, p=None. scipy is not installed. Run pip install -r requirements.txt.
- cowrie vs qwen-2.5-7b on commands_completed: n=20, statistic=None, p=None. scipy is not installed. Run pip install -r requirements.txt.

## RQ4 containment

Passed.
- local_bind: pass. listen host is 127.0.0.1
- cowrie_localhost: pass. Cowrie host is 127.0.0.1
- ollama_localhost: pass. Ollama host is 127.0.0.1
- openai_host_pinned: pass. GPT-4o mini text calls use api.openai.com only
- no_host_execution: pass. commands are not passed to the host operating system
- no_honeypot_outbound: pass. the honeypot has no outbound channel
- text_only_output: pass. model output type is text
- no_model_tools: pass. the model is not given a tool
- source_has_no_host_shell: pass. session and replay source has no host shell and no public bind

Containment audit only. Injection wording is not stored in this repository.

Study status: the four-system comparison is not complete in this log. Skipped systems remain part of the design.
