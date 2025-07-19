import os
import re
import docx2txt
from pdfminer.high_level import extract_text
import nltk
import spacy
from spacy.matcher import Matcher
from nltk.corpus import stopwords
import streamlit as st
import pathlib
import requests
import json
from sentence_transformers import SentenceTransformer
from datetime import datetime
import ast

# LM Studio API endpoint
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

# Extract text from PDF or DOCX
def extract_text_auto(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        try:
            text = extract_text(file_path)
            print("[DEBUG] Extracted PDF text:\n", text)
            return text
        except Exception as e:
            return f"Error extracting from PDF: {e}"
    elif ext == '.docx':
        try:
            text = docx2txt.process(file_path)
            text = text.replace('\t', ' ') if text else "No text found."
            print("[DEBUG] Extracted DOCX text:\n", text)
            return text
        except Exception as e:
            return f"Error extracting from DOCX: %s" % e
    else:
        return "Unsupported file format. Please upload a .pdf or .docx file."

# NAME EXTRACTION (spaCy)
# # ============================ NAME EXTRACTION (spaCy) ============================
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

# Common false positives to exclude
BLACKLIST = {
    "developer", "engineer", "intern", "project", "summary", "skills", "experience",
    "education", "system", "app", "application", "curriculum", "vitae", "resume", "cv",
    "contact", "objective", "qualification"
}

def extract_name(resume_text):
    try:
        lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
        lines = [line for line in lines if not re.match(r'^(\W|\d)+$', line)]

        # --- 0. Check for markdown-style headings (like # NAME) ---
        for line in lines[:10]:
            if line.startswith('#') and not line.startswith('##'):
                name_candidate = line.lstrip('#').strip()
                if (
                    2 <= len(name_candidate.split()) <= 3 and
                    all(word.isalpha() for word in name_candidate.split()) and
                    not any(word.lower() in BLACKLIST for word in name_candidate.split())
                ):
                    return name_candidate.title()

        # --- 0b. Main heading in ALL CAPS (e.g. SIDRA BUKHARI) ---
        for line in lines[:5]:
            if (
                line.isupper() and
                2 <= len(line.split()) <= 3 and
                all(word.isalpha() for word in line.split()) and
                not any(word.lower() in BLACKLIST for word in line.split())
            ):
                return line.title()

        # --- 1. Strong title-case heuristic (top 10 lines) ---
        for line in lines[:10]:
            if (
                2 <= len(line.split()) <= 3 and
                line == line.title() and
                all(word.isalpha() for word in line.split()) and
                not any(word.lower() in BLACKLIST for word in line.split())
            ):
                return line

        # --- 2. Uppercase name (again, fallback) ---
        for line in lines[:10]:
            if (
                line.isupper() and
                2 <= len(line.split()) <= 3 and
                all(word.isalpha() for word in line.split()) and
                not any(word.lower() in BLACKLIST for word in line.split())
            ):
                return line.title()

        # --- 3. spaCy NER: PERSON entities from top 10 lines ---
        try:
            doc = nlp(" ".join(lines[:10]))
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    name = ent.text.strip()
                    parts = name.split()
                    if (
                        2 <= len(parts) <= 3 and
                        all(p.isalpha() and p[0].isupper() for p in parts) and
                        not any(p.lower() in BLACKLIST for p in parts)
                    ):
                        return name
        except:
            pass

        # --- 4. POS tagging for Proper Nouns ---
        for line in lines[:5]:
            doc_line = nlp(line)
            name_tokens = []
            for token in doc_line:
                if token.pos_ == 'PROPN' and token.is_alpha and token.text.istitle():
                    name_tokens.append(token.text)
                elif name_tokens:
                    break  # stop on first non-proper noun
            if (
                2 <= len(name_tokens) <= 3 and
                not any(t.lower() in BLACKLIST for t in name_tokens)
            ):
                return " ".join(name_tokens)

        # --- 5. From email prefix ---
        email = extract_email(resume_text)
        if email:
            local_part = email.split('@')[0]
            possible_name = re.sub(r'[._\-]', ' ', local_part).title()
            words = possible_name.split()
            if (
                2 <= len(words) <= 3 and
                all(w.isalpha() for w in words) and
                not any(word.lower() in BLACKLIST for word in words)
            ):
                return " ".join(words)

        # --- 6. From LinkedIn URL ---
        linkedin_match = re.search(r'linkedin\.com/(?:in|pub)/([a-zA-Z\-]+)-?([a-zA-Z\-]+)', resume_text.lower())
        if linkedin_match:
            first = linkedin_match.group(1).replace('-', ' ').title()
            last = linkedin_match.group(2).replace('-', ' ').title()
            full = f"{first} {last}"
            if (
                2 <= len(full.split()) <= 3 and
                all(w.isalpha() for w in full.split()) and
                not any(word.lower() in BLACKLIST for word in full.split())
            ):
                return full

    except Exception as e:
        print("[ERROR] extract_name() failed:", e)

    return "Name Not Found"

# CONTACT INFO EXTRACTION
PHONE_REG = re.compile(r'[\+\(]?[0-9][0-9 .\-\(\)]{8,}[0-9]|\([0-9][0-9 .\-\(\)]{7,}[0-9]')
EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+', re.IGNORECASE)
GITHUB_PROFILE_REG = re.compile(
    r'https?:\/\/(?:www\.)?github\.com\/([a-zA-Z0-9\-]+)(?!\/[a-zA-Z0-9])',
    re.IGNORECASE
)
LINKEDIN_REG = re.compile(
    r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|pub|company)\/[a-zA-Z0-9\-\/]+(?=\s|$)',
    re.IGNORECASE
)

def extract_phone_number(text):
    phones = re.findall(PHONE_REG, text)
    if phones:
        raw = phones[0]
        if raw.strip().startswith('+'):
            number = '+' + re.sub(r'\D', '', raw)
        else:
            number = re.sub(r'\D', '', raw)
        if 8 < len(number.replace('+', '')) < 16:
            return number
    return None

def extract_email(text):
    try:
        emails = re.findall(EMAIL_REG, text)
        return emails[0] if emails else None
    except Exception as e:
        print("[DEBUG] Email regex failed:", e)
        return None


def fix_broken_github_urls(text):
    # Fix hyphenated line breaks
    text = re.sub(r'(\S)-\n(\S)', r'\1\2', text)

    # Add newline after GitHub/LinkedIn links to prevent merge with following words
    text = re.sub(r'(https?:\/\/[^\s]+)', r'\1\n', text)

    # Remove any leftover newlines and spaces before URLs
    text = re.sub(r'\s+(?=https?:\/\/)', '', text)
    return text

def extract_github(text):
    text = fix_broken_github_urls(text)
    match = re.search(GITHUB_PROFILE_REG, text)
    if match:
        username = match.group(1)
        return f"https://github.com/{username}"
    return None


def fix_broken_linkedin_urls(text):
    # Fix hyphenated line breaks specifically in LinkedIn usernames (e.g., muhammad-talha-\nnadeem)
    text = re.sub(
        r'(linkedin\.com\/(?:in|pub|company)\/[a-zA-Z0-9\-]+)-\s*\n\s*([a-zA-Z0-9\-]+)',
        r'\1\2',
        text,
        flags=re.IGNORECASE
    )

    # Fix generic line breaks within LinkedIn URLs (e.g., www\n.\nlinkedin\n.com/in/...)
    text = re.sub(r'www[\n\s]*\.?[\n\s]*linkedin', 'www.linkedin', text, flags=re.IGNORECASE)
    text = re.sub(r'(linkedin\.com)[\n\s]*\/[\n\s]*', r'\1/', text, flags=re.IGNORECASE)
    text = re.sub(r'(linkedin\.com\/[a-zA-Z0-9\-]+)[\n\s]*\/[\n\s]*', r'\1/', text)

    return text

def extract_linkedin(text):
    text = fix_broken_linkedin_urls(text)

    LINKEDIN_REG = re.compile(
        r'(https?:\/\/)?(www\.)?linkedin\.com\/(in|pub|company)\/[a-zA-Z0-9\-]+(?:-[a-zA-Z0-9]+)*',
        re.IGNORECASE
    )

    matches = re.finditer(LINKEDIN_REG, text)
    for match in matches:
        url = match.group(0).strip().rstrip('.,);:')
        if not url.startswith("http"):
            url = "https://" + url
        return url

    return None



# EDUCATION EXTRACTION USING LLM
def extract_education(resume_text):
    url = LM_STUDIO_URL
    user_message = {
        "role": "user",
        "content": (
            "You are a helpful assistant that extracts education details from resumes. "
            "Extract only the latest (most recent) education entry from the resume. "
            "Return a single JSON object with keys 'institute', 'degree', and 'year'. "
            "Provide only the JSON output without any additional text.\n\n"
            f"Here is the resume text: {resume_text}"
        )
    }
    payload = {
        "model": "mistral",
        "messages": [user_message],
        "temperature": 0.3,
        "max_tokens": 512,
        "stream": False
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        education_entry = json.loads(content)
        return education_entry
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        print(f"Model response: {content}")
        return None
    except KeyError as e:
        print(f"Unexpected response format: {e}")
        return None



# WORK EXPERIENCE EXTRACTION USING LLM
# def extract_work_experience(resume_text):
#     # Replace "Present" with current date for accurate calculations
#     current_date = datetime.now().strftime("%B %Y")
#     processed_text = re.sub(r'\bPresent\b', current_date, resume_text, flags=re.IGNORECASE)
    
#     url = LM_STUDIO_URL
#     user_message = {
#         "role": "user",
#         "content": (
#             "STRICT INSTRUCTION: Find all job date ranges in the resume, even if multiple ranges are in one place. "
#             "For each range, calculate the number of months worked (e.g., Jun 2024 - Aug 2024 = 2, Sept 2024 - Dec 2024 = 3). "
#             "Sum all months and return ONLY the total as a JSON integer (e.g., 5). "
#             "If a date range is written as '1 Jan 2024 - 1 Jan 2025', consider it as 12 months (not 13). "
#             "Do NOT include any explanation, breakdown, or text—just the integer in JSON. "
#             "If no experience, return 0. "
#             "If you do not follow these instructions and output anything except a JSON integer, your answer will be considered wrong.\n\n"
#             f"Resume text: {processed_text}"
#         )
#     }
#     payload = {
#         "model": "mistral",
#         "messages": [user_message],
#         "temperature": 0.0,
#         "max_tokens": 10,
#         "stream": False
#     }
#     headers = {
#         "Content-Type": "application/json"
#     }
#     try:
#         response = requests.post(url, headers=headers, data=json.dumps(payload))
#         response.raise_for_status()
#         result = response.json()
#         content = result["choices"][0]["message"]["content"].strip()
        
#         # Try to extract just the number if LLM gives verbose response or JSON object
#         try:
#             parsed = json.loads(content)
#             if isinstance(parsed, int):
#                 return parsed
#             elif isinstance(parsed, dict) and 'total_months' in parsed:
#                 return parsed['total_months']
#         except json.JSONDecodeError:
#             # If JSON parsing fails, try to extract just the number
#             number_match = re.search(r'\b(\d+)\b', content)
#             if number_match:
#                 return int(number_match.group(1))
#             else:
#                 print(f"Could not extract number from response: {content}")
#                 return None
                
#     except requests.exceptions.RequestException as e:
#         print(f"API request failed: {e}")
#         return None
#     except KeyError as e:
#         print(f"Unexpected response format: {e}")
#         return None

# DETERMINE EXPERTISE LEVEL
# def determine_expertise_level(total_months):
#     if not total_months or total_months == 0:
#         return "Beginner"
#     if total_months < 24:
#         return "Beginner"
#     elif 24 <= total_months <= 60:
#         return "Intermediate"
#     else:
#         return "Expert"

# SKILLS EXTRACTION
def extract_json_from_response(content):
    """
    Extract the first JSON object (even with single quotes) from the LLM response,
    stripping any markdown/code blocks or extra explanation.
    """
    match = re.search(r'({[\s\S]*})', content)
    if match:
        return match.group(1)
    return content  # fallback: return as is

def extract_skills(resume_text):
    url = LM_STUDIO_URL
    user_message = {
        "role": "user",
        "content": (
            "You are a helpful assistant that extracts skills from resumes. Extract all technical and soft skills from the provided resume text. For each skill, assign a confidence score (0-100) based on supporting evidence such as certifications, projects, work experience, achievements, and education level (consider education level as a minor factor).\n"
            "STRICT SCORING INSTRUCTIONS: If there is strong evidence of extensive work in a skill (such as multiple projects, long work experience, or major achievements), assign a score of 80 or above. If there is moderate evidence (such as a single project, some work experience, or a mention in achievements/education), assign a score around 60-70. If a skill is only listed in a skills section or mentioned without any supporting evidence, assign a score less than 50.\n"
            "STRICT SKILL FORMAT INSTRUCTION: Each skill must be a concise keyword or phrase (e.g., 'Python', 'Project Management', 'Teamwork'). Do NOT use sentences, descriptions, or multi-line text as a skill. Reject any skill that is a sentence, description, or spans multiple lines. Only include skills that are single keywords or short phrases.\n"
            "Categorize the skills into 'technical_skills' and 'soft_skills'. Include only skills with a confidence score of 20 or above.\n"
            "STRICT INSTRUCTION: Return ONLY the JSON object, with no markdown, no explanations, no code blocks, and no extra text before or after. If you do not follow this, your answer will be considered wrong.\n"
            "Return only a JSON object with the structure:\n"
            "{\n"
            "  'technical_skills': {\n"
            "    'SkillName': score,\n"
            "    ...\n"
            "  },\n"
            "  'soft_skills': {\n"
            "    'SkillName': score,\n"
            "    ...\n"
            "  }\n"
            "}\n"
            "If no skills are found in a category, leave the dictionary empty. Do not include any additional text.\n\n"
            f"Here is the resume text: {resume_text}"
        )
    }
    payload = {
        "model": "mistral",
        "messages": [user_message],
        "temperature": 0.3,
        "max_tokens": 1024,
        "stream": False
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        content = extract_json_from_response(content)
        try:
            skills_data = json.loads(content)
        except json.JSONDecodeError:
            try:
                # Replace single quotes with double quotes
                skills_data = json.loads(content.replace("'", '"'))
            except json.JSONDecodeError:
                try:
                    # As a last resort, use ast.literal_eval
                    skills_data = ast.literal_eval(content)
                except Exception as e:
                    print(f"Failed to parse skills data: {e}")
                    print(f"Model response: {content}")
                    return None
        return skills_data
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except KeyError as e:
        print(f"Unexpected response format: {e}")
        return None

# NEW FUNCTION: Extract Years of Experience Using Mistral 7B LLM
def extract_years_of_experience(resume_text):
    # Preprocess the text to replace "Present" with current date
    current_date = datetime.now().strftime("%B %Y")  # e.g., "July 2025"
    processed_text = re.sub(r'\bPresent\b', current_date, resume_text, flags=re.IGNORECASE)
    
    # Define the prompt for the LLM
    prompt = f"""
    STRICT INSTRUCTION: Extract the total years of work experience from the resume text provided. Identify all periods of work experience, which may be listed with date ranges (e.g., '01/2021 - 01/2022', 'Jan 2021 - Jan 2022'), durations (e.g., '1 year', '6 months'), or other formats. Convert all durations to years, where 12 months = 1 year, 6 months = 0.5 years, etc. Sum up all the years from all jobs. If a job's duration is ambiguous (e.g., 'several years'), do not include it in the total (treat as 0). If no work experience is mentioned, return 0.0.

    STRICTEST INSTRUCTION: Return ONLY the total years as a float (e.g., 2.5, 0.0), with NO extra text, NO explanation, NO formatting, NO units, and NO markdown. If you do not follow this, your answer will be considered wrong.

    Before processing, replace any instance of 'Present' with the current date (e.g., '{current_date}').

    Here is the resume text:
    {processed_text}
    """
    
    # Send request to Mistral 7B
    user_message = {
        "role": "user",
        "content": prompt
    }
    payload = {
        "model": "mistral",
        "messages": [user_message],
        "temperature": 0.0,
        "max_tokens": 200,
        "stream": False
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(LM_STUDIO_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"].strip()
        # Always extract the float number from the response, even if extra text is present
        match = re.search(r'\d+(\.\d+)?', content)
        if match:
            return float(match.group(0))
        else:
            return 0.0
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return 0.0
    except KeyError as e:
        print(f"Unexpected response format: {e}")
        return 0.0
    except ValueError as e:
        print(f"Failed to convert to float: {e}")
        return 0.0
    
# MAIN RESUME PARSING FUNCTION
def parse_resume(file_path):
    text = extract_text_auto(file_path)
    if "Error" in text:
        return {"error": text}
    
    name = extract_name(text)
    phone = extract_phone_number(text)
    email = extract_email(text)
    github = extract_github(text)
    linkedin = extract_linkedin(text)
    skills = extract_skills(text)
    if skills is None:
        skills = {}



    education = extract_education(text)
    # work_experience = extract_work_experience(text)
    
    # if work_experience and isinstance(work_experience, int): # Check if it's an integer
    #     total_exp = work_experience
    #     expertise_level = determine_expertise_level(total_exp)
    # else:
    #     total_exp = None
    #     expertise_level = "Unknown"
    
    resume_data = {
        "name": name,
        "phone": phone,
        "email": email,
        "github": github,
        "linkedin": linkedin,
        # "skills": skills,
        # "education": education if education is not None else "Failed to extract education details",
        # "work_experience": total_exp,
        # "expertise_level": expertise_level
    }
    return resume_data

# Example usage (uncomment to test)
# if __name__ == "__main__":
#     file_path = input("Enter the path to the resume file (.pdf or .docx): ")
#     result = parse_resume(file_path)
#     print(json.dumps(result, indent=2))