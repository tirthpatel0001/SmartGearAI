import streamlit as st
import os
import tempfile
from PIL import Image
import torch
import pandas as pd

from src.quality_defect.predict_quality import (
    load_quality_model,
    predict_quality,
    QUALITY_CLASSES
)

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="SGMAS – Gear Quality Detection",
    layout="wide"
)

# ================= HEADER =================
st.title("⚙️ SGMAS – Smart Gear AI")
st.subheader("🖼️ Gear Image Quality & Defect Detection")

st.markdown("---")

# ================= MODEL LOAD =================
@st.cache_resource
def load_model():
    return load_quality_model("data/models/quality_model_weights.pth")

try:
    model = load_model()
except FileNotFoundError:
    st.error("❌ Model not found. Please train the quality model first.")
    st.stop()

# ================= UPLOAD SECTION =================
st.header("📤 Upload Gear Image(s)")

uploaded_files = st.file_uploader(
    "Upload one or multiple gear images",
    type=["jpg", "jpeg", "png", "bmp"],
    accept_multiple_files=True
)

if uploaded_files:
    results = []

    st.markdown("### 🔍 Detection Results")

    cols = st.columns(3)
    col_index = 0

    for file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(file.getbuffer())
            temp_path = tmp.name

        prediction = predict_quality(temp_path, model)

        # Display image card
        with cols[col_index]:
            img = Image.open(file)
            st.image(img, width=260)
            if prediction == "GOOD":
                st.success("✅ GOOD")
            else:
                st.error("⚠️ DEFECT")

        results.append({
            "Image Name": file.name,
            "Prediction": prediction
        })

        col_index = (col_index + 1) % 3
        os.remove(temp_path)

    # ================= SUMMARY TABLE =================
    st.markdown("---")
    st.header("📊 Summary")

    df = pd.DataFrame(results)
    st.dataframe(df, width="container")

    good_count = (df["Prediction"] == "GOOD").sum()
    defect_count = (df["Prediction"] == "DEFECT").sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Images", len(df))
    col2.metric("✅ GOOD", good_count)
    col3.metric("⚠️ DEFECT", defect_count)

else:
    st.info("⬆️ Upload gear image(s) to begin detection")

# ================= FOOTER =================
st.markdown("---")
st.caption("SGMAS – Smart Gear AI System | Image-based Quality Detection")
