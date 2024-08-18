import base64
from datetime import datetime
import json
import os
import pytz
from sales_report import (
    export_body_encoded,
    fetch_data,
    add_first_page_reports,
    second_page_brands,
    third_page,
)

NZT = pytz.timezone("Pacific/Auckland")

from report_pdf import PDF


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    try:
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
        pdf_content = export_body_encoded(pdf)
        print("PDF Generated")
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/pdf",
                "Content-Disposition": 'attachment; filename="RFE-SALES-MONTHLY-REPORT.pdf"',
            },
            "body": pdf_content,
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
