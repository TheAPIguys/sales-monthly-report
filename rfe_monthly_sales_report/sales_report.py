import os
import requests

from datetime import datetime


def find_region(data, region):
    """
    Finds and returns the first item in the given data list that matches the specified region.

    Parameters:
    - data (list): A list of dictionaries representing sales data.
    - region (str): The region to search for.

    Returns:
    - dict: The first item in the data list that matches the specified region. If no match is found, an empty dictionary is returned.
    """
    for item in data:
        if item["region"] == region:
            return item
    return {}


def fetch_data(month=7, year=2024):
    """
    Fetches monthly sales report data from a specified URL.
    Returns:
        dict: The JSON response containing the sales report data.
    """
    key = os.environ.get("VINTRACE_KEY")

    url = f"https://rfe-portal.vercel.app/api/budget/sales-report-monthly/?key={key}&month={month}&year={year}"
    request = requests.get(url)
    if request.status_code != 200:
        raise Exception("Failed to fetch data")
    try:
        data = request.json()
        return data
    except:
        raise Exception("Failed to fetch data")


def format_value(value, decimal_places=1, percentage=False, currency=False):
    """
    Formats a number to a specified number of decimal places and optionally formats a percentage.

    :param value: The number to format.
    :param decimal_places: The number of decimal places to round to.
    :param percentage: Optional percentage value to format.
    :return: the formatted number and the formatted percentage if provided.
    """
    if value is None:
        return ""
    formatted_number = round(value, decimal_places)
    if percentage is not False:
        formatted_percentage = f"{str(round(value * 100))}%"
        return formatted_percentage
    else:
        return (
            "$" + format(formatted_number, ",")
            if currency
            else format(formatted_number, ",")
        )


def process_customer_data(data):
    """
    Process the customer data and return a dictionary with formatted values.

    Args:
        data (dict): A dictionary containing the customer data.

    Returns:
        dict: A dictionary with the following keys:
            - "Customer": The customer name, truncated to 20 characters.
            - "Actual Month": The actual month value, formatted as an integer.
            - "Actual YTD": The actual year-to-date value, formatted as an integer.
            - "Budget YTD": The budget year-to-date value, formatted as an integer.
            - "Var %": The year-to-date variance percentage, formatted as an integer with a percentage sign.
            - "Forecast Year": The forecast year value, formatted as an integer.
            - "Budget Year": The budget year value, formatted as an integer.
            - "Var%": The year variance percentage, formatted as an integer with a percentage sign.
    """
    customer_data = {}
    customer_data["Customer"] = data["customer"][:20]
    customer_data["Actual Month"] = format_value(data["actualMonth"], 0)
    customer_data["Actual YTD"] = format_value(data["actualYTD"], 0)
    customer_data["Budget YTD"] = format_value(data["budgetYTD"], 0)
    customer_data["Var %"] = format_value(data["varYTD"], 0, True)
    customer_data["Forecast Year"] = format_value(data["forecastYear"], 0)
    customer_data["Budget Year"] = format_value(data["budgetYear"], 0)
    customer_data["Var%"] = format_value(data["varYear"], 0, True)
    return customer_data


def add_first_page_reports(pdf, data: list[dict], month=7, year=2024):
    """
    Adds the first page of the sales report to the PDF. The first page includes the cases by region and revenue by region. the big wins this month section.

    Args:
        pdf (PDF): The PDF object to add the report to.
        data (dict): A dictionary containing the sales report data.
    """
    pdf.add_page()
    pdf.header()
    today = datetime.strptime(f"{year}-{month}-01", "%Y-%m-%d")
    for i, item in enumerate(data["firstPageCases"]):
        for key, value in item.items():
            if key != "region":
                data["firstPageCases"][i][key] = format_value(value)
            if "var" in key:
                data["firstPageCases"][i][key] = format_value(value, 0, True)

    pdf.center_title(f"RFE MONTHLY SALES REPORT - {today.strftime('%B %Y')}")
    pdf.set_font("helvetica", size=10)
    pdf.cell(0, 10, f"Cases 9 litre equivalent")
    pdf.ln(10)
    pdf.render_table_header(
        [
            "(volume 000's)",
            "Actual Month",
            "Actual YTD",
            "Budget YTD",
            "Var %",
            "Forecast Year",
            "Budget Year",
            "Var %",
        ],
        [0.2, 0.12, 0.12, 0.1, 0.12, 0.12, 0.12, 0.1],
    )
    pdf.render_table_data(
        data["firstPageCases"],
        [0.2, 0.12, 0.12, 0.1, 0.12, 0.12, 0.12, 0.1],
        True,
        True,
    )
    pdf.add_line_break()
    for i, item in enumerate(data["firstPageRevenue"]):
        for key, value in item.items():
            if key != "region":
                data["firstPageRevenue"][i][key] = format_value(value, 0, False, True)
            if "var" in key:
                data["firstPageRevenue"][i][key] = format_value(value, 1, True)

    pdf.set_font("helvetica", size=10)
    pdf.cell(0, 10, f"Revenue in NZD")
    pdf.ln(10)
    pdf.render_table_header(
        [
            "(Value $NZD)",
            "Actual Month",
            "Actual YTD",
            "Budget YTD",
            "Var %",
            "Forecast Year",
            "Budget Year",
            "Var %",
        ],
        [0.2, 0.12, 0.12, 0.1, 0.12, 0.12, 0.12, 0.1],
    )
    pdf.render_table_data(
        data["firstPageRevenue"],
        [0.2, 0.12, 0.12, 0.1, 0.12, 0.12, 0.12, 0.1],
        True,
        True,
    )
    pdf.add_line_break()
    pdf.add_big_wins_cell(
        "BIG WINS THIS MONTH",
        data["bigWins"],
    )
    return pdf


def second_page_brands(pdf, data: list[dict]):
    """
    Renders the second page of the sales report with brands performance.

    Args:
        pdf (PDF): The PDF object to render the page on.
        data (list[dict]): The data containing the brands performance.

    Returns:
        PDF: The updated PDF object.
    """
    ## Second Page Brands performance
    pdf.ln(10)
    pdf.center_title("RFE MONTHLY SALES REPORT - BRANDS PERFORMANCE")
    brands_performance = []
    for brand in data["brandsPerformance"]:
        brands_performance.append(
            {
                "Brand": brand["brand"],
                "Actual YTD": format_value(brand["cases"], 0),
                "Revenue YTD": format_value(brand["revenueYTD"], 0, False, True),
                "Avg Price": format_value(brand["avgPrice"], 2, False, True),
            }
        )
    pdf.render_table_header(
        brands_performance[0].keys(),
        [0.3, 0.2, 0.2, 0.3],
    )
    pdf.render_table_data(
        brands_performance,
        [0.3, 0.2, 0.2, 0.3],
    )
    pdf.add_line_break()
    pdf.ln(10)
    pdf.add_title("Wairau River Sauvignon Blanc")
    wr_sv_data = []
    for customer in data["wrSavPerformance"]:
        wr_sv_data.append(
            {
                "Customer": customer["customer"][:20],
                "Actual Month": format_value(customer.get("actualMonth", 0), 0),
                "Actual YTD": format_value(customer["actualYTD"], 0),
                "Budget YTD": format_value(customer["budgetYTD"], 0),
                "Var %": format_value(customer["varYTD"], 0, True),
                "Forecast Year": format_value(customer["forecastYear"], 0),
                "Budget Year": format_value(customer["budgetYear"], 0),
                "Var  %": format_value(customer["varYear"], 0, True),
            }
        )
    pdf.render_table_header(
        [
            "Customer",
            "Actual Month",
            "Actual YTD",
            "Budget YTD",
            "Var %",
            "Forecast Year",
            "Budget Year",
            "Var  %",
        ],
        [0.2, 0.12, 0.12, 0.1, 0.12, 0.12, 0.12, 0.1],
    )
    pdf.render_table_data(
        wr_sv_data, [0.2, 0.12, 0.12, 0.1, 0.12, 0.12, 0.12, 0.1], True, True
    )
    pdf.add_line_break()
    generate_wine_stocks_chart(data)
    pdf.add_chart("chart.png")
    pdf.add_page()
    return pdf


def third_page(pdf, data: list[dict]):
    """
    Generates the third page of the RFE Monthly Sales Report.
    Args:
        pdf (PDF): The PDF object used for generating the report.
        data (list[dict]): The data used for populating the report.
    Returns:
        PDF: The updated PDF object.
    """
    ## Region complete ## Customer pages
    for r in data["firstPageCases"]:
        if r["region"] == "CASES" or r["region"] == "BULK" or r["region"] == "TOTAL":
            continue
        pdf.ln(10)
        pdf.center_title(f"RFE MONTHLY SALES REPORT - {r['region']}")
        region_activity = ""
        for customer in data["customersReport"]:
            if customer["customer"] == "NZ":
                continue
            if customer["region"] == r["region"]:
                if pdf.will_page_break(30):
                    pdf.add_page()
                    pdf.ln(20)
                region_activity = customer.get("regionActivity", "")
                pdf.set_font("helvetica", size=10)
                pdf.render_table_header(
                    [
                        "Customer / Brand",
                        "Actual Month",
                        "Actual YTD",
                        "Budget YTD",
                        "Var %",
                        "Forecast Year",
                        "Budget Year",
                        "Var %",
                    ],
                    [0.2, 0.12, 0.12, 0.1, 0.12, 0.12, 0.12, 0.1],
                )
                pdf.render_table_data(
                    [process_customer_data(customer)],
                    [0.2, 0.12, 0.12, 0.1, 0.12, 0.12, 0.12, 0.1],
                    True,
                )
                brands = []
                for brand in customer["brands"]:
                    brands.append(
                        {
                            "Customer": brand["brand"],
                            "Actual Month": format_value(brand["actualMonth"], 0),
                            "Actual YTD": format_value(brand["actualYTD"], 0),
                            "Budget YTD": format_value(brand["budgetYTD"], 0),
                            "Var %": format_value(brand["varYTD"], 0, True),
                            "Forecast Year": format_value(brand["forecastYear"], 0),
                            "Budget Year": format_value(brand["budgetYear"], 0),
                            "Var-%": format_value(brand["varYear"], 0, True),
                        }
                    )
                if len(brands) != 0:
                    pdf.render_table_data(
                        brands,
                        [0.2, 0.12, 0.12, 0.1, 0.12, 0.12, 0.12, 0.1],
                        False,
                        True,
                    )
                pdf.add_customer_status(
                    customer["thisMonth"],
                    customer["lastMonth"],
                    customer["comments"],
                    customer["country"],
                )
                pdf.add_line_break()
        pdf.add_big_wins_cell(
            r["region"] + " OTHER ACTIVITY",
            region_activity,
        )
    ## BULK PAGE REPORT
    pdf.ln(15)
    pdf.center_title("RFE MONTHLY SALES REPORT - BULK SALES")
    cleaned_data = []
    for bulk_customer in data["bulkReport"]:
        cleaned_data.append(
            {
                "Customer": bulk_customer["customerName"],
                "Actual YTD": format_value(bulk_customer["actualYTD"], 0),
                "Forecast Year": format_value(bulk_customer["forecastYear"], 0),
                "Comments": bulk_customer["comments"],
            }
        )

    pdf.set_font("helvetica", size=10)
    pdf.render_table_header(
        cleaned_data[0].keys(),
        [0.3, 0.1, 0.1, 0.5],
    )
    pdf.render_bulk_table(
        cleaned_data,
        [0.3, 0.1, 0.1, 0.5],
    )
    pdf.add_line_break()
    return pdf


def generate_wine_stocks_chart(data: list[dict]):
    import matplotlib.pyplot as plt

    months = []
    cases = []
    forecasts = []

    for item in data["budgetVsForecastMonthly"]:
        month_year = datetime.strptime(item["month_year"], "%m-%Y").strftime("%b %Y")
        months.append(month_year)
        cases.append(item["cases"])
        forecasts.append(item["forecast"])
        # Create the line chart
        plt.figure(figsize=(10, 6))
        plt.plot(months, cases, label="Budget", marker="o")
        plt.plot(months, forecasts, label="Forecast", marker="o")
        # Add titles and labels
        plt.title("Wine Stocks")
        plt.xlabel("Month-Year")
        plt.ylabel("Cases 9L equivalent")
        plt.xticks(rotation=45)
        plt.legend()
        # Save the chart as a PNG file
        plt.tight_layout()
        plt.savefig("chart.png")
        plt.close()


def export_body_encoded(pdf):
    import base64

    content = pdf.output(dest="S")
    return base64.b64encode(content).decode("utf-8")
