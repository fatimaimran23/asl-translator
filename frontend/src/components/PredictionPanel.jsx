import React from "react";
import styles from "./PredictionPanel.module.css";

function ConfidenceBar({ value }) {
  const pct = Math.round(value * 100);
  const color = pct >= 70 ? "var(--success)" : pct >= 45 ? "var(--warning)" : "var(--danger)";
  return (
    <div className={styles.barWrap}>
      <div className={styles.barFill} style={{ width: `${pct}%`, background: color }} />
      <span className={styles.barLabel}>{pct}%</span>
    </div>
  );
}

export function PredictionPanel({ prediction, holdProgress }) {
  const letter = prediction?.letter || "—";
  const confidence = prediction?.confidence ?? 0;
  const top3 = prediction?.top3 ?? [];

  return (
    <div className={styles.panel}>
      <div className={styles.letterWrap}>
        <div className={styles.letter}>{letter}</div>
        <div className={styles.holdRing}>
          <svg viewBox="0 0 44 44" width="44" height="44">
            <circle cx="22" cy="22" r="19" fill="none" stroke="var(--border)" strokeWidth="3" />
            <circle
              cx="22" cy="22" r="19"
              fill="none"
              stroke="var(--accent)"
              strokeWidth="3"
              strokeDasharray={`${2 * Math.PI * 19}`}
              strokeDashoffset={`${2 * Math.PI * 19 * (1 - holdProgress)}`}
              strokeLinecap="round"
              style={{ transform: "rotate(-90deg)", transformOrigin: "center", transition: "stroke-dashoffset 0.1s" }}
            />
          </svg>
        </div>
      </div>

      {prediction && (
        <>
          <div className={styles.confRow}>
            <span className={styles.confLabel}>Confidence</span>
            <ConfidenceBar value={confidence} />
          </div>

          {top3.length > 0 && (
            <div className={styles.top3}>
              <div className={styles.top3Label}>Top predictions</div>
              {top3.map((item) => (
                <div key={item.letter} className={styles.top3Row}>
                  <span className={styles.top3Letter}>{item.letter}</span>
                  <div className={styles.barWrap} style={{ flex: 1 }}>
                    <div
                      className={styles.barFill}
                      style={{ width: `${Math.round(item.probability * 100)}%`, background: "var(--accent)" }}
                    />
                  </div>
                  <span className={styles.top3Pct}>{Math.round(item.probability * 100)}%</span>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {!prediction && (
        <p className={styles.hint}>Show your hand and make an ASL sign</p>
      )}
    </div>
  );
}
