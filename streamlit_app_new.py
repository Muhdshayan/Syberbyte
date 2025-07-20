import streamlit as st
import os
import resume_parser_2_  # Import your extraction logic
import pathlib

st.title("Resume Parser")
st.write("Upload a PDF or DOCX resume to extract key information.")

uploaded_file = st.file_uploader("Choose a resume file", type=["pdf", "docx"])

if uploaded_file is not None:
    suffix = pathlib.Path(uploaded_file.name).suffix
    temp_path = f"temp_uploaded_resume{suffix}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())
    with st.spinner("Extracting information..."):
        text = resume_parser_2_.extract_text_auto(temp_path)
        name = resume_parser_2_.extract_name(text)
        phone = resume_parser_2_.extract_phone_number(text)
#        email = resume_parser_2_.extract_email(text)
        email = resume_parser_2_.extract_email(text, temp_path)

        github = resume_parser_2_.extract_github(text)
        linkedin = resume_parser_2_.extract_linkedin(text, temp_path)

#        linkedin = resume_parser_2_.extract_linkedin(text)

    os.remove(temp_path)
    st.success("Extraction complete!")
    st.header("Extracted Information")
    st.write(f"**Name:** {name if name else 'Not found'}")
    st.write(f"**Phone:** {phone if phone else 'Not found'}")
    st.write(f"**Email:** {email if email else 'Not found'}")
    st.write(f"**GitHub:** {github if github else 'Not found'}")
    st.write(f"**LinkedIn:** {linkedin if linkedin else 'Not found'}")

