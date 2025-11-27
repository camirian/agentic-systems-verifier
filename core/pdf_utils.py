import markdown
import io
from xhtml2pdf import pisa

def convert_md_to_pdf(markdown_content):
    """
    Converts Markdown content to a PDF file in memory.
    """
    # 1. Convert Markdown to HTML
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'codehilite'])
    
    # 2. Add Basic Styling
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Helvetica, sans-serif; font-size: 12pt; }}
            h1 {{ color: #2E3440; border-bottom: 2px solid #88C0D0; padding-bottom: 10px; }}
            h2 {{ color: #3B4252; margin-top: 20px; }}
            code {{ background-color: #ECEFF4; padding: 2px; font-family: Courier; }}
            pre {{ background-color: #ECEFF4; padding: 10px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    
    # 3. Generate PDF
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(html_content), dest=pdf_buffer)
    
    if pisa_status.err:
        return None
        
    return pdf_buffer.getvalue()
