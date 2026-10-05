import { AnimationMixer, LoopOnce, LoopRepeat, type AnimationAction, type AnimationClip, type Object3D } from "three";
import type { AnimationSceneResource } from "./animationSceneAdapter.ts";

export interface AnimationFrameScheduler {
  request(callback: (timestampMs: number) => void): number;
  cancel(handle: number): void;
}

const browserScheduler: AnimationFrameScheduler = {
  request: (callback) => window.requestAnimationFrame(callback),
  cancel: (handle) => window.cancelAnimationFrame(handle),
};

/** Owns one RAF chain. Repeated start/speed changes never create a second chain. */
export class SingleAnimationFrameLoop {
  private readonly onStep: (deltaSeconds: number) => boolean;
  private readonly scheduler: AnimationFrameScheduler;
  private running = false;
  private handle: number | null = null;
  private generation = 0;
  private previousTimestamp: number | null = null;
  private speed = 1;

  constructor(
    onStep: (deltaSeconds: number) => boolean,
    scheduler: AnimationFrameScheduler = browserScheduler,
  ) {
    this.onStep = onStep;
    this.scheduler = scheduler;
  }

  get isRunning(): boolean { return this.running; }

  start(speed = 1): void {
    if (!Number.isFinite(speed) || speed <= 0) return;
    this.speed = speed;
    if (this.running) return;
    this.running = true;
    this.previousTimestamp = null;
    const generation = ++this.generation;
    this.schedule(generation);
  }

  setSpeed(speed: number): void {
    if (Number.isFinite(speed) && speed > 0) this.speed = speed;
  }

  stop(): void {
    this.running = false;
    this.previousTimestamp = null;
    this.generation += 1;
    if (this.handle !== null) this.scheduler.cancel(this.handle);
    this.handle = null;
  }

  private schedule(generation: number): void {
    this.handle = this.scheduler.request((timestamp) => this.frame(timestamp, generation));
  }

  private frame(timestampMs: number, generation: number): void {
    if (!this.running || generation !== this.generation) return;
    this.handle = null;
    const deltaSeconds = this.previousTimestamp === null
      ? 0
      : Math.max(0, (timestampMs - this.previousTimestamp) / 1000) * this.speed;
    this.previousTimestamp = timestampMs;
    const continuePlaying = this.onStep(deltaSeconds);
    if (!continuePlaying) {
      this.stop();
      return;
    }
    if (this.running && generation === this.generation) this.schedule(generation);
  }
}

export interface AnimationPlaybackOptions {
  onTimeChange?: (timeSeconds: number, completed: boolean) => void;
  scheduler?: AnimationFrameScheduler;
  repeat?: boolean;
  /** Repeated educational gestures return smoothly instead of jumping at the clip boundary. */
  pingPong?: boolean;
  /** Return is a visual reset, not the opposing muscle action. */
  returnSpeed?: number;
  /** Some actions extend from a bent preparation pose back to the native rest. */
  actionDirection?: "forward" | "reverse";
  /** Use the existing anatomy renderer's frame clock instead of creating another RAF chain. */
  registerUpdate?: (update: (deltaSeconds: number) => void) => () => void;
  /** Same-scene hosts own the imported GLTF resource and restore their nodes before disposal. */
  disposeResource?: boolean;
}

/** Playback owns only animation pose/time. It has no camera or view-reset dependency. */
export class AnimationPlaybackController {
  readonly durationSeconds: number;
  private readonly mixer: AnimationMixer;
  private readonly action: AnimationAction;
  private readonly root: Object3D;
  private readonly loop: SingleAnimationFrameLoop | null;
  private readonly resource: Pick<AnimationSceneResource, "scene" | "animations" | "dispose">;
  private readonly options: AnimationPlaybackOptions;
  private currentTimeSeconds = 0;
  private disposed = false;
  private sharedPlaying = false;
  private speed = 1;
  private direction = 1;
  private returning: { start: number; elapsed: number; duration: number; onRest?: () => void } | null = null;
  private readonly unregisterUpdate: (() => void) | null;

  constructor(
    resource: Pick<AnimationSceneResource, "scene" | "animations" | "dispose">,
    clipId: string,
    options: AnimationPlaybackOptions = {},
  ) {
    this.resource = resource;
    this.options = options;
    this.root = resource.scene;
    const clip: AnimationClip | undefined = resource.animations.find((candidate) => candidate.name === clipId);
    if (!clip || !Number.isFinite(clip.duration) || clip.duration <= 0) {
      if (options.disposeResource !== false) resource.dispose();
      throw new Error("재생할 시범 clip을 찾을 수 없습니다.");
    }
    this.durationSeconds = clip.duration;
    this.mixer = new AnimationMixer(this.root);
    this.action = this.mixer.clipAction(clip);
    this.action.setLoop(options.repeat ? LoopRepeat : LoopOnce, options.repeat ? Infinity : 0);
    this.action.clampWhenFinished = !options.repeat;
    this.action.play();
    this.action.paused = true;
    this.action.time = 0;
    this.mixer.update(0);
    if (options.registerUpdate) {
      this.loop = null;
      this.unregisterUpdate = options.registerUpdate((delta) => {
        if (!this.sharedPlaying || this.disposed) return;
        if (!this.step(delta * (this.returning ? 1 : this.speed))) this.sharedPlaying = false;
      });
    } else {
      this.loop = new SingleAnimationFrameLoop((delta) => this.step(delta), options.scheduler);
      this.unregisterUpdate = null;
    }
  }

  get currentTime(): number { return this.currentTimeSeconds; }
  get isPlaying(): boolean { return this.loop?.isRunning ?? this.sharedPlaying; }
  get phase(): "action" | "preparation" | "return" | "rest" | "held" {
    if (this.returning) return "return";
    if (!this.isPlaying) return this.currentTimeSeconds <= 1e-6 ? "rest" : "held";
    if (this.options.actionDirection === "reverse") return this.direction < 0 ? "action" : "preparation";
    return this.direction > 0 ? "action" : "return";
  }

  play(speed = 1): void {
    if (this.disposed) return;
    this.returning = null;
    if (this.currentTimeSeconds >= this.durationSeconds) {
      if (this.options.repeat && this.options.pingPong && this.options.actionDirection === 'reverse') this.direction = -1;
      else this.seek(0);
    }
    this.action.paused = false;
    this.speed = Number.isFinite(speed) && speed > 0 ? speed : 1;
    if (this.loop) this.loop.start(this.speed);
    else this.sharedPlaying = true;
  }

  pause(): void {
    if (this.disposed) return;
    this.loop?.stop();
    this.sharedPlaying = false;
    this.action.paused = true;
    this.returning = null;
  }

  /** Uses the same renderer clock, reverses only the pose, and never changes the camera. */
  returnToRest(durationSeconds = 0.7, onRest?: () => void): void {
    if (this.disposed) return;
    this.pause();
    if (this.currentTimeSeconds <= 0 || !Number.isFinite(durationSeconds) || durationSeconds <= 0) {
      this.resetPose(); onRest?.(); return;
    }
    this.returning = { start: this.currentTimeSeconds, elapsed: 0, duration: durationSeconds, onRest };
    if (this.loop) this.loop.start(1);
    else this.sharedPlaying = true;
  }

  setSpeed(speed: number): void {
    if (!this.disposed && Number.isFinite(speed) && speed > 0) {
      this.speed = speed;
      this.loop?.setSpeed(speed);
    }
  }

  seek(timeSeconds: number): void {
    if (this.disposed || !Number.isFinite(timeSeconds)) return;
    this.currentTimeSeconds = Math.max(0, Math.min(this.durationSeconds, timeSeconds));
    const wasPaused = this.action.paused;
    this.action.paused = false;
    this.action.time = this.currentTimeSeconds;
    this.mixer.update(0);
    this.action.paused = wasPaused;
    this.options.onTimeChange?.(this.currentTimeSeconds, !this.options.repeat && this.currentTimeSeconds >= this.durationSeconds);
  }

  /** Resets the clip pose only. Camera framing remains untouched. */
  resetPose(): void {
    if (this.disposed) return;
    this.pause();
    this.seek(0);
    this.direction = 1;
  }

  dispose(): void {
    if (this.disposed) return;
    this.disposed = true;
    this.loop?.stop();
    this.sharedPlaying = false;
    this.unregisterUpdate?.();
    this.mixer.stopAllAction();
    this.mixer.uncacheAction(this.action.getClip(), this.root);
    this.mixer.uncacheRoot(this.root);
    if (this.options.disposeResource !== false) this.resource.dispose();
  }

  private step(deltaSeconds: number): boolean {
    if (this.disposed) return false;
    if (this.returning) {
      const returning = this.returning;
      returning.elapsed += Math.max(0, deltaSeconds);
      const t = Math.min(1, returning.elapsed / returning.duration);
      this.seek(returning.start * (1 - t * t * (3 - 2 * t)));
      if (t < 1) return true;
      this.returning = null;
      this.direction = 1;
      returning.onRest?.();
      return false;
    }
    if (this.options.repeat && this.options.pingPong) {
      const returnSpeed = Number.isFinite(this.options.returnSpeed) && this.options.returnSpeed! > 0 ? this.options.returnSpeed! : 1;
      const period = this.durationSeconds + this.durationSeconds / returnSpeed;
      const phase = (this.direction > 0 ? this.currentTimeSeconds
        : this.durationSeconds + (this.durationSeconds - this.currentTimeSeconds) / returnSpeed) + Math.max(0, deltaSeconds);
      const wrapped = phase % period;
      this.direction = wrapped < this.durationSeconds ? 1 : -1;
      this.seek(wrapped <= this.durationSeconds ? wrapped : this.durationSeconds - (wrapped - this.durationSeconds) * returnSpeed);
      return true;
    }
    if (deltaSeconds > 0) this.mixer.update(deltaSeconds);
    this.currentTimeSeconds = this.options.repeat
      ? (this.currentTimeSeconds + deltaSeconds) % this.durationSeconds
      : Math.min(this.durationSeconds, this.currentTimeSeconds + deltaSeconds);
    if (this.options.repeat) {
      this.options.onTimeChange?.(this.currentTimeSeconds, false);
      return true;
    }
    const completed = this.currentTimeSeconds >= this.durationSeconds;
    if (completed) {
      this.action.paused = false;
      this.action.time = this.durationSeconds;
      this.mixer.update(0);
      this.action.paused = true;
    }
    this.options.onTimeChange?.(this.currentTimeSeconds, completed);
    return !completed;
  }
}
