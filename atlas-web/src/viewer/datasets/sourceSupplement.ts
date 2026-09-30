import { validateDataset, type Dataset, type Instance, type Chunk } from './schema.ts';
import { validateRuntimeIntegration, type RuntimeIntegration, type RuntimeStructureRecord } from './integration.ts';

export const COMPOSITE_LOCAL_DECISION = 'T100-composed-local-display-v1';
const PROJECT_FRAME='HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR';

export interface SupplementObject {
    sourceKey: string;
    sourceName: string;
    resource: string;
    chunkId: string;
    kind: string;
    side: string | null;
    searchGroupKey: string;
    label: string;
    names: { koModern: string | null; koTraditional: string | null; en: string };
    aliases: string[];
    regionIds: string[];
    bounds: [[number, number, number], [number, number, number]];
    matrix: number[];
    geometrySpace: 'registered_world';
    sourceNamespace: 'bp3d-r4';
    lods: Record<'overview' | 'detail', {
        resource: string; chunk: string; triangles: number; vertices: number; geometryBytes: number;
    }>;
    sourceIdentity: { sourceElementFileId: string; sourceFmaId: string; sourceSha256: string; compiledChunkSha256: string; [key: string]: unknown };
    rights: { localDisplay: string; publicRedistribution: string; sourceOnly: boolean; humanReview: string; localDecisionId: string };
    targetAssociation: { targetId: string; [key: string]: unknown };
}

export interface SourceSupplement {
    schemaVersion: number;
    id: string;
    revision: string;
    namespace: string;
    geometrySpace: string;
    projectFrame: string;
    projectUnit: string;
    sourceOnly?: boolean;
    rightsDecision: { evidencePath: string; evidenceSha256: string; decisionId: string; decisionRevision: string; localDisplay: string; publicRedistribution: string; humanReview: string; sourceOnly: boolean };
    inputSha256: Record<string, string>;
    sourceGroupMembership?: Record<string, { targetId: string; memberElementFileIds: string[]; extentStatus: string }>;
    chunks: (Chunk & { sourceNamespace: 'bp3d-r4'; selectionScoped: true })[];
    objects: SupplementObject[];
    summary: { targetCount: number; uniqueObjects: number; newCanonicalHaBindings: number; humanReview: string; publicRedistribution: string };
}

/** Compose a validated source namespace into the existing one-renderer dataset. */
export function composeSupplementDataset(baseValue: Dataset, supplement: SourceSupplement): Dataset {
    const base = validateDataset(baseValue);
    if (supplement.schemaVersion !== 1 || supplement.namespace !== 'bp3d-r4' || supplement.projectUnit !== 'm'
        || supplement.projectFrame!==PROJECT_FRAME||supplement.geometrySpace !== 'registered_world' || supplement.rightsDecision.publicRedistribution !== 'held'
        || supplement.rightsDecision.humanReview !== 'not_performed' || supplement.rightsDecision.sourceOnly !== true
        || supplement.summary.newCanonicalHaBindings !== 0 || supplement.summary.humanReview !== 'not_performed'
        || supplement.summary.publicRedistribution !== 'held' || supplement.objects.length !== supplement.summary.uniqueObjects)
        throw Error('source supplement policy');
    const chunkById=new Map(supplement.chunks.map(chunk=>[chunk.id,chunk]));
    if(chunkById.size!==supplement.chunks.length||supplement.chunks.some(chunk=>chunk.sourceNamespace!=='bp3d-r4'||chunk.selectionScoped!==true
      ||!/^\/__atlas\/body\/[a-zA-Z0-9-]+\.glb$/.test(chunk.url)||!/^[a-f0-9]{64}$/.test(chunk.sha256)))throw Error('source supplement chunk identity');
    const sourceKeys=new Set<string>();
    for(const object of supplement.objects) {
        const chunk=chunkById.get(object.chunkId);
        if(sourceKeys.has(object.sourceKey)||!/^BP3D4-FJ\d+M?$/.test(object.sourceKey)||object.sourceNamespace!=='bp3d-r4'
            ||object.geometrySpace!=='registered_world'||!chunk?.resources.includes(object.resource)
            ||object.side!==null&&object.side!=='left'&&object.side!=='right'
            ||!/^FJ\d+M?$/.test(object.sourceIdentity.sourceElementFileId)||!/^FMA\d+$/.test(object.sourceIdentity.sourceFmaId)
            ||object.sourceIdentity.compiledChunkSha256!==chunk.sha256||object.sourceIdentity.projectFrame!==PROJECT_FRAME
            ||!/^HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR$/.test(String(object.sourceIdentity.projectFrame))
            ||!/^([a-f0-9]{64})$/.test(String(object.sourceIdentity.compiledMeshAccessorSha256))
            ||object.rights.localDisplay!=='allowed_per_T77_item_decision'||object.rights.publicRedistribution!=='held'
            ||object.rights.sourceOnly!==true||object.rights.humanReview!=='not_performed'
            ||object.targetAssociation.canonicalHaBindingCreated!==false)
            throw Error('source supplement object identity/frame/policy');
        sourceKeys.add(object.sourceKey);
    }

    const chunks: Chunk[] = [
        ...base.chunks.map(chunk => ({ ...chunk, sourceNamespace: 'za-c7010a9' })),
        ...supplement.chunks.map(chunk => ({ ...chunk })),
    ];
    if (new Set(chunks.map(chunk => chunk.id)).size !== chunks.length) throw Error('source supplement duplicate chunk');

    const baseInstances: Instance[] = base.instances.map(instance => ({
        ...instance, sourceNamespace: 'za-c7010a9', geometrySpace: 'source_local',
    }));
    const supplementInstances: Instance[] = supplement.objects.map(object => ({
        sourceKey: object.sourceKey,
        sourceName: object.sourceName,
        kind: object.kind,
        matrix: [...object.matrix],
        lods: {
            overview: { ...object.lods.overview },
            detail: { ...object.lods.detail },
        },
        sourceNamespace: 'bp3d-r4',
        geometrySpace: object.geometrySpace,
        canonicalConceptId: null,
        learnerBinding: 'source_only_unbound',
        defaultLearnerVisible: false,
        appDisplayRights: 'held_not_approved_by_this_task',
        publicRedistribution: 'held',
        humanReview: 'not_performed',
        sourceHiddenStatePreserved: { hideRender: false, hideViewport: false },
    }));
    const instances = [...baseInstances, ...supplementInstances];
    if (new Set(instances.map(instance => instance.sourceKey)).size !== instances.length) throw Error('source supplement duplicate instance');
    const resources = { ...base.resources };
    const resourceOwners = new Map<string,string>();
    for (const object of supplement.objects) {
        for (const lod of Object.values(object.lods)) {
            const metrics={triangles:lod.triangles,vertices:lod.vertices,geometryBytes:lod.geometryBytes};
            const existing=resources[lod.resource];
            if(existing) {
                if(resourceOwners.get(lod.resource)!==object.sourceKey||JSON.stringify(existing)!==JSON.stringify(metrics))throw Error('source supplement duplicate resource');
            } else {
                resources[lod.resource]=metrics;
                resourceOwners.set(lod.resource,object.sourceKey);
            }
        }
    }
    const dataset: Dataset = {
        ...base,
        namespace: 'human-atlas-local',
        revision: `${base.revision}+${supplement.revision}`,
        geometrySpace: 'mixed',
        instances,
        chunks,
        resources,
        budgetPass: true,
    };
    return validateDataset(dataset);
}

/** Append only source-only, per-item locally allowed rows to the existing runtime projection. */
export function composeSupplementRuntime(
    baseValue: RuntimeIntegration,
    dataset: Dataset,
    supplement: SourceSupplement,
    sourceOverlaySha256: string,
    rightsEvidenceSha256: string,
): RuntimeIntegration {
    const base = baseValue;
    const objects: RuntimeStructureRecord[] = [
        ...base.objects.map(row => ({ ...row, displayDecisionBasis: COMPOSITE_LOCAL_DECISION })),
        ...supplement.objects.map(object => {
            if (object.rights.localDisplay !== 'allowed_per_T77_item_decision' || object.rights.publicRedistribution !== 'held'
                || object.rights.sourceOnly !== true || object.rights.humanReview !== 'not_performed'
                || object.rights.localDecisionId !== supplement.rightsDecision.decisionId)
                throw Error('source supplement per-object rights/review hold');
            return {
                sourceKey: object.sourceKey,
                searchGroupKey: object.searchGroupKey,
                kind: object.kind === 'skeletal_surface' ? 'bone' : object.kind === 'muscle_surface_or_part' ? 'muscle' : 'accessory',
                regionIds: [...object.regionIds],
                side: object.side,
                label: object.label,
                names: { ...object.names },
                aliases: [...object.aliases],
                haConceptId: null,
                learnerConceptKeys: [],
                localDisplayEligible: true,
                inspectionEligible: true,
                defaultVisible: false,
                sourceOnly: true,
                humanReview: 'not_performed',
                publicRedistribution: 'held',
                sourceHiddenStatePreserved: { hideRender: false, hideViewport: false },
                localUseRights: 'supported_local_prototype',
                displayDecisionBasis: COMPOSITE_LOCAL_DECISION,
                hardHoldReasons: [],
                bounds: [[...object.bounds[0]], [...object.bounds[1]]],
                relatedMuscles: [],
            } as RuntimeStructureRecord;
        }),
    ];
    const projection: RuntimeIntegration = {
        ...base,
        projectionSchema: 'whole-body-local-runtime-v3',
        revision: `${base.revision}+${supplement.revision}`,
        datasetRevision: dataset.revision,
        sourceOverlaySha256,
        rightsEvidenceSha256,
        policy: { ...base.policy, rightsDecisionId: COMPOSITE_LOCAL_DECISION },
        objects,
    };
    return validateRuntimeIntegration(projection, dataset);
}
