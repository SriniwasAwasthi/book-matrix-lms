import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos

class PDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("helvetica", "I", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, "Book Matrix - Technical Documentation", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def create_pdf():
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Title Page/Header
    pdf.set_font("helvetica", "B", 18)
    pdf.set_text_color(157, 80, 187) # Purple brand color
    pdf.cell(pdf.epw, 15, "Book Matrix", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("helvetica", "", 12)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(pdf.epw, 8, "Complete System Documentation & Architectural Specification", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)
    
    # Horizontal line
    pdf.set_draw_color(157, 80, 187)
    pdf.set_line_width(0.8)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    with open('system_documentation.md', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                pdf.ln(4)
                continue
            
            # Clean formatting tags
            line = line.replace('**', '')
            
            if line.startswith("# "):
                pdf.ln(6)
                pdf.set_font("helvetica", "B", 14)
                pdf.set_text_color(157, 80, 187) # Purple
                txt = line[2:]
                pdf.multi_cell(pdf.epw, 8, txt.encode('latin-1', 'replace').decode('latin-1'), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(2)
            elif line.startswith("## "):
                pdf.ln(4)
                pdf.set_font("helvetica", "B", 12)
                pdf.set_text_color(0, 150, 220) # Blue
                txt = line[3:]
                pdf.multi_cell(pdf.epw, 8, txt.encode('latin-1', 'replace').decode('latin-1'), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(1)
            elif line.startswith("### "):
                pdf.ln(3)
                pdf.set_font("helvetica", "B", 10)
                pdf.set_text_color(50, 50, 50)
                txt = line[4:]
                pdf.multi_cell(pdf.epw, 7, txt.encode('latin-1', 'replace').decode('latin-1'), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(1)
            elif line.startswith("- ") or line.startswith("* "):
                pdf.set_font("helvetica", "", 10)
                pdf.set_text_color(60, 60, 60)
                txt = "-  " + line[2:]
                pdf.multi_cell(pdf.epw, 6, txt.encode('latin-1', 'replace').decode('latin-1'), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            elif line.startswith("---"):
                pdf.ln(2)
                pdf.set_draw_color(220, 220, 220)
                pdf.set_line_width(0.2)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(4)
            else:
                pdf.set_font("helvetica", "", 10)
                pdf.set_text_color(60, 60, 60)
                pdf.multi_cell(pdf.epw, 6, line.encode('latin-1', 'replace').decode('latin-1'), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.output('Library_System_Documentation.pdf')
    print("Documentation PDF generated successfully.")

if __name__ == '__main__':
    create_pdf()
