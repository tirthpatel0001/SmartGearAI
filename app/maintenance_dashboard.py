import os
import tempfile
import pandas as pd
import streamlit as st
from src.gear_box_defect.predict import predict_fault_and_severity
from src.gear_box_defect.result import GearboxAnalysis
from src.pdf_generator.gearbox_report_pdf import generate_gearbox_pdf


def display_gearbox_diagnosis():
    st.markdown("""
        <div class="hero-header" style="padding: 40px; margin-bottom: 30px;">
            <h1>⚙️ Gearbox Diagnosis & Predictive Maintenance</h1>
            <p>AI-Powered Signal Analysis with Cost, Parts, and Risk Insights</p>
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Gearbox Vibration CSV File",
        type=["csv"]
    )

    if not uploaded_file:
        st.info("⬆️ Upload a CSV file to start gearbox diagnosis.")
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(uploaded_file.getbuffer())
        temp_csv_path = tmp.name

    try:
        with st.spinner("🔍 Analyzing gearbox signals..."):
            result = predict_fault_and_severity(temp_csv_path)

        # maintain backward compatibility in case the function returned a tuple
        if isinstance(result, tuple):
            # try to unpack into the dataclass in the same order it is defined
            try:
                result = GearboxAnalysis(*result)
            except Exception:
                # if conversion fails just raise so the error is visible
                raise

        # safe values
        fault = result.fault
        severity = result.severity
        rms = result.rms
        energy = result.energy
        recommendation = result.recommendation
        risk_label = result.risk_label
        risk_prob = result.risk_probability
        rul = result.remaining_life
        schedule = result.schedule
        health = result.health_score
        trend_curve = result.trend
        cost = result.failure_cost
        parts = result.spare_parts
        root_cause = result.root_cause
        chatbot_intro = result.chatbot_intro
        digital_summary = result.digital_twin_summary

        # ================= SAFETY NORMALIZATION =================
        fault_clean = (fault or "").strip().lower()
        severity_clean = (severity or "").strip().lower()

        # ================= THRESHOLDS & SPEED =================
        RMS_THRESHOLD = 0.02
        ENERGY_THRESHOLD = 5.0
        SAMPLING_FREQ = 10000  # Hz (assumed)

        df = pd.read_csv(temp_csv_path)
        duration_sec = len(df) / SAMPLING_FREQ if len(df) > 0 else 0
        speed_rpm = (1 / duration_sec) * 60 if duration_sec > 0 else 0

        # ================= STATUS LOGIC =================
        if fault_clean == "healthy":
            status_color = "#06A77D"
            status_text = "HEALTHY"
        elif severity_clean == "medium":
            status_color = "#FFB84D"
            status_text = "WARNING"
        else:
            status_color = "#FF6B6B"
            status_text = "CRITICAL"

        # ================= VISUAL DASHBOARD =================
        st.markdown("## 🔍 Gearbox Diagnosis Results")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <h4>⚙️ Fault Type</h4>
                    <p class="value">{fault}</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <h4>📈 RMS</h4>
                    <p class="value">{rms:.5f}</p>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <h4>⚡ Energy</h4>
                    <p class="value">{energy:.2f}</p>
                </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
                <div class="metric-card" style="background: {status_color};">
                    <h4>🚦 Status</h4>
                    <p class="value">{status_text}</p>
                </div>
            """, unsafe_allow_html=True)

        # predictive maintenance panel
        st.markdown("### 🔮 Predictive Maintenance")
        pm_col1, pm_col2, pm_col3 = st.columns(3)
        with pm_col1:
            st.markdown(f"**Failure Risk:** {risk_label} ({risk_prob*100:.1f}%)")
            st.markdown(f"**Estimated Cost:** ${cost:.2f}")
        with pm_col2:
            st.markdown(f"**Remaining Useful Life:** {rul:.0f} hours")
            st.markdown(f"**Suggested Action:** {schedule}")
            st.markdown(f"**Spare Parts:** {', '.join(parts) if parts else 'None'}")
        with pm_col3:
            st.markdown(f"**Health Score:** {health:.1f}%")
            st.markdown(f"**Root Cause:** {root_cause}")
        st.line_chart(trend_curve, height=150)

        # chatbot section
        st.markdown("### 💬 AI Assistant")
        st.write(chatbot_intro)
        user_q = st.text_input("Ask the assistant a question about risk or maintenance:")
        if user_q:
            st.write("🤖", chatbot_intro)  # simple echo for now

        # digital twin summary
        st.markdown("### 🧠 Digital Twin Simulation")
        st.write(digital_summary)

        # ================= THRESHOLD INSIGHT =================
        st.markdown("### 📊 Signal Threshold Analysis")
        threshold_df = pd.DataFrame({
            "Metric": ["RMS", "Energy", "Speed (RPM)"],
            "Measured Value": [f"{rms:.5f}", f"{energy:.2f}", f"{speed_rpm:.2f}"],
            "Threshold": [RMS_THRESHOLD, ENERGY_THRESHOLD, "—"],
            "Condition": [
                "❌ High" if rms > RMS_THRESHOLD else "✅ Normal",
                "❌ High" if energy > ENERGY_THRESHOLD else "✅ Normal",
                "ℹ️ Info"
            ]
        })
        st.dataframe(threshold_df, use_container_width=True, hide_index=True)

        # ================= PDF DOWNLOAD =================
        st.markdown("---")
        pdf_path = generate_gearbox_pdf(
            csv_file_name=uploaded_file.name,
            fault=fault,
            severity=severity if fault_clean != "healthy" else "N/A",
            rms=rms,
            energy=energy,
            speed=speed_rpm,
            rms_threshold=RMS_THRESHOLD,
            energy_threshold=ENERGY_THRESHOLD,
            recommendation=recommendation if fault_clean != "healthy" else "Not Required",
            # predictive maintenance fields
            risk_label=risk_label,
            risk_probability=risk_prob,
            remaining_life=rul,
            maintenance_schedule=schedule,
            health_score=health,
            failure_cost=cost,
            spare_parts=parts,
            root_cause=root_cause,
            chatbot_intro=chatbot_intro,
            digital_twin_summary=digital_summary,
        )
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download Maintenance Report",
                data=f,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf",
                use_container_width=True
            )

    except Exception as e:
        st.error(f"❌ Error analyzing gearbox data: {e}")

    finally:
        os.remove(temp_csv_path)
