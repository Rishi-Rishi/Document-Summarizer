import streamlit as st
from txtai.pipeline import Summary
from PyPDF2 import PdfReader
import os
import nltk
nltk.download('punkt')
from fpdf import FPDF
from googletrans import Translator

st.set_page_config(layout="wide")

@st.cache_resource
def text_summary(text, target_length=None):
    # Create summary instance
    summary = Summary("MBZUAI/LaMini-Flan-T5-248M")

    # Generate the summary
    result = summary(text, maxlength=500)

    # If target_length is specified, ensure summary covers at least half of the text
    if target_length and len(result) < target_length:
        return result

    return result

def save_to_pdf(summary_text, original_filename=None):
    # Extract the name and extension of the original file
    if original_filename:
        original_name, original_extension = os.path.splitext(original_filename)
    else:
        original_name = "summary"

    # Generate the new filename for the summarized text PDF
    new_filename = f"{original_name}_summary.pdf"
    
    pdf = FPDF()  # Create an instance of the FPDF class, which represents the PDF document
    pdf.add_page()  # Add a page to the PDF document
    pdf.set_font("Arial", size=12)  # Set the font for the text
    
    # Add the title for the summarized text
    pdf.cell(200, 10, txt="Summarized Text", ln=True, align="C")
    
    # Encode summary_text to UTF-8 before passing it to multi_cell
    encoded_summary_text = summary_text.encode('latin1', 'replace').decode('latin1')
    
    # Add the summarized text to the PDF, with automatic text wrapping
    pdf.multi_cell(0, 10, txt=encoded_summary_text)
    
    pdf.output(new_filename)  # Save the PDF document with the new filename
    return new_filename  # Return the new filename


def extract_text_from_pdf(file_path):
    # Open the PDF file using PyPDF2
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

choice = st.sidebar.selectbox("Select your choice", ["Summarize Text", "Summarize Document"])

if choice == "Summarize Text":
    st.subheader("Summarize Text")
    input_text = st.text_area("Enter your text here")
    if input_text is not None:
        if st.button("Summarize Text"):
            col1, col2 = st.columns([1,1])
            with col1:
                st.markdown("**Your Input Text**")
                st.info(input_text)
            with col2:
                st.markdown("**Summary Result**")
                # Adjust target_length to cover at least half of the input text
                target_length = len(input_text) // 2
                result = text_summary(input_text, target_length=target_length)
                st.success(result)
                 # Save summarized text to PDF and get the new filename
                new_pdf_filename = save_to_pdf(result)
                #download
                st.download_button(label="Download Summarized PDF", data=open(new_pdf_filename, "rb").read(), file_name=os.path.basename(new_pdf_filename), mime="application/pdf")
                # Translate the summary into different languages
                translator = Translator()
                languages = ['ml', 'te', 'hi', 'ta', 'kn', 'fr', 'es', 'de']
                for lang in languages:
                    translation = translator.translate(result, dest=lang)
                    translated_text = translation.text
                    st.write(f"Translated summary in {lang.upper()}:")
                    st.write(translated_text)
                    # Generate filename for translated PDF
                    translated_filename = f"{new_pdf_filename}_summary_{lang}.pdf"
                
                    # Save translated summary to PDF
                    translated_pdf = save_to_pdf(translated_text, translated_filename)
                    # Download all translated PDFs
                    st.download_button(label=f"Download {lang.upper()}", data=open(translated_pdf, "rb").read(), file_name=os.path.basename(translated_pdf), mime="application/pdf")

elif choice == "Summarize Document":
    st.subheader("Summarize Document")
    input_file = st.file_uploader("Upload your document here", type=['pdf'])
    if input_file is not None:
        if st.button("Summarize Document"):
            with open("doc_file.pdf", "wb") as f:
                f.write(input_file.getbuffer())
            col1, col2 = st.columns([1,1])
            with col1:
                st.info("File uploaded successfully")
                extracted_text = extract_text_from_pdf("doc_file.pdf")
                st.markdown("**Extracted Text is Below:**")
                st.info(extracted_text)
            with col2:
                st.markdown("**Summary Result**")
                # Adjust target_length to cover at least half of the extracted text
                target_length = len(extracted_text) // 2
                doc_summary = text_summary(extracted_text, target_length=target_length)
                st.success(doc_summary)
                # Save summarized text to PDF and get the new filename
                new_pdf_filename = save_to_pdf(doc_summary, input_file.name)
                #download
                st.download_button(label="Download Summarized PDF", data=open(new_pdf_filename, "rb").read(), file_name=os.path.basename(new_pdf_filename), mime="application/pdf")
                # Translate the summary into different languages
                translator = Translator()
                languages = ['ml', 'te', 'hi', 'ta', 'kn', 'fr', 'es', 'de']
                translated_files=[]
                for lang in languages:
                    translation = translator.translate(doc_summary, dest=lang)
                    translated_text = translation.text
                    st.write(f"Translated summary in {lang.upper()}:")
                    st.write(translated_text)
                    # Generate filename for translated PDF
                    translated_filename = f"{input_file.name}_translated_{lang}.pdf"
                    # Save translated summary to PDF
                    translated_pdf = save_to_pdf(translated_text, translated_filename)
                    # Download all translated PDFs
                    st.download_button(label=f"{lang.upper()}", data=open(translated_pdf, "rb").read(), file_name=os.path.basename(translated_pdf), mime="application/pdf")
