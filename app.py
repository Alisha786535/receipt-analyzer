import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import tempfile
import os
import sys

# Add modules to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.image_processor import ImageProcessor
from modules.ocr_engine import OCREngine
from modules.data_sparser import DataParser
from modules.categorizer import ExpenseCategorizer
from modules.analyzer import SpendingAnalyzer
from modules.llm_advisor import LLMAdvisor

# Page configuration
st.set_page_config(
    page_title="AI Receipt Analyzer",
    page_icon="🧾",
    layout="wide"
)

# Title and motivation
st.title("🧾 AI-Powered Receipt Analyzer")
st.markdown("> *You don't have to see the whole staircase, just take the first step.*")
st.markdown("---")

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

# Sidebar for API key input
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Gemini API Key (optional)", type="password")
    if api_key:
        components['advisor'].api_key = api_key
        components['advisor'].use_llm = True
        components['advisor'].__init__(api_key=api_key)
    
    st.markdown("---")
    st.markdown("### How it works")
    st.markdown("""
    1. Upload a receipt image
    2. Image preprocessing enhances text
    3. OCR extracts text from receipt
    4. AI parses items and prices
    5. Expenses are categorized
    6. Get personalized advice
    """)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Upload Receipt")
    uploaded_file = st.file_uploader(
        "Choose a receipt image",
        type=['png', 'jpg', 'jpeg', 'bmp', 'tiff']
    )
    
    if uploaded_file:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Display original image
        st.subheader("Original Receipt")
        image = Image.open(uploaded_file)
        st.image(image, width='stretch')

with col2:
    if uploaded_file:
        st.header("🔄 Processing")
        
        with st.spinner("Processing receipt..."):
            # Step 1: Image preprocessing
            st.info("1. Preprocessing image...")
            processed_img = components['image_processor'].preprocess(tmp_path)
            
            # Step 2: OCR extraction
            st.info("2. Extracting text with OCR...")
            extracted_text = components['ocr'].extract_text(processed_img)
            
            # Show extracted text in expander
            with st.expander("View extracted text"):
                st.text(extracted_text)
            
            # Step 3: Parse data
            st.info("3. Parsing items and prices...")
            items = components['parser'].parse(extracted_text)
            
            if items:
                # Step 4: Categorize expenses
                st.info("4. Categorizing expenses...")
                categorized = components['categorizer'].categorize(items)
                
                # Calculate totals
                category_totals = components['categorizer'].calculate_category_totals(categorized)
                total = components['parser'].calculate_total(items)
                
                # Step 5: Analyze spending
                st.info("5. Analyzing spending patterns...")
                percentages = components['analyzer'].calculate_percentages(category_totals, total)
                anomalies = components['analyzer'].identify_anomalies(category_totals)
                summary_stats = components['analyzer'].generate_summary_stats(items, categorized)
                
                st.success("✅ Processing complete!")
            else:
                st.error("No items could be extracted. Please try a clearer image.")

# Results section
if uploaded_file and items:
    st.markdown("---")
    st.header("📊 Spending Analysis")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Items", summary_stats['total_items'])
    with col2:
        st.metric("Total Spent", f"${summary_stats['total_spent']:.2f}")
    with col3:
        st.metric("Avg Item Price", f"${summary_stats['avg_item_price']:.2f}")
    with col4:
        st.metric("Categories", summary_stats['category_count'])
    
    # Two columns for detailed analysis
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("📋 Items by Category")
        
        # Create DataFrame for display
        items_data = []
        for category, cat_items in categorized.items():
            for item in cat_items:
                items_data.append({
                    'Category': category,
                    'Item': item.name,
                    'Quantity': item.quantity,
                    'Price': f"${item.price:.2f}"
                })
        
        df = pd.DataFrame(items_data)
        st.dataframe(df, width='stretch', hide_index=True)
    
    with col_right:
        st.subheader("💰 Spending by Category")
        
        # Create pie chart
        fig = px.pie(
            values=list(category_totals.values()),
            names=list(category_totals.keys()),
            title="Expense Distribution"
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, width='stretch')
        
        # Category totals table
        totals_data = []
        for category, amount in category_totals.items():
            totals_data.append({
                'Category': category,
                'Amount': f"${amount:.2f}",
                'Percentage': f"{percentages.get(category, 0):.1f}%"
            })
        
        st.dataframe(pd.DataFrame(totals_data), width='stretch', hide_index=True)
    
    # Anomalies section
    if anomalies:
        st.markdown("---")
        st.subheader("⚠️ Spending Anomalies Detected")
        
        for anomaly in anomalies:
            severity_color = "🔴" if anomaly['severity'] == 'High' else "🟡"
            st.warning(
                f"{severity_color} **{anomaly['category']}**: "
                f"${anomaly['amount']:.2f} (${anomaly['excess']:.2f} above threshold)"
            )
    
    # LLM Advice section
    st.markdown("---")
    st.header("🤖 AI-Powered Financial Advice")
    
    with st.spinner("Generating personalized advice..."):
        advice = components['advisor'].generate_advice(
            summary_stats, anomalies, percentages
        )
        
        if 'advice' in advice:  # LLM response
            st.markdown(advice['advice'])
            st.caption(f"Source: {advice['source']}")
        else:  # Rule-based response
            if advice['summary']:
                st.info(advice['summary'])
            
            st.subheader("💡 Money-Saving Tips")
            for tip in advice['tips']:
                st.markdown(f"• {tip}")
            
            st.subheader("🌟 Positive Notes")
            for note in advice['positive_notes']:
                st.markdown(f"✓ {note}")
            
            st.caption(f"Source: {advice['source']}")
    
    # Download results
    st.markdown("---")
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Analysis as CSV",
        data=csv,
        file_name="receipt_analysis.csv",
        mime="text/csv"
    )
    
    # Cleanup
    os.unlink(tmp_path)

# Footer
st.markdown("---")
st.markdown(
    "Built with ❤️ using Streamlit, OpenCV, Tesseract/EasyOCR, and Gemini AI"
)
