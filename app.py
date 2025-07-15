from flask import Flask, request, jsonify, send_file
import fitz  # PyMuPDF
import base64
from io import BytesIO
import os

app = Flask(__name__)

@app.route('/add-signature', methods=['POST'])
def add_signature():
    try:
        if 'file' not in request.files or 'signature_base64' not in request.form:
            return jsonify({'error': 'Missing file or signature_base64'}), 400

        uploaded_file = request.files['file']
        signature_base64 = request.form['signature_base64']
        signature_bytes = base64.b64decode(signature_base64)

        pdf_stream = BytesIO(uploaded_file.read())
        doc = fitz.open(stream=pdf_stream, filetype="pdf")

        signature_image = fitz.Pixmap(signature_bytes)
        page = doc[-1]
        padding = 40
        image_width = 150
        image_height = 50
        page_width = page.rect.width
        page_height = page.rect.height
        x0 = page_width - image_width - padding
        y0 = page_height - image_height - padding
        page.insert_image(fitz.Rect(x0, y0, x0 + image_width, y0 + image_height), pixmap=signature_image)

        output_stream = BytesIO()
        doc.save(output_stream)
        doc.close()
        output_stream.seek(0)

        return send_file(output_stream, download_name="signed.pdf", mimetype="application/pdf")

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
