import type { AnimationPlaybackController, AnimationPlaybackOptions } from "../animationPlayback.ts";
import type { MotionAsset } from "../../domain/motionLearning.ts";
import type { AnimationSceneResource } from "../animationSceneAdapter.ts";
import type { MotionLearningIntent } from "../../domain/atlasMotionExperience.ts";

/** Same-scene playback port; implementations must reuse the active renderer and frame clock. */
export interface SourceMotionHost {
  attachSourceMotion(
    asset: MotionAsset,
    resource: AnimationSceneResource,
    onTimeChange?: AnimationPlaybackOptions['onTimeChange'],
    onInvalidated?: (reason: string) => void,
    presentation?: { intent: MotionLearningIntent },
  ): Promise<AnimationPlaybackController>;
  restoreSourceMotion(reason?: string): void;
}
