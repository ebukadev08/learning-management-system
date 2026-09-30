import os
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

CERTIFICATES_DIR = os.path.join("uploads", "certificates")
os.makedirs(CERTIFICATES_DIR, exist_ok=True)

def generate_certificate_pdf(student_name: str, course_title: str, certificate_id: int) -> str:
    """
    Builds a simple landscape certificate PDF and returns the file path
    it was saved to (relative, safe to store in the DB).
    """

    filename = f"certificate_{certificate_id}.pdf"
    filepath = os.path.join(CERTIFICATES_DIR, filename)

    page_width, page_height = landscape(A4)
    c = canvas.Canvas(filepath, pagesize=landscape(A4)) 

    # Border
    c.setStrokeColor(HexColor("#2c3e50"))
    c.setLineWidth(3)
    c.rect(1.5 * cm, 1.5 * cm, page_width - 3 * cm, page_height - 3 * cm)

    # Title
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(HexColor("#2c3e50"))
    c.drawCentredString(page_width / 2, page_height - 4 * cm, "Certificate of Completion")

    # "This certifies that"
    c.setFont("Helvetica", 14)
    c.setFillColor(HexColor("#555555"))
    c.drawCentredString(page_width / 2, page_height - 6 * cm, "This certifies that")

    # Student name
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(HexColor("#000000"))
    c.drawCentredString(page_width / 2, page_height - 7.5 * cm, student_name)

    # "has successfully completed"
    c.setFont("Helvetica", 14)
    c.setFillColor(HexColor("#555555"))
    c.drawCentredString(page_width / 2, page_height - 9 * cm, "has successfully completed the course")

    # Course title
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(HexColor("#2c3e50"))
    c.drawCentredString(page_width / 2, page_height - 10.5 * cm, course_title)

    # Date + certificate ID footer
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#888888"))
    issue_date = datetime.utcnow().strftime("%B %d, %Y")
    c.drawCentredString(page_width / 2, 3 * cm, f"Issued on {issue_date}  •  Certificate ID: {certificate_id}")

    c.save()
    return filepath