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

# Download required NLTK data (commented out as assumed already done)
# nltk.download('punkt', force=True)
# nltk.download('averaged_perceptron_tagger', force=True)
# nltk.download('maxent_ne_chunker', force=True)
# nltk.download('words', force=True)
# nltk.download('punkt_tab', force=True)
# nltk.download('averaged_perceptron_tagger_eng', force=True)
# nltk.download('maxent_ne_chunker_tab', force=True)

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
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

def extract_name(resume_text):
    lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
    for line in lines[:5]:  # look at first few lines
        doc = nlp(line)
        name_tokens = []
        for token in doc:
            if token.pos_ == 'PROPN' and token.is_alpha and token.text.istitle():
                name_tokens.append(token.text)
            elif name_tokens:
                break  # stop if non-name word is hit
        if 1 < len(name_tokens) <= 3:
            return " ".join(name_tokens)
    # Fallback
    for line in lines[:3]:
        if (
            line.isupper() and
            2 <= len(line.split()) <= 4 and
            all(word.isalpha() for word in line.split())
        ):
            return line.title()
    return None

# CONTACT INFO EXTRACTION
PHONE_REG = re.compile(r'[\+\(]?[0-9][0-9 .\-\(\)]{8,}[0-9]|\([0-9][0-9 .\-\(\)]{7,}[0-9]')
EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+', re.IGNORECASE)
GITHUB_REG = re.compile(r'https?:\/\/(www\.)?github\.com\/[a-zA-Z0-9\-_.]+')
LINKEDIN_REG = re.compile(r'(https?:\/\/)?(www\.)?linkedin\.com\/(?:in|pub|company)\/[a-zA-Z0-9\-_/]+')

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
    emails = re.findall(EMAIL_REG, text)
    return emails[0] if emails else None

def extract_github(text):
    github = re.search(GITHUB_REG, text)
    return github.group(0).strip() if github else None

def extract_linkedin(text):
    linkedin = re.search(LINKEDIN_REG, text)
    return linkedin.group(0).strip() if linkedin else None

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
    education = extract_education(text)
    
    resume_data = {
        "name": name,
        "phone": phone,
        "email": email,
        "github": github,
        "linkedin": linkedin,
        "education": education if education is not None else "Failed to extract education details"
    }
    return resume_data

# Example usage (uncomment to test)
# if __name__ == "__main__":
#     file_path = input("Enter the path to the resume file (.pdf or .docx): ")
#     result = parse_resume(file_path)
#     print(json.dumps(result, indent=2))