# Comparison tables

All four systems stay in the table. A skip is a missing run, not a removed system.

| System | Status | Logged | OK replies | Skipped | Mean delay (s) | Delay 95% CI | Mean commands completed | Fidelity | Consistency | Invented content | Cost USD | Technique labels |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cowrie | ok | 200 | 200 | 0 | 0.2556 | [0.2393, 0.2727] | 10.0000 | 0.0000 | 0.1429 | 1.0000 | 0.0000 | 1 |
| gpt-4o-mini | skipped | 200 | 0 | 200 |  |  |  |  |  |  |  | 1 |
| llama-3.1-8b | ok | 200 | 106 | 0 | 46.7786 | [40.3256, 52.8875] | 0.0500 | 0.3208 | 0.6000 | 0.6415 | 0.0000 | 1 |
| qwen-2.5-7b | ok | 200 | 121 | 0 | 41.3196 | [36.0640, 46.7384] | 0.0000 | 0.3967 | 0.2000 | 0.5702 | 0.0000 | 1 |

## Wilcoxon signed-rank

- cowrie vs gpt-4o-mini on commands_completed: n=0, statistic=None, p=None. Fewer than 5 paired sessions. Wilcoxon waits for a larger shared run.
- cowrie vs llama-3.1-8b on commands_completed: n=20, statistic=0.0, p=1.1933310815418253e-05.
- cowrie vs qwen-2.5-7b on commands_completed: n=20, statistic=0.0, p=7.74421643104407e-06.

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
