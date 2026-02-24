import streamlit as st
import pandas as pd
import joblib
import os
import sys
import tempfile
from PIL import Image
import torch
from src.pdf_generator.gearbox_report_pdf import generate_gearbox_pdf
import matplotlib.pyplot as plt
from reportlab.platypus import Image as RLImage

if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Home"
st.set_page_config(page_title="SmartGear AI", page_icon="⚙️")

project_root = r"C:\Projects\SGMAS"
sys.path.append(project_root)
# including app folder to allow direct import when running as script
sys.path.append(os.path.join(project_root, "app"))




from src.quality_defect.predict_quality import (
    load_quality_model,
    predict_quality,
    QUALITY_CLASSES
)
from src.gear_box_defect.predict import predict_fault_and_severity
from maintenance_dashboard import display_gearbox_diagnosis
from src.pdf_generator.create_pdf import generate_estimate_pdf
from src.utils.config import load_config, save_config

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="SGMAS – Smart Gear Management System",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# --- Authentication gate: show login/signup when not authenticated ---
from login import login_page

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
    st.stop()

# Provide a simple logout control in the sidebar when authenticated
def _safe_rerun():
    if hasattr(st, "experimental_rerun"):
        try:
            st.experimental_rerun()
            return
        except Exception:
            pass
    st.stop()

with st.sidebar:
    st.markdown("---")
    
    # User Profile Section
    if "username" in st.session_state and st.session_state.username:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
                <div style="padding: 10px; background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%); 
                            border-radius: 10px; color: white; text-align: center;">
                    <b>👤 {st.session_state.username}</b><br>
                    <small>{st.session_state.get('role', 'User')}</small>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("🚪", help="Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.token = None
                st.session_state.username = None
                st.session_state.role = None
                _safe_rerun()
    else:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.token = None
            _safe_rerun()

# ==================== CUSTOM CSS ====================


st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    :root {
        --primary-color: #FF6B6B;
        --secondary-color: #4ECDC4;
        --accent-color: #FFE66D;
        --dark-bg: #1a1a1a;
        --light-bg: #f8f9fa;
        --card-bg: #ffffff;
        --text-dark: #2c3e50;
        --text-light: #7f8c8d;
    }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    /* Hero Header */
    .hero-header {
        background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 50%, #FFE66D 100%);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: white;
        padding: 60px 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        text-align: center;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .hero-header h1 {
        margin: 0;
        font-size: 3.5em;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .hero-header p {
        margin: 15px 0 0 0;
        font-size: 1.3em;
        opacity: 0.95;
        font-weight: 300;
    }
    
    /* Tab Styling */
    .custom-tab {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 30px;
        border-radius: 12px;
        margin: 5px;
        cursor: pointer;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
        display: inline-block;
    }
    
    .custom-tab:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        border-left: 5px solid #FF6B6B;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .feature-card h3 {
        color: #FF6B6B;
        margin-top: 0;
        font-size: 1.5em;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: scale(1.05);
    }
    
    .metric-card h4 {
        margin: 0 0 10px 0;
        font-size: 0.9em;
        opacity: 0.9;
    }
    
    .metric-card .value {
        font-size: 2.5em;
        font-weight: 700;
        margin: 0;
    }
    
    /* Success Card */
    .success-card {
        background: linear-gradient(135deg, #06A77D 0%, #048859 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 6px 20px rgba(6, 167, 125, 0.3);
        text-align: center;
    }
    
    .success-card h3 {
        margin: 0 0 15px 0;
        font-size: 1.3em;
        opacity: 0.9;
    }
    
    .success-card .price {
        font-size: 3.5em;
        font-weight: 700;
        margin: 0;
    }
    
    /* Input Section */
    .input-section {
        background: white;
        padding: 30px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-top: 4px solid #FF6B6B;
    }
    
    
    /* Results Grid */
    .result-card {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .result-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .result-status {
        padding: 15px;
        text-align: center;
        font-weight: 600;
    }
    
    .result-good {
        background: linear-gradient(135deg, #06A77D 0%, #048859 100%);
        color: white;
    }
    
    .result-defect {
        background: linear-gradient(135deg, #FF6B6B 0%, #E05555 100%);
        color: white;
    }
    
    /* Breakdown Table */
    .breakdown-table {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin: 20px 0;
    }
    
    .breakdown-table h3 {
        color: #FF6B6B;
        margin-top: 0;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 30px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4) !important;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(to right, transparent, #FF6B6B, transparent);
        margin: 30px 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 30px;
        color: #7f8c8d;
        font-size: 0.95em;
        border-top: 2px solid #ecf0f1;
        margin-top: 50px;
    }
    
    /* Sidebar */
    .sidebar-header {
        background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
    }
    
    </style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 'Home'

# ==================== HELPER FUNCTIONS ====================

def display_home_features():
    """Display home page with features"""
    st.markdown("""
        <div class="hero-header">
            <h1>⚙️ SGMAS</h1>
            <p>Smart Gear Management & Analysis System</p>
            <p style="font-size: 1em; margin-top: 20px;">Intelligent Solutions for Gear Quality Detection, Price Prediction & Gearbox Diagnosis</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

def display_quality_detection():
    """Display gear quality detection module"""
    st.markdown("""
        <div class="hero-header" style="padding: 40px; margin-bottom: 30px;">
            <h1>🖼️ Gear Quality Detection</h1>
            <p>AI-Powered Image Analysis for Defect Detection</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="info-box">
            <h4>📋 How to Use</h4>
            <p>Upload one or multiple gear images. Our AI will analyze each image to detect quality defects and classify gears as GOOD or DEFECT.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load quality model
    @st.cache_resource
    def load_quality_model_cached():
        return load_quality_model("data/models/quality_model_weights.pth")
    
    try:
        model = load_quality_model_cached()
    except FileNotFoundError:
        st.error("❌ Quality model not found. Please train the model first.")
        return
    
    # File uploader
    st.markdown("<div class='input-section'>", unsafe_allow_html=True)
    st.markdown("### 📤 Upload Gear Images")
    uploaded_files = st.file_uploader(
        "Select one or multiple gear images",
        type=["jpg", "jpeg", "png", "bmp"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    if uploaded_files:
        results = []
        st.markdown("---")
        st.markdown("### 🔍 Detection Results")
        
        # Create columns for image display
        cols = st.columns(3)
        col_index = 0
        
        for file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(file.getbuffer())
                temp_path = tmp.name
            
            try:
                prediction = predict_quality(temp_path, model)
                
                with cols[col_index]:
                    st.markdown(f"""
                        <div class="result-card">
                            <img src='file://{os.path.abspath(file.name)}' style='display:none;'>
                    """, unsafe_allow_html=True)
                    
                    img = Image.open(file)
                    # Resize image to 200x200 pixels
                    img_resized = img.resize((200, 200), Image.Resampling.LANCZOS)
                    st.image(img_resized)
                    
                    if prediction == "GOOD":
                        st.markdown("""
                            <div class="result-status result-good">
                                ✅ GOOD QUALITY
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                            <div class="result-status result-defect">
                                ⚠️ DEFECT DETECTED
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown(f"<p style='text-align: center; color: #7f8c8d;'>{file.name}</p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                results.append({
                    "Image Name": file.name,
                    "Status": prediction,
                    "Quality": "✅ Good" if prediction == "GOOD" else "⚠️ Defect"
                })
                
                col_index = (col_index + 1) % 3
            finally:
                os.remove(temp_path)
        
        # Summary Statistics
        st.markdown("---")
        st.markdown("### 📊 Summary Statistics")
        
        df = pd.DataFrame(results)
        
        col1, col2, col3 = st.columns(3)
        good_count = (df["Status"] == "GOOD").sum()
        defect_count = (df["Status"] == "DEFECT").sum()
        
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <h4>Total Images</h4>
                    <p class="value">{len(df)}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <h4>✅ Good Quality</h4>
                    <p class="value" style="color: #06A77D;">{good_count}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <h4>⚠️ Defects</h4>
                    <p class="value" style="color: #FF6B6B;">{defect_count}</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Results table
        st.markdown("### 📋 Detailed Results")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    else:
        st.markdown("""
            <div class="info-box" style="text-align: center; padding: 40px;">
                <h3>⬆️ Upload Gear Images to Begin Detection</h3>
                <p>Drag and drop or click to select gear images for quality analysis</p>
            </div>
        """, unsafe_allow_html=True)

def display_price_prediction():
    """Display gear price prediction module"""
    st.markdown("""
        <div class="hero-header" style="padding: 40px; margin-bottom: 30px;">
            <h1>💰 Gear Price Predictor</h1>
            <p>Intelligent Pricing for Precision Gears</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="info-box">
            <h4>💡 Smart Pricing Engine</h4>
            <p>Enter gear specifications below and our advanced ML model will calculate an accurate price estimate including material costs, labor, and special treatments.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load config
    config = load_config()
    
    # Check if model exists
    model_path = os.path.join(project_root, 'data', 'models', 'gear_price_model.pkl')
    if not os.path.exists(model_path):
        st.error(f"❌ Trained model not found. Please train the price prediction model first.")
        return
    
    model = joblib.load(model_path)
    
    # Input Section
    st.markdown("<div class='input-section'>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Enter Gear Specifications")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        gear_type = st.selectbox("🔧 Gear Type", ["Spur", "Helical", "Bevel"], key="gear_type")
        diameter = st.slider("📏 Diameter (mm)", 50, 300, 100, key="diameter")
        thickness = st.slider("📐 Thickness (mm)", int(diameter*0.05), int(diameter*0.2), int(diameter*0.1), key="thickness")
    
    with col2:
        material = st.selectbox("🛠️ Material", ["Steel", "Alloy Steel", "Carbon Steel"], key="material")
        teeth = st.slider("🦷 Teeth Count", int(diameter*0.3), int(diameter*0.6), int(diameter*0.5), key="teeth")
        quantity = st.slider("📦 Quantity", 1, 500, 50, key="quantity")
    
    with col3:
        special_req = st.selectbox("✨ Special Treatment", ["None", "Hardening", "Coating"], key="special_req")
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
        predict_btn = st.button("💰 Calculate Price", use_container_width=True, key="predict_btn")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if predict_btn:
        # Calculate weight
        outer_radius = diameter / 2
        inner_radius = outer_radius * 0.3
        volume_cm3 = 3.1416 * (outer_radius**2 - inner_radius**2) * thickness * 0.1
        material_density = {'Steel': 7.85, 'Alloy Steel': 7.8, 'Carbon Steel': 7.7}
        weight_kg = volume_cm3 * material_density[material] / 1000
        
        # Prepare input for model
        input_df = pd.DataFrame([{
            'Gear_Type': gear_type,
            'Material': material,
            'Diameter_mm': diameter,
            'Teeth_Count': teeth,
            'Thickness_mm': thickness,
            'Quantity': quantity,
            'Special_Requirement': special_req,
            'Weight_kg': round(weight_kg, 2)
        }])
        
        base_price = model.predict(input_df)[0]
        
        # Cost calculations
        material_cost = weight_kg * config["material_rate_per_kg"].get(material, 100)
        treatment_cost = config["surface_treatment_charge"].get(special_req, 0) * quantity
        labor_hours_per_gear = 0.5 + 0.01*teeth
        machine_hours_per_gear = 0.5 + 0.005*diameter
        labor_cost = labor_hours_per_gear * config["labor_rate_per_hour"] * quantity
        machine_cost = machine_hours_per_gear * config["machine_hourly_cost"] * quantity
        urgency_multiplier = 1 + config["urgency_percentage"]/100
        
        predicted_price = (base_price + material_cost + treatment_cost + labor_cost + machine_cost) * urgency_multiplier
        
        # Display price
        st.markdown(f"""
            <div class="success-card">
                <h3>Estimated Total Price</h3>
                <p class="price">₹ {predicted_price:,.2f}</p>
                <p>Quantity: {quantity} units | Weight: {weight_kg:.2f} kg</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Cost breakdown
        cost_breakdown = {
            "Base ML Price": base_price,
            "Material Cost": material_cost,
            "Labor Cost": labor_cost,
            "Machine Cost": machine_cost,
            "Surface Treatment": treatment_cost,
            "Urgency Adjustment": predicted_price - (base_price + material_cost + treatment_cost + labor_cost + machine_cost)
        }
        
        customer_input = {
            "Gear Type": gear_type,
            "Material": material,
            "Diameter (mm)": diameter,
            "Teeth Count": teeth,
            "Thickness (mm)": thickness,
            "Quantity": quantity,
            "Special Requirement": special_req,
            "Weight (kg)": round(weight_kg, 2)
        }
        
        # Cost breakdown table
        st.markdown("<div class='breakdown-table'>", unsafe_allow_html=True)
        st.markdown("### 📊 Cost Breakdown")
        
        breakdown_df = pd.DataFrame(list(cost_breakdown.items()), columns=['Component', 'Amount (₹)'])
        breakdown_df['Amount (₹)'] = breakdown_df['Amount (₹)'].apply(lambda x: f"₹ {x:,.2f}")
        
        st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Specifications summary
        st.markdown("### 📋 Specifications Summary")
        spec_df = pd.DataFrame(list(customer_input.items()), columns=['Parameter', 'Value'])
        st.dataframe(spec_df, use_container_width=True, hide_index=True)
        
        # PDF Download
        st.markdown("---")
        pdf_path = generate_estimate_pdf(customer_input, predicted_price, cost_breakdown)
        
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download Estimate PDF",
                data=f,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf",
                use_container_width=True
            )
            
# def generate_signal_plots(csv_path, rms, energy, rms_th, energy_th):
#     img_dir = "data/reports/plots"
#     os.makedirs(img_dir, exist_ok=True)

#     df = pd.read_csv(csv_path)

#     # Time-domain plot
#     plt.figure(figsize=(6, 3))
#     plt.plot(df.iloc[:, 0], linewidth=0.8)
#     plt.title("Vibration Signal (Time Domain)")
#     plt.xlabel("Samples")
#     plt.ylabel("Amplitude")
#     time_plot = os.path.join(img_dir, "time_signal.png")
#     plt.tight_layout()
#     plt.savefig(time_plot)
#     plt.close()

#     # RMS bar chart
#     plt.figure(figsize=(4, 3))
#     plt.bar(["RMS", "Threshold"], [rms, rms_th])
#     plt.title("RMS vs Threshold")
#     rms_plot = os.path.join(img_dir, "rms_plot.png")
#     plt.tight_layout()
#     plt.savefig(rms_plot)
#     plt.close()

#     # Energy bar chart
#     plt.figure(figsize=(4, 3))
#     plt.bar(["Energy", "Threshold"], [energy, energy_th])
#     plt.title("Energy vs Threshold")
#     energy_plot = os.path.join(img_dir, "energy_plot.png")
#     plt.tight_layout()
#     plt.savefig(energy_plot)
#     plt.close()

#     return time_plot, rms_plot, energy_plot


def display_admin_login():
    """Display admin login form"""
    st.markdown("""
        <style>
        .admin-login-container {
            max-width: 600px;
            margin: 60px auto;
            background: white;
            border-radius: 20px;
            padding: 50px 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        }
        
        .admin-header-hero {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .admin-header-hero h1 {
            background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5em;
            font-weight: 700;
            margin: 0 0 10px 0;
        }
        
        .admin-header-hero p {
            color: #7f8c8d;
            font-size: 0.95em;
            margin: 0;
        }
        </style>
        <div class="admin-login-container">
            <div class="admin-header-hero">
                <h1>🔐 Admin Access</h1>
                <p>Secure Configuration Panel</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        username = st.text_input("👤 Username", value="", placeholder="Enter admin username", key="admin_user")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter admin password", key="admin_pass")
        
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        if st.button("🔓 Login", use_container_width=True, key="admin_login_btn"):
            if username == "admin" and password == "admin":
                st.session_state.admin_authenticated = True
                st.success("✅ Authentication successful! Redirecting...")
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Please try again.")
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_admin_panel():
    """Display admin configuration panel"""
    st.markdown("""
        <div class="hero-header" style="padding: 40px; margin-bottom: 30px;">
            <h1>⚙️ Admin Control Panel</h1>
            <p>Manage Pricing, Labor Rates, and Cost Factors</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Check admin status via backend login
    role = st.session_state.get('role', 'guest')
    if role != 'admin':
        st.error('Admin access required. Please log in with an admin account.')
        return
    # Logout and Admin Status
    col1, col2, col3 = st.columns([1.5, 1.5, 1])
    with col1:
        st.markdown(f"""
            <div style="padding: 12px; background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%); 
                        border-radius: 10px; color: white; text-align: center;">
                <b>👨‍💼 Admin Panel</b><br>
                <small>Configuration Mode</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True, key="logout_admin_btn"):
            st.session_state.logged_in = False
            st.session_state.token = None
            st.session_state.role = 'guest'
            st.session_state.admin_authenticated = False
            st.experimental_rerun()
    
    st.markdown("---")
    
    config = load_config()
    
    # Create tabs for better organization
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💰 Material Rates",
        "🏭 Labor & Machine",
        "✨ Treatments",
        "⚡ Urgency",
        "📊 Configuration View"
    ])
    
    # Tab 1: Material Rates
    with tab1:
        st.markdown("""
            <div class="feature-card">
                <h3>💰 Material Rates Per Kilogram</h3>
                <p>Configure the cost per kilogram for different materials</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        materials = list(config["material_rate_per_kg"].keys())
        
        for idx, material in enumerate(materials):
            col = [col1, col2, col3][idx % 3]
            with col:
                st.markdown(f"""
                    <div class="metric-card" style="background: white; color: #2c3e50; text-align: left; padding: 20px;">
                        <h4 style="color: #FF6B6B; margin: 0 0 10px 0;">{material}</h4>
                """, unsafe_allow_html=True)
                
                config["material_rate_per_kg"][material] = st.number_input(
                    f"Rate (₹/kg)",
                    value=float(config["material_rate_per_kg"][material]),
                    step=10.0,
                    key=f"material_{material}",
                    label_visibility="collapsed"
                )
                
                st.markdown(f"""
                        <p style="margin: 10px 0 0 0; color: #7f8c8d; font-size: 0.9em;">Current: ₹{config['material_rate_per_kg'][material]:.2f}/kg</p>
                    </div>
                """, unsafe_allow_html=True)
    
    # Tab 2: Labor & Machine Costs
    with tab2:
        st.markdown("""
            <div class="feature-card">
                <h3>🏭 Labor & Machine Cost Configuration</h3>
                <p>Set hourly rates for labor and machine operations</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; color: white; border-radius: 15px;">
                    <h3 style="margin: 0 0 20px 0;">👷 Labor Rate</h3>
            """, unsafe_allow_html=True)
            
            config["labor_rate_per_hour"] = st.number_input(
                "Labor Rate (₹/hour)",
                value=float(config["labor_rate_per_hour"]),
                step=50.0,
                key="labor_rate",
                label_visibility="collapsed"
            )
            
            st.markdown(f"""
                    <p style="margin: 15px 0 0 0; opacity: 0.9;">Current: ₹{config['labor_rate_per_hour']:.2f}/hour</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="metric-card" style="background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%); padding: 20px; color: white; border-radius: 15px;">
                    <h3 style="margin: 0 0 20px 0;">🤖 Machine Cost</h3>
            """, unsafe_allow_html=True)
            
            config["machine_hourly_cost"] = st.number_input(
                "Machine Cost (₹/hour)",
                value=float(config["machine_hourly_cost"]),
                step=50.0,
                key="machine_cost",
                label_visibility="collapsed"
            )
            
            st.markdown(f"""
                    <p style="margin: 15px 0 0 0; opacity: 0.9;">Current: ₹{config['machine_hourly_cost']:.2f}/hour</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Tab 3: Surface Treatment Charges
    with tab3:
        st.markdown("""
            <div class="feature-card">
                <h3>✨ Surface Treatment Charges Per Unit</h3>
                <p>Set charges for different surface treatment options</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        treatments = list(config["surface_treatment_charge"].keys())
        
        for idx, treatment in enumerate(treatments):
            col = [col1, col2, col3][idx % 3]
            with col:
                st.markdown(f"""
                    <div class="metric-card" style="background: white; color: #2c3e50; text-align: left; padding: 20px;">
                        <h4 style="color: #4ECDC4; margin: 0 0 10px 0;">{treatment}</h4>
                """, unsafe_allow_html=True)
                
                config["surface_treatment_charge"][treatment] = st.number_input(
                    f"Charge (₹)",
                    value=float(config["surface_treatment_charge"][treatment]),
                    step=50.0,
                    key=f"treatment_{treatment}",
                    label_visibility="collapsed"
                )
                
                st.markdown(f"""
                        <p style="margin: 10px 0 0 0; color: #7f8c8d; font-size: 0.9em;">Current: ₹{config['surface_treatment_charge'][treatment]:.2f}</p>
                    </div>
                """, unsafe_allow_html=True)
    
    # Tab 4: Urgency Adjustment
    with tab4:
        st.markdown("""
            <div class="feature-card">
                <h3>⚡ Urgency Multiplier Configuration</h3>
                <p>Set percentage markup for urgent orders</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="info-box">
                <p><strong>📌 How it works:</strong> This percentage is added as a multiplier to the final price for urgent orders. 
                For example, 20% means prices will be multiplied by 1.20x for urgent requests.</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            config["urgency_percentage"] = st.slider(
                "Urgency Percentage (%)",
                min_value=0,
                max_value=100,
                value=int(config["urgency_percentage"]),
                step=5,
                key="urgency"
            )
            
            st.markdown(f"""
                <div class="feature-card">
                    <h4>Price Multiplier Impact</h4>
                    <p>With {int(config['urgency_percentage'])}% urgency adjustment:</p>
                    <p style="font-size: 1.3em; color: #FF6B6B; font-weight: 600;">Base Price × {1 + config['urgency_percentage']/100:.2f}x</p>
                    <p style="color: #7f8c8d; font-size: 0.9em;">Example: ₹100,000 would become ₹{100000 * (1 + config['urgency_percentage']/100):,.2f}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <h4>Multiplier</h4>
                    <p class="value" style="font-size: 2em; margin: 10px 0;">{1 + config['urgency_percentage']/100:.2f}x</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Tab 5: Configuration View
    with tab5:
        st.markdown("""
            <div class="feature-card">
                <h3>📊 Current Configuration Overview</h3>
                <p>View all active system configuration settings</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Material Rates Summary
        st.markdown("### 💰 Material Rates (per kg)")
        material_df = pd.DataFrame(
            list(config["material_rate_per_kg"].items()),
            columns=["Material", "Rate (₹/kg)"]
        )
        material_df["Rate (₹/kg)"] = material_df["Rate (₹/kg)"].apply(lambda x: f"₹{x:.2f}")
        st.dataframe(material_df, use_container_width=True, hide_index=True)
        
        # Labor & Machine Summary
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👷 Labor Rate")
            st.markdown(f"""
                <div class="metric-card">
                    <p class="value">₹{config['labor_rate_per_hour']:.2f}</p>
                    <p>per hour</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🤖 Machine Cost")
            st.markdown(f"""
                <div class="metric-card">
                    <p class="value">₹{config['machine_hourly_cost']:.2f}</p>
                    <p>per hour</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Treatment Charges Summary
        st.markdown("### ✨ Treatment Charges")
        treatment_df = pd.DataFrame(
            list(config["surface_treatment_charge"].items()),
            columns=["Treatment", "Charge (₹)"]
        )
        treatment_df["Charge (₹)"] = treatment_df["Charge (₹)"].apply(lambda x: f"₹{x:.2f}")
        st.dataframe(treatment_df, use_container_width=True, hide_index=True)
        
        # Urgency Summary
        st.markdown("### ⚡ Urgency Configuration")
        st.markdown(f"""
            <div class="success-card" style="text-align: left;">
                <h4>Current Urgency Multiplier: <strong>{1 + config['urgency_percentage']/100:.2f}x</strong></h4>
                <p>Markup: <strong>{int(config['urgency_percentage'])}%</strong></p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Save button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💾 Save All Changes", use_container_width=True, key="save_btn"):
            save_config(config)
            st.success("✅ Configuration saved successfully!")
            st.balloons()

# ==================== MAIN APP ====================

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
        <div class="sidebar-header">
            <h2>⚙️ SGMAS</h2>
            <p>Smart Gear Management System</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### �️ Navigation")

    role = st.session_state.get('role', 'guest')
    nav_items = [
        ("🏠 Home", "Home"),
    ]
    if role != 'guest':
        nav_items.append(("🔔 Notifications", "Notifications"))

    # Role-based navigation
    if role == 'user':
        nav_items.append(("💰 Price Prediction", "Price Prediction"))
    elif role == 'inventory_head':
        nav_items.extend([
            ("🖼️ Quality Detection", "Quality Detection"),
            ("📋 Inventory", "Inventory"),
            ("✓ Approve Requests", "Approve Requests"),
        ])
    elif role == 'maintenance_head':
        nav_items.append(("⚙️ Gearbox Diagnosis", "Gearbox Diagnosis"))
    elif role == 'production_head':
        nav_items.extend([
            ("🖼️ Quality Detection", "Quality Detection"),
            ("💰 Price Prediction", "Price Prediction"),
            ("⚙️ Gearbox Diagnosis", "Gearbox Diagnosis"),
            ("📝 Material Request", "Material Request"),
        ])
    elif role == 'scm_head':
        nav_items.extend([
            ("🛒 SCM Dashboard", "SCM Dashboard"),
            ("📋 Inventory", "Inventory"),
        ])
    elif role == 'scm_planner':
        # planner can view dashboard to see material requests and create PRs
        nav_items.extend([
            ("🛒 SCM Dashboard", "SCM Dashboard"),
            ("📝 Purchase Requests", "Purchase Requests"),
        ])
    elif role == 'scm_purchaser':
        # purchaser needs access to both PR list (to see what to order) and POs
        nav_items.extend([
            ("📝 Purchase Requests", "Purchase Requests"),
            ("📦 Purchase Orders", "Purchase Orders"),
        ])
    elif role == 'admin':
        nav_items.extend([
            ("🔧 Admin Panel", "Admin Panel"),
            ("🧾 Pending Signups", "Admin Requests"),
            ("👥 Manage Heads", "Manage Heads"),
        ])
    else:
        # guest or unknown: show Home only
        pass

    for label, key in nav_items:
        if st.button(label, use_container_width=True):
            st.session_state.current_tab = key
            st.rerun()

    st.markdown("---")
    st.markdown("### 📊 System Info")
    st.metric("Modules", 5)

    st.markdown("---")
    st.markdown("""
        **SGMAS**  
        AI-powered Gear Quality, Pricing & Diagnostics System
    """)

# ==================== MAIN CONTENT ====================

# ==================== MAIN CONTENT ====================

current = st.session_state.current_tab

if current == "Home":
    display_home_features()

elif current == "Quality Detection":
    display_quality_detection()

elif current == "Price Prediction":
    display_price_prediction()

elif current == "Gearbox Diagnosis":
    display_gearbox_diagnosis()

elif current == "Admin Panel":
    display_admin_panel()

elif current == "Admin Requests":
    from admin_requests import display_pending_requests
    display_pending_requests()

elif current == "Manage Heads":
    from manage_heads import display_manage_heads
    display_manage_heads()

elif current == "SCM Dashboard":
    # inventory head / scm_head sees overall workflow
    from scm_chain import display_scm_dashboard
    display_scm_dashboard()

elif current == "Inventory":
    from scm_chain import display_inventory_management
    display_inventory_management()

elif current == "Material Request":
    from scm_chain import display_production_requests
    display_production_requests()

elif current == "Notifications":
    from scm_chain import display_notifications
    display_notifications()

elif current == "Purchase Requests":
    from scm_chain import display_purchase_requests
    display_purchase_requests()

elif current == "Purchase Orders":
    from scm_chain import display_purchase_orders
    display_purchase_orders()

elif current == "Approve Requests":
    from inventory_manager import display_approve_requests
    display_approve_requests()
    
# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
    <div class="footer">
        <p>⚙️ <strong>SGMAS</strong> – Smart Gear Management & Analysis System</p>
        <p>Advanced AI Solutions for Precision Gear Manufacturing, Quality Control & Gearbox Diagnostics</p>
        <p style="font-size: 0.85em; opacity: 0.7;">© 2026 | Intelligent Gear Solutions | Powered by Machine Learning</p>
    </div>
""", unsafe_allow_html=True)