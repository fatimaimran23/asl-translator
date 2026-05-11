import React, { useRef, useState, useCallback, useEffect } from "react";
import { CameraView } from "./components/CameraView";
import { PredictionPanel } from "./components/PredictionPanel";
import { SentenceBuilder } from "./components/SentenceBuilder";
import { ASLReference } from "./components/ASLReference";
import { useHandDetection } from "./hooks/useHandDetection";
import { useSignPrediction } from "./hooks/useSignPrediction";
import styles from "./App.module.css";

const HOLD_MS = 1500;

export default function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const [handDetected, setHandDetected] = useState(false);
  const [words, setWords] = useState([]);
  const [currentWord, setCurrentWord] = useState("");
  const [holdProgress, setHoldProgress] = useState(0);
  const [modelStatus, setModelStatus] = useState("checking");

  const holdRef = useRef({ letter: "", start: 0, confirmed: false });

  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then(() => setModelStatus("ready"))
      .catch(() => setModelStatus("error"));
  }, []);

  const handleLetterConfirmed = useCallback((letter) => {
    setCurrentWord((w) => w + letter);
    setHoldProgress(0);
    holdRef.current = { letter: "", start: 0, confirmed: false };
  }, []);

  const { prediction, isLoading, error, predict } = useSignPrediction({
    onLetterConfirmed: handleLetterConfirmed,
  });

  const handleLandmarks = useCallback(
    (landmarks) => {
      setHandDetected(!!landmarks);
      predict(landmarks);

      if (landmarks && prediction?.letter) {
        const letter = prediction.letter;
        if (letter !== holdRef.current.letter) {
          holdRef.current = { letter, start: Date.now(), confirmed: false };
        }
        const elapsed = Date.now() - holdRef.current.start;
        setHoldProgress(Math.min(elapsed / HOLD_MS, 1));
      } else {
        setHoldProgress(0);
      }
    },
    [predict, prediction?.letter]
  );

  useHandDetection({ videoRef, canvasRef, onLandmarks: handleLandmarks, enabled: true });

  const handleSpace = () => {
    if (currentWord) { setWords((w) => [...w, currentWord]); setCurrentWord(""); }
  };
  const handleBackspace = () => setCurrentWord((w) => w.slice(0, -1));
  const handleClear = () => { setWords([]); setCurrentWord(""); };
  const handleSpeak = () => {
    const text = [...words, currentWord].filter(Boolean).join(" ");
    if (!text) return;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(new SpeechSynthesisUtterance(text));
  };

  return (
    <div className={styles.app}>
      <header className={styles.header}>
        <div className={styles.logo}>
          <span className={styles.logoIcon}>🤟</span>
          <span className={styles.logoText}>ASL Translator</span>
        </div>
        <div className={styles.statusRow}>
          {modelStatus === "checking" && <span className={styles.pill}>Connecting…</span>}
          {modelStatus === "ready"    && <span className={`${styles.pill} ${styles.pillGreen}`}>Groq API ✓</span>}
          {modelStatus === "error"    && <span className={`${styles.pill} ${styles.pillRed}`}>Backend offline</span>}
        </div>
      </header>

      <main className={styles.main}>
        <div className={styles.left}>
          <CameraView videoRef={videoRef} canvasRef={canvasRef} handDetected={handDetected} isLoading={isLoading} />
          <ASLReference />
        </div>

        <div className={styles.right}>
          <PredictionPanel prediction={prediction} holdProgress={holdProgress} />
          <SentenceBuilder
            words={words}
            currentWord={currentWord}
            onSpace={handleSpace}
            onBackspace={handleBackspace}
            onClear={handleClear}
            onSpeak={handleSpeak}
          />
          {error && <div className={styles.error}>⚠ {error}</div>}
        </div>
      </main>
    </div>
  );
}
