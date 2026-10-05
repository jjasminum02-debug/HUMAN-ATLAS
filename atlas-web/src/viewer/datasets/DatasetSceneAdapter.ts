import * as THREE from 'three';
import { demandedStructureKeys, innervationHighlightKeys, observingNerves } from './presentation.ts';
import { AnatomySceneController, type BodyProgress } from '../wholeBody/AnatomySceneController.ts';
import type { BodyManifest, BodyView } from '../wholeBody/contract.ts';
import { DatasetResources } from './DatasetResources.ts';
import { framingRecords } from './framing.ts';
import { pickSurface } from './surfacePicking.ts';
import type { Dataset } from './schema.ts';
import { DATASET_BUDGET } from './schema.ts';
import { validateRuntimeIntegration, type RuntimeIntegration, type RuntimeStructureRecord } from './integration.ts';
import { AnimationPlaybackController, type AnimationPlaybackOptions } from '../animationPlayback.ts';
import type { AnimationSceneResource } from '../animationSceneAdapter.ts';
import type { MotionAsset } from '../../domain/motionLearning.ts';
import { sourceGeometrySha256 } from './sourceMotionGeometry.ts';
import type { SourceMotionHost } from './sourceMotionHost.ts';
import { muscleActionEmphasis } from "../../domain/atlasMotionExperience.ts";
import type { MotionLearningIntent } from '../../domain/atlasMotionExperience.ts';
/** Dataset selection/presentation adapter; renderer, camera and lifecycle remain owned by the existing controller. */
export class DatasetSceneAdapter implements SourceMotionHost {
    readonly scene: AnatomySceneController;
    readonly resources: DatasetResources;
    readonly integration: RuntimeIntegration;
    readonly records: Map<string, RuntimeStructureRecord>;
    private view: BodyView = { region: null, regionIds: [], bones: true, muscles: true, supplements: false, selectedId: null, dim: true };
    private materials = new Map<string, THREE.MeshStandardMaterial>();
    private down = { x: 0, y: 0 };
    private dead = false;
    private contextLost = false;
    private motionPoseActive = false;
    private readonly actionTone = new THREE.Color('#bd5047');
    private motionPhase: AnimationPlaybackController['phase'] = 'rest';
    private motionIntent: MotionLearningIntent = 'posture_observation';
    private guidedMotionDirection: THREE.Vector3 | null = null;
    private notify: (p: BodyProgress) => void;
    private select: (id: string, side: string | null) => void;
    private motion: { asset: MotionAsset; resource: AnimationSceneResource; player: AnimationPlaybackController; originals: Map<string, { node: THREE.Mesh; visible: boolean }>; packageMaterials: Map<string, THREE.Material | THREE.Material[]>; contextKey: string; onInvalidated?: (reason: string) => void } | null = null;
    constructor(host: HTMLElement, dataset: Dataset, integration: RuntimeIntegration, notify: (p: BodyProgress) => void, select: (id: string, side: string | null) => void) {
        validateRuntimeIntegration(integration, dataset);
        this.notify = notify;
        this.select = select;
        this.integration = integration;
        this.records = new Map(integration.objects.map(r => [r.sourceKey, r]));
        const empty = { version: 2, localOnly: true, publicRedistribution: 'held', frame: 'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR', unit: 'm', lodLevels: 1, chunks: [] } as BodyManifest;
        this.scene = new AnatomySceneController(host, empty, p => { if (this.contextLost !== p.contextLost) {
            this.contextLost = p.contextLost;
            if (this.contextLost) this.restoreSourceMotion('webgl-context-lost');
            if (this.resources)
                this.apply();
        } }, () => { });
        this.resources = new DatasetResources(dataset, this.scene.root, false, () => this.apply(), new Set(integration.objects.filter(r => r.localDisplayEligible).map(r => r.sourceKey)));
        const canvas = this.scene.renderer.domElement;
        canvas.addEventListener('keydown', this.onKey, true);
        canvas.addEventListener('pointerdown', this.onDown);
        canvas.addEventListener('pointerup', this.onUp);
        this.setView(this.view);
        this.focus([]);
    }
    setView(view: BodyView) {
        const nextContextKey = this.motionContextKey(view);
        if (this.motion && this.motion.contextKey !== nextContextKey) this.restoreSourceMotion('selection-or-view-changed');
        this.view = view;
        const keys = demandedStructureKeys([...this.records.values()], view);
        this.resources.demand(keys, view.selectedId && keys.includes(view.selectedId) ? [view.selectedId] : []);
        this.apply();
    }
    private motionContextKey(view: BodyView): string {
        return JSON.stringify([view.regionIds ?? (view.region ? [view.region] : []), view.selectedId, view.bones, view.muscles,
            view.nerves, view.poseId, view.isolate, view.selectedPresentation, [...(view.hiddenSourceKeys ?? [])].sort(),
            [...(view.translucentSourceKeys ?? [])].sort(), view.dim, view.observeNerves, view.highlightInnervation, view.nerveConceptMuscleKeys]);
    }
    async attachSourceMotion(asset: MotionAsset, resource: AnimationSceneResource,
        onTimeChange?: AnimationPlaybackOptions['onTimeChange'], onInvalidated?: (reason: string) => void,
        presentation?: { intent: MotionLearningIntent }): Promise<AnimationPlaybackController> {
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
                || asset.staticBinding.side === 'midline' || asset.staticBinding.side === 'not_applicable') {
                throw new Error('motion의 dataset/revision/overlay/frame/unit/reference-pose가 현재 학습 장면과 다릅니다.');
            }
            const currentContextKey = this.motionContextKey(this.view);
            const baseKeys = demandedStructureKeys([...this.records.values()], this.view);
            const requiredKeys = [...new Set([...baseKeys, ...binding.members.map(member => member.sourceKey)])];
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
            })) {
                if (this.dead || this.motionContextKey(this.view) !== currentContextKey) throw new Error('motion context loading cancelled');
                if (performance.now() > deadline || this.resources.queue.failed.size) throw new Error('motion context resources unavailable');
                await new Promise(resolve => setTimeout(resolve, 40));
            }
            if (this.dead || this.motionContextKey(this.view) !== currentContextKey) throw new Error('motion context loading cancelled');
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
                        if (row.kind !== 'bone' || !['moving_structure', 'fixed_structure'].includes(member.role) || member.side !== asset.staticBinding.side)
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
            if (!binding.members.some(member => member.sourceKey === binding.subjectSourceKey && member.side === asset.staticBinding.side))
                throw new Error('선택 sourceKey/side가 motion package에 없습니다.');
            this.scene.root.add(resource.scene);
            for (const sourceKey of binding.members.map(row => row.sourceKey)) {
                const original = originalNodes.get(sourceKey)!;
                const motionNode = resource.sourceNodes.get(sourceKey) as THREE.Mesh;
                original.node.visible = false;
                this.resources.nodes.set(sourceKey, motionNode);
                this.resources.motionOverrides.add(sourceKey);
            }
            const player = new AnimationPlaybackController(resource, asset.clip.id, {
                repeat: true, pingPong: true,
                actionDirection: asset.poseControl?.actionDirection,
                returnSpeed: this.motionIntent === 'muscle_action' && asset.poseControl?.actionDirection !== 'reverse' ? 1.7 : 1,
                onTimeChange: (time, completed) => {
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
                            node.material.color.set('#a4aaa8').lerp(this.actionTone, emphasis);
                        }
                    }
                    onTimeChange?.(time, completed);
                }, disposeResource: false,
                registerUpdate: update => this.scene.addUpdate(update),
            });
            this.motion = { asset, resource, player, originals: originalNodes, packageMaterials, contextKey: currentContextKey, onInvalidated };
            this.scene.renderer.domElement.parentElement?.setAttribute('data-motion-context', 'active');
            this.apply();
            // Frame the complete moving chain once, retaining the user's viewing direction.
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
            const framingKeys = asset.poseControl?.framingSourceKeys?.filter(key => binding.members.some(member => member.sourceKey === key));
            this.fit(binding.members.filter(m => !framingKeys?.length || framingKeys.includes(m.sourceKey)).map(m => this.records.get(m.sourceKey)!).filter(row => row
                && (row.kind === 'bone' ? this.view.bones : this.view.muscles)
                && !this.view.hiddenSourceKeys?.includes(row.sourceKey)), 1.05);
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
                const keys = demandedStructureKeys([...this.records.values()], this.view);
                this.resources.demand(keys, this.view.selectedId ? [this.view.selectedId] : []);
                this.apply();
            }
            throw error;
        }
    }
    restoreSourceMotion(reason = 'restored') {
        const active = this.motion;
        if (!active) return;
        this.motion = null;
        this.scene.renderer.domElement.parentElement?.removeAttribute('data-motion-context');
        this.motionPoseActive = false;
        this.motionPhase = 'rest';
        active.player.resetPose();
        active.player.dispose();
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
        const keys = demandedStructureKeys([...this.records.values()], this.view);
        this.resources.demand(keys, this.view.selectedId ? [this.view.selectedId] : []);
        this.apply();
    }
    private apply() {
        if (this.dead)
            return;
        const rows = [...this.records.values()];
        const visibleKeys = new Set(demandedStructureKeys(rows, this.view));
        // Motion context may cross region boundaries, but never overrides user layer/hidden choices.
        if (this.motion && !this.view.isolate) visibleKeys.clear();
        if (this.motion && !this.view.isolate) for (const member of this.motion.asset.sourceBinding?.members ?? []) {
            const row = this.records.get(member.sourceKey);
            if (row && (row.kind === 'bone' ? this.view.bones : this.view.muscles)) visibleKeys.add(member.sourceKey);
        }
        const highlights = new Set(innervationHighlightKeys(rows, this.view, visibleKeys));
        const observe = observingNerves(rows, this.view, visibleKeys);
        const selectionAlternativeKeys = new Set(this.records.get(this.view.selectedId ?? '')?.selectionSuppressSourceKeys ?? []);
        for (const [key, node] of this.resources.nodes) {
            const row = this.records.get(key)!;
            const selected = key === this.view.selectedId;
            const motionContextOpacity = this.motion?.asset.poseControl?.contextOpacity;
            node.visible = visibleKeys.has(key) && !(this.motionPoseActive && row.kind === 'nerve') && !this.view.hiddenSourceKeys?.includes(key) && !selectionAlternativeKeys.has(key) && !(selected && this.view.selectedPresentation === 'hidden');
            const mode = this.view.translucentSourceKeys?.includes(key) || selected && this.view.selectedPresentation === 'translucent' ? 'translucent'
                : selected ? 'selected' : observe && row.kind !== 'nerve' ? highlights.has(key) ? 'motorContext' : 'nerveContext'
                : highlights.has(key) ? 'innervated' : this.motion?.originals.has(key) ? row.kind === 'muscle' && motionContextOpacity != null ? 'motionContext' : 'normal' : this.view.selectedId && this.view.dim ? 'dim' : 'normal';
            const actionPhase = selected && row.kind === 'muscle' && this.motion && this.motionIntent === 'muscle_action'
                && this.motion.asset.sourceBinding?.subjectSourceKey === key ? this.motionPhase : null;
            const phaseTone = actionPhase === 'action' ? 'action' : actionPhase === 'return' ? 'return' : null;
            const materialKey = row.kind + ':' + mode + (mode === 'motionContext' ? ':' + motionContextOpacity : '') + (phaseTone ? ':' + phaseTone : '');
            let material = this.materials.get(materialKey);
            if (!material) {
                const color = new THREE.Color(mode === 'selected' ? row.kind === 'nerve' ? '#208b3a' : '#18776d' : mode === 'innervated' || mode === 'motorContext' ? '#338fc1' : row.kind === 'nerve' ? '#d7ac20' : row.kind === 'bone' ? '#e7dec7' : '#b87969');
                if (phaseTone === 'action') color.set('#bd5047');
                else if (phaseTone === 'return') color.set('#a4aaa8');
                if (mode === 'dim' && row.kind !== 'nerve')
                    color.lerp(new THREE.Color('#e5e5dd'), .55);
                const transparent = ['translucent', 'nerveContext', 'motorContext', 'motionContext'].includes(mode);
                material = new THREE.MeshStandardMaterial({ color, roughness: .76, transparent,
                    opacity: mode === 'motionContext' ? Math.max(.1, Math.min(.6, motionContextOpacity!)) : mode === 'nerveContext' ? .12 : mode === 'motorContext' ? .82 : mode === 'translucent' ? .3 : 1,
                    depthWrite: !transparent, depthTest: true,
                    emissive: row.kind === 'nerve' ? color : '#000000', emissiveIntensity: row.kind === 'nerve' ? .22 : 0 });
                this.materials.set(materialKey, material);
            }
            node.material = material;
            node.userData.nerveObservationContext = observe && row.kind !== 'nerve';
        }
        this.scene.requestRender();
        const q = this.resources.queue;
        const wanted = [...q.wanted];
        this.notify({ loaded: wanted.filter(x => q.loaded.has(x)).length, total: wanted.length, failed: wanted.filter(x => q.failed.has(x)).length,
            contextLost: this.contextLost, selectedAvailable: !this.view.selectedId || this.resources.nodes.has(this.view.selectedId), calls: this.resources.nodes.size,
            triangles: this.scene.renderer.info.render.triangles, geometries: this.scene.renderer.info.memory.geometries });
        this.scene.renderer.domElement.dataset.dataset = JSON.stringify({ root: this.scene.root.uuid, dataset: this.resources.dataset.namespace,
            regionIds: this.view.regionIds ?? (this.view.region ? [this.view.region] : []), highlighted: [...highlights], observingNerves: observe, nerveLayer: Boolean(this.view.nerves), poseId: this.view.poseId, visible: [...this.resources.nodes].filter(([, n]) => n.visible).map(([key]) => key), selected: this.view.selectedId, bytes: q.bytes, cacheEntries: q.loaded.size, evictions: q.evictions, cancellations: q.cancellations, lateReleases: q.lateReleases, wantedChunks: [...q.wanted], pending: q.pending.size, failed: [...q.failed],
            camera: this.scene.camera.position.toArray(), cameraTarget: this.scene.controls.target.toArray(), cameraZoom: this.scene.camera.zoom, cameraAspect: this.scene.camera.aspect, cameraFov: this.scene.camera.fov, calls: this.scene.renderer.info.render.calls, triangles: this.scene.renderer.info.render.triangles,
            motion: this.motion ? { assetId: this.motion.asset.id, contextKey: this.motion.contextKey,
                learningIntent: this.motionIntent, phase: this.motionPhase,
                surfaceCount: this.motion.originals.size, fixedCount: this.motion.asset.sourceBinding?.members.filter(m => m.role === 'fixed_structure').length } : null,
            motionBytes: this.motion?.resource.memoryEstimateBytes ?? 0, estimatedActiveBytes: q.bytes + (this.motion?.resource.memoryEstimateBytes ?? 0) });
    }
    private fit(rows: RuntimeStructureRecord[], padding = 1.25) {
        const box = new THREE.Box3();
        for (const r of rows) {
            box.expandByPoint(new THREE.Vector3().fromArray(r.bounds[0]));
            box.expandByPoint(new THREE.Vector3().fromArray(r.bounds[1]));
        }
        if (box.isEmpty())
            return;
        this.scene.camera.zoom = 1;
        this.scene.camera.updateProjectionMatrix();
        const center = box.getCenter(new THREE.Vector3()), size = box.getSize(new THREE.Vector3());
        const distance = Math.max(size.y, size.x / this.scene.camera.aspect) / (2 * Math.tan(THREE.MathUtils.degToRad(17.5))) * padding + size.z / 2;
        const direction = this.scene.camera.position.clone().sub(this.scene.controls.target);
        if (direction.length() < .01)
            direction.set(0, 0, 1);
        direction.normalize();
        this.scene.controls.target.copy(center);
        this.scene.camera.position.copy(center).addScaledVector(direction, distance);
        this.scene.controls.update();
        this.scene.requestRender();
    }
    focus(regions: string[]) { this.fit(framingRecords([...this.records.values()], this.view, regions)); }
    focusSelection() { const row = this.records.get(this.view.selectedId ?? ''); if (row)
        this.fit([row]); }
    retry() { this.resources.queue.retry(); }
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
        const nodes = [...this.resources.nodes.values()].filter(n => n.visible);
        const observe = nodes.some(n => n.userData.nerveObservationContext);
        const hit = pickSurface(this.scene.camera, nodes, { x: e.clientX, y: e.clientY }, rect, observe);
        if (!hit)
            return;
        const row = this.records.get(String(hit.object.userData.sourceKey ?? hit.object.name));
        if (row?.inspectionEligible)
            this.select(row.sourceKey, row.side);
    };
    dispose() { if (this.dead)
        return; this.restoreSourceMotion('viewer-unmounted'); this.dead = true; const canvas = this.scene.renderer.domElement; canvas.removeEventListener('keydown', this.onKey, true); canvas.removeEventListener('pointerdown', this.onDown); canvas.removeEventListener('pointerup', this.onUp); this.resources.dispose(); for (const m of this.materials.values())
        m.dispose(); this.materials.clear(); this.scene.dispose(); }
}
