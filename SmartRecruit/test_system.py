#!/usr/bin/env python3
"""
Test script for SmartRecruit AI with sample data
"""
import requests
import json
from typing import Dict, List

API_BASE = "http://localhost:8000"

def test_laiba_khan_resume():
    """Test with Laiba Khan's resume data"""
    
    # Laiba Khan's resume in JSON format
    laiba_resume = {
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
                "technical": [
                    "pandas", "react", "django", "css", "sql", "postgresql",
                    "scikit-learn", "firebase", "c", "mysql", "javascript",
                    "langchain", "machine learning", "python", "html", "unity",
                    "ml", "mongodb", "nlp", "nltk"
                ],
                "soft": ["collaboration"]
            },
            "education": [
                {
                    "degree": "",
                    "institution": "Bachelor's in Computer Science FAST - National University of Computer and Emerging Sciences (NUCES)",
                    "year": "2022 - Present"
                },
                {
                    "degree": "",
                    "institution": "O-Levels (Computer Science) - The City School.",
                    "year": "2017 - 2020"
                }
            ],
            "experience": [
                {
                    "role": "Software Engineering Intern",
                    "organization": "Headstarter",
                    "duration": "",
                    "description": [
                        "Developed and optimized frontend components using React, Next.js, HTML, CSS, and JavaScript",
                        "Integrated RESTful APIs to fetch and display dynamic data efficiently",
                        "Improved website performance and responsiveness, ensuring cross-browser compatibility"
                    ]
                },
                {
                    "role": "Game Development Intern",
                    "organization": "Mindstorm Studios",
                    "duration": "",
                    "description": [
                        "Designed and implemented game mechanics using Unity and C#",
                        "Developed interactive UI components and optimized game performance",
                        "Integrated physics-based animations and gameplay logic"
                    ]
                }
            ],
            "projects": [
                {
                    "name": "PersonPicks",
                    "technologies": "Django, PostgreSQL, React, Railway, Vercel",
                    "description": "Movie & Book Recommendation System Developed a full-stack web application that suggests movies and books based on users' MBTI type. The platform enables users to connect, follow others, and view their watchlist/readlist items, providing a personalized recommendation experience.",
                    "links": [{"GitHub": "https://github.com/laibak24/personapicks2.0"}]
                },
                {
                    "name": "Slogan Quality Predictor",
                    "technologies": "Python, Machine Learning, NLP, Streamlit",
                    "description": "AI-Based Slogan Evaluation Built an AI-powered tool that evaluates the memorability and effectiveness of slogans based on multiple linguistic and psychological factors. The model assigns a quality score to slogans, assisting in branding and marketing strategies.",
                    "links": [{"GitHub": "https://github.com/laibak24/slogan-quality-predictor"}]
                },
                {
                    "name": "Hate Speech Detection",
                    "technologies": "Python, NLP, Scikit-Learn, Pandas, NLTK",
                    "description": "Sentiment Analysis on Twitter Data Developed a machine learning model for hate speech classification using sentiment analysis on Twitter data. The system utilizes NLP techniques to detect and categorize offensive language, helping in social media content moderation.",
                    "links": [{"GitHub": "https://github.com/laibak24/Hate-Speech-Detection-Using-NLP-Machine-Learning"}]
                }
            ],
            "certifications": [],
            "entities": {
                "PERSON": ["Laiba Khan"],
                "ORG": ["FAST", "Headstarter", "Mindstorm Studios"],
                "DATE": ["2022", "2020", "2017"]
            }
        }
    }
    
    # Process the resume
    print("📄 Processing Laiba Khan's resume...")
    response = requests.post(f"{API_BASE}/api/process-resume", json=laiba_resume)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Resume processed successfully!")
        print(f"   Candidate ID: {result['candidate_id']}")
        print(f"   Skills: {len(result['profile']['technical_skills'])} technical skills identified")
    else:
        print(f"❌ Error: {response.json()}")
    
    return laiba_resume

def test_job_matching(job_descriptions: List[Dict]):
    """Test job matching with multiple job descriptions"""
    
    for job in job_descriptions:
        print(f"\n🎯 Matching for: {job['title']}")
        response = requests.post(f"{API_BASE}/api/match-job", json=job)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {len(result['matches'])} matches")
            
            # Show top 3 matches
            for i, match in enumerate(result['matches'][:3], 1):
                print(f"\n   #{i} {match['name']} - Score: {match['score']}%")
                print(f"      Strengths: {', '.join(match['match_reasons'][:2])}")
                if match['missing_skills']:
                    print(f"      Missing: {', '.join(match['missing_skills'][:3])}")
            
            # Show fairness analysis
            if result['fairness_analysis']['bias_detected']:
                print(f"\n   ⚠️  Bias Detection: Issues found")
                for rec in result['fairness_analysis']['recommendations']:
                    print(f"      - {rec['issue']}: {rec['action']}")
        else:
            print(f"❌ Error: {response.json()}")

def test_multi_job_matching():
    """Test matching a candidate against multiple jobs"""
    print("\n\n🎯 Testing Multi-Job Matching...")
    
    # First, create multiple job listings
    jobs_to_create = [
        {
            "title": "Full Stack Developer",
            "level": "Mid",
            "employment_type": "Full-time",
            "location": "Karachi, Pakistan",
            "location_type": "Hybrid",
            "required_skills": {
                "React": 5,
                "Django": 5,
                "PostgreSQL": 4,
                "JavaScript": 4,
                "Python": 5
            },
            "min_experience": 2,
            "education_level": "Bachelor's in Computer Science",
            "must_have_keywords": ["React", "Django"]
        },
        {
            "title": "Machine Learning Engineer",
            "level": "Junior",
            "employment_type": "Full-time",
            "location": "Remote",
            "location_type": "Remote",
            "required_skills": {
                "Python": 5,
                "Machine Learning": 5,
                "NLP": 4,
                "scikit-learn": 4,
                "pandas": 3
            },
            "min_experience": 1,
            "education_level": "Bachelor's in CS or related field",
            "must_have_keywords": ["ML", "NLP"]
        },
        {
            "title": "Frontend Developer",
            "level": "Junior",
            "employment_type": "Full-time",
            "location": "Islamabad, Pakistan",
            "location_type": "On-site",
            "required_skills": {
                "React": 5,
                "JavaScript": 5,
                "HTML": 4,
                "CSS": 4,
                "TypeScript": 3
            },
            "min_experience": 1,
            "education_level": "Bachelor's degree",
            "must_have_keywords": ["React", "JavaScript"]
        },
        {
            "title": "Data Scientist",
            "level": "Mid",
            "employment_type": "Full-time",
            "location": "Lahore, Pakistan",
            "location_type": "Hybrid",
            "required_skills": {
                "Python": 5,
                "pandas": 5,
                "scikit-learn": 4,
                "SQL": 4,
                "Machine Learning": 5
            },
            "min_experience": 3,
            "education_level": "Bachelor's in CS, Statistics, or related",
            "must_have_keywords": ["Data Science", "ML"]
        },
        {
            "title": "Django Backend Developer",
            "level": "Mid",
            "employment_type": "Contract",
            "location": "Remote",
            "location_type": "Remote",
            "required_skills": {
                "Django": 5,
                "Python": 5,
                "PostgreSQL": 4,
                "REST API": 5,
                "Redis": 3
            },
            "min_experience": 3,
            "education_level": "Bachelor's degree or equivalent",
            "must_have_keywords": ["Django", "REST API"]
        }
    ]
    
    # Create job listings
    for job in jobs_to_create:
        response = requests.post(f"{API_BASE}/api/create-job-listing", json=job)
        if response.status_code == 200:
            print(f"✅ Created job listing: {job['title']}")
    
    # Now match Laiba against all jobs
    # Assume we have Laiba's candidate_id from previous test
    candidate_id = "candidate_Laiba_Khan_12345"  # This would come from actual processing
    
    response = requests.post(
        f"{API_BASE}/api/match-candidate-to-all-jobs",
        params={"candidate_id": candidate_id}
    )
    
    if response.status_code == 200:
        results = response.json()
        print(f"\n📊 Match Results for {results['candidate_name']}:")
        print(f"   Total jobs evaluated: {results['total_jobs_evaluated']}")
        print(f"\n   Summary:")
        print(f"   - Excellent matches (85%+): {results['summary']['excellent_matches']}")
        print(f"   - Good matches (70-84%): {results['summary']['good_matches']}")
        print(f"   - Fair matches (50-69%): {results['summary']['fair_matches']}")
        print(f"   - Poor matches (<50%): {results['summary']['poor_matches']}")
        
        print(f"\n   Top Job Matches:")
        for idx, job_match in enumerate(results['job_matches'][:5], 1):
            print(f"\n   {idx}. {job_match['job_title']}")
            print(f"      Match: {job_match['match_percentage']}% ({job_match['fit_level']})")
            print(f"      Location: {job_match['location']} ({job_match['location_type']})")
            print(f"      Skills: {job_match['score_breakdown']['skills']}%")
            print(f"      Experience: {job_match['score_breakdown']['experience']}%")
            if job_match['missing_skills']:
                print(f"      Missing: {', '.join(job_match['missing_skills'])}")
    else:
        print(f"❌ Error: {response.text}")

def main():
    """Run all tests"""
    
    print("🚀 SmartRecruit AI Test Suite")
    print("=" * 50)
    
    # Test 1: Process Laiba's resume
    laiba_resume = test_laiba_khan_resume()
    
    # Test 2: Create sample job descriptions
    job_descriptions = [
        {
            "title": "Full Stack Developer",
            "level": "Mid",
            "employment_type": "Full-time",
            "location": "Karachi, Pakistan",
            "location_type": "Hybrid",
            "required_skills": {
                "React": 5,
                "Django": 5,
                "PostgreSQL": 4,
                "JavaScript": 4,
                "Python": 5
            },
            "min_experience": 2,
            "education_level": "Bachelor's in Computer Science",
            "must_have_keywords": ["React", "Django", "REST API"]
        },
        {
            "title": "Machine Learning Engineer",
            "level": "Junior",
            "employment_type": "Full-time",
            "location": "Remote",
            "location_type": "Remote",
            "required_skills": {
                "Python": 5,
                "Machine Learning": 5,
                "NLP": 4,
                "scikit-learn": 4,
                "pandas": 3
            },
            "min_experience": 1,
            "education_level": "Bachelor's in CS or related field",
            "must_have_keywords": ["ML", "NLP", "Python"]
        },
        {
            "title": "Game Developer",
            "level": "Junior",
            "employment_type": "Full-time",
            "location": "Islamabad, Pakistan",
            "location_type": "On-site",
            "required_skills": {
                "Unity": 5,
                "C#": 5,
                "Game Development": 4,
                "UI/UX": 3
            },
            "min_experience": 1,
            "education_level": "Bachelor's degree",
            "must_have_keywords": ["Unity", "Game Development"]
        }
    ]
    
    # Test job matching
    test_job_matching(job_descriptions)
    
    # Test 3: Multi-job matching
    test_multi_job_matching()
    
    # Test 4: Batch processing
    print("\n\n📦 Testing batch processing...")
    
    # Create variations of resumes for testing
    resumes_batch = [laiba_resume]  # Add more resumes here
    
    batch_request = {
        "resumes": resumes_batch,
        "job_description": job_descriptions[0]  # Match against Full Stack role
    }
    
    response = requests.post(f"{API_BASE}/api/match-and-rank", json=batch_request)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Batch processing complete!")
        print(f"   Processed: {result['candidates_processed']} candidates")
        print(f"   Top match: {result['ranking'][0]['name']} ({result['ranking'][0]['match_percentage']})")
    
    # Test 5: Get statistics
    print("\n\n📊 System Statistics:")
    stats = requests.get(f"{API_BASE}/api/statistics").json()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test 6: Fairness report
    print("\n\n📈 Fairness Report:")
    report = requests.get(f"{API_BASE}/api/fairness-report").json()
    if "summary" in report:
        print(f"   Jobs analyzed: {report['summary']['total_jobs_analyzed']}")
        print(f"   Candidates reviewed: {report['summary']['total_candidates_reviewed']}")

if __name__ == "__main__":
    main()