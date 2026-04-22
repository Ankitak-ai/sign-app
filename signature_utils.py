from __future__ import annotations

from datetime import date
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def typed_signature_to_png_bytes(signature_text: str) -> bytes:
    img = Image.new("RGBA", (700, 220), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 72)
    except OSError:
        font = ImageFont.load_default()
    draw.text((20, 60), signature_text, fill=(20, 20, 20, 255), font=font)
    out = BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


def normalize_signature_image(file_bytes: bytes, max_w: int = 700, max_h: int = 220) -> bytes:
    image = Image.open(BytesIO(file_bytes)).convert("RGBA")
    image.thumbnail((max_w, max_h))
    out = BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


def apply_signature_to_pdf(pdf_bytes: bytes, signature_png_bytes: bytes) -> bytes:
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)

    page_w, page_h = A4
    sig_w = 5.2 * 72 / 2.54
    sig_h = 1.5 * 72 / 2.54
    x = page_w - 8.7 * 72 / 2.54
    y = 3.6 * 72 / 2.54

    signature = ImageReader(BytesIO(signature_png_bytes))
    c.drawImage(signature, x, y, width=sig_w, height=sig_h, preserveAspectRatio=True, mask="auto")
    c.setFont("Helvetica", 10)
    c.drawString(page_w - 8.7 * 72 / 2.54, 2.4 * 72 / 2.54, f"Date: {date.today().strftime('%d/%m/%Y')}")
    c.save()

    packet.seek(0)
    overlay_reader = PdfReader(packet)
    original_reader = PdfReader(BytesIO(pdf_bytes))

    writer = PdfWriter()
    last_page_index = len(original_reader.pages) - 1
    for i, page in enumerate(original_reader.pages):
        if i == last_page_index:
            page.merge_page(overlay_reader.pages[0])
        writer.add_page(page)

    out = BytesIO()
    writer.write(out)
    return out.getvalue()
