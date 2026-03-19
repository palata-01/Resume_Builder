from io import BytesIO
from math import ceil

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from pypdf import PdfReader, PdfWriter


def calculate_resume_stats(resume):
    text_parts = [
        resume.full_name or "",
        resume.title or "",
        resume.summary or "",
        " ".join(resume.skills or []),
        " ".join([str(x) for x in resume.education or []]),
        " ".join([str(x) for x in resume.experience or []]),
        " ".join([str(x) for x in resume.projects or []]),
        " ".join([str(x) for x in resume.certifications or []]),
    ]
    text = " ".join(text_parts).strip()

    words = len(text.split()) if text else 0
    characters = len(text)
    paragraphs = len([p for p in (resume.summary or "").split("\n") if p.strip()])
    reading_time = max(1, ceil(words / 200)) if words else 1

    return words, characters, paragraphs, reading_time


def draw_multiline_text(pdf, text, x, y, width, font_name="Helvetica", font_size=11, line_gap=16):
    lines = simpleSplit(text, font_name, font_size, width)
    for line in lines:
        pdf.drawString(x, y, line)
        y -= line_gap
    return y


def generate_pdf(resume):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    x = 50
    y = height - 50
    content_width = width - 100

    def new_page_if_needed(current_y, needed=80):
        nonlocal y
        if current_y < needed:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 11)
            return y
        return current_y

    pdf.setTitle(resume.resume_id or "Resume")

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(x, y, resume.full_name or "Resume")
    y -= 25

    pdf.setFont("Helvetica", 11)
    contact = f"{resume.email or ''} | {resume.phone or ''}"
    pdf.drawString(x, y, contact)
    y -= 20

    if resume.title:
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(x, y, resume.title)
        y -= 25

    def section(title, items, is_list=False):
        nonlocal y
        if not items:
            return

        y = new_page_if_needed(y)

        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(x, y, title)
        y -= 18

        pdf.setFont("Helvetica", 11)

        if is_list:
            for item in items:
                y = new_page_if_needed(y)
                bullet_text = f"• {str(item)}"
                y = draw_multiline_text(pdf, bullet_text, x + 10, y, content_width - 10)
                y -= 6
        else:
            y = draw_multiline_text(pdf, str(items), x, y, content_width)
            y -= 10

    section("Summary", resume.summary or "")
    section("Skills", resume.skills or [], is_list=True)
    section("Education", resume.education or [], is_list=True)
    section("Experience", resume.experience or [], is_list=True)
    section("Projects", resume.projects or [], is_list=True)
    section("Certifications", resume.certifications or [], is_list=True)

    pdf.save()
    buffer.seek(0)
    return buffer


def protect_pdf(pdf_buffer, password):
    reader = PdfReader(pdf_buffer)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)

    protected_pdf = BytesIO()
    writer.write(protected_pdf)
    protected_pdf.seek(0)
    return protected_pdf