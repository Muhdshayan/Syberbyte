import os
import re
import json
import docx2txt
from pdfminer.high_level import extract_text
import spacy
from spacy.matcher import Matcher
import requests
from datetime import datetime
import fitz  # PyMuPDF for PDF link extraction
from docx import Document
import glob

# Ollama API endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral:latest"
# Load spaCy model
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

# Common false positives to exclude
BLACKLIST = {
    "developer", "engineer", "intern", "project", "summary", "skills", "experience",
    "education", "system", "app", "application", "curriculum", "vitae", "resume", "cv",
    "contact", "objective", "qualification"
}

# Regular expressions for contact info
PHONE_REG = re.compile(r'[\+\(]?[0-9][0-9 .\-\(\)]{8,}[0-9]|\([0-9][0-9 .\-\(\)]{7,}[0-9]')
EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+', re.IGNORECASE)
GITHUB_PROFILE_REG = re.compile(
    r'https?:\/\/(?:www\.)?github\.com\/([a-zA-Z0-9\-]+)(?!\/[a-zA-Z0-9])',
    re.IGNORECASE
)
LINKEDIN_REG = re.compile(
    r'(https?:\/\/)?(www\.)?linkedin\.com\/(in|pub|company)\/[a-zA-Z0-9\-]+(?:-[a-zA-Z0-9]+)*',
    re.IGNORECASE
)

def extract_text_auto(file_path):
    """Extract text from PDF or DOCX files"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        try:
            text = extract_text(file_path)
            print(f"[DEBUG] Extracted PDF text from {file_path}")
            return text
        except Exception as e:
            return f"Error extracting from PDF: {e}"
    elif ext == '.docx':
        try:
            text = docx2txt.process(file_path)
            text = text.replace('\t', ' ') if text else "No text found."
            print(f"[DEBUG] Extracted DOCX text from {file_path}")
            return text
        except Exception as e:
            return f"Error extracting from DOCX: {e}"
    else:
        return "Unsupported file format. Please upload a .pdf or .docx file."

def extract_phone_number(text):
    """Extract phone number using regex"""
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

def extract_email(text, file_path=None):
    """Extract email from text and embedded hyperlinks"""
    # Extract from visible text (regex)
    try:
        emails = re.findall(EMAIL_REG, text)
        if emails:
            return emails[0]
    except Exception as e:
        print("[DEBUG] Email regex failed:", e)

    if not file_path:
        return None

    # Extract from DOCX embedded hyperlinks
    if file_path.lower().endswith(".docx"):
        try:
            doc = Document(file_path)
            for rel in doc.part.rels.values():
                if "hyperlink" in rel.reltype:
                    url = rel.target_ref.strip()
                    if url.startswith("mailto:"):
                        email = url.replace("mailto:", "").strip()
                        if re.match(EMAIL_REG, email):
                            return email
        except Exception as e:
            print("[DEBUG] Failed to extract email from DOCX hyperlinks:", e)

    # Extract from PDF embedded hyperlinks
    if file_path.lower().endswith(".pdf"):
        try:
            doc = fitz.open(file_path)
            for page in doc:
                for link in page.get_links():
                    uri = link.get("uri", "")
                    if uri.startswith("mailto:"):
                        email = uri.replace("mailto:", "").strip()
                        if re.match(EMAIL_REG, email):
                            return email
        except Exception as e:
            print("[DEBUG] Failed to extract email from PDF hyperlinks:", e)

    return None

def fix_broken_github_urls(text):
    """Fix broken GitHub URLs in text"""
    text = re.sub(r'(\S)-\n(\S)', r'\1\2', text)
    text = re.sub(r'(https?:\/\/[^\s]+)', r'\1\n', text)
    text = re.sub(r'\s+(?=https?:\/\/)', '', text)
    return text

def extract_github(text):
    """Extract GitHub profile URL"""
    text = fix_broken_github_urls(text)
    match = re.search(GITHUB_PROFILE_REG, text)
    if match:
        username = match.group(1)
        return f"https://github.com/{username}"
    return None

def fix_broken_linkedin_urls(text):
    """Fix broken LinkedIn URLs in text"""
    text = re.sub(
        r'(linkedin\.com\/(?:in|pub|company)\/[a-zA-Z0-9\-]+)-\s*\n\s*([a-zA-Z0-9\-]+)',
        r'\1\2',
        text,
        flags=re.IGNORECASE
    )
    text = re.sub(r'www[\n\s]*\.?[\n\s]*linkedin', 'www.linkedin', text, flags=re.IGNORECASE)
    text = re.sub(r'(linkedin\.com)[\n\s]*\/[\n\s]*', r'\1/', text, flags=re.IGNORECASE)
    text = re.sub(r'(linkedin\.com\/[a-zA-Z0-9\-]+)[\n\s]*\/[\n\s]*', r'\1/', text)
    return text

def extract_hyperlinks_from_docx(file_path):
    """Extract hyperlinks from DOCX file"""
    try:
        doc = Document(file_path)
        links = []
        for rel in doc.part.rels.values():
            if "hyperlink" in rel.reltype:
                url = rel.target_ref
                if "linkedin.com" in url.lower():
                    links.append(url.strip())
        return links
    except Exception as e:
        print("[DEBUG] Failed to extract hyperlinks from DOCX:", e)
        return []

def extract_hyperlinks_from_pdf(file_path):
    """Extract hyperlinks from PDF file"""
    try:
        links = []
        doc = fitz.open(file_path)
        for page in doc:
            for link in page.get_links():
                uri = link.get('uri', '')
                if uri and "linkedin.com" in uri.lower():
                    links.append(uri.strip())
        return links
    except Exception as e:
        print("[DEBUG] Failed to extract hyperlinks from PDF:", e)
        return []

def extract_linkedin(text, file_path=None):
    """Extract LinkedIn profile URL from text and embedded links"""
    # Clean raw text
    text = fix_broken_linkedin_urls(text)

    # Regex match in visible text
    matches = re.finditer(LINKEDIN_REG, text)
    for match in matches:
        url = match.group(0).strip().rstrip('.,);:')
        if not url.startswith("http"):
            url = "https://" + url
        return url

    if not file_path:
        return None

    # DOCX embedded hyperlinks
    if file_path.lower().endswith(".docx"):
        docx_links = extract_hyperlinks_from_docx(file_path)
        if docx_links:
            return docx_links[0]

    # PDF embedded hyperlinks
    if file_path.lower().endswith(".pdf"):
        pdf_links = extract_hyperlinks_from_pdf(file_path)
        if pdf_links:
            return pdf_links[0]

    return None

def extract_name(resume_text):
    """Extract name using multiple heuristics and spaCy NER"""
    try:
        lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
        lines = [line for line in lines if not re.match(r'^(\W|\d)+$', line)]

        # Check for markdown-style headings (like # NAME)
        for line in lines[:10]:
            if line.startswith('#') and not line.startswith('##'):
                name_candidate = line.lstrip('#').strip()
                if (
                    2 <= len(name_candidate.split()) <= 3 and
                    all(word.isalpha() for word in name_candidate.split()) and
                    not any(word.lower() in BLACKLIST for word in name_candidate.split())
                ):
                    return name_candidate.title()

        # Main heading in ALL CAPS (e.g. SIDRA BUKHARI)
        for line in lines[:5]:
            if (
                line.isupper() and
                2 <= len(line.split()) <= 3 and
                all(word.isalpha() for word in line.split()) and
                not any(word.lower() in BLACKLIST for word in line.split())
            ):
                return line.title()

        # Strong title-case heuristic (top 10 lines)
        for line in lines[:10]:
            if (
                2 <= len(line.split()) <= 3 and
                line == line.title() and
                all(word.isalpha() for word in line.split()) and
                not any(word.lower() in BLACKLIST for word in line.split())
            ):
                return line

        # spaCy NER: PERSON entities from top 10 lines
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

        # POS tagging for Proper Nouns
        for line in lines[:5]:
            doc_line = nlp(line)
            name_tokens = []
            for token in doc_line:
                if token.pos_ == 'PROPN' and token.is_alpha and token.text.istitle():
                    name_tokens.append(token.text)
                elif name_tokens:
                    break
            if (
                2 <= len(name_tokens) <= 3 and
                not any(t.lower() in BLACKLIST for t in name_tokens)
            ):
                return " ".join(name_tokens)

        # From email prefix (avoid circular dependency)
        emails = re.findall(EMAIL_REG, resume_text)
        if emails:
            local_part = emails[0].split('@')[0]
            possible_name = re.sub(r'[._\-]', ' ', local_part).title()
            words = possible_name.split()
            if (
                2 <= len(words) <= 3 and
                all(w.isalpha() for w in words) and
                not any(word.lower() in BLACKLIST for word in words)
            ):
                return " ".join(words)

        # From LinkedIn URL
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

def call_ollama_api(prompt, model_name=MODEL_NAME):
    """Call Ollama API for LLM inference"""
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 512
        }
    }
    
    try:
        print(f"[DEBUG] Calling Ollama API with model: {model_name}")
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        response.raise_for_status()
        result = response.json()
        api_response = result.get("response", "")
        print(f"[DEBUG] Ollama response: {api_response[:200]}...")
        return api_response
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Ollama API request failed: {e}")
        print(f"[ERROR] URL: {OLLAMA_URL}")
        print(f"[ERROR] Payload: {json.dumps(payload, indent=2)}")
        return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse Ollama response: {e}")
        return None

def extract_education(resume_text):
    """Extract education details using Ollama LLM"""
    prompt = f"""Extract the most recent education information from this resume text. Return only a JSON object with 'institute', 'degree', and 'year' fields. No additional text.

Resume text:
{resume_text[:2000]}"""

    response = call_ollama_api(prompt)
    if not response:
        print("[ERROR] No response from Ollama for education extraction")
        return None
    
    try:
        # Clean the response
        cleaned_response = response.strip()
        
        # Try to extract JSON from response
        json_match = re.search(r'\{[^{}]*\}', cleaned_response)
        if json_match:
            json_str = json_match.group(0)
            # Fix common JSON issues
            json_str = json_str.replace("'", '"')
            education_entry = json.loads(json_str)
            print(f"[DEBUG] Extracted education: {education_entry}")
            return education_entry
        else:
            print(f"[ERROR] No JSON found in education response: {cleaned_response}")
            return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse education JSON: {e}")
        print(f"[ERROR] Raw response: {response}")
        return None

def extract_skills(resume_text):
    """Extract skills using Ollama LLM"""
    prompt = f"""Extract technical and soft skills from this resume. Return only a JSON object with this exact structure:
{{
  "technical_skills": {{"Python": 75, "JavaScript": 60}},
  "soft_skills": {{"Leadership": 80, "Communication": 70}}
}}

Assign scores 0-100 based on evidence in the resume. No additional text.

Resume text:
{resume_text[:2000]}"""

    response = call_ollama_api(prompt)
    if not response:
        print("[ERROR] No response from Ollama for skills extraction")
        return None
    
    try:
        # Clean the response
        cleaned_response = response.strip()
        
        # Try to extract JSON from response
        json_match = re.search(r'\{[^{}]*"technical_skills"[^{}]*"soft_skills"[^{}]*\}', cleaned_response, re.DOTALL)
        if not json_match:
            json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(0)
            # Fix common JSON issues
            json_str = json_str.replace("'", '"')
            skills_data = json.loads(json_str)
            print(f"[DEBUG] Extracted skills: {skills_data}")
            return skills_data
        else:
            print(f"[ERROR] No JSON found in skills response: {cleaned_response}")
            return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse skills JSON: {e}")
        print(f"[ERROR] Raw response: {response}")
        return None

def extract_years_of_experience(resume_text):
    """Extract years of experience using Ollama LLM"""
    current_date = datetime.now().strftime("%B %Y")
    processed_text = re.sub(r'\bPresent\b', current_date, resume_text, flags=re.IGNORECASE)
    
    prompt = f"""Calculate total work experience in years from this resume. Look for:
- Job dates (Jan 2020 - Dec 2022 = 2 years)
- Duration mentions (2 years experience, 6 months = 0.5 years)
- Current positions (ongoing until {current_date})

Return only a number (like 2.5 or 0.0). No text, no explanation.

Resume text:
{processed_text[:2000]}"""

    response = call_ollama_api(prompt)
    if not response:
        print("[ERROR] No response from Ollama for experience extraction")
        return 0.0
    
    try:
        # Extract float number from response
        cleaned_response = response.strip()
        print(f"[DEBUG] Experience response: {cleaned_response}")
        
        # Look for numbers in the response
        numbers = re.findall(r'\d+(?:\.\d+)?', cleaned_response)
        if numbers:
            experience_years = float(numbers[0])
            print(f"[DEBUG] Extracted experience: {experience_years} years")
            return experience_years
        else:
            print("[DEBUG] No numeric value found in experience response")
            return 0.0
    except ValueError as e:
        print(f"[ERROR] Failed to convert experience to float: {e}")
        return 0.0

def parse_resume(file_path):
    """Main function to parse a single resume file"""
    print(f"\n{'='*50}")
    print(f"Processing: {os.path.basename(file_path)}")
    print(f"{'='*50}")
    
    # Extract text
    text = extract_text_auto(file_path)
    if "Error" in text:
        return {"file": file_path, "error": text}
    
    # Extract all information
    name = extract_name(text)
    phone = extract_phone_number(text)
    email = extract_email(text, file_path)
    github = extract_github(text)
    linkedin = extract_linkedin(text, file_path)
    education = extract_education(text)
    skills = extract_skills(text)
    years_of_experience = extract_years_of_experience(text)
    
    resume_data = {
        "file": os.path.basename(file_path),
        "name": name if name else 'Not found',
        "phone": phone if phone else 'Not found',
        "email": email if email else 'Not found',
        "github": github if github else 'Not found',
        "linkedin": linkedin if linkedin else 'Not found',
        "education": education if education else 'Not found',
        "skills": skills if skills else 'Not found',
        "years_of_experience": years_of_experience if years_of_experience is not None else 'Not found'
    }
    
    return resume_data

def process_resume_directory(directory_path="./resumes", output_dir="./candidates", output_filename="parsed_resumes.json"):
    """Process all resume files in a directory"""
    print(f"Scanning directory: {os.path.abspath(directory_path)}")
    
    # Create input directory if it doesn't exist
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Created directory: {directory_path}")
        print("Please add resume files (.pdf or .docx) to this directory and run again.")
        return
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Find all PDF and DOCX files
    pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
    docx_files = glob.glob(os.path.join(directory_path, "*.docx"))
    resume_files = pdf_files + docx_files
    
    if not resume_files:
        print(f"No resume files found in {directory_path}")
        print("Please add .pdf or .docx files to the directory.")
        return
    
    print(f"Found {len(resume_files)} resume file(s)")
    
    all_results = []
    
    for file_path in resume_files:
        try:
            result = parse_resume(file_path)
            all_results.append(result)
            os.remove(file_path)
            print("File deleted successfully.")
            # Print summary for each file
            print(f"\nResults for {result['file']}:")
            print(f"  Name: {result['name']}")
            print(f"  Email: {result['email']}")
            print(f"  Phone: {result['phone']}")
            print(f"  Years of Experience: {result['years_of_experience']}")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            all_results.append({"file": os.path.basename(file_path), "error": str(e)})
    
    # Create full output path
    output_path = os.path.join(output_dir, output_filename)
    
    # Save results to JSON file in the parsed directory
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"\n{'='*50}")
        print(f"Results saved to: {os.path.abspath(output_path)}")
        print(f"Total files processed: {len(all_results)}")
        print(f"{'='*50}")
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    """Main function"""
    print("Resume Parser with Ollama Integration")
    print("===================================")
    
    # Test Ollama connection first
    print("Testing Ollama connection...")
    test_response = call_ollama_api("Hello, are you working?")
    if test_response:
        print("Ollama connection successful")
    else:
        print("Ollama connection failed")
        print("Please ensure:")
        print("1. Ollama is running: docker exec -it ollama ollama serve")
        print("2. Model is loaded: docker exec -it ollama ollama run mistral:latest")
        print("3. Ollama is accessible at http://localhost:11434")
        return
    
    # You can customize these paths
    resume_directory = "./resumes"
    output_directory = "./candidates"
    output_filename = "parsed_resumes.json"
    
    process_resume_directory(resume_directory, output_directory, output_filename)

if __name__ == "__main__":
    main()