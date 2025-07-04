import torch
from llama_cpp import Llama
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self, settings):
        self.settings = settings
        self.models = {}
        self.load_models()
    
    def load_models(self):
        """Load all models into memory"""
        try:
            # Load Mistral for general understanding
            self.models['mistral'] = Llama(
                model_path=self.settings.MISTRAL_MODEL_PATH,
                n_ctx=self.settings.MODEL_N_CTX,
                n_threads=self.settings.MODEL_N_THREADS,
                verbose=False
            )
            logger.info("Mistral model loaded successfully")
            
            # Load CodeLlama for technical skills
            self.models['codellama'] = Llama(
                model_path=self.settings.CODELLAMA_MODEL_PATH,
                n_ctx=self.settings.MODEL_N_CTX,
                n_threads=self.settings.MODEL_N_THREADS,
                verbose=False
            )
            logger.info("CodeLlama model loaded successfully")
            
            # Load DistilBERT for NER
            tokenizer = AutoTokenizer.from_pretrained(self.settings.DISTILBERT_MODEL_NAME)
            model = AutoModelForTokenClassification.from_pretrained(
                self.settings.DISTILBERT_MODEL_NAME
            )
            self.models['ner'] = pipeline(
                "ner", 
                model=model, 
                tokenizer=tokenizer,
                aggregation_strategy="simple"
            )
            logger.info("DistilBERT NER model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
    
    def get_model(self, model_name: str):
        """Get a specific model"""
        return self.models.get(model_name)
    
    def inference_mistral(self, prompt: str, max_tokens: int = 512) -> str:
        """Run inference on Mistral model"""
        try:
            response = self.models['mistral'](
                prompt,
                max_tokens=max_tokens,
                temperature=self.settings.MODEL_TEMPERATURE,
                stop=["</s>", "\n\n"]
            )
            return response['choices'][0]['text'].strip()
        except Exception as e:
            logger.error(f"Mistral inference error: {str(e)}")
            return ""
    
    def inference_codellama(self, prompt: str, max_tokens: int = 512) -> str:
        """Run inference on CodeLlama model"""
        try:
            response = self.models['codellama'](
                prompt,
                max_tokens=max_tokens,
                temperature=0.3,  # Lower temperature for technical analysis
                stop=["</s>", "\n\n"]
            )
            return response['choices'][0]['text'].strip()
        except Exception as e:
            logger.error(f"CodeLlama inference error: {str(e)}")
            return ""
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities using DistilBERT"""
        try:
            entities = self.models['ner'](text)
            return entities
        except Exception as e:
            logger.error(f"NER extraction error: {str(e)}")
            return []