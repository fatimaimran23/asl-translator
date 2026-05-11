import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from typing import Optional
import logging

logger = logging.getLogger(__name__)

ASL_LETTERS = list("ABCDEFGHIKLMNOPQRSTUVWXY")  # J and Z excluded (require motion)


class ASLClassifier:
    """
    Random Forest classifier for ASL fingerspelling.

    Input:  63-dim normalised landmark vector (21 landmarks x 3 axes)
    Output: ASL letter (A-Y, excluding J and Z which need motion)

    Architecture choice: Random Forest over deep learning for:
      - No GPU needed, runs on CPU instantly
      - Interpretable feature importance
      - Robust with limited data
      - <1ms inference time
    """

    def __init__(self):
        self.pipeline: Optional[Pipeline] = None
        self.classes: list[str] = []
        self.is_trained: bool = False

    def _build_pipeline(self) -> Pipeline:
        return Pipeline([
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(
                n_estimators=300,
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1,
                max_features="sqrt",
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            )),
        ])

    def train(self, X: np.ndarray, y: np.ndarray) -> float:
        """Train and cross-validate. Returns mean CV accuracy."""
        self.pipeline = self._build_pipeline()

        scores = cross_val_score(self.pipeline, X, y, cv=5, scoring="accuracy", n_jobs=-1)
        logger.info(f"CV accuracy: {scores.mean():.4f} ± {scores.std():.4f}")

        self.pipeline.fit(X, y)
        self.classes = list(self.pipeline.classes_)
        self.is_trained = True

        return float(scores.mean())

    def predict(self, features: np.ndarray) -> tuple[str, float, list[dict]]:
        """
        Returns (predicted_letter, confidence, top3_predictions).
        top3 is a list of {"letter": str, "probability": float}.
        """
        if not self.is_trained or self.pipeline is None:
            raise RuntimeError("Model not trained.")

        x = features.reshape(1, -1)
        proba = self.pipeline.predict_proba(x)[0]
        top3_idx = np.argsort(proba)[::-1][:3]

        letter = self.classes[top3_idx[0]]
        confidence = float(proba[top3_idx[0]])
        top3 = [
            {"letter": self.classes[i], "probability": round(float(proba[i]), 4)}
            for i in top3_idx
        ]

        return letter, confidence, top3

    def save(self, path: str):
        with open(path, "wb") as f:
            pickle.dump({"pipeline": self.pipeline, "classes": self.classes}, f)
        logger.info(f"Model saved to {path}")

    def load(self, path: str):
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.pipeline = data["pipeline"]
        self.classes = data["classes"]
        self.is_trained = True
        logger.info(f"Model loaded from {path} — classes: {self.classes}")
