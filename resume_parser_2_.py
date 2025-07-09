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

  

# # ====================== CONTACT INFO EXTRACTION ======================
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



