import pandas as pd
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def calculate_cost_breakdown(base_price, input_data):
    """Calculate detailed cost breakdown"""
    breakdown = {
        'base_price': round(base_price, 2),
        'material_cost': 0,
        'manufacturing_cost': 0,
        'heat_treatment_cost': 0,
        'delivery_cost': 0,
        'bulk_discount': 0,
    }
    
    # Material affects base cost
    material_multiplier = {
        'Steel': 0,
        'Alloy Steel': base_price * 0.30,
        'Cast Iron': -base_price * 0.20,
        'Stainless Steel': base_price * 0.50
    }
    breakdown['material_cost'] = material_multiplier.get(input_data.get('material', 'Steel'), 0)
    
    # Manufacturing cost based on complexity
    module = input_data.get('module', 1)
    teeth = input_data.get('teeth', 50)
    breakdown['manufacturing_cost'] = (module * 30 + teeth * 1.5)
    
    # Heat treatment
    if input_data.get('heat_treatment', False):
        breakdown['heat_treatment_cost'] = base_price * 0.10
    
    # Delivery
    if input_data.get('delivery_type') == 'Urgent':
        breakdown['delivery_cost'] = base_price * 0.15
    else:
        breakdown['delivery_cost'] = base_price * 0.05
    
    # Bulk discount
    quantity = input_data.get('quantity', 1)
    discount_rates = {1: 0, 5: 0.05, 10: 0.10, 25: 0.15, 50: 0.20, 100: 0.25}
    discount_rate = discount_rates.get(quantity, 0)
    subtotal = (breakdown['base_price'] + breakdown['material_cost'] + 
                breakdown['manufacturing_cost'] + breakdown['heat_treatment_cost'] +
                breakdown['delivery_cost'])
    breakdown['bulk_discount'] = -(subtotal * discount_rate)
    
    breakdown['total'] = sum([v for k, v in breakdown.items() if k != 'total'])
    breakdown['total'] = max(breakdown['total'], 100)  # Minimum price
    breakdown['total'] = round(breakdown['total'], 2)
    
    return breakdown

def generate_pdf_report(input_data, price_estimate, cost_breakdown, output_path=None):
    """Generate PDF report for price estimation"""
    
    if output_path is None:
        output_path = BytesIO()
    
    # Create PDF
    doc = SimpleDocTemplate(output_path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    elements.append(Paragraph("Smart Gear AI", title_style))
    elements.append(Paragraph("Price Estimation Report", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    # Date
    date_str = datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph(f"<b>Date:</b> {date_str}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Input Details Section
    elements.append(Paragraph("INPUT SPECIFICATIONS", styles['Heading3']))
    
    input_table_data = [
        ['Parameter', 'Value'],
        ['Gear Type', str(input_data.get('gear_type', 'N/A'))],
        ['Gearbox Type', str(input_data.get('gearbox_type', 'N/A'))],
        ['Material', str(input_data.get('material', 'N/A'))],
        ['Module', f"{input_data.get('module', 0):.2f}"],
        ['Teeth', str(input_data.get('teeth', 0))],
        ['Load Capacity (kg)', f"{input_data.get('load', 0):.2f}"],
        ['Speed (RPM)', f"{input_data.get('speed', 0):.2f}"],
        ['Gear Ratio', f"{input_data.get('gear_ratio', 0):.2f}"],
        ['Heat Treatment', 'Yes' if input_data.get('heat_treatment') else 'No'],
        ['Surface Finish', str(input_data.get('surface_finish', 'N/A'))],
        ['Quantity', str(input_data.get('quantity', 1))],
        ['Delivery Type', str(input_data.get('delivery_type', 'Normal'))],
    ]
    
    input_table = Table(input_table_data, colWidths=[3*inch, 2*inch])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(input_table)
    elements.append(Spacer(1, 20))
    
    # Cost Breakdown Section
    elements.append(Paragraph("COST BREAKDOWN", styles['Heading3']))
    
    breakdown_table_data = [
        ['Cost Component', 'Amount (INR)'],
        ['Base Price', f"₹{cost_breakdown.get('base_price', 0):.2f}"],
        ['Material Cost', f"₹{cost_breakdown.get('material_cost', 0):.2f}"],
        ['Manufacturing Cost', f"₹{cost_breakdown.get('manufacturing_cost', 0):.2f}"],
        ['Heat Treatment Cost', f"₹{cost_breakdown.get('heat_treatment_cost', 0):.2f}"],
        ['Delivery Cost', f"₹{cost_breakdown.get('delivery_cost', 0):.2f}"],
        ['Bulk Discount', f"₹{cost_breakdown.get('bulk_discount', 0):.2f}"],
    ]
    
    breakdown_table = Table(breakdown_table_data, colWidths=[3.5*inch, 1.5*inch])
    breakdown_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(breakdown_table)
    elements.append(Spacer(1, 20))
    
    # Final Price Section
    final_price_style = ParagraphStyle(
        'FinalPrice',
        parent=styles['Heading2'],
        fontSize=20,
        textColor=colors.HexColor('#2ca02c'),
        spaceAfter=10,
        alignment=TA_RIGHT,
        fontName='Helvetica-Bold'
    )
    elements.append(Paragraph(f"<b>ESTIMATED PRICE: ₹{price_estimate:.2f}</b>", final_price_style))
    elements.append(Spacer(1, 12))
    
    # Footer
    elements.append(Paragraph(
        "<i>This is an automated price estimation. For official quotations, please contact sales.</i>",
        styles['Italic']
    ))
    
    # Build PDF
    if isinstance(output_path, BytesIO):
        doc.build(elements)
        output_path.seek(0)
        return output_path
    else:
        doc.build(elements)
        return output_path

def format_price(price):
    """Format price as currency string"""
    return f"₹{price:,.2f}"

def get_delivery_surcharge_percentage(delivery_type):
    """Get delivery surcharge percentage"""
    surcharges = {
        'Normal': 0.05,
        'Urgent': 0.15
    }
    return surcharges.get(delivery_type, 0.05)

def get_bulk_discount_rate(quantity):
    """Get bulk discount rate"""
    discount_rates = {
        1: 0.0,
        5: 0.05,
        10: 0.10,
        25: 0.15,
        50: 0.20,
        100: 0.25
    }
    return discount_rates.get(quantity, 0.25)
