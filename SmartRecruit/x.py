import requests
import json

# Example 1: Process a single resume (JSON format)
resume_json = {
    "metadata": {
        "parser_version": "1.2",
        "parsed_at": "2025-06-30T16:37:20.469562",
        "status": "success"
    },
    "profile": {
        "name": "Laiba Khan",
        "contact": {
            "phone": "+92 335 2036450",
            "email": "klaiba2406@gmail.com",
            "linkedin": "https://www.linkedin.com/in/laibakha",
            "github": "https://github.com/laibak24"
        },
        "skills": {
            "technical": ["React", "Django", "Python", "ML", "PostgreSQL", "JavaScript"],
            "soft": ["collaboration", "problem-solving"]
        },
        "education": [
            {
                "degree": "Bachelor's in Computer Science",
                "institution": "FAST - National University",
                "year": "2022 - Present"
            }
        ],
        "experience": [
            {
                "role": "Software Engineering Intern",
                "organization": "Headstarter",
                "description": [
                    "Developed frontend components using React",
                    "Integrated RESTful APIs"
                ]
            }
        ],
        "projects": [
            {
                "name": "PersonPicks",
                "technologies": "Django, PostgreSQL, React",
                "description": "Movie & Book Recommendation System"
            }
        ]
    }
}

# Process single resume
response = requests.post(
    'http://localhost:8000/api/process-resume',
    json=resume_json
)
print(response.json())

# Example 2: Batch process multiple resumes
batch_resumes = [resume_json, resume_json2, resume_json3]  # Multiple resumes

response = requests.post(
    'http://localhost:8000/api/process-batch',
    json=batch_resumes
)
print(f"Processed {response.json()['successful']} resumes successfully")

# Example 3: Match job with detailed requirements
job_description = {
    "title": "Senior Full Stack Developer",
    "level": "Senior",
    "employment_type": "Full-time",
    "location": "San Francisco, CA",
    "location_type": "Hybrid",
    "required_skills": {
        "React": 5,        # 5/5 importance
        "Django": 4,       # 4/5 importance
        "PostgreSQL": 3,   # 3/5 importance
        "TypeScript": 4,
        "Docker": 3
    },
    "min_experience": 5,
    "education_level": "Bachelor's in CS or equivalent",
    "company_size": "Startup",
    "salary_range": [120000, 180000],
    "must_have_keywords": ["React", "Django", "REST API"]
}

response = requests.post(
    'http://localhost:8000/api/match-job',
    json=job_description
)

# Display results
matches = response.json()
for idx, match in enumerate(matches['matches']):
    print(f"\nRank {idx+1}: {match['name']}")
    print(f"  Score: {match['score']}%")
    print(f"  Strengths: {', '.join(match['match_reasons'])}")
    if match['missing_skills']:
        print(f"  Missing: {', '.join(match['missing_skills'])}")

# Example 4: Process and match in one request
batch_request = {
    "resumes": [resume_json1, resume_json2, resume_json3],
    "job_description": job_description
}

response = requests.post(
    'http://localhost:8000/api/match-and-rank',
    json=batch_request
)

# Example 5: Get system statistics
stats = requests.get('http://localhost:8000/api/statistics').json()
print(f"Total candidates in database: {stats['total_candidates']}")
print(f"Models loaded: {', '.join(stats['models_loaded'])}")