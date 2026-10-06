import { useEffect, useRef, useState } from "react";
import {
  acceptMotionAssetLoad,
  beginMotionAssetLoad,
  failMotionAssetLoad,
  pauseMotion,
  playMotion,
  resetMotionPose,
  seekMotionProgress,
  syncMotionPlaybackTime,
  setReducedMotionPreference,
  suspendMotionForHiddenPage,
  type MotionPlayerState,
} from "../domain/motionPlayer";
import type { LearnerMotionActionOption } from "../domain/motionLearning";
import { motionActionLabel, motionLearningIntent, motionLearningTitle, motionPhaseLabel } from "../domain/atlasMotionExperience.ts";
import { motionSubjectExplanation, selectedMotionSubjectRole } from "../domain/motionSubjectPresentation.ts";
import { loadAnimationScene } from "../viewer/animationSceneAdapter";
import { AnimationPlaybackController } from "../viewer/animationPlayback";
import type { SourceMotionHost } from "../viewer/datasets/sourceMotionHost.ts";
import { DATASET_BUDGET } from "../viewer/datasets/schema.ts";

interface Props {
  actions: readonly LearnerMotionActionOption[];
  selectedActionId: string | null;
  onSelectAction(actionId: string): void;
  host: SourceMotionHost | null;
  sourceContextKey: string | null;
  active?: boolean;
  showActionPicker?: boolean;
  muscleLayerEnabled?: boolean;
  boneLayerEnabled?: boolean;
  subjectKind?: "muscle" | "bone";
  subjectHidden?: boolean;
}

function prefersReducedMotion(): boolean {
  return typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

async function readMotionPackage(response: Response, signal: AbortSignal): Promise<ArrayBuffer> {
  const declaredLength = Number(response.headers.get("content-length"));
  if (Number.isFinite(declaredLength) && declaredLength > DATASET_BUDGET.geometryBytes) {
    throw new Error("시범 자료가 현재 형상·움직임 예산을 초과합니다.");
  }
  if (!response.body) {
    const bytes = await response.arrayBuffer();
    if (bytes.byteLength > DATASET_BUDGET.geometryBytes) throw new Error("시범 자료가 현재 형상·움직임 예산을 초과합니다.");
    return bytes;
  }
  const reader = response.body.getReader();
  const chunks: Uint8Array[] = [];
  let totalBytes = 0;
  try {
    while (true) {
      if (signal.aborted) throw new DOMException("Motion load cancelled", "AbortError");
      const { done, value } = await reader.read();
      if (done) break;
      totalBytes += value.byteLength;
      if (totalBytes > DATASET_BUDGET.geometryBytes) {
        await reader.cancel();
        throw new Error("시범 자료가 현재 형상·움직임 예산을 초과합니다.");
      }
      chunks.push(value);
    }
  } finally {
    reader.releaseLock();
  }
  const output = new Uint8Array(totalBytes);
  let offset = 0;
  for (const chunk of chunks) { output.set(chunk, offset); offset += chunk.byteLength; }
  return output.buffer;
}

export function MotionLearningPanel({ actions, selectedActionId, onSelectAction, host, sourceContextKey, active = true, showActionPicker = true, muscleLayerEnabled = true, boneLayerEnabled = true, subjectKind = "muscle", subjectHidden = false }: Props) {
  const selectedAction = actions.find((action) => action.id === selectedActionId) ?? null;
  const candidate = selectedAction?.candidate ?? null;
  const intent = motionLearningIntent(selectedAction);
  const actionLabel = motionActionLabel(selectedAction?.label ?? "");
  const selectedSubjectRole = selectedMotionSubjectRole(candidate?.asset ?? null, sourceContextKey);
  const [state, setState] = useState<MotionPlayerState>(() => ({
    session: { status: "idle", definitionId: null, assetId: null, currentTimeSeconds: 0, playbackSpeed: 1, selectedStructureIds: [], errorMessage: null },
    selectedActionId,
    durationSeconds: null,
    generation: 0,
    prefersReducedMotion: prefersReducedMotion(),
    boundStructureIds: [],
  }));
  const [returning, setReturning] = useState(false);
  const returningRef = useRef(false);
  const [phase, setPhase] = useState<AnimationPlaybackController["phase"]>("rest");
  const timePublication = useRef({ at: 0, phase: "rest" });
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
    host?.restoreSourceMotion("player-unmounted");
    playbackRef.current?.dispose();
    playbackRef.current = null;
  }, [host]);

  useEffect(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    returningRef.current = false;
    setReturning(false);
    setPhase("rest");
    host?.restoreSourceMotion("selection-or-action-changed");
    playbackRef.current = null;
    const current = stateRef.current;
    publish({ ...current, session: { status: "idle", definitionId: null, assetId: null, currentTimeSeconds: 0,
      playbackSpeed: 1, selectedStructureIds: [], errorMessage: null }, durationSeconds: null,
      generation: current.generation + 1, selectedActionId, boundStructureIds: [] });
  }, [host, sourceContextKey, selectedActionId]);

  useEffect(() => {
    if (muscleLayerEnabled && !subjectHidden) return;
    abortRef.current?.abort();
    abortRef.current = null;
    host?.restoreSourceMotion(subjectHidden ? "selected-source-hidden" : "subject-layer-hidden");
    playbackRef.current?.dispose();
    playbackRef.current = null;
    returningRef.current = false;
    setReturning(false);
    const current = stateRef.current;
    publish({ ...current, session: { status: "idle", definitionId: null, assetId: null, currentTimeSeconds: 0,
      playbackSpeed: 1, selectedStructureIds: [], errorMessage: null }, durationSeconds: null,
      generation: current.generation + 1, boundStructureIds: [] });
  }, [muscleLayerEnabled, subjectHidden, host]);

  useEffect(() => {
    if (active || !playbackRef.current?.isPlaying) return;
    returnToRest();
  }, [active]);

  async function loadCandidate(startAfterLoad: boolean) {
    const option = actions.find((action) => action.id === stateRef.current.selectedActionId);
    const playable = option?.candidate ?? null;
    if (!option || !playable || !host || !muscleLayerEnabled || subjectHidden) return;
    const begun = beginMotionAssetLoad(stateRef.current);
    if (begun.requestToken === null) return;
    abortRef.current?.abort();
    host.restoreSourceMotion("new-source-motion-request");
    playbackRef.current?.dispose();
    playbackRef.current = null;
    publish(begun.state);

    const abort = new AbortController();
    abortRef.current = abort;
    try {
      const uri = new URL(playable.asset.uri, window.location.href);
      const response = await fetch(uri, { signal: abort.signal });
      if (!response.ok) throw new Error("asset request failed");
      const bytes = await readMotionPackage(response, abort.signal);
      const resource = await loadAnimationScene(bytes, playable.asset, {
        basePath: new URL(".", uri).href,
        signal: abort.signal,
      });
      const current = stateRef.current;
      if (abort.signal.aborted || current.generation !== begun.requestToken || current.session.status !== "loading") {
        resource.dispose();
        return;
      }

      const controller = await host.attachSourceMotion(playable.asset, resource, (time, completed) => {
          const latest = stateRef.current;
          const nextPhase = playbackRef.current?.phase ?? "rest";
          const now = performance.now();
          const phaseChanged = nextPhase !== timePublication.current.phase;
          // Geometry keeps its frame clock; the card needs only ten updates per second.
          if (!completed && !phaseChanged && now - timePublication.current.at < 100) return;
          timePublication.current = { at: now, phase: nextPhase };
          setPhase(nextPhase);
          publish(syncMotionPlaybackTime(latest, time, Boolean(playbackRef.current?.isPlaying) && !returningRef.current));
        }, (reason) => {
          abortRef.current?.abort();
          abortRef.current = null;
          playbackRef.current = null;
          returningRef.current = false;
    setReturning(false);
          const latest = stateRef.current;
          publish({ ...latest, session: { status: "idle", definitionId: null, assetId: null, currentTimeSeconds: 0,
            playbackSpeed: 1, selectedStructureIds: [], errorMessage: null }, durationSeconds: null,
            generation: latest.generation + 1, boundStructureIds: [] });
          setPhase("rest");
          void reason;
        }, { intent: motionLearningIntent(option) });
      const afterAttach = stateRef.current;
      if (abort.signal.aborted || afterAttach.generation !== begun.requestToken || afterAttach.session.status !== "loading") {
        host.restoreSourceMotion("late-motion-response");
        controller.dispose();
        return;
      }
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
    } catch (error) {
      if (import.meta.env.DEV) console.debug("Motion package unavailable", error);
      if (abort.signal.aborted) return;
      host.restoreSourceMotion("source-motion-load-failed");
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

  function toggleMotion() {
    // The actual clock wins over an asynchronously published card snapshot.
    if (playbackRef.current?.isPlaying) returnToRest();
    else play();
  }

  function returnToRest() {
    const player = playbackRef.current;
    if (!player) return;
    returningRef.current = true;
    setReturning(true);
    setPhase("return");
    publish(pauseMotion(stateRef.current));
    player.returnToRest(0.7, () => {
      returningRef.current = false;
    setReturning(false);
      host?.restoreSourceMotion("smooth-return-completed");
    });
  }

  function seek(fraction: number) {
    const current = stateRef.current;
    const sought = seekMotionProgress(current, fraction);
    const next = {
      ...sought,
      session: {
        ...sought.session,
        status: sought.session.currentTimeSeconds === 0 ? "ready" as const : "paused" as const,
        selectedStructureIds: [],
      },
    };
    if (next === stateRef.current) return;
    playbackRef.current?.pause();
    playbackRef.current?.seek(next.session.currentTimeSeconds);
    setPhase(playbackRef.current?.phase ?? "rest");
    publish(next);
  }

  const available = Boolean(candidate) && muscleLayerEnabled && !subjectHidden;
  const loaded = Boolean(state.session.assetId && state.durationSeconds);
  const progress = loaded && state.durationSeconds
    ? Math.round((state.session.currentTimeSeconds / state.durationSeconds) * 100)
    : 0;
  const poseFraction = loaded && state.durationSeconds ? state.session.currentTimeSeconds / state.durationSeconds : 0;
  const statusText = state.session.status === "error"
    ? state.session.errorMessage
    : state.session.status === "loading"
      ? "시범 자료를 불러오고 있습니다."
    : !selectedAction
        ? actions.length ? "먼저 작용을 선택해 주세요." : "현재 연결된 작용 설명이 없으며 재생 자료도 제공되지 않습니다."
        : !available
          ? !muscleLayerEnabled ? `${subjectKind === "bone" ? "뼈" : "근육"} 보기가 꺼져 있어 시범을 표시할 수 없습니다. 모형 보기에서 켜 주세요.` : subjectHidden ? "선택한 모형을 숨겨 시범을 표시할 수 없습니다. 선택 다시 표시를 누르면 재생할 수 있습니다." : "이 작용에 연결된 3D 시범 자료가 아직 없습니다. 글 설명으로 작용을 확인할 수 있습니다."
          : state.prefersReducedMotion
            ? "움직임 줄이기 설정이 적용되어 정지 자세로 확인합니다. 재생은 자동으로 시작되지 않습니다."
        : loaded
              ? returning ? "처음 자세로 서서히 돌아갑니다." : state.session.status === "playing" ? "움직임을 반복해서 보여 줍니다. 버튼을 다시 누르면 처음 자세로 서서히 돌아갑니다." : state.session.currentTimeSeconds > 0 ? "진행 막대로 고른 자세를 유지합니다. 버튼을 누르면 반복 시범을 시작합니다." : "움직임으로 이해하기를 눌러 시범을 볼 수 있습니다."
              : "움직임으로 이해하기를 누르면 시범을 반복해서 보여 줍니다.";

  return <section className="motion-player" aria-label="움직임으로 이해하기" data-testid="motion-player">
    <div className="motion-heading"><h4>{motionLearningTitle(intent)}</h4>
      {selectedAction && <span className="motion-kind">{intent === "muscle_action" ? "작용 시범" : intent === "bone_motion" ? "관절 시범" : intent === "posture_observation" ? "주변 구조 관찰" : "글 설명"}</span>}
    </div>
    {selectedAction && <p className="motion-action-summary">{actionLabel}</p>}
    {candidate && !boneLayerEnabled && <p className="quiet-note" role="status">뼈 보기가 꺼져 있습니다. 관절과 기시·정지 뼈를 함께 보려면 모형 아래의 뼈 보기를 켜 주세요.</p>}
    {intent === "posture_observation" && <p className="quiet-note">주변 관절이 움직일 때의 모습을 보여 줍니다. 선택한 근육의 작용 시범은 아닙니다.</p>}
    {showActionPicker && <fieldset className="motion-action-picker" aria-label="움직임 선택">
      <legend>움직임 선택</legend>
      {actions.length ? actions.map((action) => <button
        type="button"
        key={action.id}
        aria-pressed={action.id === selectedActionId}
        onClick={() => onSelectAction(action.id)}
      >{motionActionLabel(action.label)}{motionLearningIntent(action) === "posture_observation" && <small>주변 구조</small>}</button>) : <p className="quiet-note">연결된 작용 자료가 없습니다.</p>}
    </fieldset>}
    {loaded && <div className="motion-phase" data-phase={phase} aria-label="현재 동작 구간">
      <span className="motion-phase-dot"/><strong>{motionPhaseLabel(phase, actionLabel)}</strong>
      <span>{returning ? "복원 중" : state.session.status === "playing" ? "반복 재생" : "정지"}</span>
    </div>}
    <p className="motion-player-status" role="status" aria-live="polite">{statusText}</p>
    {state.prefersReducedMotion && available && <button type="button" onClick={loadStaticPose} disabled={!candidate || state.session.status === "loading"}>
      정지 자세 보기
    </button>}
    <div className="motion-player-controls" aria-label="시범 재생 조작">
      <button type="button" onClick={toggleMotion} aria-pressed={state.session.status === "playing" || returning}
        disabled={!available || state.prefersReducedMotion || state.session.status === "loading" || returning}>
        움직임으로 이해하기
      </button>
    </div>
    {candidate?.asset.poseControl && <details className="joint-angle-control"><summary>관절 조절</summary>
      <label htmlFor="joint-angle">{candidate.asset.poseControl.label}</label>
      <input id="joint-angle" aria-label="교육용 관절 각도" type="range"
        min={Math.min(candidate.asset.poseControl.startDegrees, candidate.asset.poseControl.endDegrees)}
        max={Math.max(candidate.asset.poseControl.startDegrees, candidate.asset.poseControl.endDegrees)} step={0.1}
        value={candidate.asset.poseControl.startDegrees + (candidate.asset.poseControl.endDegrees - candidate.asset.poseControl.startDegrees) * poseFraction}
        disabled={!loaded || returning} onChange={event => seek((Number(event.currentTarget.value) - candidate.asset.poseControl!.startDegrees) /
          (candidate.asset.poseControl!.endDegrees - candidate.asset.poseControl!.startDegrees))}/>
      <output htmlFor="joint-angle">{(candidate.asset.poseControl.startDegrees + (candidate.asset.poseControl.endDegrees - candidate.asset.poseControl.startDegrees) * poseFraction).toFixed(1)}°</output>
      <p className="quiet-note">교육용 자세 조절입니다. 개인의 정상 운동범위가 아닙니다. 지금 선택한 한 방향만 조절하며 다른 방향과의 조합은 제공하지 않습니다.</p>
    </details>}
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
        disabled={!loaded || returning}
        onChange={(event) => seek(Number(event.currentTarget.value) / 100)}
      />
      <output htmlFor="motion-progress">{progress}%</output>
    </div>
    <p className="motion-player-note">다시 누르면 처음 자세로 부드럽게 돌아갑니다. 진행 막대를 조절하면 고른 자세를 유지합니다.</p>
    <details className="motion-explanation"><summary>시범 안내</summary><p>{motionSubjectExplanation(subjectKind, selectedSubjectRole)} 교육용 동작이며, 힘·활성도·개인의 정상 운동범위를 나타내지 않습니다. 카메라와 보기 설정은 유지됩니다.</p></details>
  </section>;
}
