import React from "react";
import styles from "./SentenceBuilder.module.css";

export function SentenceBuilder({ words, currentWord, onSpace, onBackspace, onClear, onSpeak }) {
  const full = [...words, currentWord].filter(Boolean).join(" ");

  return (
    <div className={styles.wrap}>
      <div className={styles.header}>
        <span className={styles.label}>Sentence</span>
        <div className={styles.actions}>
          <button onClick={onSpeak} disabled={!full} title="Speak aloud">
            🔊 Speak
          </button>
          <button onClick={onClear} disabled={!full} className="danger" title="Clear all">
            Clear
          </button>
        </div>
      </div>

      <div className={styles.display}>
        {full ? (
          <span className={styles.text}>{full}</span>
        ) : (
          <span className={styles.placeholder}>Start signing to build a sentence…</span>
        )}
        <span className={styles.cursor} />
      </div>

      <div className={styles.chips}>
        {words.map((w, i) => (
          <span key={i} className={styles.chip}>{w}</span>
        ))}
        {currentWord && (
          <span className={`${styles.chip} ${styles.active}`}>{currentWord}</span>
        )}
      </div>

      <div className={styles.footer}>
        <button onClick={onSpace} disabled={!currentWord} title="Finish current word">
          ␣ Space
        </button>
        <button onClick={onBackspace} disabled={!currentWord} title="Delete last letter">
          ⌫ Backspace
        </button>
      </div>
    </div>
  );
}
