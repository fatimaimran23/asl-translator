"""
train_real.py — Train the ASL classifier on real landmark data.

Run after collecting data with collect_real_data.py:
    python train_real.py
"""

import os
import numpy as np
from model.classifier import ASLClassifier

DATA_DIR = "data"
MODEL_PATH = "model/asl_model.pkl"

LETTERS = list("ABCDEFGHIKLMNOPQRSTUVWXY")


def load_real_data():
    X, y = [], []
    missing = []
    for letter in LETTERS:
        path = os.path.join(DATA_DIR, f"landmarks_{letter}.npy")
        if os.path.exists(path):
            data = np.load(path)
            X.extend(data)
            y.extend([letter] * len(data))
            print(f"  {letter}: {len(data)} samples")
        else:
            missing.append(letter)

    if missing:
        print(f"\nMissing data for: {missing}")
        print("Run collect_real_data.py for each missing letter.\n")

    return np.array(X), np.array(y)


if __name__ == "__main__":
    print("Loading real landmark data…")
    X, y = load_real_data()

    if len(X) == 0:
        print("No data found. Run collect_real_data.py first.")
        exit(1)

    print(f"\nTotal samples: {len(X)}")
    print("Training classifier…")

    clf = ASLClassifier()
    accuracy = clf.train(X, y)
    clf.save(MODEL_PATH)

    print(f"\nDone! Cross-validated accuracy: {accuracy:.2%}")
    print(f"Model saved to {MODEL_PATH}")
