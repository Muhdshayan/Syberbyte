# ============================ SETUP ============================
import os
import re
import docx2txt
from pdfminer.high_level import extract_text
import nltk
import spacy
from spacy.matcher import Matcher
from nltk.corpus import stopwords

# Download required NLTK data
nltk.download('punkt', force=True)
nltk.download('averaged_perceptron_tagger', force=True)
nltk.download('maxent_ne_chunker', force=True)
nltk.download('words', force=True)
nltk.download('punkt_tab', force=True)
nltk.download('averaged_perceptron_tagger_eng', force=True)
nltk.download('maxent_ne_chunker_tab', force=True)

# Prompt user for file path
file_path = input("Enter the path to the resume file (.pdf or .docx): ")

# Extract text from PDF or DOCX
def extract_text_auto(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        try:
            return extract_text(file_path)
        except Exception as e:
            return f"Error extracting from PDF: {e}"
    elif ext == '.docx':
        try:
            text = docx2txt.process(file_path)
            return text.replace('\t', ' ') if text else "No text found."
        except Exception as e:
            return f"Error extracting from DOCX: %s" % e
    else:
        return "Unsupported file format. Please upload a .pdf or .docx file."

text = extract_text_auto(file_path)

# --- TECHNICAL SKILL DATABASE (COMPREHENSIVE) ---
TECH_SKILL_DB = [
    # Languages
    "python", "java", "c++", "c", "c#", "javascript", "typescript", "go", "rust",
    "ruby", "swift", "kotlin", "scala", "matlab", "r", "sql", "bash", "shell", "php",
    "perl", "haskell", "lua", "dart", "groovy", "objective-c", "assembly",
    # Web Dev
    "html", "css", "sass", "bootstrap", "tailwind", "react", "nextjs", "vue", "angular",
    "express", "flask", "django", "fastapi", "webpack", "npm", "vite", "nuxtjs", "svelte",
    "gatsby", "jquery", "d3js", "threejs", "redux", "mobx", "jest", "storybook",
    # Backend & API
    "nodejs", "spring", "dotnet", "graphql", "rest api", "soap", "grpc", "asp.net",
    "laravel", "symfony", "ruby on rails", "play framework", "micronaut", "quarkus",
    # Databases
    "mysql", "postgresql", "mongodb", "sqlite", "firebase", "redis", "elasticsearch",
    "dynamodb", "cassandra", "oracle", "mariadb", "cosmosdb", "neo4j", "arangodb",
    "hbase", "couchdb", "realm", "firestore",
    # DevOps & Cloud
    "docker", "kubernetes", "aws", "azure", "gcp", "ci/cd", "jenkins", "github actions",
    "terraform", "ansible", "linux", "nginx", "apache", "prometheus", "grafana",
    "istio", "linkerd", "helm", "pulumi", "packer", "vagrant", "consul", "vault",
    "cloudformation", "serverless", "lambda", "ec2", "s3", "rds", "cloudfront",
    "azure functions", "azure devops", "google cloud functions", "gke", "aks", "eks",
    # AI/ML
    "machine learning", "deep learning", "ml", "dl", "nlp", "computer vision",
    "tensorflow", "keras", "pytorch", "sklearn", "scikit-learn", "xgboost", "lightgbm",
    "huggingface", "langchain", "transformers", "openai", "chatgpt", "llm", "llama",
    "generative ai", "stable diffusion", "gan", "reinforcement learning", "time series",
    "opencv", "spacy", "nltk", "bert", "gpt", "gemini", "claude", "mistral",
    # Data & Analysis
    "pandas", "numpy", "matplotlib", "seaborn", "plotly", "jupyter", "sqlalchemy",
    "bigquery", "snowflake", "airflow", "spark", "hadoop", "kafka", "flink", "beam",
    "dbt", "tableau", "power bi", "looker", "qlik", "metabase", "redshift", "databricks",
    "hive", "presto", "trino", "clickhouse", "dask", "ray",
    # Business & Management
    "project management", "agile", "scrum", "kanban", "saas", "erp", "crm", "salesforce",
    "sap", "jira", "confluence", "trello", "asana", "clickup", "ms project", "okrs",
    "kpis", "business intelligence", "market analysis", "financial modeling", "risk management",
    "supply chain", "logistics", "six sigma", "lean", "process improvement", "digital transformation",
    # Cybersecurity
    "cybersecurity", "information security", "penetration testing", "ethical hacking",
    "owasp", "siem", "soc", "vulnerability assessment", "pki", "ssl/tls", "firewalls",
    "ids/ips", "iso 27001", "gdpr", "pci dss", "nist", "cryptography", "zero trust",
    # Blockchain
    "blockchain", "smart contracts", "solidity", "web3", "ethereum", "hyperledger",
    "defi", "nft", "cryptocurrency", "bitcoin", "consensus algorithms", "ipfs",
    # Embedded & IoT
    "embedded systems", "arduino", "raspberry pi", "iot", "fpga", "verilog", "vhd",
    "rtos", "microcontrollers", "bluetooth", "zigbee", "mqtt", "modbus", "can bus",
    # Game Dev
    "unity", "unreal engine", "godot", "cryengine", "game design", "3d modeling",
    "blender", "maya", "opengl", "directx", "vulkan", "shaders", "physics engines",
    # Testing
    "pytest", "unittest", "jest", "mocha", "cypress", "selenium", "jmeter", "junit",
    "testng", "cucumber", "postman", "soapui", "load testing", "stress testing",
    "security testing", "qa automation", "test driven development",
    # Mobile Dev
    "android", "ios", "flutter", "react native", "swiftui", "xcode", "android studio",
    "kotlin multiplatform", "jetpack compose", "mvvm", "mobile ui/ux", "apk",
    "google play", "app store", "push notifications", "in-app purchases",
    # Design & Multimedia
    "ui/ux", "figma", "adobe xd", "sketch", "photoshop", "illustrator", "premiere pro",
    "after effects", "motion graphics", "video editing", "3d animation", "coreldraw",
    "indesign", "prototyping", "wireframing", "user research", "accessibility",
    # Networking
    "tcp/ip", "dns", "dhcp", "vpn", "wan", "lan", "sdn", "ospf", "bgp", "mpls",
    "voip", "sip", "qos", "network security", "wireshark", "packet analysis",
    # Hardware
    "computer architecture", "cpu design", "gpu programming", "cuda", "opencl",
    "embedded linux", "device drivers", "raspberry pi", "circuit design", "pcb",
    "altium", "cad", "vlsi", "asic", "fpga programming",
    # Quantum Computing
    "quantum computing", "qiskit", "cirq", "quantum algorithms", "quantum cryptography",
    # Miscellaneous Tech
    "arduino", "raspberry pi", "robotics", "computer graphics", "gis", "autocad",
    "solidworks", "ansys", "industrial automation", "plc", "scada"
]

# --- SOFT SKILLS DATABASE ---
SOFT_SKILL_DB = [
    "communication", "teamwork", "collaboration", "leadership", "problem solving",
    "critical thinking", "adaptability", "creativity", "emotional intelligence",
    "time management", "organization", "attention to detail", "work ethic",
    "interpersonal skills", "negotiation", "conflict resolution", "decision making",
    "strategic thinking", "analytical skills", "presentation skills", "public speaking",
    "active listening", "empathy", "patience", "diplomacy", "mentoring", "coaching",
    "networking", "relationship building", "cultural awareness", "diversity and inclusion",
    "persuasion", "influence", "delegation", "accountability", "reliability", "initiative",
    "self-motivation", "resilience", "stress management", "growth mindset", "curiosity",
    "continuous learning", "flexibility", "multitasking", "prioritization", "goal setting",
    "feedback", "constructive criticism", "transparency", "professionalism", "business etiquette",
    "customer service", "client management", "stakeholder management", "project coordination",
    "change management", "risk assessment", "innovation", "design thinking", "agile mindset",
    "remote collaboration", "virtual teamwork", "written communication", "verbal communication",
    "nonverbal communication", "storytelling", "data-driven decision making", "resourcefulness",
    "self-awareness", "self-regulation", "motivation", "social skills", "positive attitude",
    "humor", "tact", "discretion", "ethical judgment", "corporate governance"
]

# ============================ NAME EXTRACTION (spaCy) ============================
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

def extract_name(resume_text):
    nlp_text = nlp(resume_text)
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    matcher.add('NAME', [pattern])
    matches = matcher(nlp_text)
    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text
    return None

# ====================== CONTACT INFO EXTRACTION ======================
PHONE_REG = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+', re.IGNORECASE)
GITHUB_REG = re.compile(r'https?:\/\/(www\.)?github\.com\/[a-zA-Z0-9\-_.]+')
LINKEDIN_REG = re.compile(r'https?:\/\/(www\.)?linkedin\.com\/(?:in|pub|company)\/[a-zA-Z0-9\-_/]+')
PORTFOLIO_REG = re.compile(r'https?:\/\/(www\.)?[a-zA-Z0-9\-]+\.[a-z]{2,}\/?.*')

def extract_phone_number(text):
    phones = re.findall(PHONE_REG, text)
    if phones:
        number = ''.join(phones[0])
        if len(number) < 16:
            return number
    return None

def extract_email(text):
    emails = re.findall(EMAIL_REG, text)
    return emails[0] if emails else None

def extract_links(text):
    links = {'github': None, 'linkedin': None, 'portfolio': None}
    github = re.search(GITHUB_REG, text)
    linkedin = re.search(LINKEDIN_REG, text)
    portfolio = re.search(PORTFOLIO_REG, text)

    if github:
        links['github'] = github.group(0).strip()
    if linkedin:
        links['linkedin'] = linkedin.group(0).strip()
    if portfolio:
        links['portfolio'] = portfolio.group(0).strip()

    return links

# ====================== EDUCATION EXTRACTION (Degree + Year) ======================
STOPWORDS = set(stopwords.words('english'))
EDUCATION = [
    'BE', 'B.E.', 'B.E', 'BS', 'B.S', 'ME', 'M.E', 'M.E.', 'M.B.A', 'MBA', 'MS', 'M.S',
    'BTECH', 'B.TECH', 'M.TECH', 'MTECH', 'SSLC', 'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII',
    'BACHELOR', 'BACHELORS', 'MASTER', 'MASTERS', 'UNDERGRADUATE', 'POSTGRADUATE',
    "BACHELOR'S", "MASTER'S", 'PHD', 'DOCTORATE',
    # Local Pakistani Degrees and Boards
    'FSC', 'FA', 'ICS', 'ICOM', 'HSSC', 'SSC',
    'BIEK', 'BISE', 'FBISE', 'KARACHI BOARD', 'LAHORE BOARD', 'RAWALPINDI BOARD',
    'PUNJAB BOARD', 'SINDH BOARD', 'KPK BOARD', 'CAMBRIDGE', 'EDEXCEL',
    # Common Pakistani Degree Programs
    'SOFTWARE ENGINEERING', 'COMPUTER SCIENCE', 'IT', 'INFORMATION TECHNOLOGY',
    'ELECTRICAL ENGINEERING', 'MECHANICAL ENGINEERING', 'CIVIL ENGINEERING',
    'BUSINESS ADMINISTRATION', 'ACCOUNTING', 'FINANCE', 'ECONOMICS', 'PSYCHOLOGY','ARTIFICIAL INTELLIGENCE'
]

FIELDS = [
    'SOFTWARE ENGINEERING', 'COMPUTER SCIENCE', 'INFORMATION TECHNOLOGY', 'IT',
    'ELECTRICAL ENGINEERING', 'MECHANICAL ENGINEERING', 'CIVIL ENGINEERING',
    'DATA SCIENCE', 'BUSINESS ADMINISTRATION', 'ACCOUNTING', 'FINANCE', 'ECONOMICS', 'PSYCHOLOGY',
    'BIOLOGY', 'PHYSICS', 'CHEMISTRY', 'MATH', 'STATISTICS', 'ARTS', 'HUMANITIES',
    'SOCIAL SCIENCES', 'MARKETING', 'SUPPLY CHAIN'
]

def extract_education(resume_text):
    nlp_text = nlp(resume_text)
    nlp_sents = [sent.text.strip() for sent in nlp_text.sents]

    edu = {}
    for index, text in enumerate(nlp_sents):
        for tex in text.split():
            tex = re.sub(r'[?|$|.|!|,]', r'', tex)
            if tex.upper() in EDUCATION and tex.lower() not in STOPWORDS:
                next_sent = nlp_sents[index + 1] if index + 1 < len(nlp_sents) else ''
                edu[tex] = text + ' ' + next_sent

    education = []
    for key in edu:
        entry = edu[key]
        year_match = re.search(r'(20|19)\d{2}', entry)
        # ✅ Improved field matching with word boundaries
        field_found = next(
            (field for field in FIELDS if re.search(rf'\b{re.escape(field.lower())}\b', entry.lower())),
            None
        )
        year = year_match.group(0) if year_match else None

        if year and field_found:
            education.append((key, year, field_found))
        elif year:
            education.append((key, year))
        else:
            education.append(key)

    return list(set(education))  # ✅ Remove duplicates

# ====================== SUMMARY EXTRACTION ======================
def extract_section(text, section_name):
    pattern = rf"{section_name}\s*\n((?:.*\n)+?)(?=\n[A-Z][^\n]*\n|\Z)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def extract_professional_summary(text):
    """
    Extracts the professional summary or career objective from the resume.
    Uses multiple fallback strategies to improve accuracy.
    """
    summary_aliases = [
        "professional summary", "summary", "career summary", "about me", "profile",
        "objective", "career objective", "personal statement"
    ]

    # --- Strategy 1: Section-based extraction (most accurate)
    for alias in summary_aliases:
        summary = extract_section(text, alias)
        if summary and len(summary.split()) >= 10:
            return summary.strip()

    # --- Strategy 2: Heuristic-based fallback (first 10 lines)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for i in range(min(10, len(lines))):
        line = lines[i]
        if any(start in line.lower() for start in ["i am", "i have", "results-driven", "seasoned", "experienced", "seeking a", "motivated", "detail-oriented"]):
            # Capture up to 3 lines if they seem part of a paragraph
            summary_lines = [line]
            for j in range(i+1, min(i+4, len(lines))):
                if len(lines[j].split()) < 3: break
                summary_lines.append(lines[j])
            summary = " ".join(summary_lines)
            if len(summary.split()) >= 10:
                return summary.strip()

    # --- Strategy 3: Regex match for typical summary phrasing
    regex_patterns = [
        r"(?:experienced|motivated|results[- ]?oriented|driven|seasoned)[^.]{20,250}\.",
        r"(?:seeking a|aiming for|looking for)[^.]{20,250}\."
    ]
    for pattern in regex_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()

    return "Summary Not Found"
# ====================== EXTRACT SKILLS ======================
def extract_skills(text, skill_db):
    """
    Extracts unique skills from a text by matching with a lowercased skill DB.
    Includes basic word boundary matching to avoid partial matches.
    """
    text_lower = text.lower()
    found = []
    for skill in skill_db:
        if re.search(rf"\b{re.escape(skill.lower())}\b", text_lower):
            found.append(skill)
    return list(set(found))

# ====================== EXPERIENCE LEVEL EXTRACTION ======================
def extract_experience(doc):
    verbs = [token.text.lower() for token in doc if token.pos_ == 'VERB']

    senior_keywords = ['lead', 'manage', 'direct', 'oversee', 'supervise', 'orchestrate', 'govern']
    mid_senior_keywords = ['develop', 'design', 'analyze', 'implement', 'coordinate', 'execute', 'strategize']
    mid_junior_keywords = ['assist', 'support', 'collaborate', 'participate', 'aid', 'facilitate', 'contribute']

    if any(keyword in verbs for keyword in senior_keywords):
        level_of_experience = "Senior"
    elif any(keyword in verbs for keyword in mid_senior_keywords):
        level_of_experience = "Mid-Senior"
    elif any(keyword in verbs for keyword in mid_junior_keywords):
        level_of_experience = "Mid-Junior"
    else:
        level_of_experience = "Entry Level"

    return level_of_experience
from dateutil import parser
from datetime import datetime

def estimate_skill_experience(text, skill):
    """
    Estimate years of experience in a given skill based on date ranges near the skill mentions.
    """
    text = text.lower()
    skill = skill.lower()

    # Split resume into lines or sentences
    lines = re.split(r'\n|\. ', text)

    experience_years = []

    for i, line in enumerate(lines):
        if skill in line:
            # Search window: nearby 2 lines (before and after)
            window = " ".join(lines[max(0, i-2):min(i+3, len(lines))])

            # Look for year ranges or patterns
            date_patterns = re.findall(r'(19|20)\d{2}[^a-zA-Z0-9]{1,3}(19|20)\d{2}', window)
            if date_patterns:
                for start, end in date_patterns:
                    try:
                        duration = int(end) - int(start)
                        if 0 <= duration <= 50:
                            experience_years.append(duration)
                    except:
                        continue

            # Support for "X years of skill" phrasing
            explicit = re.findall(r'(\d{1,2})\s*\+?\s*(?:years|yrs)[^\n]*?' + re.escape(skill), window)
            if explicit:
                experience_years.extend([int(e) for e in explicit])

    # Return sum or max of durations
    return sum(experience_years) if experience_years else 0

# ====================== DISPLAY RESULTS ======================
print("\n=== Extracted Resume Details ===")
print("\U0001F9D1 Name:", extract_name(text))
print("\U0001F4DE Phone Number:", extract_phone_number(text))
print("\U0001F4E7 Email:", extract_email(text))

links = extract_links(text)
print("\U0001F4BB GitHub:", links['github'])
print("\U0001F517 LinkedIn:", links['linkedin'])
print("\U0001F310 Portfolio:", links['portfolio'])

print("\n\U0001F4DD Professional Summary:")
print(extract_professional_summary(text))

education_info = extract_education(text)
print("\n\U0001F393 Education Qualifications:")
if education_info:
    for entry in education_info:
        print("-", entry)
else:
    print("No education details found.")

print("\n\U0001F528 Technical Skills:")
tech_skills = extract_skills(text, TECH_SKILL_DB)
for skill in tech_skills:
    print("-", skill)

print("\n\U0001F4AA Soft Skills:")
soft_skills = extract_skills(text, SOFT_SKILL_DB)
for skill in soft_skills:
    print("-", skill)

print("\n\U0001F4BC Experience Level:")
doc_nlp = nlp(text)
experience_level = extract_experience(doc_nlp)
print("-", experience_level) 