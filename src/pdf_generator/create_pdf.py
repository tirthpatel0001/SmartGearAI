from fpdf import FPDF
import os
from datetime import datetime

def generate_estimate_pdf(customer_input: dict, predicted_price: float, cost_breakdown: dict):
    project_root = r"C:\Projects\SGMAS"
    save_dir = os.path.join(project_root, 'data', 'estimates')
    os.makedirs(save_dir, exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "ELECON Industries - Gear Price Estimate", ln=True, align='C')

    pdf.set_font("Arial", "", 12)
    estimate_number = f"EST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    pdf.cell(0, 10, f"Estimate Number: {estimate_number}", ln=True)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%d-%m-%Y')}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Gear Specifications:", ln=True)
    pdf.set_font("Arial", "", 12)
    for key, value in customer_input.items():
        pdf.cell(60, 8, f"{key}:", border=0)
        pdf.cell(0, 8, f"{value}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Cost Breakdown:", ln=True)
    pdf.set_font("Arial", "", 12)
    for key, value in cost_breakdown.items():
        pdf.cell(70, 8, f"{key}:", border=0)
        pdf.cell(0, 8, f"Rs. {value:.2f}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Predicted Total Price: Rs. {predicted_price:.2f}", ln=True)

    pdf_file_name = f"Gear_Estimate_{estimate_number}.pdf"
    pdf_path = os.path.join(save_dir, pdf_file_name)
    pdf.output(pdf_path)
    
    return pdf_path
