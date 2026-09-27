import { createIdleMotionSession, type MotionSession } from "./motionLearning.ts";

export interface MotionPlayerState {
  /** Runtime-only UI state. Never write this object into learning content or localStorage. */
  session: MotionSession;
  selectedActionId: string | null;
  durationSeconds: number | null;
  generation: number;
  prefersReducedMotion: boolean;
  boundStructureIds: string[];
}

export interface LoadedMotionBinding {
  actionId: string;
  definitionId: string;
  assetId: string;
  durationSeconds: number;
  structureIds: readonly string[];
}

export function createMotionPlayerState(
  actionId: string | null,
  prefersReducedMotion = false,
): MotionPlayerState {
  return {
    session: createIdleMotionSession(),
    selectedActionId: actionId,
    durationSeconds: null,
    generation: 0,
    prefersReducedMotion,
    boundStructureIds: [],
  };
}

function emptySession(): MotionSession {
  return createIdleMotionSession();
}

function invalidated(state: MotionPlayerState, actionId: string | null): MotionPlayerState {
  return {
    ...state,
    session: emptySession(),
    selectedActionId: actionId,
    durationSeconds: null,
    generation: state.generation + 1,
    boundStructureIds: [],
  };
}

/** An action or atlas-context switch invalidates pending loads and any active emphasis. */
export function selectMotionAction(state: MotionPlayerState, actionId: string | null): MotionPlayerState {
  if (state.selectedActionId === actionId) return state;
  return invalidated(state, actionId);
}

export function changeMotionContext(state: MotionPlayerState): MotionPlayerState {
  return invalidated(state, null);
}

export function beginMotionAssetLoad(state: MotionPlayerState): { state: MotionPlayerState; requestToken: number | null } {
  if (!state.selectedActionId) return { state, requestToken: null };
  const requestToken = state.generation + 1;
  return {
    requestToken,
    state: {
      ...state,
      generation: requestToken,
      durationSeconds: null,
      boundStructureIds: [],
      session: {
        ...emptySession(),
        status: "loading",
        playbackSpeed: state.session.playbackSpeed,
      },
    },
  };
}

export function acceptMotionAssetLoad(
  state: MotionPlayerState,
  requestToken: number,
  loaded: LoadedMotionBinding,
): MotionPlayerState {
  if (state.generation !== requestToken || state.session.status !== "loading" || loaded.actionId !== state.selectedActionId) return state;
  if (!loaded.definitionId || !loaded.assetId || !Number.isFinite(loaded.durationSeconds) || loaded.durationSeconds <= 0 || loaded.structureIds.length === 0) {
    return failMotionAssetLoad(state, requestToken);
  }
  return {
    ...state,
    durationSeconds: loaded.durationSeconds,
    boundStructureIds: [...new Set(loaded.structureIds)],
    session: {
      ...state.session,
      status: "ready",
      definitionId: loaded.definitionId,
      assetId: loaded.assetId,
      currentTimeSeconds: 0,
      selectedStructureIds: [],
      errorMessage: null,
    },
  };
}

export function failMotionAssetLoad(state: MotionPlayerState, requestToken: number): MotionPlayerState {
  if (state.generation !== requestToken || state.session.status !== "loading") return state;
  return {
    ...state,
    session: {
      ...emptySession(),
      status: "error",
      playbackSpeed: state.session.playbackSpeed,
      errorMessage: "시범 자료를 불러오지 못했습니다. 글 설명은 계속 확인할 수 있습니다.",
    },
    durationSeconds: null,
    boundStructureIds: [],
  };
}

export function playMotion(state: MotionPlayerState): MotionPlayerState {
  if (state.prefersReducedMotion || !state.session.assetId || !state.durationSeconds || !["ready", "paused"].includes(state.session.status)) return state;
  return {
    ...state,
    session: { ...state.session, status: "playing", selectedStructureIds: [...state.boundStructureIds], errorMessage: null },
  };
}

export function pauseMotion(state: MotionPlayerState): MotionPlayerState {
  if (state.session.status !== "playing") return state;
  return { ...state, session: { ...state.session, status: "paused" } };
}

/** Hiding the page cancels pending loads and drops playback emphasis without losing a loaded clip. */
export function suspendMotionForHiddenPage(state: MotionPlayerState): MotionPlayerState {
  if (state.session.status === "loading") return invalidated(state, state.selectedActionId);
  if (state.session.status !== "playing" && state.session.selectedStructureIds.length === 0) return state;
  return {
    ...state,
    session: {
      ...state.session,
      status: state.session.status === "playing" ? "paused" : state.session.status,
      selectedStructureIds: [],
    },
  };
}

export function setMotionTime(state: MotionPlayerState, seconds: number): MotionPlayerState {
  if (!state.session.assetId || !state.durationSeconds || !Number.isFinite(seconds)) return state;
  const currentTimeSeconds = Math.max(0, Math.min(state.durationSeconds, seconds));
  const status = state.session.status === "playing"
    ? currentTimeSeconds >= state.durationSeconds ? "paused" : "playing"
    : currentTimeSeconds === 0 ? "ready" : "paused";
  return {
    ...state,
    session: {
      ...state.session,
      status,
      currentTimeSeconds,
      selectedStructureIds: status === "playing" ? [...state.boundStructureIds] : [],
    },
  };
}

export function seekMotionProgress(state: MotionPlayerState, fraction: number): MotionPlayerState {
  if (!Number.isFinite(fraction) || !state.durationSeconds) return state;
  return setMotionTime(state, Math.max(0, Math.min(1, fraction)) * state.durationSeconds);
}

/** Pose reset only changes clip time; it has no camera/viewer reference by design. */
export function resetMotionPose(state: MotionPlayerState): MotionPlayerState {
  if (state.session.status === "loading") return invalidated(state, state.selectedActionId);
  if (!state.session.assetId || !state.durationSeconds) return state;
  return {
    ...state,
    session: {
      ...state.session,
      status: "ready",
      currentTimeSeconds: 0,
      selectedStructureIds: [],
      errorMessage: null,
    },
  };
}

export function setMotionSpeed(state: MotionPlayerState, speed: 0.5 | 1): MotionPlayerState {
  if (state.session.playbackSpeed === speed) return state;
  return { ...state, session: { ...state.session, playbackSpeed: speed } };
}

export function setReducedMotionPreference(state: MotionPlayerState, prefersReducedMotion: boolean): MotionPlayerState {
  if (state.prefersReducedMotion === prefersReducedMotion) return state;
  const next = { ...state, prefersReducedMotion };
  if (prefersReducedMotion && state.session.status === "loading") return invalidated(next, state.selectedActionId);
  if (prefersReducedMotion && state.session.assetId) {
    return {
      ...next,
      session: { ...state.session, status: "paused", currentTimeSeconds: 0, selectedStructureIds: [] },
    };
  }
  return next;
}
