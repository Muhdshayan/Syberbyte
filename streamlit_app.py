import streamlit as st
import os
import resume_parser_LLM_integeration  # Import your extraction logic
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
        text = resume_parser_LLM_integeration.extract_text_auto(temp_path)
        name = resume_parser_LLM_integeration.extract_name(text)
        phone = resume_parser_LLM_integeration.extract_phone_number(text)
        email = resume_parser_LLM_integeration.extract_email(text)
        github = resume_parser_LLM_integeration.extract_github(text)
        linkedin = resume_parser_LLM_integeration.extract_linkedin(text)
        education = resume_parser_LLM_integeration.extract_education(text)
        # work_experience = resume_parser_LLM_integeration.extract_work_experience(text)
        skills = resume_parser_LLM_integeration.extract_skills(text)
        years_of_experience = resume_parser_LLM_integeration.extract_years_of_experience(text)
    os.remove(temp_path)
    st.success("Extraction complete!")
    st.header("Extracted Information")
    st.write(f"**Name:** {name if name else 'Not found'}")
    st.write(f"**Phone:** {phone if phone else 'Not found'}")
    st.write(f"**Email:** {email if email else 'Not found'}")
    st.write(f"**GitHub:** {github if github else 'Not found'}")
    st.write(f"**LinkedIn:** {linkedin if linkedin else 'Not found'}")

    # Display education in Streamlit
    st.write("**Education:**")
    if education and isinstance(education, dict):
        st.write(f"Institute: {education.get('institute', 'N/A')}")
        st.write(f"Degree: {education.get('degree', 'N/A')}")
        st.write(f"Year: {education.get('year', 'N/A')}")
    elif education:
        st.write(education)
    else:
        st.write("Not found")
    
    # Display years of experience in Streamlit
    st.write(f"**Total Years of Experience:** {years_of_experience if years_of_experience is not None else 'Not found'}")

    # # Display skills in Streamlit
    st.write("**Skills:**")
    if skills:
        if skills.get('technical_skills'):
            st.write("*Technical Skills:*")
            for skill, score in skills['technical_skills'].items():
                st.write(f"- {skill}: {score}")
        else:
            st.write("No technical skills found.")
        if skills.get('soft_skills'):
            st.write("*Soft Skills:*")
            for skill, score in skills['soft_skills'].items():
                st.write(f"- {skill}: {score}")
        else:
            st.write("No soft skills found.")
    else:
        st.write("No skills found.")

    # # Also print skills to terminal
    # print("\nExtracted Skills:")
    # if skills:
    #     if skills.get('technical_skills'):
    #         print("Technical Skills:")
    #         for skill, score in skills['technical_skills'].items():
    #             print(f"  - {skill}: {score}")
    #     else:
    #         print("No technical skills found.")
    #     if skills.get('soft_skills'):
    #         print("Soft Skills:")
    #         for skill, score in skills['soft_skills'].items():
    #             print(f"  - {skill}: {score}")
    #     else:
    #         print("No soft skills found.")
    # else:
    #     print("No skills found.")
    

    
    # st.write("**Total Work Experience (months):**")
    # if work_experience and isinstance(work_experience, int):
    #     st.write(f"{work_experience} months")
    # elif work_experience:
    #     st.write(work_experience)
    # else:
    #     st.write("Not found")

