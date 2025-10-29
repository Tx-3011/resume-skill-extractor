import streamlit as st
import pandas as pd
import pdfplumber
import spacy
import re
import matplotlib.pyplot as plt
from spacy.matcher import PhraseMatcher
from collections import Counter


st.set_page_config(page_title="Smart Resume Skill Extractor", page_icon="💼", layout="wide")
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f7ff;
    }
    .stButton>button {
        background-color: #0072ff;
        color: white;
        border-radius: 10px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

nlp = spacy.load("en_core_web_sm")


def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_skills(text, skills_list):
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(skill) for skill in skills_list]
    matcher.add("SKILLS", patterns)
    doc = nlp(text)
    matches = matcher(doc)
    return list(set([doc[start:end].text for _, start, end in matches]))


def extract_education(text):
    edu_keywords = [
        "bachelor", "master", "phd", "diploma", "b.tech", "bachelor of technology",
        "m.tech", "b.e", "bsc", "msc", "mba", "high school", "university", "college"
    ]
    found = []
    for word in edu_keywords:
        if re.search(word, text, re.IGNORECASE):
            found.append(word.title())
    return list(set(found))


def extract_certifications(text):
    cert_patterns = [
        r"(certified\s+\w+)", 
        r"(certificate\s+in\s+\w+)",
        r"(aws\s+certified\s+\w+)",
        r"(microsoft\s+certified\s+\w+)",
        r"(google\s+cloud\s+certified\s+\w+)"
    ]
    results = []
    for pattern in cert_patterns:
        results += re.findall(pattern, text, re.IGNORECASE)
    return [r.title() for r in set(results)]


def calculate_resume_score(extracted_skills, job_skills):
    resume_set = set(map(str.lower, extracted_skills))
    job_set = set(map(str.lower, job_skills))
    score = len(resume_set & job_set) / len(job_set) * 100 if job_set else 0
    return round(score, 2)


def highlight_skills_in_text(text, skills):
    """Highlight extracted skills in resume text"""
    for skill in sorted(skills, key=len, reverse=True):
        pattern = re.compile(re.escape(skill), re.IGNORECASE)
        text = pattern.sub(f"<span style='background-color:#ffeaa7'><b>{skill}</b></span>", text)
    return text



st.title("Smart Resume Skill Extractor & Analyzer")
st.markdown("### An NLP-based tool to extract, analyze and score resumes automatically ")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])
with col2:
    job_role = st.text_input("Enter Target Job Role (e.g., Data Scientist, Web Developer)")


role_skills = {
    "data scientist": ["python", "pandas", "numpy", "machine learning", "tensorflow", "deep learning", "sql"],
    "web developer": ["html", "css", "javascript", "react", "node.js", "flask", "django"],
    "devops engineer": ["docker", "kubernetes", "aws", "linux", "jenkins", "terraform"],
}

if uploaded_file:
    with st.spinner("Extracting text and analyzing..."):
        text = extract_text_from_pdf(uploaded_file)


        skills_df = pd.read_csv("data/skills_list.csv")
        skills_list = skills_df["skill"].tolist()
        extracted_skills = extract_skills(text, skills_list)

        education = extract_education(text)
        certifications = extract_certifications(text)


        job_skills = role_skills.get(job_role.lower(), [])
        score = calculate_resume_score(extracted_skills, job_skills)


    st.success("✅ Resume analysis complete!")
    tab1, tab2, tab3 = st.tabs(["Overview", "Education & Certifications", "Visual Insights"])

    with tab1:
        st.subheader("Extracted Technical Skills")
        st.write(", ".join(extracted_skills) if extracted_skills else "No skills detected.")

        st.metric("Resume Match Score", f"{score}%")
        if job_skills:
            st.write("**Target Role Skills:**", ", ".join(job_skills))
        else:
            st.info("No predefined skill list found for this role.")

    with tab2:
        st.subheader("Education Details")
        st.write(", ".join(education) if education else "No education details detected.")

        st.subheader("Certifications")
        st.write(", ".join(certifications) if certifications else "No certifications found.")

    with tab3:
        st.subheader("Skill Frequency Distribution")
        if extracted_skills:
            freq = Counter()
            for skill in extracted_skills:
                count = len(re.findall(rf'\b{re.escape(skill)}\b', text, re.IGNORECASE))
                freq[skill.lower()] = count

            plt.figure(figsize=(6,3))
            plt.bar(freq.keys(), freq.values(), color="#4CAF50")
            plt.xticks(rotation=45)
            plt.title("Detected Skill Frequency")
            plt.tight_layout()
            st.pyplot(plt)

        st.subheader("Skill Category Contribution")
        category_counts = {
            "Programming": len([s for s in extracted_skills if s.lower() in ["python", "java", "c++"]]),
            "Web": len([s for s in extracted_skills if s.lower() in ["html", "css", "javascript", "react", "node.js"]]),
            "Data Science": len([s for s in extracted_skills if s.lower() in ["pandas", "numpy", "tensorflow", "machine learning", "deep learning"]]),
            "DevOps": len([s for s in extracted_skills if s.lower() in ["docker", "aws", "kubernetes"]]),
        }
        labels = list(category_counts.keys())
        sizes = list(category_counts.values())

        if sum(sizes) > 0:
            
            filtered = {k: v for k, v in category_counts.items() if v > 0}

            if filtered:
                labels = list(filtered.keys())
                sizes = list(filtered.values())

                fig, ax = plt.subplots(figsize=(5, 5))
                wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.85,
        labeldistance=1.1,
        textprops={'fontsize': 10}
    )

    
                centre_circle = plt.Circle((0, 0), 0.60, fc='white')
                fig.gca().add_artist(centre_circle)

                ax.axis("equal")
                plt.tight_layout()
                st.pyplot(fig)
        else:
            st.info("No skills found for category visualization.")



    
    csv_data = pd.DataFrame({
        "Extracted Skills": [", ".join(extracted_skills)],
        "Education": [", ".join(education)],
        "Certifications": [", ".join(certifications)],
        "Score (%)": [score]
    }).to_csv(index=False)

    st.download_button(
        "⬇️ Download Extracted Data (CSV)",
        data=csv_data,
        file_name="resume_analysis.csv",
        mime="text/csv"
    )

else:
    st.info("👆 Upload a resume to begin analysis.")
