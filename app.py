# This script requires Streamlit and other dependencies to be installed.
# If you are running this in a restricted environment, please install required packages:
# pip install streamlit PyPDF2 fuzzywuzzy python-Levenshtein

try:
    import streamlit as st
    from PyPDF2 import PdfReader
    from io import StringIO
    from fuzzywuzzy import fuzz
    import re

    st.set_page_config(page_title="Resume Screening Tool", layout="centered")
    st.title("🧠 AI Resume Screening Tool")

    st.markdown("""
    Upload a candidate's **resume (PDF)** and paste the **job description** below. Get an instant **match score** and keyword analysis.
    """)

    # --- Upload Resume ---
    resume_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])

    # --- Input Job Description ---
    st.subheader("📋 Job Description")
    jd_input = st.text_area("Paste the job description here:", height=200)

    # --- Extract Text from PDF Resume ---
    def extract_text_from_pdf(pdf_file):
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    # --- Keyword Extractor (Basic) ---
    def extract_keywords(text):
        # Extract words longer than 3 characters, remove duplicates
        words = re.findall(r'\b\w{4,}\b', text.lower())
        return list(set(words))

    # --- Match Score Calculator ---
    def calculate_match_score(resume_text, jd_text):
        return fuzz.token_set_ratio(resume_text, jd_text)

    # --- On Submit ---
    if st.button("🔍 Analyze Resume"):
        if resume_file and jd_input:
            resume_text = extract_text_from_pdf(resume_file)

            # Calculate Score
            score = calculate_match_score(resume_text, jd_input)
            st.success(f"✅ Match Score: {score}%")

            # Keyword Comparison
            resume_keywords = extract_keywords(resume_text)
            jd_keywords = extract_keywords(jd_input)
            common_keywords = list(set(resume_keywords) & set(jd_keywords))

            st.subheader("🔑 Matching Keywords")
            if common_keywords:
                st.write(", ".join(sorted(common_keywords)))
            else:
                st.warning("No significant keyword overlap found.")
        else:
            st.error("Please upload a resume and enter a job description.")

except ModuleNotFoundError as e:
    print("\n[ERROR] Required module is not installed:", e)
    print("\nPlease install all dependencies using:")
    print("pip install streamlit PyPDF2 fuzzywuzzy python-Levenshtein")
