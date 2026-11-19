"""
Build Final Project Report DOCX for Blackboard (7FTC2001 / FPR template).
Calibri 12, justified body, separate comparison figures, Harvard refs.
No secrets. No attack payloads.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(r"C:\Users\devyani patil\honeypot")
FIGS = ROOT / "report_figures"
OUT_MAIN = ROOT / "Final_Report_Patil_Devyani_5034.docx"
OUT_DL = Path(r"C:\Users\devyani patil\Downloads\Final_Report_Patil_Devyani_5034.docx")
OUT_DL_REVISED = Path(
    r"C:\Users\devyani patil\Downloads\Final_Report_Patil_Devyani_5034_revised.docx"
)
OUT_MD = ROOT / "Final_Report_Patil_Devyani_5034.md"

GITHUB = "https://github.com/itsdivined/synthshell-honeypot"
DATASET_DOI = "https://doi.org/10.5281/zenodo.20816078"


def set_run_font(run, size=12, bold=False, italic=False, color=None, name="Calibri"):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def justify(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf = paragraph.paragraph_format
    pf.space_after = Pt(8)
    pf.space_before = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE


def add_body(doc, text, size=12):
    p = doc.add_paragraph()
    justify(p)
    run = p.add_run(text)
    set_run_font(run, size=size)
    return p


def add_heading_custom(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        set_run_font(
            run,
            size=14 if level == 1 else 12,
            bold=True,
            color=RGBColor(0x1F, 0x4E, 0x79),
        )
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(6)
    return h


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(12)
    run = p.add_run(text)
    set_run_font(run, size=10, italic=True)
    return p


def add_figure(doc, path: Path, width_in: float, caption: str):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(path), width=Inches(width_in))
    add_caption(doc, caption)


def add_bullet(doc, text):
    p = doc.add_paragraph(style="List Number")
    justify(p)
    p.clear()
    run = p.add_run(text)
    set_run_font(run, size=12)
    return p


def style_table(table):
    table.autofit = True
    for i, row in enumerate(table.rows):
        for cell in row.cells:
            for para in cell.paragraphs:
                para.paragraph_format.space_after = Pt(2)
                para.paragraph_format.space_before = Pt(2)
                for run in para.runs:
                    set_run_font(run, size=9, bold=(i == 0))
            if i == 0:
                shading = OxmlElement("w:shd")
                shading.set(qn("w:fill"), "1F4E79")
                shading.set(qn("w:val"), "clear")
                cell._tc.get_or_add_tcPr().append(shading)
                for para in cell.paragraphs:
                    for run in para.runs:
                        run.font.color.rgb = RGBColor(255, 255, 255)
                        run.bold = True


def add_table(doc, headers, rows, caption: str):
    add_caption(doc, caption)
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    for j, h in enumerate(headers):
        table.rows[0].cells[j].text = h
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            table.rows[i + 1].cells[j].text = str(val)
    style_table(table)
    doc.add_paragraph()
    return table


def add_page_number_only(footer):
    """Footer: page number only (no name/title)."""
    # Clear existing footer paragraphs
    for p in list(footer.paragraphs):
        p.clear()
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fld1 = OxmlElement("w:fldChar")
    fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld2 = OxmlElement("w:fldChar")
    fld2.set(qn("w:fldCharType"), "end")
    run = p.add_run()
    set_run_font(run, size=10)
    run._r.append(fld1)
    run._r.append(instr)
    run._r.append(fld2)


def add_hyperlink(paragraph, text, url):
    part = paragraph.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0563C1")
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), "24")
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), "Calibri")
    rFonts.set(qn("w:hAnsi"), "Calibri")
    rPr.append(rFonts)
    rPr.append(color)
    rPr.append(u)
    rPr.append(sz)
    new_run.append(rPr)
    text_elem = OxmlElement("w:t")
    text_elem.text = text
    new_run.append(text_elem)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)


def front_page(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("UNIVERSITY OF HERTFORDSHIRE")
    set_run_font(r, size=14, bold=True, color=RGBColor(0x1F, 0x4E, 0x79))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("School of Physics, Engineering and Computer Science")
    set_run_font(r, size=12, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("MSc Data Science Project")
    set_run_font(r, size=12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("7FTC2001 · Department of Physics, Astronomy and Mathematics")
    set_run_font(r, size=12)

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Data Science FINAL PROJECT REPORT")
    set_run_font(r, size=16, bold=True, color=RGBColor(0x1F, 0x4E, 0x79))

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Project Title:")
    set_run_font(r, size=12, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Generative AI Deception: Dynamic LLM-Powered Honeypots")
    set_run_font(r, size=14, bold=True, color=RGBColor(0x0D, 0x47, 0xA1))

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Student Name and SRN:")
    set_run_font(r, size=12, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Patil Devyani Anil · Student ID 5034")
    set_run_font(r, size=12)

    doc.add_paragraph()
    for label, value in [
        ("Supervisor:", "Dr Rama Abirami K."),
        ("Date Submitted:", "20 November 2026"),
        ("Word Count:", "[TO BE FILLED AFTER BUILD]"),
        ("GitHub address:", GITHUB),
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p.add_run(label + " ")
        set_run_font(r1, size=12, bold=True)
        if label.startswith("GitHub"):
            add_hyperlink(p, value, value)
        else:
            r2 = p.add_run(value)
            set_run_font(r2, size=12)

    doc.add_page_break()


def declaration_page(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("DECLARATION STATEMENT")
    set_run_font(r, size=14, bold=True, color=RGBColor(0x1F, 0x4E, 0x79))

    texts = [
        "This report is submitted for the MSc in Data Science at the University of Hertfordshire. "
        "I confirm that I have read and understood the University guidance on academic integrity, "
        "academic misconduct, and plagiarism.",
        "I certify that this report is my own original work except where properly referenced. "
        "Where generative AI or coding assistants were used for drafting support, editing, or "
        "figure layout code, this is declared here: drafting assistance and matplotlib figure "
        "scripts were used under supervision of my own experimental results, analysis tables, "
        "and design decisions. I will revise the wording into my own voice before Turnitin "
        "submission.",
        "I confirm that no human participants or surveys were used in this project. The study "
        "is a closed-lab technical evaluation on localhost (127.0.0.1) using a public "
        "de-identified corpus and locally captured Ubuntu ground-truth outputs.",
        "I give permission for this report to be made available on module websites as required "
        "by the University of Hertfordshire assessment process.",
    ]
    for t in texts:
        add_body(doc, t)

    doc.add_paragraph()
    for line in [
        "Student SRN number: 5034",
        "Student Name printed: Patil Devyani Anil",
        "Student signature: _______________________________",
        "Date: 20 November 2026",
    ]:
        p = doc.add_paragraph()
        r = p.add_run(line)
        set_run_font(r, size=12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(
        "UNIVERSITY OF HERTFORDSHIRE, SCHOOL OF PHYSICS, ENGINEERING AND COMPUTER SCIENCE"
    )
    set_run_font(r, size=9, italic=True)
    doc.add_page_break()


def add_ref(doc, text):
    p = doc.add_paragraph()
    justify(p)
    p.paragraph_format.left_indent = Cm(0.75)
    p.paragraph_format.first_line_indent = Cm(-0.75)
    r = p.add_run(text)
    set_run_font(r, size=11)


def build():
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(2.2)
    section.bottom_margin = Cm(2.2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(12)
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    add_page_number_only(section.footer)

    front_page(doc)
    declaration_page(doc)

    # Abstract — no other authors' names; include output/accuracy numbers
    add_heading_custom(doc, "Abstract", 1)
    abstract = (
        "Static SSH honeypots are easy for scanners to fingerprint, so they often collect less "
        "useful attacker intelligence than a defender needs. This closed-lab, localhost-only "
        "study built a replay-based evaluation lab comparing four systems—Cowrie, GPT-4o mini, "
        "Llama 3.1 8B, and Qwen 2.5 7B—on identical multi-step sessions from a public "
        "de-identified SSH attacker corpus and an Ubuntu ground-truth test set. Pretrained "
        "LLMs reproduced real Ubuntu behaviour better than the scripted honeypot on fidelity "
        "(Qwen 0.40, Llama 0.32, Cowrie 0.00), yet neither local model approached perfect "
        "fidelity (1.0). On the shared multi-step attacker-session slice, Cowrie still led "
        "mean commands completed before a defined break (about 3.50 versus about 0.20 for "
        "Llama and 0.17 for Qwen); GPT-4o mini was skipped (no API key). An exploratory "
        "character "
        "TF-IDF plus logistic regression reply-source detector achieved binary accuracy "
        "0.758, macro-F1 0.750 and AUROC 0.875, and 3-way accuracy 0.694, macro-F1 0.682 "
        "and OvR-AUROC 0.888 (per-class F1: Cowrie 0.739, Ubuntu 0.708, LLM 0.600). "
        "Containment checks for localhost bind, text-only output and no host execution "
        "passed. The results support a design trade-off: Cowrie for speed and persistence; "
        "local LLMs for higher text fidelity when hardware allows; containment-first "
        "deployment on 127.0.0.1 only. Fidelity gains do not equal fooling a real attacker; "
        "next steps include fine-tuning, controlled live deployment, and more models."
    )
    add_body(doc, abstract)
    p = doc.add_paragraph()
    justify(p)
    r = p.add_run("Keywords: ")
    set_run_font(r, size=12, bold=True)
    r2 = p.add_run(
        "honeypot; large language model; Cowrie; session survival; deception; containment; "
        "reply-source detection; cybersecurity evaluation"
    )
    set_run_font(r2, size=12, italic=True)

    add_heading_custom(doc, "Contents", 1)
    for item in [
        "1. Introduction",
        "2. Research Questions and Objectives",
        "3. Literature Review",
        "4. Methodology and Practical Work",
        "5. Results",
        "6. Discussion and Evaluation",
        "7. Limitations",
        "8. Conclusion and Future Enhancements",
        "References",
        "Appendix A. Repository and reproduction",
        "Appendix B. Backup of code and data",
    ]:
        p = doc.add_paragraph()
        r = p.add_run(item)
        set_run_font(r, size=12)

    # 1 Introduction
    add_heading_custom(doc, "1. Introduction", 1)
    add_body(
        doc,
        "Attackers routinely probe SSH services to discover weak credentials, map host "
        "configuration, and stage further activity. Defenders deploy honeypots—decoy systems "
        "that appear vulnerable—to observe reconnaissance without exposing production hosts "
        "(Javadpour et al., 2024). The practical problem is blunt: static, scripted honeypots "
        "are easy to detect, so experienced scanners leave early and the defender collects "
        "less intelligence. Traditional medium-interaction systems such as Cowrie emulate a "
        "Unix shell with fixed replies and a fake filesystem (Cowrie Project, n.d.). They are "
        "reliable and inexpensive to run, but that fixed behaviour is also what makes them "
        "fingerprintable. Generative models offer a different deception strategy: an LLM can "
        "invent plausible shell output for almost any command. That flexibility, however, "
        "brings risks of inconsistency across turns, invented paths or users, slow local "
        "inference, instruction leakage, and dependence on commercial APIs that export "
        "session text.",
    )
    add_body(
        doc,
        "Recent studies have demonstrated LLM-backed honeypots and reported encouraging "
        "engagement or human-judged realism (Sladić et al., 2024; Otal and Canbaz, 2024; "
        "Wang et al., 2026; Magazov et al., 2026a). What remains scarce is a repeatable, "
        "multi-step, multi-backend laboratory comparison in which Cowrie and several LLMs "
        "receive identical sessions, with shared metrics for fidelity, delay, session "
        "survival until a defined break, an exploratory machine-learning view of reply "
        "detectability, and a clear containment posture. Field deployments and "
        "single-command tests are hard for a student or small organisation to rerun under "
        "controlled conditions. Empirically, the gap this lab measures is also incomplete "
        "rather than closed: on Ubuntu ground truth, Cowrie fidelity was 0.00 while Llama "
        "reached 0.32 and Qwen 0.40 (Table 4)—better than the scripted baseline, but neither "
        "close to 1.0, so there is substantial room to improve before claiming "
        "attacker-grade deception.",
    )
    add_body(
        doc,
        "This project addresses that measurement gap in an isolated laptop laboratory. All "
        "SSH and model endpoints bind to 127.0.0.1. Models return text only; they receive "
        "structured session memory (current working directory, file and user deltas) but no "
        "tools and no host shell execution (Paramiko Project, n.d.; Ollama, n.d.; OpenAI, "
        "n.d.). Figure 1 shows the system architecture used throughout the study.",
    )
    add_figure(
        doc,
        FIGS / "fig1_architecture.png",
        6.2,
        "Figure 1. System architecture for the four-backend localhost honeypot lab "
        "(Cowrie, GPT-4o mini, Llama 3.1 8B, Qwen 2.5 7B) with session memory and analysis path.",
    )
    add_body(
        doc,
        "The aim is to measure how realistic, consistent, and cost-effective an LLM honeypot "
        "is compared with a traditional honeypot, how detectable honeypot replies are with a "
        "lightweight classifier, and which backend type gives the best balance for a "
        "low-cost defender. Novelty is claimed in the measurement design—not in inventing "
        "the first LLM honeypot. Contributions are: (C1) a working prototype with "
        "session-state memory on a standard SSH front end; (C2) an Ubuntu ground-truth test "
        "set joined to replay logs; (C3) a controlled four-system comparison on Magazov and "
        "Ubuntu sessions; (C4) an exploratory TF-IDF plus logistic regression reply-source "
        "detector, plus an RQ4 containment audit; (C5) a reusable comparison harness so "
        "others can plug in a new model via .env (LLAMA_MODEL / QWEN_MODEL or "
        "EXTRA_OLLAMA_MODELS) and re-run the same sessions and metrics (docs/REUSE.md). "
        "Self-developed elements emphasised for marking are the replay pipeline, session "
        "memory, metrics/analysis scripts, and the detector—built on Cowrie and public "
        "Magazov data rather than replacing those foundations. Scope is explicitly "
        "closed-lab: this is not a public honeypot deployment, and no attack payloads are "
        "reproduced in this report.",
    )
    add_body(
        doc,
        "In one line: pretrained LLMs improve Ubuntu text fidelity over Cowrie (Qwen 0.40, "
        "Llama 0.32 vs 0.00) while Magazov session length still favours Cowrie, and a "
        "lightweight detector separates reply sources above chance but not perfectly. The "
        "remainder of the report follows the module Final Project Report expectations "
        "(University of Hertfordshire, 2024): clear specifications and ethics (this section "
        "and Section 2), a critical literature review (Section 3), practical methods with "
        "dataset provenance (Section 4), results with multiple justified metrics (Section 5), "
        "evaluation against objectives and literature (Section 6), limitations (Section 7), "
        "and conclusions with future work (Section 8). Figures and tables are numbered, "
        "captioned, and cited in the body text. Harvard references appear at the end.",
    )
    add_heading_custom(doc, "1.1 Ethical considerations", 2)
    add_body(
        doc,
        "Ethics approval for this module pathway was completed via the University of "
        "Hertfordshire ethics quiz on 27 October 2026 (University of Hertfordshire, n.d.). "
        "The four ethics themes from the project data-management plan are answered as "
        "follows. (1) Human participants: none; no surveys or interviews. (2) Personal "
        "data: the Magazov corpus is published as de-identified SSH attacker commands under "
        "CC BY 4.0 (Magazov et al., 2026b); an IP screen reported zero public addresses "
        "needing review in the downloaded slice. (3) Harm and dual-use: the repository does "
        "not store injection/jailbreak payload lists; RQ4 is operationalised as a "
        "containment audit (localhost bind, text-only output, no host execution). "
        "(4) Deployment risk: all services listen on 127.0.0.1 only; there is no live "
        "attacker traffic and no public bind. API keys, if used, remain in a gitignored "
        ".env file and are not present in this report.",
    )
    add_heading_custom(doc, "1.2 Project difficulty", 2)
    add_body(
        doc,
        "Difficulty arose from integrating heterogeneous backends (SSH Cowrie via Paramiko, "
        "OpenAI text API, local Ollama), enforcing containment in code rather than "
        "documentation alone, scoring multi-step breaks with bootstrap confidence intervals "
        "and Wilcoxon tests (Wilcoxon, 1945; Efron and Tibshirani, 1993), capturing Ubuntu "
        "ground truth offline (Canonical Ltd, n.d.), training an exploratory reply-source "
        "detector with session-grouped splits (Pedregosa et al., 2011), and running "
        "multi-hour Magazov ×5 replays on a RAM-limited laptop where local 7–8B models "
        "frequently timed out. These constraints are reported honestly rather than removed "
        "from the study design.",
    )

    # 2 RQs — exactly four; RQ3 replaced (old techniques/session-break RQ → detector)
    add_heading_custom(doc, "2. Research Questions and Objectives", 1)
    add_body(
        doc,
        "Exactly four research questions and four matching objectives structure the "
        "practical work. Evidence mapping is summarised in Figure 3 later in the methods "
        "section. A session break is defined once and reused for Magazov engagement "
        "reporting: empty reply; wrong or contradictory reply; AI self-disclosure; or delay "
        "above 5 seconds. The previous session-technique / ATT&CK-style logging question "
        "was replaced by a detectability question so the report includes a clear machine-"
        "learning contribution aligned with the Data Science module, while Magazov session "
        "length remains reported as complementary engagement evidence under RQ1.",
    )
    add_body(doc, "The four research questions are:")
    add_bullet(
        doc,
        "RQ1: How realistic and consistent are LLM honeypot replies compared with real "
        "Linux output?",
    )
    add_bullet(
        doc,
        "RQ2: How do the three LLMs compare on response time and cost?",
    )
    add_bullet(
        doc,
        "RQ3: To what extent can a lightweight TF-IDF logistic regression detector "
        "distinguish real Ubuntu command replies from Cowrie and LLM honeypot replies?",
    )
    add_bullet(
        doc,
        "RQ4: How well does each LLM honeypot resist prompt injection under a "
        "containment-first design?",
    )
    add_table(
        doc,
        ["ID", "Research question", "Objective"],
        [
            [
                "RQ1",
                "How realistic and consistent are LLM honeypot replies compared with real Linux output?",
                "O1. Measure fidelity and multi-step consistency on ~200 commands / ~20 sessions with Ubuntu ground truth; report Magazov session-length contrast as engagement context.",
            ],
            [
                "RQ2",
                "How do the three LLMs compare on response time and cost?",
                "O2. Record delay per command and cost per session (local/Cowrie costed at £0 API when they reply).",
            ],
            [
                "RQ3",
                "To what extent can a lightweight TF-IDF logistic regression detector distinguish real Ubuntu command replies from Cowrie and LLM honeypot replies?",
                "O3. Train and evaluate an exploratory char TF-IDF (3–5) + balanced logistic regression detector on joined Ubuntu/honeypot reply text; report accuracy, macro-F1, AUROC and per-class F1.",
            ],
            [
                "RQ4",
                "How well does each LLM honeypot resist prompt injection under a containment-first design?",
                "O4. Run a containment audit (not a stored injection corpus) and recommend a low-cost design.",
            ],
        ],
        "Table 1. Four research questions and matching objectives for the final project.",
    )
    add_body(
        doc,
        "Table 1 shows the four RQs that every later result section answers. RQ3 replaces "
        "the earlier technique-label / session-break primary question, which was weakly "
        "differentiated in freeze tables (all systems logged the same label count). RQ4 "
        "wording follows the project plan’s injection-resistance intent, but the "
        "implemented evidence is a containment audit aligned with ethics constraints "
        "(no attack-string lists in the repository).",
    )

    # 3 Literature
    add_heading_custom(doc, "3. Literature Review", 1)
    add_body(
        doc,
        "Papers were selected if they directly inform honeypot evaluation, generative "
        "SSH/shell deception, reply detectability, or the Magazov corpus and benchmarks "
        "used in this lab. The set mixes a deception survey, generative honeypot systems, "
        "a 2026 LLM-backend benchmark, the public Magazov dataset, Cowrie as the scripted "
        "baseline, and documentation for tools actually used in the implementation. Each "
        "subsection describes purpose, data/methods, strengths and limits, and how the "
        "source shaped this project.",
    )
    add_heading_custom(doc, "3.1 Traditional honeypots and deception evaluation", 2)
    add_body(
        doc,
        "Javadpour et al. (2024) survey cyber deception and honeypot performance metrics, "
        "emphasising that realism and evaluation design matter as much as deployment "
        "volume. Their purpose is to organise how defenders measure deception systems; "
        "they draw on a wide secondary literature rather than releasing a single SSH "
        "replay harness. Strength: broad framing of why engagement quality, detection "
        "risk, and operational cost should be discussed together. Limitation: survey "
        "breadth rather than a reproducible multi-backend protocol a student can rerun "
        "on one laptop. This project uses that framing to justify measuring fidelity, "
        "delay, detectability, and session survival under identical inputs, instead of "
        "reporting only a qualitative demo. Cowrie (Cowrie Project, n.d.) remains the "
        "de-facto open-source medium-interaction SSH honeypot (BSD-3-Clause). Strength: "
        "stable scripted baseline, configurable fake filesystem, and mature logging. "
        "Limitation: fixed replies enable fingerprinting by scanners that probe for "
        "inconsistencies. Cowrie is therefore System 1 in every table here, including "
        "when LLM rows are skipped or timed out.",
    )
    add_heading_custom(doc, "3.2 Generative and LLM honeypots", 2)
    add_body(
        doc,
        "Sladić et al. (2023; 2024) present generative honeypot evaluation culminating in "
        "a peer-reviewed EuroS&PW paper, building on earlier “LLM in the shell” ideas. "
        "Purpose: show that generative models can sustain more natural shell interaction "
        "than purely scripted decoys. Strength: human/realism discussion for generative "
        "shells with clear deception framing. Limitation: not a four-system Magazov-style "
        "paired multi-step student lab with bootstrap CIs, Wilcoxon tests, and an "
        "auxiliary reply-source classifier on the same sessions. Otal and Canbaz (2024) "
        "describe interactive LLM honeypot systems. Strength: end-to-end interactivity "
        "and system-building detail. Limitation for academic replication: field-style "
        "evaluation that a marker cannot easily rerun under identical saved sessions. "
        "Wang et al. (2026) (HoneyGPT) discuss LLM terminal honeypots and engagement in "
        "Computer Networks. Strength: engagement-oriented analysis that motivates "
        "measuring how long a session continues before the decoy fails. Limitation: "
        "published field conditions differ from a controlled localhost replay with fixed "
        "break rules. Magazov et al. (2026a) benchmark LLM backends for generative SSH "
        "honeypots and note single-command sessions among remaining gaps—directly "
        "motivating this project’s multi-step paired design. Magazov et al. (2026b) "
        "release the de-identified corpus used as shared traffic here under CC BY 4.0.",
    )
    add_heading_custom(doc, "3.3 Detectability and tooling used in this lab", 2)
    add_body(
        doc,
        "Beyond generative honeypot systems, this study needs a transparent classical "
        "machine-learning baseline for reply-source detection. Pedregosa et al. (2011) "
        "document scikit-learn’s TF-IDF vectorisers and logistic regression estimators, "
        "which underpin the exploratory detector (scikit-learn developers, n.d.). The "
        "implementation also relies on Paramiko for the Cowrie SSH client path "
        "(Paramiko Project, n.d.), Ollama for local Llama/Qwen inference (Ollama, n.d.), "
        "and the OpenAI HTTP API for optional GPT-4o mini text calls (OpenAI, n.d.). "
        "Ubuntu ground truth was captured against a clean containerised Linux environment "
        "(Canonical Ltd, n.d.). These citations are included because the tools were "
        "actually used in code and evaluation, not as decorative bibliography padding.",
    )
    add_heading_custom(doc, "3.4 Positioning this work", 2)
    add_body(
        doc,
        "Relative to the literature, this study does not claim a new foundational LLM "
        "architecture or the first generative honeypot. It contributes a reusable "
        "closed-lab evaluation protocol: identical sessions to Cowrie and three LLMs; "
        "session memory without host execution; bootstrap CIs and Wilcoxon tests; "
        "Ubuntu fidelity when ground truth exists; an exploratory TF-IDF + logistic "
        "regression detector for reply detectability; and RQ4 as containment rather than "
        "a published jailbreak battery. The harness keeps the same sessions and metrics "
        "so another model can be plugged in via configuration and compared the same way: "
        "swap an existing Ollama tag with LLAMA_MODEL or QWEN_MODEL in .env, or append a "
        "new local model with EXTRA_OLLAMA_MODELS (documented in docs/REUSE.md), then "
        "re-run scripts/04_replay.py and scripts/05_analyse.py on the same session file. "
        "Results are interpreted against Magazov-style engagement concerns and "
        "HoneyGPT-style realism/engagement trade-offs, with honest hardware limits. Where "
        "prior work reports strong live engagement, this report instead reports what a "
        "resource-constrained student lab can measure repeatably—and where Cowrie still "
        "wins on persistence while remaining more stereotyped under a bag-of-character-"
        "ngrams detector.",
    )

    # 4 Methods
    add_heading_custom(doc, "4. Methodology and Practical Work", 1)
    add_body(
        doc,
        "This section describes what was implemented in the synthshell-honeypot repository. "
        "It is not a general essay on research philosophy. Figure 2 summarises the pipeline "
        "from corpus download to analysis and the exploratory detector.",
    )
    add_figure(
        doc,
        FIGS / "fig2_method_pipeline.png",
        6.2,
        "Figure 2. Method pipeline: Magazov download and screen, Ubuntu ground-truth check, "
        "four-system replay, analysis metrics, and exploratory detector branch.",
    )

    add_heading_custom(doc, "4.1 Systems under test", 2)
    add_table(
        doc,
        ["System", "Role", "Access / notes"],
        [
            ["Cowrie", "Scripted baseline", "SSH on 127.0.0.1:2222 (WSL/local)"],
            ["GPT-4o mini", "Commercial API", "Text-only OpenAI call; skipped if no OPENAI_API_KEY"],
            ["Llama 3.1 8B", "Local open-weight", "Ollama llama3.1:8b on 127.0.0.1:11434"],
            ["Qwen 2.5 7B", "Local open-weight", "Ollama qwen2.5:7b on 127.0.0.1:11434"],
        ],
        "Table 2. Four systems retained in every comparison table (skips remain as rows).",
    )
    add_body(
        doc,
        "Table 2 lists the four systems. Safety-critical categories (for example sudo or "
        "password-file reads) receive a fixed denial before any LLM call. Session memory "
        "stores cwd and file/user deltas as text context only. The backend interface is "
        "intentionally thin: a new model (local or API) can be registered beside the "
        "existing four, then re-run against the same session lists and analysis scripts "
        "so fidelity, delay, and survival remain comparable.",
    )

    add_heading_custom(doc, "4.2 Datasets", 2)
    p = doc.add_paragraph()
    justify(p)
    r = p.add_run(
        "Primary shared traffic is the Magazov et al. (2026b) de-identified SSH honeypot "
        "attacker corpus on Zenodo (DOI "
    )
    set_run_font(r, size=12)
    add_hyperlink(p, "https://doi.org/10.5281/zenodo.20816078", DATASET_DOI)
    r2 = p.add_run(
        "). Licence: data/results CC BY 4.0. Verified download size 4,871,158 bytes; "
        "12,881 command rows; accessed 25 October 2026. The study uses a screened slice of "
        "20 sessions with 70 shared commands for paired replay. Country/collection context "
        "follows the Zenodo deposit by Magazov and co-authors (de-identified attacker "
        "commands from honeypot research; no live victims in this student lab)."
    )
    set_run_font(r2, size=12)
    add_body(
        doc,
        "Ubuntu ground truth was captured in an offline ubuntu:24.04 container (--network "
        "none) and stored as ground_truth.jsonl for fidelity scoring (Canonical Ltd, n.d.). "
        "The Ubuntu study replays the same scripted sessions to all backends for RQ1 "
        "metrics and supplies joined reply text for the RQ3 detector.",
    )

    add_heading_custom(doc, "4.3 Procedure", 2)
    add_body(
        doc,
        "Procedure steps were: (1) pass the containment pre-check before any study claim; "
        "(2) replay the same session list to all four systems via scripts/04_replay.py; "
        "(3) log command, reply, delay, tokens, system, settings, run number, and "
        "break/skip reasons to JSONL; (4) score with scripts/05_analyse.py (bootstrap 95% "
        "CIs, 1000 resamples, fixed seed in code; Wilcoxon signed-rank on paired "
        "commands_completed when ≥5 pairs); (5) freeze Magazov ×5 tables on 14 November "
        "2026; (6) train the exploratory detector with scripts/06_train_detector.py on "
        "joined Ubuntu/honeypot reply text only. Default generative settings for frozen "
        "runs used temperature 0.0 and history window 10 unless a run header records "
        "otherwise. GPT-4o mini remained a design row even when skipped. Magazov ×5 "
        "produced 1,400 command rows (20 sessions × 70 shared commands × 5 runs × 4 "
        "systems) plus run metadata. Ubuntu ×1 used the captured ground-truth join for "
        "fidelity and for detector training (no Magazov mixing in the primary detector "
        "tables).",
    )
    add_body(
        doc,
        "Evidence that objectives were met is tied to artefacts a marker can open: "
        "data/analysis/runs5/tables.md for Magazov engagement and delay; "
        "data/analysis/ubuntu_runs1/tables.md for fidelity; "
        "data/analysis/detector/tables.md and RESULTS_DETECTOR.md for exploratory ML; "
        "and rq4_containment.json for the audit. Skips and TimeoutError counts are kept "
        "visible so missing backends are not silently dropped from the four-system design.",
    )
    add_figure(
        doc,
        FIGS / "fig3_rq_mapping.png",
        5.8,
        "Figure 3. Mapping from RQ1–RQ4 to primary freeze evidence (Ubuntu fidelity, delay, "
        "detector F1/AUROC, containment audit).",
    )

    add_heading_custom(doc, "4.4 Reply-source detector methods (RQ3)", 2)
    add_body(
        doc,
        "RQ3 is answered with a self-developed exploratory detector (scripts/06_train_"
        "detector.py), not a published SOTA claim. Training used already-logged reply "
        "text only: nonempty Ubuntu stdout from ground_truth.jsonl (n=160) joined to "
        "Cowrie OK replies (n=160), Llama 3.1 8B OK replies (n=83) and Qwen 2.5 7B OK "
        "replies (n=97) from the Ubuntu replay log on matching (session_id, step). Magazov "
        "rows were not mixed into the primary detector tables (RESULTS_DETECTOR.md). Text "
        "was normalised by stripping ANSI/prompt chrome so Cowrie escape sequences are not "
        "a free giveaway. Features were character TF-IDF n-grams with range 3–5, followed "
        "by logistic regression with class_weight=balanced (Pedregosa et al., 2011; "
        "scikit-learn developers, n.d.). Splits used GroupShuffleSplit by session_id "
        "(approximately 70/15/15, seed=25) to reduce same-session leakage. Primary tasks "
        "were binary (real_ubuntu versus honeypot) and 3-way (ubuntu / cowrie / llm with "
        "Llama+Qwen pooled). A 4-way per-LLM task was skipped as primary because OK counts "
        "were uneven. Metrics reported are accuracy, macro-F1, AUROC (binary honeypot-"
        "positive; 3-way OvR macro), and per-class F1.",
    )

    add_heading_custom(doc, "4.5 Metrics justification", 2)
    add_body(
        doc,
        "Multiple metrics are used because no single score captures honeypot quality. "
        "Fidelity (exact/near match to Ubuntu stdout after normalisation) and consistency "
        "(agreement across runs) address RQ1 realism; Magazov mean commands completed "
        "until first break provides complementary engagement context for the same "
        "realism-versus-persistence trade-off. Mean delay with bootstrap CIs addresses "
        "RQ2 responsiveness; API cost is computed only when price environment variables "
        "and a live key exist. RQ3 uses accuracy, macro-F1, AUROC and per-class F1 as an "
        "exploratory auxiliary view of reply separability—not as a claim of beating "
        "published detectors. RQ4 uses a pass/fail containment checklist.",
    )

    add_heading_custom(doc, "4.6 Implementation and optimisation notes", 2)
    add_body(
        doc,
        "Implementation spans Python backends for Cowrie (Paramiko SSH client), OpenAI "
        "chat completions (text-only), and Ollama HTTP generate calls. Optimisation "
        "attempts on the student laptop included keeping temperature at 0.0 for "
        "reproducibility, limiting history window, fixed denials to avoid unsafe "
        "generations, and join-only detector training on nonempty Ubuntu stdout so empty "
        "ground-truth rows do not inflate scores. Local 7–8B models still incurred many "
        "TimeoutError events on ~7.5 GB RAM CPU inference; those errors are retained as "
        "results rather than deleted. Hyperparameter exploration for the detector was "
        "intentionally simple (TF-IDF n-gram range 3–5, class_weight=balanced, fixed "
        "split seed=25) to keep the auxiliary study transparent.",
    )

    # 5 Results
    add_heading_custom(doc, "5. Results", 1)
    add_body(
        doc,
        "Results are organised by study artefact. Magazov ×5 answers engagement and delay "
        "context for RQ1–RQ2; Ubuntu ×1 answers RQ1 fidelity; Section 5.3 gives qualitative "
        "failure cases on benign OK replies; Section 5.4 answers RQ3 with the exploratory "
        "detector; RQ4 is the containment audit. Figures 4–6 each show one comparison "
        "concept only (session length, fidelity, detector F1).",
    )

    add_heading_custom(doc, "5.1 Magazov ×5 comparison (engagement and delay)", 2)
    add_figure(
        doc,
        FIGS / "fig4_magazov_session_length.png",
        5.8,
        "Figure 4. Magazov ×5 mean commands completed before break "
        "(Cowrie 3.50 vs Llama 0.20 / Qwen 0.17; GPT skipped).",
    )
    add_table(
        doc,
        [
            "System",
            "Logged",
            "OK",
            "Skipped",
            "Mean delay (s) [95% CI]",
            "Mean cmds completed",
        ],
        [
            ["cowrie", "350", "350", "0", "0.37 [0.34, 0.40]", "3.50"],
            ["gpt-4o-mini", "350", "0", "350", "—", "—"],
            ["llama-3.1-8b", "350", "86", "0", "51.5 [42.5, 60.4]", "0.20"],
            ["qwen-2.5-7b", "350", "153", "0", "50.4 [44.9, 55.7]", "0.17"],
        ],
        "Table 3. Magazov 20 sessions × 5 runs summary (data/analysis/runs5). GPT skipped (no API key).",
    )
    add_body(
        doc,
        "Figure 4 and Table 3 show that Cowrie answered all 350 command rows with "
        "sub-second mean delay and the highest mean commands completed (3.50). Local LLMs "
        "produced fewer OK replies (Llama 86; Qwen 153) with mean delays around 50 seconds, "
        "largely reflecting CPU Ollama timeouts and the >5 s break rule. GPT-4o mini "
        "contributed 350 skips. Wilcoxon signed-rank tests on commands_completed favoured "
        "Cowrie over Llama (n=100, statistic=0.0, p≈1.1×10⁻¹⁶) and over Qwen (n=100, "
        "statistic=0.0, p≈1.8×10⁻¹⁶). These tests support Cowrie’s stronger persistence on "
        "this Magazov slice as engagement context for RQ1; they do not support a claim that "
        "LLMs beat Cowrie on session length. For RQ2, delay CIs are reported for systems "
        "that replied; GPT cost remains blank without a key.",
    )

    add_heading_custom(doc, "5.2 Ubuntu fidelity study (RQ1)", 2)
    add_figure(
        doc,
        FIGS / "fig5_ubuntu_fidelity.png",
        5.5,
        "Figure 5. Ubuntu ×1 fidelity versus ground truth "
        "(Cowrie 0.00, Llama 0.32, Qwen 0.40).",
    )
    add_table(
        doc,
        ["System", "OK replies", "Fidelity", "Consistency", "Invented content", "Mean cmds completed"],
        [
            ["cowrie", "200", "0.00", "0.14", "1.00", "10.00"],
            ["gpt-4o-mini", "0 (skipped)", "—", "—", "—", "—"],
            ["llama-3.1-8b", "106", "0.32", "0.60", "0.64", "0.05"],
            ["qwen-2.5-7b", "121", "0.40", "0.20", "0.57", "0.00"],
        ],
        "Table 4. Ubuntu ground-truth replay (data/analysis/ubuntu_runs1): fidelity improvement for LLMs vs Cowrie.",
    )
    add_body(
        doc,
        "Figure 5 and Table 4 show the main realism improvement—and the remaining gap. "
        "Qwen fidelity 0.40 and Llama 0.32 versus Cowrie 0.00 against Ubuntu stdout is a "
        "clear gain for pretrained LLMs over the scripted baseline on this test set. "
        "Neither local model approaches 1.0, so the gap to real Ubuntu behaviour is still "
        "large. Cowrie still completed more commands under the break definition in that "
        "log (mean 10.00 vs near-zero for locals), again reflecting delay/timeout behaviour "
        "rather than a claim that Cowrie matched Linux text. GPT remained skipped.",
    )

    add_heading_custom(doc, "5.3 Qualitative failure analysis (Ubuntu OK replies)", 2)
    add_body(
        doc,
        "Aggregate fidelity hides why replies still fail. Five benign commands from the "
        "Ubuntu replay log (data/logs/replay_ubuntu_testset_runs1.jsonl) joined to "
        "ground_truth.jsonl illustrate concrete divergences when Llama or Qwen returned "
        "status ok. No attack payloads are reproduced; examples are ordinary shell checks.",
    )
    add_table(
        doc,
        ["Command", "Issue type", "What went wrong (brief)"],
        [
            [
                "date",
                "Hallucinated date",
                "GT: Wed Nov 11 2026 (+08). Llama: Fri Jul 5 2019 UTC; Qwen: Wed Oct 11 2023 UTC.",
            ],
            [
                "uname -a",
                "Invented kernel string",
                "GT: WSL2 6.18… kernel. Llama: 4.15.0-55-generic (2019); Qwen: 5.4.0-47-generic.",
            ],
            [
                "ls -la",
                "Content / listing mismatch",
                "GT: home listing with .bashrc/.ssh. Qwen OK reply collapsed to “total 0”; Llama errored.",
            ],
            [
                "cat notes.txt",
                "Hallucinated file content",
                "GT: hello. Qwen matched; Llama invented “This is a note about the server configuration.”",
            ],
            [
                "which bash",
                "Path / format mismatch",
                "GT: /usr/bin/bash. Qwen matched; Llama returned /bin/bash (plausible but wrong path).",
            ],
        ],
        "Table 8. Selected benign Ubuntu failure cases where OK LLM replies diverge from ground truth.",
    )
    add_body(
        doc,
        "Table 8 shows that “better than Cowrie on mean fidelity” is not the same as "
        "matching a live host turn-by-turn. Time and kernel commands expose pretrained "
        "defaults (hallucinated dates and old Ubuntu kernels). Directory listings can "
        "collapse when the model lacks grounded filesystem state beyond session-memory "
        "hints. File content can be invented even when the filename is known. Path "
        "lookups may be almost right (/bin vs /usr/bin) yet still fail exact fidelity. "
        "These cases motivate the defender takeaways in Section 6: prefer Qwen when "
        "textual realism is the priority on this hardware, keep session memory, and "
        "never treat pretrained replies as a substitute for containment.",
    )

    add_heading_custom(doc, "5.4 Exploratory reply-source detector (RQ3)", 2)
    add_figure(
        doc,
        FIGS / "fig6_detector_f1.png",
        5.8,
        "Figure 6. Exploratory detector F1 scores on the held-out test fold "
        "(binary macro-F1 0.750; 3-way macro-F1 0.682; Cowrie 0.739; Ubuntu 0.708; LLM 0.600).",
    )
    add_table(
        doc,
        ["Task", "n_test", "Accuracy", "Macro-F1", "AUROC"],
        [
            ["Binary (ubuntu vs honeypot)", "62", "0.758", "0.750", "0.875"],
            ["3-way (ubuntu / cowrie / llm)", "62", "0.694", "0.682", "0.888 (OvR)"],
            ["Ubuntu vs LLM only", "37", "0.811", "0.802", "0.927"],
            ["Ubuntu vs Cowrie only", "50", "0.800", "0.797", "0.899"],
        ],
        "Table 5. Detector test-set metrics (data/analysis/detector/tables.md; RESULTS_DETECTOR.md). Exploratory only.",
    )
    add_table(
        doc,
        ["3-way class", "F1", "Support"],
        [
            ["cowrie", "0.739", "25"],
            ["ubuntu", "0.708", "25"],
            ["llm", "0.600", "12"],
        ],
        "Table 6. Three-way per-class F1 on the held-out test fold (LLM support is small).",
    )
    add_body(
        doc,
        "Figure 6 and Tables 5–6 answer RQ3. A bag-of-character-ngrams detector can "
        "separate real Ubuntu stdout from honeypot replies above chance (binary accuracy "
        "0.758, macro-F1 0.750, AUROC 0.875) but is far from perfect. The 3-way task reached "
        "accuracy 0.694, macro-F1 0.682 and OvR-AUROC 0.888. Per-class F1 shows Cowrie "
        "0.739, Ubuntu 0.708 and pooled LLM 0.600: in this feature space and fold, "
        "scripted Cowrie replies were easier to spot than LLM replies, while LLM text "
        "overlapped more with natural shell output (RESULTS_DETECTOR.md). Pairwise AUROCs "
        "are close (Ubuntu-vs-LLM 0.927; Ubuntu-vs-Cowrie 0.899); with small held-out "
        "session groups, this report does not claim a large, stable gap. Absolute numbers "
        "are exploratory—only 20 Ubuntu sessions drive the group split, LLM test support "
        "is 12, and bootstrap CIs are wide (binary macro-F1 95% CI about 0.626–0.853). "
        "This is a cheap auxiliary signal, not a silver-bullet detector and not a claim of "
        "superiority over all published honeypot detectors.",
    )

    add_heading_custom(doc, "5.5 RQ4 containment audit", 2)
    add_table(
        doc,
        ["Check", "Result", "Detail"],
        [
            ["local_bind", "pass", "listen host is 127.0.0.1"],
            ["cowrie_localhost", "pass", "Cowrie host is 127.0.0.1"],
            ["ollama_localhost", "pass", "Ollama host is 127.0.0.1"],
            ["openai_host_pinned", "pass", "GPT text calls use api.openai.com only"],
            ["no_host_execution", "pass", "commands not passed to host OS"],
            ["no_honeypot_outbound", "pass", "no honeypot outbound channel"],
            ["text_only_output", "pass", "model output type is text"],
            ["no_model_tools", "pass", "model not given tools"],
            ["source_has_no_host_shell", "pass", "no host shell / no public bind in source path"],
        ],
        "Table 7. RQ4 containment audit checklist (overall: Passed).",
    )
    add_body(
        doc,
        "Table 7 shows that all containment checks passed. This answers RQ4 in the "
        "repository’s operational sense: resistance-by-design against host compromise and "
        "uncontrolled egress, without distributing injection strings.",
    )

    # 6 Discussion
    add_heading_custom(doc, "6. Discussion and Evaluation", 1)
    add_body(
        doc,
        "The results answer the four research questions with an honest split between "
        "realism, persistence and detectability—and with a clear “so what” for defenders. "
        "Static honeypots are easy to detect and therefore collect less intelligence; "
        "pretrained LLMs improve textual realism on this Ubuntu test set (Table 4; "
        "Figure 5), but Magazov session length still favours Cowrie (~3.50 vs ~0.2 mean "
        "commands completed; Table 3; Figure 4). Fidelity gains here do not equal fooling "
        "a real attacker. For RQ1, Qwen is the better local model on fidelity (0.40 vs "
        "Llama 0.32 vs Cowrie 0.00), yet both remain far from 1.0. Cowrie’s invented-"
        "content rate of 1.00 on that join further shows how scripted output can diverge "
        "from a live Ubuntu container even when the honeypot remains fast. For RQ2, "
        "Cowrie replied in well under one second on average; local LLMs averaged ~50 s "
        "when they replied; GPT was skipped. For RQ3, the exploratory detector "
        "(Figure 6; Tables 5–6) shows both backends remain partially detectable, with "
        "Cowrie more stereotyped (F1 0.739) than pooled LLM replies (F1 0.600) in this "
        "fold—consistent with higher fidelity overlapping natural shell text more. For "
        "RQ4, containment passed. GPT-4o mini could not be scored for delay or cost "
        "without a key; the skipped row preserves study design completeness.",
    )
    add_body(
        doc,
        "Defender takeaways follow directly from Tables 3–6 and Table 8. Prefer Qwen over "
        "Llama when the goal is closer Ubuntu-like stdout on this laptop lab. Expect Llama "
        "to invent file contents and slightly wrong paths (for example cat notes.txt and "
        "which bash), and expect both models to hallucinate time and kernel strings (date, "
        "uname -a). Expect Qwen listings to sometimes collapse (ls -la → “total 0”) even "
        "when identity-style replies look more natural. Session memory is necessary but not "
        "sufficient: it reduces some state drift, yet pretrained priors still leak. "
        "Containment (localhost bind, text-only output, no host execution, no model tools) "
        "is required for safe use; without it, an LLM honeypot is an unnecessary risk "
        "surface. The exploratory detector is a lab signal only—it does not certify that "
        "LLM replies would fool a human operator or a production scanner.",
    )
    add_body(
        doc,
        "Why methods performed as they did follows from architecture and hardware. Cowrie "
        "returns precomputed or lightly templated replies over localhost SSH, so mean "
        "delay stays near 0.37 s and sessions proceed until a content-level break. Llama "
        "and Qwen must load multi-billion-parameter models through Ollama on CPU with a "
        "history window; many calls hit the client timeout (~120 s) or exceed the 5 s "
        "engagement proxy, truncating survival. The detector’s higher Cowrie class F1 is "
        "consistent with more stereotyped scripted phrasing once ANSI chrome is stripped, "
        "while LLM text overlaps more with natural shell stdout in character n-gram "
        "space—useful as a lab signal, not as proof that LLMs are undetectable in the wild "
        "(RESULTS_DETECTOR.md).",
    )
    add_body(
        doc,
        "Compared with Magazov et al. (2026a), Sladić et al. (2024), Otal and Canbaz (2024), "
        "and Wang et al. (2026), the novelty here is the paired multi-step four-system "
        "measurement under localhost containment, plus joined Ubuntu fidelity, qualitative "
        "failure cases, and an exploratory detector that adds Data Science ML evidence. "
        "The reusable lab value is that another student or small SOC can plug in a new "
        "model via .env (swap LLAMA_MODEL/QWEN_MODEL or set EXTRA_OLLAMA_MODELS) and "
        "re-run the same sessions through 04_replay.py and 05_analyse.py without "
        "redesigning metrics—the harness keeps sessions and scoring fixed so only the "
        "backend changes. Improvements "
        "versus existing practice are therefore methodological and empirical within this "
        "lab: higher fidelity than Cowrie on Ubuntu GT; repeatable survival metrics with "
        "CIs and Wilcoxon tests; explicit skip handling; detector metrics with honest "
        "support counts; and a containment checklist that a marker can re-run from source. "
        "The work does not claim to outperform every published field honeypot on live "
        "attacker dwell time, nor to beat all published detectors on large benchmarks.",
    )
    add_body(
        doc,
        "Objectives O1–O4 are met with stated caveats: O1 fidelity is available from Ubuntu "
        "runs with Magazov session-length context; O2 delay CIs are reported for systems "
        "that replied, with GPT cost blank; O3 detector metrics are reported with "
        "exploratory framing and small LLM test support; O4 containment passed. Suitable "
        "real-world applications include a small organisation’s internal evaluation harness "
        "before choosing a honeypot backend, a teaching laboratory for deception metrics, "
        "or a pre-deployment smoke test of containment and detectability assumptions. They "
        "do not include unsupervised internet-facing deception without further hardening, "
        "monitoring, and hardware sized for interactive LLM latency.",
    )
    add_body(
        doc,
        "Design recommendation: if the priority is stable multi-step engagement on modest "
        "hardware, keep Cowrie (optionally as a front end)—it is still stronger on Magazov "
        "session length, though also easier for a bag-of-ngrams detector to spot in this "
        "lab. If the priority is more natural shell text and data must stay local, prefer "
        "Qwen among the two local models tested, with session memory and fixed denials, "
        "accepting slower replies or investing in GPU/RAM. Commercial APIs remain optional "
        "when keys and egress policy allow. Hybrid designs—Cowrie for common commands and "
        "an LLM for long-tail commands—are a practical future path suggested by the "
        "fidelity-versus-persistence trade-off observed here.",
    )

    # 7 Limitations
    add_heading_custom(doc, "7. Limitations", 1)
    add_body(
        doc,
        "Limitations bound all claims. (1) Few models were compared (two local open-weight "
        "systems plus Cowrie; GPT-4o mini skipped without an API key), so rankings are "
        "lab-specific rather than a universal leaderboard. (2) Local model timeouts on a "
        "~7.5 GB RAM CPU laptop understate LLM session survival and inflate break counts; "
        "a GPU host would likely change Magazov persistence rankings even if fidelity "
        "stayed similar. (3) The detector uses few held-out sessions and LLM test support "
        "of only 12; treat Tables 5–6 as exploratory. (4) RQ4 is a containment audit, not "
        "a multi-turn injection benchmark with stored payloads—aligned with ethics, but "
        "narrower than the original injection-battery wording in the project plan. "
        "(5) External validity is limited: higher fidelity than Cowrie is not the same as "
        "fooling a real attacker on the open internet; the closed-lab Magazov replay is "
        "not live adversaries. (6) Magazov slice size (20 sessions / 70 shared commands) "
        "is smaller than the full ~12.9k-command corpus. (7) Fidelity normalisation "
        "choices (ANSI/prompt stripping) affect both RQ1 and detector scores; different "
        "normalisers could shift absolute values. These limits are disclosed so markers "
        "can judge evidential strength rather than over-generalise.",
    )

    # 8 Conclusion
    add_heading_custom(doc, "8. Conclusion and Future Enhancements", 1)
    add_body(
        doc,
        "This project built a replay-based evaluation lab and showed that pretrained LLMs "
        "reproduce real Ubuntu behaviour better than a scripted honeypot (Qwen 0.40, Llama "
        "0.32 vs Cowrie 0.00)—while staying honest that Cowrie still leads Magazov session "
        "length (~3.50 vs ~0.2) and that the detector remains exploratory. RQ1: Qwen is "
        "the stronger local model on fidelity, with both LLMs above Cowrie but far from "
        "1.0. RQ2: Cowrie replied in well under one second on average; local LLMs averaged "
        "~50 s when they replied; GPT was skipped. RQ3: binary detector accuracy 0.758, "
        "macro-F1 0.750, AUROC 0.875; 3-way accuracy 0.694, macro-F1 0.682, OvR-AUROC "
        "0.888; per-class F1 Cowrie 0.739, Ubuntu 0.708, LLM 0.600. RQ4: containment audit "
        "passed for localhost, text-only, no-tools, no-host-execution design. Contributions "
        "C1–C4 are evidenced by the public repository, freeze tables, failure cases in "
        "Table 8, and detector artefacts. Contribution C5 is the reusable comparison lab: "
        "the harness keeps the same sessions and metrics so another model can be plugged "
        "in via config (.env model tags or EXTRA_OLLAMA_MODELS) and compared the same way "
        "(docs/REUSE.md).",
    )
    add_body(
        doc,
        "Next steps: (1) fine-tuning (for example LoRA) of a small local model on benign "
        "shell transcripts to raise fidelity and reduce invented content without sending "
        "data to a commercial API; (2) controlled live deployment behind the same "
        "containment controls, after hardware can sustain interactive latency; (3) more "
        "models via the reuse path (EXTRA_OLLAMA_MODELS or swapped tags), including "
        "re-running GPT-4o mini once an API key and price variables "
        "exist for a full four-way cost/delay comparison; (4) better hardware (more RAM / "
        "GPU) to reduce TimeoutError rates and allow fairer session-survival comparison "
        "under the same 5 s break rule; (5) optional scale-up of the exploratory detector "
        "and optional hybrid routing (Cowrie for common commands; LLM for long-tail). "
        "Together these steps would tighten the link between realism gains already seen "
        "in Table 4 and the persistence metrics in Table 3—without mistaking lab fidelity "
        "for proof that a real attacker is deceived.",
    )

    # References — 16 Harvard, alphabetical, verified / project-used
    add_heading_custom(doc, "References", 1)
    refs = [
        "Canonical Ltd (n.d.) Ubuntu documentation. Available at: https://ubuntu.com/ (Accessed: 18 November 2026).",
        "Cowrie Project (n.d.) Cowrie SSH/Telnet honeypot. Available at: https://github.com/cowrie/cowrie (Accessed: 18 November 2026).",
        "Efron, B. and Tibshirani, R.J. (1993) An Introduction to the Bootstrap. New York: Chapman & Hall.",
        "Javadpour, A., Ja’fari, F., Taleb, T., Shojafar, M. and Benzaïd, C. (2024) ‘A comprehensive survey on cyber deception techniques to improve honeypot performance’, Computers & Security, 140, 103792. Available at: https://doi.org/10.1016/j.cose.2024.103792 (Accessed: 18 November 2026).",
        "Magazov, R., Abeshev, K., Shamuratov, Y., Uralova, F. and Aksholak, G. (2026a) ‘Benchmarking LLM backends for generative SSH honeypots: security, fidelity, hallucination, latency, and stability’, AI, 7(8), 287. Available at: https://doi.org/10.3390/ai7080287 (Accessed: 18 November 2026).",
        "Magazov, R., Abeshev, K., Shamuratov, Y., Uralova, F. and Aksholak, G. (2026b) Benchmarking LLM backends for generative SSH honeypots: dataset and code [Dataset]. Zenodo. Available at: https://doi.org/10.5281/zenodo.20816078 (Accessed: 25 October 2026).",
        "Ollama (n.d.) Ollama documentation. Available at: https://github.com/ollama/ollama (Accessed: 18 November 2026).",
        "OpenAI (n.d.) OpenAI API reference. Available at: https://platform.openai.com/docs/api-reference (Accessed: 18 November 2026).",
        "Otal, H.T. and Canbaz, M.A. (2024) ‘LLM honeypot: leveraging large language models as advanced interactive honeypot systems’, 2024 IEEE Conference on Communications and Network Security (CNS). Available at: https://doi.org/10.1109/CNS62487.2024.10735607 ; also https://arxiv.org/abs/2409.08234 (Accessed: 18 November 2026).",
        "Paramiko Project (n.d.) Paramiko: A Python implementation of SSHv2. Available at: https://www.paramiko.org/ (Accessed: 18 November 2026).",
        "Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M. and Duchesnay, É. (2011) ‘Scikit-learn: machine learning in Python’, Journal of Machine Learning Research, 12, pp. 2825–2830. Available at: https://jmlr.org/papers/v12/pedregosa11a.html (Accessed: 18 November 2026).",
        "scikit-learn developers (n.d.) scikit-learn user guide. Available at: https://scikit-learn.org/stable/user_guide.html (Accessed: 18 November 2026).",
        "Sladić, M., Valeros, V., Catania, C. and Garcia, S. (2023) ‘LLM in the shell: generative honeypots’, arXiv:2309.00155. Available at: https://arxiv.org/abs/2309.00155 (Accessed: 18 November 2026).",
        "Sladić, M., Valeros, V., Catania, C. and Garcia, S. (2024) ‘LLM in the shell: generative honeypots’, Proceedings of the 2024 IEEE European Symposium on Security and Privacy Workshops (EuroS&PW), pp. 430–435. Available at: https://doi.org/10.1109/EuroSPW61312.2024.00054 (Accessed: 18 November 2026).",
        "University of Hertfordshire (n.d.) Ethics approval. Ask Herts. Available at: https://ask.herts.ac.uk/ethics-approval (Accessed: 27 October 2026).",
        "University of Hertfordshire (2024) Project Handbook Sem A MSc Data Science 2024. Hatfield: School of Physics, Engineering and Computer Science.",
        "Wang, Z., You, J., Wang, H., Yuan, T., Lv, S., Wang, Y. and Sun, L. (2026) ‘HoneyGPT: breaking the trilemma in honeypots with large language models’, Computer Networks, 282, 112223. Available at: https://doi.org/10.1016/j.comnet.2026.112223 (Accessed: 18 November 2026).",
        "Wilcoxon, F. (1945) ‘Individual comparisons by ranking methods’, Biometrics Bulletin, 1(6), pp. 80–83. Available at: https://doi.org/10.2307/3001968 (Accessed: 18 November 2026).",
    ]
    for ref in refs:
        add_ref(doc, ref)

    # Appendices like friend example
    add_heading_custom(doc, "Appendix A. Repository and reproduction", 1)
    add_body(
        doc,
        "Code and data: "
        + GITHUB
        + ". Reproduction (brief): create/activate the project .venv; install "
        "requirements.txt; configure localhost Cowrie/Ollama as needed; run "
        "scripts/04_replay.py then scripts/05_analyse.py for Magazov/Ubuntu tables; run "
        "scripts/06_train_detector.py for detector metrics. Canonical Magazov ×5 log: "
        "data/logs/replay_magazov_20sess_runs5.jsonl. Analysis: data/analysis/runs5/, "
        "data/analysis/ubuntu_runs1/, data/analysis/detector/. Freeze day for practical "
        "tables: 14 November 2026. See README.md and RESULTS_DETECTOR.md. No secrets or "
        ".env contents are included in this appendix.",
    )
    add_heading_custom(doc, "Appendix B. Backup of code and data", 1)
    add_body(
        doc,
        "A backup copy of the complete code, processed data and results is stored on "
        "Google Drive: [TODO — student to paste personal Google Drive backup link here].",
    )

    # Word count: Abstract through Conclusion (exclude References + Appendices).
    # Handbook includes abstract/contents/body; Contents also lists the word "References",
    # so locate the real References heading by scanning paragraphs in order.
    collecting = False
    wc_parts: list[str] = []
    for para in doc.paragraphs:
        t = para.text.strip()
        style = para.style.name if para.style else ""
        if style.startswith("Heading") and t == "Abstract":
            collecting = True
        if collecting and style.startswith("Heading") and t == "References":
            break
        if collecting:
            wc_parts.append(para.text)
    words = len(re.findall(r"\b\w+\b", "\n".join(wc_parts)))
    for para in doc.paragraphs:
        if "[TO BE FILLED AFTER BUILD]" in para.text:
            for run in para.runs:
                if "[TO BE FILLED AFTER BUILD]" in run.text:
                    run.text = run.text.replace(
                        "[TO BE FILLED AFTER BUILD]",
                        f"{words} (approx.; Abstract through Conclusion)",
                    )

    doc.save(OUT_MAIN)
    dl_path = OUT_DL
    try:
        shutil.copy2(OUT_MAIN, OUT_DL)
        print("WROTE", OUT_DL)
    except PermissionError:
        shutil.copy2(OUT_MAIN, OUT_DL_REVISED)
        dl_path = OUT_DL_REVISED
        print("WARN: Downloads locked; wrote", OUT_DL_REVISED)

    # Markdown backup
    md = []
    md.append("# Generative AI Deception: Dynamic LLM-Powered Honeypots\n\n")
    md.append("**Student:** Patil Devyani Anil (5034)  \n")
    md.append("**Module:** 7FTC2001 · Supervisor: Dr Rama Abirami K.  \n")
    md.append(f"**GitHub:** {GITHUB}  \n")
    md.append(f"**Approx. word count (Abstract–Conclusion):** {words}\n\n")
    md.append("## Final four research questions\n\n")
    md.append(
        "1. RQ1 realism/consistency vs Linux output.\n"
        "2. RQ2 response time and cost.\n"
        "3. RQ3 TF-IDF+LR detectability of Ubuntu vs Cowrie/LLM replies "
        "(REPLACES old session-technique / ATT&CK-style RQ).\n"
        "4. RQ4 containment / injection resistance.\n\n"
    )
    md.append("## Detector headline numbers\n\n")
    md.append(
        "Binary: acc 0.758, macro-F1 0.750, AUROC 0.875. "
        "3-way: acc 0.694, macro-F1 0.682, OvR-AUROC 0.888. "
        "Per-class F1: cowrie 0.739, ubuntu 0.708, llm 0.600.\n\n"
    )
    md.append("## Figures\n")
    for name in [
        "fig1_architecture.png",
        "fig2_method_pipeline.png",
        "fig3_rq_mapping.png",
        "fig4_magazov_session_length.png",
        "fig5_ubuntu_fidelity.png",
        "fig6_detector_f1.png",
    ]:
        md.append(f"- report_figures/{name}\n")
    OUT_MD.write_text("".join(md), encoding="utf-8")

    image_rels = [r for r in Document(str(OUT_MAIN)).part.rels.values() if "image" in r.reltype]
    print("WORD_COUNT", words)
    print("REF_COUNT", len(refs))
    print("IMAGES_IN_DOCX", len(image_rels))
    print("WROTE", OUT_MAIN)
    print("DL_PATH", dl_path)
    print("WROTE", OUT_MD)
    return words, len(refs), len(image_rels), str(dl_path)


if __name__ == "__main__":
    build()
