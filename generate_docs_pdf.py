"""
DataInterpreter - PDF Documentation Generator
Uses ReportLab for full Unicode support and professional layout.
Run: python generate_docs_pdf.py
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Preformatted, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os

OUTPUT = "DataInterpreter_Documentation.pdf"

# ── Color Palette ─────────────────────────────────────────────────────────────
C_DARK       = colors.HexColor("#0F172A")   # slate-900
C_BLUE       = colors.HexColor("#38BDF8")   # sky-400  (use only on dark backgrounds)
C_BLUE_DARK  = colors.HexColor("#1D6FA5")   # readable blue for light/white backgrounds
C_GREEN      = colors.HexColor("#156B43")   # darker emerald — readable on white
C_GREEN_DARK = colors.HexColor("#065F46")   # even darker green for table headers
C_AMBER      = colors.HexColor("#B45309")   # amber-700 — readable on white/light bg
C_RED        = colors.HexColor("#B91C1C")   # red-700 — readable on light bg
C_SLATE      = colors.HexColor("#1E293B")   # slate-800
C_GRAY       = colors.HexColor("#475569")   # slate-600 — darker for readability
C_LIGHT      = colors.HexColor("#F1F5F9")   # slate-100
C_WHITE      = colors.white
C_CODE_BG    = colors.HexColor("#1E293B")
C_CODE_TEXT  = colors.HexColor("#BAE6FD")   # lighter sky-200, visible on dark code bg


# ── Page Template with header/footer ─────────────────────────────────────────
class NumberedPageCanvas:
    def __init__(self, canvas, doc):
        self.canvas = canvas
        self.doc    = doc

    @staticmethod
    def afterPage(canvas, doc):
        if doc.page == 1:
            return
        canvas.saveState()
        w, h = A4
        # Header bar
        canvas.setFillColor(C_DARK)
        canvas.rect(0, h - 16*mm, w, 16*mm, fill=1, stroke=0)
        canvas.setFillColor(C_BLUE)
        canvas.rect(0, h - 16.5*mm, w, 0.7*mm, fill=1, stroke=0)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(C_BLUE)
        canvas.drawCentredString(w/2, h - 11*mm,
                                 "DATAINTERPRETER  |  Complete Project Documentation")
        # Footer bar
        canvas.setFillColor(C_DARK)
        canvas.rect(0, 0, w, 12*mm, fill=1, stroke=0)
        canvas.setFillColor(C_BLUE)
        canvas.rect(0, 12*mm, w, 0.5*mm, fill=1, stroke=0)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(C_GRAY)
        canvas.drawCentredString(w/2, 4*mm, f"Page {doc.page}")
        canvas.restoreState()


# ── Build Styles ──────────────────────────────────────────────────────────────
def make_styles():
    styles = {}

    styles['body'] = ParagraphStyle(
        'body', fontName='Helvetica', fontSize=10,
        leading=14, textColor=colors.black, spaceAfter=6, alignment=TA_JUSTIFY
    )
    styles['body_small'] = ParagraphStyle(
        'body_small', fontName='Helvetica', fontSize=9,
        leading=13, textColor=colors.black, spaceAfter=4
    )
    styles['chapter'] = ParagraphStyle(
        'chapter', fontName='Helvetica-Bold', fontSize=16,
        leading=20, textColor=C_BLUE, spaceBefore=14, spaceAfter=4,
        backColor=C_DARK, borderPad=8
    )
    styles['section'] = ParagraphStyle(
        'section', fontName='Helvetica-Bold', fontSize=12,
        leading=16, textColor=C_GREEN, spaceBefore=10, spaceAfter=4
    )
    styles['subsection'] = ParagraphStyle(
        'subsection', fontName='Helvetica-Bold', fontSize=10,
        leading=14, textColor=C_AMBER, spaceBefore=6, spaceAfter=3
    )
    styles['bullet'] = ParagraphStyle(
        'bullet', fontName='Helvetica', fontSize=9.5,
        leading=13, textColor=colors.black, leftIndent=16,
        bulletIndent=4, spaceAfter=3
    )
    styles['code'] = ParagraphStyle(
        'code', fontName='Courier', fontSize=8,
        leading=11, textColor=C_CODE_TEXT, backColor=C_CODE_BG,
        leftIndent=8, rightIndent=4, spaceBefore=4, spaceAfter=6,
        borderPad=6
    )
    styles['note'] = ParagraphStyle(
        'note', fontName='Helvetica-Oblique', fontSize=9,
        leading=13, textColor=colors.HexColor("#713F12"), backColor=colors.HexColor("#FEF3C7"),
        leftIndent=8, borderPad=6, spaceAfter=6
    )
    styles['note_red'] = ParagraphStyle(
        'note_red', fontName='Helvetica-Oblique', fontSize=9,
        leading=13, textColor=colors.HexColor("#7F1D1D"), backColor=colors.HexColor("#FEE2E2"),
        leftIndent=8, borderPad=6, spaceAfter=6
    )
    styles['toc_num'] = ParagraphStyle(
        'toc_num', fontName='Helvetica-Bold', fontSize=11,
        leading=16, textColor=C_GRAY
    )
    styles['toc_title'] = ParagraphStyle(
        'toc_title', fontName='Helvetica', fontSize=11,
        leading=16, textColor=C_WHITE
    )
    styles['cover_title'] = ParagraphStyle(
        'cover_title', fontName='Helvetica-Bold', fontSize=34,
        leading=40, textColor=C_BLUE, alignment=TA_CENTER
    )
    styles['cover_sub'] = ParagraphStyle(
        'cover_sub', fontName='Helvetica', fontSize=15,
        leading=20, textColor=colors.HexColor("#34D399"), alignment=TA_CENTER
    )
    styles['cover_info'] = ParagraphStyle(
        'cover_info', fontName='Helvetica', fontSize=11,
        leading=16, textColor=C_GRAY, alignment=TA_CENTER
    )
    return styles


# ── Helper Flowables ──────────────────────────────────────────────────────────
def chapter_block(num, title, styles):
    return [
        Spacer(1, 6*mm),
        Paragraph(f"  {num}.  {title}", styles['chapter']),
        HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceAfter=4),
        Spacer(1, 2*mm),
    ]


def section_block(title, styles, color=None):
    s = ParagraphStyle('_sec', parent=styles['section'],
                       textColor=color or C_GREEN)
    return [
        Spacer(1, 3*mm),
        Paragraph(title, s),
        HRFlowable(width="50%", thickness=0.5, color=color or C_GREEN, spaceAfter=3),
    ]


def body(text, styles):
    return Paragraph(text, styles['body'])


def body_small(text, styles):
    return Paragraph(text, styles['body_small'])


def bullet_item(text, styles):
    return Paragraph(f"\u2022  {text}", styles['bullet'])


def code_block(code_text, styles):
    return Preformatted(code_text, styles['code'])


def note_box(text, styles, color='amber'):
    s = styles['note_red'] if color == 'red' else styles['note']
    return Paragraph(text, s)


def hr():
    return HRFlowable(width="100%", thickness=0.3,
                      color=colors.HexColor("#334155"), spaceAfter=2)


def make_table(headers, rows, col_widths, styles_dict=None):
    """Create a styled table."""
    data = [headers] + rows

    base_ts = [
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), C_DARK),
        ('TEXTCOLOR',  (0, 0), (-1, 0), C_BLUE),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 4),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        # Data rows
        ('FONTNAME',   (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',   (0, 1), (-1, -1), 8),
        ('TEXTCOLOR',  (0, 1), (-1, -1), C_DARK),
        ('TOPPADDING', (0, 1), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [C_LIGHT, C_WHITE]),
        ('LINEBEFORE', (0, 0), (0, -1), 2, C_BLUE),
        ('LINEBELOW',  (0, -1), (-1, -1), 0.5, C_GRAY),
    ]

    t = Table(data, colWidths=[w*mm for w in col_widths])
    t.setStyle(TableStyle(base_ts))
    return t


# ══════════════════════════════════════════════════════════════════════════════
# Cover page builder
# ══════════════════════════════════════════════════════════════════════════════
def build_cover(styles):
    from reportlab.platypus import Table as RLTable, TableStyle as RLTableStyle

    cover_data = [[
        Paragraph("DATAINTERPRETER", styles['cover_title'])
    ]]
    cover_table = RLTable(cover_data, colWidths=[170*mm])
    cover_table.setStyle(RLTableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_DARK),
        ('TOPPADDING', (0, 0), (-1, -1), 80),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))

    elements = [
        cover_table,
        Spacer(1, 5*mm),
        Paragraph("Complete Project Documentation", styles['cover_sub']),
        Spacer(1, 8*mm),
        HRFlowable(width="60%", thickness=1, color=C_BLUE,
                   hAlign='CENTER', spaceAfter=8),
        Paragraph("Multi-Agent AI System  |  Natural Language to SQL", styles['cover_info']),
        Paragraph("CrewAI  |  OpenAI GPT-4o-mini  |  Streamlit  |  SQLite", styles['cover_info']),
        Paragraph("RAG: Keyword  /  FAISS  /  ChromaDB", styles['cover_info']),
        Spacer(1, 12*mm),
        Paragraph("Project Path:  D:\\DataInterpreter", styles['cover_info']),
        Paragraph("Generated:     March 2026", styles['cover_info']),
        PageBreak(),
    ]
    return elements


# ══════════════════════════════════════════════════════════════════════════════
# Main document builder
# ══════════════════════════════════════════════════════════════════════════════
def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=22*mm, bottomMargin=18*mm,
        title="DataInterpreter — Documentation",
        author="DataInterpreter",
    )

    styles = make_styles()
    story  = []
    W = 174  # usable width in mm

    # ── Cover ─────────────────────────────────────────────────────────────────
    story += build_cover(styles)

    # ── TOC ───────────────────────────────────────────────────────────────────
    toc_entries = [
        ("1",  "Project Overview"),
        ("2",  "Directory Structure"),
        ("3",  "Architecture & System Design"),
        ("4",  "Agent Definitions"),
        ("5",  "Task Definitions"),
        ("6",  "Crew Setup & Pydantic Models"),
        ("7",  "RAG System  --  4 Strategies"),
        ("8",  "Database Schema  --  21 Tables"),
        ("9",  "Database Simulator (db_simulator.py)"),
        ("10", "Streamlit UI (app.py)"),
        ("11", "CLI Flow Entry Point (main.py)"),
        ("12", "Utility Helpers (helper.py)"),
        ("13", "End-to-End Data Flow"),
        ("14", "LLM Cost Tracking"),
        ("15", "Environment & Dependencies"),
        ("16", "Key Design Decisions"),
    ]

    story.append(Paragraph("Table of Contents", styles['chapter']))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceAfter=6))

    toc_data = [[Paragraph(f"<b>{n}.</b>", styles['toc_num']),
                 Paragraph(t, styles['toc_title'])]
                for n, t in toc_entries]
    toc_tbl = Table(toc_data, colWidths=[12*mm, 158*mm])
    toc_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), C_DARK),
        ('TOPPADDING',    (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LINEBELOW',     (0, 0), (-1, -1), 0.2, colors.HexColor("#1E293B")),
    ]))
    story.append(toc_tbl)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 1. Project Overview
    # ══════════════════════════════════════════════════════════════════════════
    story += chapter_block("1", "Project Overview", styles)
    story.append(body(
        "DataInterpreter is a multi-agent AI pipeline that converts a plain English "
        "question into a fully validated, compliance-checked SQL query and executes it "
        "against a simulated 21-table e-commerce SQLite database. The system is built on "
        "CrewAI with OpenAI GPT-4o-mini as the LLM backbone and Streamlit as the "
        "interactive front-end. A RAG (Retrieval Augmented Generation) system filters the "
        "database schema before each LLM call, reducing token usage by ~67%.", styles))

    story += section_block("Core Pipeline at a Glance", styles)
    story.append(make_table(
        ["Stage", "Agent", "What It Does"],
        [["Generate", "query_generator_agent",   "Translates NL question -> SQL query"],
         ["Review",   "query_reviewer_agent",    "Checks correctness, joins, performance"],
         ["Comply",   "compliance_checker_agent","Flags PII leaks or policy violations"]],
        [22, 65, 87]
    ))

    story += section_block("Quick Stats", styles)
    story.append(make_table(
        ["Metric", "Value"],
        [["LLM Model",          "OpenAI GPT-4o-mini (temperature=0.2)"],
         ["Database",           "SQLite -- 21 tables, ~200 products, 500 orders"],
         ["Token Reduction",    "~67% via RAG (full schema -> top-5 relevant tables)"],
         ["Typical Cost / Run", "$0.0004 to $0.0010 USD (Generate + Review + Comply)"],
         ["UI Framework",       "Streamlit 1.48.1"],
         ["Agent Framework",    "CrewAI 0.130.0"],
         ["RAG Strategies",     "4 (NoRAG, Keyword, FAISS Vector, Chroma Vector)"]],
        [55, 119]
    ))

    # ══════════════════════════════════════════════════════════════════════════
    # 2. Directory Structure
    # ══════════════════════════════════════════════════════════════════════════
    story += chapter_block("2", "Directory Structure", styles)
    story.append(code_block(
        "D:\\DataInterpreter\\\n"
        "|\n"
        "+-- app.py                 # Streamlit web UI  (main entry point)\n"
        "+-- main.py                # CLI / Flow-based pipeline entry\n"
        "+-- crew_setup.py          # Agents, Tasks, Crews, Pydantic models\n"
        "|\n"
        "+-- config/\n"
        "|   +-- agents.yaml        # Agent role, goal, backstory, LLM config\n"
        "|   +-- tasks.yaml         # Task prompts + expected outputs\n"
        "|\n"
        "+-- utils/\n"
        "|   +-- db_simulator.py    # SQLite DB creation, schema, query runner\n"
        "|   +-- rag_manager.py     # 4 RAG strategies + RAGManager orchestrator\n"
        "|   +-- helper.py          # Token count parser + cost calculator\n"
        "|\n"
        "+-- data/\n"
        "|   +-- sample_db.sqlite   # 21-table e-commerce database (~533 KB)\n"
        "|   +-- chroma_db/         # Persistent Chroma vector store\n"
        "|\n"
        "+-- .env                   # OPENAI_API_KEY=sk-proj-...\n"
        "+-- requirements.txt       # Pinned dependencies (10 direct packages)\n"
        "+-- README.md              # Project readme",
        styles))

    # ══════════════════════════════════════════════════════════════════════════
    # 3. Architecture
    # ══════════════════════════════════════════════════════════════════════════
    story += chapter_block("3", "Architecture & System Design", styles)
    story.append(body(
        "The system follows a linear 3-stage pipeline triggered from the Streamlit UI. "
        "A RAG module sits upstream of the pipeline to reduce LLM token usage before the "
        "generation stage. Each stage uses a dedicated Crew (one agent + one task) and "
        "returns a typed Pydantic model rather than raw text.", styles))

    story += section_block("Pipeline Flow", styles)
    story.append(code_block(
        "User NL Query\n"
        "     |\n"
        "     v\n"
        "[RAG Manager] -- selects top-5 relevant tables from 21 total\n"
        "     |  Filtered Schema (~67% fewer tokens)\n"
        "     v\n"
        "[sql_generator_crew]  ->  SQLQuery.sqlquery\n"
        "     |\n"
        "     v  (User confirms in UI)\n"
        "[sql_reviewer_crew]   ->  ReviewedSQLQuery.reviewed_sqlquery\n"
        "     |\n"
        "     v\n"
        "[sql_compliance_crew] ->  ComplianceReport.report\n"
        "     |\n"
        "     +-- Compliant? YES -> run_query(reviewed_sql) -> Display Results\n"
        "     +-- Compliant? NO  -> Show Compliance Issues, block execution",
        styles))

    story += section_block("Key Architectural Decisions", styles)
    decisions = [
        ("3 Separate Crews (not 1)",
         "Allows staged user interaction -- confirm before committing to review. "
         "Crews can be independently invoked and return typed Pydantic outputs."),
        ("Pydantic Output Models",
         "Forces the LLM to return structured JSON. No brittle string parsing. "
         "Fields accessed via crew_output.pydantic.field_name."),
        ("RAG Before Generation",
         "Schema filtered to top-5 relevant tables before the LLM call. "
         "Prevents hallucination of non-existent tables/columns, cuts cost ~67%."),
        ("Full Schema for Review",
         "The reviewer uses the FULL schema to catch any errors the generator "
         "may have introduced -- comprehensive validation."),
        ("Temperature 0.2 on All Agents",
         "SQL generation requires precision. Low temperature reduces hallucinations "
         "and produces consistent, reproducible SQL."),
        ("Session State Machine",
         "Streamlit session state tracks each pipeline stage independently, "
         "preventing redundant LLM calls on page reruns."),
        ("SQLite for Simulation",
         "Zero-dependency, portable database. Perfect for demos without a running DB server."),
        ("ChromaDB Persistence",
         "Vector embeddings are expensive to compute; persisting them avoids "
         "re-embedding on every application startup."),
    ]
    for title, desc in decisions:
        story.append(Paragraph(f"<b><font color='#B45309'>{title}</font></b>  --  {desc}",
                                styles['body_small']))
        story.append(Spacer(1, 1*mm))

    # ══════════════════════════════════════════════════════════════════════════
    # 4. Agent Definitions
    # ══════════════════════════════════════════════════════════════════════════
    story += chapter_block("4", "Agent Definitions", styles)
    story.append(body(
        "All agents are configured in <b>config/agents.yaml</b> and instantiated in "
        "<b>crew_setup.py</b>. Each agent uses GPT-4o-mini with temperature 0.2 and "
        "allow_delegation=False.", styles))

    agents = [
        ("4.1  query_generator_agent -- Senior Data Analyst", C_BLUE_DARK,
         [["Role",        "Senior Data Analyst"],
          ["Model",       "openai/gpt-4o-mini  |  Temperature: 0.2"],
          ["Goal",        "Translate natural language into accurate, efficient SQL"],
          ["Backstory",   "Experienced analyst who knows SQL best practices; prefers readable SQL with appropriate filters and joins"],
          ["What it does","Receives NL question + filtered schema. Lists which tables/columns to use, then writes SQL. "
                          "Explicitly knows data model relationships (SKU prefixes, FK paths, inventory constraints)."]]),
        ("4.2  query_reviewer_agent -- SQL Code Reviewer", C_GREEN,
         [["Role",        "SQL Code Reviewer"],
          ["Model",       "openai/gpt-4o-mini  |  Temperature: 0.2"],
          ["Goal",        "Critically evaluate SQL for correctness, performance, and clarity"],
          ["Backstory",   "Meticulous reviewer who identifies inefficiencies, bad join patterns, and logical errors"],
          ["What it does","Takes generated SQL + the FULL schema. Checks join correctness, schema compliance "
                          "(no invented columns), performance. Returns unchanged if correct; corrects if possible; "
                          "returns -- comment if unfixable."]]),
        ("4.3  compliance_checker_agent -- Data Privacy & Governance Officer", C_AMBER,
         [["Role",        "Data Privacy and Governance Officer"],
          ["Model",       "openai/gpt-4o-mini  |  Temperature: 0.2"],
          ["Goal",        "Ensure SQL queries follow compliance rules and avoid PII exposure"],
          ["Backstory",   "Responsible for flagging PII leaks, unsafe bulk data access, or company policy violations"],
          ["What it does","Receives only the reviewed SQL. Checks for PII (emails, names), unsafe patterns "
                          "(SELECT *), policy violations. Returns markdown Compliance Report with verdict: "
                          "Compliant or Issues Found."]]),
    ]
    for agent_title, color, props in agents:
        story += section_block(agent_title, styles, color=color)
        agent_tbl_data = [[Paragraph(f"<b>{k}</b>", styles['body_small']),
                           Paragraph(v, styles['body_small'])]
                          for k, v in props]
        at = Table(agent_tbl_data, colWidths=[30*mm, 144*mm])
        at.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('ROWBACKGROUNDS',(0, 0), (-1, -1), [C_LIGHT, C_WHITE]),
            ('TOPPADDING',    (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LINEBEFORE',    (0, 0), (0, -1), 2, color),
        ]))
        story.append(at)

    # ══════════════════════════════════════════════════════════════════════════
    # 5. Task Definitions
    # ══════════════════════════════════════════════════════════════════════════
    story += chapter_block("5", "Task Definitions", styles)
    story.append(body(
        "All tasks are defined in <b>config/tasks.yaml</b>. Each task holds the full "
        "prompt template sent to the LLM, including data model relationship rules.", styles))

    story += section_block("5.1  query_task -- SQL Generation", styles)
    story.append(body_small("Inputs: {db_schema}, {user_input}", styles))
    story.append(body_small("Expected Output: Syntactically correct SQL with appropriate JOINs, filters, and GROUP BY.", styles))
    story.append(body_small("<b>Critical rules embedded in prompt:</b>", styles))
    for r in [
        "order_items.sku = product_variants.sku  (both use 'VAR-' prefix)",
        "products.sku uses 'SKU-' prefix -- different namespace entirely",
        "inventory table has NO sku column -- only variant_id, warehouse_id, quantity",
        "Revenue path: order_items -> product_variants -> products -> brands",
        "Do NOT invent tables or columns; return -- comment if request unsatisfiable",
    ]:
        story.append(bullet_item(r, styles))

    story += section_block("5.2  review_task -- SQL Review", styles)
    story.append(body_small("Inputs: {sql_query}, {db_schema} (FULL schema -- not filtered)", styles))
    for r in ["Both variant_id AND sku joins valid for sales data",
              "Return unchanged if already correct",
              "Return -- comment if unfixable",
              "Do not invent new tables or columns"]:
        story.append(bullet_item(r, styles))

    story += section_block("5.3  compliance_task -- Compliance Check", styles)
    story.append(body_small("Inputs: {reviewed_sqlquery}  |  Context: review_task output", styles))
    for r in ["Check for PII: emails, names, phone numbers",
              "Flag unsafe patterns: SELECT *, bulk personal data dumps",
              "State 'No issues found' if fully compliant",
              "Include verdict at top: Compliant | Issues Found"]:
        story.append(bullet_item(r, styles))

    # ══════════════════════════════════════════════════════════════════════════
    # 6. Crew Setup & Pydantic Models
    # ══════════════════════════════════════════════════════════════════════════
    story += chapter_block("6", "Crew Setup & Pydantic Models", styles)

    story += section_block("Pydantic Output Models  (crew_setup.py)", styles)
    story.append(body(
        "Pydantic models are attached to each Task via <b>output_pydantic=</b>. "
        "CrewAI forces the LLM response to conform to the model and deserialises it "
        "automatically. Access via <b>crew_output.pydantic.field_name</b>.", styles))
    story.append(code_block(
        "class SQLQuery(BaseModel):\n"
        "    sqlquery: str          # Raw generated SQL\n"
        "\n"
        "class ReviewedSQLQuery(BaseModel):\n"
        "    reviewed_sqlquery: str # Reviewed / corrected SQL\n"
        "\n"
        "class ComplianceReport(BaseModel):\n"
        "    report: str            # Markdown compliance report",
        styles))

    story += section_block("Three Independent Crew Objects", styles)
    story.append(code_block(
        "sql_generator_crew = Crew(\n"
        "    agents=[query_generator_agent], tasks=[query_task],  verbose=True\n"
        ")\n"
        "sql_reviewer_crew = Crew(\n"
        "    agents=[query_reviewer_agent],  tasks=[review_task], verbose=True\n"
        ")\n"
        "sql_compliance_crew = Crew(\n"
        "    agents=[compliance_checker_agent], tasks=[compliance_task], verbose=True\n"
        ")",
        styles))
    story.append(body(
        "Each crew is independently called with <b>.kickoff(inputs={...})</b>, giving "
        "the UI precise control over when each stage is triggered and allowing the user "
        "to confirm, retry, or abort between stages.", styles))

    # ══════════════════════════════════════════════════════════════════════════
    # 7. RAG System
    # ══════════════════════════════════════════════════════════════════════════
    story += chapter_block("7", "RAG System -- 4 Strategies", styles)
    story.append(body(
        "The RAG system in <b>utils/rag_manager.py</b> filters the 21-table schema "
        "down to the top-5 most relevant tables before each LLM call. This reduces "
        "token usage by ~67% and prevents hallucination of non-existent table/column names.",
        styles))

    story += section_block("Class Hierarchy", styles)
    story.append(code_block(
        "BaseRAG (ABC)\n"
        "+-- NoRAG              --  Full schema, no filtering\n"
        "+-- KeywordRAG         --  Business keyword scoring (no ML model)\n"
        "+-- FAISSVectorRAG     --  Semantic embeddings + FAISS index\n"
        "+-- ChromaVectorRAG    --  Embeddings + ChromaDB persistent storage\n"
        "\n"
        "RAGManager             --  Orchestrates all 4, benchmarks performance",
        styles))

    rag_strategies = [
        ("7.1  NoRAG -- Baseline", C_GRAY,
         "Returns the complete structured schema from SQLite with no filtering. "
         "Useful for small schemas (<10 tables) or when exhaustive coverage is needed.",
         ["Zero setup, always complete"],
         ["High token usage, slower LLM calls"]),
        ("7.2  KeywordRAG -- Business Keyword Matching", C_GREEN,
         "Scores each of 21 tables against a hand-crafted keyword dictionary. "
         "+3 per exact keyword match, +1 per partial match, +10 if exact table name appears in query. "
         "Returns top-5 tables. Falls back to pattern defaults (e.g., 'revenue' -> orders, order_items, products).",
         ["Instant, no ML model required", "No external dependencies"],
         ["Limited to predefined keyword vocabulary", "May miss complex semantic relationships"]),
        ("7.3  FAISSVectorRAG -- Semantic Embedding Search", C_BLUE_DARK,
         "Uses sentence-transformers/all-MiniLM-L6-v2 for semantic embeddings. "
         "At init: creates rich table descriptions (name, purpose, columns, FK relationships, use cases) "
         "and indexes them with FAISS IndexFlatIP (cosine similarity). "
         "At query time: encodes query, searches FAISS for top-5 similar tables (threshold=0.1).",
         ["Semantic understanding beyond keywords", "Handles complex queries"],
         ["Requires model download (~90 MB)", "Higher RAM usage"]),
        ("7.4  ChromaVectorRAG -- Persistent Vector Store", C_AMBER,
         "Same embedding model as FAISS but uses ChromaDB for persistent storage at ./data/chroma_db/. "
         "On first run: populates the Chroma collection. "
         "On subsequent runs: loads the existing indexed collection (fast startup).",
         ["Persistent storage, scalable, fast after init", "Production-ready"],
         ["Disk space required", "Additional dependency"]),
    ]

    for rag_title, color, desc, pros, cons in rag_strategies:
        story += section_block(rag_title, styles, color=color)
        story.append(body(desc, styles))
        pros_cons = Table(
            [["PROS", "CONS"]] + list(zip(pros + [""]*(len(cons)-len(pros)),
                                          cons + [""]*(len(pros)-len(cons)))),
            colWidths=[87*mm, 87*mm]
        )
        pros_cons.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (0, 0), C_GREEN),
            ('BACKGROUND',    (1, 0), (1, 0), C_RED),
            ('TEXTCOLOR',     (0, 0), (-1, 0), C_DARK),
            ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, -1), 8),
            ('TOPPADDING',    (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [C_LIGHT, C_WHITE]),
        ]))
        story.append(pros_cons)
        story.append(Spacer(1, 2*mm))

    story += section_block("7.5  RAGManager -- Orchestrator", styles)
    story.append(make_table(
        ["Method", "Purpose"],
        [["get_relevant_schema(query, approach)", "Delegate to chosen approach, record performance metrics"],
         ["compare_approaches(query)",            "Run all 4, return timing + token reduction stats"],
         ["get_available_approaches()",           "Return metadata dict for UI dropdown selection"],
         ["get_performance_summary()",            "Aggregate session-wide performance metrics"]],
        [90, 84]
    ))

    # ══════════════════════════════════════════════════════════════════════════
    # 8. Database Schema
    # ══════════════════════════════════════════════════════════════════════════
    story += chapter_block("8", "Database Schema -- 21 Tables", styles)
    story.append(body(
        "The SQLite database at <b>data/sample_db.sqlite</b> is a fully synthetic "
        "e-commerce database generated by <b>setup_ecommerce_db()</b> with seed=42 "
        "for reproducibility.", styles))

    story.append(make_table(
        ["Table", "Rows", "Purpose"],
        [["brands",               "10",    "Product manufacturers (Acme, Stark, Hooli...)"],
         ["categories",           "24",    "Hierarchical product categories (8 top x 3 sub)"],
         ["products",             "200",   "Catalog: name, sku, price, brand, category"],
         ["product_variants",     "~400",  "Color/size variants; links products to sellable items"],
         ["product_images",       "200",   "One primary image URL per product"],
         ["customers",            "200",   "name, email, country, created_at, is_active"],
         ["addresses",            "~260",  "Billing and shipping addresses per customer"],
         ["orders",               "500",   "Transactions: totals, status, dates, customer FK"],
         ["order_items",          "~1250", "Line items per order (1-5 per order)"],
         ["payments",             "500",   "One payment record per order"],
         ["shipments",            "500",   "One shipment per order with tracking"],
         ["shipment_items",       "~1250", "Package line items per shipment"],
         ["discounts",            "10",    "Promo codes: percent or fixed amount"],
         ["order_discounts",      "~125",  "Many-to-many bridge: orders <-> discounts"],
         ["warehouses",           "3",     "West DC, Central DC, East DC"],
         ["inventory",            "~1200", "Stock quantity per variant per warehouse"],
         ["suppliers",            "3",     "Procurement vendors"],
         ["purchase_orders",      "30",    "Supplier purchase orders with status"],
         ["purchase_order_items", "~90",   "Line items per supplier PO"],
         ["reviews",              "500",   "Customer ratings and comments"]],
        [45, 20, 109]
    ))

    story += section_block("Critical Relationship Rules", styles)
    story.append(code_block(
        "order_items.sku = product_variants.sku  (both use 'VAR-' prefix)\n"
        "products.sku uses 'SKU-' prefix  --  DIFFERENT namespace!\n"
        "inventory has NO sku column -- joins via variant_id ONLY\n"
        "\n"
        "Revenue join path:   order_items -> product_variants -> products -> brands\n"
        "Inventory join path: inventory   -> product_variants -> products",
        styles))
    story.append(note_box(
        "WARNING: These relationship rules are explicitly embedded into both the "
        "query_task and review_task prompts to prevent LLM hallucination of "
        "non-existent join columns.", styles, color='amber'))

    # ══════════════════════════════════════════════════════════════════════════
    # 9. db_simulator.py
    # ══════════════════════════════════════════════════════════════════════════
    story += chapter_block("9", "Database Simulator  (utils/db_simulator.py)", styles)

    story += section_block("setup_ecommerce_db(db_path, seed=42)", styles)
    story.append(body("The main database creator. Executes these steps in order:", styles))
    for s in [
        "os.makedirs(os.path.dirname(db_path), exist_ok=True)  --  ensures data/ dir exists",
        "PRAGMA foreign_keys = OFF  --  safely drop all 21 existing tables",
        "PRAGMA foreign_keys = ON   --  re-enable for table creation and data insertion",
        "CREATE TABLE ... for all 21 tables with proper FK constraints",
        "Seed: 10 brands, 24 categories, 200 products, ~400 variants, 200 customers",
        "Seed: ~260 addresses, 500 orders, ~1250 order_items, 500 payments, 500 shipments",
        "Seed: 10 discounts, 30 purchase orders, ~90 PO items, 500 reviews",
        "conn.commit() and conn.close()",
    ]:
        story.append(bullet_item(s, styles))

    story += section_block("Other Functions", styles)
    story.append(make_table(
        ["Function", "Returns", "Used By"],
        [["setup_sample_db()",          "--",             "main.py CLI (simpler 6-table DB)"],
         ["run_query(query)",           "str (5 rows)",   "app.py after compliance approval"],
         ["get_db_schema(db_path)",     "DDL string",     "main.py CLI mode"],
         ["get_structured_schema(path)","'- table: cols'","All LLM prompts and RAG fallbacks"]],
        [55, 35, 84]
    ))

    # ══════════════════════════════════════════════════════════════════════════
    # 10. Streamlit UI
    # ══════════════════════════════════════════════════════════════════════════
    story += chapter_block("10", "Streamlit UI  (app.py)", styles)
    story.append(body("Run with: <b>streamlit run app.py</b>  (default port 8501)", styles))

    story += section_block("Page Layout", styles)
    story.append(code_block(
        "+---------------------------------------------------------------+\n"
        "|  DataInterpreter  (title + description)                       |\n"
        "+---------------------|------------------------------------------+\n"
        "|  RAG Configuration  |  Database Schema                        |\n"
        "|  (approach dropdown)|  (expandable DDL view + Refresh button) |\n"
        "+---------------------+------------------------------------------+\n"
        "|  Optional: RAG Performance Comparison benchmark table          |\n"
        "+---------------------------------------------------------------+\n"
        "|  Natural Language Query Interface                             |\n"
        "|  [text input box]    [Generate SQL button]                   |\n"
        "+---------------------------------------------------------------+\n"
        "|  Query Results (state machine -- 3 stages)                   |\n"
        "|  Stage 1: Generated SQL + [Confirm] [Try Again] [Abort]      |\n"
        "|  Stage 2: 'Processing...' spinner (review + compliance)      |\n"
        "|  Stage 3: Reviewed SQL + Compliance Report + Query Results   |\n"
        "|           + LLM Cost display  +  [Start Over] button         |\n"
        "+---------------------------------------------------------------+",
        styles))

    story += section_block("Session State Machine Keys", styles)
    story.append(make_table(
        ["Key", "Type", "Meaning"],
        [["generated_sql",         "str|None", "SQL from the generation step"],
         ["awaiting_confirmation",  "bool",     "Generated but user has not confirmed yet"],
         ["processing_review",      "bool",     "Review + compliance pipeline is running"],
         ["reviewed_sql",           "str|None", "SQL after the reviewer agent"],
         ["compliance_report",      "str|None", "Markdown compliance report text"],
         ["query_result",           "str|None", "Formatted query execution result rows"],
         ["regenerate_sql",         "bool",     "'Try Again' button was clicked"],
         ["llm_cost",               "float",    "Running cumulative cost in USD"]],
        [50, 22, 102]
    ))

    story += section_block("Stage-by-Stage UI Flow", styles)
    steps = [
        ("1", "User selects RAG approach from dropdown (defaults to Keyword RAG)"),
        ("2", "User types NL query in the text input field"),
        ("3", "Clicks 'Generate SQL' -> RAG filters schema -> sql_generator_crew.kickoff()"),
        ("4", "generated_sql stored in session state; awaiting_confirmation=True -> Stage 1 displayed"),
        ("5", "User clicks 'Confirm and Review' -> awaiting_confirmation=False; processing_review=True; page reruns"),
        ("6", "Stage 2 block executes: sql_reviewer_crew -> sql_compliance_crew -> run_query (if compliant)"),
        ("7", "All results stored in session state; processing_review=False; page reruns -> Stage 3"),
        ("8", "Stage 3 displayed: results, compliance verdict, LLM cost, status banner, Start Over button"),
    ]
    for num, desc in steps:
        story.append(Paragraph(
            f"<b><font color='#1D6FA5'>{num}.</font></b>  {desc}",
            styles['body_small']))
        story.append(Spacer(1, 1*mm))

    # ══════════════════════════════════════════════════════════════════════════
    # 11. main.py
    # ══════════════════════════════════════════════════════════════════════════
    story += chapter_block("11", "CLI Flow Entry Point  (main.py)", styles)
    story.append(body(
        "Alternative to the Streamlit UI -- runs the full pipeline from the terminal "
        "using <b>CrewAI Flow</b> for sequential, event-driven orchestration. "
        "Each step is decorated with <b>@start()</b> or <b>@listen(prev_step)</b>.",
        styles))
    story.append(code_block(
        "class SQLAssistantFlow(Flow):\n"
        "    @start()\n"
        "    def collect_prompt_user(self):\n"
        '        return "Show me the top 5 products by total revenue for April 2024"\n'
        "\n"
        "    @listen(collect_prompt_user)\n"
        "    def gen_raw_sql(self, user_prompt):\n"
        "        output = sql_generator_crew.kickoff(inputs={...})\n"
        '        self.state["raw_sql"] = output.pydantic.sqlquery\n'
        "        return output\n"
        "\n"
        "    @listen(gen_raw_sql)\n"
        "    def review_raw_sql(self, _):\n"
        "        output2 = sql_reviewer_crew.kickoff(inputs={...})\n"
        '        self.state["reviewed_sql"] = output2.pydantic.reviewed_sqlquery\n'
        "        return output2\n"
        "\n"
        "    @listen(review_raw_sql)\n"
        "    def compliance_check(self, _):\n"
        "        output3 = sql_compliance_crew.kickoff(inputs={...})\n"
        '        self.state["compliance_report"] = output3.pydantic.report\n'
        "        return output3\n"
        "\n"
        "flow = SQLAssistantFlow()\n"
        "flow.kickoff()",
        styles))
    story.append(note_box(
        "NOTE: main.py uses the simpler 6-table DB (setup_sample_db()) while app.py "
        "uses the full 21-table e-commerce DB (setup_ecommerce_db()).", styles))

    # ══════════════════════════════════════════════════════════════════════════
    # 12. helper.py
    # ══════════════════════════════════════════════════════════════════════════
    story += chapter_block("12", "Utility Helpers  (utils/helper.py)", styles)

    story += section_block("extract_token_counts(token_usage_str)", styles)
    story.append(body(
        "Parses the string representation of CrewAI's <b>token_usage</b> object using "
        "regex to extract prompt_tokens and completion_tokens as integers.", styles))
    story.append(code_block(
        "def extract_token_counts(token_usage_str):\n"
        "    prompt = re.search(r'prompt_tokens=(\\d+)',     token_usage_str)\n"
        "    compl  = re.search(r'completion_tokens=(\\d+)', token_usage_str)\n"
        "    return int(prompt.group(1)), int(compl.group(1))",
        styles))

    story += section_block("calculate_gpt4o_mini_cost(prompt_tokens, completion_tokens)", styles)
    story.append(body("Calculates USD cost using OpenAI's published GPT-4o-mini pricing:", styles))
    story.append(code_block(
        "Input tokens:   $0.00015 / 1K tokens\n"
        "Output tokens:  $0.00060 / 1K tokens\n"
        "\n"
        "def calculate_gpt4o_mini_cost(prompt_tokens, completion_tokens):\n"
        "    return (prompt_tokens / 1000) * 0.00015 + (completion_tokens / 1000) * 0.0006",
        styles))

    # ══════════════════════════════════════════════════════════════════════════
    # 13. End-to-End Data Flow
    # ══════════════════════════════════════════════════════════════════════════
    story += chapter_block("13", "End-to-End Data Flow", styles)
    story.append(code_block(
        'User Query: "Show me the top 5 products by total revenue for April 2024"\n'
        "     |\n"
        "     v\n"
        "[RAG Manager -- Keyword RAG]\n"
        "  Tokenises query -> scores 21 tables\n"
        "  Top 5 selected: products, orders, order_items, brands, payments\n"
        "  Returns filtered schema (67% fewer tokens than full schema)\n"
        "     |\n"
        "     v\n"
        "[sql_generator_crew.kickoff(user_input=..., db_schema=<filtered>)]\n"
        "  Agent:  query_generator_agent  (GPT-4o-mini, temp=0.2)\n"
        "  Output: SQLQuery.sqlquery =\n"
        "          SELECT p.name, SUM(oi.quantity * oi.unit_price) AS total_revenue\n"
        "          FROM order_items oi\n"
        "          JOIN product_variants pv ON oi.variant_id = pv.variant_id\n"
        "          JOIN products p ON pv.product_id = p.product_id\n"
        "          JOIN orders o ON oi.order_id = o.order_id\n"
        "          WHERE strftime('%Y-%m', o.created_at) = '2024-04'\n"
        "          GROUP BY p.name\n"
        "          ORDER BY total_revenue DESC\n"
        "          LIMIT 5;\n"
        "     |\n"
        "     v  [User sees SQL in UI, clicks 'Confirm and Review']\n"
        "     |\n"
        "     v\n"
        "[sql_reviewer_crew.kickoff(sql_query=..., db_schema=<FULL schema>)]\n"
        "  Agent:  query_reviewer_agent  (GPT-4o-mini, temp=0.2)\n"
        "  Output: ReviewedSQLQuery.reviewed_sqlquery = <corrected or same SQL>\n"
        "     |\n"
        "     v\n"
        "[sql_compliance_crew.kickoff(reviewed_sqlquery=...)]\n"
        "  Agent:  compliance_checker_agent  (GPT-4o-mini, temp=0.2)\n"
        "  Context: review_task output included\n"
        "  Output: ComplianceReport.report =\n"
        '          "## Compliance Report\\n**Verdict: Compliant**\\nNo PII..."\n'
        "     |\n"
        "     +-- 'compliant' in report  -->  run_query(reviewed_sql)\n"
        "     |       sqlite3.connect('data/sample_db.sqlite')\n"
        "     |       pd.read_sql_query(query, conn).head().to_string()\n"
        "     |       Returns: 5-row formatted string\n"
        "     |\n"
        "     +-- 'issues found' in report  -->  Block execution, show issues\n"
        "     |\n"
        "     v\n"
        "[Streamlit displays]\n"
        "  Reviewed SQL | Compliance Report | Query Results | LLM Cost",
        styles))

    # ══════════════════════════════════════════════════════════════════════════
    # 14. LLM Cost Tracking
    # ══════════════════════════════════════════════════════════════════════════
    story += chapter_block("14", "LLM Cost Tracking", styles)
    story.append(body(
        "The app tracks cumulative USD cost across all three crew invocations per "
        "session using GPT-4o-mini's published pricing rates.", styles))
    story.append(code_block(
        "# After every crew.kickoff() call:\n"
        "token_usage_str = str(crew_output.token_usage)\n"
        "prompt_tokens, completion_tokens = extract_token_counts(token_usage_str)\n"
        "cost = calculate_gpt4o_mini_cost(prompt_tokens, completion_tokens)\n"
        'st.session_state["llm_cost"] += cost\n'
        "\n"
        "# Displayed as:\n"
        "st.info(f\"Total LLM cost: ${st.session_state['llm_cost']:.6f}\")",
        styles))
    story.append(make_table(
        ["Stage", "Prompt Tokens", "Output Tokens", "Est. Cost USD"],
        [["Generate", "800-1500",  "150-300", "$0.00023"],
         ["Review",   "1000-2000", "150-250", "$0.00028"],
         ["Comply",   "300-600",   "100-200", "$0.00017"],
         ["TOTAL",    "~2100-4100","~400-750", "$0.0004-$0.0010"]],
        [35, 42, 42, 55]
    ))

    # ══════════════════════════════════════════════════════════════════════════
    # 15. Environment & Dependencies
    # ══════════════════════════════════════════════════════════════════════════
    story += chapter_block("15", "Environment & Dependencies", styles)

    story += section_block(".env File Format", styles)
    story.append(code_block("OPENAI_API_KEY=sk-proj-...", styles))
    story.append(note_box(
        "CRITICAL: Must be a plain KEY=VALUE line. Do NOT wrap in shell syntax like: "
        'echo "OPENAI_API_KEY=...". python-dotenv reads this as a literal string, '
        "not a shell command.", styles, color='red'))
    story.append(code_block(
        "from dotenv import load_dotenv, find_dotenv\n"
        "load_dotenv(find_dotenv(), override=True)  # loaded in app.py and main.py",
        styles))

    story += section_block("Key Dependencies", styles)
    story.append(make_table(
        ["Package", "Version", "Purpose"],
        [["streamlit",            "1.48.1",  "Web UI framework"],
         ["crewai",               "0.130.0", "Multi-agent orchestration & Flow"],
         ["openai",               "1.69.0",  "LLM API client (via litellm)"],
         ["pandas",               "2.3.1",   "Query result DataFrame formatting"],
         ["sqlparse",             "0.5.3",   "SQL pretty-printing in UI"],
         ["python-dotenv",        "1.1.1",   ".env file loading"],
         ["pyyaml",               "6.0.2",   "YAML config parsing for agents/tasks"],
         ["faiss-cpu",            "1.12.0",  "Vector similarity search (FAISS RAG)"],
         ["sentence-transformers","5.1.0",   "Text embeddings: all-MiniLM-L6-v2"],
         ["chromadb",             "1.0.20",  "Persistent vector store (Chroma RAG)"]],
        [48, 24, 102]
    ))

    story += section_block("Installation & Running", styles)
    story.append(code_block(
        "# 1. Create virtual environment\n"
        "python -m venv venv\n"
        "venv\\Scripts\\activate          # Windows PowerShell\n"
        "\n"
        "# 2. Install all dependencies\n"
        "pip install -r requirements.txt\n"
        "\n"
        "# 3. Set up .env file\n"
        "echo OPENAI_API_KEY=sk-proj-...  >  .env\n"
        "\n"
        "# 4. Create the database (auto-creates data/ directory)\n"
        "python -c \"from utils.db_simulator import setup_ecommerce_db; setup_ecommerce_db()\"\n"
        "\n"
        "# 5a. Launch web UI (recommended)\n"
        "streamlit run app.py\n"
        "\n"
        "# 5b. OR run CLI pipeline\n"
        "python main.py",
        styles))

    # ══════════════════════════════════════════════════════════════════════════
    # 16. Key Design Decisions
    # ══════════════════════════════════════════════════════════════════════════
    story += chapter_block("16", "Key Design Decisions", styles)
    story.append(make_table(
        ["Decision", "Rationale"],
        [["3 Separate Crews",
          "Staged UX: confirm before review. Each crew independently invocable with typed Pydantic output."],
         ["Pydantic Output Models",
          "Eliminates brittle string parsing. LLM forced to produce structured JSON via output_pydantic=."],
         ["RAG Before Generation",
          "~67% token reduction. Prevents hallucination of non-existent table/column names."],
         ["Full Schema for Review",
          "Reviewer needs complete schema to catch errors the generator may have introduced."],
         ["Temperature 0.2 All Agents",
          "SQL requires precision. Low temperature = consistent, reproducible, non-hallucinated SQL."],
         ["SQLite for Simulation",
          "Zero-dependency, file-based. Perfect for demos and dev without a running DB server."],
         ["ChromaDB Persistence",
          "Embedding computation is expensive; persisting avoids re-embedding on every startup."],
         ["os.makedirs Before Connect",
          "sqlite3.connect() creates files but NOT directories. data/ must exist first."],
         ["Session State Machine",
          "Prevents redundant LLM calls on Streamlit re-runs. Each stage fires exactly once."]],
        [55, 119]
    ))

    # ── Build ─────────────────────────────────────────────────────────────────
    doc.build(
        story,
        onFirstPage=NumberedPageCanvas.afterPage,
        onLaterPages=NumberedPageCanvas.afterPage,
    )

    size_kb = os.path.getsize(OUTPUT) / 1024
    print(f"\nPDF created: {os.path.abspath(OUTPUT)}")
    print(f"Pages built successfully | Size: {size_kb:.1f} KB")


if __name__ == "__main__":
    build_pdf()
