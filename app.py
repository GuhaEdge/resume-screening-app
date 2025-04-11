# This version supports multiple resume uploads (PDF & Word) for batch screening with dashboard.
# Required: pip install streamlit PyPDF2 python-docx fuzzywuzzy python-Levenshtein

import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from fuzzywuzzy import fuzz
import re
import io

st.set_page_config(page_title="Resume Screening Dashboard", layout="wide")
st.title("📊 Resume Screening Dashboard")

st.markdown("""
Upload **multiple resumes (PDF or Word)** and paste the **job description** below.

The dashboard will extract:
- ✅ **Job Title**
- 🔑 **Important Keywords**
- 🔍 **Boolean String**
- 📍 **Location Match**
- 🧠 **Resume Match Score**
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

# --- Extract Job Title ---
def extract_job_title(jd_text):
    lines = jd_text.strip().split('\n')
    for line in lines:
        if "title" in line.lower() or "position" in line.lower():
            return line.strip()
    return "Unknown"

# --- Extract Boolean Search String ---
def generate_boolean_string(keywords):
    return " OR ".join([f'\"{kw}\"' for kw in keywords[:10]])  # limit for readability

# --- Match Score Calculator ---
def calculate_match_score(resume_text, jd_text):
    return fuzz.token_set_ratio(resume_text, jd_text)

# --- Location Matcher ---
def location_match(resume_text, jd_text):
    locations = ["remote", "hyderabad", "bangalore", "mumbai", "chennai", "pune", "delhi"]
    resume_locs = [loc for loc in locations if loc in resume_text.lower()]
    jd_locs = [loc for loc in locations if loc in jd_text.lower()]
    common = set(resume_locs) & set(jd_locs)
    return ", ".join(common) if common else "No Match"

# --- Analyze Resumes ---
if st.button("🚀 Analyze All Resumes"):
    if resume_files and jd_input:
        jd_keywords = extract_keywords(jd_input)
        job_title = extract_job_title(jd_input)
        boolean_str = generate_boolean_string(jd_keywords)

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
                loc_match = location_match(resume_text, jd_input)

                results.append({
                    'filename': uploaded_file.name,
                    'score': score,
                    'keywords': ", ".join(common_keywords) if common_keywords else "None",
                    'location': loc_match
                })

            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {e}")

        # --- Dashboard Output ---
        st.subheader("📊 Screening Dashboard")

        st.markdown(f"**🧾 Job Title:** `{job_title}`")
        st.markdown(f"**🧠 Boolean String:** `{boolean_str}`")

        for res in results:
            st.markdown(f"### {res['filename']}")
            st.markdown(f"✅ Match Score: `{res['score']}%`")
            st.markdown(f"📍 Location Match: `{res['location']}`")
            st.markdown(f"🔑 Matching Keywords: {res['keywords']}")
            st.markdown("---")

    else:
        st.warning("Please upload at least one resume and enter the job description.")
