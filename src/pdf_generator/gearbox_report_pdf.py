import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors


def generate_gearbox_pdf(
    csv_file_name,
    fault,
    severity,
    rms,
    energy,
    speed,
    rms_threshold,
    energy_threshold,
    recommendation,
    # predictive maintenance values
    risk_label=None,
    risk_probability=None,
    remaining_life=None,
    maintenance_schedule=None,
    health_score=None,
    # additional maintenance report fields
    failure_cost=None,
    spare_parts=None,
    root_cause=None,
    chatbot_intro=None,
    digital_twin_summary=None,
):
    """
    Generates a detailed Gearbox Diagnosis PDF Report
    """

    # ---------------- File setup ----------------
    reports_dir = "data/reports"
    os.makedirs(reports_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(
        reports_dir, f"Gearbox_Diagnosis_Report_{timestamp}.pdf"
    )

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    elements = []

    # ---------------- Custom styles ----------------
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#2c3e50")
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#FF6B6B")
    )

    normal_style = styles["Normal"]

    # ---------------- Title ----------------
    elements.append(Paragraph(
        "⚙️ Gearbox Diagnosis Report", title_style
    ))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph(
        "<b>Smart Gear Management & Analysis System (SGMAS)</b>",
        styles["Italic"]
    ))
    elements.append(Spacer(1, 20))

    # ---------------- Metadata ----------------
    metadata_table = Table([
        ["Report Generated On", datetime.now().strftime("%d %B %Y, %H:%M:%S")],
        ["Uploaded CSV File", csv_file_name],
        ["System", "AI-Based Gearbox Fault Diagnosis"]
    ], colWidths=[180, 300])

    metadata_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONT", (0, 0), (-1, -1), "Helvetica"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))

    elements.append(metadata_table)
    elements.append(Spacer(1, 25))

    # ---------------- Diagnosis Summary ----------------
    elements.append(Paragraph("🔍 Diagnosis Summary", section_style))
    elements.append(Spacer(1, 10))

    summary_data = [
        ["Fault Type", fault],
        ["RMS Vibration", f"{rms:.5f}"],
        ["RMS Threshold", f"{rms_threshold}"],
        ["Energy", f"{energy:.2f}"],
        ["Energy Threshold", f"{energy_threshold}"],
        ["Estimated Speed (RPM)", f"{speed:.2f}"]
    ]
    # include predictive maintenance info if available
    if risk_label is not None:
        summary_data.append(["Failure Risk", f"{risk_label} ({risk_probability*100:.1f}%)"])
    if remaining_life is not None:
        summary_data.append(["Remaining Useful Life", f"{remaining_life:.0f} hours"])
    if health_score is not None:
        summary_data.append(["Health Score", f"{health_score:.1f}%"])
    if failure_cost is not None:
        summary_data.append(["Estimated Failure Cost", f"${failure_cost:.2f}"])
    if spare_parts is not None:
        summary_data.append(["Suggested Spare Parts", ", ".join(spare_parts) if spare_parts else "None"])
    if root_cause is not None:
        summary_data.append(["Root Cause", root_cause])



    summary_table = Table(summary_data, colWidths=[200, 280])
    summary_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONT", (0, 0), (-1, -1), "Helvetica"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # ---------------- Severity & Recommendation ----------------
    if fault.lower() != "healthy":
        elements.append(Paragraph("⚠️ Severity & Recommendation", section_style))
        elements.append(Spacer(1, 10))

        sr_table = Table([
            ["Severity Level", severity],
            ["Maintenance Recommendation", recommendation]
        ], colWidths=[200, 280])
        
        # if we have risk information also display it here
        if risk_label is not None:
            sr_table_data = sr_table._cellvalues  # hack to append
            sr_table_data.append(["Failure Risk", f"{risk_label} ({risk_probability*100:.1f}%)"])
            sr_table = Table(sr_table_data, colWidths=[200, 280])
        if failure_cost is not None:
            sr_table_data = sr_table._cellvalues
            sr_table_data.append(["Estimated Failure Cost", f"${failure_cost:.2f}"])
            sr_table = Table(sr_table_data, colWidths=[200, 280])
        if root_cause is not None:
            sr_table_data = sr_table._cellvalues
            sr_table_data.append(["Root Cause", root_cause])
            sr_table = Table(sr_table_data, colWidths=[200, 280])


        sr_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONT", (0, 0), (-1, -1), "Helvetica"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke)
        ]))

        elements.append(sr_table)
        elements.append(Spacer(1, 20))

    # ---------------- Interpretation ----------------
    elements.append(Paragraph("📖 Interpretation & Insights", section_style))
    elements.append(Spacer(1, 10))

    interpretation_text = f"""
    <b>RMS Analysis:</b><br/>
    RMS vibration value of <b>{rms:.5f}</b> compared to threshold <b>{rms_threshold}</b>.
    Values above threshold indicate abnormal vibration and possible mechanical issues.<br/><br/>

    <b>Energy Analysis:</b><br/>
    Signal energy measured at <b>{energy:.2f}</b> against threshold <b>{energy_threshold}</b>.
    Higher energy indicates increased fault probability.<br/><br/>

    <b>Speed Estimation:</b><br/>
    Estimated gearbox rotational speed is <b>{speed:.2f} RPM</b>.
    Abnormal vibration at this speed may indicate gear mesh defects or imbalance.<br/><br/>
"""
    if chatbot_intro:
        interpretation_text += f"<b>AI Assistant:</b><br/>{chatbot_intro}<br/><br/>"
    if digital_twin_summary:
        interpretation_text += f"<b>Digital Twin:</b><br/>{digital_twin_summary}<br/><br/>"

    elements.append(Paragraph(interpretation_text, normal_style))
    elements.append(Spacer(1, 30))

    # ---------------- Footer ----------------
    elements.append(Paragraph(
        "<i>This report is generated automatically using AI-based signal analysis. "
        "For critical systems, manual inspection is recommended.</i>",
        styles["Italic"]
    ))
    




    # ---------------- Build PDF ----------------
    doc.build(elements)

    return file_path
