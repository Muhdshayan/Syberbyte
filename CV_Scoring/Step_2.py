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
from sklearn.metrics.pairwise import cosine_similarity
warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MatchingResult:
    candidate_name: str
    job_title: str
    overall_score: float
    technical_score: float
    experience_score: float
    cultural_score: float
    education_score: float
    ai_enhanced_score: float
    detailed_breakdown: Dict[str, Any]
    
    def to_dict(self):
        """Convert MatchingResult to dictionary for JSON serialization"""
        return asdict(self)

class FeedbackManager:
    """Manages feedback data for improving scoring accuracy"""
    
    def __init__(self, feedback_dir: str = "./feedback"):
        self.feedback_dir = feedback_dir
        self.feedback_cache = {}
        self.load_feedback()
    
    def load_feedback(self):
        """Load all feedback data from the feedback directory - simple format only"""
        self.feedback_cache = {'general': []}
        
        if not os.path.exists(self.feedback_dir):
            logger.info(f"Feedback directory {self.feedback_dir} does not exist. Creating it...")
            os.makedirs(self.feedback_dir, exist_ok=True)
            return
        
        feedback_files = glob.glob(f"{self.feedback_dir}/*.json")
        
        if not feedback_files:
            logger.info("No feedback files found. Will proceed without feedback.")
            return
        
        total_feedback_entries = 0
        
        for file_path in feedback_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    feedback_data = json.load(f)
                
                # Only handle the simple format: {"feedback": ["text1", "text2", ...]}
                if isinstance(feedback_data, dict) and 'feedback' in feedback_data:
                    feedback_list = feedback_data['feedback']
                    if isinstance(feedback_list, list):
                        for feedback_text in feedback_list:
                            if isinstance(feedback_text, str) and feedback_text.strip():
                                self.feedback_cache['general'].append(feedback_text.strip())
                                total_feedback_entries += 1
                        logger.info(f"Loaded {len(feedback_list)} feedback entries from {file_path}")
                    else:
                        logger.warning(f"Invalid feedback format in {file_path} - 'feedback' should be a list")
                else:
                    logger.warning(f"Invalid feedback format in {file_path} - expected {{'feedback': [...]}}")
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error in feedback file {file_path}: {e}")
            except Exception as e:
                logger.error(f"Error loading feedback file {file_path}: {e}")
        
        logger.info(f"Total feedback entries loaded: {total_feedback_entries}")
    
    def get_feedback_for_category(self, category: str) -> List[str]:
        """Get general feedback (category parameter ignored in simple format)"""
        general_feedback = self.feedback_cache.get('general', [])
        
        # Return up to 5 most recent feedback entries to keep prompt manageable
        return general_feedback[-5:] if general_feedback else []
    
    def format_feedback_for_prompt(self, category: str = None) -> str:
        """Format feedback for inclusion in prompts - category ignored in simple format"""
        feedback_list = self.get_feedback_for_category("general")
        
        if not feedback_list:
            return ""
        
        formatted_feedback = "\n".join([f"- {feedback}" for feedback in feedback_list])
        
        return f"""
Previous Feedback and Learning Points:
{formatted_feedback}

Please consider these insights when providing your assessment.
"""

class DynamicSkillSynonymMapper:
    
    def __init__(self, mistral_model=None, ollama_url: str = "http://localhost:11434", feedback_manager=None):
        self.mistral_model = mistral_model
        self.ollama_url = ollama_url
        self.synonym_cache = {}
        self.relevancy_cache = {}
        self.feedback_manager = feedback_manager
        
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
        """Updated to handle new job format"""
        title = job_description.get('title', '').lower()
        
        # Get all required skills for analysis
        all_skills = []
        required_skills = job_description.get('required_skills', {})
        if 'technical_skills' in required_skills:
            all_skills.extend(list(required_skills['technical_skills'].keys()))
        if 'soft_skills' in required_skills:
            all_skills.extend(list(required_skills['soft_skills'].keys()))
        
        skills_text = ' '.join(all_skills).lower()
        
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
        elif any(term in title for term in ['business', 'analytics', 'intelligence', 'strategy']):
            return "business analytics"
        elif any(term in title for term in ['civil engineer', 'structural', 'construction']):
            return "civil engineering"
        
        return "general"
    
    def get_career_field_from_candidate(self, candidate: Dict) -> str:
        # Extract education field/degree
        education = candidate.get('education', {})
        degree = education.get('degree', '').lower()
        
        # Check degree field first
        if any(term in degree for term in ['data science', 'data analytics', 'business analytics']):
            return "business analytics"
        elif any(term in degree for term in ['computer science', 'software', 'programming']):
            return "software development"
        elif any(term in degree for term in ['design', 'art', 'graphics']):
            return "design"
        elif any(term in degree for term in ['marketing', 'business administration']):
            return "marketing"
        elif any(term in degree for term in ['finance', 'accounting']):
            return "finance"
        elif any(term in degree for term in ['civil engineering']):
            return "civil engineering"
        elif any(term in degree for term in ['engineering']):
            return "engineering"
        
        # Fallback to analyzing skills for career field
        all_skills = self._get_all_candidate_skills_for_analysis(candidate)
        skill_names = ' '.join(all_skills.keys()).lower()
        
        if any(term in skill_names for term in ['data science', 'data visualization', 'business intelligence', 'tableau', 'power bi']):
            return "business analytics"
        elif any(term in skill_names for term in ['python', 'programming', 'software development', 'java', 'javascript']):
            return "software development"
        elif any(term in skill_names for term in ['design', 'ui', 'ux', 'canva', 'photoshop', 'illustrator']):
            return "design"
        elif any(term in skill_names for term in ['marketing', 'business planning', 'social media']):
            return "marketing"
        elif any(term in skill_names for term in ['excel', 'word', 'powerpoint', 'office']):
            return "business analytics"
        elif any(term in skill_names for term in ['autocad', 'structural design', 'construction']):
            return "civil engineering"
        
        return "general"
    
    def _get_all_candidate_skills_for_analysis(self, candidate: Dict) -> Dict[str, int]:
        """Helper method for career field analysis - flattens nested skills"""
        skills = candidate.get('skills', {})
        all_skills = {}
        
        def flatten_skills(skill_dict, prefix=""):
            for key, value in skill_dict.items():
                if isinstance(value, dict):
                    flatten_skills(value, f"{prefix}{key} " if prefix else f"{key} ")
                else:
                    skill_name = f"{prefix}{key}".strip()
                    all_skills[skill_name] = 1
        
        if 'technical_skills' in skills:
            flatten_skills(skills['technical_skills'])
        if 'soft_skills' in skills:
            flatten_skills(skills['soft_skills'])
        
        return all_skills
    
    def get_skill_variations(self, skill: str, career_field: str = "general") -> List[str]:
        cache_key = f"{skill.lower()}_{career_field.lower()}"
        if cache_key in self.synonym_cache:
            return self.synonym_cache[cache_key]
        
        # Add feedback to prompt if available
        feedback_text = ""
        if self.feedback_manager:
            feedback_text = self.feedback_manager.format_feedback_for_prompt()
        
        prompt = f"""
Generate synonyms and variations for the skill "{skill}" in {career_field} careers.

Include:
- Common abbreviations and acronyms
- Related technologies, tools, or concepts
- Different ways this skill might be written on resumes
- Limit to maximum 10 most relevant variations

{feedback_text}

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
    
    def ai_assess_cultural_fit(self, candidate: Dict, job: Dict, career_field: str) -> float:
        """AI-powered cultural fit assessment with feedback integration"""
        cache_key = f"cultural_{candidate.get('name', 'unknown')}_{job.get('title', 'unknown')}"
        
        if cache_key in self.relevancy_cache:
            return self.relevancy_cache[cache_key]
        
        # Extract soft skills
        candidate_soft = candidate.get('skills', {}).get('soft_skills', {})
        job_soft = job.get('required_skills', {}).get('soft_skills', {})
        
        # Add feedback to prompt if available
        feedback_text = ""
        if self.feedback_manager:
            feedback_text = self.feedback_manager.format_feedback_for_prompt()
        
        prompt = f"""
Assess the cultural fit between this candidate and job position in {career_field}.

Job: {job.get('title', 'Unknown')}
Job Level: {job.get('level', 'entry')}
Required Soft Skills: {list(job_soft.keys())}
Job Location: {job.get('location', 'Unknown')}
Work Type: {job.get('location_type', 'Unknown')}

Candidate: {candidate.get('name', 'Unknown')}
Candidate Soft Skills: {list(candidate_soft.keys())}
Experience Level: {candidate.get('years_of_experience', 0)} years

{feedback_text}

Rate cultural fit from 0.0 to 1.0 considering:
- Communication style match
- Leadership potential vs requirements
- Team collaboration abilities
- Work environment fit
- Career stage appropriateness

Respond with only the numerical score (e.g., 0.82).

Cultural fit score:
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
        
        # Fallback calculation
        return self._basic_cultural_fit_calculation(candidate, job)
    
    def _basic_cultural_fit_calculation(self, candidate: Dict, job: Dict) -> float:
        """Basic cultural fit fallback"""
        candidate_soft = set(candidate.get('skills', {}).get('soft_skills', {}).keys())
        job_soft = set(job.get('required_skills', {}).get('soft_skills', {}).keys())
        
        if not job_soft:
            return 0.75
        
        overlap = len(candidate_soft.intersection(job_soft)) / len(job_soft)
        return overlap

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
                logger.warning(f"WARNING: Mistral model loading failed: {e}")
                self.mistral_model = None
            
            # Load embedding model
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                if self.device == "cuda":
                    self.embedding_model = self.embedding_model.to('cuda')
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.warning(f"WARNING: Embedding model loading failed: {e}")
                self.embedding_model = None
            
            logger.info("Model loading completed")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise

class SmartRecruitMatcher:
    
    def __init__(self, ollama_url: str = "http://localhost:11434", feedback_dir: str = "./feedback"):
        self.model_manager = ModelManager()
        self.skill_mapper = None
        self.ollama_url = ollama_url
        self.feedback_manager = FeedbackManager(feedback_dir)
        
    def initialize(self):
        """Initialize the matcher with models and skill mapper"""
        try:
            self.model_manager.load_models()
            
            # Initialize skill mapper with feedback manager
            self.skill_mapper = DynamicSkillSynonymMapper(
                mistral_model=self.model_manager.mistral_model,
                ollama_url=self.ollama_url,
                feedback_manager=self.feedback_manager
            )
            
            logger.info("SmartRecruit Matcher initialized successfully!")
            
        except Exception as e:
            logger.error(f"Matcher initialization failed: {e}")
            raise
    
    def _get_candidate_technical_skills(self, candidate: Dict) -> Dict[str, int]:
        """Extract only technical skills from candidate"""
        skills = candidate.get('skills', {})
        technical_skills = {}
        
        def extract_skills_recursive(skill_dict, prefix=""):
            for key, value in skill_dict.items():
                if isinstance(value, dict):
                    extract_skills_recursive(value, f"{prefix}{key} " if prefix else f"{key} ")
                elif isinstance(value, (int, float)):
                    skill_name = f"{prefix}{key}".strip()
                    technical_skills[skill_name] = int(value)
                elif isinstance(value, str) and value.isdigit():
                    skill_name = f"{prefix}{key}".strip()
                    technical_skills[skill_name] = int(value)
                else:
                    skill_name = f"{prefix}{key}".strip()
                    technical_skills[skill_name] = 50
        
        if 'technical_skills' in skills:
            extract_skills_recursive(skills['technical_skills'])
        
        return technical_skills
    
    def _get_candidate_soft_skills(self, candidate: Dict) -> Dict[str, int]:
        """Extract only soft skills from candidate"""
        skills = candidate.get('skills', {})
        soft_skills = {}
        
        def extract_skills_recursive(skill_dict, prefix=""):
            for key, value in skill_dict.items():
                if isinstance(value, dict):
                    extract_skills_recursive(value, f"{prefix}{key} " if prefix else f"{key} ")
                elif isinstance(value, (int, float)):
                    skill_name = f"{prefix}{key}".strip()
                    soft_skills[skill_name] = int(value)
                elif isinstance(value, str) and value.isdigit():
                    skill_name = f"{prefix}{key}".strip()
                    soft_skills[skill_name] = int(value)
                else:
                    skill_name = f"{prefix}{key}".strip()
                    soft_skills[skill_name] = 50
        
        if 'soft_skills' in skills:
            extract_skills_recursive(skills['soft_skills'])
        
        return soft_skills
    
    def _get_job_technical_skills(self, job: Dict) -> Dict[str, int]:
        """Extract technical skills from job"""
        required_skills = job.get('required_skills', {})
        technical_skills = {}
        
        if 'technical_skills' in required_skills:
            for skill, level in required_skills['technical_skills'].items():
                technical_skills[skill] = int(level)
        
        return technical_skills
    
    def _get_job_soft_skills(self, job: Dict) -> Dict[str, int]:
        """Extract soft skills from job"""
        required_skills = job.get('required_skills', {})
        soft_skills = {}
        
        if 'soft_skills' in required_skills:
            for skill, level in required_skills['soft_skills'].items():
                soft_skills[skill] = int(level)
        
        return soft_skills
    
    def calculate_technical_score(self, candidate: Dict, job: Dict, career_field: str) -> float:
        """Calculate pure technical skills score"""
        candidate_tech = self._get_candidate_technical_skills(candidate)
        job_tech = self._get_job_technical_skills(job)
        
        if not job_tech:
            return 50.0  # Default if no technical requirements
        
        total_score = 0
        total_weight = 0
        
        for req_skill, req_level in job_tech.items():
            req_level = int(req_level)
            best_match_score = 0
            
            for cand_skill, cand_level in candidate_tech.items():
                cand_level = int(cand_level)
                
                similarity = self.skill_mapper.calculate_skill_similarity(req_skill, cand_skill, career_field)
                
                if similarity > 0.5:
                    level_confidence = min(1.2, cand_level / req_level)  # Allow 20% bonus for exceeding
                    match_score = similarity * level_confidence * 100
                    best_match_score = max(best_match_score, match_score)
            
            total_score += best_match_score * req_level
            total_weight += req_level
        
        return min(100.0, (total_score / total_weight) if total_weight > 0 else 0)
    
    def calculate_experience_score(self, candidate: Dict, job: Dict) -> float:
        """Calculate experience matching score with feedback integration"""
        candidate_years = float(candidate.get('years_of_experience', 0))
        required_years = float(job.get('experience', 0))
        job_level = job.get('level', 'entry').lower()
        
        # Years match component (0-40 points)
        if required_years == 0:
            years_score = 40
        else:
            years_ratio = candidate_years / required_years
            if years_ratio >= 1.0:
                years_score = min(40, 30 + (years_ratio - 1.0) * 10)  # Bonus for extra experience
            else:
                years_score = years_ratio * 30  # Penalty for insufficient experience
        
        # Level appropriateness component (0-35 points)
        level_score = self._calculate_level_appropriateness(candidate_years, job_level)
        
        # Career progression component (0-25 points)
        progression_score = self._assess_career_progression(candidate, job)
        
        total_score = years_score + level_score + progression_score
        return min(100.0, total_score)
    
    def _calculate_level_appropriateness(self, years: float, level: str) -> float:
        """Calculate if candidate's experience matches job level"""
        level_ranges = {
            'entry': (0, 2),
            'junior': (1, 3),
            'intermediate': (3, 6),
            'senior': (5, 10),
            'lead': (8, 15),
            'expert': (10, 20)
        }
        
        min_years, max_years = level_ranges.get(level, (0, 5))
        
        if min_years <= years <= max_years:
            return 35  # Perfect match
        elif years < min_years:
            return max(0, 35 - (min_years - years) * 10)  # Penalty for underqualification
        else:
            return max(20, 35 - (years - max_years) * 2)  # Small penalty for overqualification
    
    def _assess_career_progression(self, candidate: Dict, job: Dict) -> float:
        """Assess career progression appropriateness"""
        # Simple heuristic based on experience and education
        years = float(candidate.get('years_of_experience', 0))
        education = candidate.get('education', {})
        degree = education.get('degree', '').lower()
        
        # Education boost
        education_score = 0
        if any(term in degree for term in ['master', 'mba', 'phd']):
            education_score = 10
        elif any(term in degree for term in ['bachelor', 'degree']):
            education_score = 5
        
        # Experience consistency
        experience_score = min(15, years * 2)
        
        return education_score + experience_score
    
    def calculate_cultural_score(self, candidate: Dict, job: Dict, career_field: str) -> float:
        """Calculate cultural fit and soft skills score"""
        candidate_soft = self._get_candidate_soft_skills(candidate)
        job_soft = self._get_job_soft_skills(job)
        
        if not job_soft:
            return 75.0  # Default if no soft skill requirements
        
        # Direct soft skills matching (60%)
        soft_skills_score = self._calculate_soft_skills_match(candidate_soft, job_soft, career_field)
        
        # AI cultural fit assessment (40%)
        cultural_fit_score = self.skill_mapper.ai_assess_cultural_fit(candidate, job, career_field) * 100
        
        return soft_skills_score * 0.6 + cultural_fit_score * 0.4
    
    def _calculate_soft_skills_match(self, candidate_soft: Dict, job_soft: Dict, career_field: str) -> float:
        """Calculate soft skills matching"""
        total_score = 0
        total_weight = 0
        
        for req_skill, req_level in job_soft.items():
            req_level = int(req_level)
            best_match_score = 0
            
            for cand_skill, cand_level in candidate_soft.items():
                cand_level = int(cand_level)
                
                similarity = self.skill_mapper.calculate_skill_similarity(req_skill, cand_skill, career_field)
                
                if similarity > 0.5:
                    level_confidence = min(1.0, cand_level / req_level)
                    match_score = similarity * level_confidence * 100
                    best_match_score = max(best_match_score, match_score)
            
            total_score += best_match_score * req_level
            total_weight += req_level
        
        return (total_score / total_weight) if total_weight > 0 else 0
    
    def calculate_education_score(self, candidate: Dict, job: Dict) -> float:
        """Calculate education and certification matching score with feedback integration"""
        candidate_education = candidate.get('education', {})
        job_education_req = job.get('education_level', '')
        
        candidate_degree = candidate_education.get('degree', '').lower()
        candidate_field = candidate_education.get('field', '').lower()
        
        # Base education level matching
        education_score = self._match_education_level(candidate_degree, job_education_req)
        
        # Field relevance
        field_score = self._assess_field_relevance(candidate_field, job)
        
        # Additional certifications
        cert_score = self._assess_certifications(candidate_education, job)
        
        return min(100.0, education_score * 0.6 + field_score * 0.3 + cert_score * 0.1)
    
    def _match_education_level(self, candidate_degree: str, job_requirement: str) -> float:
        """Match education level requirement"""
        education_hierarchy = {
            'phd': 5, 'doctorate': 5,
            'master': 4, 'mba': 4, 'ms': 4,
            'bachelor': 3, 'degree': 3,
            'associate': 2, 'diploma': 2,
            'certificate': 1, 'high school': 1
        }
        
        candidate_level = 0
        for edu_type, level in education_hierarchy.items():
            if edu_type in candidate_degree:
                candidate_level = max(candidate_level, level)
        
        required_level = 0
        job_req_lower = job_requirement.lower()
        for edu_type, level in education_hierarchy.items():
            if edu_type in job_req_lower:
                required_level = max(required_level, level)
        
        if required_level == 0:
            return 80  # No specific requirement
        
        if candidate_level >= required_level:
            return 100
        elif candidate_level == required_level - 1:
            return 70
        else:
            return max(30, 100 - (required_level - candidate_level) * 25)
    
    def _assess_field_relevance(self, candidate_field: str, job: Dict) -> float:
        """Assess if education field is relevant to job"""
        job_title = job.get('title', '').lower()
        career_field = self.skill_mapper.get_career_field_from_job(job)
        
        # Direct field matching
        if candidate_field in job_title or job_title in candidate_field:
            return 100
        
        # Career field matching
        field_mappings = {
            'marketing': ['marketing', 'business', 'communications'],
            'engineering': ['engineering', 'technology', 'computer science'],
            'finance': ['finance', 'accounting', 'economics', 'business'],
            'design': ['design', 'art', 'creative'],
            'data science': ['data science', 'statistics', 'mathematics', 'computer science']
        }
        
        relevant_fields = field_mappings.get(career_field, [])
        for field in relevant_fields:
            if field in candidate_field:
                return 80
        
        return 50  # Neutral if no clear match
    
    def _assess_certifications(self, education: Dict, job: Dict) -> float:
        """Assess additional certifications"""
        certifications = education.get('certifications', [])
        if isinstance(certifications, str):
            certifications = [certifications]
        
        if not certifications:
            return 50
        
        # Simple certification scoring
        return min(100, len(certifications) * 20 + 50)
    
    def calculate_ai_enhanced_score(self, candidate: Dict, job: Dict) -> float:
        """Calculate AI-enhanced semantic matching score with feedback integration"""
        if not self.model_manager.embedding_model:
            return self._fallback_semantic_score(candidate, job)
        
        try:
            # Create text representations
            candidate_text = self._create_candidate_profile_text(candidate)
            job_text = self._create_job_description_text(job)
            
            # Generate embeddings
            candidate_embedding = self.model_manager.embedding_model.encode([candidate_text])
            job_embedding = self.model_manager.embedding_model.encode([job_text])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(candidate_embedding, job_embedding)[0][0]
            
            return float(similarity * 100)
            
        except Exception as e:
            logger.warning(f"AI semantic matching failed: {e}")
            return self._fallback_semantic_score(candidate, job)
    
    def _create_candidate_profile_text(self, candidate: Dict) -> str:
        """Create text representation of candidate for embedding"""
        parts = []
        
        # Basic info
        parts.append(f"Candidate: {candidate.get('name', 'Unknown')}")
        parts.append(f"Experience: {candidate.get('years_of_experience', 0)} years")
        
        # Education
        education = candidate.get('education', {})
        if education:
            degree = education.get('degree', '')
            field = education.get('field', '')
            if degree or field:
                parts.append(f"Education: {degree} {field}".strip())
        
        # Technical skills
        tech_skills = self._get_candidate_technical_skills(candidate)
        if tech_skills:
            skills_text = ', '.join([f"{skill}({level})" for skill, level in tech_skills.items()])
            parts.append(f"Technical Skills: {skills_text}")
        
        # Soft skills
        soft_skills = self._get_candidate_soft_skills(candidate)
        if soft_skills:
            skills_text = ', '.join([f"{skill}({level})" for skill, level in soft_skills.items()])
            parts.append(f"Soft Skills: {skills_text}")
        
        return '. '.join(parts)
    
    def _create_job_description_text(self, job: Dict) -> str:
        """Create text representation of job for embedding"""
        parts = []
        
        # Basic info
        parts.append(f"Job: {job.get('title', 'Unknown')}")
        parts.append(f"Level: {job.get('level', 'entry')}")
        parts.append(f"Experience Required: {job.get('experience', 0)} years")
        parts.append(f"Location: {job.get('location', 'Unknown')}")
        
        # Technical requirements
        tech_skills = self._get_job_technical_skills(job)
        if tech_skills:
            skills_text = ', '.join([f"{skill}({level})" for skill, level in tech_skills.items()])
            parts.append(f"Technical Requirements: {skills_text}")
        
        # Soft skill requirements
        soft_skills = self._get_job_soft_skills(job)
        if soft_skills:
            skills_text = ', '.join([f"{skill}({level})" for skill, level in soft_skills.items()])
            parts.append(f"Soft Skills Required: {skills_text}")
        
        # Important skills
        important_skills = job.get('important_skills', [])
        if important_skills:
            parts.append(f"Critical Skills: {', '.join(important_skills)}")
        
        return '. '.join(parts)
    
    def _fallback_semantic_score(self, candidate: Dict, job: Dict) -> float:
        """Fallback semantic scoring without embeddings with feedback integration"""
        # Simple keyword matching approach
        candidate_text = self._create_candidate_profile_text(candidate).lower()
        job_text = self._create_job_description_text(job).lower()
        
        # Extract important keywords
        job_keywords = set(re.findall(r'\b\w{3,}\b', job_text))
        candidate_keywords = set(re.findall(r'\b\w{3,}\b', candidate_text))
        
        # Calculate overlap
        common_keywords = job_keywords.intersection(candidate_keywords)
        total_keywords = job_keywords.union(candidate_keywords)
        
        if not total_keywords:
            return 50.0
        
        semantic_score = (len(common_keywords) / len(total_keywords)) * 100
        return min(100.0, semantic_score * 2)  # Boost the score since simple matching is harsh
    
    def calculate_matching_score(self, candidate: Dict, job: Dict) -> MatchingResult:
        """Calculate comprehensive matching score with feedback-enhanced analysis"""
        
        job_career_field = self.skill_mapper.get_career_field_from_job(job)
        candidate_career_field = self.skill_mapper.get_career_field_from_candidate(candidate)
        
        # Calculate individual component scores
        technical_score = self.calculate_technical_score(candidate, job, job_career_field)
        experience_score = self.calculate_experience_score(candidate, job)
        cultural_score = self.calculate_cultural_score(candidate, job, job_career_field)
        education_score = self.calculate_education_score(candidate, job)
        ai_enhanced_score = self.calculate_ai_enhanced_score(candidate, job)
        
        # Comprehensive weighted formula
        overall_score = (
            technical_score * 0.30 +      # 30% - Technical skills
            cultural_score * 0.20 +       # 20% - Cultural fit/soft skills
            experience_score * 0.25 +     # 25% - Experience match
            education_score * 0.10 +      # 10% - Education match
            ai_enhanced_score * 0.15      # 15% - AI semantic understanding
        )
        
        return MatchingResult(
            candidate_name=candidate.get('name', 'Unknown'),
            job_title=job.get('title', 'Unknown'),
            overall_score=round(overall_score, 1),
            technical_score=round(technical_score, 1),
            experience_score=round(experience_score, 1),
            cultural_score=round(cultural_score, 1),
            education_score=round(education_score, 1),
            ai_enhanced_score=round(ai_enhanced_score, 1),
            detailed_breakdown={
                "career_field_match": job_career_field == candidate_career_field,
                "job_career_field": job_career_field,
                "candidate_career_field": candidate_career_field,
                "years_of_experience": candidate.get('years_of_experience', 0),
                "job_experience_requirement": job.get('experience', 0),
                "job_level": job.get('level', 'unknown'),
                "education_match": {
                    "candidate_degree": candidate.get('education', {}).get('degree', 'Unknown'),
                    "job_requirement": job.get('education_level', 'Not specified'),
                    "field_relevance": candidate.get('education', {}).get('field', 'Unknown')
                },
                "technical_skill_matches": self._get_technical_skill_matches(candidate, job, job_career_field),
                "soft_skill_matches": self._get_soft_skill_matches(candidate, job, job_career_field),
                "important_skill_coverage": self._get_important_skill_coverage(candidate, job, job_career_field),
                "feedback_enhanced": self.feedback_manager.feedback_cache != {},
                "scoring_weights": {
                    "technical": "30%",
                    "cultural": "20%", 
                    "experience": "25%",
                    "education": "10%",
                    "ai_enhanced": "15%"
                }
            }
        )
    
    def _get_technical_skill_matches(self, candidate: Dict, job: Dict, career_field: str) -> Dict:
        """Get detailed technical skill matching information"""
        candidate_tech = self._get_candidate_technical_skills(candidate)
        job_tech = self._get_job_technical_skills(job)
        
        matches = {}
        for req_skill, req_level in job_tech.items():
            best_match = {
                "candidate_skill": None,
                "similarity": 0,
                "candidate_level": 0,
                "required_level": req_level,
                "confidence": 0
            }
            
            for cand_skill, cand_level in candidate_tech.items():
                similarity = self.skill_mapper.calculate_skill_similarity(req_skill, cand_skill, career_field)
                
                if similarity > best_match["similarity"]:
                    level_conf = min(1.2, int(cand_level) / int(req_level))
                    confidence = similarity * level_conf
                    
                    best_match.update({
                        "candidate_skill": cand_skill,
                        "similarity": round(similarity, 2),
                        "candidate_level": cand_level,
                        "confidence": round(confidence, 2)
                    })
            
            matches[req_skill] = best_match
        
        return matches
    
    def _get_soft_skill_matches(self, candidate: Dict, job: Dict, career_field: str) -> Dict:
        """Get detailed soft skill matching information"""
        candidate_soft = self._get_candidate_soft_skills(candidate)
        job_soft = self._get_job_soft_skills(job)
        
        matches = {}
        for req_skill, req_level in job_soft.items():
            best_match = {
                "candidate_skill": None,
                "similarity": 0,
                "candidate_level": 0,
                "required_level": req_level,
                "confidence": 0
            }
            
            for cand_skill, cand_level in candidate_soft.items():
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
    
    def _get_important_skill_coverage(self, candidate: Dict, job: Dict, career_field: str) -> List:
        """Get important skill coverage details"""
        important_skills = job.get('important_skills', [])
        candidate_tech = self._get_candidate_technical_skills(candidate)
        candidate_soft = self._get_candidate_soft_skills(candidate)
        all_candidate_skills = {**candidate_tech, **candidate_soft}
        
        coverage = []
        for imp_skill in important_skills:
            best_match = {
                "important_skill": imp_skill,
                "candidate_skill": None,
                "similarity": 0,
                "candidate_level": 0,
                "covered": False
            }
            
            for cand_skill, cand_level in all_candidate_skills.items():
                similarity = self.skill_mapper.calculate_skill_similarity(imp_skill, cand_skill, career_field)
                
                if similarity > best_match["similarity"]:
                    best_match.update({
                        "candidate_skill": cand_skill,
                        "similarity": round(similarity, 2),
                        "candidate_level": cand_level,
                        "covered": similarity > 0.6
                    })
            
            coverage.append(best_match)
        
        return coverage
    
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
    os.makedirs("./feedback", exist_ok=True)  # Create feedback directory
    
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
    
    # Load job descriptions - enhanced handling for new format
    jd_files = glob.glob("./jd/*.json")
    logger.info(f"Found {len(jd_files)} job description files")
    
    for file_path in jd_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = json.load(f)
                
                # Handle different file structures
                if isinstance(file_content, list):
                    # Multiple jobs in one file (expected format)
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
    """Validate candidate data structure for new format - handles nested skills"""
    required_fields = ['name']
    
    if not isinstance(candidate, dict):
        return False
    
    # Check for required fields
    for field in required_fields:
        if field not in candidate:
            logger.warning(f"Missing required field '{field}' in candidate data")
            return False
    
    # Validate structure for new format
    if 'skills' in candidate:
        skills = candidate['skills']
        if not isinstance(skills, dict):
            logger.warning("Skills field should be a dictionary")
            return False
        
        # Check for technical_skills and soft_skills structure (can be nested)
        if 'technical_skills' in skills and not isinstance(skills['technical_skills'], dict):
            logger.warning("technical_skills should be a dictionary")
            return False
        
        if 'soft_skills' in skills and not isinstance(skills['soft_skills'], dict):
            logger.warning("soft_skills should be a dictionary")
            return False
    
    if 'education' in candidate and not isinstance(candidate['education'], dict):
        logger.warning("Education field should be a dictionary")
        return False
    
    if 'years_of_experience' in candidate:
        try:
            float(candidate['years_of_experience'])
        except (ValueError, TypeError):
            logger.warning("years_of_experience should be a number")
            return False
    
    return True

def validate_job_data(job: Dict) -> bool:
    """Validate job data structure for the new format"""
    required_fields = ['title']
    
    if not isinstance(job, dict):
        return False
    
    # Check for required fields
    for field in required_fields:
        if field not in job:
            logger.warning(f"Missing required field '{field}' in job data")
            return False
    
    # Validate structure for new format
    if 'required_skills' in job:
        required_skills = job['required_skills']
        if not isinstance(required_skills, dict):
            logger.warning("required_skills field should be a dictionary")
            return False
        
        # Check for nested technical_skills and soft_skills structure
        if 'technical_skills' in required_skills and not isinstance(required_skills['technical_skills'], dict):
            logger.warning("required_skills.technical_skills should be a dictionary")
            return False
        
        if 'soft_skills' in required_skills and not isinstance(required_skills['soft_skills'], dict):
            logger.warning("required_skills.soft_skills should be a dictionary")
            return False
    
    if 'important_skills' in job and not isinstance(job['important_skills'], list):
        logger.warning("important_skills field should be a list")
        return False
    
    # Validate experience field (renamed from min_experience)
    if 'experience' in job:
        try:
            float(job['experience'])
        except (ValueError, TypeError):
            logger.warning("experience should be a number")
            return False
    
    # Validate level field
    if 'level' in job:
        valid_levels = ['entry', 'junior', 'intermediate', 'senior', 'lead', 'expert']
        if job['level'].lower() not in valid_levels:
            logger.warning(f"level should be one of: {valid_levels}")
            return False
    
    return True

def save_scores(job_results: Dict, timestamp: str):
    """Save scoring results to JSON files in ./scores directory - simplified output"""
    
    # Ensure scores directory exists
    os.makedirs("./scores", exist_ok=True)
    
    # Save individual job results - one file per job with simplified data
    for job_title, results in job_results.items():
        # Create safe filename
        safe_job_title = re.sub(r'[^\w\s-]', '', job_title).strip()
        safe_job_title = re.sub(r'[-\s]+', '_', safe_job_title)
        
        filename = f"./scores/{safe_job_title}_{timestamp}.json"
        
        # Create simplified results without scoring weights
        simplified_results = []
        for result in results:
            if isinstance(result, MatchingResult):
                simplified_results.append({
                    "candidate_name": result.candidate_name,
                    "overall_score": result.overall_score,
                    "component_scores": {
                        "technical_score": result.technical_score,
                        "experience_score": result.experience_score,
                        "cultural_score": result.cultural_score,
                        "education_score": result.education_score,
                        "ai_enhanced_score": result.ai_enhanced_score
                    },
                    "feedback_enhanced": result.detailed_breakdown.get("feedback_enhanced", False)
                })
            else:
                simplified_results.append({
                    "candidate_name": result.get('candidate_name', 'Unknown'),
                    "overall_score": result.get('overall_score', 0),
                    "feedback_enhanced": False
                })
        
        # Structure the simplified output without job details and scoring weights
        job_score_data = {
            "job_title": job_title,
            "timestamp": timestamp,
            "feedback_enhanced": any(r.get("feedback_enhanced", False) for r in simplified_results),
            "top_5_candidates": simplified_results[:5]
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(job_score_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved results for '{job_title}' to {filename}")
        except Exception as e:
            logger.error(f"Error saving scores for '{job_title}': {e}")

def create_sample_feedback_files():
    """Create sample feedback file to demonstrate the simple feedback system"""
    feedback_dir = "./feedback"
    os.makedirs(feedback_dir, exist_ok=True)
    
    # Sample feedback in the required simple format
    sample_feedback = {
        "feedback": [
            "Focus on candidates who demonstrate continuous learning and adaptability in their skill development.",
            "Consider giving higher weight to candidates with proven problem-solving experience over pure technical proficiency.",
            "Cultural fit should emphasize collaboration and communication skills more heavily for remote positions.",
            "Experience quality matters more than quantity - prioritize relevant project experience over years alone.",
            "Education field relevance should be weighted higher for specialized technical roles.",
            "Modern framework knowledge should be prioritized over legacy technology experience.",
            "Remote work experience should be a significant factor for distributed teams.",
            "Career progression consistency is more valuable than total years of experience.",
            "Relevant certifications can sometimes outweigh formal degree requirements.",
            "Context understanding is crucial - keywords alone don't determine fit."
        ]
    }
    
    # Save sample feedback file
    try:
        with open(f"{feedback_dir}/feedback.json", 'w', encoding='utf-8') as f:
            json.dump(sample_feedback, f, indent=2, ensure_ascii=False)
        
        logger.info("Created sample feedback file in ./feedback directory")
        
    except Exception as e:
        logger.error(f"Error creating sample feedback file: {e}")

def main():
    """Main execution function - process JSON data and save comprehensive scores with feedback integration"""
    print("Starting SmartRecruit Job Matching System - FEEDBACK-ENHANCED SCORING")
    print("Enhanced 5-Component Scoring with AI Learning: Technical | Experience | Cultural | Education | AI-Enhanced")
    print("NEW: Feedback integration for continuous learning and improved accuracy")
    
    # Check GPU availability
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"GPU Detected: {gpu_name} ({gpu_memory:.1f} GB VRAM)")
        torch.cuda.empty_cache()
    else:
        print("Running in CPU mode")
    
    # Create sample feedback files if feedback directory is empty
    feedback_dir = "./feedback"
    if not os.path.exists(feedback_dir) or not glob.glob(f"{feedback_dir}/*.json"):
        print("No feedback files found. Creating sample feedback files...")
        create_sample_feedback_files()
    
    # Initialize matcher with feedback integration
    matcher = SmartRecruitMatcher(ollama_url="http://localhost:11434", feedback_dir=feedback_dir)
    
    print("\nLoading AI models and feedback data...")
    start_time = time.time()
    
    try:
        matcher.initialize()
        load_time = time.time() - start_time
        print(f"Models and feedback loaded successfully in {load_time:.2f}s!")
        
        # Display feedback status
        feedback_status = matcher.feedback_manager.feedback_cache
        total_feedback = len(feedback_status.get('general', []))
        
        if total_feedback > 0:
            print(f"Feedback Integration Status: {total_feedback} feedback entries loaded")
        else:
            print("Feedback Integration Status: No feedback data found - using default scoring")
        
    except Exception as e:
        print(f"Error loading models: {e}")
        print("Continuing with limited functionality...")
    
    # Load JSON data
    print("\nLoading data from existing directories...")
    
    candidates, jobs = load_json_data()
    
    if not candidates or not jobs:
        print("No data found! Please ensure:")
        print("   • ./candidates directory contains JSON files with candidate data")
        print("   • ./jd directory contains JSON files with job descriptions")
        print("   • Job descriptions use the new format with nested required_skills")
        print("   • ./feedback directory contains JSON files with scoring feedback (optional)")
        return False
    
    print(f"Successfully loaded:")
    print(f"    {len(jobs)} job descriptions")
    print(f"    {len(candidates)} candidates")
    
    # Create timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Process each job and find top candidates
    print(f"\n{'='*80}")
    print("FEEDBACK-ENHANCED JOB MATCHING RESULTS")
    print("Scoring: Technical(30%) + Cultural(20%) + Experience(25%) + Education(10%) + AI(15%)")
    print("Enhanced with AI learning from feedback data")
    print(f"{'='*80}")
    
    total_processing_start = time.time()
    job_results = {}
    
    for i, job in enumerate(jobs, 1):
        print(f"\nJOB {i}/{len(jobs)}: {job.get('title', 'Unknown')}")
        print(f"Location: {job.get('location', 'Unknown')}")
        print(f"Level: {job.get('level', 'Unknown')} | Experience: {job.get('experience', 0)} years")
        print("-" * 60)
        
        # Find top candidates
        job_start_time = time.time()
        
        try:
            top_candidates = matcher.find_top_candidates_for_job(job, candidates, top_n=5)
            job_processing_time = time.time() - job_start_time
            
            # Store results for this job
            job_results[job.get('title', f'Job_{i}')] = top_candidates
            
            if top_candidates:
                print(f"TOP 5 MATCHING CANDIDATES (Processed in {job_processing_time:.2f}s):")
                feedback_indicator = "🧠" if total_feedback > 0 else ""
                print(f"{'Rank':<4} {'Name':<20} {'Overall':<8} {'Tech':<6} {'Exp':<6} {'Culture':<8} {'Edu':<6} {'AI':<6} {feedback_indicator}")
                print("-" * 60)
                
                for rank, result in enumerate(top_candidates, 1):
                    feedback_enhanced = "✓" if result.detailed_breakdown.get("feedback_enhanced", False) else ""
                    print(f"{rank:<4} {result.candidate_name:<20} {result.overall_score:<8.1f} "
                          f"{result.technical_score:<6.1f} {result.experience_score:<6.1f} "
                          f"{result.cultural_score:<8.1f} {result.education_score:<6.1f} "
                          f"{result.ai_enhanced_score:<6.1f} {feedback_enhanced}")
            else:
                print("No suitable candidates found")
                job_results[job.get('title', f'Job_{i}')] = []
                
        except Exception as e:
            print(f"Error processing {job.get('title', 'Unknown')}: {e}")
            job_results[job.get('title', f'Job_{i}')] = []
            continue
    
    total_processing_time = time.time() - total_processing_start
    
    # Save all results to JSON files
    print(f"\nSaving comprehensive results to ./scores directory...")
    save_scores(job_results, timestamp)
    
    # Summary statistics
    print(f"\n{'='*80}")
    print("PROCESSING SUMMARY")
    print(f"{'='*80}")
    
    print(f"Total Processing Time: {total_processing_time:.2f}s")
    print(f"Average Time per Job: {total_processing_time/len(jobs):.2f}s")
    print(f"Jobs Processed: {len(jobs)}")
    print(f"Candidates Evaluated: {len(candidates)}")
    print(f"Total Comparisons: {len(jobs) * len(candidates)}")
    print(f"Results saved with timestamp: {timestamp}")
    
    # Feedback integration summary
    if total_feedback > 0:
        print(f"\nFEEDBACK INTEGRATION:")
        print(f"    Total Feedback Entries: {total_feedback}")
        print(f"    AI Learning Status: Active")
    else:
        print(f"\nFEEDBACK INTEGRATION:")
        print(f"    AI Learning Status: Not Active (no feedback data)")
        print(f"    Tip: Add feedback JSON files to ./feedback directory for enhanced scoring")
    
    # Files created summary
    successful_jobs = len([j for j in job_results.values() if j])
    print(f"\nFILES CREATED:")
    print(f"    Individual job results: {successful_jobs} files")
    print(f"    Each file contains: comprehensive component scores + feedback enhancement status")
    print(f"    Scoring Components: Technical + Experience + Cultural + Education + AI + Feedback Learning")
    
    print(f"\nSCORING METHODOLOGY:")
    print(f"    Technical Score (30%): Pure technical skills matching + feedback insights")
    print(f"    Experience Score (25%): Years + level + career progression + feedback learning")
    print(f"    Cultural Score (20%): Soft skills + cultural fit + AI assessment + feedback")
    print(f"    Education Score (10%): Degree + field + certifications + feedback insights")
    print(f"    AI Enhanced Score (15%): Semantic understanding + relevancy + feedback integration")
    
    if torch.cuda.is_available():
        final_memory = torch.cuda.memory_allocated(0) / 1024**2
        print(f"GPU Memory Usage: {final_memory:.0f}MB")
        torch.cuda.empty_cache()
    
    # Performance metrics
    comparisons_per_second = (len(jobs) * len(candidates)) / total_processing_time
    print(f"\nPerformance: {comparisons_per_second:.1f} candidate comparisons per second")
    
    # Show file locations
    print(f"\nOUTPUT FILES LOCATION: ./scores/")
    print(f"    Format: [job_title]_{timestamp}.json")
    print(f"    Content: Comprehensive scores + component breakdown + feedback enhancement status")
    
    print(f"\nFEEDBACK SYSTEM USAGE:")
    print(f"    Directory: ./feedback/")
    print(f"    Format: JSON files with feedback array")
    print(f"    Required structure: {{'feedback': ['insight1', 'insight2', ...]}}")
    print(f"    All feedback is applied to general scoring enhancement")
    
    print(f"\nFeedback-enhanced job matching analysis complete!")
    
    return True

if __name__ == "__main__":
    try:
        print("SmartRecruit Job Matching System - FEEDBACK-ENHANCED SCORING EDITION")
        print("Features: 5-Component Scoring + AI Enhancement + Feedback Learning + Detailed Analytics")
        
        # Check if data directories exist and have files
        candidate_files = glob.glob("./candidates/*.json")
        job_files = glob.glob("./jd/*.json")
        feedback_files = glob.glob("./feedback/*.json")
        
        if not candidate_files or not job_files:
            print(f"\nNo JSON files found!")
            print(f"   Candidate files found: {len(candidate_files)}")
            print(f"   Job description files found: {len(job_files)}")
            print(f"   Feedback files found: {len(feedback_files)} (optional)")
            print(f"\nPlease ensure:")
            print(f"   • ./candidates directory contains JSON files with candidate data")
            print(f"   • ./jd directory contains JSON files with job descriptions")
            print(f"   • Job format: required_skills.technical_skills and required_skills.soft_skills")
            print(f"   • ./feedback directory (optional) contains JSON files with scoring feedback")
            print(f"   • Feedback format: {{'feedback': ['general insight 1', 'general insight 2', ...]}}")
        else:
            print(f"\nData Status:")
            print(f"   ✓ Candidate files: {len(candidate_files)}")
            print(f"   ✓ Job description files: {len(job_files)}")
            print(f"   {'✓' if feedback_files else '○'} Feedback files: {len(feedback_files)} {'(enhances AI scoring)' if feedback_files else '(optional - will create sample)'}")
            
            success = main()
            
            if success:
                print("\nExecution completed successfully!")
                print("Check the ./scores directory for comprehensive results")
                print("Each file contains detailed component scores and feedback enhancement status")
                print("Scoring: Technical(30%) + Cultural(20%) + Experience(25%) + Education(10%) + AI(15%)")
                print("Enhanced with continuous learning from feedback data")
            else:
                print("\nExecution completed with some issues")
            
    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user")
        # Cleanup GPU memory if available
        try:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except:
            pass
        print("Goodbye!")
        
    except Exception as e:
        print(f"\nFatal error: {e}")
        print("Troubleshooting tips:")
        print("   • Check if all dependencies are installed")
        print("   • Verify GPU drivers if using CUDA")
        print("   • Check if Ollama is running: ollama serve")
        print("   • Ensure JSON files are properly formatted with new JD structure")
        print("   • Check file permissions for ./candidates, ./jd, ./scores, and ./feedback directories")
        print("   • Verify job descriptions use nested required_skills format")
        print("   • Install missing dependencies: pip install scikit-learn")
        print("   • Feedback files should contain general insights in the format: {\"feedback\": [\"insight1\", \"insight2\", ...]}")
        
        # Cleanup GPU memory if available
        try:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except:
            pass