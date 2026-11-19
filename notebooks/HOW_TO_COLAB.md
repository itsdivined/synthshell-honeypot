# How to run the detector notebook in Colab

1. Open https://colab.research.google.com → File → Upload notebook → choose `detector_colab.ipynb`.
2. Upload `detector_rows.csv`, `detector_rows.jsonl`, or `detector_colab_bundle.zip` from `data/analysis/detector/colab_bundle/` (or put the zip on Drive and set `USE_UPLOAD=False`).
3. Runtime → CPU is enough; run all cells top to bottom (no API keys).
4. Expect seed=25 test metrics ≈ binary 0.758 / 0.750 / 0.875 and 3-way 0.694 / 0.682 / 0.888 (acc / macro-F1 / AUROC).
5. Keep the full honeypot demo on your laptop — Colab only needs the text+label bundle.
