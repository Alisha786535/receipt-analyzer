import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import tempfile
import os
import sys

# Add modules path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/modules")

from modules.image_processor import ImageProcessor
from modules.ocr_engine import OCREngine
from modules.data_parser import DataParser  # Fixed typo
from modules.categorizer import ExpenseCategorizer
from modules.analyzer import SpendingAnalyzer
from modules.llm_advisor import LLMAdvisor

st.set_page_config(page_title="AI Receipt Analyzer", page_icon="🧾", layout="wide")

# Initialize components
@st.cache_resource
def init_components():
    return {
        'image_processor': ImageProcessor(),
        'ocr': OCREngine(use_easyocr=True),
        'parser': DataParser(),
        'categorizer': ExpenseCategorizer(),
        'analyzer': SpendingAnalyzer(),
        'advisor': LLMAdvisor()
    }

components = init_components()

col1, col2 = st.columns([1,1])

with col1:
    st.header("📤 Upload Receipt")
    uploaded_file = st.file_uploader("Choose a receipt image", type=['png','jpg','jpeg','bmp','tiff'])

    if uploaded_file:
        # Save temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        # Display original image
        st.subheader("Original Receipt")
        image = Image.open(tmp_path)
        st.image(image, use_column_width=True)

with col2:
    if uploaded_file:
        st.header("🔄 Processing")
        with st.spinner("Processing receipt..."):
            # Image preprocessing
            processed_img = components['image_processor'].preprocess(tmp_path)

            # OCR extraction
            extracted_text = components['ocr'].extract_text(processed_img)
            with st.expander("View extracted text"):
                st.text(extracted_text)

            # Parse items
            items = components['parser'].parse(extracted_text)

            if items:
                categorized = components['categorizer'].categorize(items)
                category_totals = components['categorizer'].calculate_category_totals(categorized)
                total = components['parser'].calculate_total(items)
                percentages = components['analyzer'].calculate_percentages(category_totals, total)
                anomalies = components['analyzer'].identify_anomalies(category_totals)
                summary_stats = components['analyzer'].generate_summary_stats(items, categorized)
                st.success("✅ Processing complete!")
            else:
                st.error("No items extracted. Try a clearer image.")

# Cleanup temp file at the end
if uploaded_file:
    try:
        os.unlink(tmp_path)
    except Exception:
        pass
