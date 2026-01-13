"""
Sentence Embedder Module
========================

Embedding generation using Sentence Transformers.
"""

import numpy as np
from typing import List, Optional, Union
import os

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class SentenceEmbedder:
    """
    Generate sentence embeddings using pre-trained transformer models.
    
    Default model: all-MiniLM-L6-v2
    - Fast and efficient
    - 384 dimensional embeddings
    - Good quality for semantic similarity
    """
    
    # Singleton instances for different models
    _instances = {}
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedder with specified model.
        
        Args:
            model_name: Name of the sentence-transformer model
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = 384  # Default for MiniLM
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            # Check if model already loaded in singleton
            if self.model_name in SentenceEmbedder._instances:
                self.model = SentenceEmbedder._instances[self.model_name]
            else:
                print(f"Loading embedding model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                SentenceEmbedder._instances[self.model_name] = self.model
            
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            print(f"Model loaded. Embedding dimension: {self.embedding_dim}")
            
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.model = None
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress: bool = False,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Encode texts into embeddings.
        
        Args:
            texts: Single text or list of texts
            batch_size: Batch size for encoding
            show_progress: Show progress bar
            normalize: L2 normalize embeddings
            
        Returns:
            Numpy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts:
            return np.array([])
        
        if self.model is None:
            # Fallback to random embeddings
            return self._fallback_encode(texts)
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=normalize
        )
        
        return embeddings
    
    def _fallback_encode(self, texts: List[str]) -> np.ndarray:
        """Generate deterministic fallback embeddings."""
        import hashlib
        
        embeddings = []
        for text in texts:
            # Create deterministic embedding from text hash
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            rng = np.random.RandomState(int(text_hash[:8], 16) % (2**31))
            embedding = rng.randn(self.embedding_dim).astype(np.float32)
            # Normalize
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
            embeddings.append(embedding)
        
        return np.array(embeddings)
    
    def similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Similarity score (0-1)
        """
        # Normalize if not already
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        
        # Scale to 0-1 range
        return float((similarity + 1) / 2)
    
    def batch_similarity(
        self,
        query: np.ndarray,
        corpus: np.ndarray
    ) -> np.ndarray:
        """
        Compute similarity between query and all corpus embeddings.
        
        Args:
            query: Query embedding (1D)
            corpus: Corpus embeddings (2D)
            
        Returns:
            Array of similarity scores
        """
        # Normalize
        query_norm = query / (np.linalg.norm(query) + 1e-8)
        corpus_norms = np.linalg.norm(corpus, axis=1, keepdims=True) + 1e-8
        corpus_normalized = corpus / corpus_norms
        
        # Compute dot product
        similarities = np.dot(corpus_normalized, query_norm)
        
        # Scale to 0-1
        return (similarities + 1) / 2
    
    def save_embeddings(self, embeddings: np.ndarray, path: str):
        """Save embeddings to file."""
        np.save(path, embeddings)
    
    def load_embeddings(self, path: str) -> np.ndarray:
        """Load embeddings from file."""
        return np.load(path)


def get_embedder(model_name: str = "all-MiniLM-L6-v2") -> SentenceEmbedder:
    """Get or create embedder instance."""
    return SentenceEmbedder(model_name)
