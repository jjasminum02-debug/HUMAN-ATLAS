import * as THREE from 'three';
import { AnatomyMaterials, type MaterialMode } from '../anatomyMaterials.ts';
import { demandedStructureKeys, layerIdOf, innervationHighlightKeys, observingNerves, observationFrameKeys, attachmentObservationKeys, shouldFocusNerveSelection, nerveCourseKeys } from './presentation.ts';
import { AnatomySceneController, type BodyProgress } from '../wholeBody/AnatomySceneController.ts';
import type { BodyManifest, BodyView } from '../wholeBody/contract.ts';
import { DatasetResources } from './DatasetResources.ts';
import { framingRecords } from './framing.ts';
import { pickSurface } from './surfacePicking.ts';
import { keptBySection, sectionPlane, sectionViewDirection, type Bounds, type Section } from '../section.ts';
import type { Dataset } from './schema.ts';
import { validateRuntimeIntegration, type RuntimeIntegration, type RuntimeStructureRecord } from './integration.ts';
import { boneSegments, clampPose, segmentTransforms, type RigFile, type RigPose } from '../rig.ts';
import { parseSkinChunk, posedCopy, segmentForRole, skinGeometry, type SkinChunk, preserveVolume, volumeProfile } from '../skin.ts';
import type { Instance } from './schema.ts';
import type { ActionHighlight, MuscleActionsFile, RigHost } from '../movement.ts';
import type { StudyView } from '../../domain/bookmarks.ts';
import { acupointId, channelSegments, type AcupointFile, type AcupointHost, type SinewFile } from '../acupointLayer.ts';
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
/** Dataset selection/presentation adapter; renderer, camera and lifecycle remain owned by the existing controller. */
export class DatasetSceneAdapter implements RigHost, AcupointHost {
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
    /** M1 skeleton rig: bones follow their segment transform; null transforms = rest pose. */
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
    private attachments: { muscles: Record<string, AttachmentRow[]>; ligaments?: Record<string, AttachmentRow[]> } | 'loading' | 'failed' | null = null;
    /** An attachment observation waits for its drawn areas to load before framing them. */
    private pendingAreaFocus = false;
    /** Ligament area view: muscles and fascia turn see-through so areas inside a joint show (cleared on a new selection). */
    private areaObservation = false;
    /** Estimated (contact) areas: triangle indices per bone resource, fetched per muscle; meshes built from the bone. */
    private readonly contactTris = new Map<string, Record<string, string>[] | 'loading' | 'failed'>();
    private readonly contactNodes = new Map<string, THREE.Mesh>();
    private readonly patchRole = new Map<string, { role: AttachmentRow['role']; bone: string | null }>();
    private readonly displayKeys: Set<string>;
    private down = { x: 0, y: 0 };
    private dead = false;
    private contextLost = false;
    private notify: (p: BodyProgress) => void;
    private select: (id: string, side: string | null) => void;
    constructor(host: HTMLElement, dataset: Dataset, integration: RuntimeIntegration, notify: (p: BodyProgress) => void, select: (id: string, side: string | null) => void) {
        validateRuntimeIntegration(integration, dataset);
        // Progress reaches React state: pass it on only when it changes, not on every posed frame of a playback.
        let last = '';
        this.notify = progress => { const key = JSON.stringify(progress); if (key !== last) { last = key; notify(progress); } };
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
        if (import.meta.env?.DEV || import.meta.env?.MODE === 'qa') (window as unknown as { __atlasRig?: object }).__atlasRig = { // dev inspection only
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
            const slots = weights.roles.map(role => inverse.clone().multiply(transforms.get(segmentForRole(role, row.side, transforms)) ?? new THREE.Matrix4()).multiply(instanceMatrix));
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
                mesh.matrixAutoUpdate = false; mesh.userData = { attachmentPatch: true, attachmentOf: muscle, role: row.role };
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
        const starting = !this.pose && clamped;
        this.pose = clamped;
        // A joint pose leaves the rest geometry that static observers (skin, acupoints) were fitted to.
        if (starting) for (const listener of this.sourceMotionStartListeners) listener();
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
    // Acupoints (4-1 step 7): markers and channel lines ride on their rig segment; a click on a marker picks it.
    private acupoints?: { file: AcupointFile; group: THREE.Group; markers: Map<string, THREE.Mesh>; lines: { line: THREE.Line; ids: string[]; channel: string }[];
        selected: string | null; channel: string | null; onPick?: (id: string) => void };
    showAcupoints(file: AcupointFile | null, onPick?: (id: string) => void) {
        if (this.acupoints) { this.acupoints.group.removeFromParent(); this.acupoints.group.traverse(o => { const m = o as THREE.Mesh; m.geometry?.dispose(); (m.material as THREE.Material | undefined)?.dispose?.(); }); this.acupoints = undefined; }
        if (file) {
            const group = new THREE.Group(); group.name = 'Acupoints'; group.renderOrder = 10;
            const sphere = new THREE.SphereGeometry(.0025, 12, 8), markers = new Map<string, THREE.Mesh>();
            for (const p of file.points) {
                const marker = new THREE.Mesh(sphere, new THREE.MeshBasicMaterial({ color: 0xc2410c, depthTest: false, transparent: true, opacity: .95 }));
                marker.renderOrder = 11; marker.userData.acupoint = acupointId(p); markers.set(acupointId(p), marker); group.add(marker);
            }
            const lines = Object.keys(file.channels).flatMap(channel => ['right', 'left', 'midline'].flatMap(side => channelSegments(file, channel, side))
                .map(path => {
                    const line = new THREE.Line(new THREE.BufferGeometry().setAttribute('position', new THREE.BufferAttribute(new Float32Array(path.length * 3), 3)),
                        new THREE.LineBasicMaterial({ color: 0xc2410c, transparent: true, opacity: .55, depthTest: false }));
                    line.renderOrder = 10; group.add(line); return { line, ids: path.map(acupointId), channel };
                }));
            this.scene.root.add(group);
            this.acupoints = { file, group, markers, lines, selected: null, channel: null, onPick };
        }
        this.apply();
    }
    selectAcupoint(id: string | null, focus = true) {
        if (!this.acupoints) return;
        this.acupoints.selected = id; this.apply();
        const marker = id ? this.acupoints.markers.get(id) : undefined, point = this.acupoints.file.points.find(p => acupointId(p) === id);
        if (focus && marker && point) {
            const normal = new THREE.Vector3(...point.normal), at = marker.position.clone();
            this.scene.moveCamera({ position: at.clone().addScaledVector(normal, .32).add(new THREE.Vector3(0, .04, 0)).toArray(), target: at.toArray(), zoom: 1 });
        }
    }
    showAcupointChannel(channel: string | null) {
        if (!this.acupoints) return;
        this.acupoints.channel = channel; this.apply();
    }
    // Meridian sinews: each line vertex and binding marker rides on its own rig segment.
    private sinews?: { group: THREE.Group; items: { object: THREE.Line | THREE.Mesh | THREE.InstancedMesh; rest: Float32Array; segments: string[] }[] };
    showSinew(file: SinewFile | null, sinew: string | null) {
        if (this.sinews) { this.sinews.group.removeFromParent(); this.sinews.group.traverse(o => { const m = o as THREE.Mesh; m.geometry?.dispose(); (m.material as THREE.Material | undefined)?.dispose?.(); }); this.sinews = undefined; }
        if (file && sinew) {
            const group = new THREE.Group(); group.name = 'Sinews'; group.renderOrder = 10;
            const items: { object: THREE.Line | THREE.Mesh | THREE.InstancedMesh; rest: Float32Array; segments: string[] }[] = [];
            const knot = new THREE.SphereGeometry(.004, 12, 8), bead = new THREE.SphereGeometry(.0018, 8, 6);
            for (const path of file.paths.filter(p => p.sinew === sinew)) {
                const rest = new Float32Array(path.points.flat());
                const line = new THREE.Line(new THREE.BufferGeometry().setAttribute('position', new THREE.BufferAttribute(rest.slice(), 3)),
                    new THREE.LineBasicMaterial({ color: 0x0f766e, transparent: true, opacity: .9, depthTest: false }));
                line.renderOrder = 10; group.add(line); items.push({ object: line, rest, segments: path.segments });
                // A 1-px line is hard to see on muscle: a bead every sample along it.
                const beads = new THREE.InstancedMesh(bead, new THREE.MeshBasicMaterial({ color: 0x14b8a6, depthTest: false, transparent: true, opacity: .85 }), path.points.length);
                beads.renderOrder = 10; beads.frustumCulled = false; group.add(beads); items.push({ object: beads, rest, segments: path.segments });
                for (const node of path.nodes) {
                    const mesh = new THREE.Mesh(knot, new THREE.MeshBasicMaterial({ color: 0x115e59, depthTest: false, transparent: true, opacity: .95 }));
                    mesh.renderOrder = 11; mesh.userData.sinewNode = `${sinew}:${path.side}:${node.anchor}`; group.add(mesh);
                    items.push({ object: mesh, rest: new Float32Array(node.position), segments: [node.segment] });
                }
            }
            this.scene.root.add(group); this.sinews = { group, items };
        }
        this.apply();
    }
    private syncSinews() {
        const s = this.sinews; if (!s) return;
        const transforms = this.rigState?.transforms, at = new THREE.Vector3();
        const matrix = new THREE.Matrix4();
        for (const { object, rest, segments } of s.items) {
            if (object instanceof THREE.InstancedMesh) {
                for (let i = 0; i < segments.length; i++) {
                    at.fromArray(rest, i * 3); const posed = transforms?.get(segments[i]); if (posed) at.applyMatrix4(posed);
                    object.setMatrixAt(i, matrix.makeTranslation(at.x, at.y, at.z));
                }
                object.instanceMatrix.needsUpdate = true; continue;
            }
            if (object instanceof THREE.Mesh) {
                at.fromArray(rest); const posed = transforms?.get(segments[0]); if (posed) at.applyMatrix4(posed); object.position.copy(at); continue;
            }
            const attribute = object.geometry.getAttribute('position') as THREE.BufferAttribute;
            for (let i = 0; i < segments.length; i++) {
                at.fromArray(rest, i * 3); const posed = transforms?.get(segments[i]); if (posed) at.applyMatrix4(posed);
                attribute.setXYZ(i, at.x, at.y, at.z);
            }
            attribute.needsUpdate = true; object.geometry.computeBoundingSphere();
        }
    }
    private syncAcupoints() {
        const a = this.acupoints; if (!a) return;
        const shown = (code: string) => a.channel === null || code.replace(/\d+$/, '') === a.channel;
        const transforms = this.rigState?.transforms, at = new THREE.Vector3();
        for (const p of a.file.points) {
            const marker = a.markers.get(acupointId(p))!;
            at.set(...p.position); const posed = transforms?.get(p.segment); if (posed) at.applyMatrix4(posed);
            marker.position.copy(at); marker.visible = shown(p.code);
            const selected = a.selected === acupointId(p);
            marker.scale.setScalar(selected ? 1.9 : 1); (marker.material as THREE.MeshBasicMaterial).color.setHex(selected ? 0x7c2d12 : 0xc2410c);
        }
        for (const { line, ids, channel } of a.lines) {
            line.visible = a.channel === null || channel === a.channel;
            const attribute = line.geometry.getAttribute('position') as THREE.BufferAttribute;
            ids.forEach((id, i) => attribute.setXYZ(i, ...a.markers.get(id)!.position.toArray() as [number, number, number]));
            attribute.needsUpdate = true; line.geometry.computeBoundingSphere();
        }
    }
    // Bookmarks (4-1 step 6): the viewer owns layers and the section; the scene owns the camera.
    private studyView?: { get: () => Omit<StudyView, 'camera'>; restore: (view: StudyView) => void };
    registerStudyView(get: () => Omit<StudyView, 'camera'>, restore: (view: StudyView) => void) {
        this.studyView = { get, restore }; return () => { if (this.studyView?.get === get) this.studyView = undefined; };
    }
    captureStudyView(): StudyView | null { return this.studyView ? { ...this.studyView.get(), camera: this.scene.cameraState() } : null; }
    restoreStudyView(view: StudyView) {
        this.studyView?.restore(view);
        // After the selection's own framing has run.
        requestAnimationFrame(() => requestAnimationFrame(() => { if (!this.dead) this.scene.moveCamera(view.camera); }));
    }
    openMovement(jointId: string) { for (const listener of this.openMovementListeners) listener(jointId); }
    onOpenMovement(listener: (jointId: string) => void) { this.openMovementListeners.add(listener); return () => { this.openMovementListeners.delete(listener); }; }
    setView(view: BodyView) {
        const wasObserving = Boolean(this.view.focusObservation || this.view.attachmentObservation);
        const observing = Boolean(view.focusObservation || view.attachmentObservation);
        const changedAttachment = this.view.attachmentObservation?.role !== view.attachmentObservation?.role;
        const changedSelection = this.view.selectedId !== view.selectedId;
        if (changedSelection) { this.pendingAreaFocus = false; this.areaObservation = false; }
        if (changedSelection || this.view.poseId !== view.poseId) for (const listener of this.sourceSelectionListeners) listener();
        const focusNerve = shouldFocusNerveSelection(this.integration.objects, this.view, view);
        if (wasObserving && (!observing || changedSelection)) this.scene.endObservation();
        this.view = view;
        if (observing && (!wasObserving || changedSelection || changedAttachment)) {
            this.scene.beginObservation(); this.focusSelection(true);
        }
        const keys = demandedStructureKeys(this.integration.objects, view);
        this.resources.demand(this.withPatches(keys), view.selectedId && keys.includes(view.selectedId) ? [view.selectedId] : []);
        this.apply();
        // Fit the initial deep link before the opening orbit captures its camera.
        if (focusNerve && !observing) this.focusSelection(this.resources.nodes.size > 0 && !this.scene.renderer.domElement.dataset.entrance);
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
    /** Static observers (skin, acupoints) need the rest pose: leave any joint pose. The clip player that used to own this
     * port was removed in D3 part 2; rig poses are the only motion now. */
    restoreSourceMotion(_reason = 'restored') {
        if (this.pose && this.rigState) this.setRigPose(this.rigState.file, null);
    }
    /** The selected muscle's attachment patches, when bones are shown; fetches the patch table on first use. */
    private selectedAttachments(): AttachmentRow[] {
        const id = this.view.selectedId, kind = id ? this.records.get(id)?.kind : undefined;
        if (!id || (kind !== 'muscle' && kind !== 'joint') || !this.view.bones) return [];
        if (this.attachments === null) this.loadAttachments();
        if (typeof this.attachments !== 'object' || !this.attachments) return [];
        // Ligaments, capsules, labra and menisci (4-1 step 6): estimated contact areas only.
        return (kind === 'muscle' ? this.attachments.muscles[id] : this.attachments.ligaments?.[id]) ?? [];
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
            node.visible = visibleKeys.has(key) && !this.view.hiddenSourceKeys?.includes(key) && !selectionAlternativeKeys.has(key) && !(selected && this.view.selectedPresentation === 'hidden');
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
                : highlights.has(key) ? 'innervated' : (this.view.focusObservation && row.kind === 'muscle') || (this.areaObservation && ['muscle', 'fascia', 'tendon'].includes(row.kind)) ? 'observationContext' : this.view.selectedId && this.view.dim || this.quizTarget ? 'dim' : 'normal');
            const phaseTone = null;
            const layerId = layerIdOf(row);
            const highlight = !this.actionHighlight || selected ? undefined
                : this.actionHighlight.agonists.includes(key) ? 'agonist' as const : this.actionHighlight.antagonists.includes(key) ? 'antagonist' as const : undefined;
            // Shown movers stay coloured even while the rest is dimmed around a selection.
            const material = this.materials.get(row.kind, { mode: highlight && mode === 'dim' ? 'normal' : mode, phase: phaseTone, role: highlight, userTranslucent: Boolean(attachmentMode && this.view.translucentSourceKeys?.includes(key)),
                variant: row.tissue, layerOpacity: layerId ? this.view.layerOpacity?.[layerId] : undefined });
            node.material = material;
            node.userData.nerveObservationContext = observe && row.kind !== 'nerve';
        }
        if (this.rigState) {
            const { segmentOf, transforms } = this.rigState;
            for (const [key, node] of this.resources.nodes) {
                const segment = segmentOf.get(key) ?? segmentOf.get(this.patchRole.get(key)?.bone ?? ''); if (!segment) continue;
                node.matrix.fromArray(node.userData.instanceMatrix);
                const posed = transforms?.get(segment); if (posed) node.matrix.premultiply(posed);
            }
            this.skinSoftTissue();
        }
        this.syncContactAreas();
        this.syncAcupoints();
        this.syncSinews();
        if (this.pendingAreaFocus && !this.attachmentAreaBox(this.view.attachmentObservation?.role).isEmpty()) {
            this.pendingAreaFocus = false;
            if (this.view.attachmentObservation) this.focusSelection(true); else this.focusAttachmentAreas(true);
        }
        const selectedNode = this.view.selectedId ? this.resources.nodes.get(this.view.selectedId) : this.quizTarget ? this.resources.nodes.get(this.quizTarget) : undefined;
        this.scene.setOutline(selectedNode?.visible ? [selectedNode] : []);
        this.scene.requestRender();
        const q = this.resources.queue;
        const wanted = [...q.wanted];
        this.notify({ loaded: wanted.filter(x => q.loaded.has(x)).length, total: wanted.length, failed: wanted.filter(x => q.failed.has(x)).length,
            contextLost: this.contextLost, selectedAvailable: !this.view.selectedId || this.resources.nodes.has(this.view.selectedId), calls: this.resources.nodes.size,
            triangles: this.scene.renderer.info.render.triangles, geometries: this.scene.renderer.info.memory.geometries });
        this.scene.renderer.domElement.dataset.dataset = JSON.stringify({ root: this.scene.root.uuid, dataset: this.resources.dataset.namespace,
            regionIds: this.view.regionIds ?? (this.view.region ? [this.view.region] : []), highlighted: [...highlights], observingNerves: observe, focusObservation: Boolean(this.view.focusObservation), attachmentObservation: this.view.attachmentObservation ?? null, attachmentBones: [...attachmentBones], hidden: this.view.hiddenSourceKeys ?? [], translucent: this.view.translucentSourceKeys ?? [], nerveLayer: Boolean(this.view.nerves), poseId: this.view.poseId, visible: [...this.resources.nodes].filter(([, n]) => n.visible).map(([key]) => key), selected: this.view.selectedId, bytes: q.bytes, cacheEntries: q.loaded.size, evictions: q.evictions, cancellations: q.cancellations, lateReleases: q.lateReleases, wantedChunks: [...q.wanted], pending: q.pending.size, failed: [...q.failed],
            camera: this.scene.camera.position.toArray(), cameraTarget: this.scene.controls.target.toArray(), cameraZoom: this.scene.camera.zoom, cameraAspect: this.scene.camera.aspect, cameraFov: this.scene.camera.fov, calls: this.scene.renderer.info.render.calls, triangles: this.scene.renderer.info.render.triangles,
            estimatedActiveBytes: q.bytes });
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
    /** World box of the attachment areas drawn for the selection (one role, or all). */
    private attachmentAreaBox(role?: AttachmentRow['role']) {
        const box = new THREE.Box3(), part = new THREE.Box3();
        const add = (mesh: THREE.Mesh) => {
            if (!mesh.visible) return;
            if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
            box.union(part.copy(mesh.geometry.boundingBox!).applyMatrix4(mesh.matrix));
        };
        for (const p of this.selectedPatches()) { const node = this.resources.nodes.get(p.key); if (node && (!role || p.role === role)) add(node); }
        for (const mesh of this.contactNodes.values()) if (!role || mesh.userData.role === role) add(mesh);
        // A footprint is small: keep at least 8 cm of view around it.
        if (!box.isEmpty()) box.expandByVector(box.getSize(new THREE.Vector3()).subScalar(.08).negate().max(new THREE.Vector3()).multiplyScalar(.5));
        return box;
    }
    /** Camera facing the drawn areas along their mean surface normal, at least 16 cm of view across. */
    private attachmentAreaView(role?: AttachmentRow['role']) {
        const box = this.attachmentAreaBox(role);
        if (box.isEmpty()) return null;
        const normal = new THREE.Vector3(), n = new THREE.Vector3(), normalMatrix = new THREE.Matrix3();
        const add = (mesh: THREE.Mesh) => {
            const attribute = mesh.geometry.getAttribute('normal'); if (!mesh.visible || !attribute) return;
            normalMatrix.getNormalMatrix(mesh.matrix);
            for (let i = 0; i < attribute.count; i++) normal.add(n.fromBufferAttribute(attribute, i).applyMatrix3(normalMatrix));
        };
        for (const p of this.selectedPatches()) { const node = this.resources.nodes.get(p.key); if (node && (!role || p.role === role)) add(node); }
        for (const mesh of this.contactNodes.values()) if (!role || mesh.userData.role === role) add(mesh);
        if (normal.lengthSq() < 1e-12) return null;
        const centre = box.getCenter(new THREE.Vector3()), radius = Math.max(box.getSize(n).length() / 2, .08);
        const distance = radius / Math.sin(THREE.MathUtils.degToRad(this.scene.camera.fov) / 2) * 1.2;
        return { position: centre.clone().addScaledVector(normal.normalize(), distance).toArray(), target: centre.toArray(), zoom: 1 };
    }
    /** Frame the drawn attachment areas of the selection (ligament cards, "부착 면 관찰"). Returns false when none are drawn yet. */
    focusAttachmentAreas(smooth = true) {
        if (!this.areaObservation) { this.areaObservation = true; this.apply(); }
        const view = this.attachmentAreaView();
        if (!view) { this.pendingAreaFocus = true; return false; }
        this.pendingAreaFocus = false; this.scene.moveCamera(view, smooth); return true;
    }
    focusSelection(smooth = true) {
        // Origin/insertion observation looks at the drawn area on the bone, not the whole bone (4-1 step 6).
        const role = this.view.attachmentObservation?.role;
        if (role) {
            const view = this.attachmentAreaView(role);
            if (view) { this.pendingAreaFocus = false; this.scene.moveCamera(view, smooth); return; }
            this.pendingAreaFocus = true;
        }
        const keys = observationFrameKeys(this.integration.objects, this.view);
        const box = new THREE.Box3();
        for (const key of keys) {
            const row = this.records.get(key); if (!row || this.view.hiddenSourceKeys?.includes(key)) continue;
            box.expandByPoint(new THREE.Vector3().fromArray(row.bounds[0])); box.expandByPoint(new THREE.Vector3().fromArray(row.bounds[1]));
        }
        // Include the actual current moving surfaces, not only their frozen rest bounds.
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
        if (this.acupoints) {
            // Markers draw on top, so they are picked first (a small screen radius around each).
            const pointer = new THREE.Vector2(e.clientX, e.clientY);
            let best: { id: string; d: number } | null = null;
            for (const [id, marker] of this.acupoints.markers) {
                if (!marker.visible) continue;
                const s = marker.position.clone().project(this.scene.camera);
                if (s.z > 1) continue;
                const d = pointer.distanceTo(new THREE.Vector2(rect.left + (s.x + 1) / 2 * rect.width, rect.top + (1 - s.y) / 2 * rect.height));
                if (d < 10 && (!best || d < best.d)) best = { id, d };
            }
            if (best) { this.acupoints.onPick?.(best.id); return; }
        }
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
