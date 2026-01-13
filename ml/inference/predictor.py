"""
Predictor Module
================

Inference pipeline for resume-job matching.
"""

import os
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

from ml.preprocessing.feature_engineer import FeatureEngineer
from ml.embeddings.sentence_embedder import SentenceEmbedder


class MatchPredictor:
    """
    Inference pipeline for resume-job matching predictions.
    Combines feature-based and embedding-based approaches.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        scaler_path: Optional[str] = None,
        use_embeddings: bool = True
    ):
        """
        Initialize predictor.
        
        Args:
            model_path: Path to trained model file
            scaler_path: Path to fitted scaler file
            use_embeddings: Whether to use embedding-based features
        """
        self.feature_engineer = FeatureEngineer()
        self.use_embeddings = use_embeddings
        
        if use_embeddings:
            self.embedder = SentenceEmbedder()
        else:
            self.embedder = None
        
        self.model = None
        self.scaler = None
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        
        if scaler_path and os.path.exists(scaler_path):
            self.load_scaler(scaler_path)
    
    def load_model(self, path: str):
        """Load trained model from disk."""
        if not JOBLIB_AVAILABLE:
            raise ImportError("joblib is required to load models")
        
        self.model = joblib.load(path)
        print(f"Model loaded from {path}")
    
    def load_scaler(self, path: str):
        """Load fitted scaler from disk."""
        if not JOBLIB_AVAILABLE:
            raise ImportError("joblib is required to load scaler")
        
        self.scaler = joblib.load(path)
        print(f"Scaler loaded from {path}")
    
    def predict(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict match score for resume-job pair.
        
        Args:
            resume_data: Resume information
            job_data: Job information
            
        Returns:
            Prediction results with scores and explanation
        """
        # Extract features
        features = self.feature_engineer.extract_features(resume_data, job_data)
        feature_vector = self.feature_engineer.features_to_vector(features)
        
        # Calculate embedding-based similarity
        embedding_score = 0.0
        if self.use_embeddings and self.embedder:
            embedding_score = self._calculate_embedding_similarity(
                resume_data.get("raw_text", ""),
                job_data.get("description", "")
            )
        
        # Model prediction
        if self.model is not None:
            # Scale features
            if self.scaler is not None:
                feature_vector = self.scaler.transform([feature_vector])[0]
            
            # Get prediction and probability
            prediction = self.model.predict([feature_vector])[0]
            
            if hasattr(self.model, 'predict_proba'):
                proba = self.model.predict_proba([feature_vector])[0]
                confidence = max(proba)
                match_probability = proba[1] if len(proba) > 1 else proba[0]
            else:
                confidence = 0.8
                match_probability = float(prediction)
        else:
            # Fallback: rule-based scoring
            skill_score = features["skill_overlap_ratio"]
            exp_score = features["experience_ratio"]
            edu_score = features["education_level_ratio"]
            
            match_probability = (
                0.5 * skill_score +
                0.2 * exp_score +
                0.1 * edu_score +
                0.2 * embedding_score
            )
            prediction = 1 if match_probability >= 0.5 else 0
            confidence = abs(match_probability - 0.5) * 2
        
        # Combine scores
        overall_score = (
            0.6 * match_probability +
            0.4 * embedding_score
        ) * 100
        
        return {
            "match": bool(prediction),
            "overall_score": round(overall_score, 2),
            "match_probability": round(match_probability, 4),
            "semantic_similarity": round(embedding_score, 4),
            "confidence": round(confidence, 4),
            "features": features,
            "explanation": self._generate_explanation(features, overall_score)
        }
    
    def predict_batch(
        self,
        resume_data: Dict[str, Any],
        jobs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Predict match scores for one resume against multiple jobs.
        
        Args:
            resume_data: Resume information
            jobs: List of job dictionaries
            
        Returns:
            List of predictions sorted by score
        """
        predictions = []
        
        for i, job in enumerate(jobs):
            pred = self.predict(resume_data, job)
            pred["job_index"] = i
            pred["job_id"] = job.get("id")
            predictions.append(pred)
        
        # Sort by score
        predictions.sort(key=lambda x: x["overall_score"], reverse=True)
        
        return predictions
    
    def _calculate_embedding_similarity(
        self,
        resume_text: str,
        job_text: str
    ) -> float:
        """Calculate embedding-based similarity."""
        if not resume_text or not job_text:
            return 0.5
        
        try:
            embeddings = self.embedder.encode([resume_text, job_text])
            similarity = self.embedder.similarity(embeddings[0], embeddings[1])
            return similarity
        except Exception as e:
            print(f"Embedding error: {e}")
            return 0.5
    
    def _generate_explanation(
        self,
        features: Dict[str, float],
        score: float
    ) -> str:
        """Generate human-readable explanation."""
        parts = []
        
        # Overall assessment
        if score >= 80:
            parts.append("Excellent match!")
        elif score >= 60:
            parts.append("Good match with some gaps.")
        elif score >= 40:
            parts.append("Moderate match. Consider skill development.")
        else:
            parts.append("Limited match. Significant gaps identified.")
        
        # Skill analysis
        skill_ratio = features.get("skill_overlap_ratio", 0)
        if skill_ratio >= 0.8:
            parts.append(f"Strong skill alignment ({skill_ratio*100:.0f}% match).")
        elif skill_ratio >= 0.5:
            parts.append(f"Partial skill match ({skill_ratio*100:.0f}%).")
        else:
            parts.append(f"Skill gaps present ({skill_ratio*100:.0f}% match).")
        
        # Experience
        if features.get("experience_meets_req", 0):
            parts.append("Experience meets requirements.")
        elif features.get("experience_ratio", 0) > 0.5:
            parts.append("Experience partially meets requirements.")
        
        return " ".join(parts)
    
    def get_top_recommendations(
        self,
        resume_data: Dict[str, Any],
        jobs: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get top K job recommendations.
        
        Args:
            resume_data: Resume information
            jobs: List of jobs to rank
            top_k: Number of recommendations
            
        Returns:
            Top K jobs with predictions
        """
        predictions = self.predict_batch(resume_data, jobs)
        return predictions[:top_k]


def get_predictor(
    model_path: Optional[str] = None,
    scaler_path: Optional[str] = None
) -> MatchPredictor:
    """Factory function to create predictor instance."""
    return MatchPredictor(model_path, scaler_path)
