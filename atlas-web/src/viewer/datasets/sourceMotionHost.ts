import type { AnimationPlaybackController, AnimationPlaybackOptions } from "../animationPlayback.ts";
import type { MotionAsset } from "../../domain/motionLearning.ts";
import type { AnimationSceneResource } from "../animationSceneAdapter.ts";

/** Same-scene playback port; implementations must reuse the active renderer and frame clock. */
export interface SourceMotionHost {
  attachSourceMotion(
    asset: MotionAsset,
    resource: AnimationSceneResource,
    onTimeChange?: AnimationPlaybackOptions['onTimeChange'],
    onInvalidated?: (reason: string) => void,
  ): Promise<AnimationPlaybackController>;
  restoreSourceMotion(reason?: string): void;
}
