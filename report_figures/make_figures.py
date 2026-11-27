"""Generate Final Report diagram PNGs with matplotlib (no GenAI image models)."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent


def _box(ax, xy, w, h, text, fc="#E8F1F8", ec="#1F4E79", fontsize=9, lw=1.5):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.02",
        facecolor=fc, edgecolor=ec, linewidth=lw,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2, y + h / 2, text, ha="center", va="center",
        fontsize=fontsize, color="#0D2137", fontfamily="sans-serif",
    )
    return patch


def _arrow(ax, start, end):
    ax.annotate(
        "", xy=end, xytext=start,
        arrowprops=dict(arrowstyle="-|>", color="#334155", lw=1.4),
    )


def fig_architecture():
    fig, ax = plt.subplots(figsize=(11, 7.2), dpi=160)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7.2)
    ax.axis("off")
    ax.set_title(
        "System architecture: four backends + localhost containment",
        fontsize=13, fontweight="bold", pad=12, color="#0D2137",
    )

    boundary = FancyBboxPatch(
        (0.35, 0.35), 10.3, 6.5, boxstyle="round,pad=0.02,rounding_size=0.05",
        facecolor="#F7FAFC", edgecolor="#B91C1C", linewidth=2.2, linestyle="--",
    )
    ax.add_patch(boundary)
    ax.text(
        0.55, 6.55,
        "Isolated lab containment (127.0.0.1 only — no public bind)",
        fontsize=9, color="#B91C1C", fontweight="bold",
    )

    _box(
        ax, (3.5, 5.55), 4.0, 0.7,
        "Saved sessions\n(Magazov slice / Ubuntu test set)",
        fc="#FEF3C7", ec="#B45309", fontsize=9,
    )
    _box(
        ax, (3.5, 4.35), 4.0, 0.7,
        "scripts/04_replay.py\nidentical session list → all four systems",
        fc="#DBEAFE", ec="#1D4ED8", fontsize=9,
    )
    _arrow(ax, (5.5, 5.55), (5.5, 5.05))

    systems = [
        (0.6, 2.85, "Cowrie\nscripted baseline\n127.0.0.1:2222", "#ECFDF5", "#047857"),
        (3.15, 2.85, "GPT-4o mini\nAPI text-only\napi.openai.com\n(skip if no key)", "#F3E8FF", "#6D28D9"),
        (5.7, 2.85, "Llama 3.1 8B\nOllama local\n127.0.0.1:11434", "#E0F2FE", "#0369A1"),
        (8.25, 2.85, "Qwen 2.5 7B\nOllama local\n127.0.0.1:11434", "#FFEDD5", "#C2410C"),
    ]
    for x, y, t, fc, ec in systems:
        _box(ax, (x, y), 2.15, 1.15, t, fc=fc, ec=ec, fontsize=8)
        _arrow(ax, (5.5, 4.35), (x + 1.05, 4.0))

    _box(
        ax, (1.2, 1.55), 8.6, 0.7,
        "Session memory (cwd / file / user deltas) — text-only — NO host OS execution — NO model tools",
        fc="#FEE2E2", ec="#991B1B", fontsize=8,
    )
    _box(
        ax, (2.0, 0.55), 7.0, 0.7,
        "JSONL logs → scripts/05_analyse.py → tables, CIs, Wilcoxon, RQ4 containment audit",
        fc="#E2E8F0", ec="#334155", fontsize=8,
    )
    for x, _, _, _, _ in systems:
        _arrow(ax, (x + 1.05, 2.85), (5.5, 2.25))
    _arrow(ax, (5.5, 1.55), (5.5, 1.25))

    fig.tight_layout()
    path = OUT / "fig1_architecture.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", path)


def fig_pipeline():
    fig, ax = plt.subplots(figsize=(11, 4.8), dpi=160)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.8)
    ax.axis("off")
    ax.set_title(
        "Method pipeline: download → screen → replay → analyse",
        fontsize=13, fontweight="bold", pad=10, color="#0D2137",
    )

    steps = [
        (0.3, "01_download.py\nMagazov Zenodo\nCC BY 4.0 corpus", "#FEF3C7", "#B45309"),
        (2.45, "02_screen.py\nIP counts only\nno payload store", "#E0E7FF", "#4338CA"),
        (4.6, "03_testset.py\nUbuntu GT check\n(~200 cmds)", "#FCE7F3", "#BE185D"),
        (6.75, "04_replay.py\n20 sessions × 5\nfour systems", "#DBEAFE", "#1D4ED8"),
        (8.9, "05_analyse.py\nmetrics + CIs\nRQ4 audit", "#D1FAE5", "#047857"),
    ]
    for x, text, fc, ec in steps:
        _box(ax, (x, 2.4), 1.9, 1.35, text, fc=fc, ec=ec, fontsize=8)
    for i in range(len(steps) - 1):
        x0 = steps[i][0] + 1.9
        x1 = steps[i + 1][0]
        _arrow(ax, (x0, 3.05), (x1, 3.05))

    _box(
        ax, (0.3, 0.55), 4.0, 1.2,
        "Study A — Magazov ×5\n20 sessions, 70 shared cmds\nengagement / delay / labels",
        fc="#F8FAFC", ec="#475569", fontsize=8,
    )
    _box(
        ax, (4.7, 0.55), 3.0, 1.2,
        "Study B — Ubuntu ×1\nGT present\nfidelity / consistency",
        fc="#F8FAFC", ec="#475569", fontsize=8,
    )
    _box(
        ax, (8.05, 0.55), 2.65, 1.2,
        "Detector — TF-IDF+LR\nbinary / 3-way\nexploratory ML",
        fc="#EEF2FF", ec="#4338CA", fontsize=8,
    )

    ax.annotate(
        "", xy=(6.2, 1.75), xytext=(7.7, 2.4),
        arrowprops=dict(arrowstyle="-|>", color="#334155", lw=1.2),
    )
    ax.annotate(
        "", xy=(9.3, 1.75), xytext=(9.85, 2.4),
        arrowprops=dict(arrowstyle="-|>", color="#334155", lw=1.2),
    )

    fig.tight_layout()
    path = OUT / "fig2_method_pipeline.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", path)


def fig_rq_map():
    fig, ax = plt.subplots(figsize=(10.5, 6.2), dpi=160)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 6.2)
    ax.axis("off")
    ax.set_title(
        "Research questions mapped to evidence (freeze tables)",
        fontsize=13, fontweight="bold", pad=10, color="#0D2137",
    )

    rows = [
        (
            "RQ1 Realism /\nconsistency",
            "Ubuntu GT fidelity\nCowrie 0.00 · Llama 0.32 · Qwen 0.40\n(+ Magazov session length contrast)",
            "#DBEAFE", "#1D4ED8",
        ),
        (
            "RQ2 Time / cost",
            "Mean delay + 95% CI\nCowrie ~0.37 s · Llama ~51.5 s\nQwen ~50.4 s · GPT skipped",
            "#FEF3C7", "#B45309",
        ),
        (
            "RQ3 Detectability\n(TF-IDF + LR)",
            "Binary F1 0.750 · AUROC 0.875\n3-way F1 0.682 · OvR-AUROC 0.888\nCowrie F1 0.739 · LLM F1 0.600",
            "#D1FAE5", "#047857",
        ),
        (
            "RQ4 Containment /\ninjection resistance",
            "Containment audit PASSED\nlocalhost · text-only · no tools\nno host execution",
            "#FCE7F3", "#BE185D",
        ),
    ]
    for i, (rq, evid, fc, ec) in enumerate(rows):
        y = 4.55 - i * 1.15
        _box(ax, (0.4, y), 3.2, 0.95, rq, fc=fc, ec=ec, fontsize=9)
        _box(ax, (4.2, y), 5.8, 0.95, evid, fc="#F8FAFC", ec=ec, fontsize=8)
        _arrow(ax, (3.6, y + 0.48), (4.2, y + 0.48))

    ax.text(
        0.4, 0.35,
        "Honest split: fidelity improvement is Ubuntu Study B; Magazov Study A shows Cowrie higher session length.",
        fontsize=8, color="#334155", style="italic",
    )

    fig.tight_layout()
    path = OUT / "fig3_rq_mapping.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", path)


def fig_magazov_session_length():
    """One concept: Magazov session length only."""
    fig, ax = plt.subplots(figsize=(8.5, 4.6), dpi=160)
    systems = ["Cowrie", "Llama 3.1 8B", "Qwen 2.5 7B", "GPT-4o mini"]
    means = [3.50, 0.20, 0.17, 0.0]
    colors = ["#047857", "#0369A1", "#C2410C", "#94A3B8"]
    bars = ax.bar(systems, means, color=colors, edgecolor="#0F172A", width=0.62)
    ax.set_ylabel("Mean commands completed before break", fontsize=11)
    ax.set_title("Magazov ×5 session length by system", fontsize=13, fontweight="bold", color="#0D2137")
    ax.set_ylim(0, 4.2)
    for b, label in zip(bars, ["3.50", "0.20", "0.17", "skipped"]):
        ax.text(
            b.get_x() + b.get_width() / 2, b.get_height() + 0.08, label,
            ha="center", va="bottom", fontsize=10, fontweight="bold",
        )
    ax.tick_params(axis="x", labelsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#E2E8F0", lw=0.8)
    fig.tight_layout()
    path = OUT / "fig4_magazov_session_length.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", path)


def fig_ubuntu_fidelity():
    """One concept: Ubuntu fidelity only."""
    fig, ax = plt.subplots(figsize=(7.8, 4.6), dpi=160)
    systems = ["Cowrie", "Llama 3.1 8B", "Qwen 2.5 7B"]
    fid = [0.00, 0.32, 0.40]
    colors = ["#047857", "#0369A1", "#C2410C"]
    bars = ax.bar(systems, fid, color=colors, edgecolor="#0F172A", width=0.55)
    ax.set_ylabel("Fidelity vs Ubuntu ground truth", fontsize=11)
    ax.set_title("Ubuntu ×1 fidelity by system", fontsize=13, fontweight="bold", color="#0D2137")
    ax.set_ylim(0, 0.55)
    for b, v in zip(bars, fid):
        ax.text(
            b.get_x() + b.get_width() / 2, b.get_height() + 0.015,
            f"{v:.2f}", ha="center", va="bottom", fontsize=11, fontweight="bold",
        )
    ax.tick_params(axis="x", labelsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#E2E8F0", lw=0.8)
    fig.tight_layout()
    path = OUT / "fig5_ubuntu_fidelity.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", path)


def fig_detector_f1():
    """One concept: detector F1 scores only."""
    fig, ax = plt.subplots(figsize=(8.2, 4.6), dpi=160)
    labels = [
        "Binary\nmacro-F1",
        "3-way\nmacro-F1",
        "3-way\nCowrie F1",
        "3-way\nUbuntu F1",
        "3-way\nLLM F1",
    ]
    vals = [0.750, 0.682, 0.739, 0.708, 0.600]
    colors = ["#0369A1", "#C2410C", "#047857", "#4338CA", "#B45309"]
    bars = ax.bar(range(len(vals)), vals, color=colors, edgecolor="#0F172A", width=0.68)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("F1 score", fontsize=11)
    ax.set_title("Exploratory detector F1 scores (held-out test)", fontsize=13, fontweight="bold", color="#0D2137")
    for b, v in zip(bars, vals):
        ax.text(
            b.get_x() + b.get_width() / 2, v + 0.025, f"{v:.3f}",
            ha="center", va="bottom", fontsize=10, fontweight="bold",
        )
    ax.axhline(0.5, color="#CBD5E1", lw=0.9, linestyle="--")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#E2E8F0", lw=0.8)
    fig.tight_layout()
    path = OUT / "fig6_detector_f1.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    # Also write legacy filename used by older report drafts.
    import shutil
    shutil.copy2(path, OUT / "fig5_detector.png")
    print("wrote", path)


if __name__ == "__main__":
    fig_architecture()
    fig_pipeline()
    fig_rq_map()
    fig_magazov_session_length()
    fig_ubuntu_fidelity()
    fig_detector_f1()
