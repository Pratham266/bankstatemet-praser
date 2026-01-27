import streamlit as st
import main
import json
import pdfplumber
from pdfminer.pdfdocument import PDFPasswordIncorrect

# ./venv/bin/streamlit run app.py
# ./venv/bin/uvicorn api:app --reload
st.set_page_config(page_title="PDF Extraction Tool", layout="wide")

st.title("Bank Statement PDF Extractor")
st.markdown("Upload a PDF file to extract transactions using PDFPlumber (Text-based).")

# Sidebar for options
st.sidebar.header("Configuration")
bank_options = ["UNION BANK OF INDIA","KOTAK MAHINDRA BANK","Generic (Raw Text)", ]
selected_bank = st.sidebar.selectbox("Select Bank Format", bank_options)

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Check for password protection
    password = None
    is_encrypted = False
    try:
        uploaded_file.seek(0)
        with pdfplumber.open(uploaded_file) as pdf:
            # Accessing pages to trigger decryption check
            len(pdf.pages)
    except PDFPasswordIncorrect:
        is_encrypted = True
    except Exception as e:
        if "Password" in str(e) or "Encrypted" in str(e) or "PDFPasswordIncorrect" in repr(e):
            is_encrypted = True
    
    uploaded_file.seek(0)

    if is_encrypted:
        st.warning("This PDF is password protected.")
        password = st.text_input("Enter PDF Password", type="password")
        if not password:
            st.stop()

    if st.button("Extract Data"):
        
        with st.spinner(f"Processing PDF..."):
            try:
                if selected_bank == "Generic (Raw Text)":
                    # Raw text dump from plumber
                    full_text = []
                    # Pass password here
                    with pdfplumber.open(uploaded_file, password=password) as pdf:
                        for i, page in enumerate(pdf.pages):
                            text = page.extract_text(layout=True)
                            full_text.append(f"--- Page {i+1} ---\n{text}\n")
                    
                    final_text = "\n".join(full_text)
                    
                    st.success("Text Extraction Complete!")
                    st.subheader("Extracted Text (Layout Preserved)")
                    st.text_area("Result", final_text, height=400)
                    
                    st.download_button(
                        label="Download Result as Text",
                        data=final_text,
                        file_name="extracted_text_plumber.txt",
                        mime="text/plain"
                    )
                else:
                    # Structured Extraction via Plumber
                    # Pass password here
                    transactions = main.process_bank_statement_pdf(uploaded_file, bank_name=selected_bank, password=password)
                    st.success(f"Extraction Complete for {selected_bank}!")
                    
                    # Also show as table
                    if transactions:
                        st.subheader("Tabular View")
                        st.dataframe(transactions)

                    # Display as JSON
                    json_str = json.dumps(transactions, indent=2)
                    st.subheader("Extracted JSON Data")
                    st.code(json_str, language="json")
                    
                    st.download_button(
                        label="Download Result as JSON",
                        data=json_str,
                        file_name="extracted_data.json",
                        mime="application/json"
                    )
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
