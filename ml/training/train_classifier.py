"""
Model Training Module
=====================

Training scripts for resume-job matching classifiers.
"""

import os
import json
import pickle
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import numpy as np

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from ml.preprocessing.feature_engineer import FeatureEngineer


class ModelTrainer:
    """
    Trainer for resume-job matching classification models.
    
    Trains and compares:
    - Logistic Regression (baseline, interpretable)
    - Random Forest (robust, handles non-linearity)
    - Gradient Boosting (high performance)
    """
    
    def __init__(self, model_dir: str = "./ml/models"):
        """
        Initialize trainer.
        
        Args:
            model_dir: Directory to save trained models
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required for model training")
        
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.feature_engineer = FeatureEngineer()
        self.scaler = StandardScaler()
        
        # Initialize models
        self.models = {
            "logistic_regression": LogisticRegression(
                max_iter=1000,
                class_weight='balanced',
                random_state=42
            ),
            "random_forest": RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                class_weight='balanced',
                random_state=42,
                n_jobs=-1
            ),
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        }
        
        self.trained_models = {}
        self.evaluation_results = {}
    
    def prepare_data(
        self,
        resume_job_pairs: List[Dict],
        labels: List[int]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data from resume-job pairs.
        
        Args:
            resume_job_pairs: List of dicts with 'resume' and 'job' data
            labels: List of binary labels (1=match, 0=no match)
            
        Returns:
            Feature matrix X and label array y
        """
        X = []
        
        for pair in resume_job_pairs:
            features = self.feature_engineer.extract_features(
                pair["resume"],
                pair["job"]
            )
            feature_vector = self.feature_engineer.features_to_vector(features)
            X.append(feature_vector)
        
        X = np.array(X)
        y = np.array(labels)
        
        return X, y
    
    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2,
        cross_validate: bool = True
    ) -> Dict[str, Any]:
        """
        Train all models and evaluate.
        
        Args:
            X: Feature matrix
            y: Labels
            test_size: Test set proportion
            cross_validate: Perform cross-validation
            
        Returns:
            Training results and metrics
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        results = {}
        
        for name, model in self.models.items():
            print(f"\nTraining {name}...")
            
            # Train
            model.fit(X_train_scaled, y_train)
            self.trained_models[name] = model
            
            # Predict
            y_pred = model.predict(X_test_scaled)
            
            # Evaluate
            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, zero_division=0),
                "recall": recall_score(y_test, y_pred, zero_division=0),
                "f1": f1_score(y_test, y_pred, zero_division=0)
            }
            
            # Cross-validation
            if cross_validate:
                cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
                metrics["cv_mean"] = cv_scores.mean()
                metrics["cv_std"] = cv_scores.std()
            
            results[name] = metrics
            self.evaluation_results[name] = metrics
            
            print(f"  Accuracy: {metrics['accuracy']:.4f}")
            print(f"  F1 Score: {metrics['f1']:.4f}")
        
        return results
    
    def get_best_model(self) -> Tuple[str, Any]:
        """
        Get the best performing model based on F1 score.
        
        Returns:
            Tuple of (model_name, model_instance)
        """
        if not self.evaluation_results:
            raise ValueError("No models trained yet")
        
        best_name = max(
            self.evaluation_results,
            key=lambda k: self.evaluation_results[k]["f1"]
        )
        
        return best_name, self.trained_models[best_name]
    
    def get_feature_importance(self, model_name: str = None) -> Dict[str, float]:
        """
        Get feature importance from trained model.
        
        Args:
            model_name: Model to get importance from (default: best model)
            
        Returns:
            Dictionary of feature names to importance scores
        """
        if model_name is None:
            model_name, _ = self.get_best_model()
        
        model = self.trained_models.get(model_name)
        if model is None:
            raise ValueError(f"Model {model_name} not found")
        
        feature_names = self.feature_engineer.feature_names
        
        # Get importance based on model type
        if hasattr(model, 'feature_importances_'):
            # Random Forest, Gradient Boosting
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            # Logistic Regression
            importances = np.abs(model.coef_[0])
        else:
            return {}
        
        # Normalize
        importances = importances / importances.sum()
        
        return dict(zip(feature_names, importances))
    
    def save_models(self, prefix: str = ""):
        """
        Save all trained models to disk.
        
        Args:
            prefix: Prefix for model filenames
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for name, model in self.trained_models.items():
            filename = f"{prefix}{name}_{timestamp}.joblib"
            filepath = os.path.join(self.model_dir, filename)
            joblib.dump(model, filepath)
            print(f"Saved {name} to {filepath}")
        
        # Save scaler
        scaler_path = os.path.join(self.model_dir, f"{prefix}scaler_{timestamp}.joblib")
        joblib.dump(self.scaler, scaler_path)
        
        # Save evaluation results
        results_path = os.path.join(self.model_dir, f"{prefix}results_{timestamp}.json")
        with open(results_path, 'w') as f:
            json.dump(self.evaluation_results, f, indent=2)
        
        # Save best model info
        best_name, _ = self.get_best_model()
        best_info = {
            "best_model": best_name,
            "metrics": self.evaluation_results[best_name],
            "feature_importance": self.get_feature_importance(best_name),
            "timestamp": timestamp
        }
        best_path = os.path.join(self.model_dir, f"{prefix}best_model_info.json")
        with open(best_path, 'w') as f:
            json.dump(best_info, f, indent=2)
    
    def load_model(self, model_path: str):
        """
        Load a trained model from disk.
        
        Args:
            model_path: Path to saved model file
            
        Returns:
            Loaded model
        """
        return joblib.load(model_path)


def generate_synthetic_data(n_samples: int = 1000) -> Tuple[List[Dict], List[int]]:
    """
    Generate synthetic training data for testing.
    
    Args:
        n_samples: Number of samples to generate
        
    Returns:
        Tuple of (resume_job_pairs, labels)
    """
    import random
    
    skills_pool = [
        "python", "javascript", "java", "sql", "react", "node.js",
        "machine learning", "data analysis", "aws", "docker", "git",
        "tensorflow", "pandas", "flask", "django", "mongodb"
    ]
    
    pairs = []
    labels = []
    
    for _ in range(n_samples):
        # Generate resume
        resume_skills = random.sample(skills_pool, random.randint(3, 8))
        resume = {
            "skills": resume_skills,
            "experience_years": random.randint(0, 15),
            "education": [{"degree": random.choice(["bachelor", "master", "phd"])}],
            "raw_text": f"Experienced professional with skills in {', '.join(resume_skills)}"
        }
        
        # Generate job
        job_skills = random.sample(skills_pool, random.randint(3, 6))
        job = {
            "skills_required": job_skills,
            "experience_required": random.randint(1, 10),
            "education_required": random.choice(["bachelor", "master", ""]),
            "description": f"Looking for someone with {', '.join(job_skills)}"
        }
        
        # Determine label based on skill overlap and experience
        skill_overlap = len(set(resume_skills) & set(job_skills)) / len(job_skills)
        exp_ratio = resume["experience_years"] / max(1, job["experience_required"])
        
        # Label: 1 if good match, 0 otherwise
        match_score = 0.6 * skill_overlap + 0.4 * min(1, exp_ratio)
        label = 1 if match_score > 0.5 + random.uniform(-0.1, 0.1) else 0
        
        pairs.append({"resume": resume, "job": job})
        labels.append(label)
    
    return pairs, labels


if __name__ == "__main__":
    # Example training run
    print("Generating synthetic training data...")
    pairs, labels = generate_synthetic_data(1000)
    
    print(f"Generated {len(pairs)} samples")
    print(f"Positive samples: {sum(labels)} ({sum(labels)/len(labels)*100:.1f}%)")
    
    trainer = ModelTrainer()
    
    print("\nPreparing features...")
    X, y = trainer.prepare_data(pairs, labels)
    print(f"Feature matrix shape: {X.shape}")
    
    print("\nTraining models...")
    results = trainer.train(X, y)
    
    print("\n" + "="*50)
    print("TRAINING RESULTS")
    print("="*50)
    for name, metrics in results.items():
        print(f"\n{name}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.4f}")
    
    best_name, _ = trainer.get_best_model()
    print(f"\nBest model: {best_name}")
    
    print("\nFeature importance:")
    importance = trainer.get_feature_importance()
    for feat, imp in sorted(importance.items(), key=lambda x: x[1], reverse=True):
        print(f"  {feat}: {imp:.4f}")
    
    trainer.save_models()
    print("\nModels saved!")
