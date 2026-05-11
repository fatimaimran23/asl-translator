"""
collect_real_data.py — Record real ASL landmark data from your webcam.

Usage:
    python collect_real_data.py --letter A --samples 100

This saves landmark vectors to data/landmarks_A.npy for training.
Once all letters are collected, run:
    python train_real.py
"""

import argparse
import time
import cv2
import numpy as np
import mediapipe as mp
import os

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

LETTERS = list("ABCDEFGHIKLMNOPQRSTUVWXY")
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


def extract_features(landmarks) -> np.ndarray:
    lm = np.array([[p.x, p.y, p.z] for p in landmarks])
    lm -= lm[0]
    scale = np.linalg.norm(lm[9]) or 1.0
    lm /= scale
    return lm.flatten()


def collect(letter: str, n_samples: int):
    if letter not in LETTERS:
        print(f"Letter '{letter}' not supported (J and Z require motion).")
        return

    cap = cv2.VideoCapture(0)
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1,
                            min_detection_confidence=0.7)

    samples = []
    collecting = False
    print(f"\nReady to collect '{letter}'. Press SPACE to start, Q to quit.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        status = f"Samples: {len(samples)}/{n_samples}"
        color = (0, 200, 0) if collecting else (200, 200, 200)
        cv2.putText(frame, f"Letter: {letter}  {status}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.putText(frame, "SPACE=start  Q=quit", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)

        if results.multi_hand_landmarks:
            lm = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
            if collecting:
                feat = extract_features(lm.landmark)
                samples.append(feat)
                cv2.putText(frame, "RECORDING", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        cv2.imshow("ASL Data Collector", frame)

        if len(samples) >= n_samples:
            print(f"Collected {n_samples} samples for '{letter}'.")
            break

        key = cv2.waitKey(1) & 0xFF
        if key == ord(" "):
            collecting = True
            print("Recording started…")
        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    if samples:
        out_path = os.path.join(DATA_DIR, f"landmarks_{letter}.npy")
        np.save(out_path, np.array(samples))
        print(f"Saved {len(samples)} samples to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect ASL landmark data")
    parser.add_argument("--letter", required=True, help="ASL letter to collect (A-Y, no J/Z)")
    parser.add_argument("--samples", type=int, default=100, help="Number of samples to collect")
    args = parser.parse_args()
    collect(args.letter.upper(), args.samples)
