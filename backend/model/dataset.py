"""
ASL Landmark Dataset

PRODUCTION USE:
  Replace generate_synthetic_dataset() with real data from:
  - Kaggle ASL Alphabet dataset (images → run through MediaPipe to get landmarks)
  - https://www.kaggle.com/datasets/grassknoted/asl-alphabet
  - Use collect_real_data.py to record your own landmarks via webcam

The synthetic data here is for demo/development only. With real landmark
data, accuracy should exceed 95% on held-out test sets.
"""

import numpy as np
from typing import Tuple

LETTERS = list("ABCDEFGHIKLMNOPQRSTUVWXY")

# Approximate hand configurations per ASL letter.
# Each tuple is (finger_states, thumb_state, special_notes)
# finger_states: [index, middle, ring, pinky] 1=extended, 0=curled
# These approximate real ASL handshapes for landmark simulation.
ASL_CONFIGS = {
    "A": {"fingers": [0, 0, 0, 0], "thumb": "side",   "wrist_rot": 0.0},
    "B": {"fingers": [1, 1, 1, 1], "thumb": "across",  "wrist_rot": 0.0},
    "C": {"fingers": [0.5,0.5,0.5,0.5], "thumb": "curved", "wrist_rot": 0.2},
    "D": {"fingers": [1, 0, 0, 0], "thumb": "circle",  "wrist_rot": 0.0},
    "E": {"fingers": [0.2,0.2,0.2,0.2], "thumb": "under","wrist_rot": 0.0},
    "F": {"fingers": [0, 1, 1, 1], "thumb": "circle",  "wrist_rot": 0.0},
    "G": {"fingers": [1, 0, 0, 0], "thumb": "point",   "wrist_rot": 0.5},
    "H": {"fingers": [1, 1, 0, 0], "thumb": "side",    "wrist_rot": 0.5},
    "I": {"fingers": [0, 0, 0, 1], "thumb": "side",    "wrist_rot": 0.0},
    "K": {"fingers": [1, 1, 0, 0], "thumb": "up",      "wrist_rot": 0.0},
    "L": {"fingers": [1, 0, 0, 0], "thumb": "up",      "wrist_rot": 0.0},
    "M": {"fingers": [0, 0, 0, 0], "thumb": "under3",  "wrist_rot": 0.0},
    "N": {"fingers": [0, 0, 0, 0], "thumb": "under2",  "wrist_rot": 0.0},
    "O": {"fingers": [0.3,0.3,0.3,0.3], "thumb": "tip","wrist_rot": 0.0},
    "P": {"fingers": [1, 1, 0, 0], "thumb": "point",   "wrist_rot": -0.5},
    "Q": {"fingers": [1, 0, 0, 0], "thumb": "down",    "wrist_rot": -0.5},
    "R": {"fingers": [1, 1, 0, 0], "thumb": "side",    "wrist_rot": 0.1},
    "S": {"fingers": [0, 0, 0, 0], "thumb": "front",   "wrist_rot": 0.0},
    "T": {"fingers": [0, 0, 0, 0], "thumb": "between",  "wrist_rot": 0.0},
    "U": {"fingers": [1, 1, 0, 0], "thumb": "side",    "wrist_rot": 0.0},
    "V": {"fingers": [1, 1, 0, 0], "thumb": "side",    "wrist_rot": 0.15},
    "W": {"fingers": [1, 1, 1, 0], "thumb": "side",    "wrist_rot": 0.0},
    "X": {"fingers": [0.5,0,0,0],  "thumb": "side",    "wrist_rot": 0.0},
    "Y": {"fingers": [0, 0, 0, 1], "thumb": "up",      "wrist_rot": 0.0},
}

# Finger landmark chain lengths (relative units)
FINGER_LENGTHS = {
    "thumb":  [0.06, 0.04, 0.03],        # 3 bones
    "index":  [0.10, 0.07, 0.05, 0.04],  # 4 bones
    "middle": [0.10, 0.07, 0.05, 0.04],
    "ring":   [0.09, 0.06, 0.05, 0.04],
    "pinky":  [0.07, 0.05, 0.04, 0.03],
}

MCP_POSITIONS = np.array([
    [0.00,  0.10, 0.0],  # index MCP  (lm 5)
    [0.03,  0.10, 0.0],  # middle MCP (lm 9)
    [0.06,  0.09, 0.0],  # ring MCP   (lm 13)
    [0.09,  0.07, 0.0],  # pinky MCP  (lm 17)
])


def _finger_landmarks(mcp: np.ndarray, extension: float,
                       n_joints: int, curl_axis: str = "y") -> list[np.ndarray]:
    """Generate pip/dip/tip positions given extension [0=curled, 1=extended]."""
    pts = [mcp]
    direction = np.array([0.0, 1.0, 0.0])
    lengths = [0.07, 0.05, 0.04, 0.03][:n_joints]
    for i, l in enumerate(lengths):
        curl = (1.0 - extension) * (0.4 * (i + 1))
        dx = np.sin(curl) * 0.5
        dy = np.cos(curl)
        pts.append(pts[-1] + np.array([dx * 0.3, dy * l, 0.0]))
    return pts[1:]


def simulate_landmarks(letter: str, noise: float = 0.005) -> np.ndarray:
    """
    Simulate 21 MediaPipe hand landmarks for a given ASL letter.
    Returns array of shape (21, 3).
    """
    cfg = ASL_CONFIGS[letter]
    lm = np.zeros((21, 3))

    # Wrist (0)
    lm[0] = [0.0, 0.0, 0.0]

    # Thumb base (1)
    thumb_base = np.array([-0.05, 0.06, 0.0])
    lm[1] = thumb_base

    thumb_ext = {"side": 0.6, "across": 0.2, "curved": 0.5, "circle": 0.4,
                 "point": 0.8, "up": 0.9, "under": 0.1, "under2": 0.15,
                 "under3": 0.1, "tip": 0.3, "front": 0.2, "between": 0.25,
                 "down": 0.5}.get(cfg["thumb"], 0.5)

    for i, off in enumerate([0.05, 0.04, 0.03]):
        lm[2 + i] = lm[1 + i] + np.array([-0.02, off * thumb_ext, 0.02 * (1 - thumb_ext)])

    # Fingers (indices 5-20)
    finger_exts = cfg["fingers"]
    for f_idx, ext in enumerate(finger_exts):
        mcp = MCP_POSITIONS[f_idx].copy()
        lm[5 + f_idx * 4] = mcp
        pts = _finger_landmarks(mcp, ext, 3)
        for j, p in enumerate(pts[:3]):
            lm[6 + f_idx * 4 + j] = p

    # Apply wrist rotation
    rot = cfg.get("wrist_rot", 0.0)
    if rot != 0.0:
        c, s = np.cos(rot), np.sin(rot)
        R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        lm = (R @ lm.T).T

    # Add noise to simulate real sensor jitter
    lm += np.random.normal(0, noise, lm.shape)

    return lm


def landmarks_to_features(lm: np.ndarray) -> np.ndarray:
    """Normalise landmarks relative to wrist and scale by hand size."""
    lm = lm - lm[0]
    scale = np.linalg.norm(lm[9]) or 1.0
    lm /= scale
    return lm.flatten()


def generate_synthetic_dataset(samples_per_class: int = 400) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic training data for all ASL letters.

    NOTE: For production, replace with real MediaPipe landmark data.
    See README for instructions on using the Kaggle ASL Alphabet dataset.
    """
    X, y = [], []
    rng = np.random.RandomState(42)

    for letter in LETTERS:
        for _ in range(samples_per_class):
            noise = rng.uniform(0.003, 0.012)
            lm = simulate_landmarks(letter, noise=noise)
            features = landmarks_to_features(lm)
            X.append(features)
            y.append(letter)

    return np.array(X), np.array(y)
