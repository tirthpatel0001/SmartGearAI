import streamlit as st
from src.utils.config import load_config, save_config

st.set_page_config(
    page_title="Admin Panel - ELECON",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ADVANCED Admin Panel
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    :root {
        --primary-dark: #1E3A5F;
        --primary-steel: #2C5282;
        --accent-orange: #D97706;
        --success-green: #059669;
        --background: #F5F7FA;
        --card-bg: #FFFFFF;
        --text-primary: #111827;
        --text-secondary: #6B7280;
        --border-light: #E5E7EB;
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
        --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 12px 24px rgba(0, 0, 0, 0.12);
    }
    
    .main {
        background-color: var(--background);
    }
    
    .admin-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 50%, #2C5282 100%);
        color: white;
        padding: 50px;
        border-radius: 16px;
        margin-bottom: 35px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        border-top: 5px solid var(--accent-orange);
        position: relative;
        overflow: hidden;
        animation: fadeInDown 0.6s ease-out;
    }
    
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .admin-header::before {
        content: '🔧';
        position: absolute;
        top: -30px;
        right: -30px;
        font-size: 120px;
        opacity: 0.08;
    }
    
    .admin-header h1 {
        margin: 0;
        font-size: 3em;
        font-weight: 800;
        letter-spacing: -0.5px;
        position: relative;
        z-index: 1;
        background: linear-gradient(135deg, #FFFFFF 0%, #FFE5CC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .admin-header p {
        margin: 14px 0 0 0;
        opacity: 0.95;
        font-size: 1.1em;
        position: relative;
        z-index: 1;
    }
    
    .section-header {
        background: linear-gradient(135deg, var(--accent-orange) 0%, #F59E0B 100%);
        color: white;
        padding: 18px 24px;
        border-radius: 12px;
        margin: 24px 0 18px 0;
        font-weight: 700;
        letter-spacing: 0.3px;
        box-shadow: 0 10px 25px rgba(217, 119, 6, 0.2);
        transition: all 0.3s ease;
    }
    
    .section-header h3 {
        margin: 0;
        font-size: 1.15em;
    }
    
    .config-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%);
        padding: 28px;
        border-radius: 14px;
        box-shadow: var(--shadow-md);
        margin: 16px 0;
        transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
        border-left: 5px solid var(--accent-orange);
        border: 1px solid rgba(229, 231, 235, 0.8);
    }
    
    .config-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-6px);
        background: linear-gradient(135deg, #FFFFFF 0%, #F3F4F6 100%);
    }
    
    .config-card h4 {
        color: var(--primary-dark);
        margin: 0 0 14px 0;
        font-weight: 700;
        font-size: 1.15em;
        letter-spacing: -0.2px;
    }
    
    .config-card p {
        color: var(--text-secondary);
        font-size: 0.9em;
        margin: 0;
    }
    
    .save-button {
        margin: 32px 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-orange) 0%, #F59E0B 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 32px !important;
        font-weight: 700 !important;
        font-size: 0.95em !important;
        transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        box-shadow: 0 10px 25px rgba(217, 119, 6, 0.25) !important;
        letter-spacing: 0.3px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 15px 35px rgba(217, 119, 6, 0.35) !important;
        background: linear-gradient(135deg, #B45309 0%, #D97706 100%) !important;
    }
    
    input, select, textarea {
        border-radius: 10px !important;
        border: 1.5px solid rgba(217, 119, 6, 0.3) !important;
        padding: 12px 14px !important;
        transition: all 0.3s ease !important;
        font-weight: 500 !important;
    }
    
    input:focus, select:focus, textarea:focus {
        border-color: var(--accent-orange) !important;
        box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.1) !important;
        outline: none !important;
    }
    
    label {
        font-weight: 700 !important;
        color: var(--primary-dark) !important;
        font-size: 0.9em !important;
        letter-spacing: 0.2px !important;
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
