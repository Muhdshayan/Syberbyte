import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import uvicorn
from pydantic import BaseModel, Field
from datetime import datetime

from src.core.models import ModelManager
from src.core.pipeline import ResumePipeline
from src.vectorization.vector_store import VectorStore
from src.matching.job_matcher import JobMatcher, JobDescription
from src.bias_detection.fairness_analyzer import FairnessAnalyzer
from config.settings import settings

# Initialize components
app = FastAPI(title="SmartRecruit AI", version="1.0.0")

# Pydantic models for JSON validation
class ResumeJSON(BaseModel):
    metadata: Dict[str, Any]
    profile: Dict[str, Any]

class JobDescriptionJSON(BaseModel):
    title: str
    level: str = Field(..., pattern="^(Junior|Mid|Senior|Lead)$")
    employment_type: str
    location: str
    location_type: str = "On-site"
    required_skills: Dict[str, int] = Field(..., description="Skill: importance (1-5)")
    min_experience: int = Field(..., ge=0)
    education_level: str
    company_size: str = "Not specified"
    salary_range: List[int] = None
    must_have_keywords: List[str] = []

class BatchProcessRequest(BaseModel):
    resumes: List[ResumeJSON]
    job_description: JobDescriptionJSON

# Global instances
model_manager = None
pipeline = None
vector_store = None
job_matcher = None
fairness_analyzer = None

@app.on_event("startup")
async def startup_event():
    """Initialize all components on startup"""
    global model_manager, pipeline, vector_store, job_matcher, fairness_analyzer
    
    print("Loading models...")
    model_manager = ModelManager(settings)
    
    print("Initializing vector store...")
    vector_store = VectorStore(settings)
    
    print("Setting up pipeline...")
    pipeline = ResumePipeline(model_manager, vector_store)
    
    print("Initializing job matcher...")
    job_matcher = JobMatcher(vector_store, model_manager)
    
    print("Setting up fairness analyzer...")
    fairness_analyzer = FairnessAnalyzer(settings)
    
    print("SmartRecruit AI ready!")

@app.get("/")
async def root():
    return {"message": "SmartRecruit AI API", "status": "operational"}

@app.post("/api/process-resume")
async def process_resume(resume: ResumeJSON):
    """Process a single resume from JSON"""
    try:
        # Process through pipeline
        candidate_profile = await pipeline.process_resume(resume.dict())
        
        return {
            "status": "success",
            "candidate_id": f"candidate_{candidate_profile.name.replace(' ', '_')}_{datetime.now().timestamp()}",
            "profile": {
                "name": candidate_profile.name,
                "contact": candidate_profile.contact,
                "technical_skills": candidate_profile.raw_data['profile']['skills']['technical'],
                "experience_years": len(candidate_profile.raw_data['profile'].get('experience', [])) * 2,
                "education": candidate_profile.raw_data['profile'].get('education', []),
                "vectors_generated": True,
                "metadata": candidate_profile.metadata
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-batch")
async def process_batch(resumes: List[ResumeJSON]):
    """Process multiple resumes in batch"""
    try:
        results = []
        
        for resume in resumes:
            try:
                candidate_profile = await pipeline.process_resume(resume.dict())
                results.append({
                    "status": "success",
                    "name": candidate_profile.name,
                    "candidate_id": f"candidate_{candidate_profile.name.replace(' ', '_')}_{datetime.now().timestamp()}"
                })
            except Exception as e:
                results.append({
                    "status": "error",
                    "name": resume.profile.get('name', 'Unknown'),
                    "error": str(e)
                })
        
        return {
            "status": "success",
            "processed": len(results),
            "successful": sum(1 for r in results if r['status'] == 'success'),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/match-job")
async def match_job(job_description: JobDescriptionJSON):
    """Match job to candidates in the database"""
    try:
        # Create JobDescription object
        job = JobDescription(
            title=job_description.title,
            level=job_description.level,
            employment_type=job_description.employment_type,
            location=job_description.location,
            location_type=job_description.location_type,
            required_skills=job_description.required_skills,
            min_experience=job_description.min_experience,
            education_level=job_description.education_level,
            company_size=job_description.company_size,
            salary_range=tuple(job_description.salary_range) if job_description.salary_range else None,
            must_have_keywords=job_description.must_have_keywords
        )
        
        # Find matching candidates
        matches = await job_matcher.match_job_to_candidates(job, top_k=20)
        
        # Analyze fairness
        fairness_analysis = await fairness_analyzer.analyze_candidate_pool(
            matches, job_description.dict()
        )
        
        # Format results
        formatted_matches = []
        for match in matches[:10]:  # Top 10
            candidate_data = match['candidate']['data']['profile']
            formatted_matches.append({
                "candidate_id": match['candidate']['id'],
                "name": candidate_data['name'],
                "score": round(match['total_score'], 2),
                "score_breakdown": {
                    "skill_match": round(match['score_breakdown']['skill_match'], 2),
                    "experience_match": round(match['score_breakdown']['experience_match'], 2),
                    "level_match": round(match['score_breakdown']['level_match'], 2),
                    "keyword_match": round(match['score_breakdown']['keyword_match'], 2),
                    "education_match": round(match['score_breakdown']['education_match'], 2)
                },
                "match_reasons": match['match_reasons'],
                "missing_skills": match['missing_skills'],
                "contact": candidate_data.get('contact', {})
            })
        
        return {
            "status": "success",
            "job_title": job.title,
            "total_candidates_evaluated": len(matches),
            "matches": formatted_matches,
            "fairness_analysis": {
                "bias_detected": len(fairness_analysis['recommendations']) > 0,
                "selection_rates": fairness_analysis['selection_rates'],
                "recommendations": fairness_analysis['recommendations'][:3],
                "report_generated": True
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/match-and-rank")
async def match_and_rank(request: BatchProcessRequest):
    """Process resumes and immediately match against a job"""
    try:
        # First, process all resumes
        processed_candidates = []
        for resume in request.resumes:
            candidate_profile = await pipeline.process_resume(resume.dict())
            processed_candidates.append(candidate_profile)
        
        # Then match against the job
        job = JobDescription(
            title=request.job_description.title,
            level=request.job_description.level,
            employment_type=request.job_description.employment_type,
            location=request.job_description.location,
            location_type=request.job_description.location_type,
            required_skills=request.job_description.required_skills,
            min_experience=request.job_description.min_experience,
            education_level=request.job_description.education_level,
            company_size=request.job_description.company_size,
            salary_range=tuple(request.job_description.salary_range) if request.job_description.salary_range else None,
            must_have_keywords=request.job_description.must_have_keywords
        )
        
        # Get matches
        matches = await job_matcher.match_job_to_candidates(job, top_k=len(processed_candidates))
        
        # Analyze fairness
        fairness_analysis = await fairness_analyzer.analyze_candidate_pool(
            matches, request.job_description.dict()
        )
        
        return {
            "status": "success",
            "job_title": job.title,
            "candidates_processed": len(processed_candidates),
            "ranking": [
                {
                    "rank": idx + 1,
                    "name": match['candidate']['data']['profile']['name'],
                    "score": round(match['total_score'], 2),
                    "match_percentage": f"{match['total_score']:.0f}%",
                    "strengths": match['match_reasons'],
                    "gaps": match['missing_skills']
                }
                for idx, match in enumerate(matches[:10])
            ],
            "fairness_summary": {
                "analysis_complete": True,
                "issues_found": len(fairness_analysis['recommendations']),
                "recommendations": fairness_analysis['recommendations']
            }
        }
        
@app.post("/api/match-candidate-to-all-jobs")
async def match_candidate_to_all_jobs(candidate_id: str):
    """Match a single candidate against all available job descriptions"""
    try:
        # Get candidate from database
        candidate_data = await vector_store.get_candidate_by_id(candidate_id)
        if not candidate_data:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Get all active job descriptions from storage
        all_jobs = await get_all_active_jobs()
        
        results = []
        for job_data in all_jobs:
            job = JobDescription(**job_data)
            
            # Calculate match score
            match_result = await job_matcher.calculate_single_match(
                candidate_data, job
            )
            
            results.append({
                "job_id": job_data.get('id', f"job_{hash(job.title)}"),
                "job_title": job.title,
                "company": job.company_size,
                "location": job.location,
                "location_type": job.location_type,
                "match_percentage": round(match_result['total_score'], 1),
                "score_breakdown": {
                    "skills": round(match_result['skill_match'], 1),
                    "experience": round(match_result['experience_match'], 1),
                    "level": round(match_result['level_match'], 1)
                },
                "fit_level": _categorize_fit(match_result['total_score']),
                "missing_skills": match_result['missing_skills'][:3]  # Top 3
            })
        
        # Sort by match percentage
        results.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return {
            "status": "success",
            "candidate_name": candidate_data['profile']['name'],
            "total_jobs_evaluated": len(results),
            "job_matches": results,
            "summary": {
                "excellent_matches": sum(1 for r in results if r['match_percentage'] >= 85),
                "good_matches": sum(1 for r in results if 70 <= r['match_percentage'] < 85),
                "fair_matches": sum(1 for r in results if 50 <= r['match_percentage'] < 70),
                "poor_matches": sum(1 for r in results if r['match_percentage'] < 50)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/match-all-candidates-to-job")
async def match_all_candidates_to_job(job_description: JobDescriptionJSON):
    """Match all candidates in database to a specific job"""
    try:
        job = JobDescription(
            title=job_description.title,
            level=job_description.level,
            employment_type=job_description.employment_type,
            location=job_description.location,
            location_type=job_description.location_type,
            required_skills=job_description.required_skills,
            min_experience=job_description.min_experience,
            education_level=job_description.education_level,
            company_size=job_description.company_size,
            salary_range=tuple(job_description.salary_range) if job_description.salary_range else None,
            must_have_keywords=job_description.must_have_keywords
        )
        
        # Get all candidates
        all_candidates = await vector_store.get_all_candidates()
        
        # Calculate matches
        matches = []
        for candidate in all_candidates:
            match_result = await job_matcher.calculate_single_match(
                candidate, job
            )
            
            matches.append({
                "candidate_id": candidate['id'],
                "name": candidate['profile']['name'],
                "match_percentage": round(match_result['total_score'], 1),
                "fit_level": _categorize_fit(match_result['total_score']),
                "key_strengths": match_result['match_reasons'][:2],
                "main_gaps": match_result['missing_skills'][:2]
            })
        
        # Sort by match percentage
        matches.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return {
            "status": "success",
            "job_title": job.title,
            "candidates_evaluated": len(matches),
            "top_matches": matches[:10],  # Top 10
            "distribution": {
                "90_100": sum(1 for m in matches if m['match_percentage'] >= 90),
                "80_89": sum(1 for m in matches if 80 <= m['match_percentage'] < 90),
                "70_79": sum(1 for m in matches if 70 <= m['match_percentage'] < 80),
                "60_69": sum(1 for m in matches if 60 <= m['match_percentage'] < 70),
                "below_60": sum(1 for m in matches if m['match_percentage'] < 60)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/create-job-listing")
async def create_job_listing(job_description: JobDescriptionJSON):
    """Store a new job description in the system"""
    try:
        job_id = f"job_{job_description.title.replace(' ', '_')}_{datetime.now().timestamp()}"
        
        # Store job description
        await store_job_description(job_id, job_description.dict())
        
        return {
            "status": "success",
            "job_id": job_id,
            "message": "Job listing created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/get-all-jobs")
async def get_all_jobs():
    """Retrieve all active job listings"""
    try:
        jobs = await get_all_active_jobs()
        
        return {
            "status": "success",
            "total_jobs": len(jobs),
            "jobs": [
                {
                    "job_id": job.get('id'),
                    "title": job['title'],
                    "level": job['level'],
                    "location": job['location'],
                    "location_type": job['location_type'],
                    "required_skills": list(job['required_skills'].keys()),
                    "min_experience": job['min_experience']
                }
                for job in jobs
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _categorize_fit(score: float) -> str:
    """Categorize match fit level"""
    if score >= 85:
        return "Excellent Fit"
    elif score >= 70:
        return "Good Fit"
    elif score >= 50:
        return "Fair Fit"
    else:
        return "Poor Fit"

# Helper functions for job storage
async def store_job_description(job_id: str, job_data: dict):
    """Store job description in database"""
    # Implement storage logic - could be file-based or database
    import json
    from pathlib import Path
    
    job_file = Path(f"data/job_descriptions/{job_id}.json")
    job_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(job_file, 'w') as f:
        json.dump({
            'id': job_id,
            'created_at': datetime.now().isoformat(),
            **job_data
        }, f, indent=2)

async def get_all_active_jobs() -> List[dict]:
    """Retrieve all active job descriptions"""
    import json
    from pathlib import Path
    
    jobs = []
    job_dir = Path("data/job_descriptions")
    
    if job_dir.exists():
        for job_file in job_dir.glob("*.json"):
            with open(job_file, 'r') as f:
                jobs.append(json.load(f))
    
    return jobs
async def get_fairness_report():
    """Get comprehensive fairness report"""
    try:
        report = fairness_analyzer.generate_fairness_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/statistics")
async def get_statistics():
    """Get system statistics"""
    try:
        # Get counts from vector store
        candidate_count = vector_store.collection.count()
        
        return {
            "total_candidates": candidate_count,
            "models_loaded": list(model_manager.models.keys()),
            "system_status": "operational",
            "vector_dimensions": settings.EMBEDDING_DIM * 4  # 4 vector types
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )