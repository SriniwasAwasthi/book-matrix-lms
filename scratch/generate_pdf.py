from fpdf import FPDF
import os

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=11)

try:
    with open('queries.md', 'r', encoding='utf-8') as f:
        for line in f:
            pdf.multi_cell(0, 8, txt=line.encode('latin-1', 'replace').decode('latin-1'))
    pdf.output('Library_Assistant_Queries.pdf')
    print("PDF generated successfully.")
except Exception as e:
    print(f"Error: {e}")
