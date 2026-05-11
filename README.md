# ASL Translator

A full-stack web app that translates American Sign Language fingerspelling in real time using your webcam. Show a hand sign, hold it steady, and the app spells out the letter — building words and sentences you can have read aloud.

## Stack

- Frontend: React 18 + Vite
- Backend: FastAPI (Python)
- ML: Random Forest trained on 87k real ASL images
- Hand tracking: MediaPipe Hands (runs in browser via WASM)

## Running locally

**Backend**
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Training on real data

```bash
cd backend
pip install kaggle tqdm
# Add kaggle.json to C:\Users\YOU\.kaggle\kaggle.json
python setup_real_model.py
```

Downloads the Kaggle ASL Alphabet dataset, extracts landmarks, and trains the model (~10 mins). Expected accuracy: 93-95%.

## Supported letters

A B C D E F G H I K L M N O P Q R S T U V W X Y

J and Z are excluded as they require motion.

