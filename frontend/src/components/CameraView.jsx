import React from "react";
import styles from "./CameraView.module.css";

export function CameraView({ videoRef, canvasRef, handDetected, isLoading }) {
  return (
    <div className={styles.wrap}>
      <video
        ref={videoRef}
        className={styles.video}
        autoPlay
        playsInline
        muted
      />
      <canvas ref={canvasRef} className={styles.canvas} />

      <div className={`${styles.badge} ${handDetected ? styles.detected : styles.noHand}`}>
        <span className={styles.dot} />
        {handDetected ? "Hand detected" : "No hand"}
      </div>

      {isLoading && (
        <div className={styles.analysing}>Analysing…</div>
      )}
    </div>
  );
}
