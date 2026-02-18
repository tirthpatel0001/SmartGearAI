import sys
import os
import streamlit as st
from datetime import datetime

def workload_ui():
    # -------------------------------------------------
    # Fix import path
    # -------------------------------------------------
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

    # -------------------------------------------------
    # Project imports
    # -------------------------------------------------
    from src.workload_analyzer.db import create_table, get_connection
    from src.workload_analyzer.analyze import analyze_workload

    # -------------------------------------------------
    # Page Configuration
    # -------------------------------------------------
    st.set_page_config(
        page_title="Workload Analyzer - ELECON",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # -------------------------------------------------
    # Custom CSS
    # -------------------------------------------------
    st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .main-header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        
        .section-header {
            background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin: 25px 0 15px 0;
        }
        
        .input-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            margin: 15px 0;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .progress-bar {
            background: linear-gradient(135deg, #06A77D 0%, #048859 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin: 10px 0;
        }
        
        .status-running {
            background: linear-gradient(135deg, #06A77D 0%, #048859 100%);
            color: white;
            padding: 10px 15px;
            border-radius: 6px;
            display: inline-block;
            font-weight: bold;
        }
        
        .status-stopped {
            background: linear-gradient(135deg, #F18F01 0%, #C74707 100%);
            color: white;
            padding: 10px 15px;
            border-radius: 6px;
            display: inline-block;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    # -------------------------------------------------
    # Initialize DB
    # -------------------------------------------------
    create_table()

    # -------------------------------------------------
    # Main Header
    # -------------------------------------------------
    st.markdown("""
        <div class="main-header">
            <h1>⚙️ Production Workload Analyzer</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.1em;">
                Real-time gear production tracking and analysis
            </p>
        </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------
    # Tabs
    # -------------------------------------------------
    tab1, tab2 = st.tabs(["➕ Add/Update Record", "📊 Analysis Dashboard"])

    # =================================================
    # TAB 1 : ADD / UPDATE RECORD
    # =================================================
    with tab1:
        st.markdown(
            '<div class="section-header"><h3 style="margin: 0;">📝 Production Record Entry</h3></div>',
            unsafe_allow_html=True
        )

        st.markdown('<div class="input-card">', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 🔑 Gear Identification")
            gear_id = st.text_input("Gear ID", key="wl_gear_id")
            machine_id = st.text_input("Machine ID", key="wl_machine_id")

        with col2:
            st.markdown("#### 📋 Operation Details")
            operation = st.text_input("Operation Stage", key="wl_operation")
            operator_name = st.text_input("Operator Name", key="wl_operator")

        with col3:
            st.markdown("#### 📊 Progress Tracking")
            total_steps = st.number_input("Total Steps", min_value=1, value=10, step=1, key="wl_total")
            completed_steps = st.number_input("Completed Steps", min_value=0, step=1, key="wl_completed")

        st.markdown("</div>", unsafe_allow_html=True)

        # Status section
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            machine_status = st.selectbox(
                "Machine Status",
                ["RUNNING", "STOPPED"],
                key="wl_status"
            )

        with col2:
            progress_pct = (completed_steps / total_steps * 100) if total_steps > 0 else 0
            st.metric("Progress", f"{progress_pct:.0f}%")

        with col3:
            st.metric("Remaining", max(0, total_steps - completed_steps))

        st.markdown("</div>", unsafe_allow_html=True)

        # Save Button
        if st.button("💾 Save / Update Record", use_container_width=True, key="wl_save"):
            if not gear_id or not operation:
                st.error("❌ Gear ID and Operation Stage are required")
            else:
                conn = get_connection()
                cur = conn.cursor()
                now = datetime.now().isoformat()

                cur.execute("""
                    SELECT id FROM production_logs
                    WHERE gear_id = ?
                    ORDER BY id DESC LIMIT 1
                """, (gear_id,))
                existing = cur.fetchone()

                if existing:
                    cur.execute("""
                        UPDATE production_logs
                        SET completed_steps=?, last_update=?, machine_status=?
                        WHERE id=?
                    """, (completed_steps, now, machine_status, existing[0]))
                else:
                    cur.execute("""
                        INSERT INTO production_logs
                        (gear_id, operation, total_steps, completed_steps,
                         start_time, last_update, machine_id, operator_name, machine_status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        gear_id, operation, total_steps, completed_steps,
                        now, now, machine_id, operator_name, machine_status
                    ))

                conn.commit()
                conn.close()
                st.success("✅ Record saved / updated successfully")

    # =================================================
    # TAB 2 : ANALYSIS DASHBOARD
    # =================================================
    with tab2:
        st.markdown(
            '<div class="section-header"><h3 style="margin: 0;">🔍 Workload Analysis</h3></div>',
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            search_gear_id = st.text_input(
                "Search Gear ID",
                key="wl_search",
                placeholder="Enter Gear ID"
            )

        with col2:
            analyze_btn = st.button("🔎 Analyze", use_container_width=True, key="wl_analyze")

        if analyze_btn:
            if not search_gear_id:
                st.error("❌ Please enter a Gear ID")
            else:
                with st.spinner("⏳ Analyzing workload..."):
                    result = analyze_workload(search_gear_id)

                if "error" in result:
                    st.error(result["error"])
                else:
                    st.markdown('<div class="progress-bar">', unsafe_allow_html=True)
                    st.progress(result["progress_percent"] / 100)
                    st.markdown(
                        f"<h3 style='text-align:center;'>{result['progress_percent']:.1f}% Complete</h3>",
                        unsafe_allow_html=True
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

                    col1, col2, col3, col4 = st.columns(4)

                    col1.metric("⏱️ Elapsed (min)", f"{result['elapsed_minutes']:.1f}")
                    col2.metric("⏳ Remaining (min)", f"{result['remaining_minutes']:.1f}")
                    col3.metric("🔄 Shifts", result["shifts_required"])

                    status_html = (
                        "<div class='status-running'>RUNNING</div>"
                        if result["machine_status"] == "RUNNING"
                        else "<div class='status-stopped'>STOPPED</div>"
                    )
                    col4.markdown(status_html, unsafe_allow_html=True)
