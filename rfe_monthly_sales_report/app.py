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

# Set the MPLCONFIGDIR environment variable
os.environ["MPLCONFIGDIR"] = "/tmp"


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
    ## get month and year from the query string
    month = int(event["queryStringParameters"]["month"])
    year = int(event["queryStringParameters"]["year"])
    try:
        data = fetch_data(month=month, year=year)
        pdf = PDF()
        pdf = add_first_page_reports(pdf, data)
        pdf = second_page_brands(pdf, data)
        pdf = third_page(pdf, data)
        pdf_content = export_body_encoded(pdf)
        print("PDF Generated")
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/pdf",
                "Content-Disposition": f'attachment; filename="rfe_sales_monthly_report_{month}-{year}.pdf"',
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
