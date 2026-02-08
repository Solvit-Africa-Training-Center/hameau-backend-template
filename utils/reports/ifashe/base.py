from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from openpyxl import Workbook


class BasePDFReport:
    title = "IFASHE Report"

    def __init__(self, file_path):
        self.file_path = file_path
        self.styles = getSampleStyleSheet()
        self.elements = []

    def add_title(self):
        self.elements.append(Paragraph(f"<b>{self.title}</b>", self.styles["Title"]))

    def add_table(self, headers, rows):
        table = Table([headers] + rows, repeatRows=1)
        self.elements.append(table)

    def build(self):
        doc = SimpleDocTemplate(
            self.file_path,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )
        doc.build(self.elements)


class BaseExcelReport:
    def __init__(self):
        self.wb = Workbook(write_only=True)
