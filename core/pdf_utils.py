from fpdf import FPDF
import io

class MarkdownPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.cell(0, 10, 'Project Documentation', new_x="LMARGIN", new_y="NEXT", align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def chapter_title(self, label):
        self.set_font('Helvetica', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, label, new_x="LMARGIN", new_y="NEXT", align='L', fill=True)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Helvetica', '', 11)
        self.multi_cell(0, 5, body)
        self.ln()

def clean_text(text):
    """
    Sanitize text for FPDF (Latin-1).
    Replaces unsupported characters (like emojis) with '?' or removes them.
    """
    return text.encode('latin-1', 'replace').decode('latin-1')

def convert_md_to_pdf(markdown_content):
    """
    Converts Markdown content to a PDF file in memory using FPDF2.
    This is a simplified converter that handles basic text and headers.
    """
    try:
        pdf = MarkdownPDF()
        pdf.add_page()
        
        # Simple parsing: Treat lines starting with # as headers
        lines = markdown_content.split('\n')
        
        body_buffer = ""
        
        for line in lines:
            stripped = line.strip()
            # Sanitize line
            clean_line = clean_text(stripped)
            
            if stripped.startswith('#'):
                # Flush existing body
                if body_buffer:
                    pdf.chapter_body(body_buffer)
                    body_buffer = ""
                
                # Add Header
                clean_header = clean_line.lstrip('#').strip()
                pdf.chapter_title(clean_header)
            else:
                body_buffer += clean_line + "\n"
        
        # Flush remaining body
        if body_buffer:
            pdf.chapter_body(body_buffer)
            
        return bytes(pdf.output())
        
    except Exception as e:
        print(f"PDF Generation Error: {e}")
        return None
