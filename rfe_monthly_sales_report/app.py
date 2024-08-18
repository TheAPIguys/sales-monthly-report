import base64
from datetime import datetime
import json
import os
import pytz
from sales_report import (
    fetch_data,
    add_first_page_reports,
    second_page_brands,
    third_page,
)

NZT = pytz.timezone("Pacific/Auckland")

from report_pdf import PDF
import io


def generate_pdf_stream():
    data = fetch_data()
    pdf = PDF()
    pdf = add_first_page_reports(
        pdf,
        data,
        """* Liquorland NZ core range WR Pinot Gris * start 1st September (175 stores)
 * New World Wine Awards Top 50 WRSB24. This will drive serious 
 volume of the SB. We will need to allocate all remaining SB23 to 
 other accounts other than Foodstuffs.
 * 105k SB24 bulk sold to Booster. Potential for more
 * Wairau River is named a 2023 Impact Hot Prospect Brand 
 (2nd year in a row!) The 2023 Hot Prospects will be featured in the 
 Sept 1 & 15th issue of Impact and the October issue of Market 
 Watch
 """,
    )
    pdf = second_page_brands(pdf, data)
    pdf = third_page(pdf, data)

    # Create a BytesIO object to simulate streaming
    pdf_stream = io.BytesIO()
    pdf.output(pdf_stream, dest="F")
    pdf_stream.seek(0)

    return pdf_stream


def lambda_handler(event, context):
    try:
        # Generate the PDF stream
        pdf_stream = generate_pdf_stream()

        # Read the stream in chunks and encode in Base64
        chunks = []
        for chunk in iter(lambda: pdf_stream.read(4096), b""):
            chunks.append(base64.b64encode(chunk).decode("utf-8"))

        # Prepare the response
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/pdf",
                "Content-Disposition": 'attachment; filename="generated_pdf.pdf"',
            },
            "body": "".join(chunks),
            "isBase64Encoded": True,
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "message": f"An error occurred: {e}",
                }
            ),
        }
