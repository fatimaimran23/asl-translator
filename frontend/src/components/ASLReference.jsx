import React, { useState } from "react";
import styles from "./ASLReference.module.css";

// Unicode regional indicator letters render as hand sign emojis in some contexts.
// We use a simple text-based reference with descriptions instead.
const SIGNS = [
  { letter: "A", desc: "Fist, thumb to side" },
  { letter: "B", desc: "Fingers straight up, thumb across palm" },
  { letter: "C", desc: "Curved hand, C-shape" },
  { letter: "D", desc: "Index up, others curl to touch thumb" },
  { letter: "E", desc: "Fingers curled, thumb tucked under" },
  { letter: "F", desc: "Index + thumb circle, others extended" },
  { letter: "G", desc: "Index + thumb point sideways" },
  { letter: "H", desc: "Index + middle extended sideways" },
  { letter: "I", desc: "Pinky up, fist" },
  { letter: "K", desc: "Index up, middle angled, thumb between" },
  { letter: "L", desc: "L-shape: index up, thumb out" },
  { letter: "M", desc: "Three fingers folded over thumb" },
  { letter: "N", desc: "Two fingers folded over thumb" },
  { letter: "O", desc: "All fingers curve to touch thumb tip" },
  { letter: "P", desc: "K-shape pointing downward" },
  { letter: "Q", desc: "G-shape pointing downward" },
  { letter: "R", desc: "Index + middle crossed" },
  { letter: "S", desc: "Fist, thumb over fingers" },
  { letter: "T", desc: "Thumb between index and middle" },
  { letter: "U", desc: "Index + middle extended together" },
  { letter: "V", desc: "Index + middle in V (peace sign)" },
  { letter: "W", desc: "Index + middle + ring extended, spread" },
  { letter: "X", desc: "Index hooked/bent" },
  { letter: "Y", desc: "Thumb + pinky extended (hang loose)" },
];

export function ASLReference() {
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(null);

  return (
    <div className={styles.wrap}>
      <button onClick={() => setOpen((v) => !v)} className={styles.toggle}>
        {open ? "▲" : "▼"} ASL Fingerspelling Reference
      </button>

      {open && (
        <div className={styles.grid}>
          {SIGNS.map(({ letter, desc }) => (
            <div
              key={letter}
              className={`${styles.card} ${active === letter ? styles.cardActive : ""}`}
              onClick={() => setActive(active === letter ? null : letter)}
            >
              <div className={styles.cardLetter}>{letter}</div>
              {active === letter && (
                <div className={styles.cardDesc}>{desc}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
