from typing import Dict, List, Any
import json
from dataclasses import dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

@dataclass
class CandidateProfile:
    """Structured candidate profile"""
    name: str
    contact: Dict[str, str]
    technical_vector: List[float]
    experience_vector: List[float]
    soft_skills_vector: List[float]
    industry_vector: List[float]
    raw_data: Dict[str, Any]
    metadata: Dict[str, Any]

class ResumePipeline:
    def __init__(self, model_manager, vector_store):
        self.model_manager = model_manager
        self.vector_store = vector_store
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def process_resume(self, resume_data: Dict[str, Any]) -> CandidateProfile:
        """Main pipeline: Resume → Models → Vectors → Profile"""
        try:
            # Stage 1: General Understanding (Mistral)
            general_understanding = await self._general_understanding(resume_data)
            
            # Stage 2: Technical Skills Analysis (CodeLlama)
            technical_analysis = await self._technical_analysis(
                resume_data, general_understanding
            )
            
            # Stage 3: Entity Extraction (DistilBERT)
            entities = await self._entity_extraction(resume_data)
            
            # Stage 4: Ensemble Coordination
            profile = await self._ensemble_coordination(
                resume_data, general_understanding, technical_analysis, entities
            )
            
            # Stage 5: Vector Generation
            vectors = await self._generate_vectors(profile)
            
            # Create final candidate profile
            candidate = CandidateProfile(
                name=profile['name'],
                contact=profile['contact'],
                technical_vector=vectors['technical'],
                experience_vector=vectors['experience'],
                soft_skills_vector=vectors['soft_skills'],
                industry_vector=vectors['industry'],
                raw_data=resume_data,
                metadata={
                    'processed_at': str(datetime.now()),
                    'pipeline_version': '1.0'
                }
            )
            
            # Store in vector database
            await self._store_candidate(candidate)
            
            return candidate
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            raise
    
    async def _general_understanding(self, resume_data: Dict) -> Dict:
        """Stage 1: Extract general understanding using Mistral"""
        prompt = f"""<s>[INST] Analyze this resume and extract:
1. Professional summary
2. Career level (Junior/Mid/Senior)
3. Key strengths
4. Industry focus
5. Career trajectory

Resume:
{json.dumps(resume_data['profile'], indent=2)}
[/INST]"""
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self.model_manager.inference_mistral,
            prompt,
            1024
        )
        
        # Parse structured output
        return self._parse_mistral_output(result)
    
    async def _technical_analysis(self, resume_data: Dict, general: Dict) -> Dict:
        """Stage 2: Deep technical skills analysis using CodeLlama"""
        skills = resume_data['profile'].get('skills', {}).get('technical', [])
        projects = resume_data['profile'].get('projects', [])
        
        prompt = f"""<s>[INST] Analyze technical expertise:

Skills: {', '.join(skills)}
Projects: {json.dumps(projects, indent=2)}

Evaluate:
1. Skill proficiency levels (1-10)
2. Technology stack coherence
3. Project complexity scores
4. Missing skills for seniority level
5. Technical growth trajectory
[/INST]"""
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self.model_manager.inference_codellama,
            prompt,
            1024
        )
        
        return self._parse_codellama_output(result)
    
    async def _entity_extraction(self, resume_data: Dict) -> List[Dict]:
        """Stage 3: Extract entities using DistilBERT NER"""
        # Combine all text
        text_parts = []
        
        # Add experience descriptions
        for exp in resume_data['profile'].get('experience', []):
            text_parts.extend(exp.get('description', []))
        
        # Add project descriptions
        for proj in resume_data['profile'].get('projects', []):
            text_parts.append(proj.get('description', ''))
        
        full_text = ' '.join(text_parts)
        
        loop = asyncio.get_event_loop()
        entities = await loop.run_in_executor(
            self.executor,
            self.model_manager.extract_entities,
            full_text
        )
        
        return entities
    
    async def _ensemble_coordination(self, resume_data: Dict, 
                                   general: Dict, technical: Dict, 
                                   entities: List[Dict]) -> Dict:
        """Stage 4: Coordinate outputs from all models"""
        profile = {
            'name': resume_data['profile']['name'],
            'contact': resume_data['profile']['contact'],
            'summary': general.get('summary', ''),
            'level': general.get('career_level', 'Mid'),
            'technical_skills': technical.get('skills_assessment', {}),
            'project_complexity': technical.get('project_scores', {}),
            'entities': self._organize_entities(entities),
            'strengths': general.get('key_strengths', []),
            'growth_areas': technical.get('missing_skills', [])
        }
        
        return profile
    
    async def _generate_vectors(self, profile: Dict) -> Dict[str, List[float]]:
        """Generate multi-dimensional vectors for matching"""
        from sentence_transformers import SentenceTransformer
        
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        vectors = {}
        
        # Technical vector
        tech_text = ' '.join([
            f"{skill} {details.get('proficiency', 5)}" 
            for skill, details in profile['technical_skills'].items()
        ])
        vectors['technical'] = model.encode(tech_text).tolist()
        
        # Experience vector
        exp_text = f"{profile['level']} {profile['summary']}"
        vectors['experience'] = model.encode(exp_text).tolist()
        
        # Soft skills vector
        soft_text = ' '.join(profile['strengths'])
        vectors['soft_skills'] = model.encode(soft_text).tolist()
        
        # Industry vector
        industry_text = ' '.join([
            entity['word'] for entity in profile['entities'].get('ORG', [])
        ])
        vectors['industry'] = model.encode(industry_text).tolist()
        
        return vectors
    
    async def _store_candidate(self, candidate: CandidateProfile):
        """Store candidate in vector database"""
        await self.vector_store.add_candidate(candidate)
    
    def _parse_mistral_output(self, output: str) -> Dict:
        """Parse Mistral output into structured data"""
        # Implementation depends on your prompt engineering
        # This is a simplified version
        lines = output.strip().split('\n')
        result = {
            'summary': '',
            'career_level': 'Mid',
            'key_strengths': [],
            'industry_focus': '',
            'trajectory': ''
        }
        
        current_section = None
        for line in lines:
            if 'Professional Summary:' in line:
                current_section = 'summary'
            elif 'Career Level:' in line:
                result['career_level'] = line.split(':')[1].strip()
            elif 'Key Strengths:' in line:
                current_section = 'strengths'
            elif current_section == 'summary':
                result['summary'] += line + ' '
            elif current_section == 'strengths' and line.strip():
                result['key_strengths'].append(line.strip('- '))
        
        return result
    
    def _parse_codellama_output(self, output: str) -> Dict:
        """Parse CodeLlama output for technical analysis"""
        # Simplified parser - extend based on your needs
        result = {
            'skills_assessment': {},
            'stack_coherence': 0,
            'project_scores': {},
            'missing_skills': [],
            'growth_trajectory': ''
        }
        
        lines = output.strip().split('\n')
        current_section = None
        
        for line in lines:
            if 'Skill Proficiency:' in line:
                current_section = 'skills'
            elif 'Missing Skills:' in line:
                current_section = 'missing'
            elif current_section == 'skills' and ':' in line:
                skill, score = line.split(':')
                try:
                    result['skills_assessment'][skill.strip()] = {
                        'proficiency': int(score.strip())
                    }
                except:
                    pass
            elif current_section == 'missing' and line.strip():
                result['missing_skills'].append(line.strip('- '))
        
        return result
    
    def _organize_entities(self, entities: List[Dict]) -> Dict[str, List[Dict]]:
        """Organize entities by type"""
        organized = {}
        for entity in entities:
            entity_type = entity['entity_group']
            if entity_type not in organized:
                organized[entity_type] = []
            organized[entity_type].append(entity)
        return organized