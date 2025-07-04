import chromadb
import faiss
import numpy as np
from typing import List, Dict, Any
import pickle
import json
from pathlib import Path

class VectorStore:
    def __init__(self, settings):
        self.settings = settings
        self.setup_stores()
    
    def setup_stores(self):
        """Initialize ChromaDB and FAISS"""
        # ChromaDB for metadata-rich storage
        self.chroma_client = chromadb.PersistentClient(
            path=self.settings.CHROMA_PERSIST_DIR
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name="candidates",
            metadata={"hnsw:space": "cosine"}
        )
        
        # FAISS for high-performance similarity search
        self.faiss_index = None
        self.faiss_metadata = []
        self._load_or_create_faiss()
    
    def _load_or_create_faiss(self):
        """Load existing FAISS index or create new one"""
        index_path = Path(self.settings.FAISS_INDEX_PATH)
        metadata_path = index_path.with_suffix('.meta')
        
        if index_path.exists():
            self.faiss_index = faiss.read_index(str(index_path))
            with open(metadata_path, 'rb') as f:
                self.faiss_metadata = pickle.load(f)
        else:
            # Create new index
            self.faiss_index = faiss.IndexFlatIP(self.settings.EMBEDDING_DIM)
            self.faiss_metadata = []
    
    async def add_candidate(self, candidate):
        """Add candidate to both stores"""
        # Prepare data
        candidate_id = f"candidate_{candidate.name.replace(' ', '_')}_{hash(str(candidate.contact))}"
        
        # Combine all vectors
        combined_vector = np.concatenate([
            candidate.technical_vector,
            candidate.experience_vector,
            candidate.soft_skills_vector,
            candidate.industry_vector
        ])
        
        # Normalize for FAISS
        normalized_vector = combined_vector / np.linalg.norm(combined_vector)
        
        # Add to ChromaDB
        self.collection.add(
            documents=[json.dumps(candidate.raw_data)],
            embeddings=[combined_vector.tolist()],
            metadatas=[{
                'name': candidate.name,
                'level': candidate.raw_data.get('level', 'Unknown'),
                'skills': ','.join(candidate.raw_data['profile']['skills']['technical']),
                'experience_years': self._estimate_experience_years(candidate.raw_data)
            }],
            ids=[candidate_id]
        )
        
        # Add to FAISS
        self.faiss_index.add(normalized_vector.reshape(1, -1))
        self.faiss_metadata.append({
            'id': candidate_id,
            'name': candidate.name,
            'vectors': {
                'technical': candidate.technical_vector,
                'experience': candidate.experience_vector,
                'soft_skills': candidate.soft_skills_vector,
                'industry': candidate.industry_vector
            }
        })
        
        # Save FAISS
        self._save_faiss()
    
    async def search_candidates(self, query_vector: np.ndarray, 
                              k: int = 10, filters: Dict = None) -> List[Dict]:
        """Search for similar candidates"""
        # Normalize query
        query_norm = query_vector / np.linalg.norm(query_vector)
        
        # FAISS search
        distances, indices = self.faiss_index.search(query_norm.reshape(1, -1), k * 2)
        
        # Get candidates from ChromaDB with metadata
        candidate_ids = [self.faiss_metadata[idx]['id'] for idx in indices[0] if idx < len(self.faiss_metadata)]
        
        # Apply filters if provided
        where_clause = {}
        if filters:
            if 'min_experience' in filters:
                where_clause['experience_years'] = {"$gte": filters['min_experience']}
            if 'required_skills' in filters:
                where_clause['skills'] = {"$contains": filters['required_skills']}
        
        results = self.collection.get(
            ids=candidate_ids,
            where=where_clause if where_clause else None
        )
        
        # Combine results with scores
        candidates = []
        for i, candidate_id in enumerate(candidate_ids):
            if candidate_id in results['ids']:
                idx = results['ids'].index(candidate_id)
                candidates.append({
                    'id': candidate_id,
                    'score': float(distances[0][i]),
                    'metadata': results['metadatas'][idx],
                    'data': json.loads(results['documents'][idx])
                })
        
        return candidates[:k]
    
    def _save_faiss(self):
        """Save FAISS index and metadata"""
        index_path = Path(self.settings.FAISS_INDEX_PATH)
        index_path.parent.mkdir(parents=True, exist_ok=True)
        
        faiss.write_index(self.faiss_index, str(index_path))
        
        with open(index_path.with_suffix('.meta'), 'wb') as f:
            pickle.dump(self.faiss_metadata, f)
    
    def _estimate_experience_years(self, resume_data: Dict) -> int:
        """Estimate years of experience from resume"""
        # Simple estimation - enhance based on your needs
        experience = resume_data['profile'].get('experience', [])
        return len(experience) * 2  # Rough estimate