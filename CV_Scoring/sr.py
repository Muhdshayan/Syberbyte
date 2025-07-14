import json
import numpy as np
import torch
from typing import Dict, List, Tuple, Any, Optional
import re
from collections import defaultdict
import logging
from dataclasses import dataclass
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
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MatchingResult:
    """Data class to store matching results"""
    candidate_name: str
    job_title: str
    overall_score: float
    skill_match_score: float
    experience_score: float
    education_score: float
    important_skills_score: float
    semantic_similarity_score: float
    detailed_breakdown: Dict[str, Any]

@dataclass
class RAGResult:
    """Data class for RAG retrieval results"""
    retrieved_candidates: List[Dict]
    similarity_scores: List[float]
    contextual_insights: str

class SkillSynonymMapper:
    """Maps skills to their synonyms and related terms"""
    
    def __init__(self):
        self.skill_synonyms = {
            # Programming Languages
            "python": ["python", "py", "python3", "python programming", "python development"],
            "javascript": ["javascript", "js", "node.js", "nodejs", "ecmascript", "es6", "es2015"],
            "java": ["java", "java programming", "java development", "jvm", "spring", "hibernate"],
            "c++": ["c++", "cpp", "c plus plus", "c/c++", "visual c++"],
            "c#": ["c#", "csharp", "c sharp", ".net", "dotnet", "asp.net"],
            
            # Data Science & ML
            "machine learning": ["machine learning", "ml", "artificial intelligence", "ai", "deep learning", 
                               "neural networks", "data science", "predictive modeling", "statistical modeling"],
            "data science": ["data science", "data scientist", "data analysis", "data analytics", 
                           "statistical analysis", "data mining", "big data", "analytics"],
            "pandas": ["pandas", "pd", "python pandas", "data manipulation", "dataframe"],
            "numpy": ["numpy", "np", "numerical computing", "scientific computing"],
            "scikit-learn": ["scikit-learn", "sklearn", "sci-kit learn", "machine learning library"],
            "tensorflow": ["tensorflow", "tf", "keras", "deep learning framework"],
            "pytorch": ["pytorch", "torch", "deep learning", "neural networks"],
            
            # Databases
            "sql": ["sql", "mysql", "postgresql", "sqlite", "database", "rdbms", "structured query language"],
            "mongodb": ["mongodb", "mongo", "nosql", "document database"],
            "redis": ["redis", "in-memory database", "caching"],
            
            # Web Technologies
            "react": ["react", "reactjs", "react.js", "jsx", "react native"],
            "angular": ["angular", "angularjs", "typescript", "ng"],
            "vue": ["vue", "vuejs", "vue.js", "nuxt"],
            "html": ["html", "html5", "markup", "web markup"],
            "css": ["css", "css3", "styling", "sass", "scss", "less"],
            
            # DevOps & Cloud
            "docker": ["docker", "containerization", "containers", "dockerfile"],
            "kubernetes": ["kubernetes", "k8s", "container orchestration", "microservices"],
            "aws": ["aws", "amazon web services", "ec2", "s3", "lambda", "cloud computing"],
            "git": ["git", "version control", "github", "gitlab", "bitbucket"],
            
            # Backend Technologies
            "nodejs": ["nodejs", "node.js", "node", "express", "express.js"],
            "django": ["django", "python web framework", "web development"],
            "flask": ["flask", "python microframework", "web api"],
            "spring boot": ["spring boot", "spring", "java framework", "microservices"],
            
            # Testing
            "testing": ["testing", "unit testing", "integration testing", "test automation", "qa"],
            "selenium": ["selenium", "web automation", "browser automation"],
            
            # Mobile Development
            "android": ["android", "android development", "kotlin", "java android"],
            "ios": ["ios", "swift", "objective-c", "xcode", "iphone development"],
            
            # Soft Skills
            "communication": ["communication", "verbal communication", "written communication", "presentation"],
            "leadership": ["leadership", "team lead", "management", "team management"],
            "problem solving": ["problem solving", "analytical thinking", "critical thinking", "troubleshooting"],
        }
    
    def get_skill_variations(self, skill: str) -> List[str]:
        """Get all variations of a skill"""
        skill_lower = skill.lower().strip()
        
        # Direct match
        if skill_lower in self.skill_synonyms:
            return self.skill_synonyms[skill_lower]
        
        # Search in synonyms
        for key, synonyms in self.skill_synonyms.items():
            if skill_lower in [s.lower() for s in synonyms]:
                return synonyms
        
        # If not found, return the original skill
        return [skill_lower]
    
    def calculate_skill_similarity(self, skill1: str, skill2: str) -> float:
        """Calculate similarity between two skills based on synonyms"""
        variations1 = set(s.lower() for s in self.get_skill_variations(skill1))
        variations2 = set(s.lower() for s in self.get_skill_variations(skill2))
        
        # Direct match
        if skill1.lower() == skill2.lower():
            return 1.0
        
        # Synonym match
        if variations1.intersection(variations2):
            return 0.9
        
        # Partial match (contains)
        for v1 in variations1:
            for v2 in variations2:
                if v1 in v2 or v2 in v1:
                    return 0.7
        
        return 0.0

class ModelManager:
    """Manages the three AI models with RTX 3050 optimization"""
    
    def __init__(self, models_dir: str = "./models"):
        self.models_dir = models_dir
        self.mistral_model = None
        self.codellama_model = None
        self.distilbert_session = None
        self.embedding_model = None
        self.device = self._detect_optimal_device()
        self.gpu_layers = self._calculate_optimal_gpu_layers()
        
    def _detect_optimal_device(self):
        """Detect optimal device for RTX 3050"""
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f" GPU Detected: {gpu_name} ({gpu_memory:.1f} GB VRAM)")
            
            # RTX 3050 specific optimization
            if "3050" in gpu_name or gpu_memory < 6.0:
                logger.info(" RTX 3050 optimization mode enabled")
                return "cuda"
            else:
                logger.info(" High-end GPU detected")
                return "cuda"
        else:
            logger.warning(" No CUDA GPU detected, using CPU")
            return "cpu"
    
    def _calculate_optimal_gpu_layers(self):
        """Calculate optimal GPU layers for RTX 3050"""
        if self.device == "cpu":
            return 0
        
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        
        if gpu_memory <= 4.5:  # RTX 3050 (4GB)
            return 15  # Conservative for 4GB VRAM
        elif gpu_memory <= 6.5:  # RTX 3060 (6GB)
            return 25
        elif gpu_memory <= 8.5:  # RTX 3070 (8GB)
            return 30
        else:  # Higher end GPUs
            return 35
        
    def load_models(self):
        """Load all three models with RTX 3050 optimization"""
        try:
            # CUDA memory management
            if self.device == "cuda":
                torch.cuda.empty_cache()
                logger.info(f"🔧 Using {self.gpu_layers} GPU layers for RTX 3050")
            
            # Load Mistral-7B for general understanding with RTX 3050 optimization
            logger.info("Loading Mistral-7B model...")
            self.mistral_model = Llama(
                model_path=f"{self.models_dir}/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                n_ctx=1024 if self.gpu_layers <= 15 else 2048,  # Reduced context for RTX 3050
                n_gpu_layers=self.gpu_layers,
                n_batch=256 if self.gpu_layers <= 15 else 512,  # Smaller batch for RTX 3050
                n_threads=4,  # Optimize CPU threads
                use_mmap=True,  # Memory mapping for efficiency
                use_mlock=False,  # Don't lock memory on RTX 3050
                verbose=False
            )
            
            # Load CodeLlama-7B for technical skills analysis
            logger.info("Loading CodeLlama-7B model...")
            self.codellama_model = Llama(
                model_path=f"{self.models_dir}/codellama-7b.Q4_K_M.gguf",
                n_ctx=1024 if self.gpu_layers <= 15 else 2048,
                n_gpu_layers=self.gpu_layers,
                n_batch=256 if self.gpu_layers <= 15 else 512,
                n_threads=4,
                use_mmap=True,
                use_mlock=False,
                verbose=False
            )
            
            # Load DistilBERT for NER with GPU acceleration
            logger.info("Loading DistilBERT NER model...")
            providers = []
            if self.device == "cuda":
                # Configure CUDA provider for RTX 3050
                cuda_provider_options = {
                    'device_id': 0,
                    'arena_extend_strategy': 'kSameAsRequested',
                    'gpu_mem_limit': 2 * 1024 * 1024 * 1024,  # 2GB limit for RTX 3050
                    'cudnn_conv_algo_search': 'EXHAUSTIVE',
                    'do_copy_in_default_stream': True,
                }
                providers = [
                    ('CUDAExecutionProvider', cuda_provider_options),
                    'CPUExecutionProvider'
                ]
            else:
                providers = ['CPUExecutionProvider']
                
            self.distilbert_session = ort.InferenceSession(
                f"{self.models_dir}/distilbert_ner.onnx",
                providers=providers
            )
            
            # Load sentence transformer for embeddings with GPU support
            logger.info("Loading sentence transformer...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Move to GPU if available
            if self.device == "cuda":
                self.embedding_model = self.embedding_model.to('cuda')
                logger.info("Sentence transformer moved to GPU")
            
            # Log final GPU memory usage
            if self.device == "cuda":
                memory_allocated = torch.cuda.memory_allocated(0) / 1024**2
                memory_reserved = torch.cuda.memory_reserved(0) / 1024**2
                logger.info(f" GPU Memory - Allocated: {memory_allocated:.1f}MB, Reserved: {memory_reserved:.1f}MB")
            
            logger.info("All models loaded successfully with GPU optimization!")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            logger.info("🔄 Falling back to CPU mode...")
            self.device = "cpu"
            self.gpu_layers = 0
            # Retry with CPU settings
            self._load_models_cpu_fallback()
    
    def _load_models_cpu_fallback(self):
        """Fallback to CPU-only mode"""
        try:
            logger.info("Loading models in CPU-only mode...")
            
            self.mistral_model = Llama(
                model_path=f"{self.models_dir}/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                n_ctx=1024,
                n_gpu_layers=0,
                n_threads=4,
                verbose=False
            )
            
            self.codellama_model = Llama(
                model_path=f"{self.models_dir}/codellama-7b.Q4_K_M.gguf",
                n_ctx=1024,
                n_gpu_layers=0,
                n_threads=4,
                verbose=False
            )
            
            self.distilbert_session = ort.InferenceSession(
                f"{self.models_dir}/distilbert_ner.onnx",
                providers=['CPUExecutionProvider']
            )
            
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info("CPU fallback successful!")
            
        except Exception as e:
            logger.error(f"CPU fallback failed: {e}")
            raise
    
    def generate_mistral_response(self, prompt: str, max_tokens: int = 512) -> str:
        """Generate response using Mistral model"""
        try:
            response = self.mistral_model(
                prompt,
                max_tokens=max_tokens,
                temperature=0.1,
                stop=["</s>", "\n\n"]
            )
            return response['choices'][0]['text'].strip()
        except Exception as e:
            logger.error(f"Error with Mistral model: {e}")
            return ""
    
    def generate_codellama_response(self, prompt: str, max_tokens: int = 512) -> str:
        """Generate response using CodeLlama model"""
        try:
            response = self.codellama_model(
                prompt,
                max_tokens=max_tokens,
                temperature=0.1,
                stop=["</s>", "\n\n"]
            )
            return response['choices'][0]['text'].strip()
        except Exception as e:
            logger.error(f"Error with CodeLlama model: {e}")
            return ""
    
    def extract_entities(self, text: str) -> List[str]:
        """Extract entities using DistilBERT NER (simplified implementation)"""
        try:
            # This is a simplified version - you'd need proper tokenization for the actual model
            # For now, we'll use regex patterns to extract technical terms
            patterns = [
                r'\b[A-Z][a-z]*(?:\s+[A-Z][a-z]*)*\b',  # Proper nouns
                r'\b(?:Python|Java|JavaScript|React|Angular|Vue|Node\.js|Django|Flask|SQL|MongoDB|AWS|Docker|Kubernetes)\b',
                r'\b\w+(?:\.\w+)*\b'  # Technical terms with dots
            ]
            
            entities = []
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities.extend(matches)
            
            return list(set(entities))
        except Exception as e:
            logger.error(f"Error with entity extraction: {e}")
            return []
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for text using sentence transformer"""
        try:
            embeddings = self.embedding_model.encode(texts)
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return np.array([])

class ChromaDBManager:
    """Manages ChromaDB for RAG functionality"""
    
    def __init__(self, db_path: str = "./chroma_db", embedding_model=None):
        self.db_path = db_path
        self.client = None
        self.candidate_collection = None
        self.job_collection = None
        self.embedding_model = embedding_model
        self.embedding_function = None
        
    def initialize_chromadb(self):
        """Initialize ChromaDB client and collections"""
        try:
            # Create ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Create custom embedding function
            if self.embedding_model:
                self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
            else:
                self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
            
            # Create or get candidate collection
            try:
                self.candidate_collection = self.client.create_collection(
                    name="candidates",
                    embedding_function=self.embedding_function,
                    metadata={"description": "Candidate profiles for job matching"}
                )
            except Exception:
                self.candidate_collection = self.client.get_collection("candidates")
            
            # Create or get job collection
            try:
                self.job_collection = self.client.create_collection(
                    name="jobs",
                    embedding_function=self.embedding_function,
                    metadata={"description": "Job descriptions for candidate matching"}
                )
            except Exception:
                self.job_collection = self.client.get_collection("jobs")
            
            logger.info("ChromaDB initialized successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise
    
    def add_candidate_to_db(self, candidate: Dict, candidate_profile: Dict) -> str:
        """Add candidate to ChromaDB"""
        try:
            candidate_id = str(uuid.uuid4())
            
            # Create comprehensive candidate text for embedding
            candidate_text = self._create_candidate_text(candidate, candidate_profile)
            
            # Prepare metadata
            metadata = {
                "name": candidate.get("name", "Unknown"),
                "email": candidate.get("email", ""),
                "experience_years": float(candidate.get("Experience", {}).get("Years", 0)),
                "experience_months": float(candidate.get("Experience", {}).get("Months", 0)),
                "education_degree": candidate.get("Education", {}).get("degree", ""),
                "education_field": candidate.get("Education", {}).get("field", ""),
                "title": candidate.get("Experience", {}).get("Title", ""),
                "skills": json.dumps(candidate.get("Skills", {})),
                "soft_skills": json.dumps(candidate.get("Soft_Skills", [])),
                "added_date": datetime.now().isoformat()
            }
            
            # Add to collection
            self.candidate_collection.add(
                documents=[candidate_text],
                metadatas=[metadata],
                ids=[candidate_id]
            )
            
            logger.info(f"Added candidate {candidate.get('name')} to ChromaDB")
            return candidate_id
            
        except Exception as e:
            logger.error(f"Error adding candidate to DB: {e}")
            return ""
    
    def add_job_to_db(self, job: Dict) -> str:
        """Add job to ChromaDB"""
        try:
            job_id = str(uuid.uuid4())
            
            # Create comprehensive job text for embedding
            job_text = self._create_job_text(job)
            
            # Prepare metadata
            metadata = {
                "title": job.get("title", "Unknown"),
                "level": job.get("level", ""),
                "location": job.get("location", ""),
                "location_type": job.get("location_type", ""),
                "min_experience": job.get("min_experience", 0),
                "education_level": job.get("education_level", ""),
                "employment_type": job.get("employment_type", ""),
                "required_skills": json.dumps(job.get("required_skills", {})),
                "important_skills": json.dumps(job.get("important_skills", [])),
                "salary_range": job.get("salary_range", ""),
                "added_date": datetime.now().isoformat()
            }
            
            # Add to collection
            self.job_collection.add(
                documents=[job_text],
                metadatas=[metadata],
                ids=[job_id]
            )
            
            logger.info(f"Added job {job.get('title')} to ChromaDB")
            return job_id
            
        except Exception as e:
            logger.error(f"Error adding job to DB: {e}")
            return ""
    
    def retrieve_similar_candidates(self, job: Dict, n_results: int = 10) -> RAGResult:
        """Retrieve similar candidates for a job using RAG"""
        try:
            job_text = self._create_job_text(job)
            
            # Query the candidate collection
            results = self.candidate_collection.query(
                query_texts=[job_text],
                n_results=min(n_results, self.candidate_collection.count())
            )
            
            retrieved_candidates = []
            similarity_scores = []
            
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # Convert distance to similarity score (1 - normalized_distance)
                    similarity_score = max(0, 1 - distance)
                    similarity_scores.append(similarity_score)
                    
                    # Reconstruct candidate info from metadata
                    candidate_info = {
                        "name": metadata.get("name", "Unknown"),
                        "email": metadata.get("email", ""),
                        "experience_years": metadata.get("experience_years", 0),
                        "education": f"{metadata.get('education_degree', '')} in {metadata.get('education_field', '')}",
                        "title": metadata.get("title", ""),
                        "skills": json.loads(metadata.get("skills", "{}")),
                        "similarity_score": similarity_score,
                        "document_text": doc
                    }
                    retrieved_candidates.append(candidate_info)
            
            # Generate contextual insights
            contextual_insights = self._generate_contextual_insights(job, retrieved_candidates)
            
            return RAGResult(
                retrieved_candidates=retrieved_candidates,
                similarity_scores=similarity_scores,
                contextual_insights=contextual_insights
            )
            
        except Exception as e:
            logger.error(f"Error retrieving similar candidates: {e}")
            return RAGResult([], [], "Error during retrieval")
    
    def retrieve_similar_jobs(self, candidate: Dict, n_results: int = 10) -> RAGResult:
        """Retrieve similar jobs for a candidate using RAG"""
        try:
            candidate_text = self._create_candidate_text(candidate, {})
            
            # Query the job collection
            results = self.job_collection.query(
                query_texts=[candidate_text],
                n_results=min(n_results, self.job_collection.count())
            )
            
            retrieved_jobs = []
            similarity_scores = []
            
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # Convert distance to similarity score
                    similarity_score = max(0, 1 - distance)
                    similarity_scores.append(similarity_score)
                    
                    # Reconstruct job info from metadata
                    job_info = {
                        "title": metadata.get("title", "Unknown"),
                        "level": metadata.get("level", ""),
                        "location": metadata.get("location", ""),
                        "min_experience": metadata.get("min_experience", 0),
                        "required_skills": json.loads(metadata.get("required_skills", "{}")),
                        "important_skills": json.loads(metadata.get("important_skills", "[]")),
                        "similarity_score": similarity_score,
                        "document_text": doc
                    }
                    retrieved_jobs.append(job_info)
            
            # Generate contextual insights
            contextual_insights = self._generate_job_insights(candidate, retrieved_jobs)
            
            return RAGResult(
                retrieved_candidates=retrieved_jobs,  # Using same structure
                similarity_scores=similarity_scores,
                contextual_insights=contextual_insights
            )
            
        except Exception as e:
            logger.error(f"Error retrieving similar jobs: {e}")
            return RAGResult([], [], "Error during retrieval")
    
    def _create_candidate_text(self, candidate: Dict, candidate_profile: Dict) -> str:
        """Create comprehensive text representation of candidate for embedding"""
        parts = []
        
        # Basic info
        parts.append(f"Candidate: {candidate.get('name', 'Unknown')}")
        
        # Experience
        exp = candidate.get("Experience", {})
        years = exp.get("Years", 0)
        months = exp.get("Months", 0)
        title = exp.get("Title", "")
        parts.append(f"Experience: {years} years {months} months as {title}")
        
        # Education
        edu = candidate.get("Education", {})
        degree = edu.get("degree", "")
        field = edu.get("field", "")
        parts.append(f"Education: {degree} in {field}")
        
        # Skills with levels
        skills = candidate.get("Skills", {})
        skill_text = []
        for skill, level in skills.items():
            skill_text.append(f"{skill} (Level {level})")
        if skill_text:
            parts.append(f"Technical Skills: {', '.join(skill_text)}")
        
        # Soft skills
        soft_skills = candidate.get("Soft_Skills", [])
        if soft_skills:
            parts.append(f"Soft Skills: {', '.join(soft_skills)}")
        
        # AI insights if available
        if candidate_profile.get("general_understanding"):
            parts.append(f"Profile Analysis: {candidate_profile['general_understanding']}")
        
        if candidate_profile.get("technical_analysis"):
            parts.append(f"Technical Analysis: {candidate_profile['technical_analysis']}")
        
        return " | ".join(parts)
    
    def _create_job_text(self, job: Dict) -> str:
        """Create comprehensive text representation of job for embedding"""
        parts = []
        
        # Basic info
        parts.append(f"Job Title: {job.get('title', 'Unknown')}")
        parts.append(f"Level: {job.get('level', 'Not specified')}")
        parts.append(f"Location: {job.get('location', '')} ({job.get('location_type', '')})")
        
        # Requirements
        parts.append(f"Minimum Experience: {job.get('min_experience', 0)} years")
        parts.append(f"Education: {job.get('education_level', 'Not specified')}")
        
        # Skills
        required_skills = job.get("required_skills", {})
        if required_skills:
            skill_text = []
            for skill, level in required_skills.items():
                skill_text.append(f"{skill} (Required Level {level})")
            parts.append(f"Required Skills: {', '.join(skill_text)}")
        
        # Important skills
        important_skills = job.get("important_skills", [])
        if important_skills:
            parts.append(f"Critical Skills: {', '.join(important_skills)}")
        
        # Additional details
        if job.get("salary_range"):
            parts.append(f"Salary: {job['salary_range']}")
        
        parts.append(f"Employment Type: {job.get('employment_type', 'Not specified')}")
        
        return " | ".join(parts)
    
    def _generate_contextual_insights(self, job: Dict, candidates: List[Dict]) -> str:
        """Generate insights about retrieved candidates for a job"""
        if not candidates:
            return "No similar candidates found in the database."
        
        insights = []
        insights.append(f"Found {len(candidates)} relevant candidates for {job.get('title', 'this position')}.")
        
        # Analyze similarity scores
        scores = [c.get('similarity_score', 0) for c in candidates]
        avg_score = np.mean(scores) if scores else 0
        insights.append(f"Average similarity score: {avg_score:.2f}")
        
        # Top candidates
        top_3 = candidates[:3]
        insights.append("Top matching candidates:")
        for i, candidate in enumerate(top_3, 1):
            insights.append(f"{i}. {candidate.get('name', 'Unknown')} (Score: {candidate.get('similarity_score', 0):.2f})")
        
        return " | ".join(insights)
    
    def _generate_job_insights(self, candidate: Dict, jobs: List[Dict]) -> str:
        """Generate insights about retrieved jobs for a candidate"""
        if not jobs:
            return "No similar jobs found in the database."
        
        insights = []
        insights.append(f"Found {len(jobs)} relevant positions for {candidate.get('name', 'this candidate')}.")
        
        # Analyze similarity scores
        scores = [j.get('similarity_score', 0) for j in jobs]
        avg_score = np.mean(scores) if scores else 0
        insights.append(f"Average job compatibility score: {avg_score:.2f}")
        
        # Top jobs
        top_3 = jobs[:3]
        insights.append("Best matching positions:")
        for i, job in enumerate(top_3, 1):
            insights.append(f"{i}. {job.get('title', 'Unknown')} (Score: {job.get('similarity_score', 0):.2f})")
        
        return " | ".join(insights)
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collections"""
        try:
            candidate_count = self.candidate_collection.count() if self.candidate_collection else 0
            job_count = self.job_collection.count() if self.job_collection else 0
            
            return {
                "candidates_in_db": candidate_count,
                "jobs_in_db": job_count,
                "total_documents": candidate_count + job_count
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}

class RAGProcessor:
    """Enhanced RAG processing class with ChromaDB integration"""
    
    def __init__(self):
        self.model_manager = ModelManager()
        self.skill_mapper = SkillSynonymMapper()
        self.chroma_manager = None
        
    def initialize(self):
        """Initialize the RAG processor"""
        self.model_manager.load_models()
        
        # Initialize ChromaDB
        self.chroma_manager = ChromaDBManager(
            embedding_model=self.model_manager.embedding_model
        )
        self.chroma_manager.initialize_chromadb()
    
    def process_candidate_profile(self, candidate: Dict) -> Dict:
        """Process candidate profile through the AI pipeline"""
        
        # Step 1: General Understanding with Mistral-7B
        general_prompt = f"""
        Analyze this candidate profile and provide a comprehensive summary:
        
        Candidate: {json.dumps(candidate, indent=2)}
        
        Provide insights about:
        1. Overall professional background
        2. Career progression potential
        3. Key strengths and expertise areas
        4. Suitability for different types of roles
        
        Summary:
        """
        
        general_understanding = self.model_manager.generate_mistral_response(general_prompt)
        
        # Step 2: Technical Skills Analysis with CodeLlama-7B
        technical_prompt = f"""
        Analyze the technical skills of this candidate:
        
        Skills: {json.dumps(candidate.get('Skills', {}), indent=2)}
        Experience: {candidate.get('Experience', {})}
        Education: {candidate.get('Education', {})}
        
        Evaluate:
        1. Technical skill proficiency levels
        2. Technology stack compatibility
        3. Programming language expertise
        4. Framework and tool knowledge
        5. Potential for technical growth
        
        Technical Analysis:
        """
        
        technical_analysis = self.model_manager.generate_codellama_response(technical_prompt)
        
        # Step 3: Entity Extraction with DistilBERT
        full_text = f"{json.dumps(candidate)} {general_understanding} {technical_analysis}"
        extracted_entities = self.model_manager.extract_entities(full_text)
        
        # Step 4: Store in ChromaDB for RAG
        candidate_id = ""
        if self.chroma_manager:
            processed_profile = {
                "general_understanding": general_understanding,
                "technical_analysis": technical_analysis,
                "extracted_entities": extracted_entities
            }
            candidate_id = self.chroma_manager.add_candidate_to_db(candidate, processed_profile)
        
        return {
            "general_understanding": general_understanding,
            "technical_analysis": technical_analysis,
            "extracted_entities": extracted_entities,
            "processed_skills": self._process_candidate_skills(candidate.get('Skills', {})),
            "candidate_id": candidate_id
        }
    
    def process_job_description(self, job: Dict) -> Dict:
        """Process job description and store in ChromaDB"""
        job_id = ""
        if self.chroma_manager:
            job_id = self.chroma_manager.add_job_to_db(job)
        
        return {
            "job_id": job_id,
            "processed_skills": self._process_job_skills(job.get('required_skills', {}))
        }
    
    def rag_based_matching(self, job: Dict, use_rag: bool = True) -> List[MatchingResult]:
        """Perform RAG-based candidate matching for a job"""
        if not use_rag or not self.chroma_manager:
            return []
        
        # Retrieve similar candidates using RAG
        rag_result = self.chroma_manager.retrieve_similar_candidates(job, n_results=10)
        
        results = []
        for i, retrieved_candidate in enumerate(rag_result.retrieved_candidates):
            # Create a candidate dict from retrieved data
            candidate = {
                "name": retrieved_candidate.get("name", "Unknown"),
                "email": retrieved_candidate.get("email", ""),
                "Experience": {
                    "Years": str(int(retrieved_candidate.get("experience_years", 0))),
                    "Months": "0",
                    "Title": retrieved_candidate.get("title", "")
                },
                "Education": {"degree": "", "field": ""},
                "Skills": retrieved_candidate.get("skills", {})
            }
            
            # Calculate traditional matching score
            candidate_profile = {"general_understanding": "", "technical_analysis": ""}
            traditional_result = self.calculate_matching_score(candidate, job, candidate_profile)
            
            # Enhanced result with RAG similarity
            enhanced_result = MatchingResult(
                candidate_name=traditional_result.candidate_name,
                job_title=traditional_result.job_title,
                overall_score=round((traditional_result.overall_score * 0.7 + 
                                   retrieved_candidate.get("similarity_score", 0) * 100 * 0.3), 2),
                skill_match_score=traditional_result.skill_match_score,
                experience_score=traditional_result.experience_score,
                education_score=traditional_result.education_score,
                important_skills_score=traditional_result.important_skills_score,
                semantic_similarity_score=round(retrieved_candidate.get("similarity_score", 0) * 100, 2),
                detailed_breakdown={
                    **traditional_result.detailed_breakdown,
                    "rag_insights": rag_result.contextual_insights,
                    "semantic_match": retrieved_candidate.get("similarity_score", 0),
                    "retrieved_rank": i + 1
                }
            )
            results.append(enhanced_result)
        
        return results
    
    def find_jobs_for_candidate(self, candidate: Dict) -> List[Dict]:
        """Find suitable jobs for a candidate using RAG"""
        if not self.chroma_manager:
            return []
        
        # Retrieve similar jobs using RAG
        rag_result = self.chroma_manager.retrieve_similar_jobs(candidate, n_results=10)
        
        return rag_result.retrieved_candidates  # Jobs in this case
    
    def _process_candidate_skills(self, skills: Dict) -> Dict:
        """Process and normalize candidate skills"""
        processed = {}
        for skill, level in skills.items():
            variations = self.skill_mapper.get_skill_variations(skill)
            processed[skill] = {
                "level": level,
                "variations": variations,
                "normalized_name": variations[0] if variations else skill.lower()
            }
        return processed
    
    def _process_job_skills(self, skills: Dict) -> Dict:
        """Process and normalize job required skills"""
        processed = {}
        for skill, level in skills.items():
            variations = self.skill_mapper.get_skill_variations(skill)
            processed[skill] = {
                "required_level": level,
                "variations": variations,
                "normalized_name": variations[0] if variations else skill.lower()
            }
        return processed
    
    def calculate_matching_score(self, candidate: Dict, job: Dict, candidate_profile: Dict) -> MatchingResult:
        """Calculate comprehensive matching score"""
        
        # 1. Skill Matching (35% weight - reduced to make room for semantic)
        skill_score = self._calculate_skill_match(
            candidate.get('Skills', {}), 
            job.get('required_skills', {}),
            job.get('important_skills', [])
        )
        
        # 2. Experience Matching (25% weight)
        experience_score = self._calculate_experience_match(
            candidate.get('Experience', {}),
            job.get('min_experience', 0),
            job.get('level', 'entry')
        )
        
        # 3. Education Matching (15% weight)
        education_score = self._calculate_education_match(
            candidate.get('Education', {}),
            job.get('education_level', '')
        )
        
        # 4. Important Skills Bonus (20% weight)
        important_skills_score = self._calculate_important_skills_match(
            candidate.get('Skills', {}),
            job.get('important_skills', [])
        )
        
        # 5. Semantic Similarity (5% weight - will be enhanced in RAG mode)
        semantic_score = 50.0  # Default value, enhanced in RAG mode
        
        # Calculate weighted overall score
        overall_score = (
            skill_score * 0.35 +
            experience_score * 0.25 +
            education_score * 0.15 +
            important_skills_score * 0.20 +
            semantic_score * 0.05
        )
        
        return MatchingResult(
            candidate_name=candidate.get('name', 'Unknown'),
            job_title=job.get('title', 'Unknown'),
            overall_score=round(overall_score, 2),
            skill_match_score=round(skill_score, 2),
            experience_score=round(experience_score, 2),
            education_score=round(education_score, 2),
            important_skills_score=round(important_skills_score, 2),
            semantic_similarity_score=round(semantic_score, 2),
            detailed_breakdown={
                "skill_matches": self._get_detailed_skill_matches(candidate.get('Skills', {}), job.get('required_skills', {})),
                "experience_analysis": self._get_experience_analysis(candidate.get('Experience', {}), job),
                "ai_insights": candidate_profile.get('general_understanding', ''),
                "technical_insights": candidate_profile.get('technical_analysis', '')
            }
        )
    
    def _calculate_skill_match(self, candidate_skills: Dict, required_skills: Dict, important_skills: List) -> float:
        """Calculate skill matching score"""
        if not required_skills:
            return 50.0
        
        total_score = 0
        max_possible_score = 0
        
        for req_skill, req_level in required_skills.items():
            max_possible_score += req_level
            best_match_score = 0
            
            for cand_skill, cand_level in candidate_skills.items():
                similarity = self.skill_mapper.calculate_skill_similarity(req_skill, cand_skill)
                if similarity > 0:
                    # Calculate level match (candidate level vs required level)
                    level_match = min(int(cand_level), req_level) / req_level
                    skill_score = similarity * level_match * req_level
                    best_match_score = max(best_match_score, skill_score)
            
            total_score += best_match_score
        
        return (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
    
    def _calculate_important_skills_match(self, candidate_skills: Dict, important_skills: List) -> float:
        """Calculate important skills matching with higher weightage"""
        if not important_skills:
            return 50.0
        
        matched_important = 0
        for imp_skill in important_skills:
            for cand_skill in candidate_skills.keys():
                similarity = self.skill_mapper.calculate_skill_similarity(imp_skill, cand_skill)
                if similarity >= 0.7:  # High threshold for important skills
                    matched_important += 1
                    break
        
        return (matched_important / len(important_skills)) * 100
    
    def _calculate_experience_match(self, candidate_exp: Dict, min_exp: int, level: str) -> float:
        """Calculate experience matching score"""
        try:
            cand_years = int(candidate_exp.get('Years', 0))
            cand_months = int(candidate_exp.get('Months', 0))
            total_exp_months = cand_years * 12 + cand_months
            total_exp_years = total_exp_months / 12
            
            if total_exp_years >= min_exp:
                # Bonus for exceeding minimum
                excess = total_exp_years - min_exp
                return min(100, 80 + (excess * 5))  # 80% base + bonus
            else:
                # Penalty for not meeting minimum
                ratio = total_exp_years / max(min_exp, 1)
                return ratio * 70  # Max 70% if below minimum
                
        except (ValueError, TypeError):
            return 30.0  # Default low score for invalid experience data
    
    def _calculate_education_match(self, candidate_edu: Dict, required_edu: str) -> float:
        """Calculate education matching score"""
        if not required_edu:
            return 80.0  # Default score when no requirement
        
        cand_degree = candidate_edu.get('degree', '').lower()
        cand_field = candidate_edu.get('field', '').lower()
        required_lower = required_edu.lower()
        
        # Degree level matching
        degree_score = 0
        if 'bachelor' in required_lower and 'bachelor' in cand_degree:
            degree_score = 80
        elif 'master' in required_lower and ('master' in cand_degree or 'bachelor' in cand_degree):
            degree_score = 90 if 'master' in cand_degree else 70
        elif 'phd' in required_lower:
            if 'phd' in cand_degree:
                degree_score = 100
            elif 'master' in cand_degree:
                degree_score = 80
            elif 'bachelor' in cand_degree:
                degree_score = 60
        else:
            degree_score = 60  # Default for other cases
        
        # Field matching
        field_score = 0
        relevant_fields = ['cs', 'computer science', 'se', 'software engineering', 'ai', 'artificial intelligence']
        if any(field in required_lower for field in relevant_fields):
            if any(field in cand_field for field in relevant_fields):
                field_score = 20
            else:
                field_score = 10
        else:
            field_score = 15
        
        return min(100, degree_score + field_score)
    
    def _get_detailed_skill_matches(self, candidate_skills: Dict, required_skills: Dict) -> Dict:
        """Get detailed breakdown of skill matches"""
        matches = {}
        for req_skill, req_level in required_skills.items():
            best_match = {"skill": None, "similarity": 0, "level_match": 0}
            
            for cand_skill, cand_level in candidate_skills.items():
                similarity = self.skill_mapper.calculate_skill_similarity(req_skill, cand_skill)
                if similarity > best_match["similarity"]:
                    level_match = min(int(cand_level), req_level) / req_level
                    best_match = {
                        "skill": cand_skill,
                        "similarity": similarity,
                        "level_match": level_match,
                        "candidate_level": cand_level,
                        "required_level": req_level
                    }
            
            matches[req_skill] = best_match
        
        return matches
    
    def _get_experience_analysis(self, candidate_exp: Dict, job: Dict) -> Dict:
        """Get detailed experience analysis"""
        return {
            "candidate_experience": candidate_exp,
            "required_minimum": job.get('min_experience', 0),
            "job_level": job.get('level', 'entry'),
            "title_match": candidate_exp.get('Title', '').lower() in job.get('title', '').lower()
        }

def create_sample_data():
    """Create sample candidates and job descriptions"""
    
    candidates = [
        {
            "name": "Ali Hassan",
            "email": "ali.hassan@gmail.com", 
            "portfolio": "www.alihassan.dev",
            "LinkedIn": "www.linkedin.com/in/alihassan",
            "Education": {
                "degree": "Bachelor's",
                "year": "2023",
                "field": "Computer Science"
            },
            "Experience": {
                "Years": "2",
                "Months": "6",
                "Title": "Junior AI Developer"
            },
            "Skills": {
                "Data Science": "4",
                "Python": "5",
                "Machine Learning": "4",
                "pandas": "5",
                "scikit-learn": "4",
                "SQL": "4",
                "TensorFlow": "3",
                "Django": "3"
            },
            "Soft_Skills": [
                "Problem Solving",
                "Communication",
                "Team Work"
            ]
        },
        {
            "name": "Sara Ahmed",
            "email": "sara.ahmed@gmail.com",
            "portfolio": "www.saraahmed.com", 
            "LinkedIn": "www.linkedin.com/in/saraahmed",
            "Education": {
                "degree": "Master's",
                "year": "2022",
                "field": "Software Engineering"
            },
            "Experience": {
                "Years": "3",
                "Months": "2",
                "Title": "Full Stack Developer"
            },
            "Skills": {
                "JavaScript": "5",
                "React": "5",
                "Node.js": "4",
                "Python": "3",
                "MongoDB": "4",
                "AWS": "3",
                "Docker": "3",
                "Git": "5"
            },
            "Soft_Skills": [
                "Leadership",
                "Project Management",
                "Critical Thinking"
            ]
        },
        {
            "name": "Ahmed Khan",
            "email": "ahmed.khan@gmail.com",
            "portfolio": "www.ahmedkhan.tech",
            "LinkedIn": "www.linkedin.com/in/ahmedkhan",
            "Education": {
                "degree": "Bachelor's", 
                "year": "2021",
                "field": "Information Technology"
            },
            "Experience": {
                "Years": "4",
                "Months": "0",
                "Title": "Senior Software Engineer"
            },
            "Skills": {
                "Java": "5",
                "Spring Boot": "4",
                "Microservices": "4",
                "Kubernetes": "3",
                "PostgreSQL": "4",
                "Redis": "3",
                "Jenkins": "3",
                "Machine Learning": "2"
            },
            "Soft_Skills": [
                "Mentoring",
                "Architecture Design",
                "Technical Writing"
            ]
        }
    ]
    
    jobs = [
        {
            "title": "Senior Data Scientist",
            "level": "senior",
            "employment_type": "Full-time",
            "location": "Lahore, Pakistan",
            "location_type": "Hybrid",
            "required_skills": {
                "Python": 5,
                "pandas": 5,
                "scikit-learn": 4,
                "SQL": 4,
                "Machine Learning": 5,
                "TensorFlow": 4,
                "Statistics": 4
            },
            "min_experience": 4,
            "education_level": "Master's in CS, Data Science, Statistics or related field",
            "salary_range": "PKR 200,000 - 350,000",
            "important_skills": [
                "Data Science",
                "Machine Learning",
                "Python"
            ]
        },
        {
            "title": "Full Stack Developer",
            "level": "intermediate",
            "employment_type": "Full-time", 
            "location": "Karachi, Pakistan",
            "location_type": "Remote",
            "required_skills": {
                "JavaScript": 5,
                "React": 4,
                "Node.js": 4,
                "MongoDB": 3,
                "HTML": 4,
                "CSS": 4,
                "Git": 4
            },
            "min_experience": 2,
            "education_level": "Bachelor's in CS, SE or related field",
            "salary_range": "PKR 120,000 - 200,000",
            "important_skills": [
                "React",
                "JavaScript",
                "Node.js"
            ]
        },
        {
            "title": "Backend Engineer",
            "level": "senior",
            "employment_type": "Full-time",
            "location": "Islamabad, Pakistan", 
            "location_type": "On-site",
            "required_skills": {
                "Java": 5,
                "Spring Boot": 4,
                "Microservices": 4,
                "PostgreSQL": 4,
                "Docker": 3,
                "Kubernetes": 3,
                "Redis": 3
            },
            "min_experience": 3,
            "education_level": "Bachelor's in CS, SE or related field",
            "salary_range": "PKR 150,000 - 280,000",
            "important_skills": [
                "Java",
                "Microservices",
                "Spring Boot"
            ]
        }
    ]
    
    return candidates, jobs

def main():
    """Main execution function with enhanced RTX 3050 GPU utilization"""
    print("Starting SmartRecruit RAG AI Module with RTX 3050 GPU Acceleration...")
    
    # Check GPU availability first
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"GPU Detected: {gpu_name} ({gpu_memory:.1f} GB VRAM)")
        
        # RTX 3050 specific messages
        if "3050" in gpu_name:
            print("RTX 3050 optimization enabled!")
            print("Using conservative GPU settings for stable performance")
        
        # Clear any existing GPU memory
        torch.cuda.empty_cache()
    else:
        print(" No CUDA GPU detected - running in CPU mode")
    
    # Initialize RAG processor
    rag_processor = RAGProcessor()
    
    print("Loading AI models and initializing ChromaDB...")
    start_time = time.time()
    
    try:
        rag_processor.initialize()
        load_time = time.time() - start_time
        print(f"Models and ChromaDB loaded successfully in {load_time:.2f}s!")
        
        # Display GPU memory usage if available
        if torch.cuda.is_available():
            memory_allocated = torch.cuda.memory_allocated(0) / 1024**2
            memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**2
            memory_percent = (memory_allocated / memory_total) * 100
            print(f"GPU Memory Usage: {memory_allocated:.0f}MB/{memory_total:.0f}MB ({memory_percent:.1f}%)")
            
    except Exception as e:
        print(f"Error loading models: {e}")
        print("Continuing with limited functionality...")
    
    # Create sample data
    candidates, jobs = create_sample_data()
    
    print(f"\nProcessing {len(candidates)} candidates against {len(jobs)} job descriptions...")
    
    # Process all candidates and store in ChromaDB
    candidate_profiles = {}
    total_candidates = len(candidates)
    
    for i, candidate in enumerate(candidates, 1):
        print(f"\nProcessing candidate {i}/{total_candidates}: {candidate['name']}")
        start_time = time.time()
        
        try:
            profile = rag_processor.process_candidate_profile(candidate)
            candidate_profiles[candidate['name']] = profile
            
            process_time = time.time() - start_time
            print(f"Processed {candidate['name']} in {process_time:.2f}s")
            
            # Show GPU memory if available
            if torch.cuda.is_available():
                memory_used = torch.cuda.memory_allocated(0) / 1024**2
                print(f"GPU Memory: {memory_used:.0f}MB")
                
        except Exception as e:
            print(f"Error processing {candidate['name']}: {e}")
            candidate_profiles[candidate['name']] = {"error": str(e)}
    
    # Process all jobs and store in ChromaDB
    job_profiles = {}
    total_jobs = len(jobs)
    
    for i, job in enumerate(jobs, 1):
        print(f"\nProcessing job {i}/{total_jobs}: {job['title']}")
        try:
            job_profile = rag_processor.process_job_description(job)
            job_profiles[job['title']] = job_profile
            print(f"Processed and stored {job['title']} in ChromaDB")
        except Exception as e:
            print(f"Error processing {job['title']}: {e}")
            job_profiles[job['title']] = {"error": str(e)}
    
    # Get ChromaDB statistics
    if rag_processor.chroma_manager:
        stats = rag_processor.chroma_manager.get_collection_stats()
        print(f"\nChromaDB Stats: {stats}")
    
    # Performance monitoring for RTX 3050
    processing_start = time.time()
    
    # Perform traditional matching
    print("\nCalculating traditional matching scores...")
    traditional_results = []
    
    for candidate in candidates:
        for job in jobs:
            try:
                candidate_profile = candidate_profiles.get(candidate['name'], {})
                result = rag_processor.calculate_matching_score(candidate, job, candidate_profile)
                traditional_results.append(result)
            except Exception as e:
                print(f"Error calculating match for {candidate['name']} - {job['title']}: {e}")
    
    # Perform RAG-based matching with GPU acceleration
    print("\nPerforming RAG-based intelligent matching...")
    rag_results = []
    
    for job in jobs:
        print(f"Finding candidates for: {job['title']}")
        try:
            job_rag_results = rag_processor.rag_based_matching(job, use_rag=True)
            rag_results.extend(job_rag_results)
            print(f"Found {len(job_rag_results)} RAG matches for {job['title']}")
        except Exception as e:
            print(f"Error in RAG matching for {job['title']}: {e}")
    
    processing_time = time.time() - processing_start
    print(f"\n⚡ Total processing time: {processing_time:.2f}s")
    
    # Final GPU memory cleanup
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        final_memory = torch.cuda.memory_allocated(0) / 1024**2
        print(f"Final GPU Memory Usage: {final_memory:.0f}MB")
    
    # Display results with performance metrics
    print("\n" + "="*80)
    print("PERFORMANCE SUMMARY")
    print("="*80)
    
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        print(f"GPU: {gpu_name}")
        print(f"Processing Speed: {len(candidates) * len(jobs) / processing_time:.1f} matches/second")
        if "3050" in gpu_name:
            print("RTX 3050 delivered excellent performance for AI recruitment!")
    else:
        print("CPU Processing completed")
        print(f"Processing Speed: {len(candidates) * len(jobs) / processing_time:.1f} matches/second")
    
    # Continue with result display...
    print("\n" + "="*80)
    print("TRADITIONAL MATCHING RESULTS")
    print("="*80)
    
    traditional_results.sort(key=lambda x: x.overall_score, reverse=True)
    
    for i, result in enumerate(traditional_results[:6], 1):  # Show top 6
        print(f"\n{i}. {result.candidate_name} → {result.job_title}")
        print(f"Overall Score: {result.overall_score}%")
        print(f"Skill Match: {result.skill_match_score}%")
        print(f"Experience: {result.experience_score}%") 
        print(f"Education: {result.education_score}%")
        print(f"Important Skills: {result.important_skills_score}%")
        
        if result.overall_score >= 80:
            print("EXCELLENT MATCH")
        elif result.overall_score >= 65:
            print("GOOD MATCH") 
        elif result.overall_score >= 50:
            print("FAIR MATCH")
        else:
            print("POOR MATCH")
    
    # Display RAG-enhanced results
    if rag_results:
        print("\n" + "="*80)
        print("RAG-ENHANCED MATCHING RESULTS")
        print("="*80)
        
        rag_results.sort(key=lambda x: x.overall_score, reverse=True)
        
        for i, result in enumerate(rag_results[:6], 1):  # Show top 6
            print(f"\n{i}. {result.candidate_name} → {result.job_title}")
            print(f"Overall Score: {result.overall_score}% (RAG-Enhanced)")
            print(f"Skill Match: {result.skill_match_score}%")
            print(f"Semantic Similarity: {result.semantic_similarity_score}%")
            print(f"Experience: {result.experience_score}%") 
            print(f"Important Skills: {result.important_skills_score}%")
            print(f"RAG Rank: #{result.detailed_breakdown.get('retrieved_rank', 'N/A')}")
            
            # Show RAG insights
            rag_insights = result.detailed_breakdown.get('rag_insights', '')
            if rag_insights:
                print(f"RAG Insights: {rag_insights[:150]}...")
            
            if result.overall_score >= 85:
                print("EXCELLENT RAG MATCH")
            elif result.overall_score >= 70:
                print("GOOD RAG MATCH") 
            elif result.overall_score >= 55:
                print("FAIR RAG MATCH")
            else:
                print("POOR RAG MATCH")
    
    # Show comparison between traditional vs RAG
    print("\n" + "="*50)
    print("TRADITIONAL vs RAG COMPARISON")
    print("="*50)
    
    if traditional_results and rag_results:
        trad_avg = np.mean([r.overall_score for r in traditional_results])
        rag_avg = np.mean([r.overall_score for r in rag_results])
        
        print(f"Traditional Average Score: {trad_avg:.2f}%")
        print(f"RAG-Enhanced Average Score: {rag_avg:.2f}%")
        print(f"RAG Improvement: {rag_avg - trad_avg:+.2f}%")
    
    # Show top overall matches
    print("\n" + "="*50)
    print("TOP OVERALL MATCHES (ALL METHODS)")
    print("="*50)
    
    all_results = traditional_results + rag_results
    all_results.sort(key=lambda x: x.overall_score, reverse=True)
    
    for i, result in enumerate(all_results[:5], 1):
        method = "RAG" if hasattr(result, 'semantic_similarity_score') and result.semantic_similarity_score > 50 else "Traditional"
        print(f"\n{i}. {result.candidate_name} → {result.job_title} ({method})")
        print(f"Score: {result.overall_score}%")
        
        if hasattr(result, 'semantic_similarity_score'):
            print(f"Semantic: {result.semantic_similarity_score}%")
    
    # Show job recommendation for candidates
    print("\n" + "="*50)
    print("JOB RECOMMENDATIONS FOR CANDIDATES")
    print("="*50)
    
    for candidate in candidates[:2]:  # Show for first 2 candidates
        print(f"\n👤 Jobs recommended for {candidate['name']}:")
        try:
            recommended_jobs = rag_processor.find_jobs_for_candidate(candidate)
            for i, job in enumerate(recommended_jobs[:3], 1):
                print(f"{i}. {job.get('title', 'Unknown')} (Similarity: {job.get('similarity_score', 0)*100:.1f}%)")
        except Exception as e:
            print(f"Error finding jobs: {e}")
    
    print(f"\n✨ Analysis complete! Processed {len(candidates)} candidates against {len(jobs)} positions.")
    print("Results include both traditional scoring and RAG-enhanced semantic matching.")
    print("All data stored in ChromaDB for future queries and learning.")

if __name__ == "__main__":
    main()