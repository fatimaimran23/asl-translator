import { useRef, useState, useCallback } from "react";

const API_BASE = "/api";
const COOLDOWN_MS = 2500; // Claude API needs more time than local model
const HOLD_MS = 1500;

export function useSignPrediction({ onLetterConfirmed }) {
  const [prediction, setPrediction] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const lastCallRef = useRef(0);
  const lastLetterRef = useRef("");
  const holdStartRef = useRef(0);
  const confirmedRef = useRef(false);

  const predict = useCallback(async (landmarks) => {
    if (!landmarks) {
      setPrediction(null);
      lastLetterRef.current = "";
      return;
    }

    const now = Date.now();
    if (now - lastCallRef.current < COOLDOWN_MS || isLoading) return;
    lastCallRef.current = now;

    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/predict/landmarks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ landmarks }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Prediction failed");
      }

      const data = await res.json();
      setPrediction(data);

      const letter = data.letter;
      const confidence = data.confidence;

      if (letter && letter !== "?" && confidence > 0.4) {
        if (letter !== lastLetterRef.current) {
          lastLetterRef.current = letter;
          holdStartRef.current = Date.now();
          confirmedRef.current = false;
        } else if (!confirmedRef.current && Date.now() - holdStartRef.current >= HOLD_MS) {
          confirmedRef.current = true;
          onLetterConfirmed(letter);
        }
      } else {
        lastLetterRef.current = "";
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, onLetterConfirmed]);

  return { prediction, isLoading, error, predict };
}
