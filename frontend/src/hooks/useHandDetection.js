import { useEffect, useRef, useCallback } from "react";

const MEDIAPIPE_CDN = "https://cdn.jsdelivr.net/npm/@mediapipe/hands/";

/**
 * useHandDetection
 *
 * Initialises MediaPipe Hands on the provided video element,
 * draws landmarks on the canvas overlay, and calls `onLandmarks`
 * with the raw 21-point array whenever a hand is detected.
 */
export function useHandDetection({ videoRef, canvasRef, onLandmarks, enabled = true }) {
  const handsRef = useRef(null);
  const cameraRef = useRef(null);
  const animRef = useRef(null);

  const draw = useCallback((results, canvas) => {
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!results.multiHandLandmarks?.length) return;

    const lm = results.multiHandLandmarks[0];

    // Draw connections
    const CONNECTIONS = window.HAND_CONNECTIONS || [];
    ctx.strokeStyle = "#7c6af7";
    ctx.lineWidth = 2;
    for (const [a, b] of CONNECTIONS) {
      ctx.beginPath();
      ctx.moveTo(lm[a].x * canvas.width, lm[a].y * canvas.height);
      ctx.lineTo(lm[b].x * canvas.width, lm[b].y * canvas.height);
      ctx.stroke();
    }

    // Draw joints
    for (const point of lm) {
      ctx.beginPath();
      ctx.arc(point.x * canvas.width, point.y * canvas.height, 4, 0, Math.PI * 2);
      ctx.fillStyle = "#22c55e";
      ctx.fill();
    }
  }, []);

  useEffect(() => {
    if (!enabled || !videoRef.current || !canvasRef.current) return;

    let active = true;

    async function init() {
      // Dynamically load MediaPipe scripts
      await loadScript(`${MEDIAPIPE_CDN}hands.js`);
      await loadScript("https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js");

      if (!active) return;

      const Hands = window.Hands;
      const Camera = window.Camera;

      const hands = new Hands({
        locateFile: (f) => `${MEDIAPIPE_CDN}${f}`,
      });

      hands.setOptions({
        maxNumHands: 1,
        modelComplexity: 1,
        minDetectionConfidence: 0.75,
        minTrackingConfidence: 0.65,
      });

      hands.onResults((results) => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        canvas.width = videoRef.current?.videoWidth || 640;
        canvas.height = videoRef.current?.videoHeight || 480;
        draw(results, canvas);

        if (results.multiHandLandmarks?.length) {
          const raw = results.multiHandLandmarks[0];
          const landmarks = raw.map((p) => [p.x, p.y, p.z]);
          onLandmarks(landmarks);
        } else {
          onLandmarks(null);
        }
      });

      const camera = new Camera(videoRef.current, {
        onFrame: async () => {
          if (videoRef.current && active) {
            await hands.send({ image: videoRef.current });
          }
        },
        width: 640,
        height: 480,
      });

      await camera.start();
      handsRef.current = hands;
      cameraRef.current = camera;
    }

    init().catch(console.error);

    return () => {
      active = false;
      cameraRef.current?.stop?.();
    };
  }, [enabled, draw, onLandmarks, videoRef, canvasRef]);
}

function loadScript(src) {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve();
      return;
    }
    const s = document.createElement("script");
    s.src = src;
    s.onload = resolve;
    s.onerror = reject;
    document.head.appendChild(s);
  });
}
