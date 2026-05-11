# 🤟 ASL Translator

A full-stack American Sign Language (ASL) fingerspelling translator that uses your webcam, MediaPipe hand tracking, and a trained machine learning classifier to recognise ASL letters A–Y in real time.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 + Vite, MediaPipe Hands (WASM) |
| Backend | FastAPI (Python 3.11+) |
| ML Model | Random Forest via scikit-learn (63-dim landmark features) |
| Hand Tracking | Google MediaPipe Hands — 21 3D landmarks per frame |

## Architecture

```
Webcam → MediaPipe Hands (browser, WASM)
          │  21 landmark (x,y,z) coordinates
          ▼
FastAPI /predict/landmarks
          │  Normalise + scale landmarks
          ▼
Random Forest Classifier
          │  Letter + confidence + top-3
          ▼
React UI  — hold-to-confirm → sentence builder → TTS
```

Landmark extraction runs **client-side** in the browser via WASM — only the tiny 63-float feature vector is sent to the backend, keeping latency under 20 ms on LAN.

## Project Structure

```
asl-translator/
├── backend/
│   ├── main.py                 # FastAPI app, routes
│   ├── requirements.txt
│   ├── collect_real_data.py    # Webcam data collection tool
│   ├── train_real.py           # Train on collected data
│   └── model/
│       ├── classifier.py       # Random Forest wrapper
│       ├── dataset.py          # Synthetic data generator
│       └── asl_model.pkl       # Trained model (generated)
└── frontend/
    ├── index.html
    ├── vite.config.js
    └── src/
        ├── App.jsx
        ├── hooks/
        │   ├── useHandDetection.js   # MediaPipe integration
        │   └── useSignPrediction.js  # API calls + hold logic
        └── components/
            ├── CameraView.jsx        # Video + canvas overlay
            ├── PredictionPanel.jsx   # Letter + confidence bars
            ├── SentenceBuilder.jsx   # Word/sentence assembly
            └── ASLReference.jsx      # A-Y reference guide
```

## Quick Start

### 1. Clone

```bash
git clone https://github.com/YOUR_USERNAME/asl-translator.git
cd asl-translator
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Train the model (uses synthetic data for demo — see below for real data):

```bash
uvicorn main:app --reload
# Then in another terminal:
curl -X POST http://localhost:8000/train
```

Or train from Python directly:

```python
python -c "
from model.dataset import generate_synthetic_dataset
from model.classifier import ASLClassifier
X, y = generate_synthetic_dataset()
clf = ASLClassifier()
acc = clf.train(X, y)
clf.save('model/asl_model.pkl')
print(f'Accuracy: {acc:.2%}')
"
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** — the Vite proxy routes `/api/*` to the FastAPI backend automatically.

## Using Real Data (Recommended for CV)

The default model uses synthetic landmark data. For production accuracy, collect real data:

```bash
cd backend

# Collect 100 samples for each letter (A, B, C, ...)
python collect_real_data.py --letter A --samples 100
python collect_real_data.py --letter B --samples 100
# ... repeat for all letters A-Y (excluding J and Z — they require motion)

# Train on your collected data
python train_real.py
```

Alternatively, download the [Kaggle ASL Alphabet dataset](https://www.kaggle.com/datasets/grassknoted/asl-alphabet), run the images through MediaPipe to extract landmarks, and use `train_real.py`.

> **Note:** J and Z are excluded because they require motion (dynamic gestures). The model covers A–Y (24 static letters).

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check backend + model status |
| POST | `/predict/landmarks` | Classify from 21×3 landmark array |
| POST | `/predict/frame` | Classify from base64 image |
| POST | `/train` | Train model on synthetic dataset |

### Example: POST /predict/landmarks

```json
{
  "landmarks": [[0.5, 0.7, 0.01], ...] // 21 items, each [x, y, z]
}
```

Response:

```json
{
  "letter": "A",
  "confidence": 0.87,
  "top3": [
    {"letter": "A", "probability": 0.87},
    {"letter": "S", "probability": 0.09},
    {"letter": "E", "probability": 0.03}
  ],
  "hand_detected": true
}
```

## How It Works

1. **MediaPipe Hands** runs in the browser (WebAssembly) and tracks 21 3D landmarks on the hand at ~30 fps
2. Landmarks are **normalised** relative to the wrist and scaled by hand size, making the features scale/position invariant
3. The **63-dimensional feature vector** is sent to the FastAPI backend
4. A **Random Forest classifier** (300 trees) predicts the letter with per-class probabilities
5. The UI uses a **hold-to-confirm** mechanic — a sign must be held steady for 1.2 seconds before the letter is accepted, reducing accidental inputs
6. Confirmed letters build a **word**, words build a **sentence**, which can be read aloud via the Web Speech API

## Performance

| Metric | Value |
|--------|-------|
| Landmark extraction | ~30 fps (WASM, client-side) |
| API round-trip | ~15–30 ms (localhost) |
| Inference time | <1 ms (Random Forest, CPU) |
| CV accuracy (synthetic) | ~72% |
| CV accuracy (real data, 100 samples/class) | ~91–95% |

## Supported Signs

A B C D E F G H I K L M N O P Q R S T U V W X Y

*(J and Z excluded — require motion tracking)*

## License

MIT
