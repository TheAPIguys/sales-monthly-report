import json
from fpdf import FPDF
from datetime import datetime
import urllib.request
import os
import pytz

from sales_report import (
    add_first_page_reports,
    export_body_encoded,
    fetch_data,
    second_page_brands,
    third_page,
)

NZT = pytz.timezone("Pacific/Auckland")

os.chdir("/tmp")

DATE_FORMAT = "%d %b, %Y"
RFE_LOGO = "https://images2.imgbox.com/28/32/3Wdfx842_o.png"
urllib.request.urlretrieve(
    RFE_LOGO,
    "rfe_logo.png",
)


class PDF(FPDF):
    def header(self):
        self.image("rfe_logo.png", (self.w / 2) - 15, 5, 15, 15)
        with self.local_context(fill_opacity=0.5, stroke_opacity=0.5):
            self.set_line_width(0.5)
            self.set_draw_color(142, 127, 85)
            self.line(self.w - self.epw - 10, 15 + 7, self.epw + 10, 15 + 7)
            # Performing a line break:
        self.set_font("helvetica", size=10)
        self.ln(5)

    def add_line_break(self):
        self.ln(3)
        with self.local_context(fill_opacity=0.5, stroke_opacity=0.5):
            self.set_line_width(0.5)
            self.set_draw_color(142, 127, 85)
            self.line(self.w - self.epw - 10, self.get_y(), self.epw + 10, self.get_y())
            # Performing a line break:
        self.ln(3)

    def footer(self):
        # Setting position at 1.5 cm from bottom:
        self.set_y(-15)
        # Setting font: helvetica italic 8
        self.set_font("helvetica", "I", 8)
        # Setting text color to gray:
        self.set_text_color(128)
        # Printing page number
        self.cell(0, 10, f"Page {self.page_no()}", align="R")

    def filter_unsupported_characters(self, text):
        supported_characters = (
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?()'- "
        )
        return "".join(c for c in text if c in supported_characters)

    def add_big_wins_cell(self, title: str, text: str):
        if self.will_page_break(40):
            self.add_page()
            self.ln(20)
        self.ln(5)
        self.set_font("helvetica", "U", 14)  # Set font for the big cell text
        self.set_fill_color(255, 255, 255)  # Set fill color for the big cell
        self.set_draw_color(142, 127, 85)  # Set border color for the big cell

        remaining_height = self.h - self.get_y() - self.b_margin
        start_y = self.y
        self.cell(0, remaining_height, "", border=1, align="L")
        self.x = self.l_margin
        self.y = start_y + 3
        self.cell(0, 10, title, align="L")
        self.set_font("Times", size=10, style="I")
        self.x = self.l_margin
        self.y = self.y + 15

        self.write_html(
            text,
            align="L",
            max_line_height=6,
        )
        ## pass to the next page now
        self.add_page()

    def add_customer_status(
        self, this_month: str, last_month: str, comments: str, country="Country"
    ):
        self.set_font("helvetica", size=10)
        if self.will_page_break(30):
            self.add_page()
            self.ln(20)
        start_y = self.y
        first_w = 0.2 * self.epw
        second_w = 0.12 * self.epw
        with self.local_context(stroke_opacity=0.5, fill_opacity=1):
            self.set_draw_color(142, 127, 85)
            self.cell(first_w, 8, country, align="R", border=1)
        self.y = start_y
        with self.local_context(stroke_opacity=0.5, fill_opacity=1):
            self.set_draw_color(142, 127, 85)
            self.cell(second_w, 8, f"This Month", align="R", border=1)
        self.y = start_y

        with self.local_context(stroke_opacity=0.5, fill_opacity=1):
            self.set_draw_color(142, 127, 85)
            if this_month == "Green":
                self.set_fill_color(74, 222, 128)
            elif this_month == "Orange":
                self.set_fill_color(251, 146, 60)
            else:
                self.set_fill_color(248, 113, 113)
            self.cell(second_w, 8, "", align="R", border=1, fill=True)
            self.set_fill_color(255, 255, 255)
        self.y = start_y
        with self.local_context(stroke_opacity=0.5, fill_opacity=1):
            self.set_draw_color(142, 127, 85)
            self.cell(second_w, 8, f"Last Month", align="R", border=1)
        self.y = start_y
        with self.local_context(stroke_opacity=0.5, fill_opacity=1):
            self.set_draw_color(142, 127, 85)
            if last_month == "Green":
                self.set_fill_color(74, 222, 128)
            elif last_month == "Orange":
                self.set_fill_color(251, 146, 60)
            else:
                self.set_fill_color(248, 113, 113)
            self.cell(second_w, 8, "", align="R", border=1, fill=True)
            self.set_fill_color(255, 255, 255)
        with self.local_context(stroke_opacity=0.5, fill_opacity=1):
            self.set_draw_color(142, 127, 85)
            self.cell(
                self.epw - first_w - (second_w * 4), 8, "Status", align="L", border=1
            )
        self.ln(8)
        if self.will_page_break(15):
            self.ln(25)
        start_y = self.y
        with self.local_context(stroke_opacity=0.5, fill_opacity=1):
            self.set_draw_color(142, 127, 85)
            self.cell(first_w, 10, f"Comments", align="R", border=1)
        self.y = start_y
        with self.local_context(stroke_opacity=0.5, fill_opacity=1):
            self.set_draw_color(142, 127, 85)
            self.set_font("helvetica", size=8, style="I")
            self.multi_cell(
                self.epw - first_w, 10, comments, align="L", border=1, max_line_height=5
            )

        self.ln(5)

    def add_date_of_report(self):
        date = datetime.now(NZT).strftime(DATE_FORMAT)
        self.set_font("helvetica", size=10, style="B")
        self.ln(self.font_size * 2)
        self.cell(txt=f"Date: {date}")

    def add_title(self, title):
        self.set_font("helvetica", size=12, style="B")
        line_height = self.font_size * 2
        self.cell(txt=title, align="L")
        self.ln(line_height + 5)

    def center_title(self, title):
        self.set_font("helvetica", size=20)
        line_height = self.font_size * 2
        width = self.get_string_width(title)  # self.title
        self.set_x = (self.x / 2) - (width / 2)  # type: ignore
        self.cell(
            0,
            18,
            txt=title,
            align="C",
        )
        self.ln(line_height)

    def render_table_header(self, table_headers: list, columns_size: list):
        self.set_font("helvetica", "I", 8)
        self.set_font(style="B")  # enabling bold text
        line_height = self.font_size * 2
        index = 0
        for col_name in table_headers:
            col_width = columns_size[index] * self.epw
            self.cell(col_width, line_height, col_name, border=False, align="C")
            index += 1
        self.ln(line_height)
        with self.local_context(fill_opacity=0.5, stroke_opacity=0.5):
            self.set_line_width(0.5)
            self.set_draw_color(142, 127, 85)
            self.line(self.w - self.epw - 10, self.get_y(), self.epw + 10, self.get_y())

        self.set_font(style="")  # disabling bold text

    def render_table_data(
        self, table_data, columns_size: list, highlight_last_row=True, line_break=False
    ):
        first_line = []
        second_line = []
        last_line = []
        line_height = self.font_size * 2
        # distribute content evenly
        col_width = self.epw / len(table_data[0].keys())

        for i, row in enumerate(table_data):
            index = 0
            if self.will_page_break(line_height):
                self.add_page()
                self.ln(10)
                self.render_table_header(table_data[0].keys(), columns_size)
            row_cases = False
            key_num = 0
            for key, value in row.items():
                col_width = columns_size[index] * self.epw
                index += 1
                if key == "region":
                    row_cases = value == "CASES"

                if row_cases:
                    with self.local_context(stroke_opacity=0.5, fill_opacity=0.7):
                        self.set_draw_color(142, 127, 85)
                        self.set_fill_color(199, 191, 170)
                        if "-" in value:
                            self.set_text_color(185, 28, 28)
                        else:
                            self.set_text_color(0, 0, 0)

                        self.set_font(style="B")
                        self.cell(
                            col_width,
                            line_height,
                            value,
                            border=True,
                            align="R",
                            fill=True,
                        )
                    if key_num == 0 and (i == 0 or i == len(table_data) - 1):
                        first_line.append(self.get_x())
                        first_line.append(self.get_y() - line_height)
                    if key_num == 4 and (i == 0 or i == len(table_data) - 1):
                        second_line.append(self.get_x())
                        second_line.append(self.get_y() - line_height)
                    if key_num == 7 and (i == 0 or i == len(table_data) - 1):
                        last_line.append(self.get_x())
                        last_line.append(self.get_y() - line_height)

                    key_num += 1
                    continue

                # Ensure value is a string
                if isinstance(value, dict):
                    value = str(value)  # Convert dictionary to string

                if i == len(table_data) - 1 and highlight_last_row:
                    with self.local_context(stroke_opacity=0.5, fill_opacity=1):
                        self.set_draw_color(142, 127, 85)
                        self.set_fill_color(199, 191, 170)
                        if "-" in value:
                            self.set_text_color(185, 28, 28)
                        else:
                            self.set_text_color(0, 0, 0)

                        self.set_font(style="B")
                        self.cell(
                            col_width,
                            line_height,
                            value,
                            border=True,
                            align="R",
                            fill=True,
                        )

                else:
                    with self.local_context(stroke_opacity=0.5):
                        self.set_draw_color(142, 127, 85)
                        if "-" in value:
                            self.set_text_color(185, 28, 28)
                        else:
                            self.set_text_color(0, 0, 0)
                        self.cell(col_width, line_height, value, border=True, align="R")
                if key_num == 0 and (i == 0 or i == len(table_data) - 1):
                    first_line.append(self.get_x())
                    first_line.append(self.get_y() - line_height)
                if key_num == 4 and (i == 0 or i == len(table_data) - 1):
                    second_line.append(self.get_x())
                    second_line.append(self.get_y() - line_height)
                if key_num == 7 and (i == 0 or i == len(table_data) - 1):
                    last_line.append(self.get_x())
                    last_line.append(self.get_y() - line_height)
                key_num += 1

            self.ln(line_height)
        if line_break:
            with self.local_context(stroke_opacity=1, fill_opacity=1):
                self.set_draw_color(142, 127, 85)
                self.set_line_width(0.7)
                self.line(first_line[0], first_line[1], first_line[0], self.get_y())
            with self.local_context(stroke_opacity=1, fill_opacity=1):
                self.set_draw_color(142, 127, 85)
                self.set_line_width(0.7)
                self.line(second_line[0], second_line[1], second_line[0], self.get_y())
            with self.local_context(stroke_opacity=1, fill_opacity=1):
                self.set_draw_color(142, 127, 85)
                self.set_line_width(0.7)
                self.line(last_line[0], last_line[1], last_line[0], self.get_y())

    def render_bulk_table(
        self, table_data, columns_size: list, highlight_last_row=True
    ):
        line_height = self.font_size * 2

        for i, row in enumerate(table_data):
            index = 0
            max_height = line_height
            if self.will_page_break(line_height):
                self.add_page()
                self.ln(10)
                self.render_table_header(table_data[0].keys(), columns_size)
            row_cases = False

            # First pass: calculate maximum cell height
            for key, value in row.items():
                col_width = columns_size[index] * self.epw
                if key == "Comments":
                    # Calculate height of multi-cell
                    text_height = self.get_string_height(col_width, str(value))
                    if text_height > max_height:
                        max_height = text_height
                index += 1

            # Reset index for second pass
            index = 0

            # Second pass: render cells
            for key, value in row.items():
                col_width = columns_size[index] * self.epw
                index += 1
                if key == "region":
                    row_cases = value == "CASES"

                # Ensure value is a string
                if isinstance(value, dict):
                    value = str(value)  # Convert dictionary to string

                if row_cases:
                    self.render_special_cell(col_width, max_height, value, True)
                elif i == len(table_data) - 1 and highlight_last_row:
                    self.render_special_cell(col_width, max_height, value, False)
                else:
                    if key == "Comments":
                        self.line_height = 8
                        self.set_font(style="I")  # Italic style for comments
                        self.multi_cell(
                            col_width,
                            line_height,
                            value,
                            border=1,
                            align="L",
                            wrapmode="word",
                        )
                        # Move cursor back up to top of cell
                        self.set_y(self.get_y() - max_height)
                        self.set_font(style="")  # Reset to default style
                    else:
                        with self.local_context(stroke_opacity=0.5):
                            self.set_draw_color(142, 127, 85)
                            if "-" in value:
                                self.set_text_color(185, 28, 28)
                            else:
                                self.set_text_color(0, 0, 0)
                            self.cell(
                                col_width, max_height, value, border=True, align="R"
                            )

            self.ln(max_height)

    def render_special_cell(self, width, height, value, is_cases):
        with self.local_context(
            stroke_opacity=0.5, fill_opacity=0.7 if is_cases else 1
        ):
            self.set_draw_color(142, 127, 85)
            self.set_fill_color(199, 191, 170)
            if "-" in value:
                self.set_text_color(185, 28, 28)
            else:
                self.set_text_color(0, 0, 0)
            self.set_font(style="B")
            self.cell(width, height, value, border=True, align="R", fill=True)

    def get_string_height(self, width, txt):
        self.set_font(style="")  # Reset to default style
        return self.get_string_width(txt) / width * self.font_size * 1.5

    def add_chart(self, filename):
        remaining_height = self.h - self.get_y() - self.b_margin

        self.image(
            filename,
            x=self.l_margin,
            y=self.get_y(),
            w=self.epw,
            h=remaining_height,
            keep_aspect_ratio=True,
        )


if __name__ == "__main__":

    def mock_data():
        ## open the json file data
        with open("data.json", "r") as file:
            data = json.load(file)
        return data

    data = mock_data()

    pdf = PDF()
    pdf = add_first_page_reports(pdf, data)
    pdf = second_page_brands(pdf, data)
    pdf = third_page(pdf, data)
    today = datetime.strptime("2024-07-01", "%Y-%m-%d")
    pdf.output(f"RFE MONTHLY SALES REPORT - {today.strftime('%B %Y')}.pdf")

    print("PDF Generated")
