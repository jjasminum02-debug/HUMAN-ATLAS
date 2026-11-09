import * as THREE from 'three';
import { AnatomyMaterials, ANATOMY_PALETTE, type MaterialMode } from '../anatomyMaterials.ts';
import { demandedStructureKeys, layerIdOf, innervationHighlightKeys, observingNerves, observationFrameKeys, attachmentObservationKeys, shouldFocusNerveSelection, nerveCourseKeys } from './presentation.ts';
import { AnatomySceneController, type BodyProgress } from '../wholeBody/AnatomySceneController.ts';
import type { BodyManifest, BodyView } from '../wholeBody/contract.ts';
import { DatasetResources } from './DatasetResources.ts';
import { framingRecords } from './framing.ts';
import { pickSurface } from './surfacePicking.ts';
import { keptBySection, sectionPlane, sectionViewDirection, type Bounds, type Section } from '../section.ts';
import type { Dataset } from './schema.ts';
import { DATASET_BUDGET } from './schema.ts';
import { validateRuntimeIntegration, type RuntimeIntegration, type RuntimeStructureRecord } from './integration.ts';
import { AnimationPlaybackController, type AnimationPlaybackOptions } from '../animationPlayback.ts';
import type { AnimationSceneResource } from '../animationSceneAdapter.ts';
import type { MotionAsset } from '../../domain/motionLearning.ts';
import { sourceGeometrySha256 } from './sourceMotionGeometry.ts';
import type { SourceMotionHost } from './sourceMotionHost.ts';
import { attachmentBoneKeys } from './regionalContext.ts';
import { motionFrameSourceKeys } from './motionFrameContext.ts';
import { motionContextVisibility } from './motionContextVisibility.ts';
import { contextBoneFollowers, followContextBone, limbMotionContextKeys } from './motionContextBonePose.ts';
import { muscleActionEmphasis } from "../../domain/atlasMotionExperience.ts";
import { boneSegments, clampPose, segmentTransforms, type RigFile, type RigPose } from '../rig.ts';
import { parseSkinChunk, posedCopy, segmentForRole, skinGeometry, type SkinChunk, preserveVolume, volumeProfile } from '../skin.ts';
import type { Instance } from './schema.ts';
import type { ActionHighlight, MuscleActionsFile, RigHost } from '../movement.ts';
/** Row kinds whose surfaces bend with the rig (M2); bones move rigidly instead. */
const SKINNED_KINDS = new Set(['muscle', 'tendon', 'fascia', 'joint', 'vessel', 'nerve']);
/** C4 attachment area: a Z-Anatomy patch (`key`) or an estimated bone-contact area (`source: 'contact'`). */
type AttachmentRow = { key?: string; role: 'origin' | 'insertion' | 'attachment'; bone: string | null; source: 'za' | 'contact' };
const ATTACHMENT_VARIANT = { origin: 'attachmentOrigin', insertion: 'attachmentInsertion', attachment: 'attachmentEstimated' } as const;
/** Non-indexed copy of the given triangles of `source` (own buffers, safe to dispose). */
function triangleSubset(source: THREE.BufferGeometry, triangles: Uint32Array) {
    const index = source.getIndex()!, position = source.getAttribute('position'), normal = source.getAttribute('normal');
    const p = new Float32Array(triangles.length * 9), n = new Float32Array(triangles.length * 9);
    triangles.forEach((t, i) => { for (let k = 0; k < 3; k++) { const v = index.getX(t * 3 + k), o = (i * 3 + k) * 3;
        p[o] = position.getX(v); p[o + 1] = position.getY(v); p[o + 2] = position.getZ(v);
        if (normal) { n[o] = normal.getX(v); n[o + 1] = normal.getY(v); n[o + 2] = normal.getZ(v); } } });
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(p, 3));
    if (normal) geometry.setAttribute('normal', new THREE.BufferAttribute(n, 3)); else geometry.computeVertexNormals();
    return geometry;
}
const decodeTriangles = (packed: string) => { const bytes = Uint8Array.from(atob(packed), c => c.charCodeAt(0)); return new Uint32Array(bytes.buffer); };
import type { MotionLearningIntent } from '../../domain/atlasMotionExperience.ts';
/** Dataset selection/presentation adapter; renderer, camera and lifecycle remain owned by the existing controller. */
export class DatasetSceneAdapter implements SourceMotionHost, RigHost {
    readonly scene: AnatomySceneController;
    readonly resources: DatasetResources;
    readonly integration: RuntimeIntegration;
    readonly records: Map<string, RuntimeStructureRecord>;
    private view: BodyView = { region: null, regionIds: [], bones: true, muscles: true, supplements: false, selectedId: null, dim: true };
    private materials = new AnatomyMaterials();
    /** Q2-2 cross-section: one clipping plane on the renderer, so every pass (AO, outline) is cut too. */
    private sectionState: { section: Section; plane: THREE.Plane } | null = null;
    /** Q2-3 quiz: structure highlighted like a selection, without selecting it (the card would give the name away). */
    private quizTarget: string | null = null;
    /** M1 skeleton rig: bones follow their segment transform; null transforms = rest pose. Ignored while a motion clip plays. */
    private rigState: { file: RigFile; segmentOf: Map<string, string>; transforms: Map<string, THREE.Matrix4> | null } | null = null;
    private readonly skinChunks = new Map<string, SkinChunk | 'loading' | 'failed'>();
    private instanceByKey?: Map<string, Instance>;
    /** M3: learner pose (as set, before clamping), agonist/antagonist colouring, and the panel's open requests. */
    private pose: RigPose | null = null;
    private actionHighlight: ActionHighlight = null;
    private rigFile?: Promise<RigFile>;
    private muscleActions?: Promise<MuscleActionsFile>;
    private readonly poseListeners = new Set<(pose: RigPose | null) => void>();
    private readonly openMovementListeners = new Set<(jointId: string) => void>();
    /** C4: origin/insertion patches drawn on the bone for the selected muscle (/__atlas/v2/attachments.json). */
    private attachments: { muscles: Record<string, AttachmentRow[]> } | 'loading' | 'failed' | null = null;
    /** Estimated (contact) areas: triangle indices per bone resource, fetched per muscle; meshes built from the bone. */
    private readonly contactTris = new Map<string, Record<string, string>[] | 'loading' | 'failed'>();
    private readonly contactNodes = new Map<string, THREE.Mesh>();
    private readonly patchRole = new Map<string, { role: AttachmentRow['role']; bone: string | null }>();
    private readonly displayKeys: Set<string>;
    private down = { x: 0, y: 0 };
    private dead = false;
    private contextLost = false;
    private motionPoseActive = false;
    private readonly actionTone = new THREE.Color(ANATOMY_PALETTE.action);
    private readonly returnTone = new THREE.Color(ANATOMY_PALETTE.return);
    private motionPhase: AnimationPlaybackController['phase'] = 'rest';
    private motionIntent: MotionLearningIntent = 'posture_observation';
    private guidedMotionDirection: THREE.Vector3 | null = null;
    private notify: (p: BodyProgress) => void;
    private select: (id: string, side: string | null) => void;
    private motion: { asset: MotionAsset; resource: AnimationSceneResource; player: AnimationPlaybackController; originals: Map<string, { node: THREE.Mesh; visible: boolean }>; packageMaterials: Map<string, THREE.Material | THREE.Material[]>; contextKey: string; frameSourceKeys: string[]; extraContextKeys: string[]; boneFollowers: Array<{ node: THREE.Mesh; rest: THREE.Matrix4; anchor: THREE.Object3D; anchorRestInverse: THREE.Matrix4 }>; onInvalidated?: (reason: string) => void } | null = null;
    constructor(host: HTMLElement, dataset: Dataset, integration: RuntimeIntegration, notify: (p: BodyProgress) => void, select: (id: string, side: string | null) => void) {
        validateRuntimeIntegration(integration, dataset);
        this.notify = notify;
        this.select = select;
        this.integration = integration;
        this.records = new Map(integration.objects.map(r => [r.sourceKey, r]));
        const empty = { version: 2, localOnly: true, publicRedistribution: 'held', frame: dataset.frameContract?.targetFrameId ?? 'unverified', unit: 'm', lodLevels: 1, chunks: [] } as BodyManifest;
        this.scene = new AnatomySceneController(host, empty, p => { if (this.contextLost !== p.contextLost) {
            this.contextLost = p.contextLost;
            if (this.contextLost) this.restoreSourceMotion('webgl-context-lost');
            if (this.resources)
                this.apply();
        } }, () => { });
        this.displayKeys = new Set(integration.objects.filter(r => r.localDisplayEligible).map(r => r.sourceKey));
        this.resources = new DatasetResources(dataset, this.scene.root, false, () => this.apply(), this.displayKeys);
        const canvas = this.scene.renderer.domElement;
        canvas.addEventListener('keydown', this.onKey, true);
        canvas.addEventListener('pointerdown', this.onDown);
        canvas.addEventListener('pointerup', this.onUp);
        this.setView(this.view);
        this.focus([], false);
        if (import.meta.env?.DEV) (window as unknown as { __atlasRig?: object }).__atlasRig = { // dev inspection only
            load: async () => (await fetch('/__atlas/v2/rig.json')).json() as Promise<RigFile>,
            set: (rig: RigFile, pose: RigPose) => this.setRigPose(rig, pose), reset: (rig: RigFile) => this.setRigPose(rig, null) };
    }
    /** M2: bend muscles, tendons, ligaments, capsules and fascia with the pose; restore rest geometry when unposed. */
    private skinSoftTissue() {
        const transforms = this.rigState?.transforms ?? null;
        this.instanceByKey ??= new Map(this.resources.dataset.instances.map(instance => [instance.sourceKey, instance]));
        const instanceMatrix = new THREE.Matrix4(), inverse = new THREE.Matrix4();
        for (const [key, node] of this.resources.nodes) {
            const row = this.records.get(key);
            if (!row || !SKINNED_KINDS.has(row.kind)) continue;
            const posed = node.userData.posedGeometry as THREE.BufferGeometry | undefined;
            const rest = posed && node.geometry === posed ? posed.userData.skinRest as THREE.BufferGeometry : node.geometry;
            if (!transforms) {
                if (posed) { node.geometry = rest; posed.dispose(); delete node.userData.posedGeometry; }
                continue;
            }
            const instance = this.instanceByKey.get(key);
            const chunkId = instance && [instance.lods.overview, instance.lods.detail].find(lod => lod.resource === node.userData.resourceKey)?.chunk;
            if (!chunkId) continue;
            const chunk = this.skinChunks.get(chunkId);
            if (!chunk) { this.loadSkin(chunkId); continue; }
            if (chunk === 'loading' || chunk === 'failed') continue;
            const weights = chunk.get(node.userData.resourceKey);
            if (!weights || weights.data.length !== rest.getAttribute('position').count) continue;
            instanceMatrix.fromArray(node.userData.instanceMatrix); inverse.copy(instanceMatrix).invert();
            const slots = weights.roles.map(role => inverse.clone().multiply(transforms.get(segmentForRole(role, row.side)) ?? new THREE.Matrix4()).multiply(instanceMatrix));
            let target = posed && posed.userData.skinRest === rest ? posed : undefined;
            if (!target) { posed?.dispose(); target = posedCopy(rest); node.userData.posedGeometry = target; }
            skinGeometry(rest, weights.data, slots, target);
            // Muscle bellies keep their volume: thicker when shortened, thinner when stretched (tendons and sheets do not).
            if (row.kind === 'muscle') {
                if (rest.userData.volumeProfile === undefined) rest.userData.volumeProfile = volumeProfile(rest.getAttribute('position').array as Float32Array);
                if (rest.userData.volumeProfile) preserveVolume(rest.userData.volumeProfile, target);
            }
            node.geometry = target;
        }
    }
    private loadSkin(chunkId: string) {
        this.skinChunks.set(chunkId, 'loading');
        fetch(`/__atlas/v2/skin/${chunkId}.bin`).then(response => response.ok ? response.arrayBuffer() : Promise.reject(Error(String(response.status))))
            .then(buffer => { this.skinChunks.set(chunkId, parseSkinChunk(buffer)); if (!this.dead) this.apply(); })
            .catch(() => this.skinChunks.set(chunkId, 'failed'));
    }
    /** Estimated attachment areas of the selected muscle, rebuilt from the bone mesh it lies on; follows the bone's pose. */
    private syncContactAreas() {
        const muscle = this.view.selectedId ?? '';
        const rows = this.selectedAttachments().filter(r => r.source === 'contact');
        let tris = rows.length ? this.contactTris.get(muscle) : undefined;
        if (rows.length && !tris) {
            this.contactTris.set(muscle, 'loading'); tris = 'loading';
            fetch(`/__atlas/v2/attachments/${muscle}.json`).then(r => r.ok ? r.json() : Promise.reject(Error(String(r.status))))
                .then(file => { this.contactTris.set(muscle, file.rows); if (!this.dead) this.apply(); })
                .catch(() => this.contactTris.set(muscle, 'failed'));
        }
        const wanted = new Set<string>();
        if (Array.isArray(tris)) rows.forEach((row, i) => {
            const bone = this.resources.nodes.get(row.bone ?? ''), resource = bone?.userData.resourceKey as string | undefined;
            const packed = resource && (tris as Record<string, string>[])[i]?.[resource];
            if (!bone || !bone.visible || !packed) return;
            const id = `${muscle}:${i}:${resource}`;
            let mesh = this.contactNodes.get(id);
            if (!mesh) {
                mesh = new THREE.Mesh(triangleSubset(bone.geometry, decodeTriangles(packed)));
                mesh.matrixAutoUpdate = false; mesh.userData = { attachmentPatch: true, attachmentOf: muscle };
                this.contactNodes.set(id, mesh); this.scene.root.add(mesh);
            }
            mesh.material = this.materials.get('accessory', { variant: ATTACHMENT_VARIANT[row.role] });
            mesh.matrix.copy(bone.matrix); mesh.visible = true; wanted.add(id);
        });
        for (const [id, mesh] of this.contactNodes) if (!wanted.has(id)) { mesh.removeFromParent(); mesh.geometry.dispose(); this.contactNodes.delete(id); }
    }
    /** Pose the bones by joint angles (degrees per dof id), clamped to each dof's range; null returns to rest. */
    setRigPose(rig: RigFile, pose: RigPose | null) {
        const segmentOf = this.rigState?.file === rig ? this.rigState.segmentOf : boneSegments(rig);
        const clamped = pose && Object.values(pose).some(Boolean) ? clampPose(rig, pose) : null;
        this.rigState = { file: rig, segmentOf, transforms: clamped ? segmentTransforms(rig, clamped) : null };
        this.pose = clamped;
        for (const listener of this.poseListeners) listener(clamped);
        this.apply();
    }
    get rigPose() { return this.pose; }
    onRigPoseChange(listener: (pose: RigPose | null) => void) { this.poseListeners.add(listener); return () => { this.poseListeners.delete(listener); }; }
    loadRig() {
        this.rigFile ??= fetch('/__atlas/v2/rig.json').then(r => r.ok ? r.json() as Promise<RigFile> : Promise.reject(Error(String(r.status))));
        this.rigFile.catch(() => { this.rigFile = undefined; });
        return this.rigFile;
    }
    loadMuscleActions() {
        this.muscleActions ??= fetch('/__atlas/v2/actions.json').then(r => r.ok ? r.json() as Promise<MuscleActionsFile> : Promise.reject(Error(String(r.status))));
        this.muscleActions.catch(() => { this.muscleActions = undefined; });
        return this.muscleActions;
    }
    setActionHighlight(highlight: ActionHighlight) { this.actionHighlight = highlight; this.apply(); }
    openMovement(jointId: string) { for (const listener of this.openMovementListeners) listener(jointId); }
    onOpenMovement(listener: (jointId: string) => void) { this.openMovementListeners.add(listener); return () => { this.openMovementListeners.delete(listener); }; }
    setView(view: BodyView) {
        const nextContextKey = this.motionContextKey(view);
        if (this.motion && this.motion.contextKey !== nextContextKey) this.restoreSourceMotion('selection-or-view-changed');
        const wasObserving = Boolean(this.view.focusObservation || this.view.attachmentObservation);
        const observing = Boolean(view.focusObservation || view.attachmentObservation);
        const changedAttachment = this.view.attachmentObservation?.role !== view.attachmentObservation?.role;
        const changedSelection = this.view.selectedId !== view.selectedId;
        if (changedSelection || this.view.poseId !== view.poseId) for (const listener of this.sourceSelectionListeners) listener();
        const focusNerve = shouldFocusNerveSelection(this.integration.objects, this.view, view);
        if (wasObserving && (!observing || changedSelection)) this.scene.endObservation();
        this.view = view;
        if (observing && (!wasObserving || changedSelection || changedAttachment)) {
            this.scene.beginObservation(); this.focusSelection(true);
        }
        const keys = this.motion ? motionContextVisibility(
            [...this.motion.asset.sourceBinding?.members ?? [], ...this.motion.extraContextKeys.map(sourceKey => ({sourceKey, role:'co_moving_context'}))],
            this.motion.frameSourceKeys, key => this.records.get(key), view)
            : demandedStructureKeys(this.integration.objects, view);
        this.resources.demand(this.withPatches(keys), view.selectedId && keys.includes(view.selectedId) ? [view.selectedId] : []);
        this.apply();
        // Fit the initial deep link before the opening orbit captures its camera.
        if (focusNerve && !observing && !this.motion) this.focusSelection(this.resources.nodes.size > 0 && !this.scene.renderer.domElement.dataset.entrance);
    }
    private motionContextKey(view: BodyView): string {
        return JSON.stringify([view.regionIds ?? (view.region ? [view.region] : []), view.selectedId, view.bones, view.muscles,
            view.nerves, view.poseId, view.isolate, view.selectedPresentation, [...(view.hiddenSourceKeys ?? [])].sort(),
            [...(view.translucentSourceKeys ?? [])].sort(), view.dim, view.observeNerves, view.highlightInnervation, view.nerveConceptMuscleKeys, view.attachmentObservation]);
    }
    private readonly sourceSelectionListeners = new Set<() => void>();
    onSourceSelectionChange(listener: () => void) {
        this.sourceSelectionListeners.add(listener);
        return () => { this.sourceSelectionListeners.delete(listener); };
    }
    private readonly sourceMotionStartListeners = new Set<() => void>();
    onSourceMotionStart(listener: () => void) {
        this.sourceMotionStartListeners.add(listener);
        return () => { this.sourceMotionStartListeners.delete(listener); };
    }
    async attachSourceMotion(asset: MotionAsset, resource: AnimationSceneResource,
        onTimeChange?: AnimationPlaybackOptions['onTimeChange'], onInvalidated?: (reason: string) => void,
        presentation?: { intent: MotionLearningIntent }): Promise<AnimationPlaybackController> {
        for (const listener of this.sourceMotionStartListeners) listener();
        // Motion clips verify rest geometry and transforms: return any rig pose to rest first.
        if (this.rigState?.transforms) this.setRigPose(this.rigState.file, null);
        this.actionHighlight = null;
        this.scene.cancelCameraMotion();
        const zoom = asset.poseControl?.observationZoom ?? 1;
        if (!Number.isFinite(zoom) || zoom < 1 || zoom > 1.5) throw new Error('관찰 화면 확대 범위가 올바르지 않습니다.');
        this.restoreSourceMotion('replaced');
        this.motionIntent = presentation?.intent ?? 'posture_observation';
        const originalNodes = new Map<string, { node: THREE.Mesh; visible: boolean }>();
        const packageMaterials = new Map<string, THREE.Material | THREE.Material[]>();
        try {
            const binding = asset.sourceBinding;
            if (asset.representationType !== 'source_bound_surface' || !binding || asset.technicalStatus !== 'binding_verified')
                throw new Error('현재 장면에는 exact source-bound surface motion만 연결할 수 있습니다.');
            const dataset = this.resources.dataset;
            const frameContract = dataset.frameContract;
            const component = this.integration.sourceComponents?.[binding.datasetNamespace];
            const componentMatches = component
                ? component.datasetRevision === binding.datasetRevision
                    && component.integrationRevision === binding.integrationRevision && component.overlaySha256 === binding.sourceOverlaySha256
                    && (dataset.sourceRevisions?.[binding.datasetNamespace] ?? (dataset.namespace === binding.datasetNamespace ? dataset.revision : null)) === binding.datasetRevision
                : binding.datasetNamespace === dataset.namespace && binding.datasetRevision === dataset.revision
                    && binding.integrationRevision === this.integration.revision && binding.sourceOverlaySha256 === this.integration.sourceOverlaySha256;
            if (!componentMatches
                || binding.frameId !== frameContract?.targetFrameId || binding.frameId !== asset.staticBinding.frameId
                || binding.units !== dataset.unit || binding.referencePoseId !== frameContract?.staticReferencePose?.id
                || asset.staticBinding.modelId !== binding.datasetNamespace || asset.staticBinding.sceneRevision !== binding.datasetRevision
                || this.view.selectedId !== binding.subjectSourceKey || asset.staticBinding.side === 'bilateral'
                || (asset.staticBinding.side === 'midline' && binding.subjectKind !== 'bone')
                || asset.staticBinding.side === 'not_applicable') {
                throw new Error('motion의 dataset/revision/overlay/frame/unit/reference-pose가 현재 학습 장면과 다릅니다.');
            }
            const currentContextKey = this.motionContextKey(this.view);
            const baseKeys = demandedStructureKeys(this.integration.objects, this.view);
            const subject = this.records.get(binding.subjectSourceKey);
            const exactAttachmentKeys = !this.view.isolate && this.view.bones && subject
                ? attachmentBoneKeys(binding.subjectSourceKey, undefined, this.integration.objects).filter(key => {
                    const row = this.records.get(key);
                    return row?.kind === 'bone' && row.localDisplayEligible && row.defaultVisible && !row.hardHoldReasons.length
                        && !row.sourceHiddenStatePreserved.hideViewport && !this.view.hiddenSourceKeys?.includes(key)
                        && (row.side === subject.side || row.side === null || row.side === 'midline');
                })
                : [];
            const extraContextKeys = this.view.isolate ? [] : limbMotionContextKeys(asset, this.integration.objects, key => attachmentBoneKeys(key, 'origin').length && attachmentBoneKeys(key, 'insertion').length ? attachmentBoneKeys(key) : [])
                .filter(key => this.records.get(key)?.kind === 'bone' ? this.view.bones : this.view.muscles);
            const frameSourceKeys = this.view.isolate ? [binding.subjectSourceKey] : [...new Set([...motionFrameSourceKeys(
                binding.members, asset.poseControl?.framingSourceKeys, binding.subjectSourceKey,
                key => this.records.get(key)?.kind, exactAttachmentKeys,
            ), ...extraContextKeys])];
            const requiredKeys = [...new Set([...baseKeys, ...binding.members.map(member => member.sourceKey), ...frameSourceKeys])];
            const detailKeys = binding.members.filter(member => member.lod === 'detail').map(member => member.sourceKey);
            // An exact motion buffer may bind overview even for the selected bone.
            // Upgrading it to detail would make the required source hash unreachable.
            if (this.view.selectedId && !binding.members.some(m => m.sourceKey === this.view.selectedId)
                && !detailKeys.includes(this.view.selectedId)) detailKeys.push(this.view.selectedId);
            this.resources.demand(requiredKeys, detailKeys);
            const deadline = performance.now() + 15000;
            while (!binding.members.every(member => {
                const node = this.resources.nodes.get(member.sourceKey);
                return node?.userData.resourceKey === member.resourceKey;
            }) || !frameSourceKeys.every(key => this.resources.nodes.has(key))) {
                if (this.dead || this.motionContextKey(this.view) !== currentContextKey) throw new Error('motion context loading cancelled');
                if (performance.now() > deadline || this.resources.queue.failed.size) throw new Error('motion context resources unavailable');
                await new Promise(resolve => setTimeout(resolve, 40));
            }
            if (this.dead || this.motionContextKey(this.view) !== currentContextKey) throw new Error('motion context loading cancelled');
            // Prior selections may retain unused detail chunks. Keep live/pinned geometry,
            // but release that idle cache before admitting a larger existing motion package.
            this.resources.queue.trimUnused(DATASET_BUDGET.geometryBytes - resource.memoryEstimateBytes);
            if (this.resources.queue.bytes + resource.memoryEstimateBytes > DATASET_BUDGET.geometryBytes)
                throw new Error('현재 정적 자원과 motion 원본·형상·clip 버퍼가 함께 활성 장면 예산을 초과합니다.');
            const instances = new Map(dataset.instances.map(instance => [instance.sourceKey, instance]));
            const chunks = new Map(dataset.chunks.map(chunk => [chunk.id, chunk]));
            const seenSourceKeys = new Set<string>();
            let hasSubject = false;
            for (const member of binding.members) {
                if (seenSourceKeys.has(member.sourceKey)) throw new Error(`motion sourceKey가 중복되었습니다: ${member.sourceKey}`);
                seenSourceKeys.add(member.sourceKey);
                const instance = instances.get(member.sourceKey);
                const row = this.records.get(member.sourceKey);
                const chunk = instance && chunks.get(instance.lods[member.lod].chunk);
                const activeNode = this.resources.nodes.get(member.sourceKey);
                const motionNode = resource.sourceNodes.get(member.sourceKey);
                if (!instance || !row || !chunk || !activeNode || !motionNode || !(motionNode as THREE.Mesh).isMesh)
                    throw new Error(`현재 표시 장면 또는 source motion GLB에 고정 source instance가 없습니다: ${member.sourceKey}`);
                const namespace = instance.sourceNamespace ?? dataset.namespace;
                const lod = instance.lods[member.lod];
                if (namespace !== member.sourceNamespace || chunk.sha256 !== member.sourceChunkSha256
                    || lod.resource !== member.resourceKey || JSON.stringify(instance.matrix) !== JSON.stringify(member.instanceMatrix)
                    || row.side !== member.side || activeNode.userData.resourceKey !== member.resourceKey
                    || instance.lods[activeNode.userData.lod as 'overview' | 'detail']?.resource !== member.resourceKey || !row.localDisplayEligible || row.hardHoldReasons.length
                    || row.sourceHiddenStatePreserved.hideViewport || (member.role === 'deforming_muscle_surface' && row.kind !== 'muscle')) {
                    throw new Error(`sourceKey, side, resource/LOD, transform 또는 로컬 표시 근거가 현재 장면과 다릅니다: ${member.sourceKey}`);
                }
                if (member.sourceKey === binding.subjectSourceKey && (!(binding.subjectKind === 'bone' ? this.view.bones : this.view.muscles)
                    || this.view.hiddenSourceKeys?.includes(member.sourceKey) || this.view.selectedPresentation === 'hidden')) {
                    throw new Error(`motion source가 현재 선택/레이어/부위 보기에서 활성 상태가 아닙니다: ${member.sourceKey}`);
                }
                const [activeGeometryHash, motionGeometryHash] = await Promise.all([
                    sourceGeometrySha256(activeNode.geometry), sourceGeometrySha256((motionNode as THREE.Mesh).geometry),
                ]);
                if (activeGeometryHash !== member.geometrySha256 || motionGeometryHash !== member.geometrySha256)
                    throw new Error(`기본 geometry hash가 현재 장면과 derived motion 사이에 일치하지 않습니다: ${member.sourceKey}`);
                if (motionNode.parent !== resource.scene) throw new Error(`motion surface는 고정된 scene root의 직접 child여야 합니다: ${member.nodeId}`);
                if (member.sourceKey === binding.subjectSourceKey) {
                    if (binding.subjectKind === 'bone') {
                        if (row.kind !== 'bone' || !['moving_structure', 'fixed_structure'].includes(member.role)
                            || (member.side !== asset.staticBinding.side && !(asset.staticBinding.side === 'midline' && member.side === null)))
                            throw new Error('뼈 subject는 실제 같은 쪽 이동·고정 관절 구조여야 합니다.');
                        hasSubject = true;
                    } else {
                        if (row.kind !== 'muscle' || !['deforming_muscle_surface', 'deforming_passive_surface'].includes(member.role) || member.side !== asset.staticBinding.side)
                            throw new Error('근육 subject는 정확히 선택된 같은 쪽 변형 표면이어야 합니다.');
                        hasSubject = true;
                    }
                }
                const motionMesh = motionNode as THREE.Mesh;
                const activeMatrix = new THREE.Matrix4().fromArray(member.instanceMatrix);
                if (member.role === 'moving_structure' || member.role === 'co_moving_context') {
                    activeMatrix.decompose(motionMesh.position, motionMesh.quaternion, motionMesh.scale);
                    motionMesh.matrixAutoUpdate = true;
                    motionMesh.updateMatrix();
                } else {
                    motionMesh.matrix.copy(activeMatrix); motionMesh.matrixAutoUpdate = false;
                }
                motionMesh.matrixWorldNeedsUpdate = true;
                motionMesh.userData.sourceKey = member.sourceKey;
                motionMesh.userData.sourceName = instance.sourceName;
                originalNodes.set(member.sourceKey, { node: activeNode, visible: activeNode.visible });
                packageMaterials.set(member.sourceKey, Array.isArray(motionMesh.material) ? [...motionMesh.material] : motionMesh.material);
            }
            if (!hasSubject) throw new Error('선택 근육의 exact sourceKey/side 변형 표면이 manifest에 없습니다.');
            if (!binding.members.some(member => member.sourceKey === binding.subjectSourceKey
                && (member.side === asset.staticBinding.side || (binding.subjectKind === 'bone' && asset.staticBinding.side === 'midline' && member.side === null))))
                throw new Error('선택 sourceKey/side가 motion package에 없습니다.');
            // A static observation may have opened while the motion resource was loading.
            for (const listener of this.sourceMotionStartListeners) listener();
            this.scene.root.add(resource.scene);
            for (const sourceKey of binding.members.map(row => row.sourceKey)) {
                const original = originalNodes.get(sourceKey)!;
                const motionNode = resource.sourceNodes.get(sourceKey) as THREE.Mesh;
                original.node.visible = false;
                this.resources.nodes.set(sourceKey, motionNode);
                this.resources.motionOverrides.add(sourceKey);
            }
            const boneFollowers = contextBoneFollowers(asset, extraContextKeys, key => this.records.get(key)).map(follower => {
                const node = this.resources.nodes.get(follower.sourceKey)!;
                const anchor = resource.sourceNodes.get(follower.anchorSourceKey)!;
                return { node, rest: node.matrix.clone(), anchor, anchorRestInverse: anchor.matrix.clone().invert() };
            });
            const player = new AnimationPlaybackController(resource, asset.clip.id, {
                repeat: true, pingPong: true,
                actionDirection: asset.poseControl?.actionDirection,
                returnSpeed: this.motionIntent === 'muscle_action' && asset.poseControl?.actionDirection !== 'reverse' ? 1.7 : 1,
                onTimeChange: (time, completed) => {
                    for (const follower of boneFollowers) {
                        follower.anchor.updateMatrix();
                        followContextBone(follower.rest, follower.anchorRestInverse, follower.anchor.matrix, follower.node.matrix);
                        follower.node.updateMatrixWorld(true);
                    }
                    const activePose = time > 1e-6;
                    const phase = player.phase;
                    if (this.motionPoseActive !== activePose || this.motionPhase !== phase) {
                        this.motionPoseActive = activePose; this.motionPhase = phase; this.apply();
                    }
                    if (this.motionIntent === 'muscle_action' && asset.sourceBinding?.subjectSourceKey === this.view.selectedId) {
                        const node = this.resources.nodes.get(asset.sourceBinding.subjectSourceKey);
                        const fraction = time / player.durationSeconds;
                        const emphasis = muscleActionEmphasis(phase, asset.poseControl?.actionDirection === 'reverse' ? 1 - fraction : fraction);
                        if (emphasis !== null && node?.material instanceof THREE.MeshStandardMaterial) {
                            node.material.color.copy(this.returnTone).lerp(this.actionTone, emphasis);
                        }
                    }
                    // Scrubbing within the same phase must also paint the new pose.
                    // The host skips draw calls while the shared player is held.
                    this.scene.requestRender();
                    onTimeChange?.(time, completed);
                }, disposeResource: false,
                registerUpdate: update => this.scene.addUpdate(update),
            });
            this.motion = { asset, resource, player, originals: originalNodes, packageMaterials, contextKey: currentContextKey, frameSourceKeys, extraContextKeys, boneFollowers, onInvalidated };
            this.scene.renderer.domElement.parentElement?.setAttribute('data-motion-context', 'active');
            this.apply();
            // Frame the complete moving chain once, retaining the user's viewing direction.
            this.scene.beginObservation('motion');
            // Playback, scrubbing and restoration never continually refit or reset the camera.
            const defaultFront = this.scene.camera.position.clone().sub(this.scene.controls.target).normalize();
            // A straight frontal default hides sagittal motion in depth. Establish an
            // oblique teaching view once; retain any already chosen non-default view.
            const untouchedFront = defaultFront.z > .999 && Math.abs(defaultFront.x) < .01 && Math.abs(defaultFront.y) < .01;
            const previousGuideRetained = this.guidedMotionDirection !== null && defaultFront.dot(this.guidedMotionDirection) > .9999;
            if (asset.poseControl?.observationDirection && (untouchedFront || previousGuideRetained)) {
                const observation = new THREE.Vector3(...asset.poseControl.observationDirection);
                if (Number.isFinite(observation.lengthSq()) && observation.lengthSq() > .01) {
                    this.scene.camera.position.copy(this.scene.controls.target).add(observation.normalize());
                    this.guidedMotionDirection = observation.clone();
                }
            } else if (asset.poseControl?.actionDirection === 'reverse' && defaultFront.z > .999
                && Math.abs(defaultFront.x) < .01 && Math.abs(defaultFront.y) < .01) {
                this.scene.camera.position.copy(this.scene.controls.target).add(new THREE.Vector3(.866, 0, .5));
            }
            this.fit(frameSourceKeys.map(key => this.records.get(key)!).filter(row => row && row.localDisplayEligible
                && !row.hardHoldReasons.length && !row.sourceHiddenStatePreserved.hideViewport
                && (row.kind === 'bone' ? this.view.bones : this.view.muscles)
                && !this.view.hiddenSourceKeys?.includes(row.sourceKey)
                && (row.defaultVisible || row.sourceKey === this.view.selectedId)), 1.05);
            this.scene.camera.zoom = zoom;
            this.scene.camera.updateProjectionMatrix();
            this.scene.requestRender();
            this.apply();
            return player;
        } catch (error) {
            for (const [sourceKey, original] of originalNodes) {
                const motionNode = resource.sourceNodes.get(sourceKey) as THREE.Mesh | undefined;
                const originalMaterial = packageMaterials.get(sourceKey);
                if (motionNode && originalMaterial) motionNode.material = originalMaterial;
                this.resources.nodes.set(sourceKey, original.node);
                this.resources.motionOverrides.delete(sourceKey);
                original.node.visible = original.visible;
                if (!original.node.parent) this.scene.root.add(original.node);
            }
            resource.dispose();
            if (!this.dead) {
                const keys = demandedStructureKeys(this.integration.objects, this.view);
                this.resources.demand(this.withPatches(keys), this.view.selectedId ? [this.view.selectedId] : []);
                this.apply();
            }
            throw error;
        }
    }
    restoreSourceMotion(reason = 'restored') {
        const active = this.motion;
        if (!active) return;
        this.motion = null;
        this.scene.endObservation('motion', false);
        this.scene.renderer.domElement.parentElement?.removeAttribute('data-motion-context');
        this.motionPoseActive = false;
        this.motionPhase = 'rest';
        active.player.resetPose();
        active.player.dispose();
        for (const follower of active.boneFollowers) {
            follower.node.matrix.copy(follower.rest);
            follower.node.updateMatrixWorld(true);
        }
        for (const [sourceKey, original] of active.originals) {
            const motionNode = active.resource.sourceNodes.get(sourceKey) as THREE.Mesh | undefined;
            const originalMaterial = active.packageMaterials.get(sourceKey);
            if (motionNode && originalMaterial) motionNode.material = originalMaterial;
            this.resources.nodes.set(sourceKey, original.node);
            this.resources.motionOverrides.delete(sourceKey);
            original.node.visible = original.visible;
            if (!original.node.parent) this.scene.root.add(original.node);
        }
        active.resource.dispose();
        active.onInvalidated?.(reason);
        const keys = demandedStructureKeys(this.integration.objects, this.view);
        this.resources.demand(this.withPatches(keys), this.view.selectedId ? [this.view.selectedId] : []);
        this.apply();
    }
    /** The selected muscle's attachment patches, when bones are shown; fetches the patch table on first use. */
    private selectedAttachments(): AttachmentRow[] {
        const id = this.view.selectedId;
        if (!id || this.records.get(id)?.kind !== 'muscle' || !this.view.bones || this.motion) return [];
        if (this.attachments === null) this.loadAttachments();
        return typeof this.attachments === 'object' && this.attachments ? this.attachments.muscles[id] ?? [] : [];
    }
    private selectedPatches() { return this.selectedAttachments().filter((p): p is AttachmentRow & { key: string } => Boolean(p.key)); }
    private withPatches(keys: string[]) {
        const patches = this.selectedPatches().map(p => p.key);
        return patches.length ? [...keys, ...patches] : keys;
    }
    private loadAttachments() {
        this.attachments = 'loading';
        fetch('/__atlas/v2/attachments.json').then(r => r.ok ? r.json() : Promise.reject(Error(String(r.status)))).then(file => {
            this.attachments = file;
            for (const rows of Object.values(file.muscles) as AttachmentRow[][])
                for (const p of rows) if (p.key) { this.patchRole.set(p.key, { role: p.role, bone: p.bone }); this.displayKeys.add(p.key); }
            if (!this.dead) this.setView(this.view);
        }).catch(() => { this.attachments = 'failed'; });
    }
    private apply() {
        if (this.dead)
            return;
        const rows = this.integration.objects;
        const visibleKeys = new Set(demandedStructureKeys(rows, this.view));
        // Motion context may cross region boundaries, but never overrides user layer/hidden choices.
        if (this.motion) {
            visibleKeys.clear();
            const contextMembers = [...this.motion.asset.sourceBinding?.members ?? [], ...this.motion.extraContextKeys.map(sourceKey => ({sourceKey, role:'co_moving_context'}))];
            for (const key of motionContextVisibility(contextMembers, this.motion.frameSourceKeys,
                key => this.records.get(key), this.view)) visibleKeys.add(key);
        }
        const course = new Set(nerveCourseKeys(rows, this.view));
        const attachmentBones = new Set(attachmentObservationKeys(rows, this.view));
        const highlights = new Set(innervationHighlightKeys(rows, this.view, visibleKeys));
        const observe = observingNerves(rows, this.view, visibleKeys);
        const selectionAlternativeKeys = new Set(this.records.get(this.view.selectedId ?? '')?.selectionSuppressSourceKeys ?? []);
        const attachmentRows = this.selectedAttachments();
        const shownPatches = new Set(this.selectedPatches().map(p => p.key));
        for (const [key, node] of this.resources.nodes) {
            const row = this.records.get(key)!;
            const patch = this.patchRole.get(key);
            if (patch) {
                node.visible = shownPatches.has(key) && !this.view.hiddenSourceKeys?.includes(patch.bone ?? '');
                node.userData.attachmentPatch = true;
                node.material = this.materials.get('accessory', { variant: ATTACHMENT_VARIANT[patch.role] });
                continue;
            }
            const selected = key === this.view.selectedId;
            const motionContextOpacity = this.motion?.asset.poseControl?.contextOpacity;
            node.visible = visibleKeys.has(key) && !(this.motionPoseActive && row.kind === 'nerve') && !this.view.hiddenSourceKeys?.includes(key) && !selectionAlternativeKeys.has(key) && !(selected && this.view.selectedPresentation === 'hidden');
            const observedRole = attachmentBones.has(key) ? this.view.attachmentObservation!.role : null;
            const drawnArea = observedRole && attachmentRows.some(r => r.bone === key && r.role === observedRole);
            const attachmentMode = observedRole ? observedRole === 'origin' ? drawnArea ? 'originAreaContext' : 'originContext'
                : drawnArea ? 'insertionAreaContext' : 'insertionContext' : null;
            // While observing its attachments, the selected muscle is see-through so the drawn areas under it show.
            const observingAreas = selected && this.view.attachmentObservation && attachmentRows.length > 0;
            const mode: MaterialMode = attachmentMode ?? (this.view.translucentSourceKeys?.includes(key) || observingAreas || selected && this.view.selectedPresentation === 'translucent' ? 'translucent'
                : selected || course.has(key) || key === this.quizTarget ? 'selected'
                // Quiz: the target may lie under muscles or bone, so everything else turns see-through (bones less so).
                : this.quizTarget && !this.view.selectedId ? row.kind === 'bone' ? 'translucent' : 'observationContext' : observe && row.kind !== 'nerve' ? highlights.has(key) ? 'motorContext' : 'nerveContext'
                : highlights.has(key) ? 'innervated' : this.view.focusObservation && row.kind === 'muscle' ? 'observationContext' : this.motion?.originals.has(key) ? row.kind === 'muscle' && motionContextOpacity != null ? 'motionContext' : 'normal' : this.view.selectedId && this.view.dim || this.quizTarget ? 'dim' : 'normal');
            const actionPhase = selected && row.kind === 'muscle' && this.motion && this.motionIntent === 'muscle_action'
                && this.motion.asset.sourceBinding?.subjectSourceKey === key ? this.motionPhase : null;
            const phaseTone = actionPhase === 'action' ? 'action' : actionPhase === 'return' ? 'return' : null;
            const layerId = layerIdOf(row);
            const highlight = this.motion || !this.actionHighlight || selected ? undefined
                : this.actionHighlight.agonists.includes(key) ? 'agonist' as const : this.actionHighlight.antagonists.includes(key) ? 'antagonist' as const : undefined;
            // Shown movers stay coloured even while the rest is dimmed around a selection.
            const material = this.materials.get(row.kind, { mode: highlight && mode === 'dim' ? 'normal' : mode, phase: phaseTone, role: highlight, contextOpacity: motionContextOpacity, userTranslucent: Boolean(attachmentMode && this.view.translucentSourceKeys?.includes(key)),
                variant: row.tissue, layerOpacity: layerId ? this.view.layerOpacity?.[layerId] : undefined });
            node.material = material;
            node.userData.nerveObservationContext = observe && row.kind !== 'nerve';
        }
        if (this.rigState && !this.motion) {
            const { segmentOf, transforms } = this.rigState;
            for (const [key, node] of this.resources.nodes) {
                const segment = segmentOf.get(key) ?? segmentOf.get(this.patchRole.get(key)?.bone ?? ''); if (!segment) continue;
                node.matrix.fromArray(node.userData.instanceMatrix);
                const posed = transforms?.get(segment); if (posed) node.matrix.premultiply(posed);
            }
            this.skinSoftTissue();
        }
        this.syncContactAreas();
        const selectedNode = this.view.selectedId ? this.resources.nodes.get(this.view.selectedId) : this.quizTarget ? this.resources.nodes.get(this.quizTarget) : undefined;
        this.scene.setOutline(selectedNode?.visible && !this.motion ? [selectedNode] : []);
        this.scene.requestRender();
        const q = this.resources.queue;
        const wanted = [...q.wanted];
        this.notify({ loaded: wanted.filter(x => q.loaded.has(x)).length, total: wanted.length, failed: wanted.filter(x => q.failed.has(x)).length,
            contextLost: this.contextLost, selectedAvailable: !this.view.selectedId || this.resources.nodes.has(this.view.selectedId), calls: this.resources.nodes.size,
            triangles: this.scene.renderer.info.render.triangles, geometries: this.scene.renderer.info.memory.geometries });
        this.scene.renderer.domElement.dataset.dataset = JSON.stringify({ root: this.scene.root.uuid, dataset: this.resources.dataset.namespace,
            regionIds: this.view.regionIds ?? (this.view.region ? [this.view.region] : []), highlighted: [...highlights], observingNerves: observe, focusObservation: Boolean(this.view.focusObservation), attachmentObservation: this.view.attachmentObservation ?? null, attachmentBones: [...attachmentBones], hidden: this.view.hiddenSourceKeys ?? [], translucent: this.view.translucentSourceKeys ?? [], nerveLayer: Boolean(this.view.nerves), poseId: this.view.poseId, visible: [...this.resources.nodes].filter(([, n]) => n.visible).map(([key]) => key), selected: this.view.selectedId, bytes: q.bytes, cacheEntries: q.loaded.size, evictions: q.evictions, cancellations: q.cancellations, lateReleases: q.lateReleases, wantedChunks: [...q.wanted], pending: q.pending.size, failed: [...q.failed],
            camera: this.scene.camera.position.toArray(), cameraTarget: this.scene.controls.target.toArray(), cameraZoom: this.scene.camera.zoom, cameraAspect: this.scene.camera.aspect, cameraFov: this.scene.camera.fov, calls: this.scene.renderer.info.render.calls, triangles: this.scene.renderer.info.render.triangles,
            motion: this.motion ? { assetId: this.motion.asset.id, contextKey: this.motion.contextKey,
                learningIntent: this.motionIntent, phase: this.motionPhase,
                surfaceCount: this.motion.originals.size, fixedCount: this.motion.asset.sourceBinding?.members.filter(m => m.role === 'fixed_structure').length } : null,
            contextBoneFollowers: this.motion?.boneFollowers.map(follower => ({sourceKey:follower.node.userData.sourceKey, matrix:follower.node.matrix.toArray(), rest:follower.rest.toArray()})) ?? [],
            motionBytes: this.motion?.resource.memoryEstimateBytes ?? 0, estimatedActiveBytes: q.bytes + (this.motion?.resource.memoryEstimateBytes ?? 0) });
    }
    private fit(rows: RuntimeStructureRecord[], padding = 1.25, smooth = true) {
        const box = new THREE.Box3();
        for (const r of rows) {
            box.expandByPoint(new THREE.Vector3().fromArray(r.bounds[0]));
            box.expandByPoint(new THREE.Vector3().fromArray(r.bounds[1]));
        }
        if (box.isEmpty())
            return;
        this.scene.fitObservationBounds(box, padding, smooth);
    }
    focus(regions: string[], smooth = true) { this.fit(framingRecords(this.integration.objects, this.view, regions), 1.25, smooth); }
    focusSelection(smooth = true) {
        const keys = this.motion ? this.motion.frameSourceKeys : observationFrameKeys(this.integration.objects, this.view);
        const box = new THREE.Box3();
        for (const key of keys) {
            const row = this.records.get(key); if (!row || this.view.hiddenSourceKeys?.includes(key)) continue;
            box.expandByPoint(new THREE.Vector3().fromArray(row.bounds[0])); box.expandByPoint(new THREE.Vector3().fromArray(row.bounds[1]));
        }
        // Include the actual current moving surfaces, not only their frozen rest bounds.
        if (this.motion) box.union(new THREE.Box3().setFromObject(this.motion.resource.scene));
        this.scene.fitObservationBounds(box, 1.25, smooth);
    }
    retry() { this.resources.queue.retry(); }
    get section() { return this.sectionState?.section ?? null; }
    setQuizTarget(key: string | null) {
        this.quizTarget = key; this.apply();
        const row = key ? this.records.get(key) : undefined;
        if (!row) return;
        // Frame at least 30 cm around the target so a small muscle is shown in its body region.
        const box = new THREE.Box3(new THREE.Vector3().fromArray(row.bounds[0]), new THREE.Vector3().fromArray(row.bounds[1]));
        const size = box.getSize(new THREE.Vector3()), centre = box.getCenter(new THREE.Vector3());
        box.setFromCenterAndSize(centre, size.max(new THREE.Vector3(.3, .3, .3)));
        this.scene.fitObservationBounds(box, 1.25, true);
    }
    /** Selectable structures drawn right now (layer on, not hidden, not cut away by a section). */
    visibleQuizKeys() {
        const plane = this.sectionState?.plane ?? null;
        return [...this.resources.nodes].filter(([key, node]) => node.visible && !node.userData.attachmentPatch && this.records.get(key)?.inspectionEligible
            && keptBySection(plane, new THREE.Vector3().fromArray(this.records.get(key)!.bounds[0]).add(new THREE.Vector3().fromArray(this.records.get(key)!.bounds[1])).multiplyScalar(.5)))
            .map(([key]) => key);
    }
    /** Extent of every displayable structure: the section slider runs across it. */
    sectionBounds(): Bounds {
        const box = new THREE.Box3();
        for (const r of this.records.values()) if (r.localDisplayEligible) { box.expandByPoint(new THREE.Vector3().fromArray(r.bounds[0])); box.expandByPoint(new THREE.Vector3().fromArray(r.bounds[1])); }
        return [box.min.toArray(), box.max.toArray()];
    }
    setSection(section: Section | null) {
        const plane = section ? sectionPlane(section, this.sectionBounds()) : null;
        this.sectionState = section && plane ? { section, plane } : null;
        this.scene.renderer.clippingPlanes = plane ? [plane] : [];
        this.materials.setSectioned(Boolean(plane));
        this.scene.requestRender();
    }
    /** Turn the camera to look straight at the cut face, keeping the current distance. */
    faceSection() {
        const plane = this.sectionState?.plane; if (!plane) return;
        const { camera, controls } = this.scene;
        this.scene.cancelCameraMotion();
        const target = plane.projectPoint(controls.target, new THREE.Vector3());
        const distance = camera.position.distanceTo(controls.target);
        controls.target.copy(target);
        camera.position.copy(target).addScaledVector(sectionViewDirection(plane), distance);
        camera.lookAt(target); controls.update(); this.scene.requestRender();
    }
    private onKey = (e: KeyboardEvent) => { if (e.key === 'Home') {
        e.preventDefault();
        e.stopImmediatePropagation();
        this.focus(this.view.regionIds ?? (this.view.region ? [this.view.region] : []));
    } };
    private onDown = (e: PointerEvent) => { this.down = { x: e.clientX, y: e.clientY }; };
    private onUp = (e: PointerEvent) => {
        if (e.button !== 0 || Math.hypot(e.clientX - this.down.x, e.clientY - this.down.y) > 5)
            return;
        const rect = this.scene.renderer.domElement.getBoundingClientRect();
        const nodes = [...this.resources.nodes.values()].filter(n => n.visible && !n.userData.attachmentPatch);
        const observe = nodes.some(n => n.userData.nerveObservationContext);
        const plane = this.sectionState?.plane ?? null;
        const hit = pickSurface(this.scene.camera, nodes, { x: e.clientX, y: e.clientY }, rect, observe, point => keptBySection(plane, point));
        if (!hit)
            return;
        const row = this.records.get(String(hit.object.userData.sourceKey ?? hit.object.name));
        if (row?.inspectionEligible)
            this.select(row.sourceKey, row.side);
    };
    dispose() { if (this.dead)
        return; this.restoreSourceMotion('viewer-unmounted'); this.dead = true; const canvas = this.scene.renderer.domElement; canvas.removeEventListener('keydown', this.onKey, true); canvas.removeEventListener('pointerdown', this.onDown); canvas.removeEventListener('pointerup', this.onUp); this.resources.dispose(); this.materials.dispose(); this.scene.dispose(); }
}
