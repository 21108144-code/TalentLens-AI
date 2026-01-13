"""
Embedding Service
=================

Service for generating text embeddings using Sentence Transformers.
"""

import numpy as np
from typing import List, Optional, Union
from loguru import logger

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("sentence-transformers not installed. Using fallback embeddings.")


class EmbeddingService:
    """
    Service for generating text embeddings using pre-trained transformer models.
    Uses all-MiniLM-L6-v2 by default (384 dimensions, fast, good quality).
    """
    
    _instance = None
    _model = None
    
    def __new__(cls):
        """Singleton pattern for model loading."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding service.
        
        Args:
            model_name: Sentence-transformer model name
        """
        self.model_name = model_name
        self.embedding_dim = 384  # Default for MiniLM
        
        if EMBEDDINGS_AVAILABLE and EmbeddingService._model is None:
            self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            EmbeddingService._model = SentenceTransformer(self.model_name)
            self.embedding_dim = EmbeddingService._model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded. Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            EmbeddingService._model = None
    
    async def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Numpy array of embeddings
        """
        if not EMBEDDINGS_AVAILABLE or EmbeddingService._model is None:
            return self._fallback_embedding(text)
        
        try:
            embedding = EmbeddingService._model.encode(
                text,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            return embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return self._fallback_embedding(text)
    
    async def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            Numpy array of embeddings (batch_size x embedding_dim)
        """
        if not texts:
            return np.array([])
        
        if not EMBEDDINGS_AVAILABLE or EmbeddingService._model is None:
            return np.array([self._fallback_embedding(t) for t in texts])
        
        try:
            embeddings = EmbeddingService._model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False,
                batch_size=32
            )
            return embeddings
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {e}")
            return np.array([self._fallback_embedding(t) for t in texts])
    
    def _fallback_embedding(self, text: str) -> np.ndarray:
        """
        Generate fallback embedding using simple TF-IDF-like approach.
        This is used when sentence-transformers is not available.
        
        Args:
            text: Input text
            
        Returns:
            Numpy array of pseudo-embeddings
        """
        # Simple fallback: random but deterministic embedding based on text hash
        import hashlib
        
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # Use hash to seed random generator for reproducibility
        rng = np.random.RandomState(int(text_hash[:8], 16) % (2**31))
        
        return rng.randn(self.embedding_dim).astype(np.float32)
    
    def compute_similarity(
        self, 
        embedding1: np.ndarray, 
        embedding2: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Similarity score (0-1)
        """
        # Normalize
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        
        # Clamp to [0, 1]
        return float(max(0.0, min(1.0, (similarity + 1) / 2)))
    
    def compute_batch_similarity(
        self,
        query_embedding: np.ndarray,
        corpus_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Compute similarities between a query and multiple corpus items.
        
        Args:
            query_embedding: Query embedding (1D)
            corpus_embeddings: Corpus embeddings (2D: n_items x embedding_dim)
            
        Returns:
            Array of similarity scores
        """
        # Normalize query
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
        
        # Normalize corpus
        corpus_norms = np.linalg.norm(corpus_embeddings, axis=1, keepdims=True) + 1e-8
        corpus_normalized = corpus_embeddings / corpus_norms
        
        # Compute similarities
        similarities = np.dot(corpus_normalized, query_norm)
        
        # Scale to [0, 1]
        return (similarities + 1) / 2
    
    def embedding_to_bytes(self, embedding: np.ndarray) -> bytes:
        """Convert embedding array to bytes for storage."""
        return embedding.astype(np.float32).tobytes()
    
    def bytes_to_embedding(self, data: bytes) -> np.ndarray:
        """Convert bytes back to embedding array."""
        return np.frombuffer(data, dtype=np.float32)
