import streamlit as st
from src.gear_box_defect.train import train_models
from src.gear_box_defect.predict import predict_fault
from src.gear_box_defect.recommendation import get_recommendation
from src.quality_defect.defect_defects import load_defect_model, detect_defects
import os
import cv2
import numpy as np
from PIL import Image
import tempfile

st.set_page_config(page_title="SGMAS – Gearbox Defect Detection", layout="wide")

st.title("⚙️ SGMAS – Smart Gear AI")
st.subheader("Gearbox Defect Detection & Diagnosis")

st.markdown("---")

# ---------------- TRAINING SECTION ----------------
st.header("🔧 Model Training (Admin)")

st.info(
    "Use this option only if models are not trained yet "
    "or if new data is added."
)

if st.button("Train Gearbox Models"):
    with st.spinner("Training models... this may take a few minutes"):
        train_models()
    st.success("✅ Models trained and saved successfully!")

st.markdown("---")

# ---------------- IMAGE DEFECT DETECTION SECTION ----------------
st.header("🖼️ Image Defect Detection")

st.info(
    "Upload an image to detect defects using computer vision. "
    "The system will analyze the image and highlight any detected defects."
)

uploaded_image = st.file_uploader(
    "Upload Image for Defect Detection",
    type=["jpg", "jpeg", "png", "bmp"]
)

if uploaded_image is not None:
    try:
        # Load the defect detection model
        defect_model = load_defect_model("data/models/defect_model.pth")
        
        # Save uploaded image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            tmp_file.write(uploaded_image.getbuffer())
            temp_image_path = tmp_file.name
        
        with st.spinner("Detecting defects in image..."):
            result_img, defects = detect_defects(temp_image_path, defect_model, threshold=0.5)
        
        # Display results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📸 Original Image")
            original_img = Image.open(uploaded_image)
            st.image(original_img, use_column_width=True)
        
        with col2:
            st.subheader("🔍 Defects Detected")
            result_img_rgb = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)
            st.image(result_img_rgb, use_column_width=True)
        
        # Display defect summary
        st.subheader("📊 Detection Summary")
        if defects:
            st.success(f"✅ Found {len(defects)} defect(s)")
            for i, defect in enumerate(defects, 1):
                st.write(f"- Defect {i}: **{defect['class']}** at location {defect['bbox']}")
        else:
            st.info("✅ No defects detected in the image")
        
        # Clean up temp file
        os.remove(temp_image_path)
        
    except FileNotFoundError:
        st.error("⚠️ Defect model not found. Please ensure the model is trained first.")
    except Exception as e:
        st.error(f"❌ Error processing image: {str(e)}")

st.markdown("---")

# ---------------- PREDICTION SECTION ----------------
st.header("📊 Gearbox Fault Prediction")

uploaded_file = st.file_uploader(
    "Upload Gearbox Excel File",
    type=["xlsx", "csv"]
)

if uploaded_file is not None:
    with st.spinner("Analyzing gearbox vibration data..."):
        status, fault_type = predict_fault(uploaded_file)

    st.subheader("🧾 Diagnosis Result")

    if status == "Healthy":
        st.success("✅ Gearbox Condition: HEALTHY")
        st.info("No maintenance action required.")
    else:
        st.error("⚠️ Gearbox Condition: FAULT DETECTED")
        st.warning(f"Detected Fault Type: **{fault_type}**")

        recommendation = get_recommendation(fault_type)
        st.markdown("### 🛠 Maintenance Recommendation")
        st.write(recommendation)
