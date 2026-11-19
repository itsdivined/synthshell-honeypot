"""Build short FPR Draft (progress checkpoint) — not the final 7500-word report."""
from __future__ import annotations

import shutil
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(r"C:\Users\devyani patil\honeypot")
FIGS = ROOT / "report_figures"
OUT = ROOT / "FPR_Draft_Patil_Devyani_5034.docx"
OUT_DL = Path(r"C:\Users\devyani patil\Downloads") / "FPR_Draft_Patil_Devyani_5034.docx"
MD_BACKUP = ROOT / "FPR_Draft_Patil_Devyani_5034.md"


def set_run_font(run, size=11, bold=False, italic=False, color=None):
    run.font.name = "Calibri"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color


def add_para(doc, text, *, size=11, bold=False, italic=False, align="justify", space_after=8, space_before=0):
    p = doc.add_paragraph()
    if align == "justify":
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    elif align == "center":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "left":
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    elif align == "right":
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, italic=italic)
    return p


def add_heading_custom(doc, text, level=1):
    # Use built-in heading style then force Calibri
    h = doc.add_heading(text, level=level)
    h.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in h.runs:
        set_run_font(run, size=14 if level == 1 else 12, bold=True, color=RGBColor(0x1F, 0x4E, 0x79))
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(6)
    return h


def add_caption(doc, text):
    p = add_para(doc, text, size=10, italic=True, align="center", space_after=10, space_before=4)
    return p


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        run = p.add_run(h)
        set_run_font(run, size=9, bold=True)
    for r_i, row in enumerate(rows):
        cells = table.rows[r_i + 1].cells
        for c_i, val in enumerate(row):
            cells[c_i].text = ""
            p = cells[c_i].paragraphs[0]
            run = p.add_run(str(val))
            set_run_font(run, size=9)
    doc.add_paragraph()
    return table


def cite_inline(p, before, cite, after=""):
    """Add justified paragraph with Harvard-style citation."""
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r1 = p.add_run(before)
    set_run_font(r1)
    r2 = p.add_run(cite)
    set_run_font(r2)
    if after:
        r3 = p.add_run(after)
        set_run_font(r3)
    p.paragraph_format.space_after = Pt(8)


def build():
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.2)
    section.right_margin = Cm(2.2)

    # Page numbers
    footer = section.footer
    footer.is_linked_to_previous = False
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = fp.add_run("FPR Draft — Patil Devyani Anil (5034) — Page ")
    set_run_font(run, size=9)
    # simple page field
    fld = run._element
    from docx.oxml import OxmlElement

    def add_page_number(paragraph):
        run = paragraph.add_run()
        set_run_font(run, size=9)
        fldChar1 = OxmlElement("w:fldChar")
        fldChar1.set(qn("w:fldCharType"), "begin")
        instrText = OxmlElement("w:instrText")
        instrText.set(qn("xml:space"), "preserve")
        instrText.text = " PAGE "
        fldChar2 = OxmlElement("w:fldChar")
        fldChar2.set(qn("w:fldCharType"), "end")
        run._r.append(fldChar1)
        run._r.append(instrText)
        run._r.append(fldChar2)

    add_page_number(fp)

    # ========== FRONT PAGE ==========
    add_para(doc, "University of Hertfordshire", size=12, bold=True, align="center", space_after=2)
    add_para(
        doc,
        "School of Physics, Engineering and Computer Science",
        size=11,
        align="center",
        space_after=16,
    )
    add_para(doc, "MSc Data Science Project", size=14, bold=True, align="center", space_after=4)
    add_para(doc, "Module: 7FTC2001", size=11, align="center", space_after=4)
    add_para(
        doc,
        "FPR DRAFT (Formative / Progress Report — NOT the final report)",
        size=12,
        bold=True,
        align="center",
        space_after=18,
    )
    add_para(
        doc,
        "Generative AI Deception: Dynamic LLM-Powered Honeypots",
        size=16,
        bold=True,
        align="center",
        space_after=20,
    )
    add_para(doc, "Student: Patil Devyani Anil", size=11, align="center", space_after=2)
    add_para(doc, "Student ID: 5034", size=11, align="center", space_after=2)
    add_para(doc, "Programme: MSc Data Science (Full-time)", size=11, align="center", space_after=2)
    add_para(doc, "Supervisor: Dr Rama Abirami K", size=11, align="center", space_after=2)
    add_para(doc, "Date: Saturday 14 November 2026 (results freeze day)", size=11, align="center", space_after=2)
    add_para(doc, "Final report due: 20 November 2026 · Viva: 23 November 2026", size=10, align="center", space_after=8)
    add_para(
        doc,
        "GitHub: https://github.com/itsdivined/synthshell-honeypot",
        size=11,
        bold=True,
        align="center",
        space_after=12,
    )
    add_para(
        doc,
        "Word count (body estimate, excl. front matter / refs / captions): ~2,200",
        size=10,
        italic=True,
        align="center",
        space_after=8,
    )
    add_para(
        doc,
        "Student note: lightly edit this draft into your own voice before Turnitin / Blackboard submission.",
        size=10,
        italic=True,
        align="center",
        space_after=6,
    )
    doc.add_page_break()

    # ========== DECLARATION (short) ==========
    add_heading_custom(doc, "Declaration (draft)", level=1)
    add_para(
        doc,
        "I confirm that this FPR draft describes my own project progress for module 7FTC2001. "
        "I will personalise the wording before formal submission, cite all sources in Harvard format, "
        "and declare any permitted AI assistance according to University of Hertfordshire policy. "
        "No secrets, API keys, or attack payloads are included.",
        space_after=6,
    )
    add_para(doc, "Student name: Patil Devyani Anil", space_after=2)
    add_para(doc, "Student ID: 5034", space_after=2)
    add_para(doc, "Date: 14 November 2026", space_after=12)

    # ========== ABSTRACT ==========
    add_heading_custom(doc, "1. Abstract", level=1)
    add_para(
        doc,
        "This formative progress report (FPR) summarises work to date on a closed-lab comparison of "
        "scripted and LLM-backed SSH honeypots. Four systems were designed into every experiment: "
        "Cowrie (scripted baseline), GPT-4o mini (commercial API), Llama 3.1 8B and Qwen 2.5 7B "
        "(local Ollama). Identical sessions were replayed on localhost only (127.0.0.1); model replies "
        "are text-only and commands are not executed on the host OS. On Magazov corpus replays "
        "(20 sessions × 5 runs), Cowrie completed a mean of 3.50 commands before break, while Llama "
        "and Qwen completed about 0.20 and 0.17 respectively; GPT-4o mini was skipped for all rows "
        "(no API key). On an Ubuntu ground-truth test set (runs1), reply fidelity improved for the "
        "local LLMs (Llama ≈0.32, Qwen ≈0.40) compared with Cowrie (0.00 by design against real Linux "
        "output). The RQ4 containment audit passed. This document is a progress FPR for Blackboard, "
        "not the final project report.",
    )
    add_para(
        doc,
        "Keywords: honeypot; large language model; Cowrie; fidelity; session survival; containment; Magazov corpus",
        italic=True,
        size=10,
    )

    # ========== INTRO ==========
    add_heading_custom(doc, "2. Introduction and project specification", level=1)
    add_para(
        doc,
        "SSH services are routinely probed. Defenders use honeypots to observe probing without exposing "
        "production hosts. Scripted medium-interaction honeypots such as Cowrie are stable but can be "
        "fingerprinted because replies and filesystem state are fixed. LLM honeypots can invent "
        "plausible shell text for unseen commands, yet they may invent details, forget state, time out, "
        "or depend on paid APIs. Organisations need repeatable evidence for choosing a backend.",
    )
    add_para(
        doc,
        "Aim (README / PDM): how realistic, consistent, and cost-effective an LLM honeypot is compared "
        "with a traditional honeypot, and which type of LLM gives the best balance in an isolated lab.",
    )

    add_heading_custom(doc, "2.1 Research gap, novelty, and contribution", level=2)
    add_para(
        doc,
        "Research gap: there is no student-reproducible multi-step test that compares Cowrie with "
        "several LLM honeypots on fidelity, session survival, speed/cost, and containment under "
        "identical sessions. Prior work often uses one model, single-command sessions, or field "
        "deployments that cannot be rerun.",
    )
    add_para(
        doc,
        "Novelty (measurement design — LLM honeypots already exist): (1) multi-step stateful replay "
        "with session memory; (2) four fixed systems receiving the same sessions; (3) session survival "
        "until a defined break plus technique labels; (4) local open-weight models versus a commercial "
        "API; (5) RQ4 operationalised as a containment audit (localhost bind, text-only, no host "
        "execution), not a stored injection corpus.",
    )
    add_para(
        doc,
        "Contributions in progress: C1 working prototype with session memory; C2 Ubuntu test set with "
        "ground truth (now used for fidelity); C3 controlled Magazov four-system comparison (×5 runs); "
        "C4 technique labels, containment audit, and low-cost design notes.",
    )

    add_heading_custom(doc, "2.2 Research questions and objectives", level=2)
    add_table(
        doc,
        ["ID", "Research question", "Objective"],
        [
            [
                "RQ1 / O1",
                "How realistic and consistent are LLM honeypot replies vs real Linux output?",
                "Measure fidelity and multi-step consistency on ~200 commands / ~20 sessions.",
            ],
            [
                "RQ2 / O2",
                "How do the three LLMs compare on response time and cost?",
                "Record delay per command and cost per session for each model.",
            ],
            [
                "RQ3 / O3",
                "How far do scripted sessions get before each system gives itself away, and which techniques are observed?",
                "Replay until first break; compare commands completed and technique labels with Cowrie.",
            ],
            [
                "RQ4 / O4",
                "How well does each LLM honeypot resist prompt injection?",
                "Run the containment audit and recommend a low-cost design (not a list of injection strings).",
            ],
        ],
    )
    add_caption(doc, "Table 1. Research questions and objectives (PDM / README wording).")
    add_para(
        doc,
        "Break definition: empty reply; wrong or contradictory reply; AI self-disclosure; or delay above "
        "5 seconds. Scope: isolated laptop lab only — no public honeypot.",
    )

    add_heading_custom(doc, "2.3 Ethical considerations (PDM four questions — brief)", level=2)
    add_para(
        doc,
        "No human participants and no surveys. Data are a de-identified public corpus plus lab-captured "
        "Ubuntu outputs; no live attacker traffic is generated. Risks are contained by binding services "
        "to 127.0.0.1, using text-only model output, and never executing honeypot commands on the host. "
        "The ethics quiz was completed on 27 October 2026 "
        "(University of Hertfordshire, n.d.). API keys remain in a gitignored .env file.",
    )

    # ========== LIT ==========
    add_heading_custom(doc, "3. Related work (brief critical review)", level=1)
    add_para(
        doc,
        "Papers below were selected because they cover traditional deception/honeypots, generative "
        "SSH shells, interactive LLM honeypots, backend benchmarking, and the shared traffic corpus "
        "used in this lab. Only sources already verified in the project brief / README are cited.",
    )
    add_para(
        doc,
        "Javadpour et al. (2024) survey cyber deception and honeypot performance, motivating careful "
        "evaluation of realism. Cowrie remains the open-source scripted SSH/Telnet baseline used here "
        "(Cowrie Project, n.d.). Sladić et al. (2023; 2024) establish generative “LLM in the shell” "
        "honeypots and peer-reviewed evaluation context at EuroS&PW. Otal and Canbaz (2024) describe "
        "interactive LLM honeypot systems (IEEE CNS / arXiv:2409.08234), typically harder to rerun "
        "identically than a closed replay design. Wang et al. (2026) present HoneyGPT as an LLM "
        "terminal honeypot line of work emphasising engagement. Magazov et al. (2026a) benchmark LLM "
        "backends for generative SSH honeypots and highlight gaps around single-command sessions; "
        "Magazov et al. (2026b) release the de-identified corpus used as shared Magazov traffic in "
        "this project. This FPR positions the lab as a repeatable four-system multi-step comparison "
        "with explicit fidelity, survival, delay, and containment metrics.",
    )

    # ========== METHODS ==========
    add_heading_custom(doc, "4. Methods (what was done)", level=1)
    add_heading_custom(doc, "4.1 Systems and containment", level=2)
    add_para(
        doc,
        "Four systems stay in every table. A missing key or timeout is recorded as skipped/error — "
        "the system is not removed from the design. Cowrie listens on 127.0.0.1:2222. Local models "
        "use Ollama on 127.0.0.1:11434 (llama3.1:8b, qwen2.5:7b). GPT-4o mini uses text-only calls to "
        "api.openai.com when OPENAI_API_KEY is present. Session memory stores cwd and file/user "
        "deltas; the model has no tools. Safety-critical categories receive fixed denials before an "
        "LLM call. Figure 1 summarises the architecture.",
    )
    doc.add_picture(str(FIGS / "fig1_system_architecture.png"), width=Inches(6.2))
    add_caption(
        doc,
        "Figure 1. System architecture: Magazov/Ubuntu sessions replayed to four backends under localhost containment.",
    )

    add_heading_custom(doc, "4.2 Data", level=2)
    add_para(
        doc,
        "Magazov public corpus: Magazov et al. (2026b), Zenodo DOI https://doi.org/10.5281/zenodo.20816078, "
        "licence CC BY 4.0, accessed 25 October 2026 (~12,881 command rows after download/screen). "
        "Used as shared realistic SSH session traffic. Ubuntu ground-truth test set: ~200 commands / "
        "20 sessions captured in an offline container for RQ1 fidelity scoring "
        "(analysis folder data/analysis/ubuntu_runs1/).",
    )

    add_heading_custom(doc, "4.3 Procedure and metrics", level=2)
    add_para(
        doc,
        "Pipeline (Figure 2): download Magazov → screen IP counts → replay identical sessions to all "
        "four systems (scripts/04_replay.py) → analyse with bootstrap 95% CIs and Wilcoxon signed-rank "
        "where paired sessions ≥5 (scripts/05_analyse.py) → freeze tables on 14 November 2026. "
        "Primary frozen logs: Magazov 20 sessions × 5 runs; Ubuntu test-set runs1 for fidelity.",
    )
    doc.add_picture(str(FIGS / "fig2_method_pipeline.png"), width=Inches(6.2))
    add_caption(doc, "Figure 2. Method pipeline from corpus download to freeze-day analysis.")
    add_para(
        doc,
        "Metrics justified by RQs: fidelity / consistency / invented-content (RQ1); delay and cost "
        "(RQ2); commands completed until break and technique labels (RQ3); containment checklist "
        "(RQ4). Figure 3 maps each RQ to freeze-day evidence.",
    )
    doc.add_picture(str(FIGS / "fig3_rq_mapping.png"), width=Inches(6.0))
    add_caption(doc, "Figure 3. RQ mapping to freeze-day evidence sources.")

    # ========== RESULTS ==========
    add_heading_custom(doc, "5. Results so far (freeze day 14 Nov 2026)", level=1)
    add_para(
        doc,
        "Numbers below are taken from data/analysis/runs5/tables.md (Magazov) and "
        "data/analysis/ubuntu_runs1/tables.md (Ubuntu fidelity). Magazov ×5 was not re-run for this FPR.",
    )

    add_heading_custom(doc, "5.1 Magazov ×5 — delay, survival, status", level=2)
    add_table(
        doc,
        [
            "System",
            "OK / skipped / error",
            "Mean delay (s) [95% CI]",
            "Mean cmds completed",
            "Technique labels",
        ],
        [
            ["cowrie", "350 / 0 / 0", "0.37 [0.34, 0.40]", "3.50", "8"],
            ["gpt-4o-mini", "0 / 350 / 0", "— (skipped)", "—", "8"],
            ["llama-3.1-8b", "86 / 0 / 264", "51.5 [42.5, 60.4]", "0.20", "8"],
            ["qwen-2.5-7b", "153 / 0 / 197", "50.4 [44.9, 55.7]", "0.17", "8"],
        ],
    )
    add_caption(
        doc,
        "Table 2. Magazov 20 sessions × 5 runs (data/analysis/runs5). GPT skipped: no API key. "
        "Local errors are mainly TimeoutError on CPU/RAM-limited Ollama.",
    )
    add_para(
        doc,
        "Wilcoxon on commands completed (Cowrie vs LLM): vs Llama n=100, statistic=0.0, p≈1.1×10⁻¹⁶; "
        "vs Qwen n=100, statistic=0.0, p≈1.8×10⁻¹⁶; vs GPT n=0 (all skipped). Honest reading: on "
        "Magazov traffic under the 5-second break rule, Cowrie survives longer than the local LLMs. "
        "This FPR does not claim that LLMs beat Cowrie on Magazov session length.",
    )

    add_heading_custom(doc, "5.2 Ubuntu runs1 — fidelity (RQ1 improvement)", level=2)
    add_table(
        doc,
        ["System", "OK replies", "Fidelity", "Consistency", "Invented content", "Mean cmds completed"],
        [
            ["cowrie", "200", "0.00", "0.14", "1.00", "10.00"],
            ["gpt-4o-mini", "0 (skipped)", "—", "—", "—", "—"],
            ["llama-3.1-8b", "106", "0.32", "0.60", "0.64", "0.05"],
            ["qwen-2.5-7b", "121", "0.40", "0.20", "0.57", "0.00"],
        ],
    )
    add_caption(
        doc,
        "Table 3. Ubuntu ground-truth fidelity (data/analysis/ubuntu_runs1). Cowrie fidelity 0.00 is "
        "expected when scored against real Linux output (scripted replies differ by design).",
    )
    add_para(
        doc,
        "This is the main measured improvement over the scripted baseline for realism: Qwen "
        "(≈0.40) and Llama (≈0.32) exceed Cowrie (0.00) on fidelity to Ubuntu ground truth, while "
        "still showing invented-content rates and poor session survival under the delay break.",
    )
    doc.add_picture(str(FIGS / "fig4_results_bars.png"), width=Inches(6.2))
    add_caption(
        doc,
        "Figure 4. Left: Magazov mean commands completed (Cowrie stronger). Right: Ubuntu fidelity "
        "(local LLMs stronger than Cowrie).",
    )

    add_heading_custom(doc, "5.3 RQ4 containment", level=2)
    add_para(
        doc,
        "Containment audit: Passed. Checks include local_bind, cowrie_localhost, ollama_localhost, "
        "openai_host_pinned, no_host_execution, no_honeypot_outbound, text_only_output, no_model_tools, "
        "and source_has_no_host_shell (data/analysis/runs5/rq4_containment.json). Injection wording is "
        "not stored in the repository.",
    )

    # ========== DISCUSSION ==========
    add_heading_custom(doc, "6. Discussion: novelty and improvement vs existing systems", level=1)
    add_para(
        doc,
        "Relative to generative honeypot systems in the literature (Sladić et al., 2023; 2024; "
        "Otal and Canbaz, 2024; Wang et al., 2026) and backend benchmarking (Magazov et al., 2026a), "
        "this lab’s contribution is not “first LLM honeypot” but a repeatable four-system multi-step "
        "measurement with honest skip/timeout accounting.",
    )
    add_para(
        doc,
        "Improvement claim (honest): on Ubuntu ground truth, local LLMs raise reply fidelity "
        "(Qwen 0.40, Llama 0.32) above Cowrie’s 0.00. Trade-off: on Magazov multi-step survival and "
        "delay, Cowrie remains clearly stronger (3.50 vs ~0.2 commands; sub-second vs ~50 s mean delay "
        "on OK replies). GPT-4o mini contributes no delay/cost numbers yet because every Magazov and "
        "Ubuntu row was skipped without an API key — the row stays in the design. Hardware "
        "(~7.5 GB RAM, CPU Ollama) explains many timeouts and should be stated in the viva.",
    )
    add_para(
        doc,
        "Objectives progress: O1 partially met via Ubuntu fidelity; O2 partially met (delay CIs; "
        "GPT cost blank); O3 met for Magazov survival/Wilcoxon/labels; O4 met as containment pass. "
        "Study_complete remains false while GPT is skipped.",
    )
    add_para(
        doc,
        "Use-case: a low-cost organisation lab can keep Cowrie for fast scripted coverage, add a "
        "text-only local LLM with session memory when hardware meets the 5 s engagement threshold, "
        "and keep fixed denials plus localhost bind. Do not execute model text as host commands.",
    )

    # ========== LIMITATIONS ==========
    add_heading_custom(doc, "7. Limitations", level=1)
    add_para(
        doc,
        "(1) Isolated lab only — limited external validity to live attackers. "
        "(2) CPU/RAM timeouts dominate Llama/Qwen Magazov rows. "
        "(3) GPT-4o mini skipped — no commercial delay/cost figures. "
        "(4) Cowrie fidelity 0.00 on Ubuntu GT is by design (scripted ≠ real Linux). "
        "(5) RQ4 is a containment audit, not an injection-string battery. "
        "(6) Ubuntu fidelity is currently runs1 (not ×5); Magazov has no Ubuntu GT joined for fidelity.",
    )

    # ========== CONCLUSION ==========
    add_heading_custom(doc, "8. Conclusion and future enhancement", level=1)
    add_para(
        doc,
        "RQ1: local LLMs show higher Ubuntu fidelity than Cowrie (Qwen 0.40, Llama 0.32 vs 0.00). "
        "RQ2: Cowrie is fast; local models are slow/timeout-prone; GPT skipped. "
        "RQ3: Cowrie completes more Magazov commands before break than Llama/Qwen — LLMs do not "
        "outperform Cowrie on Magazov session length in these freezes. "
        "RQ4: containment audit passed.",
    )
    add_para(
        doc,
        "Future enhancement before/after the final report: complete a keyed GPT-4o mini replay into "
        "a separate log; re-test local models on GPU/more RAM to reduce timeouts; optionally extend "
        "Ubuntu runs to ×5 for stronger consistency CIs; keep Magazov ×5 frozen (no re-run). "
        "The final project report (due 20 November 2026) will expand literature critique, appendices, "
        "and viva-ready code walk-throughs — this FPR is the shorter progress checkpoint only.",
    )

    # ========== REFERENCES ==========
    add_heading_custom(doc, "References", level=1)
    refs = [
        "Cowrie Project (n.d.) Cowrie SSH/Telnet honeypot [Online]. Available at: https://github.com/cowrie/cowrie (Accessed: 14 November 2026).",
        "Javadpour, A. et al. (2024) ‘A survey of cyber deception and honeypot performance’, Computers & Security, 140, 103792. Available at: https://doi.org/10.1016/j.cose.2024.103792",
        "Magazov, R. et al. (2026a) ‘Benchmarking LLM backends for generative SSH honeypots’, AI, 7(8), 287. Available at: https://doi.org/10.3390/ai7080287",
        "Magazov, R., Abeshev, K., Shamuratov, Y., Uralova, F. and Aksholak, G. (2026b) De-identified SSH honeypot attacker corpus [Dataset]. Zenodo. Available at: https://doi.org/10.5281/zenodo.20816078 (CC BY 4.0).",
        "Otal, H. and Canbaz, M.A. (2024) ‘LLM honeypot: monitoring AI jailbreaks with generative honeypot systems’. arXiv:2409.08234. Available at: https://arxiv.org/abs/2409.08234 (see also IEEE CNS / Xplore 10735607).",
        "Sladić, M. et al. (2023) ‘LLM in the shell: generative honeypots’. arXiv:2309.00155. Available at: https://arxiv.org/abs/2309.00155",
        "Sladić, M. et al. (2024) Generative honeypot evaluation paper, IEEE European Symposium on Security and Privacy Workshops (EuroS&PW). Available at: https://doi.org/10.1109/EuroSPW61312.2024.00054",
        "University of Hertfordshire (n.d.) Ethics approval information [Online]. Available at: https://ask.herts.ac.uk/ethics-approval (Accessed: 14 November 2026).",
        "Wang et al. (2026) ‘HoneyGPT…’, Computer Networks, 282, 112223. Available at: https://doi.org/10.1016/j.comnet.2026.112223",
    ]
    for r in refs:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.left_indent = Cm(0.5)
        p.paragraph_format.first_line_indent = Cm(-0.5)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(r)
        set_run_font(run, size=10)

    add_heading_custom(doc, "Appendix A — Analysis pointers (not full code dump)", level=1)
    add_para(
        doc,
        "Frozen Magazov analysis: data/analysis/runs5/ (tables.md, summary.json, rq4_containment.json). "
        "Ubuntu fidelity: data/analysis/ubuntu_runs1/. Reproduce scoring without re-running Magazov ×5: "
        "python scripts/05_analyse.py --log data\\logs\\replay_magazov_20sess_runs5.jsonl "
        "--out-dir data\\analysis\\runs5. Full code appendix belongs in the final report; GitHub holds "
        "the working repository: https://github.com/itsdivined/synthshell-honeypot",
        size=10,
    )
    add_para(
        doc,
        "— End of FPR Draft (progress checkpoint). Final report is separate and due 20 November 2026. —",
        italic=True,
        align="center",
        size=10,
    )

    doc.save(OUT)
    shutil.copy2(OUT, OUT_DL)
    print("Wrote", OUT)
    print("Copied", OUT_DL)

    # rough word count of body text via paragraphs
    words = 0
    for p in doc.paragraphs:
        words += len(p.text.split())
    print("Approx paragraph word count:", words)


if __name__ == "__main__":
    build()
