// Weak GPUs are limited by pixels drawn, so moving frames may render at a lower resolution; the still view is always sharp.
// Only unbroken runs of drawn frames are judged, so sparse redraws (hover, a click) can never look like a slow machine.
const WINDOW = 8, SLOW_MS = 40, FAST_MS = 18, RAISE_AFTER = 96, STEP = .75, TAB_SWITCH_MS = 2000;

export class AdaptiveResolution {
  private ratio: number; private intervals: number[] = []; private fastFrames = 0; private raised = false; private locked = false;
  readonly full: number; readonly floor: number;
  constructor(full: number, floor = .5) { this.full = full; this.floor = Math.min(full, floor); this.ratio = full; }
  get degraded() { return this.ratio < this.full; }
  /** The pixel ratio for this moving frame. `intervalMs` is the time since the previous animation frame. */
  moving(intervalMs: number, drewPreviousFrame: boolean) {
    if (!drewPreviousFrame || intervalMs <= 0 || intervalMs > TAB_SWITCH_MS) { this.intervals = []; this.fastFrames = 0; return this.ratio; }
    this.intervals.push(intervalMs);
    if (this.intervals.length < WINDOW) return this.ratio;
    const average = this.intervals.reduce((sum, value) => sum + value, 0) / WINDOW; this.intervals = [];
    if (average > SLOW_MS && this.ratio > this.floor) {
      this.ratio = Math.max(this.floor, this.ratio * STEP); this.fastFrames = 0;
      if (this.raised) this.locked = true; // It was tried one step higher and could not hold: stop probing.
    } else if (average < FAST_MS && this.degraded && !this.locked) {
      this.fastFrames += WINDOW;
      if (this.fastFrames >= RAISE_AFTER) { this.ratio = Math.min(this.full, this.ratio / STEP); this.fastFrames = 0; this.raised = true; }
    } else this.fastFrames = 0;
    return this.ratio;
  }
}
