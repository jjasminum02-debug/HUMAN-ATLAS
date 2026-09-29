import * as THREE from 'three';
import { AnatomySceneController, type BodyProgress } from '../wholeBody/AnatomySceneController.ts';
import type { BodyManifest, BodyView } from '../wholeBody/contract.ts';
import { DatasetResources } from './DatasetResources.ts';
import type { Dataset } from './schema.ts';
import { validateIntegration, type Integration, type StructureRecord } from './integration.ts';
/** Dataset selection/presentation adapter; renderer, camera and lifecycle remain owned by the existing controller. */
export class DatasetSceneAdapter {
    readonly scene: AnatomySceneController;
    readonly resources: DatasetResources;
    readonly records: Map<string, StructureRecord>;
    private view: BodyView = { region: null, regionIds: [], bones: true, muscles: true, supplements: false, selectedId: null, dim: true };
    private materials = new Map<string, THREE.MeshStandardMaterial>();
    private down = { x: 0, y: 0 };
    private dead = false;
    private contextLost = false;
    private notify: (p: BodyProgress) => void;
    private select: (id: string, side: string | null) => void;
    constructor(host: HTMLElement, dataset: Dataset, integration: Integration, notify: (p: BodyProgress) => void, select: (id: string, side: string | null) => void) {
        validateIntegration(integration, dataset);
        this.notify = notify;
        this.select = select;
        this.records = new Map(integration.objects.map(r => [r.sourceKey, r]));
        const empty = { version: 2, localOnly: true, publicRedistribution: 'held', frame: 'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR', unit: 'm', lodLevels: 1, chunks: [] } as BodyManifest;
        this.scene = new AnatomySceneController(host, empty, p => { if (this.contextLost !== p.contextLost) {
            this.contextLost = p.contextLost;
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
        this.view = view;
        const regions = view.regionIds ?? (view.region ? [view.region] : []);
        const keys = [...this.records.values()].filter(r => r.localDisplayEligible && (!regions.length || r.regionIds.some(x => regions.includes(x))) &&
            (r.kind === 'bone' ? view.bones : r.kind === 'muscle' && view.muscles) && (!view.isolate || !view.selectedId || r.sourceKey === view.selectedId)).map(r => r.sourceKey);
        this.resources.demand(keys, view.selectedId ? [view.selectedId] : []);
        this.apply();
    }
    private apply() {
        if (this.dead)
            return;
        for (const [key, node] of this.resources.nodes) {
            const row = this.records.get(key)!;
            const selected = key === this.view.selectedId;
            node.visible = !(selected && this.view.selectedPresentation === 'hidden');
            const mode = selected ? (this.view.selectedPresentation === 'translucent' ? 'translucent' : 'selected') : this.view.selectedId && this.view.dim ? 'dim' : 'normal';
            const materialKey = row.kind + ':' + mode;
            let material = this.materials.get(materialKey);
            if (!material) {
                const color = new THREE.Color(selected ? '#398b80' : row.kind === 'bone' ? '#e7dec7' : '#b87969');
                if (mode === 'dim')
                    color.lerp(new THREE.Color('#e5e5dd'), .55);
                material = new THREE.MeshStandardMaterial({ color, roughness: .76, transparent: mode === 'translucent', opacity: mode === 'translucent' ? .3 : 1, depthWrite: mode !== 'translucent' });
                this.materials.set(materialKey, material);
            }
            node.material = material;
        }
        this.scene.requestRender();
        const q = this.resources.queue;
        const wanted = [...q.wanted];
        this.notify({ loaded: wanted.filter(x => q.loaded.has(x)).length, total: wanted.length, failed: wanted.filter(x => q.failed.has(x)).length,
            contextLost: this.contextLost, selectedAvailable: !this.view.selectedId || this.resources.nodes.has(this.view.selectedId), calls: this.resources.nodes.size,
            triangles: this.scene.renderer.info.render.triangles, geometries: this.scene.renderer.info.memory.geometries });
        this.scene.renderer.domElement.dataset.dataset = JSON.stringify({ root: this.scene.root.uuid, dataset: this.resources.dataset.namespace,
            visible: [...this.resources.nodes].filter(([, n]) => n.visible).map(([key]) => key), selected: this.view.selectedId, bytes: q.bytes, pending: q.pending.size, failed: [...q.failed],
            camera: this.scene.camera.position.toArray(), calls: this.scene.renderer.info.render.calls, triangles: this.scene.renderer.info.render.triangles });
    }
    private fit(rows: StructureRecord[]) {
        const box = new THREE.Box3();
        for (const r of rows) {
            box.expandByPoint(new THREE.Vector3().fromArray(r.bounds[0]));
            box.expandByPoint(new THREE.Vector3().fromArray(r.bounds[1]));
        }
        if (box.isEmpty())
            return;
        const center = box.getCenter(new THREE.Vector3()), size = box.getSize(new THREE.Vector3());
        const distance = Math.max(size.y, size.x / this.scene.camera.aspect) / (2 * Math.tan(THREE.MathUtils.degToRad(17.5))) * 1.25 + size.z / 2;
        const direction = this.scene.camera.position.clone().sub(this.scene.controls.target);
        if (direction.length() < .01)
            direction.set(0, 0, 1);
        direction.normalize();
        this.scene.controls.target.copy(center);
        this.scene.camera.position.copy(center).addScaledVector(direction, distance);
        this.scene.controls.update();
        this.scene.requestRender();
    }
    focus(regions: string[]) { this.fit([...this.records.values()].filter(r => r.localDisplayEligible && (!regions.length || r.regionIds.some(x => regions.includes(x))))); }
    focusSelection() { const row = this.records.get(this.view.selectedId ?? ''); if (row)
        this.fit([row]); }
    retry() { this.resources.queue.retry(); }
    private onKey = (e: KeyboardEvent) => { if (e.key === 'Home') {
        e.preventDefault();
        e.stopImmediatePropagation();
        this.focus([]);
    } };
    private onDown = (e: PointerEvent) => { this.down = { x: e.clientX, y: e.clientY }; };
    private onUp = (e: PointerEvent) => {
        if (e.button !== 0 || Math.hypot(e.clientX - this.down.x, e.clientY - this.down.y) > 5)
            return;
        const rect = this.scene.renderer.domElement.getBoundingClientRect();
        const ray = new THREE.Raycaster();
        ray.setFromCamera(new THREE.Vector2((e.clientX - rect.left) / rect.width * 2 - 1, -(e.clientY - rect.top) / rect.height * 2 + 1), this.scene.camera);
        const nodes = [...this.resources.nodes.values()].filter(n => n.visible);
        const hit = ray.intersectObjects(nodes, false)[0];
        if (!hit)
            return;
        const row = this.records.get(hit.object.name);
        if (row?.inspectionEligible)
            this.select(row.sourceKey, row.side);
    };
    dispose() { if (this.dead)
        return; this.dead = true; const canvas = this.scene.renderer.domElement; canvas.removeEventListener('keydown', this.onKey, true); canvas.removeEventListener('pointerdown', this.onDown); canvas.removeEventListener('pointerup', this.onUp); this.resources.dispose(); for (const m of this.materials.values())
        m.dispose(); this.materials.clear(); this.scene.dispose(); }
}
