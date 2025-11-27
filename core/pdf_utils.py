import markdown
import io
from xhtml2pdf import pisa

def convert_md_to_pdf(markdown_content):
    """
    Converts Markdown content to a PDF file in memory.
    """
    # 1. Convert Markdown to HTML
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'codehilite'])
    
    # 2. Add Styling (Professional Look)
    html_content = f"""
    <html>
    <head>
        <style>
            @page {{
                size: letter;
                margin: 2.5cm;
            }}
            body {{
                font-family: Helvetica, sans-serif;
                line-height: 1.6;
                font-size: 11pt;
                color: #2E3440;
            }}
            h1 {{
                color: #2E3440;
                border-bottom: 2px solid #88C0D0;
                padding-bottom: 10px;
                margin-top: 0;
            }}
            h2 {{
                color: #3B4252;
                margin-top: 20px;
                border-bottom: 1px solid #E5E9F0;
            }}
            h3 {{
                color: #434C5E;
                margin-top: 15px;
            }}
            p {{
                margin-bottom: 10px;
                text-align: justify;
            }}
            code {{
                background-color: #ECEFF4;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: Courier, monospace;
                font-size: 0.9em;
            }}
            pre {{
                background-color: #ECEFF4;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #D8DEE9;
                white-space: pre-wrap;
            }}
            blockquote {{
                border-left: 4px solid #88C0D0;
                padding-left: 15px;
                color: #4C566A;
                font-style: italic;
            }}
            ul, ol {{
                margin-bottom: 10px;
            }}
            li {{
                margin-bottom: 5px;
            }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    
    # 3. Generate PDF
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(src=html_content, dest=result)
    
    if pisa_status.err:
        return None
        
    return result.getvalue()
