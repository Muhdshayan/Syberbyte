import json
import numpy as np
import torch
from typing import Dict, List, Tuple, Any, Optional
import re
from collections import defaultdict
import logging
from dataclasses import dataclass, asdict
from sentence_transformers import SentenceTransformer
import uuid
import os
import time
from datetime import datetime
import warnings
import requests
import glob
from sklearn.metrics.pairwise import cosine_similarity
import chromadb
from chromadb.config import Settings
import hashlib

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)
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
        return asdict(self)

class ChromaDBManager:
    def __init__(self, persist_directory: str = "./chromadb"):
        self.persist_directory = persist_directory
        self.client = None
        self.collections = {}
        self.initialize_chromadb()
    
    def initialize_chromadb(self):
        """Initialize ChromaDB client and collections"""
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Create collections for different types of data
            self._create_collections()
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.client = None
    
    def _create_collections(self):
        """Create necessary collections"""
        collection_configs = {
            'candidates': 'Candidate profiles and embeddings',
            'jobs': 'Job descriptions and embeddings',
            'skills': 'Skill synonyms and variations',
            'cultural_assessments': 'Cultural fit assessments cache'
        }
        
        for name, description in collection_configs.items():
            try:
                collection = self.client.get_or_create_collection(
                    name=name,
                    metadata={"description": description}
                )
                self.collections[name] = collection
            except Exception as e:
                logger.error(f"Failed to create collection {name}: {e}")
    
    def store_candidate_embedding(self, candidate: Dict, embedding: np.ndarray, career_field: str):
        """Store candidate profile embedding"""
        if not self.client or 'candidates' not in self.collections:
            return
        
        try:
            candidate_id = self._generate_id(candidate.get('name', ''), 'candidate')
            metadata = {
                'name': candidate.get('name', 'Unknown'),
                'years_experience': str(candidate.get('years_of_experience', 0)),
                'career_field': career_field,
                'education_degree': candidate.get('education', {}).get('degree', ''),
                'timestamp': datetime.now().isoformat()
            }
            
            # Ensure embedding is 1D
            if embedding.ndim > 1:
                embedding = embedding.flatten()
            
            self.collections['candidates'].upsert(
                ids=[candidate_id],
                embeddings=[embedding.tolist()],
                metadatas=[metadata],
                documents=[self._create_candidate_text(candidate)]
            )
        except Exception as e:
            logger.error(f"Failed to store candidate embedding: {e}")
    
    def store_job_embedding(self, job: Dict, embedding: np.ndarray, career_field: str):
        """Store job description embedding"""
        if not self.client or 'jobs' not in self.collections:
            return
        
        try:
            job_id = self._generate_id(job.get('title', ''), 'job')
            metadata = {
                'title': job.get('title', 'Unknown'),
                'level': job.get('level', 'entry'),
                'experience_required': str(job.get('experience', 0)),
                'career_field': career_field,
                'location': job.get('location', ''),
                'timestamp': datetime.now().isoformat()
            }
            
            # Ensure embedding is 1D
            if embedding.ndim > 1:
                embedding = embedding.flatten()
            
            self.collections['jobs'].upsert(
                ids=[job_id],
                embeddings=[embedding.tolist()],
                metadatas=[metadata],
                documents=[self._create_job_text(job)]
            )
        except Exception as e:
            logger.error(f"Failed to store job embedding: {e}")
    
    def get_candidate_embedding(self, candidate: Dict) -> Optional[np.ndarray]:
        """Retrieve candidate embedding if exists"""
        if not self.client or 'candidates' not in self.collections:
            return None
        
        try:
            candidate_id = self._generate_id(candidate.get('name', ''), 'candidate')
            results = self.collections['candidates'].get(
                ids=[candidate_id],
                include=['embeddings']
            )
            
            if results['embeddings'] is not None and len(results['embeddings']) > 0 and results['embeddings'][0] is not None:
                return np.array(results['embeddings'][0])
        except Exception as e:
            logger.error(f"Failed to retrieve candidate embedding: {e}")
        
        return None
    
    def get_job_embedding(self, job: Dict) -> Optional[np.ndarray]:
        """Retrieve job embedding if exists"""
        if not self.client or 'jobs' not in self.collections:
            return None
        
        try:
            job_id = self._generate_id(job.get('title', ''), 'job')
            results = self.collections['jobs'].get(
                ids=[job_id],
                include=['embeddings']
            )
            
            if results['embeddings'] is not None and len(results['embeddings']) > 0 and results['embeddings'][0] is not None:
                return np.array(results['embeddings'][0])
        except Exception as e:
            logger.error(f"Failed to retrieve job embedding: {e}")
        
        return None
    
    def find_similar_candidates(self, job_embedding: np.ndarray, career_field: str = None, top_k: int = 10) -> List[Dict]:
        """Find similar candidates using vector similarity"""
        if not self.client or 'candidates' not in self.collections:
            return []
        
        try:
            # Ensure embedding is 1D
            if job_embedding.ndim > 1:
                job_embedding = job_embedding.flatten()
            
            where_clause = {}
            if career_field:
                where_clause = {"career_field": career_field}
            
            # Check if collection is empty
            collection_count = self.collections['candidates'].count()
            if collection_count == 0:
                return []
            
            # Limit top_k to available candidates
            actual_top_k = min(top_k, collection_count)
            
            results = self.collections['candidates'].query(
                query_embeddings=[job_embedding.tolist()],
                n_results=actual_top_k,
                where=where_clause if where_clause else None,
                include=['metadatas', 'distances']
            )
            
            similar_candidates = []
            if results['metadatas'] is not None and len(results['metadatas']) > 0:
                for i, metadata in enumerate(results['metadatas'][0]):
                    similarity_score = 1 - results['distances'][0][i]  # Convert distance to similarity
                    candidate_info = {
                        'name': metadata.get('name'),
                        'similarity_score': float(similarity_score),
                        'career_field': metadata.get('career_field'),
                        'years_experience': metadata.get('years_experience')
                    }
                    similar_candidates.append(candidate_info)
            
            return similar_candidates
        except Exception as e:
            logger.error(f"Failed to find similar candidates: {e}")
            return []
    
    def store_skill_variations(self, skill: str, career_field: str, variations: List[str]):
        """Store skill variations in ChromaDB"""
        if not self.client or 'skills' not in self.collections:
            return
        
        try:
            skill_id = self._generate_id(f"{skill}_{career_field}", 'skill')
            metadata = {
                'original_skill': skill,
                'career_field': career_field,
                'variations_count': str(len(variations)),
                'timestamp': datetime.now().isoformat()
            }
            
            self.collections['skills'].upsert(
                ids=[skill_id],
                metadatas=[metadata],
                documents=[json.dumps({'skill': skill, 'variations': variations})]
            )
        except Exception as e:
            logger.error(f"Failed to store skill variations: {e}")
    
    def get_skill_variations(self, skill: str, career_field: str) -> Optional[List[str]]:
        """Retrieve skill variations from ChromaDB"""
        if not self.client or 'skills' not in self.collections:
            return None
        
        try:
            skill_id = self._generate_id(f"{skill}_{career_field}", 'skill')
            results = self.collections['skills'].get(
                ids=[skill_id],
                include=['documents']
            )
            
            if results['documents'] is not None and len(results['documents']) > 0 and results['documents'][0] is not None:
                skill_data = json.loads(results['documents'][0])
                return skill_data.get('variations', [])
        except Exception as e:
            logger.error(f"Failed to retrieve skill variations: {e}")
        
        return None
    
    def store_cultural_assessment(self, candidate_name: str, job_title: str, score: float, career_field: str):
        """Store cultural assessment result"""
        if not self.client or 'cultural_assessments' not in self.collections:
            return
        
        try:
            assessment_id = self._generate_id(f"{candidate_name}_{job_title}", 'cultural')
            metadata = {
                'candidate_name': candidate_name,
                'job_title': job_title,
                'score': str(score),
                'career_field': career_field,
                'timestamp': datetime.now().isoformat()
            }
            
            self.collections['cultural_assessments'].upsert(
                ids=[assessment_id],
                metadatas=[metadata],
                documents=[f"Cultural fit assessment for {candidate_name} and {job_title}"]
            )
        except Exception as e:
            logger.error(f"Failed to store cultural assessment: {e}")
    
    def get_cultural_assessment(self, candidate_name: str, job_title: str) -> Optional[float]:
        """Retrieve cultural assessment if exists"""
        if not self.client or 'cultural_assessments' not in self.collections:
            return None
        
        try:
            assessment_id = self._generate_id(f"{candidate_name}_{job_title}", 'cultural')
            results = self.collections['cultural_assessments'].get(
                ids=[assessment_id],
                include=['metadatas']
            )
            
            if results['metadatas'] is not None and len(results['metadatas']) > 0 and results['metadatas'][0] is not None:
                return float(results['metadatas'][0]['score'])
        except Exception as e:
            logger.error(f"Failed to retrieve cultural assessment: {e}")
        
        return None
    
    def _generate_id(self, identifier: str, prefix: str) -> str:
        """Generate consistent ID for ChromaDB"""
        # Handle empty or None identifiers
        if not identifier:
            identifier = "unknown"
        combined = f"{prefix}_{identifier}".lower()
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _create_candidate_text(self, candidate: Dict) -> str:
        """Create text representation of candidate for ChromaDB"""
        parts = [f"Candidate: {candidate.get('name', 'Unknown')}", f"Experience: {candidate.get('years_of_experience', 0)} years"]
        
        education = candidate.get('education', {})
        if education:
            degree = education.get('degree', '')
            field = education.get('field', '')
            if degree or field: 
                parts.append(f"Education: {degree} {field}".strip())
        
        return '. '.join(parts)
    
    def _create_job_text(self, job: Dict) -> str:
        """Create text representation of job for ChromaDB"""
        parts = [
            f"Job: {job.get('title', 'Unknown')}", 
            f"Level: {job.get('level', 'entry')}", 
            f"Experience Required: {job.get('experience', 0)} years", 
            f"Location: {job.get('location', 'Unknown')}"
        ]
        return '. '.join(parts)
    
    def cleanup_old_entries(self, days_old: int = 30):
        """Clean up old entries from ChromaDB"""
        if not self.client:
            return
        
        try:
            cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            cutoff_iso = datetime.fromtimestamp(cutoff_date).isoformat()
            
            for collection_name, collection in self.collections.items():
                try:
                    # Get all items with timestamps older than cutoff
                    all_items = collection.get(include=['metadatas'])
                    old_ids = []
                    
                    if all_items['ids'] is not None and len(all_items['ids']) > 0:
                        for i, metadata in enumerate(all_items['metadatas']):
                            if metadata and metadata.get('timestamp', '') < cutoff_iso:
                                old_ids.append(all_items['ids'][i])
                    
                    # Delete old items
                    if old_ids:
                        collection.delete(ids=old_ids)
                        logger.info(f"Cleaned up {len(old_ids)} old entries from {collection_name}")
                        
                except Exception as e:
                    logger.error(f"Failed to cleanup collection {collection_name}: {e}")
        except Exception as e:
            logger.error(f"Failed to cleanup old entries: {e}")

class FeedbackManager:
    def __init__(self, feedback_dir: str = "./feedback"):
        self.feedback_dir = feedback_dir
        self.feedback_cache = {'general': []}
        self.load_feedback()
    
    def load_feedback(self):
        os.makedirs(self.feedback_dir, exist_ok=True)
        for file_path in glob.glob(f"{self.feedback_dir}/*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    feedback_data = json.load(f)
                if isinstance(feedback_data, dict) and 'feedback' in feedback_data:
                    feedback_list = feedback_data['feedback']
                    if isinstance(feedback_list, list):
                        for feedback_text in feedback_list:
                            if isinstance(feedback_text, str) and feedback_text.strip():
                                self.feedback_cache['general'].append(feedback_text.strip())
            except Exception as e:
                logger.error(f"Failed to load feedback from {file_path}: {e}")
    
    def get_feedback_for_category(self, category: str) -> List[str]:
        return self.feedback_cache.get('general', [])[-5:]
    
    def format_feedback_for_prompt(self, category: str = None) -> str:
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
    def __init__(self, ollama_url: str = "http://localhost:11434", feedback_manager=None, chromadb_manager=None):
        self.ollama_url = ollama_url
        self.synonym_cache = {}
        self.relevancy_cache = {}
        self.feedback_manager = feedback_manager
        self.chromadb_manager = chromadb_manager
        
    def _call_ollama_api(self, prompt: str, model: str = "mistral", timeout: int = 30, max_retries: int = 3) -> str:
        """Call Ollama API with retry logic and better error handling"""
        for attempt in range(max_retries):
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
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    result = response.json().get("response", "").strip()
                    if result:  # Only return if we got a valid response
                        return result
                    else:
                        logger.warning(f"Empty response from Ollama on attempt {attempt + 1}")
                else:
                    logger.warning(f"Ollama API returned status {response.status_code} on attempt {attempt + 1}")
                    
            except requests.exceptions.ConnectionError:
                logger.error(f"Cannot connect to Ollama server at {self.ollama_url} on attempt {attempt + 1}")
            except requests.exceptions.Timeout:
                logger.error(f"Ollama API timeout on attempt {attempt + 1}")
            except Exception as e:
                logger.error(f"Ollama API call failed on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
        
        # If all retries failed, return basic fallback
        logger.error(f"All {max_retries} attempts to call Ollama API failed. Using basic fallback.")
        return ""
    
    def get_career_field_from_job(self, job_description: Dict) -> str:
        title = job_description.get('title', '').lower()
        all_skills = []
        required_skills = job_description.get('required_skills', {})
        if 'technical_skills' in required_skills:
            all_skills.extend(list(required_skills['technical_skills'].keys()))
        if 'soft_skills' in required_skills:
            all_skills.extend(list(required_skills['soft_skills'].keys()))
        
        if any(term in title for term in ['data', 'scientist', 'analyst', 'ml', 'ai']): return "data science"
        elif any(term in title for term in ['developer', 'engineer', 'programmer', 'software']): return "software development"
        elif any(term in title for term in ['marketing', 'brand', 'digital', 'social media']): return "marketing"
        elif any(term in title for term in ['designer', 'ui', 'ux', 'graphic', 'creative']): return "design"
        elif any(term in title for term in ['finance', 'accounting', 'financial', 'analyst']): return "finance"
        elif any(term in title for term in ['hr', 'human resources', 'recruitment', 'talent']): return "human resources"
        elif any(term in title for term in ['sales', 'business development', 'account']): return "sales"
        elif any(term in title for term in ['project manager', 'product manager', 'scrum']): return "project management"
        elif any(term in title for term in ['devops', 'infrastructure', 'cloud', 'system admin']): return "devops"
        elif any(term in title for term in ['security', 'cyber', 'information security']): return "cybersecurity"
        elif any(term in title for term in ['business', 'analytics', 'intelligence', 'strategy']): return "business analytics"
        elif any(term in title for term in ['civil engineer', 'structural', 'construction']): return "civil engineering"
        return "general"
    
    def get_career_field_from_candidate(self, candidate: Dict) -> str:
        education = candidate.get('education', {})
        degree = education.get('degree', '').lower()
        
        if any(term in degree for term in ['data science', 'data analytics', 'business analytics']): return "business analytics"
        elif any(term in degree for term in ['computer science', 'software', 'programming']): return "software development"
        elif any(term in degree for term in ['design', 'art', 'graphics']): return "design"
        elif any(term in degree for term in ['marketing', 'business administration']): return "marketing"
        elif any(term in degree for term in ['finance', 'accounting']): return "finance"
        elif any(term in degree for term in ['civil engineering']): return "civil engineering"
        elif any(term in degree for term in ['engineering']): return "engineering"
        
        all_skills = self._get_all_candidate_skills_for_analysis(candidate)
        skill_names = ' '.join(all_skills.keys()).lower()
        
        if any(term in skill_names for term in ['data science', 'data visualization', 'business intelligence', 'tableau', 'power bi']): return "business analytics"
        elif any(term in skill_names for term in ['python', 'programming', 'software development', 'java', 'javascript']): return "software development"
        elif any(term in skill_names for term in ['design', 'ui', 'ux', 'canva', 'photoshop', 'illustrator']): return "design"
        elif any(term in skill_names for term in ['marketing', 'business planning', 'social media']): return "marketing"
        elif any(term in skill_names for term in ['excel', 'word', 'powerpoint', 'office']): return "business analytics"
        elif any(term in skill_names for term in ['autocad', 'structural design', 'construction']): return "civil engineering"
        return "general"
    
    def _get_all_candidate_skills_for_analysis(self, candidate: Dict) -> Dict[str, int]:
        skills = candidate.get('skills', {})
        all_skills = {}
        
        def flatten_skills(skill_dict, prefix=""):
            for key, value in skill_dict.items():
                if isinstance(value, dict):
                    flatten_skills(value, f"{prefix}{key} " if prefix else f"{key} ")
                else:
                    skill_name = f"{prefix}{key}".strip()
                    all_skills[skill_name] = 1
        
        if 'technical_skills' in skills: flatten_skills(skills['technical_skills'])
        if 'soft_skills' in skills: flatten_skills(skills['soft_skills'])
        return all_skills
    
    def get_skill_variations(self, skill: str, career_field: str = "general") -> List[str]:
        cache_key = f"{skill.lower()}_{career_field.lower()}"
        if cache_key in self.synonym_cache:
            return self.synonym_cache[cache_key]
        
        # Check ChromaDB first
        if self.chromadb_manager:
            cached_variations = self.chromadb_manager.get_skill_variations(skill, career_field)
            if cached_variations:
                self.synonym_cache[cache_key] = cached_variations
                return cached_variations
        
        feedback_text = self.feedback_manager.format_feedback_for_prompt() if self.feedback_manager else ""
        prompt = f"""Generate synonyms and variations for the skill "{skill}" in {career_field} careers.
Include: Common abbreviations and acronyms, Related technologies, tools, or concepts, Different ways this skill might be written on resumes
Limit to maximum 10 most relevant variations
{feedback_text}
Skill: {skill}
Career Field: {career_field}
Variations (comma-separated):"""

        response = self._call_ollama_api(prompt)
        if not response:
            # Basic fallback variations
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
        
        # Store in ChromaDB for future use
        if self.chromadb_manager:
            self.chromadb_manager.store_skill_variations(skill, career_field, variations)
        
        return variations
    
    def _parse_variations_response(self, response: str, original_skill: str) -> List[str]:
        variations = [original_skill.lower()]
        response = response.replace("Variations:", "").strip()
        potential_variations = re.split(r'[,\n\r\t;]', response)
        
        for variation in potential_variations:
            cleaned = variation.strip().lower()
            if (cleaned and len(cleaned) > 1 and len(cleaned) < 50 and
                not cleaned.startswith(('note:', 'here are', 'these include', 'variations:')) and
                cleaned not in variations):
                variations.append(cleaned)
        return variations[:10]
    
    def calculate_skill_similarity(self, skill1: str, skill2: str, career_field: str = "general") -> float:
        variations1 = set(self.get_skill_variations(skill1, career_field))
        variations2 = set(self.get_skill_variations(skill2, career_field))
        
        if skill1.lower() == skill2.lower(): return 1.0
        
        intersection = variations1.intersection(variations2)
        if intersection: return 0.95
        
        for v1 in variations1:
            for v2 in variations2:
                if len(v1) > 2 and len(v2) > 2:
                    if v1 in v2 or v2 in v1: return 0.6
        return 0.0
    
    def ai_assess_cultural_fit(self, candidate: Dict, job: Dict, career_field: str) -> float:
        candidate_name = candidate.get('name', 'unknown')
        job_title = job.get('title', 'unknown')
        
        # Check ChromaDB first
        if self.chromadb_manager:
            cached_score = self.chromadb_manager.get_cultural_assessment(candidate_name, job_title)
            if cached_score is not None:
                return cached_score
        
        cache_key = f"cultural_{candidate_name}_{job_title}"
        if cache_key in self.relevancy_cache:
            return self.relevancy_cache[cache_key]
        
        candidate_soft = candidate.get('skills', {}).get('soft_skills', {})
        job_soft = job.get('required_skills', {}).get('soft_skills', {})
        feedback_text = self.feedback_manager.format_feedback_for_prompt() if self.feedback_manager else ""
        
        prompt = f"""Assess the cultural fit between this candidate and job position in {career_field}.
Job: {job.get('title', 'Unknown')}
Job Level: {job.get('level', 'entry')}
Required Soft Skills: {list(job_soft.keys())}
Job Location: {job.get('location', 'Unknown')}
Work Type: {job.get('location_type', 'Unknown')}
Candidate: {candidate.get('name', 'Unknown')}
Candidate Soft Skills: {list(candidate_soft.keys())}
Experience Level: {candidate.get('years_of_experience', 0)} years
{feedback_text}
Rate cultural fit from 0.0 to 1.0 considering: Communication style match, Leadership potential vs requirements, Team collaboration abilities, Work environment fit, Career stage appropriateness
Respond with only the numerical score (e.g., 0.82).
Cultural fit score:"""
        
        response = self._call_ollama_api(prompt)
        try:
            score_match = re.search(r'(\d+\.?\d*)', response)
            if score_match:
                score = float(score_match.group(1))
                if score > 1: score = score / 10 if score <= 10 else score / 100
                score = max(0.0, min(1.0, score))
                self.relevancy_cache[cache_key] = score
                
                # Store in ChromaDB for future use
                if self.chromadb_manager:
                    self.chromadb_manager.store_cultural_assessment(candidate_name, job_title, score, career_field)
                
                return score
        except Exception as e:
            logger.error(f"Error parsing cultural fit score: {e}")
        
        return self._basic_cultural_fit_calculation(candidate, job)
    
    def _basic_cultural_fit_calculation(self, candidate: Dict, job: Dict) -> float:
        candidate_soft = set(candidate.get('skills', {}).get('soft_skills', {}).keys())
        job_soft = set(job.get('required_skills', {}).get('soft_skills', {}).keys())
        if not job_soft: return 0.75
        return len(candidate_soft.intersection(job_soft)) / len(job_soft)

class ModelManager:
    def __init__(self):
        self.embedding_model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_models(self):
        """Load only the embedding model"""
        if self.device == "cuda": 
            torch.cuda.empty_cache()
        
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            if self.device == "cuda": 
                self.embedding_model = self.embedding_model.to('cuda')
            logger.info(f"Embedding model loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None

class SmartRecruitMatcher:
    def __init__(self, ollama_url: str = "http://localhost:11434", feedback_dir: str = "./feedback", chromadb_dir: str = "./chromadb"):
        self.model_manager = ModelManager()
        self.skill_mapper = None
        self.ollama_url = ollama_url
        self.feedback_manager = FeedbackManager(feedback_dir)
        self.chromadb_manager = ChromaDBManager(chromadb_dir)
        
    def initialize(self):
        """Initialize the matcher with simplified model loading"""
        # Test Ollama connection first
        self._test_ollama_connection()
        
        # Load only the embedding model
        self.model_manager.load_models()
        
        # Initialize the skill mapper
        self.skill_mapper = DynamicSkillSynonymMapper(
            ollama_url=self.ollama_url,
            feedback_manager=self.feedback_manager,
            chromadb_manager=self.chromadb_manager
        )
    
    def _test_ollama_connection(self):
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("Successfully connected to Ollama server")
            else:
                logger.warning(f"Ollama server responded with status {response.status_code}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Ollama server at {self.ollama_url}")
            logger.error("Please ensure Ollama is running and accessible")
        except Exception as e:
            logger.error(f"Error testing Ollama connection: {e}")
    
    def _get_candidate_technical_skills(self, candidate: Dict) -> Dict[str, int]:
        skills = candidate.get('skills', {})
        technical_skills = {}
        
        def extract_skills_recursive(skill_dict, prefix=""):
            for key, value in skill_dict.items():
                if isinstance(value, dict):
                    extract_skills_recursive(value, f"{prefix}{key} " if prefix else f"{key} ")
                elif isinstance(value, (int, float)):
                    technical_skills[f"{prefix}{key}".strip()] = int(value)
                elif isinstance(value, str) and value.isdigit():
                    technical_skills[f"{prefix}{key}".strip()] = int(value)
                else:
                    technical_skills[f"{prefix}{key}".strip()] = 50
        
        if 'technical_skills' in skills: extract_skills_recursive(skills['technical_skills'])
        return technical_skills
    
    def _get_candidate_soft_skills(self, candidate: Dict) -> Dict[str, int]:
        skills = candidate.get('skills', {})
        soft_skills = {}
        
        def extract_skills_recursive(skill_dict, prefix=""):
            for key, value in skill_dict.items():
                if isinstance(value, dict):
                    extract_skills_recursive(value, f"{prefix}{key} " if prefix else f"{key} ")
                elif isinstance(value, (int, float)):
                    soft_skills[f"{prefix}{key}".strip()] = int(value)
                elif isinstance(value, str) and value.isdigit():
                    soft_skills[f"{prefix}{key}".strip()] = int(value)
                else:
                    soft_skills[f"{prefix}{key}".strip()] = 50
        
        if 'soft_skills' in skills: extract_skills_recursive(skills['soft_skills'])
        return soft_skills
    
    def _get_job_technical_skills(self, job: Dict) -> Dict[str, int]:
        required_skills = job.get('required_skills', {})
        technical_skills = {}
        if 'technical_skills' in required_skills:
            for skill, level in required_skills['technical_skills'].items():
                try:
                    technical_skills[skill] = int(level)
                except (ValueError, TypeError):
                    technical_skills[skill] = 50  # Default level
        return technical_skills
    
    def _get_job_soft_skills(self, job: Dict) -> Dict[str, int]:
        required_skills = job.get('required_skills', {})
        soft_skills = {}
        if 'soft_skills' in required_skills:
            for skill, level in required_skills['soft_skills'].items():
                try:
                    soft_skills[skill] = int(level)
                except (ValueError, TypeError):
                    soft_skills[skill] = 50  # Default level
        return soft_skills
    
    def calculate_technical_score(self, candidate: Dict, job: Dict, career_field: str) -> float:
        candidate_tech = self._get_candidate_technical_skills(candidate)
        job_tech = self._get_job_technical_skills(job)
        if not job_tech: return 50.0
        
        total_score = 0
        total_weight = 0
        
        for req_skill, req_level in job_tech.items():
            req_level = int(req_level)
            best_match_score = 0
            
            for cand_skill, cand_level in candidate_tech.items():
                cand_level = int(cand_level)
                similarity = self.skill_mapper.calculate_skill_similarity(req_skill, cand_skill, career_field)
                if similarity > 0.5:
                    level_confidence = min(1.2, cand_level / max(req_level, 1))  # Avoid division by zero
                    match_score = similarity * level_confidence * 100
                    best_match_score = max(best_match_score, match_score)
            
            total_score += best_match_score * req_level
            total_weight += req_level
        
        return min(100.0, (total_score / total_weight) if total_weight > 0 else 0)
    
    def calculate_experience_score(self, candidate: Dict, job: Dict) -> float:
        try:
            candidate_years = float(candidate.get('years_of_experience', 0))
            required_years = float(job.get('experience', 0))
        except (ValueError, TypeError):
            candidate_years = 0
            required_years = 0
            
        job_level = job.get('level', 'entry').lower()
        
        if required_years == 0:
            years_score = 40
        else:
            years_ratio = candidate_years / required_years
            if years_ratio >= 1.0:
                years_score = min(40, 30 + (years_ratio - 1.0) * 10)
            else:
                years_score = years_ratio * 30
        
        level_score = self._calculate_level_appropriateness(candidate_years, job_level)
        progression_score = self._assess_career_progression(candidate, job)
        
        return min(100.0, years_score + level_score + progression_score)
    
    def _calculate_level_appropriateness(self, years: float, level: str) -> float:
        level_ranges = {
            'entry': (0, 2), 'junior': (1, 3), 'intermediate': (3, 6),
            'senior': (5, 10), 'lead': (8, 15), 'expert': (10, 20)
        }
        min_years, max_years = level_ranges.get(level, (0, 5))
        
        if min_years <= years <= max_years: return 35
        elif years < min_years: return max(0, 35 - (min_years - years) * 10)
        else: return max(20, 35 - (years - max_years) * 2)
    
    def _assess_career_progression(self, candidate: Dict, job: Dict) -> float:
        try:
            years = float(candidate.get('years_of_experience', 0))
        except (ValueError, TypeError):
            years = 0
            
        education = candidate.get('education', {})
        degree = education.get('degree', '').lower()
        
        education_score = 0
        if any(term in degree for term in ['master', 'mba', 'phd']): education_score = 10
        elif any(term in degree for term in ['bachelor', 'degree']): education_score = 5
        
        return education_score + min(15, years * 2)
    
    def calculate_cultural_score(self, candidate: Dict, job: Dict, career_field: str) -> float:
        candidate_soft = self._get_candidate_soft_skills(candidate)
        job_soft = self._get_job_soft_skills(job)
        if not job_soft: return 75.0
        
        soft_skills_score = self._calculate_soft_skills_match(candidate_soft, job_soft, career_field)
        cultural_fit_score = self.skill_mapper.ai_assess_cultural_fit(candidate, job, career_field) * 100
        return soft_skills_score * 0.6 + cultural_fit_score * 0.4
    
    def _calculate_soft_skills_match(self, candidate_soft: Dict, job_soft: Dict, career_field: str) -> float:
        total_score = 0
        total_weight = 0
        
        for req_skill, req_level in job_soft.items():
            req_level = int(req_level)
            best_match_score = 0
            
            for cand_skill, cand_level in candidate_soft.items():
                cand_level = int(cand_level)
                similarity = self.skill_mapper.calculate_skill_similarity(req_skill, cand_skill, career_field)
                if similarity > 0.5:
                    level_confidence = min(1.0, cand_level / max(req_level, 1))  # Avoid division by zero
                    match_score = similarity * level_confidence * 100
                    best_match_score = max(best_match_score, match_score)
            
            total_score += best_match_score * req_level
            total_weight += req_level
        
        return (total_score / total_weight) if total_weight > 0 else 0
    
    def calculate_education_score(self, candidate: Dict, job: Dict) -> float:
        candidate_education = candidate.get('education', {})
        job_education_req = job.get('education_level', '')
        candidate_degree = candidate_education.get('degree', '').lower()
        candidate_field = candidate_education.get('field', '').lower()
        
        education_score = self._match_education_level(candidate_degree, job_education_req)
        field_score = self._assess_field_relevance(candidate_field, job)
        cert_score = self._assess_certifications(candidate_education, job)
        
        return min(100.0, education_score * 0.6 + field_score * 0.3 + cert_score * 0.1)
    
    def _match_education_level(self, candidate_degree: str, job_requirement: str) -> float:
        education_hierarchy = {
            'phd': 5, 'doctorate': 5, 'master': 4, 'mba': 4, 'ms': 4,
            'bachelor': 3, 'degree': 3, 'associate': 2, 'diploma': 2,
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
        
        if required_level == 0: return 80
        if candidate_level >= required_level: return 100
        elif candidate_level == required_level - 1: return 70
        else: return max(30, 100 - (required_level - candidate_level) * 25)
    
    def _assess_field_relevance(self, candidate_field: str, job: Dict) -> float:
        job_title = job.get('title', '').lower()
        career_field = self.skill_mapper.get_career_field_from_job(job)
        
        if candidate_field in job_title or job_title in candidate_field: return 100
        
        field_mappings = {
            'marketing': ['marketing', 'business', 'communications'],
            'engineering': ['engineering', 'technology', 'computer science'],
            'finance': ['finance', 'accounting', 'economics', 'business'],
            'design': ['design', 'art', 'creative'],
            'data science': ['data science', 'statistics', 'mathematics', 'computer science']
        }
        
        relevant_fields = field_mappings.get(career_field, [])
        for field in relevant_fields:
            if field in candidate_field: return 80
        return 50
    
    def _assess_certifications(self, education: Dict, job: Dict) -> float:
        certifications = education.get('certifications', [])
        if isinstance(certifications, str): certifications = [certifications]
        if not certifications: return 50
        return min(100, len(certifications) * 20 + 50)
    
    def calculate_ai_enhanced_score(self, candidate: Dict, job: Dict) -> float:
        if not self.model_manager.embedding_model:
            return self._fallback_semantic_score(candidate, job)
        
        try:
            # Check if embeddings are cached in ChromaDB
            candidate_embedding = self.chromadb_manager.get_candidate_embedding(candidate) if self.chromadb_manager else None
            job_embedding = self.chromadb_manager.get_job_embedding(job) if self.chromadb_manager else None
            
            # Generate embeddings if not cached
            if candidate_embedding is None:
                candidate_text = self._create_candidate_profile_text(candidate)
                candidate_embedding = self.model_manager.embedding_model.encode([candidate_text])[0]
                
                # Store in ChromaDB for future use
                if self.chromadb_manager:
                    career_field = self.skill_mapper.get_career_field_from_candidate(candidate)
                    self.chromadb_manager.store_candidate_embedding(candidate, candidate_embedding, career_field)
            
            if job_embedding is None:
                job_text = self._create_job_description_text(job)
                job_embedding = self.model_manager.embedding_model.encode([job_text])[0]
                
                # Store in ChromaDB for future use
                if self.chromadb_manager:
                    career_field = self.skill_mapper.get_career_field_from_job(job)
                    self.chromadb_manager.store_job_embedding(job, job_embedding, career_field)
            
            # Calculate similarity
            similarity = cosine_similarity([candidate_embedding], [job_embedding])[0][0]
            return float(similarity * 100)
        except Exception as e:
            logger.error(f"Error in AI enhanced score calculation: {e}")
            return self._fallback_semantic_score(candidate, job)
    
    def _create_candidate_profile_text(self, candidate: Dict) -> str:
        parts = [f"Candidate: {candidate.get('name', 'Unknown')}", f"Experience: {candidate.get('years_of_experience', 0)} years"]
        
        education = candidate.get('education', {})
        if education:
            degree = education.get('degree', '')
            field = education.get('field', '')
            if degree or field: parts.append(f"Education: {degree} {field}".strip())
        
        tech_skills = self._get_candidate_technical_skills(candidate)
        if tech_skills:
            skills_text = ', '.join([f"{skill}({level})" for skill, level in tech_skills.items()])
            parts.append(f"Technical Skills: {skills_text}")
        
        soft_skills = self._get_candidate_soft_skills(candidate)
        if soft_skills:
            skills_text = ', '.join([f"{skill}({level})" for skill, level in soft_skills.items()])
            parts.append(f"Soft Skills: {skills_text}")
        
        return '. '.join(parts)
    
    def _create_job_description_text(self, job: Dict) -> str:
        parts = [
            f"Job: {job.get('title', 'Unknown')}", f"Level: {job.get('level', 'entry')}", 
            f"Experience Required: {job.get('experience', 0)} years", f"Location: {job.get('location', 'Unknown')}"
        ]
        
        tech_skills = self._get_job_technical_skills(job)
        if tech_skills:
            skills_text = ', '.join([f"{skill}({level})" for skill, level in tech_skills.items()])
            parts.append(f"Technical Requirements: {skills_text}")
        
        soft_skills = self._get_job_soft_skills(job)
        if soft_skills:
            skills_text = ', '.join([f"{skill}({level})" for skill, level in soft_skills.items()])
            parts.append(f"Soft Skills Required: {skills_text}")
        
        important_skills = job.get('important_skills', [])
        if important_skills: parts.append(f"Critical Skills: {', '.join(important_skills)}")
        
        return '. '.join(parts)
    
    def _fallback_semantic_score(self, candidate: Dict, job: Dict) -> float:
        candidate_text = self._create_candidate_profile_text(candidate).lower()
        job_text = self._create_job_description_text(job).lower()
        job_keywords = set(re.findall(r'\b\w{3,}\b', job_text))
        candidate_keywords = set(re.findall(r'\b\w{3,}\b', candidate_text))
        common_keywords = job_keywords.intersection(candidate_keywords)
        total_keywords = job_keywords.union(candidate_keywords)
        if not total_keywords: return 50.0
        return min(100.0, (len(common_keywords) / len(total_keywords)) * 200)
    
    def calculate_matching_score(self, candidate: Dict, job: Dict) -> MatchingResult:
        job_career_field = self.skill_mapper.get_career_field_from_job(job)
        candidate_career_field = self.skill_mapper.get_career_field_from_candidate(candidate)
        
        technical_score = self.calculate_technical_score(candidate, job, job_career_field)
        experience_score = self.calculate_experience_score(candidate, job)
        cultural_score = self.calculate_cultural_score(candidate, job, job_career_field)
        education_score = self.calculate_education_score(candidate, job)
        ai_enhanced_score = self.calculate_ai_enhanced_score(candidate, job)
        
        overall_score = (technical_score * 0.30 + cultural_score * 0.20 + experience_score * 0.25 + 
                        education_score * 0.10 + ai_enhanced_score * 0.15)
        
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
                "feedback_enhanced": bool(self.feedback_manager.feedback_cache.get('general')),
                "chromadb_enhanced": self.chromadb_manager.client is not None,
                "ollama_enhanced": True,  # Since we're using Ollama exclusively
                "scoring_weights": {"technical": "30%", "cultural": "20%", "experience": "25%", "education": "10%", "ai_enhanced": "15%"}
            }
        )
    
    def _get_technical_skill_matches(self, candidate: Dict, job: Dict, career_field: str) -> Dict:
        candidate_tech = self._get_candidate_technical_skills(candidate)
        job_tech = self._get_job_technical_skills(job)
        matches = {}
        
        for req_skill, req_level in job_tech.items():
            best_match = {"candidate_skill": None, "similarity": 0, "candidate_level": 0, "required_level": req_level, "confidence": 0}
            
            for cand_skill, cand_level in candidate_tech.items():
                similarity = self.skill_mapper.calculate_skill_similarity(req_skill, cand_skill, career_field)
                if similarity > best_match["similarity"]:
                    level_conf = min(1.2, int(cand_level) / max(int(req_level), 1))  # Avoid division by zero
                    confidence = similarity * level_conf
                    best_match.update({
                        "candidate_skill": cand_skill, "similarity": round(similarity, 2),
                        "candidate_level": cand_level, "confidence": round(confidence, 2)
                    })
            matches[req_skill] = best_match
        return matches
    
    def _get_soft_skill_matches(self, candidate: Dict, job: Dict, career_field: str) -> Dict:
        candidate_soft = self._get_candidate_soft_skills(candidate)
        job_soft = self._get_job_soft_skills(job)
        matches = {}
        
        for req_skill, req_level in job_soft.items():
            best_match = {"candidate_skill": None, "similarity": 0, "candidate_level": 0, "required_level": req_level, "confidence": 0}
            
            for cand_skill, cand_level in candidate_soft.items():
                similarity = self.skill_mapper.calculate_skill_similarity(req_skill, cand_skill, career_field)
                if similarity > best_match["similarity"]:
                    level_conf = min(1.0, int(cand_level) / max(int(req_level), 1))  # Avoid division by zero
                    confidence = similarity * level_conf
                    best_match.update({
                        "candidate_skill": cand_skill, "similarity": round(similarity, 2),
                        "candidate_level": cand_level, "confidence": round(confidence, 2)
                    })
            matches[req_skill] = best_match
        return matches
    
    def _get_important_skill_coverage(self, candidate: Dict, job: Dict, career_field: str) -> List:
        important_skills = job.get('important_skills', [])
        candidate_tech = self._get_candidate_technical_skills(candidate)
        candidate_soft = self._get_candidate_soft_skills(candidate)
        all_candidate_skills = {**candidate_tech, **candidate_soft}
        coverage = []
        
        for imp_skill in important_skills:
            best_match = {"important_skill": imp_skill, "candidate_skill": None, "similarity": 0, "candidate_level": 0, "covered": False}
            
            for cand_skill, cand_level in all_candidate_skills.items():
                similarity = self.skill_mapper.calculate_skill_similarity(imp_skill, cand_skill, career_field)
                if similarity > best_match["similarity"]:
                    best_match.update({
                        "candidate_skill": cand_skill, "similarity": round(similarity, 2),
                        "candidate_level": cand_level, "covered": similarity > 0.6
                    })
            coverage.append(best_match)
        return coverage
    
    def find_top_candidates_for_job(self, job: Dict, candidates: List[Dict], top_n: int = 5) -> List[MatchingResult]:
        results = []
        for candidate in candidates:
            try:
                result = self.calculate_matching_score(candidate, job)
                results.append(result)
            except Exception as e:
                logger.error(f"Error calculating score for candidate {candidate.get('name', 'Unknown')}: {e}")
                continue
        results.sort(key=lambda x: x.overall_score, reverse=True)
        return results[:top_n]
    
    def find_similar_candidates_using_chromadb(self, job: Dict, top_k: int = 10) -> List[Dict]:
        """Use ChromaDB to find similar candidates efficiently"""
        if not self.chromadb_manager or not self.model_manager.embedding_model:
            return []
        
        try:
            # Get or create job embedding
            job_embedding = self.chromadb_manager.get_job_embedding(job)
            if job_embedding is None:
                job_text = self._create_job_description_text(job)
                job_embedding = self.model_manager.embedding_model.encode([job_text])[0]
                career_field = self.skill_mapper.get_career_field_from_job(job)
                self.chromadb_manager.store_job_embedding(job, job_embedding, career_field)
            
            # Find similar candidates
            career_field = self.skill_mapper.get_career_field_from_job(job)
            similar_candidates = self.chromadb_manager.find_similar_candidates(
                job_embedding, career_field, top_k
            )
            
            return similar_candidates
        except Exception as e:
            logger.error(f"Failed to find similar candidates using ChromaDB: {e}")
            return []

def load_json_data():
    os.makedirs("./candidates", exist_ok=True)
    os.makedirs("./jd", exist_ok=True)
    os.makedirs("./scores", exist_ok=True)
    os.makedirs("./feedback", exist_ok=True)
    
    candidates = []
    jobs = []
    
    for file_path in glob.glob("./candidates/*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = json.load(f)
                
                if isinstance(file_content, list):
                    for candidate_data in file_content:
                        if validate_candidate_data(candidate_data):
                            candidates.append(candidate_data)
                elif isinstance(file_content, dict):
                    if 'candidates' in file_content and isinstance(file_content['candidates'], list):
                        for candidate_data in file_content['candidates']:
                            if validate_candidate_data(candidate_data):
                                candidates.append(candidate_data)
                    elif validate_candidate_data(file_content):
                        candidates.append(file_content)
        except Exception as e:
            logger.error(f"Error loading candidate file {file_path}: {e}")
    
    for file_path in glob.glob("./jd/*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = json.load(f)
                
                if isinstance(file_content, list):
                    for job_data in file_content:
                        if validate_job_data(job_data):
                            jobs.append(job_data)
                elif isinstance(file_content, dict):
                    if 'jobs' in file_content and isinstance(file_content['jobs'], list):
                        for job_data in file_content['jobs']:
                            if validate_job_data(job_data):
                                jobs.append(job_data)
                    elif validate_job_data(file_content):
                        jobs.append(file_content)
        except Exception as e:
            logger.error(f"Error loading job file {file_path}: {e}")
    
    return candidates, jobs

def validate_candidate_data(candidate: Dict) -> bool:
    if not isinstance(candidate, dict) or 'name' not in candidate: return False
    if 'skills' in candidate:
        skills = candidate['skills']
        if not isinstance(skills, dict): return False
        if 'technical_skills' in skills and not isinstance(skills['technical_skills'], dict): return False
        if 'soft_skills' in skills and not isinstance(skills['soft_skills'], dict): return False
    if 'education' in candidate and not isinstance(candidate['education'], dict): return False
    if 'years_of_experience' in candidate:
        try: float(candidate['years_of_experience'])
        except: return False
    return True

def validate_job_data(job: Dict) -> bool:
    if not isinstance(job, dict) or 'title' not in job: return False
    if 'required_skills' in job:
        required_skills = job['required_skills']
        if not isinstance(required_skills, dict): return False
        if 'technical_skills' in required_skills and not isinstance(required_skills['technical_skills'], dict): return False
        if 'soft_skills' in required_skills and not isinstance(required_skills['soft_skills'], dict): return False
    if 'important_skills' in job and not isinstance(job['important_skills'], list): return False
    if 'experience' in job:
        try: float(job['experience'])
        except: return False
    if 'level' in job:
        valid_levels = ['entry', 'junior', 'intermediate', 'senior', 'lead', 'expert']
        if job['level'].lower() not in valid_levels: return False
    return True

def save_scores(job_results: Dict, timestamp: str):
    os.makedirs("./scores", exist_ok=True)
    
    for job_title, results in job_results.items():
        safe_job_title = re.sub(r'[^\w\s-]', '', job_title).strip()
        safe_job_title = re.sub(r'[-\s]+', '_', safe_job_title)
        filename = f"./scores/{safe_job_title}_{timestamp}.json"
        
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
                    "feedback_enhanced": result.detailed_breakdown.get("feedback_enhanced", False),
                    "chromadb_enhanced": result.detailed_breakdown.get("chromadb_enhanced", False),
                    "ollama_enhanced": result.detailed_breakdown.get("ollama_enhanced", False)
                })
        
        job_score_data = {
            "job_title": job_title,
            "timestamp": timestamp,
            "feedback_enhanced": any(r.get("feedback_enhanced", False) for r in simplified_results),
            "chromadb_enhanced": any(r.get("chromadb_enhanced", False) for r in simplified_results),
            "ollama_enhanced": any(r.get("ollama_enhanced", False) for r in simplified_results),
            "top_5_candidates": simplified_results[:5]
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(job_score_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving scores to {filename}: {e}")

def main():
    matcher = SmartRecruitMatcher(
        ollama_url="http://localhost:11434", 
        feedback_dir="./feedback", 
        chromadb_dir="./chromadb"
    )
    start_time = time.time()
    
    try: 
        matcher.initialize()
    except Exception as e:
        logger.error(f"Failed to initialize matcher: {e}")
        return False
    
    candidates, jobs = load_json_data()
    if not candidates or not jobs: 
        logger.warning("No candidates or jobs found")
        return False
    
    logger.info(f"Loaded {len(candidates)} candidates and {len(jobs)} jobs")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_results = {}
    
    for i, job in enumerate(jobs, 1):
        try:
            logger.info(f"Processing job {i}/{len(jobs)}: {job.get('title', f'Job_{i}')}")
            top_candidates = matcher.find_top_candidates_for_job(job, candidates, top_n=5)
            job_results[job.get('title', f'Job_{i}')] = top_candidates
        except Exception as e:
            logger.error(f"Error processing job {job.get('title', f'Job_{i}')}: {e}")
            job_results[job.get('title', f'Job_{i}')] = []
    
    save_scores(job_results, timestamp)
    
    # Optional: Clean up old ChromaDB entries periodically
    try:
        if matcher.chromadb_manager and matcher.chromadb_manager.client:
            matcher.chromadb_manager.cleanup_old_entries(30)  # Clean entries older than 30 days
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
    
    end_time = time.time()
    logger.info(f"Matching process completed in {end_time - start_time:.2f} seconds")
    return True

if __name__ == "__main__":
    try:
        candidate_files = glob.glob("./candidates/*.json")
        job_files = glob.glob("./jd/*.json")
        
        if not candidate_files or not job_files:
            logger.warning("No candidate or job files found. Please ensure files exist in ./candidates/ and ./jd/ directories")
            print("Missing files:")
            if not candidate_files:
                print("  - No candidate files found in ./candidates/")
            if not job_files:
                print("  - No job files found in ./jd/")
        else:
            print("Starting AI-powered recruitment matching...")
            print("Requirements:")
            print("  - Ollama server running at http://localhost:11434")
            print("  - Mistral model available in Ollama")
            print("  - Candidate files in ./candidates/")
            print("  - Job description files in ./jd/")
            print()
            
            success = main()
            if success:
                print("Matching process completed successfully")
                print("Results saved in ./scores/ directory")
            else:
                print("Matching process failed")
                
            # Clean up GPU memory if available
            if torch.cuda.is_available(): 
                torch.cuda.empty_cache()
                
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        try:
            if torch.cuda.is_available(): 
                torch.cuda.empty_cache()
        except: 
            pass
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        print(f"Fatal error: {e}")
        try:
            if torch.cuda.is_available(): 
                torch.cuda.empty_cache()
        except: 
            pass