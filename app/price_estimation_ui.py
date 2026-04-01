import streamlit as st
import requests
import json
import pandas as pd
from io import BytesIO
import time

# Page config
st.set_page_config(page_title="Price Estimation", page_icon="💰", layout="wide")

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

def check_access():
    """Check if user has access to this module"""
    if st.session_state.user_role != 'user':
        st.error("❌ Access Denied: Only users can access the Price Estimation module.")
        st.stop()

def estimate_price_api(input_data):
    """Call backend API to estimate price"""
    try:
        headers = {
            'Authorization': f'Bearer {st.session_state.token}',
            'X-User-Role': st.session_state.user_role
        }
        
        response = requests.post(
            'http://localhost:5000/api/estimate-price',
            json=input_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.json().get('error', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def download_pdf_api(input_data, price_estimate, cost_breakdown):
    """Call backend API to generate PDF"""
    try:
        headers = {
            'Authorization': f'Bearer {st.session_state.token}',
            'X-User-Role': st.session_state.user_role
        }
        
        payload = {
            'input_data': input_data,
            'price_estimate': price_estimate,
            'cost_breakdown': cost_breakdown
        }
        
        response = requests.post(
            'http://localhost:5000/api/generate-pdf',
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Error: {response.json().get('error', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def main():
    """Main application"""
    # Retrieve token from session state (set by main.py)
    if 'token' not in st.session_state or st.session_state.token is None:
        st.error("❌ Session expired. Please log in again.")
        st.stop()
    
    if 'user_role' not in st.session_state or st.session_state.user_role is None:
        st.session_state.user_role = 'user'
    
    check_access()
    
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%); color: white; padding: 32px; border-radius: 8px; margin-bottom: 24px; border-top: 4px solid #D97706;">
            <h1 style="margin: 0; font-size: 2.2em; font-weight: 700;">💰 Intelligent Price Estimation</h1>
            <p style="margin: 8px 0 0 0; opacity: 0.95;">Calculate optimal gearbox prices based on specifications and market conditions</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Estimation", "Batch Estimation", "Help"])
    
    with tab1:
        st.subheader("Calculate Gear Price")
        
        # BASIC SPECIFICATIONS
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%);
                color: white;
                padding: 16px 20px;
                border-radius: 12px;
                margin: 20px 0 18px 0;
                border-left: 5px solid #D97706;
                font-weight: 700;
                font-size: 1.15em;
                letter-spacing: 0.3px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            ">🔧 Basic Specifications</div>
        """, unsafe_allow_html=True)
        
        basic_col1, basic_col2, basic_col3 = st.columns(3)
        
        with basic_col1:
            gear_type = st.selectbox(
                "Gear Type",
                ["Spur", "Helical", "Bevel", "Worm"],
                key="gear_type"
            )
        
        with basic_col2:
            gearbox_type = st.selectbox(
                "Gearbox Type",
                ["Industrial", "Marine", "Automotive", "Aerospace", "Agricultural"],
                key="gearbox_type"
            )
        
        with basic_col3:
            application = st.text_input(
                "Application (Optional)",
                value="General Purpose",
                key="application"
            )
        
        # TECHNICAL SPECIFICATIONS
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%);
                color: white;
                padding: 16px 20px;
                border-radius: 12px;
                margin: 20px 0 18px 0;
                border-left: 5px solid #D97706;
                font-weight: 700;
                font-size: 1.15em;
                letter-spacing: 0.3px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            ">⚙️ Technical Specifications</div>
        """, unsafe_allow_html=True)
        
        tech_col1, tech_col2, tech_col3, tech_col4, tech_col5 = st.columns(5)
        
        with tech_col1:
            module = st.number_input(
                "Module",
                min_value=0.5,
                max_value=15.0,
                value=2.5,
                step=0.1,
                key="module"
            )
        
        with tech_col2:
            teeth = st.number_input(
                "Teeth",
                min_value=12,
                max_value=200,
                value=50,
                step=1,
                key="teeth"
            )
        
        with tech_col3:
            load_capacity = st.number_input(
                "Load Capacity (kg)",
                min_value=100.0,
                max_value=10000.0,
                value=1000.0,
                step=100.0,
                key="load"
            )
        
        with tech_col4:
            speed = st.number_input(
                "Speed (RPM)",
                min_value=100.0,
                max_value=5000.0,
                value=1200.0,
                step=100.0,
                key="speed"
            )
        
        with tech_col5:
            gear_ratio = st.number_input(
                "Gear Ratio",
                min_value=1.0,
                max_value=100.0,
                value=2.5,
                step=0.1,
                key="gear_ratio"
            )
        
        # MATERIAL
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%);
                color: white;
                padding: 16px 20px;
                border-radius: 12px;
                margin: 20px 0 18px 0;
                border-left: 5px solid #D97706;
                font-weight: 700;
                font-size: 1.15em;
                letter-spacing: 0.3px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            ">🏭 Material</div>
        """, unsafe_allow_html=True)
        
        mat_col1, mat_col2 = st.columns(2)
        
        with mat_col1:
            material = st.selectbox(
                "Material Type",
                ["Steel", "Alloy Steel", "Cast Iron", "Stainless Steel"],
                key="material"
            )
        
        with mat_col2:
            heat_treatment = st.checkbox(
                "Heat Treatment",
                value=True,
                key="heat_treatment"
            )
        
        # MANUFACTURING
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%);
                color: white;
                padding: 16px 20px;
                border-radius: 12px;
                margin: 20px 0 18px 0;
                border-left: 5px solid #D97706;
                font-weight: 700;
                font-size: 1.15em;
                letter-spacing: 0.3px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            ">🔩 Manufacturing</div>
        """, unsafe_allow_html=True)
        
        mfg_col1, mfg_col2, mfg_col3 = st.columns(3)
        
        with mfg_col1:
            surface_finish = st.selectbox(
                "Surface Finish",
                ["Ground", "Polished", "Honed", "Raw"],
                key="surface_finish"
            )
        
        with mfg_col2:
            quantity = st.selectbox(
                "Quantity",
                [1, 5, 10, 25, 50, 100],
                key="quantity"
            )
        
        with mfg_col3:
            delivery_type = st.selectbox(
                "Delivery Type",
                ["Normal", "Urgent"],
                key="delivery_type"
            )
        
        st.markdown("---")
        
        # Estimate Button with spinner
        if st.button("🚀 Estimate Price", use_container_width=True, type="primary"):
            with st.spinner("Calculating price estimation..."):
                time.sleep(0.5)  # Simulate processing
                
                input_data = {
                    "gear_type": gear_type,
                    "gearbox_type": gearbox_type,
                    "material": material,
                    "module": module,
                    "teeth": teeth,
                    "load": load_capacity,
                    "speed": speed,
                    "gear_ratio": gear_ratio,
                    "heat_treatment": heat_treatment,
                    "surface_finish": surface_finish,
                    "quantity": quantity,
                    "delivery_type": delivery_type
                }
                
                result = estimate_price_api(input_data)
                
                if result and result['status'] == 'success':
                    st.session_state.last_estimate = {
                        'input': input_data,
                        'price': result['estimated_price'],
                        'breakdown': result['cost_breakdown']
                    }
                    
                    # Display results
                    st.success("✅ Price estimation completed!")
                    
                    # Price Display
                    st.markdown("### 💵 Estimated Price")
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.metric(
                            label="Total Estimated Price",
                            value=f"₹{result['estimated_price']:,.2f}",
                            delta=None
                        )
                    
                    # Cost Breakdown
                    st.markdown("### 📊 Cost Breakdown")
                    
                    breakdown_data = result['cost_breakdown']
                    breakdown_df = pd.DataFrame({
                        'Component': [
                            'Base Price',
                            'Material Cost',
                            'Manufacturing',
                            'Heat Treatment',
                            'Delivery',
                            'Bulk Discount',
                            'TOTAL'
                        ],
                        'Amount': [
                            breakdown_data.get('base_price', 0),
                            breakdown_data.get('material_cost', 0),
                            breakdown_data.get('manufacturing_cost', 0),
                            breakdown_data.get('heat_treatment_cost', 0),
                            breakdown_data.get('delivery_cost', 0),
                            breakdown_data.get('bulk_discount', 0),
                            breakdown_data.get('total', 0)
                        ]
                    })
                    
                    st.dataframe(
                        breakdown_df.style.format({'Amount': '₹{:,.2f}'}),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # JSON Breakdown
                    st.markdown("### 📋 Detailed Breakdown")
                    st.json(breakdown_data)
                    
                    # Download PDF Button
                    st.markdown("---")
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("📥 Download PDF Report", use_container_width=True):
                            with st.spinner("Generating PDF..."):
                                pdf_content = download_pdf_api(
                                    input_data,
                                    result['estimated_price'],
                                    breakdown_data
                                )
                                
                                if pdf_content:
                                    st.download_button(
                                        label="⬇️ Click to Download PDF",
                                        data=pdf_content,
                                        file_name=f"gear_price_estimate.pdf",
                                        mime="application/pdf"
                                    )
    
    with tab2:
        st.subheader("Batch Price Estimation")
        
        st.markdown("""
        Upload a CSV file with multiple gear specifications to estimate prices in batch.
        
        **Expected columns:**
        - gear_type, gearbox_type, material, module, teeth, load, speed, gear_ratio, 
        heat_treatment, surface_finish, quantity, delivery_type
        """)
        
        uploaded_file = st.file_uploader("Choose CSV file", type="csv", key="batch_upload")
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.write(f"Loaded {len(df)} items for estimation")
                st.dataframe(df.head(), use_container_width=True)
                
                if st.button("🚀 Estimate All Prices"):
                    with st.spinner("Processing batch estimation..."):
                        items = df.to_dict('records')
                        
                        headers = {
                            'Authorization': f'Bearer {st.session_state.token}',
                            'X-User-Role': st.session_state.user_role
                        }
                        
                        try:
                            response = requests.post(
                                'http://localhost:5000/api/estimate-price-batch',
                                json={'items': items},
                                headers=headers,
                                timeout=30
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                
                                st.success(f"✅ Batch complete! {result['successful']}/{result['total_items']} successful")
                                
                                # Extract results
                                results_list = []
                                for r in result['results']:
                                    if r['status'] == 'success':
                                        results_list.append({
                                            'Price': f"${r['estimated_price']:,.2f}",
                                            'Status': 'Success'
                                        })
                                    else:
                                        results_list.append({
                                            'Price': 'N/A',
                                            'Status': 'Failed'
                                        })
                                
                                results_df = pd.DataFrame(results_list)
                                st.dataframe(results_df, use_container_width=True)
                                
                                # Download results
                                csv_buffer = BytesIO()
                                results_df.to_csv(csv_buffer, index=False)
                                csv_buffer.seek(0)
                                
                                st.download_button(
                                    label="📥 Download Results",
                                    data=csv_buffer.getvalue(),
                                    file_name="batch_price_estimates.csv",
                                    mime="text/csv"
                                )
                            else:
                                st.error(f"Error: {response.json()}")
                        except Exception as e:
                            st.error(f"Connection error: {str(e)}")
            
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    with tab3:
        st.subheader("Help & Documentation")
        
        st.markdown("""
        ### 📖 How to Use Price Estimation
        
        1. **Enter Specifications**: Fill in all gear specifications including type, material, and technical parameters
        2. **Select Options**: Choose heat treatment, surface finish, quantity, and delivery type
        3. **Estimate**: Click "Estimate Price" to get the price prediction
        4. **Review**: Check the cost breakdown and detailed analysis
        5. **Download**: Export the report as PDF for sharing
        
        ### 🔍 Parameter Explanations
        
        - **Gear Type**: Spur (simple), Helical (smooth), Bevel (angular), Worm (perpendicular)
        - **Module**: Gear tooth size (higher = larger teeth)
        - **Heat Treatment**: Hardens material for durability (+10% cost)
        - **Delivery Type**: Normal (5 days) or Urgent (2 days, +15% cost)
        - **Quantity**: Bulk orders receive discounts (up to 25% for 100 units)
        
        ### 💡 Tips
        
        - Material choice significantly affects price (Steel is baseline)
        - Larger modules and more teeth increase manufacturing cost
        - Bulk orders provide better per-unit pricing
        - Heat treatment improves durability for high-load applications
        
        ### 📞 Support
        
        For questions, contact: support@smartgearai.com
        """)

if __name__ == "__main__":
    main()
