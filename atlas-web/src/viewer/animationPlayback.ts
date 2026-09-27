import { AnimationMixer, LoopOnce, type AnimationAction, type AnimationClip, type Object3D } from "three";
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
}

/** Playback owns only animation pose/time. It has no camera or view-reset dependency. */
export class AnimationPlaybackController {
  readonly durationSeconds: number;
  private readonly mixer: AnimationMixer;
  private readonly action: AnimationAction;
  private readonly root: Object3D;
  private readonly loop: SingleAnimationFrameLoop;
  private readonly resource: Pick<AnimationSceneResource, "scene" | "animations" | "dispose">;
  private readonly options: AnimationPlaybackOptions;
  private currentTimeSeconds = 0;
  private disposed = false;

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
      resource.dispose();
      throw new Error("재생할 시범 clip을 찾을 수 없습니다.");
    }
    this.durationSeconds = clip.duration;
    this.mixer = new AnimationMixer(this.root);
    this.action = this.mixer.clipAction(clip);
    this.action.setLoop(LoopOnce, 0);
    this.action.clampWhenFinished = true;
    this.action.play();
    this.action.paused = true;
    this.action.time = 0;
    this.mixer.update(0);
    this.loop = new SingleAnimationFrameLoop((delta) => this.step(delta), options.scheduler);
  }

  get currentTime(): number { return this.currentTimeSeconds; }
  get isPlaying(): boolean { return this.loop.isRunning; }

  play(speed = 1): void {
    if (this.disposed) return;
    if (this.currentTimeSeconds >= this.durationSeconds) this.seek(0);
    this.action.paused = false;
    this.loop.start(speed);
  }

  pause(): void {
    if (this.disposed) return;
    this.loop.stop();
    this.action.paused = true;
  }

  setSpeed(speed: number): void {
    if (!this.disposed) this.loop.setSpeed(speed);
  }

  seek(timeSeconds: number): void {
    if (this.disposed || !Number.isFinite(timeSeconds)) return;
    this.currentTimeSeconds = Math.max(0, Math.min(this.durationSeconds, timeSeconds));
    const wasPaused = this.action.paused;
    this.action.paused = false;
    this.action.time = this.currentTimeSeconds;
    this.mixer.update(0);
    this.action.paused = wasPaused;
    this.options.onTimeChange?.(this.currentTimeSeconds, this.currentTimeSeconds >= this.durationSeconds);
  }

  /** Resets the clip pose only. Camera framing remains untouched. */
  resetPose(): void {
    if (this.disposed) return;
    this.pause();
    this.seek(0);
  }

  dispose(): void {
    if (this.disposed) return;
    this.disposed = true;
    this.loop.stop();
    this.mixer.stopAllAction();
    this.mixer.uncacheAction(this.action.getClip(), this.root);
    this.mixer.uncacheRoot(this.root);
    this.resource.dispose();
  }

  private step(deltaSeconds: number): boolean {
    if (this.disposed) return false;
    if (deltaSeconds > 0) this.mixer.update(deltaSeconds);
    this.currentTimeSeconds = Math.min(this.durationSeconds, this.currentTimeSeconds + deltaSeconds);
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
