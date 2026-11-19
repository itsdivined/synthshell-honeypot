# Comparison tables

All four systems stay in the table. A skip is a missing run, not a removed system.

| System | Status | Logged | OK replies | Skipped | Mean delay (s) | Delay 95% CI | Mean commands completed | Fidelity | Consistency | Invented content | Cost USD | Technique labels |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cowrie | ok | 350 | 350 | 0 | 0.3666 | [0.3357, 0.3968] | 3.5000 |  |  |  | 0.0000 | 8 |
| gpt-4o-mini | skipped | 350 | 0 | 350 |  |  |  |  |  |  |  | 8 |
| llama-3.1-8b | ok | 350 | 86 | 0 | 51.5045 | [42.4896, 60.4352] | 0.2000 |  |  |  | 0.0000 | 8 |
| qwen-2.5-7b | ok | 350 | 153 | 0 | 50.3696 | [44.9417, 55.6815] | 0.1700 |  |  |  | 0.0000 | 8 |

## Wilcoxon signed-rank

- cowrie vs gpt-4o-mini on commands_completed: n=0, statistic=None, p=None. Fewer than 5 paired sessions. Wilcoxon waits for a larger shared run.
- cowrie vs llama-3.1-8b on commands_completed: n=100, statistic=0.0, p=1.1383212734538795e-16.
- cowrie vs qwen-2.5-7b on commands_completed: n=100, statistic=0.0, p=1.7961765809351272e-16.

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
