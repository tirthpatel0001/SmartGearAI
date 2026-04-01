import streamlit as st
import pandas as pd
import joblib
import os
import sys

project_root = r"C:\Projects\SGMAS"
sys.path.append(project_root)

from src.pdf_generator.create_pdf import generate_estimate_pdf
from src.utils.config import load_config, save_config

st.set_page_config(
    page_title="ELECON Gear Price Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# Custom CSS for ADVANCED modern styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;300;400;500;600;700;800&display=swap');
    
    :root {
        --primary-dark: #1E3A5F;
        --primary-steel: #2C5282;
        --accent-orange: #D97706;
        --success-green: #059669;
        --danger-red: #DC2626;
        --background: #F5F7FA;
        --card-bg: #FFFFFF;
        --text-primary: #111827;
        --text-secondary: #6B7280;
        --border-light: #E5E7EB;
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
        --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 12px 24px rgba(0, 0, 0, 0.12);
    }
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background-color: var(--background);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%);
        color: var(--text-primary);
        padding: 28px;
        border-radius: 14px;
        margin: 14px 0;
        box-shadow: var(--shadow-md);
        transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
        border-top: 4px solid var(--accent-orange);
        border: 1px solid rgba(229, 231, 235, 0.8);
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: var(--shadow-lg);
        background: linear-gradient(135deg, #FFFFFF 0%, #F3F4F6 100%);
    }
    
    .success-card {
        background: linear-gradient(135deg, var(--success-green) 0%, #047857 100%);
        color: white;
        padding: 32px;
        border-radius: 14px;
        margin: 16px 0;
        border-left: 5px solid #10B981;
        box-shadow: 0 12px 24px rgba(5, 150, 105, 0.2);
        transition: all 0.3s ease;
        animation: scaleIn 0.5s ease-out;
    }
    
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    
    .success-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 32px rgba(5, 150, 105, 0.3);
    }
    
    .header-container {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 50%, #2C5282 100%);
        color: white;
        padding: 50px;
        border-radius: 16px;
        margin-bottom: 30px;
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
    
    .header-container::before {
        content: '💹';
        position: absolute;
        top: -30px;
        right: -30px;
        font-size: 120px;
        opacity: 0.08;
    }
    
    .header-container h1 {
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
    
    .header-container p {
        margin: 14px 0 0 0;
        opacity: 0.95;
        font-size: 1.1em;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    .input-section {
        background: linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%);
        padding: 32px;
        border-radius: 14px;
        margin: 20px 0;
        box-shadow: var(--shadow-md);
        border-top: 4px solid var(--primary-dark);
        border: 1px solid rgba(229, 231, 235, 0.8);
        transition: all 0.3s ease;
    }
    
    .input-section:hover {
        box-shadow: var(--shadow-lg);
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
    </style>
""", unsafe_allow_html=True)
        box-shadow: var(--shadow-md);
        border-top: 3px solid var(--primary-dark);
    }
    
    .breakdown-table {
        background: var(--card-bg);
        padding: 24px;
        border-radius: 8px;
        box-shadow: var(--shadow-md);
    }
    </style>
""", unsafe_allow_html=True)

# Load Config
config = load_config()

# Check admin status
is_admin = st.session_state.get('admin_authenticated', False)

# Header
st.markdown("""
    <div class="header-container">
        <h1>⚙️ Gear Price Predictor</h1>
        <p>Intelligent pricing and estimate generation for precision gears</p>
    </div>
""", unsafe_allow_html=True)

# ================== ADMIN SECTION ==================
if is_admin:
    with st.sidebar:
        if st.expander("🔧 Admin Configuration", expanded=False):
            st.markdown("### 💰 Cost Configuration")
            
            st.markdown("#### Material Rates (per kg)")
            col1, col2, col3 = st.columns(3)
            with col1:
                steel_rate = st.number_input("Steel Rate", value=config["material_rate_per_kg"].get("Steel", 100), key="steel_rate")
            with col2:
                alloy_rate = st.number_input("Alloy Steel Rate", value=config["material_rate_per_kg"].get("Alloy Steel", 120), key="alloy_rate")
            with col3:
                carbon_rate = st.number_input("Carbon Steel Rate", value=config["material_rate_per_kg"].get("Carbon Steel", 90), key="carbon_rate")
            
            st.markdown("#### Labor & Machine Costs")
            col1, col2 = st.columns(2)
            with col1:
                labor_rate = st.number_input("Labor Rate (per hour)", value=config["labor_rate_per_hour"], key="labor_rate")
            with col2:
                machine_rate = st.number_input("Machine Cost (per hour)", value=config["machine_hourly_cost"], key="machine_rate")
            
            st.markdown("#### Treatment Charges")
            col1, col2, col3 = st.columns(3)
            with col1:
                hardening = st.number_input("Hardening Charge", value=config["surface_treatment_charge"].get("Hardening", 50), key="hardening")
            with col2:
                coating = st.number_input("Coating Charge", value=config["surface_treatment_charge"].get("Coating", 30), key="coating")
            with col3:
                urgency = st.number_input("Urgency % (markup)", value=config["urgency_percentage"], key="urgency")
            
            # Save config button
            if st.button("💾 Save Configuration", use_container_width=True):
                config["material_rate_per_kg"]["Steel"] = steel_rate
                config["material_rate_per_kg"]["Alloy Steel"] = alloy_rate
                config["material_rate_per_kg"]["Carbon Steel"] = carbon_rate
                config["labor_rate_per_hour"] = labor_rate
                config["machine_hourly_cost"] = machine_rate
                config["surface_treatment_charge"]["Hardening"] = hardening
                config["surface_treatment_charge"]["Coating"] = coating
                config["urgency_percentage"] = urgency
                save_config(config)
                st.success("✅ Configuration saved successfully!")
                st.rerun()
            
            st.divider()
            st.markdown("#### Current Configuration")
            st.json(config)

st.markdown("### 📋 Enter Gear Specifications")

col1, col2, col3 = st.columns(3)

with col1:
    gear_type = st.selectbox("🔧 Gear Type", ["Spur", "Helical", "Bevel"])
    diameter = st.number_input("📏 Diameter (mm)", 50, 300, 100)
    thickness = st.number_input("📐 Thickness (mm)", int(diameter*0.05), int(diameter*0.2), int(diameter*0.1))

with col2:
    material = st.selectbox("🛠️ Material", ["Steel", "Alloy Steel", "Carbon Steel"])
    teeth = st.number_input("🦷 Teeth Count", int(diameter*0.3), int(diameter*0.6), int(diameter*0.5))
    quantity = st.number_input("📦 Quantity", 1, 500, 50)

with col3:
    special_req = st.selectbox("✨ Special Requirement", ["None", "Hardening", "Coating"])

# Load model
model_path = os.path.join(project_root, 'data', 'models', 'gear_price_model.pkl')
if not os.path.exists(model_path):
    st.error(f"❌ Trained model not found at {model_path}. Run train_model.py first.")
    st.stop()
model = joblib.load(model_path)

# Calculate button with custom styling
col_button1, col_button2, col_button3 = st.columns([1, 2, 1])
with col_button2:
    predict_btn = st.button("💰 Calculate Price", use_container_width=True, key="predict_btn")

if predict_btn:
    outer_radius = diameter / 2
    inner_radius = outer_radius * 0.3
    volume_cm3 = 3.1416 * (outer_radius**2 - inner_radius**2) * thickness * 0.1
    material_density = {'Steel': 7.85, 'Alloy Steel': 7.8, 'Carbon Steel': 7.7}
    weight_kg = volume_cm3 * material_density[material] / 1000

    input_df = pd.DataFrame([{
        'Gear_Type': gear_type,
        'Material': material,
        'Diameter_mm': diameter,
        'Teeth_Count': teeth,
        'Thickness_mm': thickness,
        'Quantity': quantity,
        'Special_Requirement': special_req,
        'Weight_kg': round(weight_kg,2)
    }])

    base_price = model.predict(input_df)[0]

    # Cost calculation using admin config
    material_cost = weight_kg * config["material_rate_per_kg"].get(material, 100)
    treatment_cost = config["surface_treatment_charge"].get(special_req, 0) * quantity
    labor_hours_per_gear = 0.5 + 0.01*teeth
    machine_hours_per_gear = 0.5 + 0.005*diameter
    labor_cost = labor_hours_per_gear * config["labor_rate_per_hour"] * quantity
    machine_cost = machine_hours_per_gear * config["machine_hourly_cost"] * quantity
    urgency_multiplier = 1 + config["urgency_percentage"]/100

    predicted_price = (base_price + material_cost + treatment_cost + labor_cost + machine_cost) * urgency_multiplier

    # Display price in an attractive card
    st.markdown(f"""
        <div class="success-card">
            <h3 style="margin: 0; font-size: 1.5em;">Estimated Total Price</h3>
            <h1 style="margin: 10px 0 0 0; font-size: 3em;">₹ {predicted_price:,.2f}</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Quantity: {quantity} units</p>
        </div>
    """, unsafe_allow_html=True)

    cost_breakdown = {
        "Base ML Price": base_price,
        "Material Cost": material_cost,
        "Labor Cost": labor_cost,
        "Machine Cost": machine_cost,
        "Surface Treatment Cost": treatment_cost,
        "Urgency Adjustment": predicted_price - (base_price + material_cost + treatment_cost + labor_cost + machine_cost)
    }

    customer_input_dict = {
        "Gear Type": gear_type,
        "Material": material,
        "Diameter (mm)": diameter,
        "Teeth Count": teeth,
        "Thickness (mm)": thickness,
        "Quantity": quantity,
        "Special Requirement": special_req,
        "Weight (kg)": round(weight_kg,2)
    }

    # Display cost breakdown
    st.markdown("### 📊 Cost Breakdown")
    breakdown_df = pd.DataFrame(list(cost_breakdown.items()), columns=['Component', 'Amount (₹)'])
    breakdown_df['Amount (₹)'] = breakdown_df['Amount (₹)'].apply(lambda x: f"₹ {x:,.2f}")
    
    st.markdown("""
        <div class="breakdown-table">
    """, unsafe_allow_html=True)
    st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # PDF Download
    pdf_path = generate_estimate_pdf(customer_input_dict, predicted_price, cost_breakdown)
    with open(pdf_path, "rb") as f:
        col_pdf1, col_pdf2, col_pdf3 = st.columns([1, 2, 1])
        with col_pdf2:
            st.download_button(
                label="📥 Download Estimate PDF",
                data=f,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf",
                use_container_width=True
            )
    