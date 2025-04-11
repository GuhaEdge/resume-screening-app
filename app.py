# This version supports multiple resume uploads (PDF & Word) for batch screening.
# Required: pip install streamlit PyPDF2 python-docx fuzzywuzzy python-Levenshtein

import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from fuzzywuzzy import fuzz
import re
import io

st.set_page_config(page_title="Batch Resume Screening Tool", layout="wide")
st.title("📂 Bulk Resume Screening Tool")

st.markdown("""
Upload **multiple resumes (PDF or Word)** and paste the **job description** below. 
Get a **match score** for each resume and see keyword overlaps.
""")

# --- Upload Resumes ---
resume_files = st.file_uploader("📄 Upload Resumes (PDF or DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

# --- Input Job Description ---
st.subheader("📋 Job Description")
jd_input = st.text_area("Paste the job description here:", height=200)

# --- Extract text from DOCX ---
def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# --- Extract text from PDF ---
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# --- Keyword Extractor ---
def extract_keywords(text):
    words = re.findall(r'\b\w{4,}\b', text.lower())
    return list(set(words))

# --- Match Score Calculator ---
def calculate_match_score(resume_text, jd_text):
    return fuzz.token_set_ratio(resume_text, jd_text)

# --- Analyze Resumes ---
if st.button("🚀 Analyze All Resumes"):
    if resume_files and jd_input:
        jd_keywords = extract_keywords(jd_input)
        results = []

        for uploaded_file in resume_files:
            file_type = uploaded_file.name.split('.')[-1].lower()

            try:
                if file_type == 'pdf':
                    resume_text = extract_text_from_pdf(uploaded_file)
                elif file_type == 'docx':
                    resume_text = extract_text_from_docx(uploaded_file)
                else:
                    st.warning(f"Unsupported file type: {uploaded_file.name}")
                    continue

                score = calculate_match_score(resume_text, jd_input)
                resume_keywords = extract_keywords(resume_text)
                common_keywords = sorted(set(resume_keywords) & set(jd_keywords))

                results.append({
                    'filename': uploaded_file.name,
                    'score': score,
                    'keywords': ", ".join(common_keywords) if common_keywords else "None"
                })

            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {e}")

        # --- Display Results ---
        st.subheader("📊 Match Scores")
        for res in results:
            st.markdown(f"**{res['filename']}** — ✅ Score: `{res['score']}%`")
            st.caption(f"Matching Keywords: {res['keywords']}")
    else:
        st.warning("Please upload at least one resume and enter the job description.")
