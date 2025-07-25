import json
import numpy as np
import torch
from typing import Dict, List, Tuple, Any, Optional
import re
from collections import defaultdict
import logging
from dataclasses import dataclass, asdict
from sentence_transformers import SentenceTransformer
import onnxruntime as ort
from llama_cpp import Llama
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import uuid
import os
import time
from datetime import datetime
import warnings
import requests
import glob
warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MatchingResult:
    candidate_name: str
    job_title: str
    overall_score: float
    skill_confidence_score: float
    important_skills_score: float
    relevancy_score: float
    detailed_breakdown: Dict[str, Any]
    
    def to_dict(self):
        """Convert MatchingResult to dictionary for JSON serialization"""
        return asdict(self)

class DynamicSkillSynonymMapper:
    
    def __init__(self, mistral_model=None, ollama_url: str = "http://localhost:11434"):
        self.mistral_model = mistral_model
        self.ollama_url = ollama_url
        self.synonym_cache = {}
        self.relevancy_cache = {}
        
    def _call_ollama_api(self, prompt: str, model: str = "mistral") -> str:
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "num_predict": 200
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.warning(f"Ollama API error: {response.status_code}")
                return ""
                
        except requests.exceptions.ConnectionError:
            logger.warning("Ollama server not accessible, falling back to local model")
            return self._fallback_to_local_model(prompt)
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return ""
    
    def _fallback_to_local_model(self, prompt: str) -> str:
        if self.mistral_model:
            try:
                response = self.mistral_model(
                    prompt,
                    max_tokens=200,
                    temperature=0.1,
                    stop=["</s>", "\n\n"]
                )
                return response['choices'][0]['text'].strip()
            except Exception as e:
                logger.error(f"Error with local Mistral model: {e}")
                return ""
        return ""
    
    def get_career_field_from_job(self, job_description: Dict) -> str:
        title = job_description.get('title', '').lower()
        skills = job_description.get('required_skills', {})
        
        
        if any(term in title for term in ['data', 'scientist', 'analyst', 'ml', 'ai']):
            return "data science"
        elif any(term in title for term in ['developer', 'engineer', 'programmer', 'software']):
            return "software development"
        elif any(term in title for term in ['marketing', 'brand', 'digital', 'social media']):
            return "marketing"
        elif any(term in title for term in ['designer', 'ui', 'ux', 'graphic', 'creative']):
            return "design"
        elif any(term in title for term in ['finance', 'accounting', 'financial', 'analyst']):
            return "finance"
        elif any(term in title for term in ['hr', 'human resources', 'recruitment', 'talent']):
            return "human resources"
        elif any(term in title for term in ['sales', 'business development', 'account']):
            return "sales"
        elif any(term in title for term in ['project manager', 'product manager', 'scrum']):
            return "project management"
        elif any(term in title for term in ['devops', 'infrastructure', 'cloud', 'system admin']):
            return "devops"
        elif any(term in title for term in ['security', 'cyber', 'information security']):
            return "cybersecurity"
        
        return "general"
    
    def get_career_field_from_candidate(self, candidate: Dict) -> str:
        title = candidate.get('Experience', {}).get('Title', '').lower()
        education = candidate.get('Education', {}).get('field', '').lower()
        
        # Quick heuristic classification
        if any(term in title for term in ['data', 'scientist', 'analyst', 'ml', 'ai']):
            return "data science"
        elif any(term in title for term in ['developer', 'engineer', 'programmer', 'software']):
            return "software development"
        elif any(term in title for term in ['designer', 'ui', 'ux', 'creative']):
            return "design"
        elif any(term in title for term in ['marketing', 'digital', 'brand']):
            return "marketing"
        elif any(term in title for term in ['finance', 'accounting', 'financial']):
            return "finance"
        
        return "general"
    
    def get_skill_variations(self, skill: str, career_field: str = "general") -> List[str]:
        cache_key = f"{skill.lower()}_{career_field.lower()}"
        if cache_key in self.synonym_cache:
            return self.synonym_cache[cache_key]
        
        prompt = f"""
Generate synonyms and variations for the skill "{skill}" in {career_field} careers.

Include:
- Common abbreviations and acronyms
- Related technologies, tools, or concepts
- Different ways this skill might be written on resumes
- Limit to maximum 10 most relevant variations

Skill: {skill}
Career Field: {career_field}

Variations (comma-separated):
"""

        response = self._call_ollama_api(prompt)
        
        if not response:
            basic_variations = [
                skill.lower(),
                skill.lower().replace(" ", ""),
                skill.lower().replace(" ", "-"),
                skill.lower().replace(" ", "_")
            ]
            self.synonym_cache[cache_key] = basic_variations
            return basic_variations
        
        variations = self._parse_variations_response(response, skill)
        self.synonym_cache[cache_key] = variations
        return variations
    
    def _parse_variations_response(self, response: str, original_skill: str) -> List[str]:
        variations = [original_skill.lower()]
        
        response = response.replace("Variations:", "").strip()
        potential_variations = re.split(r'[,\n\r\t;]', response)
        
        for variation in potential_variations:
            cleaned = variation.strip().lower()
            
            if (cleaned and 
                len(cleaned) > 1 and 
                len(cleaned) < 50 and
                not cleaned.startswith(('note:', 'here are', 'these include', 'variations:')) and
                cleaned not in variations):
                variations.append(cleaned)
        
        return variations[:10]
    
    def calculate_skill_similarity(self, skill1: str, skill2: str, career_field: str = "general") -> float:
        variations1 = set(self.get_skill_variations(skill1, career_field))
        variations2 = set(self.get_skill_variations(skill2, career_field))
        
        if skill1.lower() == skill2.lower():
            return 1.0
        
        intersection = variations1.intersection(variations2)
        if intersection:
            return 0.95
        
        # Check for partial matches
        for v1 in variations1:
            for v2 in variations2:
                if len(v1) > 2 and len(v2) > 2:
                    if v1 in v2 or v2 in v1:
                        return 0.6
        
        return 0.0
    
    def calculate_job_relevancy(self, candidate: Dict, job: Dict, career_field: str) -> float:
        """Calculate how relevant a candidate is for a job using AI assessment"""
        cache_key = f"{candidate.get('name', 'unknown')}_{job.get('title', 'unknown')}_{career_field}"
        
        if cache_key in self.relevancy_cache:
            return self.relevancy_cache[cache_key]
        
        prompt = f"""
Assess how relevant this candidate is for the given job in {career_field}.

Job: {job.get('title', 'Unknown')}
Required Skills: {list(job.get('required_skills', {}).keys())}
Important Skills: {job.get('important_skills', [])}
Min Experience: {job.get('min_experience', 0)} years
Level: {job.get('level', 'entry')}

Candidate: {candidate.get('name', 'Unknown')}
Title: {candidate.get('Experience', {}).get('Title', 'Unknown')}
Experience: {candidate.get('Experience', {}).get('Years', 0)} years
Skills: {list(candidate.get('Skills', {}).keys())}
Education: {candidate.get('Education', {}).get('field', 'Unknown')}

Rate the overall relevancy from 0.0 (completely irrelevant) to 1.0 (perfect match).
Consider: skill alignment, experience level, career progression, education background.

Respond with only the numerical score (e.g., 0.85).

Relevancy score:
"""
        
        response = self._call_ollama_api(prompt)
        
        try:
            score_match = re.search(r'(\d+\.?\d*)', response)
            if score_match:
                score = float(score_match.group(1))
                if score > 1:
                    score = score / 10 if score <= 10 else score / 100
                score = max(0.0, min(1.0, score))
                self.relevancy_cache[cache_key] = score
                return score
        except (ValueError, AttributeError):
            pass
        
        # Fallback to basic relevancy calculation
        fallback_score = self._basic_relevancy_calculation(candidate, job)
        self.relevancy_cache[cache_key] = fallback_score
        return fallback_score
    
    def _basic_relevancy_calculation(self, candidate: Dict, job: Dict) -> float:
        """Basic fallback relevancy calculation"""
        candidate_skills = set(candidate.get('Skills', {}).keys())
        required_skills = set(job.get('required_skills', {}).keys())
        important_skills = set(job.get('important_skills', []))
        
        # Skill overlap
        skill_overlap = len(candidate_skills.intersection(required_skills)) / max(len(required_skills), 1)
        important_overlap = len(candidate_skills.intersection(important_skills)) / max(len(important_skills), 1)
        
        # Experience match
        candidate_exp = int(candidate.get('Experience', {}).get('Years', 0))
        required_exp = job.get('min_experience', 0)
        exp_score = min(1.0, candidate_exp / max(required_exp, 1))
        
        # Combined score
        return (skill_overlap * 0.4 + important_overlap * 0.4 + exp_score * 0.2)

class ModelManager:
    
    def __init__(self, models_dir: str = "./models"):
        self.models_dir = models_dir
        self.mistral_model = None
        self.embedding_model = None
        self.device = self._detect_optimal_device()
        self.gpu_layers = self._calculate_optimal_gpu_layers()
        
    def _detect_optimal_device(self):
        if torch.cuda.is_available():
            return "cuda"
        else:
            return "cpu"
    
    def _calculate_optimal_gpu_layers(self):
        if self.device == "cpu":
            return 0
        
        try:
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            if gpu_memory <= 4.5:
                return 15
            elif gpu_memory <= 6.5:
                return 25
            else:
                return 30
        except:
            return 15
        
    def load_models(self):
        try:
            if self.device == "cuda":
                torch.cuda.empty_cache()
            
            # Load Mistral model
            try:
                self.mistral_model = Llama(
                    model_path=f"{self.models_dir}/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                    n_ctx=1024,
                    n_gpu_layers=self.gpu_layers,
                    n_batch=256,
                    n_threads=4,
                    use_mmap=True,
                    use_mlock=False,
                    verbose=False
                )
                logger.info("Mistral model loaded successfully")
            except Exception as e:
                logger.warning(f"⚠️ Mistral model loading failed: {e}")
                self.mistral_model = None
            
            # Load embedding model
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                if self.device == "cuda":
                    self.embedding_model = self.embedding_model.to('cuda')
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.warning(f"⚠️ Embedding model loading failed: {e}")
                self.embedding_model = None
            
            logger.info(" Model loading completed")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise

class SmartRecruitMatcher:
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.model_manager = ModelManager()
        self.skill_mapper = None
        self.ollama_url = ollama_url
        
    def initialize(self):
        """Initialize the matcher with models and skill mapper"""
        try:
            self.model_manager.load_models()
            
            # Initialize skill mapper
            self.skill_mapper = DynamicSkillSynonymMapper(
                mistral_model=self.model_manager.mistral_model,
                ollama_url=self.ollama_url
            )
            
            logger.info(" SmartRecruit Matcher initialized successfully!")
            
        except Exception as e:
            logger.error(f"Matcher initialization failed: {e}")
            raise
    
    def calculate_matching_score(self, candidate: Dict, job: Dict) -> MatchingResult:
        """Calculate comprehensive matching score with emphasis on important skills"""
        
        job_career_field = self.skill_mapper.get_career_field_from_job(job)
        candidate_career_field = self.skill_mapper.get_career_field_from_candidate(candidate)
        
        # Calculate skill confidence score
        skill_confidence_score = self._calculate_skill_confidence(
            candidate.get('Skills', {}), 
            job.get('required_skills', {}),
            job_career_field
        )
        
        # Calculate important skills match with higher weight
        important_skills_score = self._calculate_important_skills_match(
            candidate.get('Skills', {}),
            job.get('important_skills', []),
            job_career_field
        )
        
        # Calculate AI-based relevancy score
        relevancy_score = self.skill_mapper.calculate_job_relevancy(
            candidate, job, job_career_field
        ) * 100
        
        # Calculate overall score with emphasis on important skills
        overall_score = (
            skill_confidence_score * 0.35 +
            important_skills_score * 0.45 +  # Higher weight for important skills
            relevancy_score * 0.20
        )
        
        return MatchingResult(
            candidate_name=candidate.get('name', 'Unknown'),
            job_title=job.get('title', 'Unknown'),
            overall_score=round(overall_score, 1),
            skill_confidence_score=round(skill_confidence_score, 1),
            important_skills_score=round(important_skills_score, 1),
            relevancy_score=round(relevancy_score, 1),
            detailed_breakdown={
                "career_field_match": job_career_field == candidate_career_field,
                "job_career_field": job_career_field,
                "candidate_career_field": candidate_career_field,
                "skill_matches": self._get_skill_matches(
                    candidate.get('Skills', {}), 
                    job.get('required_skills', {}), 
                    job_career_field
                ),
                "important_skill_matches": self._get_important_skill_matches(
                    candidate.get('Skills', {}),
                    job.get('important_skills', []),
                    job_career_field
                )
            }
        )
    
    def _calculate_skill_confidence(self, candidate_skills: Dict, required_skills: Dict, career_field: str) -> float:
        """Calculate skill confidence based on level matching and skill similarity"""
        if not required_skills:
            return 50.0
        
        total_confidence = 0
        total_weight = 0
        
        for req_skill, req_level in required_skills.items():
            req_level = int(req_level)
            best_match_confidence = 0
            
            for cand_skill, cand_level in candidate_skills.items():
                cand_level = int(cand_level)
                
                # Calculate skill similarity
                similarity = self.skill_mapper.calculate_skill_similarity(req_skill, cand_skill, career_field)
                
                if similarity > 0.5:  # Only consider reasonably similar skills
                    # Level confidence: how well the candidate's level matches the requirement
                    level_confidence = min(1.0, cand_level / req_level)
                    
                    # Skill match confidence combines similarity and level confidence
                    match_confidence = similarity * level_confidence * 100
                    best_match_confidence = max(best_match_confidence, match_confidence)
            
            total_confidence += best_match_confidence * req_level  # Weight by required level
            total_weight += req_level
        
        return (total_confidence / total_weight) if total_weight > 0 else 0
    
    def _calculate_important_skills_match(self, candidate_skills: Dict, important_skills: List, career_field: str) -> float:
        """Calculate how well candidate matches important skills"""
        if not important_skills:
            return 75.0  # Default score if no important skills specified
        
        matched_important = 0
        total_importance_score = 0
        
        for imp_skill in important_skills:
            best_match_score = 0
            
            for cand_skill, cand_level in candidate_skills.items():
                cand_level = int(cand_level)
                similarity = self.skill_mapper.calculate_skill_similarity(imp_skill, cand_skill, career_field)
                
                if similarity > 0.5:
                    # Score based on similarity and skill level
                    skill_score = similarity * (cand_level / 5.0)  # Normalize to 0-1
                    best_match_score = max(best_match_score, skill_score)
            
            if best_match_score > 0.6:  # Threshold for considering it a match
                matched_important += 1
                total_importance_score += best_match_score
        
        if matched_important == 0:
            return 0
        
        # Calculate score: (matched skills / total important skills) * average match quality
        match_ratio = matched_important / len(important_skills)
        avg_match_quality = total_importance_score / matched_important
        
        return match_ratio * avg_match_quality * 100
    
    def _get_skill_matches(self, candidate_skills: Dict, required_skills: Dict, career_field: str) -> Dict:
        """Get detailed skill matching information"""
        matches = {}
        
        for req_skill, req_level in required_skills.items():
            best_match = {
                "candidate_skill": None,
                "similarity": 0,
                "candidate_level": 0,
                "required_level": req_level,
                "confidence": 0
            }
            
            for cand_skill, cand_level in candidate_skills.items():
                similarity = self.skill_mapper.calculate_skill_similarity(req_skill, cand_skill, career_field)
                
                if similarity > best_match["similarity"]:
                    level_conf = min(1.0, int(cand_level) / int(req_level))
                    confidence = similarity * level_conf
                    
                    best_match.update({
                        "candidate_skill": cand_skill,
                        "similarity": round(similarity, 2),
                        "candidate_level": cand_level,
                        "confidence": round(confidence, 2)
                    })
            
            matches[req_skill] = best_match
        
        return matches
    
    def _get_important_skill_matches(self, candidate_skills: Dict, important_skills: List, career_field: str) -> List:
        """Get important skill matching details"""
        matches = []
        
        for imp_skill in important_skills:
            best_match = {
                "important_skill": imp_skill,
                "candidate_skill": None,
                "similarity": 0,
                "candidate_level": 0,
                "matched": False
            }
            
            for cand_skill, cand_level in candidate_skills.items():
                similarity = self.skill_mapper.calculate_skill_similarity(imp_skill, cand_skill, career_field)
                
                if similarity > best_match["similarity"]:
                    best_match.update({
                        "candidate_skill": cand_skill,
                        "similarity": round(similarity, 2),
                        "candidate_level": cand_level,
                        "matched": similarity > 0.6
                    })
            
            matches.append(best_match)
        
        return matches
    
    def find_top_candidates_for_job(self, job: Dict, candidates: List[Dict], top_n: int = 5) -> List[MatchingResult]:
        """Find top N candidates for a given job"""
        
        results = []
        
        for candidate in candidates:
            try:
                result = self.calculate_matching_score(candidate, job)
                results.append(result)
            except Exception as e:
                logger.error(f"Error matching {candidate.get('name', 'Unknown')}: {e}")
                continue
        
        # Sort by overall score and return top N
        results.sort(key=lambda x: x.overall_score, reverse=True)
        return results[:top_n]

def load_json_data():
    """Load candidates and job descriptions from JSON files - enhanced to handle multiple objects per file"""
    
    # Create directories if they don't exist
    os.makedirs("./candidates", exist_ok=True)
    os.makedirs("./jd", exist_ok=True)
    os.makedirs("./scores", exist_ok=True)
    
    candidates = []
    jobs = []
    
    # Load candidates - enhanced handling
    candidate_files = glob.glob("./candidates/*.json")
    logger.info(f"Found {len(candidate_files)} candidate files")
    
    for file_path in candidate_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = json.load(f)
                
                # Handle different file structures
                if isinstance(file_content, list):
                    # Multiple candidates in one file
                    for i, candidate_data in enumerate(file_content):
                        if validate_candidate_data(candidate_data):
                            candidates.append(candidate_data)
                            logger.info(f"Loaded candidate {i+1}: {candidate_data.get('name', 'Unknown')} from {file_path}")
                        else:
                            logger.warning(f"Invalid candidate data {i+1} in {file_path}")
                
                elif isinstance(file_content, dict):
                    # Check if it's a wrapper with candidates array
                    if 'candidates' in file_content and isinstance(file_content['candidates'], list):
                        for i, candidate_data in enumerate(file_content['candidates']):
                            if validate_candidate_data(candidate_data):
                                candidates.append(candidate_data)
                                logger.info(f"Loaded candidate {i+1}: {candidate_data.get('name', 'Unknown')} from {file_path}")
                            else:
                                logger.warning(f"Invalid candidate data {i+1} in {file_path}")
                    # Single candidate object
                    elif validate_candidate_data(file_content):
                        candidates.append(file_content)
                        logger.info(f"Loaded candidate: {file_content.get('name', 'Unknown')} from {file_path}")
                    else:
                        logger.warning(f"Invalid candidate data structure in {file_path}")
                
                else:
                    logger.warning(f"Unexpected file structure in {file_path}")
                    
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error loading candidate file {file_path}: {e}")
    
    # Load job descriptions - enhanced handling
    jd_files = glob.glob("./jd/*.json")
    logger.info(f"Found {len(jd_files)} job description files")
    
    for file_path in jd_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = json.load(f)
                
                # Handle different file structures
                if isinstance(file_content, list):
                    # Multiple jobs in one file
                    for i, job_data in enumerate(file_content):
                        if validate_job_data(job_data):
                            jobs.append(job_data)
                            logger.info(f"Loaded job {i+1}: {job_data.get('title', 'Unknown')} from {file_path}")
                        else:
                            logger.warning(f"Invalid job data {i+1} in {file_path}")
                
                elif isinstance(file_content, dict):
                    # Check if it's a wrapper with jobs array
                    if 'jobs' in file_content and isinstance(file_content['jobs'], list):
                        for i, job_data in enumerate(file_content['jobs']):
                            if validate_job_data(job_data):
                                jobs.append(job_data)
                                logger.info(f"Loaded job {i+1}: {job_data.get('title', 'Unknown')} from {file_path}")
                            else:
                                logger.warning(f"Invalid job data {i+1} in {file_path}")
                    # Single job object
                    elif validate_job_data(file_content):
                        jobs.append(file_content)
                        logger.info(f"Loaded job: {file_content.get('title', 'Unknown')} from {file_path}")
                    else:
                        logger.warning(f"Invalid job data structure in {file_path}")
                
                else:
                    logger.warning(f"Unexpected file structure in {file_path}")
                    
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error loading job file {file_path}: {e}")
    
    if not candidates:
        logger.warning("No valid candidate files found in ./candidates directory")
    
    if not jobs:
        logger.warning("No valid job description files found in ./jd directory")
    
    logger.info(f"Total loaded: {len(candidates)} candidates and {len(jobs)} jobs")
    return candidates, jobs

def validate_candidate_data(candidate: Dict) -> bool:
    """Validate candidate data structure"""
    required_fields = ['name']
    
    if not isinstance(candidate, dict):
        return False
    
    # Check for required fields
    for field in required_fields:
        if field not in candidate:
            logger.warning(f"Missing required field '{field}' in candidate data")
            return False
    
    # Validate structure
    if 'Skills' in candidate and not isinstance(candidate['Skills'], dict):
        logger.warning("Skills field should be a dictionary")
        return False
    
    if 'Experience' in candidate and not isinstance(candidate['Experience'], dict):
        logger.warning("Experience field should be a dictionary")
        return False
    
    if 'Education' in candidate and not isinstance(candidate['Education'], dict):
        logger.warning("Education field should be a dictionary")
        return False
    
    return True

def validate_job_data(job: Dict) -> bool:
    """Validate job data structure"""
    required_fields = ['title']
    
    if not isinstance(job, dict):
        return False
    
    # Check for required fields
    for field in required_fields:
        if field not in job:
            logger.warning(f"Missing required field '{field}' in job data")
            return False
    
    # Validate structure
    if 'required_skills' in job and not isinstance(job['required_skills'], dict):
        logger.warning("required_skills field should be a dictionary")
        return False
    
    if 'important_skills' in job and not isinstance(job['important_skills'], list):
        logger.warning("important_skills field should be a list")
        return False
    
    return True

def save_scores(job_results: Dict, timestamp: str):
    """Save scoring results to JSON files in ./scores directory - simplified to only candidate name and matching percentage"""
    
    # Ensure scores directory exists
    os.makedirs("./scores", exist_ok=True)
    
    # Save individual job results - one file per job with simplified data
    for job_title, results in job_results.items():
        # Create safe filename
        safe_job_title = re.sub(r'[^\w\s-]', '', job_title).strip()
        safe_job_title = re.sub(r'[-\s]+', '_', safe_job_title)
        
        filename = f"./scores/{safe_job_title}_{timestamp}.json"
        
        # Create simplified results with only candidate name and matching percentage
        simplified_results = []
        for result in results:
            if isinstance(result, MatchingResult):
                simplified_results.append({
                    "candidate_name": result.candidate_name,
                    "matching_percentage": result.overall_score
                })
            else:
                simplified_results.append({
                    "candidate_name": result.get('candidate_name', 'Unknown'),
                    "matching_percentage": result.get('overall_score', 0)
                })
        
        # Structure the simplified output
        job_score_data = {
            "job_title": job_title,
            "timestamp": timestamp,
            "top_5_candidates": simplified_results[:5]  # Only top 5 with name and percentage
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(job_score_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved top 5 candidates for '{job_title}' to {filename}")
        except Exception as e:
            logger.error(f" Error saving scores for '{job_title}': {e}")

def main():
    """Main execution function - process JSON data and save simplified scores"""
    print(" Starting SmartRecruit Job Matching System")
    print(" Output: Top 5 candidates per job (name + matching percentage only)")
    
    # Check GPU availability
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f" GPU Detected: {gpu_name} ({gpu_memory:.1f} GB VRAM)")
        torch.cuda.empty_cache()
    else:
        print(" Running in CPU mode")
    
    # Initialize matcher
    matcher = SmartRecruitMatcher(ollama_url="http://localhost:11434")
    
    print("\n Loading AI models...")
    start_time = time.time()
    
    try:
        matcher.initialize()
        load_time = time.time() - start_time
        print(f"Models loaded successfully in {load_time:.2f}s!")
        
    except Exception as e:
        print(f" Error loading models: {e}")
        print(" Continuing with limited functionality...")
    
    # Load JSON data
    print("\n Loading data from existing directories...")
    
    candidates, jobs = load_json_data()
    
    if not candidates or not jobs:
        print(" No data found! Please ensure:")
        print("   • ./candidates directory contains JSON files with candidate data")
        print("   • ./jd directory contains JSON files with job descriptions")
        return False
    
    print(f"Successfully loaded:")
    print(f"    {len(jobs)} job descriptions")
    print(f"    {len(candidates)} candidates")
    
    # Create timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Process each job and find top candidates
    print(f"\n{'='*60}")
    print(" JOB MATCHING RESULTS")
    print(f"{'='*60}")
    
    total_processing_start = time.time()
    job_results = {}
    
    for i, job in enumerate(jobs, 1):
        print(f"\n JOB {i}/{len(jobs)}: {job.get('title', 'Unknown')}")
        print("-" * 40)
        
        # Find top candidates
        job_start_time = time.time()
        
        try:
            top_candidates = matcher.find_top_candidates_for_job(job, candidates, top_n=5)
            job_processing_time = time.time() - job_start_time
            
            # Store results for this job
            job_results[job.get('title', f'Job_{i}')] = top_candidates
            
            if top_candidates:
                print(f" TOP 5 MATCHING CANDIDATES (Processed in {job_processing_time:.2f}s):")
                
                for rank, result in enumerate(top_candidates, 1):
                    print(f"   {rank}. {result.candidate_name}: {result.overall_score}%")
            else:
                print(" No suitable candidates found")
                job_results[job.get('title', f'Job_{i}')] = []
                
        except Exception as e:
            print(f" Error processing {job.get('title', 'Unknown')}: {e}")
            job_results[job.get('title', f'Job_{i}')] = []
            continue
    
    total_processing_time = time.time() - total_processing_start
    
    # Save all results to JSON files
    print(f"\n Saving simplified results to ./scores directory...")
    save_scores(job_results, timestamp)
    
    # Summary statistics
    print(f"\n{'='*60}")
    print(" PROCESSING SUMMARY")
    print(f"{'='*60}")
    
    print(f" Total Processing Time: {total_processing_time:.2f}s")
    print(f" Average Time per Job: {total_processing_time/len(jobs):.2f}s")
    print(f" Jobs Processed: {len(jobs)}")
    print(f" Candidates Evaluated: {len(candidates)}")
    print(f" Total Comparisons: {len(jobs) * len(candidates)}")
    print(f" Results saved with timestamp: {timestamp}")
    
    # Files created summary
    successful_jobs = len([j for j in job_results.values() if j])
    print(f"\n FILES CREATED:")
    print(f"    Individual job results: {successful_jobs} files")
    print(f"    Each file contains: job_title, timestamp, top_5_candidates")
    print(f"    Candidate data: candidate_name + matching_percentage only")
    
    if torch.cuda.is_available():
        final_memory = torch.cuda.memory_allocated(0) / 1024**2
        print(f" GPU Memory Usage: {final_memory:.0f}MB")
        torch.cuda.empty_cache()
    
    # Performance metrics
    comparisons_per_second = (len(jobs) * len(candidates)) / total_processing_time
    print(f"\n Performance: {comparisons_per_second:.1f} candidate comparisons per second")
    
    # Show file locations
    print(f"\n OUTPUT FILES LOCATION: ./scores/")
    print(f"    Format: [job_title]_{timestamp}.json")
    print(f"    Content: Simplified - candidate names and matching percentages only")
    
    print(f"\nJob matching analysis complete!")
    
    return True

if __name__ == "__main__":
    try:
        print("SmartRecruit Job Matching System - Simplified Output")
        print("Features: Uses existing files + Simplified scoring output")
        
        # Check if data directories exist and have files
        candidate_files = glob.glob("./candidates/*.json")
        job_files = glob.glob("./jd/*.json")
        
        if not candidate_files or not job_files:
            print(f"\nNo JSON files found!")
            print(f"   Candidate files found: {len(candidate_files)}")
            print(f"   Job description files found: {len(job_files)}")
            print(f"\nPlease ensure:")
            print(f"   • ./candidates directory contains JSON files with candidate data")
            print(f"   • ./jd directory contains JSON files with job descriptions")
        else:
            success = main()
            
            if success:
                print("\nExecution completed successfully!")
                print("Check the ./scores directory for simplified results")
                print("Each file contains only candidate names and matching percentages")
            else:
                print("\nExecution completed with some issues")
            
    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user")
        # Cleanup GPU memory if available
        try:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                print("🧹 GPU memory cleaned up")
        except:
            pass
        print(" Goodbye!")
        
    except Exception as e:
        print(f"\nFatal error: {e}")
        print(" Troubleshooting tips:")
        print("   • Check if all dependencies are installed")
        print("   • Verify GPU drivers if using CUDA")
        print("   • Check if Ollama is running: ollama serve")
        print("   • Ensure JSON files are properly formatted")
        print("   • Check file permissions for ./candidates, ./jd, and ./scores directories")
        
        # Cleanup GPU memory if available
        try:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except:
            pass