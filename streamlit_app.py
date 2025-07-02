import streamlit as st
import tempfile
import os

# Import your parser functions
from resume_parser_without_subcategories import (
    read_pdf, read_docx, build_profile
)

st.set_page_config(page_title="Resume Parser", layout="wide")
st.title("Resume Parser (No Subcategories)")

st.write("Upload a PDF or DOCX resume. The app will extract and display all fields.")

uploaded_file = st.file_uploader("Choose a resume file", type=["pdf", "docx"])

if uploaded_file is not None:
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix="." + uploaded_file.name.split('.')[-1]) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # Extract text
    if uploaded_file.name.endswith(".pdf"):
        resume_text = read_pdf(tmp_path)
    elif uploaded_file.name.endswith(".docx"):
        resume_text = read_docx(tmp_path)
    else:
        st.error("Unsupported file type.")
        os.remove(tmp_path)
        st.stop()

    # Parse resume
    profile = build_profile(resume_text)

    # Display results
    st.header("Extracted Information")
    st.subheader("Name")
    st.write(profile.get("name", ""))

    st.subheader("Contact")
    st.json(profile.get("contact", {}))

    st.subheader("Summary")
    st.write(profile.get("summary", ""))

    st.subheader("Technical Skills")
    st.write(", ".join(profile.get("skills", {}).get("technical", [])))

    st.subheader("Soft Skills")
    st.write(", ".join(profile.get("skills", {}).get("soft", [])))

    st.subheader("Education")
    st.write(profile.get("education", []))

    st.subheader("Experience")
    st.write(profile.get("experience", []))

    st.subheader("Projects")
    projects = profile.get("projects", [])
    if projects and isinstance(projects[0], dict):
        for i, proj in enumerate(projects, 1):
            st.markdown(f"**Project {i}:** {proj.get('content', '')}")
    else:
        st.write(projects)

    st.subheader("Certifications")
    st.write(profile.get("certifications", []))

    # Clean up temp file
    os.remove(tmp_path)