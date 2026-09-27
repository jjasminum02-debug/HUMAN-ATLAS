import { useEffect, useRef, useState } from "react";
import {
  acceptMotionAssetLoad,
  beginMotionAssetLoad,
  failMotionAssetLoad,
  pauseMotion,
  playMotion,
  resetMotionPose,
  seekMotionProgress,
  setMotionSpeed,
  setMotionTime,
  setReducedMotionPreference,
  suspendMotionForHiddenPage,
  type MotionPlayerState,
} from "../domain/motionPlayer";
import type { LearnerMotionActionOption } from "../domain/motionLearning";
import { loadAnimationScene } from "../viewer/animationSceneAdapter";
import { AnimationPlaybackController } from "../viewer/animationPlayback";

interface Props {
  actions: readonly LearnerMotionActionOption[];
  selectedActionId: string | null;
  onSelectAction(actionId: string): void;
}

function prefersReducedMotion(): boolean {
  return typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function MotionLearningPanel({ actions, selectedActionId, onSelectAction }: Props) {
  const selectedAction = actions.find((action) => action.id === selectedActionId) ?? null;
  const candidate = selectedAction?.candidate ?? null;
  const [state, setState] = useState<MotionPlayerState>(() => ({
    session: { status: "idle", definitionId: null, assetId: null, currentTimeSeconds: 0, playbackSpeed: 1, selectedStructureIds: [], errorMessage: null },
    selectedActionId,
    durationSeconds: null,
    generation: 0,
    prefersReducedMotion: prefersReducedMotion(),
    boundStructureIds: [],
  }));
  const stateRef = useRef(state);
  const abortRef = useRef<AbortController | null>(null);
  const playbackRef = useRef<AnimationPlaybackController | null>(null);

  function publish(next: MotionPlayerState) {
    stateRef.current = next;
    setState(next);
  }

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const sync = () => {
      const current = stateRef.current;
      const next = setReducedMotionPreference(current, media.matches);
      if (next === current) return;
      if (media.matches) {
        abortRef.current?.abort();
        playbackRef.current?.resetPose();
      }
      publish(next);
    };
    media.addEventListener("change", sync);
    sync();
    return () => media.removeEventListener("change", sync);
  }, []);

  useEffect(() => {
    const onVisibility = () => {
      if (document.visibilityState !== "hidden") return;
      abortRef.current?.abort();
      abortRef.current = null;
      playbackRef.current?.pause();
      publish(suspendMotionForHiddenPage(stateRef.current));
    };
    document.addEventListener("visibilitychange", onVisibility);
    return () => document.removeEventListener("visibilitychange", onVisibility);
  }, []);

  useEffect(() => () => {
    abortRef.current?.abort();
    abortRef.current = null;
    playbackRef.current?.dispose();
    playbackRef.current = null;
  }, []);

  async function loadCandidate(startAfterLoad: boolean) {
    const option = actions.find((action) => action.id === stateRef.current.selectedActionId);
    const playable = option?.candidate ?? null;
    if (!option || !playable) return;
    const begun = beginMotionAssetLoad(stateRef.current);
    if (begun.requestToken === null) return;
    abortRef.current?.abort();
    playbackRef.current?.dispose();
    playbackRef.current = null;
    publish(begun.state);

    const abort = new AbortController();
    abortRef.current = abort;
    try {
      const uri = new URL(playable.asset.uri, window.location.href);
      const response = await fetch(uri, { signal: abort.signal });
      if (!response.ok) throw new Error("asset request failed");
      const bytes = await response.arrayBuffer();
      const resource = await loadAnimationScene(bytes, playable.asset, {
        basePath: new URL(".", uri).href,
        signal: abort.signal,
      });
      const current = stateRef.current;
      if (abort.signal.aborted || current.generation !== begun.requestToken || current.session.status !== "loading") {
        resource.dispose();
        return;
      }

      const controller = new AnimationPlaybackController(resource, playable.asset.clip.id, {
        onTimeChange: (time, completed) => {
          const latest = stateRef.current;
          publish(setMotionTime(latest, completed ? playable.asset.clip.durationSeconds : time));
        },
      });
      playbackRef.current = controller;
      const ready = acceptMotionAssetLoad(current, begun.requestToken, {
        actionId: option.id,
        definitionId: playable.definition.id,
        assetId: playable.asset.id,
        durationSeconds: controller.durationSeconds,
        structureIds: option.subjectIds,
      });
      publish(ready);
      if (startAfterLoad && !ready.prefersReducedMotion) {
        const playing = playMotion(ready);
        if (playing !== ready) {
          controller.play(playing.session.playbackSpeed);
          publish(playing);
        }
      }
    } catch {
      if (abort.signal.aborted) return;
      playbackRef.current?.dispose();
      playbackRef.current = null;
      publish(failMotionAssetLoad(stateRef.current, begun.requestToken));
    }
  }

  function play() {
    if (!candidate || stateRef.current.prefersReducedMotion) return;
    const current = stateRef.current;
    if (current.session.assetId && playbackRef.current) {
      const next = playMotion(current);
      if (next !== current) {
        playbackRef.current.play(next.session.playbackSpeed);
        publish(next);
      }
      return;
    }
    void loadCandidate(true);
  }

  function loadStaticPose() {
    if (!candidate) return;
    if (playbackRef.current) {
      playbackRef.current.resetPose();
      publish(resetMotionPose(stateRef.current));
      return;
    }
    void loadCandidate(false);
  }

  function pause() {
    playbackRef.current?.pause();
    publish(pauseMotion(stateRef.current));
  }

  function resetPose() {
    playbackRef.current?.resetPose();
    publish(resetMotionPose(stateRef.current));
  }

  function seek(fraction: number) {
    const next = seekMotionProgress(stateRef.current, fraction);
    if (next === stateRef.current) return;
    playbackRef.current?.seek(next.session.currentTimeSeconds);
    publish(next);
  }

  function toggleSlow() {
    const speed = stateRef.current.session.playbackSpeed === 1 ? 0.5 : 1;
    const next = setMotionSpeed(stateRef.current, speed);
    playbackRef.current?.setSpeed(speed);
    publish(next);
  }

  const available = Boolean(candidate);
  const loaded = Boolean(state.session.assetId && state.durationSeconds);
  const progress = loaded && state.durationSeconds
    ? Math.round((state.session.currentTimeSeconds / state.durationSeconds) * 100)
    : 0;
  const statusText = state.session.status === "error"
    ? state.session.errorMessage
    : state.session.status === "loading"
      ? "시범 자료를 불러오고 있습니다."
      : !selectedAction
        ? "먼저 작용을 선택해 주세요."
        : !available
          ? "이 작용에 연결된 3D 시범 자료가 아직 없습니다. 글 설명으로 작용을 확인할 수 있습니다."
          : state.prefersReducedMotion
            ? "움직임 줄이기 설정이 적용되어 정지 자세로 확인합니다. 재생은 자동으로 시작되지 않습니다."
            : loaded
              ? state.session.status === "playing" ? "교육용 시범을 재생 중입니다." : "재생 버튼을 눌러 교육용 시범을 볼 수 있습니다."
              : "재생을 누르면 연결된 시범 자료를 불러옵니다. 자동 재생은 하지 않습니다.";

  return <section className="motion-player" aria-label="움직임으로 이해하기" data-testid="motion-player">
    <h4>움직임으로 이해하기</h4>
    <fieldset className="motion-action-picker" aria-label="작용 선택">
      <legend>작용 선택</legend>
      {actions.length ? actions.map((action) => <button
        type="button"
        key={action.id}
        aria-pressed={action.id === selectedActionId}
        onClick={() => onSelectAction(action.id)}
      >{action.label}</button>) : <p className="quiet-note">연결된 작용 자료가 없습니다.</p>}
    </fieldset>
    <p className="motion-player-status" role="status" aria-live="polite">{statusText}</p>
    {state.prefersReducedMotion && available && <button type="button" onClick={loadStaticPose} disabled={!candidate || state.session.status === "loading"}>
      정지 자세 보기
    </button>}
    <div className="motion-player-controls" aria-label="시범 재생 조작">
      <button type="button" onClick={play} disabled={!available || state.prefersReducedMotion || state.session.status === "loading" || state.session.status === "playing"}>재생</button>
      <button type="button" onClick={pause} disabled={state.session.status !== "playing"}>멈춤</button>
      <button type="button" onClick={resetPose} disabled={!loaded}>처음 자세</button>
      <button type="button" onClick={toggleSlow} aria-pressed={state.session.playbackSpeed < 1} disabled={!available}>
        느리게 보기{state.session.playbackSpeed < 1 ? " 켬" : " 끔"}
      </button>
    </div>
    <label className="motion-progress-label" htmlFor="motion-progress">시범 진행</label>
    <div className="motion-progress-row">
      <input
        id="motion-progress"
        aria-label="시범 진행 위치"
        type="range"
        min={0}
        max={100}
        step={1}
        value={progress}
        disabled={!loaded}
        onChange={(event) => seek(Number(event.currentTarget.value) / 100)}
      />
      <output htmlFor="motion-progress">{progress}%</output>
    </div>
    <p className="motion-player-note">진행 막대는 시범의 재생 위치를 나타냅니다. 힘이나 근력의 비율이 아닙니다. 처음 자세는 움직임만 되돌리며, 카메라는 별도 보기 조작으로 초기화합니다.</p>
  </section>;
}
