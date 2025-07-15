from flask import Flask, request, jsonify, send_file
import fitz  # PyMuPDF
import base64
from io import BytesIO

app = Flask(__name__)

@app.route('/add-signature', methods=['POST'])
def add_signature():
    try:
        if 'file' not in request.files or 'signature_base64' not in request.form:
            return jsonify({'error': 'Missing file or signature_base64'}), 400

        uploaded_file = request.files['file']
        signature_base64 = request.form['signature_base64']
        signature_bytes = base64.b64decode(signature_base64)

        # Load PDF
        pdf_bytes = uploaded_file.read()
        pdf_stream = BytesIO(pdf_bytes)
        doc = fitz.open(stream=pdf_stream, filetype="pdf")

        # Load the image as a pixmap using fitz.open
        img_doc = fitz.open("png", signature_bytes)
        signature_image = img_doc[0].get_pixmap()

        # Target the last page
        page = doc[-1]

        # Define position for the image (bottom-right)
        padding = 40
        image_width = 150
        image_height = 50
        page_width = page.rect.width
        page_height = page.rect.height
        x0 = page_width - image_width - padding
        y0 = page_height - image_height - padding
        x1 = x0 + image_width
        y1 = y0 + image_height

        # Insert the image
        page.insert_image(fitz.Rect(x0, y0, x1, y1), pixmap=signature_image)

        # Return new PDF
        output_stream = BytesIO()
        doc.save(output_stream)
        doc.close()
        output_stream.seek(0)

        return send_file(output_stream, download_name="signed.pdf", mimetype="application/pdf")

    except Exception as e:
        return jsonify({'error': str(e)}), 500
