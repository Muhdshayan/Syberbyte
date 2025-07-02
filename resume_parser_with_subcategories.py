import fitz  # PyMuPDF
import docx
import re
import json
import datetime
from pathlib import Path
import spacy
import sys

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

def read_pdf(path):
    doc = fitz.open(path)
    return "\n".join([page.get_text() for page in doc])

def read_docx(path):
    doc = docx.Document(path)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_contact_info(text):
    contact_info = {
        "phone": "",
        "email": "",
        "linkedin": "",
        "github": ""
    }
    phone_pattern = r'(?:(?:\+|00)?[0-9]{1,3}[\s\-]?)?(?:\(?\d{2,4}\)?[\s\-]?)?\d{3,4}[\s\-]?\d{3,4}'
    phones = re.findall(phone_pattern, text)
    valid_phones = [p.strip() for p in phones if len(re.sub(r'\D', '', p)) >= 10]
    if valid_phones:
        contact_info["phone"] = valid_phones[0]
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    emails = re.findall(email_pattern, text)
    if emails and all(c not in emails[0] for c in [" ", ",", ";"]):
        contact_info["email"] = emails[0].lower()
    linkedin_pattern = r'https?:\/\/(www\.)?linkedin\.com\/[a-zA-Z0-9\/\-_]+'
    linkedin = re.search(linkedin_pattern, text)
    if linkedin:
        contact_info["linkedin"] = linkedin.group(0).strip()
    github_pattern = r'https?:\/\/(www\.)?github\.com\/[a-zA-Z0-9\-_]+'
    github = re.search(github_pattern, text)
    if github:
        contact_info["github"] = github.group(0).strip()
    return contact_info

def extract_section(text, section_title):
    section_aliases = {
        "education": ["education", "academics", "educational background"],
        "experience": ["experience", "work history", "professional experience"],
        "skills": ["skills", "technical skills", "key skills"],
        "projects": ["projects", "key projects", "personal projects"],
        "certifications": ["certifications", "certificates", "courses and certifications"],
        "soft skills": ["soft skills", "interpersonal skills", "strengths"]
    }
    normalized_title = None
    for key, aliases in section_aliases.items():
        if section_title.lower() in [key.lower()] + [a.lower() for a in aliases]:
            normalized_title = key
            break
    if not normalized_title:
        normalized_title = section_title
    title_pattern = "|".join([re.escape(t) for t in [normalized_title] + section_aliases.get(normalized_title, [])])
    pattern = rf"(?i)(?:{title_pattern}).*?(?=\n\s*\n|\n[A-Z][A-Za-z ]+(?:\n|$)|\Z)"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        section = match.group(0).strip()
        section = re.sub(rf"^(?:{title_pattern})[\s:.-]*", "", section, flags=re.IGNORECASE)
        return section.strip()
    return ""

def extract_resume_sections(resume_text):
    sections = {
        "education": extract_section(resume_text, "Education"),
        "experience": extract_section(resume_text, "Experience"),
        "skills": extract_section(resume_text, "Skills"),
        "projects": extract_section(resume_text, "Projects"),
        "certifications": extract_section(resume_text, "Certifications"),
        "soft_skills": extract_section(resume_text, "Soft Skills")
    }
    for section, content in sections.items():
        content = "\n".join([line.strip() for line in content.splitlines() if line.strip()])
        content = re.sub(r"^[\s•\-*]\s*", "", content, flags=re.MULTILINE)
        sections[section] = content.strip()
    return sections

def extract_skills(text, skill_db):
    text_lower = text.lower()
    found = []
    for skill in skill_db:
        if re.search(rf"\b{re.escape(skill.lower())}\b", text_lower):
            found.append(skill)
    return list(set(found))

def extract_soft_skills(text, soft_skill_db):
    text_lower = text.lower()
    found = []
    for skill in soft_skill_db:
        skill_lower = skill.lower()
        pattern = r"(^|\W)" + re.escape(skill_lower) + r"($|\W)"
        if re.search(pattern, text_lower):
            found.append(skill)
    variations = {
        "teamwork": ["team player", "team-player", "team work"],
        "communication": ["communication skills", "communicate effectively"],
        "problem solving": ["problem-solve", "solving problems"],
        "time management": ["manage time", "time-manage"]
    }
    for canonical_skill, aliases in variations.items():
        if canonical_skill in found:
            continue
        for alias in aliases:
            if re.search(rf"\b{re.escape(alias)}\b", text_lower):
                found.append(canonical_skill)
                break
    return sorted(list(set(found)), key=lambda x: x.lower())

def extract_name(resume_text, entities, skill_db):
    NON_NAME_PATTERNS = [
        r'academic', r'qualification', r'education', r'experience',
        r'skill', r'project', r'objective', r'summary',
        r'curriculum vitae', r'resume', r'cv', r'contact'
    ]
    skill_db_lower = [skill.lower() for skill in skill_db]
    if "PERSON" in entities:
        for name in entities["PERSON"]:
            name_clean = name.strip().title()
            name_parts = name_clean.split()
            if (2 <= len(name_parts) <= 3 and
                all(len(part) > 1 for part in name_parts) and
                all(part.isalpha() for part in name_parts) and
                not any(re.search(pattern, name_clean.lower()) for pattern in NON_NAME_PATTERNS) and
                name_clean.lower() not in skill_db_lower):
                return name_clean
    lines = [line.strip() for line in resume_text.split('\n') if line.strip()][:15]
    for line in lines:
        line_clean = line.strip()
        line_parts = line_clean.split()
        if (len(line_clean) > 40 or
           len(line_clean) < 5 or
           len(line_parts) not in [2, 3] or
           not line_clean == line_clean.title() or
           any(c.isdigit() for c in line_clean) or
           any(not word.isalpha() for word in line_parts) or
           any(word.lower() in skill_db_lower for word in line_parts) or
           any(re.search(pattern, line_clean.lower()) for pattern in NON_NAME_PATTERNS)):
            continue
        return line_clean
    email_match = re.search(r'([a-zA-Z]+)[\._]([a-zA-Z]+)@', resume_text)
    if email_match:
        first = email_match.group(1).title()
        last = email_match.group(2).title()
        if (len(first) > 1 and len(last) > 1 and
            first.lower() not in skill_db_lower and
            last.lower() not in skill_db_lower):
            return f"{first} {last}"
    linkedin_match = re.search(r'linkedin\.com/(?:in|pub)/([a-zA-Z-]+)-?([a-zA-Z-]+)', resume_text.lower())
    if linkedin_match:
        first = linkedin_match.group(1).title()
        last = linkedin_match.group(2).title()
        if (len(first) > 1 and len(last) > 1 and
            first.lower() not in skill_db_lower and
            last.lower() not in skill_db_lower):
            return f"{first} {last}"
    return "Name Not Found"

def extract_professional_summary(text):
    summary_aliases = [
        "professional summary", "summary", "career summary", "about me", "profile",
        "objective", "career objective", "personal statement"
    ]
    for alias in summary_aliases:
        summary = extract_section(text, alias)
        if summary and len(summary.split()) >= 10:
            return summary.strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for i in range(min(10, len(lines))):
        line = lines[i]
        if any(start in line.lower() for start in ["i am", "i have", "results-driven", "seasoned", "experienced", "seeking a", "motivated", "detail-oriented"]):
            summary_lines = [line]
            for j in range(i+1, min(i+4, len(lines))):
                if len(lines[j].split()) < 3: break
                summary_lines.append(lines[j])
            summary = " ".join(summary_lines)
            if len(summary.split()) >= 10:
                return summary.strip()
    regex_patterns = [
        r"(?:experienced|motivated|results[- ]?oriented|driven|seasoned)[^.]{20,250}\.",
        r"(?:seeking a|aiming for|looking for)[^.]{20,250}\."
    ]
    for pattern in regex_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    return "Summary Not Found"

def extract_education(resume_text):
    education_entries = []
    text = re.sub(r'[–—]', '-', resume_text)
    education_section = re.search(
        r'(?i)(?:education|academic qualification|academic background|qualification)[\s:]*(.*?)(?=\n\s*\n|\n\w+:|$)',
        text, re.DOTALL
    )
    text_to_scan = education_section.group(1) if education_section else text
    entries = re.split(r'\n(?=\s*\d{4}\s*-\s*(?:Present|\d{4}))|\n\s*\n', text_to_scan)
    for entry in entries:
        if not entry.strip():
            continue
        edu_entry = {
            'degree': '',
            'institution': '',
            'year': ''
        }
        year_match = re.search(
            r'(\d{4}\s*-\s*(?:Present|\d{4}))',
            entry
        )
        if year_match:
            edu_entry['year'] = year_match.group(1).strip()
            entry = entry.replace(year_match.group(1), '').strip()
        parts = re.split(r'[-–—:•]', entry, maxsplit=1)
        if len(parts) == 2:
            edu_entry['degree'] = parts[0].strip()
            edu_entry['institution'] = parts[1].strip()
        else:
            edu_entry['degree'] = entry.strip()
        edu_entry['degree'] = re.sub(r'\d{4}.*$', '', edu_entry['degree']).strip()
        if edu_entry['institution']:
            edu_entry['institution'] = re.sub(r'[.,]\s*\d{4}.*$', '', edu_entry['institution']).strip()
        if edu_entry['degree'] or edu_entry['institution']:
            education_entries.append(edu_entry)
    return education_entries

def extract_experience(resume_text):
    try:
        experiences = []
        text = re.sub(r'\t', '    ', resume_text)
        text = re.sub(r'[–—]', '-', text)
        exp_section_match = re.search(
            r'(?i)(?:work\s*experience|professional\s*experience|employment\s*history|internship\s*experience|internships?|experience|relevant\s*experience|career\s*history|work)[\s:]*\n(.*?)(?=\n\s*(?:education|skills|projects|awards|publications|volunteer|personal|references|summary|about|interests|achievements|certifications)[\s:]|\Z)',
            text,
            re.DOTALL
        )
        exp_section = exp_section_match.group(1).strip() if exp_section_match else text
        entries = re.split(r'\n\s*\n|\n(?=\s*[A-Z][a-zA-Z].*?\s{2,}.*?\d{4})', exp_section)
        for entry in entries:
            entry = entry.strip()
            if not entry or len(entry) < 20:
                continue
            if re.search(r'(email|contact|phone|linkedin|github|@|\+\d|^\s*[A-Z]+\s*$)', entry, re.I):
                continue
            exp = {
                'role': '',
                'organization': '',
                'duration': '',
                'description': []
            }
            lines = [line.strip() for line in entry.split('\n') if line.strip()]
            if not lines:
                continue
            header = lines[0]
            parts = re.split(r'\s{2,}|[|\-]', header)
            parts = [p.strip() for p in parts if p.strip()]
            if len(parts) >= 2:
                exp['role'] = parts[0]
                org_date_part = ' '.join(parts[1:])
                org_date_match = re.search(r'(.+?)\s*[(\[]?(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{1,2}|\d{4})', org_date_part, re.I)
                if org_date_match:
                    exp['organization'] = org_date_match.group(1).strip()
                duration_match = re.search(
                    r'(\(?\s*(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[,.\s-]*(?:\d{4}|\d{1,2})?\s*(?:-|to|–)\s*(?:Present|Now|Current|(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[,.\s-]*(?:\d{4}|\d{1,2})?)\s*\)?|\d{4}\s*(?:-|to|–)\s*(?:Present|Now|Current|\d{4}))',
                    org_date_part,
                    re.I
                )
                if duration_match:
                    exp['duration'] = duration_match.group(1).strip('() ')
            if not exp['organization'] and len(parts) > 0:
                exp['role'] = parts[0]
            if len(lines) > 1:
                exp['description'] = [
                    line.strip('•-* ')
                    for line in lines[1:]
                    if line.strip() and len(line.strip()) > 10
                ]
            if exp['role'] and (exp['organization'] or exp['duration'] or exp['description']):
                experiences.append(exp)
        return experiences
    except Exception as e:
        print(f"Experience extraction error: {str(e)}")
        return []

def extract_projects(resume_text):
    try:
        projects = []
        text = re.sub(r'[–—]', '-', resume_text)
        projects_section_match = re.search(
            r'(?i)Personal Projects\s*\n([\s\S]*?)(?=\n\s*(?:Courses & Certificates|Education|Skills|Experience|Work|Employment|Certificates|Achievements|$))',
            text
        )
        if not projects_section_match:
            return []
        projects_section = projects_section_match.group(1).strip()
        project_entries = re.split(r'\n(?=\S.+?-.+?\(.+?\)\s*\n)', projects_section)
        for entry in project_entries:
            entry = entry.strip()
            if not entry or len(entry) < 30:
                continue
            project = {
                'name': '',
                'technologies': '',
                'description': '',
                'links': []
            }
            lines = [line.strip() for line in entry.split('\n') if line.strip()]
            if lines:
                first_line = lines[0]
                match = re.fullmatch(r'^(.+?)\s*-\s*(.+?)\s*\((.+?)\)\s*$', first_line)
                if not match:
                    continue
                project['name'] = match.group(1).strip()
                project['technologies'] = match.group(3).strip()
                description_lines = [match.group(2).strip()]
            if len(lines) > 1:
                for line in lines[1:]:
                    if re.match(r'^GitHub:', line, re.I):
                        github_match = re.search(r'https?://\S+', line)
                        if github_match:
                            project['links'].append({"GitHub": github_match.group(0)})
                    else:
                        description_lines.append(line)
                project['description'] = ' '.join(description_lines)
                project['description'] = re.sub(r'\s+', ' ', project['description']).strip()
            if project['name'] and project['technologies']:
                projects.append(project)
        return projects
    except Exception as e:
        print(f"Project extraction error: {str(e)}")
        return []

def extract_courses_certificates(resume_text):
    lines = resume_text.splitlines()
    course_lines = []
    capture = False
    section_headers = ['certifications', 'certification', 'courses', 'coursework', 'relevant coursework']
    stop_headers = ['experience', 'education', 'projects', 'skills', 'internship', 'achievements']
    for line in lines:
        line_clean = line.strip()
        line_lower = line_clean.lower()
        if any(header in line_lower for header in section_headers):
            capture = True
            continue
        if any(header in line_lower for header in stop_headers):
            capture = False
        if capture and line_clean:
            course_lines.append(line_clean)
    certificates = []
    for line in course_lines:
        line = re.sub(r'\(.*?\)', '', line)
        line = re.split(r'[-–:|]', line)[0]
        course_name = line.strip()
        if 3 <= len(course_name) <= 100:
            certificates.append(course_name)
    return certificates

def get_entities(text):
    entities = {"PERSON": [], "ORG": [], "DATE": [], "GPE": []}
    try:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text.strip())
    except Exception as e:
        print(f"⚠️ spaCy entity recognition error: {str(e)}")
    return entities

def build_profile(resume_text):
    entities = get_entities(resume_text)
    return {
        "name": extract_name(resume_text, entities, TECH_SKILL_DB),
        "contact": extract_contact_info(resume_text),
        "summary": extract_professional_summary(resume_text),
        "skills": {
            "technical": extract_skills(resume_text, TECH_SKILL_DB),
            "soft": extract_soft_skills(resume_text, SOFT_SKILL_DB)
        },
        "education": extract_education(resume_text),
        "experience": extract_experience(resume_text),
        "projects": extract_projects(resume_text),
        "certifications": extract_courses_certificates(resume_text)
    }

def save_profile_to_file(profile, filename=None):
    try:
        if not filename:
            name = profile.get("name", "unknown").replace(" ", "_").lower()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"resume_profile_{name}_{timestamp}.json"
        if not filename.lower().endswith('.json'):
            filename += '.json'
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        return str(filepath)
    except Exception as e:
        print(f"⚠️ Error saving profile: {str(e)}")
        return None

def print_profile(profile):
    print(json.dumps(profile, indent=2, ensure_ascii=False))

def main():
    if len(sys.argv) < 2:
        print("Usage: python resume_parser_with_subcategories.py <resume_file>")
        return
    file_path = sys.argv[1]
    if file_path.endswith(".pdf"):
        resume_text = read_pdf(file_path)
    elif file_path.endswith(".docx"):
        resume_text = read_docx(file_path)
    else:
        raise ValueError("Unsupported file type. Please provide a PDF or DOCX file.")
    profile = build_profile(resume_text)
    print_profile(profile)
    save_profile_to_file(profile)

if __name__ == "__main__":
    main()