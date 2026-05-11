import os
import base64
import logging
import json
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ASL Translator API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY environment variable not set!")

client = Groq(api_key=GROQ_API_KEY)


class LandmarkRequest(BaseModel):
    landmarks: list[list[float]]

class PredictionResponse(BaseModel):
    letter: str
    confidence: float
    top3: list[dict]
    hand_detected: bool
    hint: str = ""


def landmarks_to_description(landmarks: list[list[float]]) -> str:
    lm = np.array(landmarks)
    lm -= lm[0]
    scale = np.linalg.norm(lm[9]) or 1.0
    lm /= scale

    def dist(a, b):
        return float(np.linalg.norm(lm[a] - lm[b]))

    def extended(tip, pip):
        return lm[tip][1] < lm[pip][1]

    fingers = {
        "thumb":  "extended" if dist(4, 2) > 0.3 else "curled",
        "index":  "extended" if extended(8, 6)    else "curled",
        "middle": "extended" if extended(12, 10)  else "curled",
        "ring":   "extended" if extended(16, 14)  else "curled",
        "pinky":  "extended" if extended(20, 18)  else "curled",
    }

    return f"""Hand landmark analysis:
Finger states: {fingers}
Thumb-to-index distance: {dist(4,8):.3f} (small = touching)
Thumb-to-middle distance: {dist(4,12):.3f}
Wrist to index tip: {dist(0,8):.3f}
Index tip pos: x={lm[8][0]:.3f}, y={lm[8][1]:.3f}
Pinky tip pos: x={lm[20][0]:.3f}, y={lm[20][1]:.3f}
Thumb tip pos: x={lm[4][0]:.3f}, y={lm[4][1]:.3f}"""


PROMPT_TEMPLATE = """You are an expert ASL (American Sign Language) fingerspelling recogniser.

{description}

Based on these hand measurements, identify which ASL fingerspelling letter (A-Y, excluding J and Z) is being signed.

Key ASL handshapes:
- A: fist, thumb to side, all fingers curled
- B: all 4 fingers straight up, thumb folded across palm
- C: all fingers curved in C-shape
- D: index extended up, others curl to touch thumb tip
- E: all fingers bent/hooked, thumb tucked under
- F: index+thumb form circle, other 3 fingers extended
- G: index and thumb point sideways horizontally
- H: index+middle extended horizontally sideways
- I: only pinky extended up, fist
- K: index up, middle angled out, thumb between them
- L: index up + thumb out at 90 degrees (L-shape)
- M: 3 fingers over thumb
- N: 2 fingers over thumb
- O: all fingers curved to touch thumb tip
- R: index+middle crossed
- S: fist with thumb over fingers
- T: thumb between index and middle fingers
- U: index+middle together pointing up
- V: index+middle spread in V/peace sign
- W: index+middle+ring all extended and spread
- X: index finger hooked/bent
- Y: thumb+pinky extended, others curled

Respond ONLY with valid JSON, no markdown, no extra text:
{{"letter": "A", "confidence": 0.85, "hint": "fist with thumb to side", "top3": [{{"letter": "A", "probability": 0.85}}, {{"letter": "S", "probability": 0.10}}, {{"letter": "E", "probability": 0.05}}]}}"""


@app.get("/health")
def health():
    return {"status": "ok", "model": "groq/llama-3.3-70b", "model_loaded": True}


@app.post("/predict/landmarks", response_model=PredictionResponse)
def predict_from_landmarks(req: LandmarkRequest):
    if len(req.landmarks) != 21:
        raise HTTPException(400, "Expected 21 landmarks.")

    description = landmarks_to_description(req.landmarks)
    prompt = PROMPT_TEMPLATE.format(description=description)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.1,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)
        return PredictionResponse(
            letter=data.get("letter", "?"),
            confidence=float(data.get("confidence", 0.5)),
            top3=data.get("top3", []),
            hand_detected=True,
            hint=data.get("hint", ""),
        )
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        raise HTTPException(500, f"Prediction failed: {e}")


@app.post("/train")
def train_model():
    return {"message": "Using Groq API — no training needed!", "accuracy": 1.0}
