"""Train a simple TF-IDF + logistic regression reply-source detector.

Labels (Ubuntu-aligned primary set):
  - binary: real_ubuntu vs honeypot (cowrie + llama + qwen pooled)
  - 3-way:  ubuntu / cowrie / llm (llama + qwen pooled)

Uses only reply text already logged. No Magazov mixing by default (cleaner story).
Group-aware split by session_id to reduce leakage across steps of the same session.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_TRUTH = ROOT / "data" / "test_set" / "ground_truth.jsonl"
DEFAULT_UBUNTU_LOG = ROOT / "data" / "logs" / "replay_ubuntu_testset_runs1.jsonl"
DEFAULT_OUT = ROOT / "data" / "analysis" / "detector"

ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b\].*?\x07|\x1b.")
PROMPT_RE = re.compile(r"(?:^|\n)[\w.-]+@[\w.-]+:[^\n]*[$#]\s*$")


def normalize_text(text: str) -> str:
    """Light cleanup so Cowrie ANSI/prompt chrome is not a free giveaway."""
    if not text:
        return ""
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    t = ANSI_RE.sub("", t)
    t = t.replace("\x00", "")
    t = PROMPT_RE.sub("", t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _step_key(session_id: str, step) -> tuple[str, int]:
    return session_id, int(step)


def load_ubuntu_rows(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            o = json.loads(line)
            stdout = (o.get("stdout") or "").strip()
            if not stdout:
                continue
            text = normalize_text(o.get("stdout") or "")
            if not text:
                continue
            rows.append(
                {
                    "text": text,
                    "raw_len": len(o.get("stdout") or ""),
                    "session_id": o["session_id"],
                    "step": int(o["step"]),
                    "source_system": "real_ubuntu",
                    "label_binary": "real_ubuntu",
                    "label_3way": "ubuntu",
                    "label_4way": "ubuntu",
                    "join_key": _step_key(o["session_id"], o["step"]),
                }
            )
    return rows


def load_honeypot_rows(
    path: Path,
    systems: set[str],
    join_keys: set[tuple[str, int]] | None,
    join_only: bool,
) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            o = json.loads(line)
            if o.get("record_type") not in (None, "command"):
                continue
            system = o.get("system")
            if system not in systems:
                continue
            if o.get("status") != "ok":
                continue
            reply = o.get("reply") or ""
            if not reply.strip():
                continue
            key = _step_key(o["session_id"], o["step"])
            if join_only and join_keys is not None and key not in join_keys:
                continue
            text = normalize_text(reply)
            if not text:
                continue
            if system == "cowrie":
                lab3, lab4 = "cowrie", "cowrie"
            else:
                lab3, lab4 = "llm", system
            rows.append(
                {
                    "text": text,
                    "raw_len": len(reply),
                    "session_id": o["session_id"],
                    "step": int(o["step"]),
                    "source_system": system,
                    "label_binary": "honeypot",
                    "label_3way": lab3,
                    "label_4way": lab4,
                    "join_key": key,
                }
            )
    return rows


def group_split(
    texts: list[str],
    labels: list[str],
    groups: list[str],
    seed: int,
    test_size: float = 0.15,
    val_size: float = 0.15,
):
    """70/15/15-ish split with disjoint session_id groups."""
    X = np.array(texts)
    y = np.array(labels)
    g = np.array(groups)

    gss_test = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    train_val_idx, test_idx = next(gss_test.split(X, y, g))
    X_tv, y_tv, g_tv = X[train_val_idx], y[train_val_idx], g[train_val_idx]
    # val fraction of remaining ≈ val_size / (1 - test_size)
    val_frac = val_size / (1.0 - test_size)
    gss_val = GroupShuffleSplit(n_splits=1, test_size=val_frac, random_state=seed + 1)
    train_idx_rel, val_idx_rel = next(gss_val.split(X_tv, y_tv, g_tv))

    return {
        "X_train": X_tv[train_idx_rel],
        "y_train": y_tv[train_idx_rel],
        "X_val": X_tv[val_idx_rel],
        "y_val": y_tv[val_idx_rel],
        "X_test": X[test_idx],
        "y_test": y[test_idx],
        "n_train": int(len(train_idx_rel)),
        "n_val": int(len(val_idx_rel)),
        "n_test": int(len(test_idx)),
        "sessions_train": sorted(set(g_tv[train_idx_rel].tolist())),
        "sessions_val": sorted(set(g_tv[val_idx_rel].tolist())),
        "sessions_test": sorted(set(g[test_idx].tolist())),
    }


def make_pipeline(seed: int) -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(3, 5),
                    min_df=2,
                    max_features=20000,
                    lowercase=True,
                    strip_accents="unicode",
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=seed,
                    solver="lbfgs",
                ),
            ),
        ]
    )


def bootstrap_macro_f1(
    y_true: np.ndarray, y_pred: np.ndarray, n: int = 500, seed: int = 25
) -> dict:
    rng = np.random.default_rng(seed)
    scores = []
    idx = np.arange(len(y_true))
    for _ in range(n):
        sample = rng.choice(idx, size=len(idx), replace=True)
        scores.append(f1_score(y_true[sample], y_pred[sample], average="macro", zero_division=0))
    scores.sort()
    lo = scores[int(0.025 * (n - 1))]
    hi = scores[int(0.975 * (n - 1))]
    return {
        "mean": float(np.mean(scores)),
        "low": float(lo),
        "high": float(hi),
        "n_resamples": n,
    }


def evaluate_split(
    pipe: Pipeline,
    X: np.ndarray,
    y: np.ndarray,
    label_names: list[str],
    binary: bool,
) -> dict:
    pred = pipe.predict(X)
    proba = pipe.predict_proba(X)
    classes = list(pipe.named_steps["clf"].classes_)
    report = classification_report(
        y, pred, labels=label_names, output_dict=True, zero_division=0
    )
    cm = confusion_matrix(y, pred, labels=label_names).tolist()
    out: dict = {
        "n": int(len(y)),
        "accuracy": float(accuracy_score(y, pred)),
        "macro_f1": float(f1_score(y, pred, average="macro", zero_division=0)),
        "per_class_f1": {
            lab: float(report[lab]["f1-score"]) for lab in label_names if lab in report
        },
        "per_class_support": {
            lab: int(report[lab]["support"]) for lab in label_names if lab in report
        },
        "confusion_matrix": {"labels": label_names, "matrix": cm},
        "classification_report": report,
        "bootstrap_macro_f1": bootstrap_macro_f1(y, pred),
    }
    if binary and set(classes) <= set(label_names) and len(classes) == 2:
        # Prefer non-Ubuntu as the positive (detectable) class when present.
        preferred = ("honeypot", "llm", "cowrie")
        pos = next((p for p in preferred if p in classes), classes[1])
        pos_idx = classes.index(pos)
        out["auroc"] = float(roc_auc_score((y == pos).astype(int), proba[:, pos_idx]))
        out["positive_class"] = pos
    elif not binary and len(classes) >= 3:
        # One-vs-rest AUROC (macro), only classes present in y
        try:
            out["auroc_ovr_macro"] = float(
                roc_auc_score(y, proba, multi_class="ovr", average="macro", labels=classes)
            )
        except ValueError:
            out["auroc_ovr_macro"] = None
    return out


def top_features(pipe: Pipeline, label_names: list[str], k: int = 15) -> dict:
    vec: TfidfVectorizer = pipe.named_steps["tfidf"]
    clf: LogisticRegression = pipe.named_steps["clf"]
    feats = np.array(vec.get_feature_names_out())
    out: dict = {}
    if clf.coef_.shape[0] == 1 and len(label_names) == 2:
        # liblinear binary: coef for classes_[1]
        pos = clf.classes_[1]
        neg = clf.classes_[0]
        coef = clf.coef_[0]
        order = np.argsort(coef)
        out[pos] = feats[order[::-1][:k]].tolist()
        out[neg] = feats[order[:k]].tolist()
    else:
        for i, lab in enumerate(clf.classes_):
            coef = clf.coef_[i]
            order = np.argsort(coef)
            out[lab] = feats[order[::-1][:k]].tolist()
    return out


def save_confusion_png(cm: list[list[int]], labels: list[str], path: Path, title: str) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    arr = np.array(cm)
    fig, ax = plt.subplots(figsize=(5.2, 4.4))
    im = ax.imshow(arr, cmap="Blues")
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_yticklabels(labels)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(title)
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            ax.text(j, i, str(arr[i, j]), ha="center", va="center", color="black", fontsize=10)
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for r in rows:
        lines.append("| " + " | ".join(r) + " |")
    return "\n".join(lines)


def run_task(
    name: str,
    rows: list[dict],
    label_key: str,
    label_names: list[str],
    seed: int,
    out_dir: Path,
) -> dict:
    texts = [r["text"] for r in rows]
    labels = [r[label_key] for r in rows]
    groups = [r["session_id"] for r in rows]
    counts = dict(Counter(labels))
    split = group_split(texts, labels, groups, seed=seed)

    pipe = make_pipeline(seed)
    pipe.fit(split["X_train"], split["y_train"])

    binary = len(label_names) == 2
    val_metrics = evaluate_split(pipe, split["X_val"], split["y_val"], label_names, binary)
    test_metrics = evaluate_split(pipe, split["X_test"], split["y_test"], label_names, binary)
    train_acc = float(accuracy_score(split["y_train"], pipe.predict(split["X_train"])))

    result = {
        "task": name,
        "label_key": label_key,
        "label_names": label_names,
        "class_counts_all": counts,
        "split": {
            "n_train": split["n_train"],
            "n_val": split["n_val"],
            "n_test": split["n_test"],
            "sessions_train": split["sessions_train"],
            "sessions_val": split["sessions_val"],
            "sessions_test": split["sessions_test"],
            "train_label_counts": dict(Counter(split["y_train"].tolist())),
            "val_label_counts": dict(Counter(split["y_val"].tolist())),
            "test_label_counts": dict(Counter(split["y_test"].tolist())),
        },
        "train_accuracy": train_acc,
        "val": val_metrics,
        "test": test_metrics,
        "top_char_ngrams": top_features(pipe, label_names),
        "vectorizer": {
            "analyzer": "char_wb",
            "ngram_range": [3, 5],
            "max_features": 20000,
            "min_df": 2,
        },
        "classifier": "LogisticRegression(class_weight=balanced, solver=lbfgs)",
    }

    save_confusion_png(
        test_metrics["confusion_matrix"]["matrix"],
        label_names,
        out_dir / f"confusion_{name}_test.png",
        f"{name} — test confusion",
    )
    return result


def build_tables_md(meta: dict, results: list[dict]) -> str:
    lines = [
        "# Reply-source detector results",
        "",
        f"Source truth: `{meta['truth']}`",
        f"Source honeypot log: `{meta['ubuntu_log']}`",
        f"Join-only with nonempty Ubuntu stdout: **{meta['join_only']}**",
        f"Magazov mixed in: **{meta['include_magazov']}**",
        f"Text normalization: ANSI/prompt strip + whitespace cleanup",
        f"Split: GroupShuffleSplit by `session_id` (~70/15/15), seed={meta['seed']}",
        "",
        "## Class counts (full set before split)",
        "",
    ]
    for r in results:
        lines.append(f"### {r['task']}")
        lines.append("")
        rows = [[k, str(v)] for k, v in sorted(r["class_counts_all"].items())]
        lines.append(md_table(["label", "n"], rows))
        lines.append("")

    lines.append("## Test-set metrics")
    lines.append("")
    metric_rows = []
    for r in results:
        t = r["test"]
        auroc = t.get("auroc", t.get("auroc_ovr_macro"))
        auroc_s = f"{auroc:.3f}" if isinstance(auroc, float) else "n/a"
        ci = t["bootstrap_macro_f1"]
        metric_rows.append(
            [
                r["task"],
                str(t["n"]),
                f"{t['accuracy']:.3f}",
                f"{t['macro_f1']:.3f}",
                f"{ci['low']:.3f}–{ci['high']:.3f}",
                auroc_s,
            ]
        )
    lines.append(
        md_table(
            ["task", "n_test", "accuracy", "macro-F1", "macro-F1 95% boot CI", "AUROC"],
            metric_rows,
        )
    )
    lines.append("")
    lines.append("AUROC: binary = honeypot-positive; 3-way = OvR macro.")
    lines.append("")

    for r in results:
        t = r["test"]
        lines.append(f"### Per-class F1 — {r['task']} (test)")
        lines.append("")
        rows = [
            [lab, f"{t['per_class_f1'][lab]:.3f}", str(t["per_class_support"][lab])]
            for lab in r["label_names"]
        ]
        lines.append(md_table(["class", "F1", "support"], rows))
        lines.append("")
        lines.append("Confusion matrix (rows=true, cols=pred):")
        lines.append("")
        labels = t["confusion_matrix"]["labels"]
        cm = t["confusion_matrix"]["matrix"]
        header = ["true\\pred"] + labels
        cm_rows = [[labels[i]] + [str(x) for x in cm[i]] for i in range(len(labels))]
        lines.append(md_table(header, cm_rows))
        lines.append("")

    # Interpretation helpers
    bin_r = next((x for x in results if x["task"] == "binary"), None)
    three = next((x for x in results if x["task"] == "3way"), None)
    lines.append("## Interpretation notes (auto)")
    lines.append("")
    if three:
        f1 = three["test"]["per_class_f1"]
        cow = f1.get("cowrie", 0.0)
        llm = f1.get("llm", 0.0)
        ubu = f1.get("ubuntu", 0.0)
        lines.append(
            f"- 3-way test F1: ubuntu={ubu:.3f}, cowrie={cow:.3f}, llm={llm:.3f}."
        )
        if cow > llm + 0.05:
            lines.append(
                "- Cowrie is **easier to spot** than pooled LLM replies (higher Cowrie F1 / clearer separation)."
            )
        elif llm > cow + 0.05:
            lines.append(
                "- Pooled LLM replies are **easier to spot** than Cowrie in this feature space."
            )
        else:
            lines.append(
                "- Cowrie and LLM F1 are close; neither is clearly much harder under TF-IDF+LR."
            )
        cm = three["test"]["confusion_matrix"]
        labs = cm["labels"]
        mat = cm["matrix"]
        if "ubuntu" in labs and "llm" in labs and "cowrie" in labs:
            ui, li, ci = labs.index("ubuntu"), labs.index("llm"), labs.index("cowrie")
            # How often true ubuntu predicted as llm vs cowrie
            ub_row = mat[ui]
            lines.append(
                f"- True ubuntu predicted as: "
                + ", ".join(f"{labs[j]}={ub_row[j]}" for j in range(len(labs)))
            )
            llm_as_ub = mat[li][ui]
            cow_as_ub = mat[ci][ui]
            lines.append(
                f"- Confusions into ubuntu: llm→ubuntu={llm_as_ub}, cowrie→ubuntu={cow_as_ub}."
            )
            if llm_as_ub > cow_as_ub:
                lines.append(
                    "- Honest reading: LLM replies are confused with real Ubuntu more often than Cowrie is — LLMs look more Ubuntu-like under this detector."
                )
            elif cow_as_ub > llm_as_ub:
                lines.append(
                    "- Honest reading: Cowrie is confused with real Ubuntu more often than LLMs in the test fold."
                )
    if bin_r:
        t = bin_r["test"]
        lines.append(
            f"- Binary honeypot-vs-ubuntu test: accuracy={t['accuracy']:.3f}, "
            f"macro-F1={t['macro_f1']:.3f}, AUROC={t.get('auroc', float('nan')):.3f}."
        )
    lines.append("")
    lines.append(
        "Caveat: group split by session leaves few sessions in val/test; treat absolute numbers as exploratory, not a large-scale claim."
    )
    lines.append("")
    return "\n".join(lines)


def write_readme(out_dir: Path, meta: dict, results: list[dict]) -> None:
    bin_r = next(x for x in results if x["task"] == "binary")
    three = next(x for x in results if x["task"] == "3way")
    text = f"""# Reply-source detector

Trains a lightweight **TF-IDF (char_wb 3–5) + LogisticRegression** classifier on already-logged shell reply text.

## Labels

| Scheme | Classes | Meaning |
| --- | --- | --- |
| binary | `real_ubuntu`, `honeypot` | Ubuntu ground-truth stdout vs Cowrie+LLM replies pooled |
| 3-way | `ubuntu`, `cowrie`, `llm` | Llama 3.1 8B + Qwen 2.5 7B pooled as `llm` |

4-way (separate llama/qwen) was **not** used as the primary report task: per-model OK counts on the Ubuntu replay are uneven and the cleaner story is Ubuntu vs Cowrie vs LLM-as-a-class.

## Data

- Real Ubuntu: `{meta['truth']}` nonempty `stdout`
- Honeypot: `{meta['ubuntu_log']}` systems cowrie / llama-3.1-8b / qwen-2.5-7b with `status=ok` and nonempty `reply`
- Join-only mode: **{meta['join_only']}** (same `session_id`,`step` as nonempty Ubuntu stdout)
- Magazov mixed: **{meta['include_magazov']}** (kept off for a single command-distribution story)

Text is lightly normalized (ANSI / trailing shell-prompt chrome stripped) so Cowrie control sequences are not a free feature.

## How to rerun

From the repo root, with the project venv:

```bash
.venv\\Scripts\\python.exe -m pip install "scikit-learn>=1.4" "matplotlib>=3.8"
.venv\\Scripts\\python.exe scripts\\06_train_detector.py
```

Useful flags: `--join-only`, `--seed 25`, `--out-dir data/analysis/detector`.

## Main test numbers (seed={meta['seed']})

**Binary** — n_test={bin_r['test']['n']}: accuracy={bin_r['test']['accuracy']:.3f}, macro-F1={bin_r['test']['macro_f1']:.3f}, AUROC={bin_r['test'].get('auroc', float('nan')):.3f}

**3-way** — n_test={three['test']['n']}: accuracy={three['test']['accuracy']:.3f}, macro-F1={three['test']['macro_f1']:.3f}, OvR-AUROC={three['test'].get('auroc_ovr_macro') if three['test'].get('auroc_ovr_macro') is not None else 'n/a'}

Per-class F1 (3-way test): {', '.join(f"{k}={v:.3f}" for k,v in three['test']['per_class_f1'].items())}

Outputs: `metrics.json`, `tables.md`, `confusion_*_test.png`, this README.
"""
    (out_dir / "DETECTOR_README.md").write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Train TF-IDF+LR reply-source detector.")
    parser.add_argument("--truth", type=Path, default=DEFAULT_TRUTH)
    parser.add_argument("--ubuntu-log", type=Path, default=DEFAULT_UBUNTU_LOG)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--join-only",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Keep honeypot rows only when (session_id,step) has nonempty Ubuntu stdout (default: on).",
    )
    parser.add_argument(
        "--include-magazov",
        action="store_true",
        help="Also append Magazov runs5 cowrie/llama/qwen ok replies (off by default).",
    )
    parser.add_argument("--seed", type=int, default=25)
    args = parser.parse_args(argv)

    truth = args.truth if args.truth.is_absolute() else ROOT / args.truth
    ubuntu_log = args.ubuntu_log if args.ubuntu_log.is_absolute() else ROOT / args.ubuntu_log
    out_dir = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    ubuntu_rows = load_ubuntu_rows(truth)
    join_keys = {r["join_key"] for r in ubuntu_rows}
    hp_systems = {"cowrie", "llama-3.1-8b", "qwen-2.5-7b"}
    hp_rows = load_honeypot_rows(ubuntu_log, hp_systems, join_keys, join_only=args.join_only)

    if args.include_magazov:
        mag = ROOT / "data" / "logs" / "replay_magazov_20sess_runs5.jsonl"
        if mag.is_file():
            hp_rows.extend(
                load_honeypot_rows(mag, hp_systems, join_keys=None, join_only=False)
            )

    all_rows = ubuntu_rows + hp_rows
    by_src = Counter(r["source_system"] for r in all_rows)
    by_3 = Counter(r["label_3way"] for r in all_rows)
    print("Loaded source_system counts:", dict(by_src))
    print("Loaded 3-way counts:", dict(by_3))

    # Label choice: enough n for 3-way; skip 4-way as primary
    meta = {
        "truth": str(truth.as_posix()),
        "ubuntu_log": str(ubuntu_log.as_posix()),
        "join_only": bool(args.join_only),
        "include_magazov": bool(args.include_magazov),
        "seed": args.seed,
        "source_system_counts": dict(by_src),
        "label_choice": (
            "Primary report tasks are binary (ubuntu vs honeypot) and 3-way "
            "(ubuntu / cowrie / llm with llama+qwen pooled). "
            "4-way not primary: smaller per-LLM OK counts and weaker story."
        ),
        "n_total": len(all_rows),
    }

    results = [
        run_task(
            "binary",
            all_rows,
            "label_binary",
            ["real_ubuntu", "honeypot"],
            args.seed,
            out_dir,
        ),
        run_task(
            "3way",
            all_rows,
            "label_3way",
            ["ubuntu", "cowrie", "llm"],
            args.seed,
            out_dir,
        ),
    ]

    # Optional secondary: ubuntu vs llm only (exclude cowrie) for honest "are LLMs harder?"
    llm_only_rows = [r for r in all_rows if r["label_3way"] in ("ubuntu", "llm")]
    for r in llm_only_rows:
        r["label_ub_llm"] = "real_ubuntu" if r["label_3way"] == "ubuntu" else "llm"
    results.append(
        run_task(
            "ubuntu_vs_llm",
            llm_only_rows,
            "label_ub_llm",
            ["real_ubuntu", "llm"],
            args.seed,
            out_dir,
        )
    )

    cow_only_rows = [r for r in all_rows if r["label_3way"] in ("ubuntu", "cowrie")]
    for r in cow_only_rows:
        r["label_ub_cow"] = "real_ubuntu" if r["label_3way"] == "ubuntu" else "cowrie"
    results.append(
        run_task(
            "ubuntu_vs_cowrie",
            cow_only_rows,
            "label_ub_cow",
            ["real_ubuntu", "cowrie"],
            args.seed,
            out_dir,
        )
    )

    payload = {"meta": meta, "results": results}
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tables = build_tables_md(meta, results)
    (out_dir / "tables.md").write_text(tables, encoding="utf-8")
    write_readme(out_dir, meta, results)
    (out_dir / "SOURCE.txt").write_text(
        "\n".join(
            [
                f"Truth: {truth.resolve()}",
                f"Ubuntu replay log: {ubuntu_log.resolve()}",
                f"Script: scripts/06_train_detector.py",
                f"join_only={args.join_only} include_magazov={args.include_magazov} seed={args.seed}",
                f"n_total={len(all_rows)}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(tables)
    print(f"Wrote {metrics_path}")
    print(f"Wrote {out_dir / 'tables.md'}")
    print(f"Wrote {out_dir / 'DETECTOR_README.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
