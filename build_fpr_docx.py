"""Build FPR_Draft_Patil_Devyani_5034.docx for Blackboard draft submission."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(r"C:\Users\devyani patil\honeypot")
FIGS = ROOT / "report_figures"
OUT = ROOT / "FPR_Draft_Patil_Devyani_5034.docx"
OUT_DL = Path(r"C:\Users\devyani patil\Downloads\FPR_Draft_Patil_Devyani_5034.docx")
MD_BACKUP = ROOT / "FPR_Draft_Patil_Devyani_5034.md"

GITHUB = "https://github.com/itsdivined/synthshell-honeypot"


def set_run_font(run, size=11, bold=False, italic=False, color=None):
    run.font.name = "Calibri"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def add_para(doc, text, *, size=11, bold=False, italic=False, align="justify",
             space_after=8, space_before=0, first_line=True):
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
    if first_line and align == "justify":
        pf.first_line_indent = Cm(0.5)
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, italic=italic)
    return p


def add_heading_custom(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        set_run_font(run, size=14 if level == 1 else 12, bold=True)
        run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(8)
    return h


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(10)
    run = p.add_run(text)
    set_run_font(run, size=10, italic=True)
    return p


def add_figure(doc, path: Path, caption: str, width_inches=5.9):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(path), width=Inches(width_inches))
    add_caption(doc, caption)


def set_cell_text(cell, text, *, bold=False, size=9):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold)


def add_table(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    for i, h in enumerate(headers):
        set_cell_text(table.rows[0].cells[i], h, bold=True, size=9)
    for r_i, row in enumerate(rows):
        for c_i, val in enumerate(row):
            set_cell_text(table.rows[r_i + 1].cells[c_i], str(val), size=9)
    if col_widths:
        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Cm(w)
    doc.add_paragraph()
    return table


def front_page(doc):
    for _ in range(2):
        add_para(doc, "", align="center", space_after=0, first_line=False)
    add_para(doc, "University of Hertfordshire", size=14, bold=True,
             align="center", first_line=False, space_after=2)
    add_para(doc, "School of Physics, Engineering and Computer Science",
             size=11, align="center", first_line=False, space_after=2)
    add_para(doc, "Department of Physics, Astronomy and Mathematics",
             size=11, align="center", first_line=False, space_after=14)
    add_para(doc, "MSc Data Science Project", size=12, bold=True,
             align="center", first_line=False, space_after=2)
    add_para(doc, "Module 7FTC2001", size=11, align="center",
             first_line=False, space_after=10)
    add_para(doc, "Data Science FINAL PROJECT REPORT", size=16, bold=True,
             align="center", first_line=False, space_after=18)

    fields = [
        ("Project Title:", "Generative AI Deception: Dynamic LLM-Powered Honeypots"),
        ("Student Name and SRN:", "Patil Devyani Anil, ID 5034"),
        ("Programme:", "MSc Data Science (Full-Time)"),
        ("Supervisor:", "Dr Rama Abirami K"),
        ("Date Submitted (draft):", "14 November 2026 (practical freeze day)"),
        ("Report due:", "20 November 2026"),
        ("Word Count (estimate):", "~4700 draft (max ~7500; expand in your voice)"),
        ("GitHub address:", GITHUB),
    ]
    for label, value in fields:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.first_line_indent = Cm(0)
        r1 = p.add_run(label + " ")
        set_run_font(r1, size=11, bold=True)
        r2 = p.add_run(value)
        set_run_font(r2, size=11)
        if "GitHub" in label:
            r2.font.color.rgb = RGBColor(0x05, 0x63, 0xC1)

    add_para(doc, "", first_line=False)
    add_para(
        doc,
        "DRAFT for student editing before Turnitin / Blackboard final upload. "
        "Rewrite in your own voice; declare any AI assistance per UH policy.",
        size=10, italic=True, align="center", first_line=False,
    )
    doc.add_page_break()


def declaration_page(doc):
    add_heading_custom(doc, "DECLARATION STATEMENT", level=1)
    add_para(
        doc,
        "This report is submitted in partial fulfilment of the requirement for the "
        "degree of Master of Science in Data Science at the University of Hertfordshire.",
        first_line=False,
    )
    add_para(
        doc,
        "I confirm that this is my own work. Where material from other sources has been "
        "used, it is clearly cited using Harvard referencing. I understand that plagiarism, "
        "collusion, fabrication of data, and false referencing are academic offences.",
        first_line=False,
    )
    add_para(
        doc,
        "No human participants or surveys were used in this project. The study is a "
        "closed-lab comparison on localhost (127.0.0.1) using a public de-identified "
        "SSH corpus and locally captured Ubuntu ground-truth outputs.",
        first_line=False,
    )
    add_para(
        doc,
        "AI-assistance note (student must complete before final submission): This file is "
        "a DRAFT scaffold. I will edit the wording into my own voice. Any remaining use of "
        "generative AI tools will be declared and referenced in line with University of "
        "Hertfordshire policy. I have not submitted undeclared AI-written text as final work.",
        first_line=False, italic=True,
    )
    add_para(
        doc,
        "I give permission for this report to be made available on module websites as "
        "required by the programme.",
        first_line=False,
    )
    add_para(doc, "", first_line=False)
    for line in [
        "Student SRN number: 5034",
        "Student Name printed: Patil Devyani Anil",
        "Student signature: _______________________________    Date: _______________",
    ]:
        add_para(doc, line, align="left", first_line=False, space_after=10)
    add_para(
        doc,
        "UNIVERSITY OF HERTFORDSHIRE — SCHOOL OF PHYSICS, ENGINEERING AND COMPUTER SCIENCE",
        size=9, align="center", first_line=False, space_before=24,
    )
    doc.add_page_break()


def abstract_and_keywords(doc):
    add_heading_custom(doc, "Abstract", level=1)
    add_para(
        doc,
        "Scripted SSH honeypots such as Cowrie are stable but often fingerprintable because "
        "replies and filesystem state are fixed. Large language model (LLM) honeypots can "
        "invent plausible shell text for almost any command, yet they may forget session "
        "state, invent details, time out, or depend on paid APIs. This project asks how "
        "realistic, consistent, and cost-effective an LLM honeypot is compared with a "
        "traditional honeypot, and which backend gives the best balance in a closed lab.",
    )
    add_para(
        doc,
        "Four systems were compared on identical multi-step sessions: Cowrie (scripted "
        "baseline), GPT-4o mini (commercial API), Llama 3.1 8B (local Ollama), and Qwen "
        "2.5 7B (local Ollama). Shared traffic came from the Magazov et al. (2026b) "
        "de-identified SSH corpus (Zenodo DOI 10.5281/zenodo.20816078, CC BY 4.0). Twenty "
        "Magazov sessions were replayed five times to each system. Separately, an Ubuntu "
        "ground-truth test set was replayed once to score fidelity. Metrics included delay "
        "with bootstrap 95% confidence intervals, commands completed until a defined break, "
        "technique labels, fidelity versus real Linux output, and a containment audit for "
        "research question four (RQ4).",
    )
    add_para(
        doc,
        "On Magazov engagement, Cowrie completed a mean of 3.50 commands per session with "
        "sub-second delay, while local LLMs completed far fewer commands before break "
        "(Llama 0.20; Qwen 0.17), largely because of CPU/RAM timeouts; GPT-4o mini was "
        "skipped for all Magazov rows (no API key). On Ubuntu fidelity — the realism "
        "improvement over the scripted baseline — Cowrie scored 0.00 by design against "
        "Ubuntu ground truth, whereas Llama reached 0.32 and Qwen 0.40. RQ4 containment "
        "passed (localhost bind, text-only model output, no host execution). The honest "
        "conclusion is that LLMs improve reply realism relative to Cowrie under ground-truth "
        "scoring, but do not beat Cowrie on Magazov session length on this laptop hardware.",
    )
    add_para(
        doc,
        "Keywords: honeypot; large language model; Cowrie; session survival; fidelity; "
        "containment; Magazov corpus",
        italic=True, first_line=False,
    )


def section_introduction(doc):
    add_heading_custom(doc, "1. Introduction", level=1)
    add_para(
        doc,
        "Attackers and scanners routinely probe SSH services. Defenders use honeypots to "
        "observe probing behaviour without exposing production hosts. Traditional "
        "medium-interaction honeypots such as Cowrie emulate a shell with scripted replies "
        "and a fake filesystem (Cowrie Project, n.d.). They are stable and cheap to run, "
        "but experienced scanners can recognise fixed banners, incomplete command coverage, "
        "and inconsistent state. Generative AI changes the design space: an LLM can produce "
        "shell-like text for commands that a script never anticipated (Sladić et al., 2023; "
        "Wang et al., 2026). That flexibility may increase realism, but it also introduces "
        "new failure modes — invented file contents, forgotten session state, slow replies, "
        "and dependency on external APIs.",
    )
    add_para(
        doc,
        "Organisations that cannot send session data off-site may prefer small local models; "
        "others may prefer a commercial API for quality. Without a repeatable comparison, "
        "those choices rest on demos rather than evidence. Magazov et al. (2026a) note "
        "evaluation gaps around single-command designs and backend comparison. This project "
        "responds with a closed-lab, multi-step, four-system replay study on identical "
        "saved sessions.",
    )

    add_heading_custom(doc, "1.1 Aim and scope", level=2)
    add_para(
        doc,
        "The aim is to assess how realistic, consistent, and cost-effective an LLM honeypot "
        "is relative to a traditional honeypot, and which type of LLM gives the best balance "
        "in an isolated laptop lab. Everything binds to 127.0.0.1. There is no public "
        "honeypot and no live attacker traffic generated by this project. LLM backends "
        "return text only: the model is not given tools, and commands are not executed on "
        "the host operating system.",
    )

    add_heading_custom(doc, "1.2 Research gap, novelty, and contributions", level=2)
    add_para(
        doc,
        "Research gap. There is no repeatable multi-step test that compares Cowrie with "
        "several LLM honeypots on consistency, session survival, speed, cost, and "
        "injection-related resistance under identical conditions. Existing studies often "
        "fix one model, send one command per session, rely on small human studies or "
        "field deployments that cannot be rerun, and leave invented details, slow replies, "
        "and paid APIs weakly measured.",
    )
    add_para(
        doc,
        "Novelty. LLM honeypots already exist. The novelty claimed here is measurement "
        "design, not “first LLM honeypot”: (1) multi-step stateful testing with session "
        "memory; (2) Cowrie and three LLM honeypots receiving identical sessions; "
        "(3) session survival as a proxy for engagement plus technique labels; (4) small "
        "local models compared with a commercial API; (5) RQ4 operationalised as a "
        "containment audit (local bind, text-only output, no host execution). Injection "
        "wording is not stored in the repository.",
    )
    add_para(
        doc,
        "Contributions. C1: a working LLM honeypot prototype with session-state memory. "
        "C2: a reusable Ubuntu test set with ground-truth outputs (~200 commands / "
        "~20 sessions). C3: a controlled four-system comparison on Magazov and Ubuntu "
        "sessions. C4: technique-label counts, containment audit, and low-cost design notes.",
    )

    add_heading_custom(doc, "1.3 Research questions and objectives", level=2)
    add_para(
        doc,
        "Table 1 states the four research questions (RQs) and matching objectives (O1–O4). "
        "Every later result is mapped back to these questions.",
        first_line=False,
    )
    add_table(
        doc,
        ["ID", "Research question", "Objective"],
        [
            ["RQ1 / O1",
             "How realistic and consistent are LLM honeypot replies compared with real Linux output?",
             "Measure fidelity and multi-step consistency on about 200 commands and 20 sessions."],
            ["RQ2 / O2",
             "How do the three LLMs compare on response time and cost?",
             "Record delay per command and cost per session for each model."],
            ["RQ3 / O3",
             "How far do scripted sessions get before each system gives itself away, and which techniques are observed?",
             "Replay until first break; compare commands completed and technique labels with Cowrie."],
            ["RQ4 / O4",
             "How well does each LLM honeypot resist prompt injection?",
             "Run the containment audit and recommend a low-cost design (not a stored injection-string list)."],
        ],
    )
    add_caption(doc, "Table 1. Research questions and objectives (README / PDM wording).")
    add_para(
        doc,
        "Break definition (used throughout): empty reply; wrong or contradictory reply; "
        "AI self-disclosure; or delay above 5 seconds. Study settings: 5 runs per system "
        "for Magazov; 95% bootstrap confidence intervals; Wilcoxon signed-rank tests when "
        "at least five paired sessions exist.",
    )

    add_heading_custom(doc, "1.4 Ethical considerations (PDM four questions)", level=2)
    add_para(
        doc,
        "Ethics quiz completed 27 October 2026 (University of Hertfordshire, n.d.). The "
        "four PDM ethical questions are answered as follows for this project.",
    )
    add_para(
        doc,
        "(1) Human participants: none. No interviews, surveys, or identifiable persons. "
        "(2) Personal / sensitive data: Magazov corpus is de-identified by its authors; "
        "an IP screen reported zero public addresses needing review; no attacker payload "
        "files are retained as study artefacts. (3) Risk of harm: isolated laptop lab only; "
        "bind 127.0.0.1; models return text only; commands are not executed on the host; "
        "injection strings are not stored. (4) Legal / licence compliance: Magazov data "
        "CC BY 4.0 attributed; Cowrie BSD-3-Clause; API keys stay in gitignored .env; "
        "GitHub repository documents licences.",
    )

    add_heading_custom(doc, "1.5 Difficulty of the project", level=2)
    add_para(
        doc,
        "The work combines systems engineering (Cowrie on localhost, Ollama local models, "
        "API skip handling), data engineering (Zenodo download, screening, JSONL logging), "
        "and statistical evaluation (bootstrap CIs, Wilcoxon). Practical difficulty on the "
        "student laptop (~7.5 GB RAM, CPU Ollama) produced frequent timeouts for 7–8B "
        "models, which is reported honestly rather than hidden. Building a four-row design "
        "that keeps skipped systems visible required careful experimental discipline.",
    )

    add_heading_custom(doc, "1.6 Report structure", level=2)
    add_para(
        doc,
        "Section 2 reviews related literature critically. Section 3 describes data, "
        "systems, and methods. Section 4 reports frozen results. Section 5 discusses "
        "findings against the RQs and prior work. Section 6 states limitations. Section 7 "
        "concludes and outlines future enhancements. References and appendices follow.",
    )


def section_literature(doc):
    add_heading_custom(doc, "2. Literature review", level=1)
    add_para(
        doc,
        "This review selects peer-reviewed and arXiv sources already verified in the "
        "project brief and README. Papers were chosen because they either define "
        "traditional SSH honeypot practice, introduce generative/LLM honeypots, or "
        "provide shared traffic and backend-benchmark framing used directly in this "
        "lab. Website-only student theses are avoided. Each subsection describes the "
        "work, notes strengths and limits, and states how the paper informed this project.",
        first_line=False,
    )

    add_heading_custom(doc, "2.1 Traditional honeypots and cyber deception", level=2)
    add_para(
        doc,
        "Javadpour et al. (2024) survey cyber deception and honeypot performance in "
        "Computers & Security. Purpose: synthesise how decoys are evaluated; data and "
        "methods vary across the surveyed literature; results emphasise that realism and "
        "evaluation design matter for defensive value. Strengths: broad framing of why "
        "honeypot quality is not only “does it run?” Limitations: survey breadth rather "
        "than a single reproducible multi-backend protocol. Relation to this project: "
        "justifies treating realism, engagement proxies, and evaluation discipline as "
        "first-class outcomes, and motivates keeping Cowrie as a recognised scripted "
        "baseline (Cowrie Project, n.d.).",
    )

    add_heading_custom(doc, "2.2 Generative and LLM honeypots", level=2)
    add_para(
        doc,
        "Sladić et al. (2023) explore LLMs “in the shell” as generative honeypots "
        "(arXiv:2309.00155). Purpose: show that language models can emit shell-like "
        "replies; methods rely on generative prompting rather than fixed scripts; "
        "conclusions support feasibility of LLM shells. Strengths: early clear motivation "
        "for generative replies. Limitations: not a four-system paired Magazov-style "
        "student-lab protocol with bootstrap CIs. Relation: motivates the LLM backend "
        "rows in this study.",
    )
    add_para(
        doc,
        "Sladić et al. (2024) provide a peer-reviewed EuroS&PW evaluation context for "
        "generative honeypots (doi:10.1109/EuroSPW61312.2024.00054). Strengths: "
        "workshop peer review and human/realism discussion. Limitations: evaluation "
        "setting differs from closed identical-session replay on a student laptop. "
        "Relation: supports discussing realism carefully rather than claiming a live "
        "attacker field trial.",
    )
    add_para(
        doc,
        "Otal and Canbaz (2024) present an interactive LLM honeypot system "
        "(arXiv:2409.08234; IEEE CNS). Purpose/methods: interactive LLM honeypot "
        "behaviour in a system-oriented setting. Strengths: demonstrates interactive "
        "design. Limitations: field/system demos are hard to rerun identically. Relation: "
        "contrast with this project’s closed replay of saved sessions so markers can "
        "reproduce tables from logs.",
    )
    add_para(
        doc,
        "Wang et al. (2026) describe HoneyGPT as an LLM terminal honeypot line of work "
        "in Computer Networks (doi:10.1016/j.comnet.2026.112223; also arXiv:2406.01882 "
        "as cited in the PDM). Strengths: engagement and terminal-honeypot discussion. "
        "Limitations: not the same Magazov five-run paired design used here. Relation: "
        "motivates measuring how far sessions get before a defined break.",
    )

    add_heading_custom(doc, "2.3 Benchmarks and shared traffic", level=2)
    add_para(
        doc,
        "Magazov et al. (2026a) benchmark LLM backends for generative SSH honeypots "
        "(AI, 7(8), 287; doi:10.3390/ai7080287). Purpose: compare backends; they note "
        "gaps such as single-command sessions. Strengths: closest published framing for "
        "backend comparison. Limitations: not identical to this student’s four-row "
        "multi-step survival + Ubuntu fidelity package. Relation: directly informs the "
        "research gap wording and multi-step design.",
    )
    add_para(
        doc,
        "Magazov et al. (2026b) released a de-identified SSH honeypot attacker corpus on "
        "Zenodo (doi:10.5281/zenodo.20816078, CC BY 4.0). Purpose: share realistic "
        "command traffic; ~12,881 command rows in the verified download used here. "
        "Strengths: public, citable, licence-clear shared sessions. Limitations: "
        "de-identified attacker traffic is not Ubuntu ground truth. Relation: Study A "
        "replays a 20-session Magazov slice to all four systems for engagement and delay.",
    )

    add_heading_custom(doc, "2.4 Position of this project", level=2)
    add_para(
        doc,
        "Prior work shows LLM honeypots are feasible and that realism/engagement matter. "
        "What remains scarce is a student-lab comparison in which Cowrie and several LLM "
        "backends receive the same multi-step sessions, with explicit session-survival "
        "scoring, bootstrap intervals, paired tests against Cowrie, local versus API "
        "privacy trade-offs, Ubuntu fidelity when ground truth exists, and a documented "
        "containment posture. That niche is filled by the synthshell-honeypot repository "
        f"({GITHUB}).",
    )


def section_methods(doc):
    add_heading_custom(doc, "3. Data, systems, and methods", level=1)
    add_para(
        doc,
        "This section describes what was done in this project only — tools, paths, and "
        "decisions — not a general philosophy of research methods.",
        first_line=False,
    )

    add_heading_custom(doc, "3.1 Lab architecture", level=2)
    add_para(
        doc,
        "Figure 1 shows the four backends inside a localhost containment boundary. "
        "scripts/04_replay.py sends the same session list to Cowrie (127.0.0.1:2222), "
        "GPT-4o mini (text call to api.openai.com, skipped if no key), Llama 3.1 8B and "
        "Qwen 2.5 7B (Ollama on 127.0.0.1:11434). Session memory records cwd and file/user "
        "deltas; models have no tools; commands are never passed to the host OS.",
    )
    add_figure(
        doc,
        FIGS / "fig1_architecture.png",
        "Figure 1. System architecture: four systems and localhost containment.",
    )

    add_heading_custom(doc, "3.2 Method pipeline", level=2)
    add_para(
        doc,
        "Figure 2 summarises the pipeline: download Magazov → screen IPs → check Ubuntu "
        "test-set scaffold → replay identical sessions → analyse scores and RQ4 audit. "
        "Study A is Magazov ×5 (engagement/delay). Study B is Ubuntu ×1 with ground truth "
        "(fidelity). Tables froze on 14 November 2026.",
    )
    add_figure(
        doc,
        FIGS / "fig2_method_pipeline.png",
        "Figure 2. Method pipeline from download through replay and analysis.",
    )

    add_heading_custom(doc, "3.3 Systems under test", level=2)
    add_table(
        doc,
        ["System", "Role", "How it is run", "Notes"],
        [
            ["Cowrie", "Scripted baseline", "SSH 127.0.0.1:2222 (WSL/local)", "BSD-3-Clause"],
            ["GPT-4o mini", "Commercial API", "Text-only OpenAI call", "Skip if no OPENAI_API_KEY"],
            ["Llama 3.1 8B", "Local open-weight", "Ollama llama3.1:8b @ 127.0.0.1", "CPU timeouts likely"],
            ["Qwen 2.5 7B", "Local open-weight", "Ollama qwen2.5:7b @ 127.0.0.1", "CPU timeouts likely"],
        ],
    )
    add_caption(doc, "Table 2. Four systems kept as rows even when a backend is skipped.")
    add_para(
        doc,
        "Safety-critical categories (for example sudo / password-file reads) receive a "
        "fixed denial before an LLM call. Cowrie uses its own replies. The four-row design "
        "never drops a system because of a missing key or timeout; those outcomes are "
        "recorded as skipped/error statuses.",
    )

    add_heading_custom(doc, "3.4 Datasets", level=2)
    add_para(
        doc,
        "Magazov public corpus (Study A). Magazov et al. (2026b), Zenodo DOI "
        "10.5281/zenodo.20816078, https://doi.org/10.5281/zenodo.20816078, licence "
        "CC BY 4.0 (data/results). Verified download: 12,881 command rows; accessed "
        "25 October 2026; MD5 checked in data/MANIFEST.txt; IP screen via "
        "scripts/02_screen.py reported zero public addresses needing review. Study slice: "
        "--source magazov --max-sessions 20 --runs 5, log "
        "data/logs/replay_magazov_20sess_runs5.jsonl (finished 7 November 2026). Analysis: "
        "data/analysis/runs5/.",
    )
    add_para(
        doc,
        "Ubuntu container test set (Study B). About 200 ground-truth commands and "
        "20 scripted sessions captured offline for fidelity scoring against real Linux "
        "output. Replay/analysis: data/analysis/ubuntu_runs1/ from "
        "replay_ubuntu_testset_runs1.jsonl (800 command rows scored; ground truth present). "
        "Cowrie fidelity of 0.00 against Ubuntu ground truth is expected by design for a "
        "scripted emulator that does not match a live Ubuntu container output-for-output.",
    )

    add_heading_custom(doc, "3.5 Procedure", level=2)
    add_para(
        doc,
        "1) Containment pre-check (must pass for RQ4 claims). 2) Replay the same session "
        "list to all four systems via scripts/04_replay.py. 3) Log command, reply, delay, "
        "tokens, system, settings, run number, and status (ok / skipped / error). "
        "4) Score with scripts/05_analyse.py (bootstrap CIs, Wilcoxon when pairs exist, "
        "RQ4 audit). 5) Freeze tables on 14 November 2026 for the FPR.",
        first_line=False,
    )

    add_heading_custom(doc, "3.6 Metrics, statistics, and optimisation", level=2)
    add_para(
        doc,
        "Metrics (more than one, justified). Fidelity and invented-content rate (RQ1) "
        "compare replies to Ubuntu ground truth when joined. Consistency (RQ1) measures "
        "within-session agreement of replies to the same command. Delay with 95% bootstrap "
        "CI (RQ2) quantifies responsiveness on OK replies. Cost USD (RQ2) applies to GPT "
        "only after price environment variables are set; local/Cowrie costed at 0 when they "
        "reply. Commands completed until first break (RQ3) is the engagement / session-"
        "survival proxy under the 5-second delay rule. Technique-label counts (RQ3) "
        "summarise defender-visible labels attached by the pipeline. Wilcoxon signed-rank "
        "tests compare each LLM with Cowrie on paired commands_completed. RQ4 uses a "
        "pass/fail containment checklist rather than stored injection payloads.",
    )
    add_para(
        doc,
        "Optimisation / parameter exploration. Prompt temperature candidates (0, 0.2, 0.5) "
        "and history windows (5, 10, 20) were considered on a small validation set kept "
        "separate from the test set; frozen Magazov runs used the lab defaults recorded in "
        "the run header (temperature 0.0, history window 10 as configured in src/config.py). "
        "Fixed denials for safety-critical categories were retained after early smoke tests. "
        "Hardware constraints (CPU Ollama, ~7.5 GB RAM) dominated local-model outcomes; "
        "further latency optimisation would require GPU/RAM upgrades rather than silent "
        "removal of slow systems from the table.",
    )

    add_heading_custom(doc, "3.7 RQ mapping figure", level=2)
    add_figure(
        doc,
        FIGS / "fig3_rq_mapping.png",
        "Figure 3. Research questions mapped to frozen evidence sources.",
    )

    add_heading_custom(doc, "3.8 Ethics and safety in practice", level=2)
    add_para(
        doc,
        "No public honeypot; no host execution; no injection-string corpus in the "
        "repository; secrets never committed. GitHub: "
        f"{GITHUB}.",
    )


def section_results(doc):
    add_heading_custom(doc, "4. Results", level=1)
    add_para(
        doc,
        "Results are organised by study and then by RQ. Numbers match "
        "data/analysis/runs5/tables.md (Magazov ×5) and "
        "data/analysis/ubuntu_runs1/tables.md (Ubuntu ×1).",
        first_line=False,
    )

    add_heading_custom(doc, "4.1 Study A — Magazov 20 sessions × 5 runs", level=2)
    add_para(
        doc,
        "Command-row totals: Cowrie 350 OK; GPT-4o mini 350 skipped (no API key); "
        "Llama 86 OK / 264 errors (timeouts); Qwen 153 OK / 197 errors (timeouts). "
        "Table 3 summarises scored metrics.",
    )
    add_table(
        doc,
        ["System", "Logged", "OK", "Skipped", "Mean delay (s) [95% CI]",
         "Mean cmds completed", "Cost USD", "Technique labels"],
        [
            ["cowrie", "350", "350", "0", "0.37 [0.34, 0.40]", "3.50", "0.00", "8"],
            ["gpt-4o-mini", "350", "0", "350", "—", "—", "—", "8"],
            ["llama-3.1-8b", "350", "86", "0", "51.5 [42.5, 60.4]", "0.20", "0.00", "8"],
            ["qwen-2.5-7b", "350", "153", "0", "50.4 [44.9, 55.7]", "0.17", "0.00", "8"],
        ],
    )
    add_caption(
        doc,
        "Table 3. Magazov ×5 four-system comparison (fidelity blank — no Magazov GT join).",
    )

    add_table(
        doc,
        ["Comparison", "n pairs", "Statistic", "p-value", "Interpretation"],
        [
            ["cowrie vs gpt-4o-mini", "0", "—", "—", "All GPT skipped"],
            ["cowrie vs llama-3.1-8b", "100", "0.0", "≈1.14×10⁻¹⁶", "Cowrie higher cmds completed"],
            ["cowrie vs qwen-2.5-7b", "100", "0.0", "≈1.80×10⁻¹⁶", "Cowrie higher cmds completed"],
        ],
    )
    add_caption(doc, "Table 4. Wilcoxon signed-rank on Magazov commands_completed.")

    add_heading_custom(doc, "4.2 Study B — Ubuntu ground-truth fidelity (×1)", level=2)
    add_para(
        doc,
        "With Ubuntu ground truth present, fidelity becomes measurable. Table 5 is the "
        "key novelty evidence for realism improvement over the scripted baseline. Cowrie "
        "fidelity 0.00 is by design when scored against live Ubuntu container outputs. "
        "Local LLMs achieve non-zero fidelity (Llama 0.32; Qwen 0.40) on OK replies, "
        "despite remaining slow and often timing out.",
    )
    add_table(
        doc,
        ["System", "OK", "Skipped/Err", "Mean delay (s)", "Mean cmds completed",
         "Fidelity", "Consistency", "Invented content"],
        [
            ["cowrie", "200", "0", "0.26 [0.24, 0.27]", "10.00", "0.00", "0.14", "1.00"],
            ["gpt-4o-mini", "0", "200 skipped", "—", "—", "—", "—", "—"],
            ["llama-3.1-8b", "106", "94 err", "46.8 [40.3, 52.9]", "0.05", "0.32", "0.60", "0.64"],
            ["qwen-2.5-7b", "121", "79 err", "41.3 [36.1, 46.7]", "0.00", "0.40", "0.20", "0.57"],
        ],
    )
    add_caption(
        doc,
        "Table 5. Ubuntu ×1 fidelity study (GPT skipped). Fidelity is the RQ1 improvement signal.",
    )

    add_figure(
        doc,
        FIGS / "fig4_results_bars.png",
        "Figure 4. Magazov session survival (left) versus Ubuntu fidelity (right).",
    )

    add_heading_custom(doc, "4.3 RQ4 containment audit", level=2)
    add_para(doc, "Overall result: Passed (both Magazov and Ubuntu analysis folders).", first_line=False)
    add_table(
        doc,
        ["Check", "Result", "Detail"],
        [
            ["local_bind", "pass", "listen host is 127.0.0.1"],
            ["cowrie_localhost", "pass", "Cowrie host is 127.0.0.1"],
            ["ollama_localhost", "pass", "Ollama host is 127.0.0.1"],
            ["openai_host_pinned", "pass", "GPT text calls use api.openai.com only"],
            ["no_host_execution", "pass", "commands are not passed to the host OS"],
            ["no_honeypot_outbound", "pass", "the honeypot has no outbound channel"],
            ["text_only_output", "pass", "model output type is text"],
            ["no_model_tools", "pass", "the model is not given a tool"],
            ["source_has_no_host_shell", "pass", "session/replay source has no host shell / public bind"],
        ],
    )
    add_caption(
        doc,
        "Table 6. RQ4 containment checklist. Containment audit only; injection wording not stored.",
    )

    add_heading_custom(doc, "4.4 Results by research question", level=2)
    add_para(
        doc,
        "RQ1 (realism/consistency). On Ubuntu ground truth, Qwen fidelity 0.40 and Llama "
        "0.32 exceed Cowrie’s 0.00. Consistency was higher for Llama (0.60) than Qwen "
        "(0.20) or Cowrie (0.14) in the Ubuntu ×1 log. Invented-content rates remain "
        "substantial for LLMs (0.64 Llama; 0.57 Qwen), so realism gains are partial. "
        "Magazov Study A does not provide fidelity cells.",
    )
    add_para(
        doc,
        "RQ2 (time/cost). Cowrie mean delay ≈0.37 s (Magazov) / ≈0.26 s (Ubuntu). Local "
        "LLMs mean ≈41–52 s on OK replies and frequently hit TimeoutError. GPT-4o mini "
        "contributed no delay or cost numbers (all skipped). Local/Cowrie cost fields are "
        "0.00 where replies occurred.",
    )
    add_para(
        doc,
        "RQ3 (session survival / techniques). On Magazov, Cowrie mean commands completed "
        "3.50 >> Llama 0.20 and Qwen 0.17; Wilcoxon on 100 pairs strongly favours Cowrie. "
        "This report does not claim that LLMs beat Cowrie on Magazov session length. "
        "Eight Magazov technique labels are listed in the analysis vocabulary (discovery, "
        "cron, sudo, credential paths, ingress transfer, escape-to-host related labels). "
        "Ubuntu sessions used a benign-shell-check label set in that log.",
    )
    add_para(
        doc,
        "RQ4 (injection resistance as containment). Audit passed all checks. This answers "
        "the repository operationalisation of RQ4. It does not claim a scored jailbreak-"
        "string battery.",
    )
    add_para(
        doc,
        "Evidence that objectives were met. O1: fidelity/consistency reported from Ubuntu "
        "Study B. O2: delays and CIs reported; GPT cost blank because skipped. O3: "
        "commands completed + Wilcoxon + labels reported. O4: containment Passed + "
        "low-cost design recommendation in Section 5. Study_complete remains false while "
        "GPT is skipped — by design the four-row table is retained.",
    )


def section_discussion(doc):
    add_heading_custom(doc, "5. Discussion and evaluation", level=1)

    add_heading_custom(doc, "5.1 What the results show", level=2)
    add_para(
        doc,
        "Two complementary stories must not be collapsed into one slogan. On Magazov "
        "engagement under a strict 5-second break rule and CPU Ollama hardware, Cowrie "
        "is the only reliably fast multi-step backend. On Ubuntu fidelity, local LLMs "
        "are the systems that improve realism over scripted Cowrie. That split is the "
        "honest novelty framing: generative backends can look more like real Linux when "
        "scored against ground truth, but they do not automatically deliver longer Magazov "
        "sessions on a constrained laptop.",
    )

    add_heading_custom(doc, "5.2 Why one method is “better” depends on the metric", level=2)
    add_para(
        doc,
        "If the organisational goal is fast, stable decoy coverage and observable "
        "technique labels under replay, Cowrie wins on Magazov survival and delay. If the "
        "goal is reply realism versus real Ubuntu output, Qwen (0.40) and Llama (0.32) "
        "beat Cowrie (0.00). If the goal is privacy with no egress for inference, local "
        "Ollama models are preferable to GPT — but only if the machine can meet latency "
        "goals. GPT remains an empty row until a key is provisioned; keeping the skip is "
        "itself an organisational result.",
    )

    add_heading_custom(doc, "5.3 Comparison with literature", level=2)
    add_para(
        doc,
        "Magazov et al. (2026a) motivate careful backend benchmarking and note "
        "single-command evaluation gaps; this project’s multi-step Magazov ×5 design "
        "responds to that gap, while Ubuntu fidelity adds a ground-truth realism axis "
        "that Magazov traffic alone cannot provide. Generative honeypot systems "
        "(Sladić et al., 2023; 2024; Otal and Canbaz, 2024; Wang et al., 2026) show that "
        "LLM shells can be engaging in their own settings. Differences here — lower LLM "
        "session survival — are explained by hardware timeouts, the 5-second break "
        "threshold, and identical-session replay rather than live interactive attackers. "
        "The containment audit aligns with ethical closed-lab practice emphasised in the "
        "module handbook and UH ethics guidance (University of Hertfordshire, n.d.).",
    )

    add_heading_custom(doc, "5.4 Real-world application and design recommendation", level=2)
    add_para(
        doc,
        "Suitable applications: teaching/lab evaluation of honeypot backends; small "
        "organisations deciding between scripted SSH decoys and local LLM text shells; "
        "privacy-sensitive environments that refuse API egress. Design recommendation: "
        "keep Cowrie (or similar) for fast scripted coverage; add a text-only local LLM "
        "with session memory when realism against Linux-like output matters and hardware "
        "can sustain latency; use fixed denials for safety-critical categories; bind only "
        "to localhost unless a separate ethically approved deployment exists; never "
        "execute model-suggested commands on the host.",
    )

    add_heading_custom(doc, "5.5 Objectives and research questions — verdict", level=2)
    add_para(
        doc,
        "The results answer the stated RQs with honest splits: fidelity improvement is "
        "real on Ubuntu GT; Magazov session-length superiority for LLMs is not claimed; "
        "delay/cost evidence is partial because GPT was skipped; containment passed. That "
        "is sufficient to meet the project objectives without fabricating missing GPT or "
        "GPU-accelerated numbers.",
    )


def section_limitations(doc):
    add_heading_custom(doc, "6. Limitations", level=1)
    add_para(
        doc,
        "1) Isolated lab only — not a public honeypot; limited external validity to live "
        "internet attackers. 2) Local model CPU/RAM timeouts — understate what the same "
        "7–8B models might achieve on GPU/larger RAM; inflate breaks under the 5 s rule. "
        "3) GPT-4o mini skipped — no API key during Magazov ×5 and Ubuntu ×1; commercial "
        "delay/cost blank. 4) Cowrie fidelity 0.00 on Ubuntu GT by design — scripted "
        "emulator versus container outputs; do not misread as “Cowrie produced no replies” "
        "(it produced 200 OK replies). 5) RQ4 = containment audit — not a published "
        "injection-string benchmark. 6) Ubuntu fidelity study is ×1 run — weaker than "
        "Magazov’s five-run engagement package for consistency CIs. 7) Single student "
        "laptop / Ollama contention — do not claim production scale.",
        first_line=False,
    )


def section_conclusion(doc):
    add_heading_custom(doc, "7. Conclusion and future enhancement", level=1)
    add_para(
        doc,
        "RQ1: Against Ubuntu ground truth, local LLMs improve fidelity over Cowrie "
        "(Qwen 0.40, Llama 0.32 versus Cowrie 0.00), with remaining invented-content risk. "
        "RQ2: Cowrie is fast; local LLMs are slow/timeout-limited on this hardware; GPT "
        "provided no delay/cost data (skipped). RQ3: On Magazov, Cowrie completes far more "
        "commands before break than Llama or Qwen; LLMs are not claimed to beat Cowrie on "
        "session length. RQ4: Containment audit passed (localhost, text-only, no tools, "
        "no host execution).",
    )
    add_para(
        doc,
        "Contributions C1–C4 are evidenced in the public repository and freeze analyses. "
        "The practical recommendation is a hybrid posture: scripted speed from Cowrie, "
        "optional local LLM text realism when hardware allows, strict containment always.",
    )
    add_para(
        doc,
        "Future enhancement. (1) Re-run local models on GPU or higher-RAM hosts to test "
        "whether Magazov session survival rises once delays fall under 5 s. (2) Complete a "
        "keyed GPT-4o mini replay into a separate log so commercial delay/cost enter the "
        "four-row table. (3) Expand Ubuntu ground-truth runs beyond ×1 for stronger "
        "consistency intervals. (4) Optional ethically approved, separately governed "
        "deployment study — outside this closed-lab scope. (5) Further prompt/history "
        "tuning once latency is hardware-solved.",
    )


def section_references(doc):
    add_heading_custom(doc, "References", level=1)
    refs = [
        "Cowrie Project (n.d.) Cowrie SSH/Telnet honeypot [Online]. Available at: https://github.com/cowrie/cowrie (Accessed: 14 November 2026).",
        "Javadpour, A., et al. (2024) ‘A survey of cyber deception and honeypot performance’, Computers & Security, 140, 103792. Available at: https://doi.org/10.1016/j.cose.2024.103792",
        "Magazov, R., et al. (2026a) ‘Benchmarking LLM backends for generative SSH honeypots’, AI, 7(8), 287. Available at: https://doi.org/10.3390/ai7080287",
        "Magazov, R., Abeshev, K., Shamuratov, Y., Uralova, F. and Aksholak, G. (2026b) De-identified SSH honeypot attacker corpus [Dataset]. Zenodo. Available at: https://doi.org/10.5281/zenodo.20816078 (CC BY 4.0).",
        "Otal, H. and Canbaz, M.A. (2024) ‘LLM honeypot: monitoring AI jailbreaks… interactive honeypot systems’, IEEE Conference on Communications and Network Security (CNS). arXiv:2409.08234. Available at: https://arxiv.org/abs/2409.08234 (see also IEEE Xplore 10735607).",
        "Sladić, M., et al. (2023) ‘LLM in the shell: generative honeypots’. arXiv:2309.00155. Available at: https://arxiv.org/abs/2309.00155",
        "Sladić, M., et al. (2024) Generative honeypot evaluation paper, IEEE European Symposium on Security and Privacy Workshops (EuroS&PW). Available at: https://doi.org/10.1109/EuroSPW61312.2024.00054",
        "University of Hertfordshire (n.d.) Ethics approval information [Online]. Available at: https://ask.herts.ac.uk/ethics-approval (Accessed: 14 November 2026).",
        "Wang, et al. (2026) ‘HoneyGPT…’, Computer Networks, 282, 112223. Available at: https://doi.org/10.1016/j.comnet.2026.112223 (also arXiv:2406.01882 as cited in the project PDM).",
    ]
    for r in refs:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.left_indent = Cm(0.75)
        p.paragraph_format.first_line_indent = Cm(-0.75)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(r)
        set_run_font(run, size=10)


def section_appendices(doc):
    add_heading_custom(doc, "Appendix A — Reproduce analysis (no Magazov re-run required)", level=1)
    add_para(
        doc,
        "python scripts/05_analyse.py --log data\\logs\\replay_magazov_20sess_runs5.jsonl "
        "--out-dir data\\analysis\\runs5",
        first_line=False, italic=True,
    )
    add_para(
        doc,
        "python scripts/05_analyse.py --log data\\logs\\replay_ubuntu_testset_runs1.jsonl "
        "--out-dir data\\analysis\\ubuntu_runs1",
        first_line=False, italic=True,
    )

    add_heading_custom(doc, "Appendix B — Selected code path (text)", level=1)
    add_para(
        doc,
        "Core flow (names only): scripts/04_replay.py → src/backends.py (Cowrie / OpenAI / "
        "Ollama text backends) → src/session_memory.py (structured state, no host shell) → "
        "JSONL logs → scripts/05_analyse.py → src/analyse.py + src/containment.py. Full "
        f"source is on GitHub: {GITHUB}. Do not paste secrets or .env contents into the FPR.",
        first_line=False,
    )

    add_heading_custom(doc, "Appendix C — Freeze pointers", level=1)
    add_para(
        doc,
        "Magazov freeze analysis: data/analysis/runs5/ (tables.md, summary.json, "
        "rq4_containment.json). Ubuntu fidelity: data/analysis/ubuntu_runs1/. Practical "
        "freeze day: 14 November 2026. Report due: 20 November 2026. Viva: 23 November 2026.",
        first_line=False,
    )


def estimate_word_count(doc: Document) -> int:
    texts = []
    for p in doc.paragraphs:
        texts.append(p.text)
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                texts.append(cell.text)
    blob = "\n".join(texts)
    # Exclude front matter roughly by counting after Abstract heading if present
    words = re.findall(r"\b[\w'-]+\b", blob)
    return len(words)


def write_md_backup():
    md = f"""# Generative AI Deception: Dynamic LLM-Powered Honeypots

**Student:** Patil Devyani Anil (ID 5034)  
**Module:** 7FTC2001 · MSc Data Science FT · Supervisor: Dr Rama Abirami K  
**GitHub:** {GITHUB}  
**Draft date:** 14 November 2026 (freeze day) · **Due:** 20 November 2026  

*Markdown backup of the Word FPR draft. Edit the .docx for Blackboard; rewrite in your own voice before Turnitin.*

## Abstract (see .docx)

Four systems (Cowrie, GPT-4o mini, Llama 3.1 8B, Qwen 2.5 7B) compared on Magazov ×5 and Ubuntu fidelity ×1. Magazov: Cowrie mean cmds 3.50 vs Llama 0.20 / Qwen 0.17; GPT skipped. Ubuntu fidelity: Cowrie 0.00, Llama 0.32, Qwen 0.40. RQ4 containment Passed. Do not claim LLMs beat Cowrie on Magazov session length.

## Figures

- `report_figures/fig1_architecture.png`
- `report_figures/fig2_method_pipeline.png`
- `report_figures/fig3_rq_mapping.png`
- `report_figures/fig4_results_bars.png`

## Key tables

See Word document Tables 1–6 and analysis folders `data/analysis/runs5/` and `data/analysis/ubuntu_runs1/`.
"""
    MD_BACKUP.write_text(md, encoding="utf-8")


def main():
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.2)
    section.right_margin = Cm(2.2)

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")

    # Page numbers
    footer = section.footer
    footer.is_linked_to_previous = False
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = fp.add_run("Patil Devyani Anil (5034) — FPR Draft — Page ")
    set_run_font(run, size=9)
    # simple PAGE field
    fld = run._element
    # add page number via XML
    from docx.oxml import OxmlElement

    def add_page_number(paragraph):
        run1 = paragraph.add_run()
        set_run_font(run1, size=9)
        r = run1._r
        fldChar1 = OxmlElement("w:fldChar")
        fldChar1.set(qn("w:fldCharType"), "begin")
        instrText = OxmlElement("w:instrText")
        instrText.text = " PAGE "
        fldChar2 = OxmlElement("w:fldChar")
        fldChar2.set(qn("w:fldCharType"), "end")
        r.append(fldChar1)
        r.append(instrText)
        r.append(fldChar2)

    add_page_number(fp)

    front_page(doc)
    declaration_page(doc)
    abstract_and_keywords(doc)
    section_introduction(doc)
    section_literature(doc)
    section_methods(doc)
    section_results(doc)
    section_discussion(doc)
    section_limitations(doc)
    section_conclusion(doc)
    section_references(doc)
    section_appendices(doc)

    wc = estimate_word_count(doc)
    # update word count note on a final para
    add_para(
        doc,
        f"Document word-count estimate (all paragraphs/tables including front matter): "
        f"approximately {wc} words. Module maximum ~7500 for the report body — trim or "
        f"expand during personal editing as needed.",
        size=9, italic=True, first_line=False, space_before=12,
    )

    doc.save(OUT)
    shutil.copy2(OUT, OUT_DL)
    write_md_backup()
    print("WORD_COUNT_ESTIMATE", wc)
    print("WROTE", OUT)
    print("COPIED", OUT_DL)
    print("MD", MD_BACKUP)


if __name__ == "__main__":
    main()
