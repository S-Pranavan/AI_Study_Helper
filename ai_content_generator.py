#!/usr/bin/env python3
"""
AI Study Helper - Phase 2: AI Content Generation
AI-powered content generation using Hugging Face models
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re
import json

try:
    from transformers import (
        pipeline, 
        AutoTokenizer, 
        AutoModelForSeq2SeqLM,
        AutoModelForMaskedLM
    )
    from sentence_transformers import SentenceTransformer
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers library not available. Install with: pip install transformers torch sentence-transformers")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContentGenerationResult:
    """Result of AI content generation"""
    success: bool
    content: str
    model_used: str
    processing_time: float
    confidence_score: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict] = None

class AIContentGenerator:
    """AI-powered content generation using Hugging Face models"""
    
    def __init__(self, use_gpu: bool = False, cache_dir: str = "./model_cache"):
        """
        Initialize AI Content Generator
        
        Args:
            use_gpu: Whether to use GPU acceleration
            cache_dir: Directory to cache downloaded models
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers library is required. Install with: pip install transformers torch sentence-transformers")
        
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.cache_dir = cache_dir
        self.device = "cuda" if self.use_gpu else "cpu"
        
        # Initialize models
        self.summarizer = None
        self.explainer = None
        self.keyword_extractor = None
        self.sentence_transformer = None
        
        # Model configurations
        self.model_configs = {
            'summarization': {
                'model_name': 'facebook/bart-large-cnn',
                'max_length': 150,
                'min_length': 50,
                'do_sample': False
            },
            'explanation': {
                'model_name': 't5-base',
                'max_length': 200,
                'min_length': 100,
                'do_sample': True,
                'temperature': 0.7
            },
            'keywords': {
                'model_name': 'distilbert-base-uncased',
                'max_keywords': 10
            }
        }
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all AI models"""
        try:
            logger.info("Initializing AI models...")
            
            # Initialize summarization model (BART)
            logger.info("Loading BART summarization model...")
            self.summarizer = pipeline(
                "summarization",
                model=self.model_configs['summarization']['model_name'],
                device=0 if self.use_gpu else -1,
                cache_dir=self.cache_dir
            )
            
            # Initialize explanation model (T5)
            logger.info("Loading T5 explanation model...")
            self.explainer = pipeline(
                "text2text-generation",
                model=self.model_configs['explanation']['model_name'],
                device=0 if self.use_gpu else -1,
                cache_dir=self.cache_dir
            )
            
            # Initialize keyword extraction model
            logger.info("Loading DistilBERT keyword extraction model...")
            self.keyword_extractor = pipeline(
                "fill-mask",
                model=self.model_configs['keywords']['model_name'],
                device=0 if self.use_gpu else -1,
                cache_dir=self.cache_dir
            )
            
            # Initialize sentence transformer for semantic similarity
            logger.info("Loading sentence transformer model...")
            self.sentence_transformer = SentenceTransformer(
                'all-MiniLM-L6-v2',
                cache_folder=self.cache_dir
            )
            
            logger.info("All AI models initialized successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
            raise
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for AI models
        
        Args:
            text: Input text to preprocess
            
        Returns:
            Preprocessed text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might interfere with models
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        # Ensure text is not too long for models
        max_length = 1024
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text
    
    def generate_summary(self, text: str, max_length: int = None) -> ContentGenerationResult:
        """
        Generate a concise summary of the input text
        
        Args:
            text: Input text to summarize
            max_length: Maximum length of summary
            
        Returns:
            ContentGenerationResult with generated summary
        """
        start_time = time.time()
        
        try:
            if not self.summarizer:
                return ContentGenerationResult(
                    success=False,
                    content="",
                    model_used="BART",
                    processing_time=0,
                    error_message="Summarization model not initialized"
                )
            
            # Preprocess text
            processed_text = self.preprocess_text(text)
            if not processed_text:
                return ContentGenerationResult(
                    success=False,
                    content="",
                    model_used="BART",
                    processing_time=0,
                    error_message="No valid text to summarize"
                )
            
            # Generate summary
            config = self.model_configs['summarization']
            max_len = max_length or config['max_length']
            
            summary_result = self.summarizer(
                processed_text,
                max_length=max_len,
                min_length=config['min_length'],
                do_sample=config['do_sample']
            )
            
            summary = summary_result[0]['summary_text']
            processing_time = time.time() - start_time
            
            return ContentGenerationResult(
                success=True,
                content=summary,
                model_used="BART",
                processing_time=processing_time,
                confidence_score=0.85,  # BART typically has high confidence
                metadata={
                    'original_length': len(text),
                    'summary_length': len(summary),
                    'compression_ratio': len(summary) / len(text)
                }
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error generating summary: {str(e)}")
            return ContentGenerationResult(
                success=False,
                content="",
                model_used="BART",
                processing_time=processing_time,
                error_message=str(e)
            )
    
    def generate_explanation(self, text: str, style: str = "simple") -> ContentGenerationResult:
        """
        Generate an explanation of the input text
        
        Args:
            text: Input text to explain
            style: Explanation style ("simple", "detailed", "step_by_step")
            
        Returns:
            ContentGenerationResult with generated explanation
        """
        start_time = time.time()
        
        try:
            if not self.explainer:
                return ContentGenerationResult(
                    success=False,
                    content="",
                    model_used="T5",
                    processing_time=0,
                    error_message="Explanation model not initialized"
                )
            
            # Preprocess text
            processed_text = self.preprocess_text(text)
            if not processed_text:
                return ContentGenerationResult(
                    success=False,
                    content="",
                    model_used="T5",
                    processing_time=0,
                    error_message="No valid text to explain"
                )
            
            # Create prompt based on style
            prompts = {
                "simple": f"explain simply: {processed_text}",
                "detailed": f"explain in detail: {processed_text}",
                "step_by_step": f"explain step by step: {processed_text}"
            }
            
            prompt = prompts.get(style, prompts["simple"])
            
            # Generate explanation
            config = self.model_configs['explanation']
            explanation_result = self.explainer(
                prompt,
                max_length=config['max_length'],
                min_length=config['min_length'],
                do_sample=config['do_sample'],
                temperature=config['temperature']
            )
            
            explanation = explanation_result[0]['generated_text']
            processing_time = time.time() - start_time
            
            return ContentGenerationResult(
                success=True,
                content=explanation,
                model_used="T5",
                processing_time=processing_time,
                confidence_score=0.80,
                metadata={
                    'style': style,
                    'original_length': len(text),
                    'explanation_length': len(explanation)
                }
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error generating explanation: {str(e)}")
            return ContentGenerationResult(
                success=False,
                content="",
                model_used="T5",
                processing_time=0,
                error_message=str(e)
            )
    
    def extract_keywords(self, text: str, max_keywords: int = None) -> ContentGenerationResult:
        """
        Extract key concepts and keywords from text
        
        Args:
            text: Input text to analyze
            max_keywords: Maximum number of keywords to extract
            
        Returns:
            ContentGenerationResult with extracted keywords
        """
        start_time = time.time()
        
        try:
            if not self.sentence_transformer:
                return ContentGenerationResult(
                    success=False,
                    content="",
                    model_used="DistilBERT",
                    processing_time=0,
                    error_message="Keyword extraction model not initialized"
                )
            
            # Preprocess text
            processed_text = self.preprocess_text(text)
            if not processed_text:
                return ContentGenerationResult(
                    success=False,
                    content="",
                    model_used="DistilBERT",
                    processing_time=0,
                    error_message="No valid text to analyze"
                )
            
            # Extract keywords using sentence transformer
            max_kw = max_keywords or self.model_configs['keywords']['max_keywords']
            
            # Split text into sentences for better keyword extraction
            sentences = re.split(r'[.!?]+', processed_text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return ContentGenerationResult(
                    success=False,
                    content="",
                    model_used="DistilBERT",
                    processing_time=0,
                    error_message="No valid sentences found"
                )
            
            # Get embeddings for sentences
            embeddings = self.sentence_transformer.encode(sentences)
            
            # Simple keyword extraction based on sentence importance
            # In a more sophisticated implementation, you could use TF-IDF or other methods
            keywords = []
            for i, sentence in enumerate(sentences[:max_kw]):
                # Extract potential keywords (words with capital letters or technical terms)
                words = re.findall(r'\b[A-Z][a-z]+|\b[a-z]+[A-Z][a-z]*\b', sentence)
                if words:
                    keywords.extend(words[:2])  # Take up to 2 keywords per sentence
            
            # Remove duplicates and limit
            keywords = list(set(keywords))[:max_kw]
            
            processing_time = time.time() - start_time
            
            return ContentGenerationResult(
                success=True,
                content=json.dumps(keywords),
                model_used="DistilBERT",
                processing_time=processing_time,
                confidence_score=0.75,
                metadata={
                    'keywords_count': len(keywords),
                    'sentences_analyzed': len(sentences),
                    'keywords': keywords
                }
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error extracting keywords: {str(e)}")
            return ContentGenerationResult(
                success=False,
                content="",
                model_used="DistilBERT",
                processing_time=0,
                error_message=str(e)
            )
    
    def generate_study_materials(self, text: str) -> Dict[str, ContentGenerationResult]:
        """
        Generate comprehensive study materials from input text
        
        Args:
            text: Input text to process
            
        Returns:
            Dictionary containing all generated content
        """
        results = {}
        
        # Generate summary
        logger.info("Generating summary...")
        results['summary'] = self.generate_summary(text)
        
        # Generate explanation
        logger.info("Generating explanation...")
        results['explanation'] = self.generate_explanation(text, style="simple")
        
        # Extract keywords
        logger.info("Extracting keywords...")
        results['keywords'] = self.extract_keywords(text)
        
        return results
    
    def get_model_info(self) -> Dict[str, any]:
        """Get information about loaded models"""
        return {
            'summarization_model': self.model_configs['summarization']['model_name'],
            'explanation_model': self.model_configs['explanation']['model_name'],
            'keyword_model': self.model_configs['keywords']['model_name'],
            'device': self.device,
            'gpu_available': torch.cuda.is_available() if TRANSFORMERS_AVAILABLE else False,
            'models_loaded': {
                'summarizer': self.summarizer is not None,
                'explainer': self.explainer is not None,
                'keyword_extractor': self.keyword_extractor is not None,
                'sentence_transformer': self.sentence_transformer is not None
            }
        }
    
    def cleanup(self):
        """Clean up models and free memory"""
        try:
            if self.use_gpu and torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info("AI models cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

# Example usage and testing
if __name__ == "__main__":
    try:
        # Initialize AI generator
        ai_generator = AIContentGenerator(use_gpu=False)
        
        # Test text
        test_text = """
        Machine learning is a subset of artificial intelligence that focuses on the development 
        of computer programs that can access data and use it to learn for themselves. The process 
        of learning begins with observations or data, such as examples, direct experience, or 
        instruction, in order to look for patterns in data and make better decisions in the future 
        based on the examples that we provide. The primary aim is to allow the computers learn 
        automatically without human intervention or assistance and adjust actions accordingly.
        """
        
        print("🤖 AI Content Generator Test")
        print("=" * 50)
        
        # Generate study materials
        results = ai_generator.generate_study_materials(test_text)
        
        print(f"\n📝 Summary:")
        print(f"Success: {results['summary'].success}")
        print(f"Content: {results['summary'].content}")
        print(f"Time: {results['summary'].processing_time:.2f}s")
        
        print(f"\n🔍 Explanation:")
        print(f"Success: {results['explanation'].success}")
        print(f"Content: {results['explanation'].content}")
        print(f"Time: {results['explanation'].processing_time:.2f}s")
        
        print(f"\n🏷️ Keywords:")
        print(f"Success: {results['keywords'].success}")
        print(f"Content: {results['keywords'].content}")
        print(f"Time: {results['keywords'].processing_time:.2f}s")
        
        # Cleanup
        ai_generator.cleanup()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("Make sure you have installed the required packages:")
        print("pip install transformers torch sentence-transformers")
