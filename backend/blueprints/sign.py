"""
PDF Signing Blueprint
Provides endpoint to add text-based signatures to PDF documents.
"""

import fitz
import io
from flask import Blueprint, request
from utils.helpers import error, send_file_and_cleanup
from utils.validators import validate_uploaded_file, validate_pdf_file

sign_bp = Blueprint("sign", __name__)


@sign_bp.route("/sign/signPdf", methods=["POST"])
def sign_pdf():
    """
    Sign a PDF by adding signature text to the document.

    Expected form data:
    - file: PDF file to sign
    - signature: Signature text to add
    - position: (Optional) Position of signature (bottom-right, bottom-left, top-right, top-left, center)
    - font_size: (Optional) Size of the signature text (default: 14)
    - color: (Optional) Hex color code for the signature text (default: 000099 - dark blue)

    Returns:
    - PDF file with signature stamped on the last page.
    """
    doc = None
    try:
        # Validate uploaded file
        pdf_file, filename, upload_error = validate_uploaded_file(request, "file")
        if upload_error:
            return upload_error

        # Validate PDF extension
        pdf_error = validate_pdf_file(filename)
        if pdf_error:
            return pdf_error

        # Get signature text
        signature_text = request.form.get("signature", "").strip()
        if not signature_text:
            return error("Signature text is required", 400)

        # Get optional parameters
        position = request.form.get("position", "bottom-right")
        try:
            font_size = int(request.form.get("font_size", 14))
        except (ValueError, TypeError):
            font_size = 14

        color_hex = request.form.get("color", "000099").lstrip("#")
        try:
            # Convert hex to RGB values between 0 and 1
            color_rgb = tuple(int(color_hex[i:i+2], 16) / 255 for i in (0, 2, 4))
        except (ValueError, IndexError):
            color_rgb = (0, 0, 0.6)  # Default dark blue

        # Process PDF
        pdf_bytes = pdf_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        if len(doc) == 0:
            return error("The PDF document has no pages", 400)

        # Stamp signature text on the last page
        page = doc[-1]
        
        # Define possible positions
        positions = {
            "bottom-right": (page.rect.width - 220, page.rect.height - 60, page.rect.width - 20, page.rect.height - 20),
            "bottom-left": (20, page.rect.height - 60, 220, page.rect.height - 20),
            "top-right": (page.rect.width - 220, 20, page.rect.width - 20, 60),
            "top-left": (20, 20, 220, 60),
            "center": ((page.rect.width - 200) / 2, (page.rect.height - 40) / 2, (page.rect.width + 200) / 2, (page.rect.height + 40) / 2),
        }

        coord = positions.get(position, positions["bottom-right"])
        rect = fitz.Rect(*coord)
        
        # Insert text with specified properties
        page.insert_textbox(
            rect, 
            signature_text, 
            fontsize=font_size, 
            color=color_rgb,
            align=fitz.TEXT_ALIGN_CENTER if position == "center" else fitz.TEXT_ALIGN_LEFT
        )

        # Save to memory
        out = io.BytesIO()
        doc.save(out)
        out.seek(0)

        return send_file_and_cleanup(
            out.getvalue(),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="signed.pdf",
        )

    except Exception as e:
        return error(f"Failed to sign PDF: {str(e)}", 500)
    finally:
        if doc:
            doc.close()
