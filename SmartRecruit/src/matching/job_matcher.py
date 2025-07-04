from typing import Dict, List, Tuple
import numpy as np
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import re

@dataclass
class JobDescription:
    title: str
    level: str
    employment_type: str
    location: str
    location_type: str  # Remote/On-site/Hybrid
    required_skills: Dict[str, int]  # skill: importance (1-5)
    min_experience: int
    education_level: str
    company_size: str = "Not specified"
    salary_range: Tuple[int, int] = None
    must_have_keywords: List[str] = None

class JobMatcher:
    def __init__(self, vector_store, model_manager):
        self.vector_store = vector_store
        self.model_manager = model_manager
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
    
    async def match_job_to_candidates(self, job: JobDescription, 
                                    top_k: int = 20) -> List[Dict]:
        """Match job description to candidates"""
        # Generate job vector
        job_vector = await self._vectorize_job(job)
        
        # Search candidates
        filters = {
            'min_experience': job.min_experience,
            'required_skills': ','.join(job.required_skills.keys())
        }
        
        candidates = await self.vector_store.search_candidates(
            job_vector, k=top_k * 2, filters=filters
        )
        
        # Score and rank candidates
        scored_candidates = []
        for candidate in candidates:
            score_details = await self._calculate_match_score(candidate, job)
            scored_candidates.append({
                'candidate': candidate,
                'total_score': score_details['total'],
                'score_breakdown': score_details,
                'match_reasons': self._generate_match_reasons(score_details),
                'missing_skills': score_details['missing_skills']
            })
        
        # Sort by total score
        scored_candidates.sort(key=lambda x: x['total_score'], reverse=True)
        
        return scored_candidates[:top_k]
    
    async def calculate_single_match(self, candidate: Dict, 
                                   job: JobDescription) -> Dict:
        """Calculate match score for a single candidate-job pair"""
        # Create a match structure similar to search results
        candidate_wrapper = {
            'id': candidate.get('id', 'unknown'),
            'data': candidate.get('profile', candidate),
            'metadata': candidate.get('metadata', {})
        }
        
        # Calculate detailed match score
        score_details = await self._calculate_match_score(
            {'candidate': candidate_wrapper}, job
        )
        
        # Generate match reasons
        match_reasons = self._generate_match_reasons(score_details)
        
        return {
            'total_score': score_details['total'],
            'skill_match': score_details['skill_match'],
            'experience_match': score_details['experience_match'],
            'level_match': score_details['level_match'],
            'keyword_match': score_details['keyword_match'],
            'education_match': score_details['education_match'],
            'missing_skills': score_details['missing_skills'],
            'match_reasons': match_reasons
        }
    
    async def _vectorize_job(self, job: JobDescription) -> np.ndarray:
        """Convert job description to vector"""
        # Create comprehensive job text
        job_text = f"""
        {job.title} {job.level}
        Required skills: {', '.join([f"{skill} (importance: {imp})" for skill, imp in job.required_skills.items()])}
        Experience: {job.min_experience}+ years
        Education: {job.education_level}
        {' '.join(job.must_have_keywords or [])}
        """
        
        # Use Mistral for enhanced understanding
        prompt = f"""<s>[INST] Create a comprehensive profile for this job:
        {job_text}
        
        Include: required expertise, team fit, growth opportunities, and key responsibilities.
        [/INST]"""
        
        enhanced_description = self.model_manager.inference_mistral(prompt, 512)
        
        # Combine and encode
        full_text = job_text + " " + enhanced_description
        job_vector = self.encoder.encode(full_text)
        
        return job_vector
    
    async def _calculate_match_score(self, candidate: Dict, 
                                   job: JobDescription) -> Dict:
        """Calculate detailed match score"""
        scores = {
            'skill_match': 0,
            'experience_match': 0,
            'level_match': 0,
            'keyword_match': 0,
            'education_match': 0,
            'missing_skills': [],
            'total': 0
        }
        
        candidate_data = candidate['data']['profile']
        
        # 1. Skill matching (40% weight)
        candidate_skills = set(candidate_data.get('skills', {}).get('technical', []))
        skill_score = 0
        max_skill_score = 0
        
        for skill, importance in job.required_skills.items():
            max_skill_score += importance
            if any(skill.lower() in cs.lower() for cs in candidate_skills):
                skill_score += importance
            else:
                scores['missing_skills'].append(skill)
        
        scores['skill_match'] = (skill_score / max_skill_score * 40) if max_skill_score > 0 else 0
        
        # 2. Experience matching (25% weight)
        candidate_exp = self._extract_experience_years(candidate_data)
        if candidate_exp >= job.min_experience:
            scores['experience_match'] = 25
        else:
            scores['experience_match'] = (candidate_exp / job.min_experience) * 25
        
        # 3. Level matching (15% weight)
        candidate_level = self._determine_level(candidate_data)
        if candidate_level == job.level:
            scores['level_match'] = 15
        elif abs(self._level_to_num(candidate_level) - self._level_to_num(job.level)) == 1:
            scores['level_match'] = 10
        else:
            scores['level_match'] = 5
        
        # 4. Keyword matching (10% weight)
        if job.must_have_keywords:
            keyword_matches = sum(
                1 for keyword in job.must_have_keywords
                if self._keyword_in_resume(keyword, candidate_data)
            )
            scores['keyword_match'] = (keyword_matches / len(job.must_have_keywords)) * 10
        else:
            scores['keyword_match'] = 10
        
        # 5. Education matching (10% weight)
        if self._education_meets_requirement(candidate_data, job.education_level):
            scores['education_match'] = 10
        else:
            scores['education_match'] = 5
        
        # Calculate total
        scores['total'] = sum([
            scores['skill_match'],
            scores['experience_match'],
            scores['level_match'],
            scores['keyword_match'],
            scores['education_match']
        ])
        
        return scores
    
    def _generate_match_reasons(self, scores: Dict) -> List[str]:
        """Generate human-readable match reasons"""
        reasons = []
        
        if scores['skill_match'] >= 30:
            reasons.append("Strong technical skill alignment")
        elif scores['skill_match'] >= 20:
            reasons.append("Good technical skill match")
        
        if scores['experience_match'] >= 20:
            reasons.append("Meets experience requirements")
        
        if scores['level_match'] >= 12:
            reasons.append("Appropriate seniority level")
        
        if scores['keyword_match'] >= 8:
            reasons.append("Contains important keywords")
        
        if not scores['missing_skills']:
            reasons.append("Has all required skills")
        elif len(scores['missing_skills']) <= 2:
            reasons.append("Missing only minor skills")
        
        return reasons
    
    def _extract_experience_years(self, candidate_data: Dict) -> int:
        """Extract years of experience"""
        # Look for experience section
        experience = candidate_data.get('experience', [])
        
        # Simple calculation - enhance this
        total_years = 0
        for exp in experience:
            # Try to parse duration
            duration = exp.get('duration', '')
            # Add logic to parse duration strings
            total_years += 2  # Placeholder
        
        return total_years
    
    def _determine_level(self, candidate_data: Dict) -> str:
        """Determine candidate level"""
        exp_years = self._extract_experience_years(candidate_data)
        
        if exp_years < 2:
            return "Junior"
        elif exp_years < 5:
            return "Mid"
        elif exp_years < 8:
            return "Senior"
        else:
            return "Lead"
    
    def _level_to_num(self, level: str) -> int:
        """Convert level to numeric for comparison"""
        levels = {"Junior": 1, "Mid": 2, "Senior": 3, "Lead": 4}
        return levels.get(level, 2)
    
    def _keyword_in_resume(self, keyword: str, candidate_data: Dict) -> bool:
        """Check if keyword exists in resume"""
        # Search in all text fields
        text_to_search = []
        
        # Add skills
        text_to_search.extend(candidate_data.get('skills', {}).get('technical', []))
        
        # Add experience descriptions
        for exp in candidate_data.get('experience', []):
            text_to_search.extend(exp.get('description', []))
        
        # Add project descriptions
        for proj in candidate_data.get('projects', []):
            text_to_search.append(proj.get('description', ''))
        
        full_text = ' '.join(text_to_search).lower()
        return keyword.lower() in full_text
    
    def _education_meets_requirement(self, candidate_data: Dict, 
                                   required: str) -> bool:
        """Check if education meets requirements"""
        education = candidate_data.get('education', [])
        
        # Simple check - enhance this
        for edu in education:
            if 'bachelor' in edu.get('degree', '').lower():
                return True
            if 'bachelor' in edu.get('institution', '').lower():
                return True
        
        return False