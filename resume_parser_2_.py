# # ============================ SETUP ============================
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
# import openai

# # IMPORTANT: For LM Studio compatibility, use openai==0.28.1
# # pip install openai==0.28.1
# # Download required NLTK data
# nltk.download('punkt', force=True)
# nltk.download('averaged_perceptron_tagger', force=True)
# nltk.download('maxent_ne_chunker', force=True)
# nltk.download('words', force=True)
# nltk.download('punkt_tab', force=True)
# nltk.download('averaged_perceptron_tagger_eng', force=True)
# nltk.download('maxent_ne_chunker_tab', force=True)

# # Prompt user for file path
# # file_path = input("Enter the path to the resume file (.pdf or .docx): ")

# # LM Studio API endpoint
# LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

# # Extract text from PDF or DOCX


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

# # ====================== CONTACT INFO EXTRACTION ======================
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

def fix_broken_linkedin_urls(text):
    # 1. Handle cases where URL is followed by text without space
    text = re.sub(
        r'(linkedin\.com\/[a-zA-Z0-9\-]+)([A-Z][a-z]+)',
        r'\1 \2',
        text,
        flags=re.IGNORECASE
    )

    # 2. Join hyphenated line breaks specifically for LinkedIn URLs
    # This handles cases like "laiba-khan-\n129347587"
    text = re.sub(
        r'(linkedin\.com\/[a-zA-Z\-]+)-\n([0-9]+)',
        r'\1-\2',
        text,
        flags=re.IGNORECASE
    )

    # 3. Join LinkedIn URLs split across lines
    text = re.sub(r'www[\n\s]*\.?[\n\s]*linkedin', 'www.linkedin', text, flags=re.IGNORECASE)
    text = re.sub(r'(linkedin\.com)[\n\s]*\/[\n\s]*', r'\1/', text, flags=re.IGNORECASE)
    text = re.sub(r'(linkedin\.com\/[a-zA-Z]+)[\n\s]*\/[\n\s]*', r'\1/', text)

    # 4. Clean up: remove internal newlines and fix space before http(s)
    text = re.sub(r'\s+(?=https?:\/\/)', '', text)
    return text

def extract_linkedin(text):
    text = fix_broken_linkedin_urls(text)
    
    # Improved LinkedIn regex that:
    # 1. Matches standard LinkedIn URL patterns
    # 2. Stops at word boundaries
    # 3. Specifically handles the numeric suffix case
    LINKEDIN_REG = re.compile(
        r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|pub|company)\/'
        r'(?:[a-zA-Z0-9\-]+(?:-[0-9]+)?)'  # handles both name and name-number patterns
        r'(?=\/|$|\s|\?|\))',  # stops at common delimiters
        re.IGNORECASE
    )
    
    matches = re.finditer(LINKEDIN_REG, text)
    for match in matches:
        url = match.group(0).strip()
        if not url.startswith("http"):
            url = "https://" + url.lstrip('/')
        return url
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

# def extract_linkedin(text):
#     text = fix_broken_linkedin_urls(text)
#     matches = re.findall(LINKEDIN_REG, text)
#     if matches:
#         url = matches[0].strip()
#         if not url.startswith("http"):
#             url = "https://" + url.lstrip('/')
#         return url
#     return None
