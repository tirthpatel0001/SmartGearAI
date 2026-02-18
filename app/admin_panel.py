import streamlit as st
from src.utils.config import load_config, save_config

st.set_page_config(
    page_title="Admin Panel - ELECON",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Admin Panel
st.markdown("""
    <style>
    .admin-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .admin-header h1 {
        margin: 0;
        font-size: 2.5em;
    }
    
    .section-header {
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        margin: 20px 0 15px 0;
    }
    
    .config-card {
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin: 10px 0;
    }
    
    .save-button {
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="admin-header">
        <h1>⚙️ Admin Control Panel</h1>
        <p style="margin: 10px 0 0 0; font-size: 1.1em;">Manage pricing, labor rates, and cost factors</p>
    </div>
""", unsafe_allow_html=True)

config = load_config()

# Create tabs for better organization
tab1, tab2, tab3, tab4 = st.tabs([
    "💰 Material Rates",
    "🏭 Labor & Machine",
    "✨ Treatments",
    "⚡ Urgency"
])

# Tab 1: Material Rates
with tab1:
    st.markdown('<div class="section-header"><h3 style="margin: 0;">Material Rates Per Kilogram</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    materials = list(config["material_rate_per_kg"].keys())
    
    for idx, material in enumerate(materials):
        col = [col1, col2, col3][idx % 3]
        with col:
            st.markdown(f"""
                <div class="config-card">
                    <h4>{material}</h4>
            """, unsafe_allow_html=True)
            config["material_rate_per_kg"][material] = st.number_input(
                f"{material} Rate (₹/kg)",
                value=config["material_rate_per_kg"][material],
                step=10,
                key=f"material_{material}"
            )
            st.markdown("</div>", unsafe_allow_html=True)

# Tab 2: Labor & Machine Costs
with tab2:
    st.markdown('<div class="section-header"><h3 style="margin: 0;">Labor & Machine Cost Configuration</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="config-card">', unsafe_allow_html=True)
        st.markdown("### 👷 Labor Rate")
        config["labor_rate_per_hour"] = st.number_input(
            "Labor Rate (₹/hour)",
            value=config["labor_rate_per_hour"],
            step=50,
            key="labor_rate"
        )
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="config-card">', unsafe_allow_html=True)
        st.markdown("### 🤖 Machine Cost")
        config["machine_hourly_cost"] = st.number_input(
            "Machine Cost (₹/hour)",
            value=config["machine_hourly_cost"],
            step=50,
            key="machine_cost"
        )
        st.markdown("</div>", unsafe_allow_html=True)

# Tab 3: Surface Treatment Charges
with tab3:
    st.markdown('<div class="section-header"><h3 style="margin: 0;">Surface Treatment Charges Per Unit</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    treatments = list(config["surface_treatment_charge"].keys())
    
    for idx, treatment in enumerate(treatments):
        col = [col1, col2, col3][idx % 3]
        with col:
            st.markdown(f"""
                <div class="config-card">
                    <h4>{treatment}</h4>
            """, unsafe_allow_html=True)
            config["surface_treatment_charge"][treatment] = st.number_input(
                f"{treatment} Charge (₹)",
                value=config["surface_treatment_charge"][treatment],
                step=50,
                key=f"treatment_{treatment}"
            )
            st.markdown("</div>", unsafe_allow_html=True)

# Tab 4: Urgency Adjustment
with tab4:
    st.markdown('<div class="section-header"><h3 style="margin: 0;">Urgency Multiplier</h3></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="config-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info("📌 This percentage is added as a multiplier to the final price for urgent orders")
        config["urgency_percentage"] = st.slider(
            "Urgency Percentage (%)",
            0,
            100,
            int(config["urgency_percentage"]),
            step=5,
            key="urgency"
        )
    with col2:
        st.metric("Current Multiplier", f"{1 + config['urgency_percentage']/100:.2f}x")
    st.markdown("</div>", unsafe_allow_html=True)

# Save button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("💾 Save All Changes", use_container_width=True, key="save_btn"):
        save_config(config)
        st.success("✅ Configuration saved successfully!")
        st.balloons()
