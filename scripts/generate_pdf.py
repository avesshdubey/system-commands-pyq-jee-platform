import json
import os
import re
from xml.sax.saxutils import escape
from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "questions.json")
OUTPUT_PDF = os.path.join(BASE_DIR, "system_commands_questions_categorized.pdf")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#555555"))
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "IIT Madras - System Commands (SC) | Past Year Question Bank")
            self.setStrokeColor(colors.HexColor("#dddddd"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)
            
        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, footer_text)
        self.drawString(54, 36, "Confidential - For Personal Educational & Exam Preparation Use")
        self.setStrokeColor(colors.HexColor("#dddddd"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)
        self.restoreState()

def build_pdf():
    print(f"Loading questions from: {DATA_FILE}")
    if not os.path.exists(DATA_FILE):
        print("Data file not found. Ensure extraction finishes first.")
        return
        
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)
        
    print(f"Total questions to compile: {len(questions)}")
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        alignment=1, # Center
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=15
    )
    
    week_header_style = ParagraphStyle(
        'WeekHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=16,
        textColor=colors.white,
        spaceAfter=0
    )
    
    subtopic_header_style = ParagraphStyle(
        'SubtopicHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=6
    )
    
    q_header_style = ParagraphStyle(
        'QHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#1e3a8a')
    )
    
    q_stem_style = ParagraphStyle(
        'QStem',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#212121'),
        spaceAfter=4
    )
    
    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=4
    )
    
    ans_style = ParagraphStyle(
        'AnsText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#15803d'),
        spaceBefore=3,
        spaceAfter=3
    )

    story = []
    
    # Title Page Header
    story.append(Spacer(1, 10))
    story.append(Paragraph("INDIAN INSTITUTE OF TECHNOLOGY MADRAS", ParagraphStyle(
        'InstTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=colors.HexColor('#64748b'),
        alignment=1,
        spaceAfter=4
    )))
    
    total_q = len(questions)
    total_papers = len(set(p for q in questions for p in q.get('source_papers', [])))
    w1_count = sum(1 for q in questions if 'Week 1' in q['week'])
    w2_count = sum(1 for q in questions if 'Week 2' in q['week'])
    w3_count = sum(1 for q in questions if 'Week 3' in q['week'])
    w4_count = sum(1 for q in questions if 'Week 4' in q['week'])
    
    story.append(Paragraph("System Commands (Linux / Bash)", title_style))
    story.append(Paragraph(f"Past Year Question Bank ({total_papers} Exam Sessions) — Official Categorized Syllabus Edition", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))
    
    summary_data = [
        [
            Paragraph(f"<b>Total Unique Questions:</b> {total_q}", styles['Normal']),
            Paragraph(f"<b>Exam Sessions Covered:</b> {total_papers} Papers", styles['Normal']),
            Paragraph("<b>Format:</b> MCQ, MSQ, NAT / SA", styles['Normal'])
        ],
        [
            Paragraph(f"<b>Week 1:</b> Shell & Basics ({w1_count} Qs)", styles['Normal']),
            Paragraph(f"<b>Week 2:</b> Permissions & Streams ({w2_count} Qs)", styles['Normal']),
            Paragraph(f"<b>Week 3:</b> Filters, Grep & Awk ({w3_count} Qs)", styles['Normal'])
        ],
        [
            Paragraph(f"<b>Week 4:</b> Scripting & Processes ({w4_count} Qs)", styles['Normal']),
            Paragraph("<b>Fidelity:</b> Official TCS iON Cards", styles['Normal']),
            Paragraph("<b>Interactive Mode:</b> NTA JEE CBT Online", styles['Normal'])
        ]
    ]
    t = Table(summary_data, colWidths=[168, 168, 168])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))
    
    # Group questions by Week and Subtopic
    grouped = {}
    for q in questions:
        wk = q.get('week', 'Uncategorized')
        sub = q.get('subtopic', 'General')
        grouped.setdefault(wk, {}).setdefault(sub, []).append(q)
        
    week_order = [
        "Week 1: Introduction to Operating Systems, Shell & Basic Commands",
        "Week 2: File System Hierarchy, Permissions, Redirection & Links",
        "Week 3: Text Processing Filters, Grep/Regex, Sed & Awk",
        "Week 4: Shell Scripting, Environment Variables & Process Management"
    ]
    
    week_colors = {
        "Week 1: Introduction to Operating Systems, Shell & Basic Commands": colors.HexColor('#1e40af'), # Blue
        "Week 2: File System Hierarchy, Permissions, Redirection & Links": colors.HexColor('#4338ca'), # Indigo
        "Week 3: Text Processing Filters, Grep/Regex, Sed & Awk": colors.HexColor('#0d9488'), # Teal
        "Week 4: Shell Scripting, Environment Variables & Process Management": colors.HexColor('#7c3aed') # Purple
    }

    for wk in week_order:
        if wk not in grouped:
            continue
            
        subtopics = grouped[wk]
        wk_total = sum(len(qs) for qs in subtopics.values())
        
        story.append(Spacer(1, 8))
        banner_table = Table([[Paragraph(f"{wk} &nbsp;({wk_total} Questions)", week_header_style)]], colWidths=[504])
        banner_color = week_colors.get(wk, colors.HexColor('#334155'))
        banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), banner_color),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 0.5, banner_color)
        ]))
        story.append(banner_table)
        story.append(Spacer(1, 6))
        
        for sub, qs in subtopics.items():
            sub_count = len(qs)
            story.append(Paragraph(f"<b>&bull; {sub}</b> &nbsp;<font color='#64748b'>({sub_count} Questions)</font>", subtopic_header_style))
            story.append(Spacer(1, 3))
            
            for q in qs:
                card_elements = []
                q_id = q.get('id', 'SC_???')
                q_type = q.get('question_type', 'MCQ')
                marks = q.get('marks', 3)
                sources = q.get('source_papers', ['Official IITM Paper'])
                source_count = len(sources)
                first_src = os.path.basename(sources[0]).replace('.pdf', '')
                
                header_line = f"<b>{q_id}</b> &nbsp;|&nbsp; [{q_type}] &nbsp;|&nbsp; <b>Marks:</b> +{marks} &nbsp;|&nbsp; <i>{first_src}</i>"
                if source_count > 1:
                    header_line += f" <i>(+{source_count - 1} more papers)</i>"
                    
                card_elements.append(Paragraph(header_line, q_header_style))
                card_elements.append(Paragraph(f"<i>Category: {q.get('week')} &rsaquo; {q.get('subtopic')}</i>", meta_style))
                card_elements.append(Spacer(1, 3))
                
                # Question Paper Card Image
                card_rel = q.get('card_image')
                has_card = False
                if card_rel:
                    card_full = os.path.join(BASE_DIR, card_rel)
                    if os.path.exists(card_full):
                        try:
                            with PILImage.open(card_full) as im:
                                iw, ih = im.size
                            scale = min(490.0 / iw, 500.0 / ih)
                            w_pt = iw * scale
                            h_pt = ih * scale
                            card_elements.append(Image(card_full, width=w_pt, height=h_pt))
                            card_elements.append(Spacer(1, 4))
                            has_card = True
                        except Exception:
                            pass
                            
                # Fallback text if card image was missing
                if not has_card:
                    stem = q.get('question_text', '').strip() or "[Refer to exam paper]"
                    safe_stem = escape(stem)
                    card_elements.append(Paragraph(safe_stem, q_stem_style))
                    
                # Official Answer
                correct_ans = q.get('correct_answer', [])
                if correct_ans:
                    if q_type in ['MCQ', 'MSQ']:
                        ans_str = ", ".join([f"Option ({a})" for a in correct_ans])
                        card_elements.append(Paragraph(f"&#10004; <b>Official Answer Key:</b> {ans_str}", ans_style))
                    else:
                        val_str = " / ".join([str(a) for a in correct_ans])
                        card_elements.append(Paragraph(f"&#10004; <b>Official Answer Key (Numerical Value):</b> {escape(val_str)}", ans_style))
                else:
                    card_elements.append(Paragraph("&#10004; <b>Official Answer Key:</b> <i>[Refer to detailed question paper]</i>", meta_style))
                    
                card_elements.append(Spacer(1, 6))
                card_elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=8))
                
                story.append(KeepTogether(card_elements))
                
    print("Compiling PDF with NumberedCanvas...")
    doc.build(story, canvasmaker=NumberedCanvas)
    
    file_size_mb = os.path.getsize(OUTPUT_PDF) / (1024 * 1024)
    print(f"\nPDF Compilation Complete!")
    print(f"Destination: {OUTPUT_PDF}")
    print(f"File Size: {file_size_mb:.2f} MB")

if __name__ == "__main__":
    build_pdf()
