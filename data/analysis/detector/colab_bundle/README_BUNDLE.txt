Colab mini-bundle for TF-IDF + logistic regression reply-source detector.
Rows: already-normalized reply text + labels (join-only Ubuntu-aligned set).
n_rows=500
Columns: session_id, step, source_system, label_binary, label_3way, text, raw_len
label_binary: real_ubuntu | honeypot
label_3way: ubuntu | cowrie | llm (llama+qwen pooled)
No Magazov, no API keys. Seed used locally: 25.
