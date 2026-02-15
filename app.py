if uploaded_file:
    # Save temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    try:
        # Display original receipt
        st.subheader("Original Receipt")
        image = Image.open(tmp_path)
        st.image(image, use_column_width=True)

        # Processing in column 2
        with col2:
            st.header("🔄 Processing")
            with st.spinner("Processing receipt..."):
                processed_img = components['image_processor'].preprocess(tmp_path)
                extracted_text = components['ocr'].extract_text(processed_img)
                with st.expander("View extracted text"):
                    st.text(extracted_text)

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

    finally:
        # Cleanup temp file
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
