import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import openpyxl

def generate_pdf_report(data, title, filename):
    """
    Generates a PDF report using ReportLab.
    
    Args:
        data (list of dict): List of dictionaries containing the data for the table.
        title (str): The title of the report.
        filename (str): The suggested filename (used for the buffer name mostly).
    
    Returns:
        BytesIO: A buffer containing the PDF data.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))

    if data:
        # Create table data
        # Assume all dicts in data have the same keys, use keys as headers
        headers = list(data[0].keys())
        table_data = [headers]
        
        for row in data:
            table_data.append([str(row.get(h, '')) for h in headers])

        # Create the table
        t = Table(table_data)
        
        # Add style to the table
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(t)
    else:
        elements.append(Paragraph("No data available for this report.", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_excel_report(data, filename):
    """
    Generates an Excel report using openpyxl.
    
    Args:
        data (list of dict): List of dictionaries containing data.
        filename (str): The filename.
        
    Returns:
        BytesIO: buffer containing excel file
    """
    buffer = io.BytesIO()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Report"

    if data:
        headers = list(data[0].keys())
        ws.append(headers)
        
        for row in data:
            ws.append([row.get(h, '') for h in headers])
            
    wb.save(buffer)
    buffer.seek(0)
    return buffer

def generate_child_progress_pdf(child, current_progress, previous_progress=None):
    """
    Generates a specific PDF for child progress report.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    elements.append(Paragraph(f"Progress Report: {child.full_name}", styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Child Info
    elements.append(Paragraph(f"<b>Date of Birth:</b> {child.date_of_birth}", styles['Normal']))
    elements.append(Paragraph(f"<b>Status:</b> {child.status}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Current Progress
    elements.append(Paragraph(f"<b>Current Progress ({current_progress.created_on.strftime('%Y-%m-%d')}):</b>", styles['Heading2']))
    elements.append(Paragraph(current_progress.notes, styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Previous Progress Comparison
    if previous_progress:
        elements.append(Paragraph(f"<b>Previous Progress ({previous_progress.created_on.strftime('%Y-%m-%d')}):</b>", styles['Heading2']))
        elements.append(Paragraph(previous_progress.notes, styles['Normal']))
    else:
        elements.append(Paragraph("<b>Previous Progress:</b> No previous records found (First Report).", styles['Normal']))
        
    doc.build(elements)
    buffer.seek(0)
    return buffer
