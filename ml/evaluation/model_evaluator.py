"""
Model Evaluator Module
======================

Evaluation and metrics for ML models.
"""

from typing import Dict, List, Any, Optional
import numpy as np

try:
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score, f1_score,
        confusion_matrix, classification_report, roc_auc_score,
        precision_recall_curve, roc_curve
    )
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class ModelEvaluator:
    """
    Comprehensive model evaluation with multiple metrics.
    """
    
    def __init__(self):
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required for model evaluation")
    
    def evaluate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive model evaluation.
        
        Args:
            y_true: Ground truth labels
            y_pred: Predicted labels
            y_prob: Prediction probabilities (optional)
            
        Returns:
            Dictionary of evaluation metrics
        """
        metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred, zero_division=0),
            "f1": f1_score(y_true, y_pred, zero_division=0)
        }
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics["confusion_matrix"] = cm.tolist()
        
        # True/False Positives/Negatives
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
            metrics["true_positives"] = int(tp)
            metrics["true_negatives"] = int(tn)
            metrics["false_positives"] = int(fp)
            metrics["false_negatives"] = int(fn)
        
        # ROC-AUC if probabilities provided
        if y_prob is not None:
            try:
                metrics["roc_auc"] = roc_auc_score(y_true, y_prob)
            except:
                pass
        
        return metrics
    
    def compare_models(
        self,
        models_predictions: Dict[str, Dict],
        y_true: np.ndarray
    ) -> Dict[str, Dict]:
        """
        Compare multiple models.
        
        Args:
            models_predictions: Dict of model_name -> {y_pred, y_prob}
            y_true: Ground truth labels
            
        Returns:
            Comparison metrics for all models
        """
        comparison = {}
        
        for model_name, preds in models_predictions.items():
            y_pred = preds["y_pred"]
            y_prob = preds.get("y_prob")
            
            comparison[model_name] = self.evaluate(y_true, y_pred, y_prob)
        
        return comparison
    
    def get_classification_report(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        target_names: List[str] = None
    ) -> str:
        """
        Get detailed classification report.
        
        Args:
            y_true: Ground truth labels
            y_pred: Predicted labels
            target_names: Names for classes
            
        Returns:
            Classification report string
        """
        if target_names is None:
            target_names = ["No Match", "Match"]
        
        return classification_report(y_true, y_pred, target_names=target_names)
    
    def get_threshold_analysis(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray,
        thresholds: List[float] = None
    ) -> Dict[str, List]:
        """
        Analyze model performance at different thresholds.
        
        Args:
            y_true: Ground truth labels
            y_prob: Prediction probabilities
            thresholds: Thresholds to evaluate
            
        Returns:
            Metrics at each threshold
        """
        if thresholds is None:
            thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]
        
        results = {
            "threshold": [],
            "precision": [],
            "recall": [],
            "f1": [],
            "accuracy": []
        }
        
        for thresh in thresholds:
            y_pred = (y_prob >= thresh).astype(int)
            
            results["threshold"].append(thresh)
            results["precision"].append(precision_score(y_true, y_pred, zero_division=0))
            results["recall"].append(recall_score(y_true, y_pred, zero_division=0))
            results["f1"].append(f1_score(y_true, y_pred, zero_division=0))
            results["accuracy"].append(accuracy_score(y_true, y_pred))
        
        return results
    
    def find_optimal_threshold(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray,
        metric: str = "f1"
    ) -> Tuple[float, float]:
        """
        Find optimal threshold for a given metric.
        
        Args:
            y_true: Ground truth labels
            y_prob: Prediction probabilities
            metric: Metric to optimize (f1, precision, recall)
            
        Returns:
            Tuple of (optimal_threshold, metric_value)
        """
        best_threshold = 0.5
        best_score = 0
        
        for thresh in np.arange(0.1, 0.9, 0.05):
            y_pred = (y_prob >= thresh).astype(int)
            
            if metric == "f1":
                score = f1_score(y_true, y_pred, zero_division=0)
            elif metric == "precision":
                score = precision_score(y_true, y_pred, zero_division=0)
            elif metric == "recall":
                score = recall_score(y_true, y_pred, zero_division=0)
            else:
                raise ValueError(f"Unknown metric: {metric}")
            
            if score > best_score:
                best_score = score
                best_threshold = thresh
        
        return best_threshold, best_score


def print_evaluation_report(metrics: Dict[str, Any], model_name: str = "Model"):
    """Print formatted evaluation report."""
    print(f"\n{'='*50}")
    print(f"EVALUATION REPORT: {model_name}")
    print('='*50)
    
    print(f"\nClassification Metrics:")
    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall:    {metrics['recall']:.4f}")
    print(f"  F1 Score:  {metrics['f1']:.4f}")
    
    if "roc_auc" in metrics:
        print(f"  ROC-AUC:   {metrics['roc_auc']:.4f}")
    
    if "confusion_matrix" in metrics:
        print(f"\nConfusion Matrix:")
        cm = np.array(metrics["confusion_matrix"])
        print(f"  [[TN={cm[0,0]:4d}  FP={cm[0,1]:4d}]")
        print(f"   [FN={cm[1,0]:4d}  TP={cm[1,1]:4d}]]")
    
    print('='*50)
