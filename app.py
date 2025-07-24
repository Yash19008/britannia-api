from flask import Flask, request, jsonify
import pdfplumber
import re

app = Flask(__name__)

@app.route('/extract-sale-goods', methods=['POST'])
def extract_goods():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Only PDF files allowed'}), 400

    goods = []
    invoice_no = None
    invoice_date = None

    with pdfplumber.open(file.stream) as pdf:
        if len(pdf.pages) < 1:
            return jsonify({'error': 'PDF has no pages'}), 400

        page = pdf.pages[0]
        text = page.extract_text()

        for line in text.split('\n'):
            if re.match(r'^\d+\s+.+?\s+\d{1,3}(,?\d+)*\s+.*Pcs', line):
                goods.append(line.strip())

        # Match invoice number, e-Way Bill, and date based on known positions
        invoice_line_match = re.search(
            r'Invoice No\. e-Way Bill No\. Dated\s*\n(?:.*?\s)?(\d+)\s+(\d{12})\s+(\d{1,2}-[A-Za-z]{3}-\d{2,4})',
            text
        )

        if invoice_line_match:
            invoice_no = invoice_line_match.group(1)       # Correctly captures '50'
            # e_way_bill = invoice_line_match.group(2)     # '382007970378' if needed
            invoice_date = invoice_line_match.group(3)      # '27-May-25'

    return jsonify({
        'invoice_number': invoice_no,
        'invoice_date': invoice_date,
        'sold_goods': goods
    })

if __name__ == '__main__':
    app.run(debug=True)
