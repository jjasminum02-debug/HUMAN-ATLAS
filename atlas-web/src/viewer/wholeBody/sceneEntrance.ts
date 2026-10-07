// Presentation only: orbit the existing camera, never rotate anatomy or its frame.
export const ENTRANCE_SECONDS = 1.4;
export const ENTRANCE_YAW = 12 * Math.PI / 180;

export function entranceFrame(elapsedSeconds: number) {
  const t = Math.max(0, Math.min(1, elapsedSeconds / ENTRANCE_SECONDS));
  const eased = t * t * t * (t * (t * 6 - 15) + 10);
  return { yaw: ENTRANCE_YAW * eased, opacity: 0.2 + 0.8 * eased, finished: t === 1 };
}
