import { searchEntries } from '../../domain/search.ts';
import type { Dataset } from './schema.ts';
import { inRegionalRoute, inRegionalScene, regionalAttachmentBoneKeys } from './regionalContext.ts';
export interface StructureRecord {
    sourceKey: string;
    sourceName: string;
    kind: 'bone' | 'muscle' | 'accessory';
    regionIds: string[];
    side: string | null;
    label: string;
    names: {
        koTraditional: string | null;
        koModern: string | null;
        en: string;
    };
    aliases: string[];
    haConceptId: string | null;
    targetId: string | null;
    targetIds: string[];
    mappingStatus: string;
    localDisplayEligible: boolean;
    inspectionEligible: boolean;
    defaultVisible: boolean;
    sourceOnly: boolean;
    humanReview: string;
    publicRedistribution: string;
    sourceHiddenStatePreserved: {
        hideRender: boolean;
        hideViewport: boolean;
    };
    localUseRights: string;
    displayDecisionBasis: string;
    hardHoldReasons: string[];
    semanticReview?: string;
    /** Explicit local semantic reassignment when the source object label conflicts with the evaluated surface location. */
    surfaceAssignmentCorrection?: {
        correctionId: string;
        sourceNameObservation: string;
        sourceLabelConflict: true;
        displayedPart: 'superior' | 'inferior';
        evaluatedGeometrySha256: string;
        detailResourceSha256: string;
        worldYBoundsMetres: [number, number];
        evidencePath: string;
    };
    /** Name and taxonomy evidence for an AI project crosswalk; never an HA learner binding. */
    nameEvidence?: Partial<Record<'koModern' | 'koTraditional' | 'en', {
        value: string;
        sourceIds: string[];
        locator: string;
    }>>;
    /** Opaque learner/source concept links. They do not create a canonical HA binding. */
    learnerConceptLinks?: {
        conceptKey: string | null;
        relationKind: 'verified_source_crosswalk' | 'verified_class_member' | 'verified_taxonomy_member' | 'normalized_exact_target_term' | 'paired_source_concept' | 'side_or_source_identity_conflict';
        targetIds: string[];
        memberCode: string | null;
        targetTermMatches: { targetId: string; matchedValues: string[] }[];
        matchRule: string;
        evidenceIds: string[];
        identityStatus: 'evidence_backed' | 'source_label_pair_only' | 'side_conflicted' | 'held';
        humanReview: 'not_performed';
    }[];
    targetRelationEvidence?: {
        targetId: string;
        targetEnglish: string;
        targetLatin: string;
        targetSemanticKind: string;
        targetPrimaryOwner: string;
        targetRegionIds: string[];
        targetLaterality: string;
        sourceKey: string;
        sourceObjectName: string;
        sourceDataName: string | null;
        sourceParent: string;
        sourceCollections: string[];
        sourceSide: string | null;
        evaluatedGeometrySha256: string;
        sourceHash: string;
        sourceRevision: string;
        matchBasis: string;
        directObjectNameMatch: boolean;
        ancestorNameAloneUsed: boolean;
        upstreamFjOrTa2IdClaim: boolean;
        canonicalHaBindingCreated: boolean;
        humanReview: string;
        relationKind?: 'direct_exact_name' | 'qualified_target_synonym' | 'class_member';
        matchedTargetSynonym?: string | null;
        sourceSegmentCode?: string | null;
        /** Stable member key for a bounded class-member crosswalk; not a learner or upstream ID. */
        memberCode?: string | null;
        matchEvidenceSourceIds?: string[];
    }[];
    searchApproximate?: boolean;
    bounds: [
        number[],
        number[]
    ];
    relatedMuscles?: {
        sourceKey: string;
        label: string;
        roles: string[];
    }[];
}
export interface RuntimeStructureRecord {
    sourceKey: string;
    /** Separates learner-ready routes from local-only source inspection routes. */
    routeAudience: 'learner' | 'inspection';
    searchGroupKey: string;
    kind: 'bone' | 'muscle' | 'accessory' | 'nerve' | 'fascia' | 'joint' | 'tendon' | 'vessel';
    /** Muscle/tendon rows: superficial layer (ZA "Superficial muscles") or deeper. */
    depth?: 'superficial' | 'deep';
    /** Fine tissue type for fascia/joint/tendon rows, vessel rows (artery/vein/heart) and non-bone skeletal rows (ligament, meniscus, tooth ...). */
    tissue?: string;
    regionIds: string[];
    side: string | null;
    label: string;
    names: { koTraditional: string | null; koModern: string | null; en: string };
    aliases: string[];
    haConceptId: string | null;
    /** Opaque, side-deduplicated concept handles only; no TA2 IDs or evidence. */
    learnerConceptKeys: string[];
    /** Opaque, evidence-validated target/member route handles; raw TA2 IDs stay internal. */
    targetRoutes: { key: string; regionId: string }[];
    /** Exact alternate source nodes hidden only while this source observation is selected. */
    selectionSuppressSourceKeys?: string[];
    localDisplayEligible: boolean;
    inspectionEligible: boolean;
    defaultVisible: boolean;
    sourceOnly: boolean;
    humanReview: 'not_performed';
    publicRedistribution: 'held';
    sourceHiddenStatePreserved: { hideRender: boolean; hideViewport: boolean };
    localUseRights: string;
    displayDecisionBasis: string;
    hardHoldReasons: string[];
    bounds: [[number, number, number], [number, number, number]];
    relatedMuscles: { sourceKey: string; label: string; roles: string[] }[];
    nerve?: { poseId: string; branchKeys: string[]; muscleKeys: string[] };
}
export interface RuntimeIntegration {
    sourceComponents?: Record<string, { datasetRevision: string; integrationRevision: string; overlaySha256: string }>;
    schemaVersion: 1;
    projectionSchema: 'whole-body-local-runtime-v5';
    revision: string;
    datasetRevision: string;
    sourceOverlaySha256: string;
    rightsEvidenceSha256: string;
    scope: { targets: number; memberships: number; regions: number };
    policy: {
        localOnly: true;
        publicRedistribution: 'held';
        humanReview: 'not_performed';
        localUseRights: 'supported_local_prototype';
        rightsDecisionId: string;
    };
    objects: RuntimeStructureRecord[];
}

const RUNTIME_SCHEMA = 'whole-body-local-runtime-v5' as const;
const FROZEN_T100_SCOPE = { targets: 542, memberships: 563, regions: 12 } as const;
const projectionKeys = ['schemaVersion', 'projectionSchema', 'revision', 'datasetRevision', 'sourceOverlaySha256', 'rightsEvidenceSha256', 'scope', 'policy', 'objects', 'sourceComponents'];
const runtimeRowKeys = ['sourceKey', 'routeAudience', 'searchGroupKey', 'kind', 'regionIds', 'side', 'label', 'names', 'aliases', 'haConceptId', 'learnerConceptKeys', 'targetRoutes', 'selectionSuppressSourceKeys', 'localDisplayEligible', 'inspectionEligible', 'defaultVisible', 'sourceOnly', 'humanReview', 'publicRedistribution', 'sourceHiddenStatePreserved', 'localUseRights', 'displayDecisionBasis', 'hardHoldReasons', 'bounds', 'relatedMuscles'];
const runtimePolicyKeys = ['localOnly', 'publicRedistribution', 'humanReview', 'localUseRights', 'rightsDecisionId'];
function exactKeys(value: unknown, expected: string[], message: string): asserts value is Record<string, unknown> {
    if (!value || typeof value !== 'object' || Array.isArray(value)
        || Object.keys(value).sort().join('\u0000') !== [...expected].sort().join('\u0000'))
        throw Error(message);
}
function runtimeCanDisplayLocally(row: RuntimeStructureRecord, policy: RuntimeIntegration['policy']) {
    return policy.localOnly && policy.localUseRights === 'supported_local_prototype'
        && row.localUseRights === 'supported_local_prototype' && row.displayDecisionBasis === policy.rightsDecisionId
        && row.hardHoldReasons.length === 0 && !row.sourceHiddenStatePreserved.hideViewport
        && row.kind !== 'accessory' && row.regionIds.length > 0;
}
function runtimeKindForDataset(kind: string): RuntimeStructureRecord['kind'] | null {
    return kind === 'skeletal_surface' ? 'bone'
        : kind === 'muscle_surface_or_part' ? 'muscle'
            : kind === 'musculoskeletal_accessory' ? 'accessory' : kind === 'nerve_surface' ? 'nerve'
                : kind === 'fascia_surface' ? 'fascia' : kind === 'joint_surface' ? 'joint' : kind === 'tendon_surface' ? 'tendon' : kind === 'vessel_surface' ? 'vessel' : null;
}
export function validateRuntimeIntegration(value: unknown, dataset: Dataset): RuntimeIntegration {
    exactKeys(value, (value as RuntimeIntegration)?.sourceComponents === undefined ? projectionKeys.filter(key => key !== 'sourceComponents') : projectionKeys, 'runtime projection shape');
    const i = value as unknown as RuntimeIntegration;
    if (i.schemaVersion !== 1 || i.projectionSchema !== RUNTIME_SCHEMA || !i.revision
        || i.datasetRevision !== dataset.revision || !/^[a-f0-9]{64}$/.test(i.sourceOverlaySha256)
        || !/^[a-f0-9]{64}$/.test(i.rightsEvidenceSha256))
        throw Error('runtime projection provenance');
    if (i.sourceComponents !== undefined) {
        if (!i.sourceComponents || typeof i.sourceComponents !== 'object' || Array.isArray(i.sourceComponents)) throw Error('runtime source components');
        for (const [namespace, component] of Object.entries(i.sourceComponents)) {
            exactKeys(component, ['datasetRevision', 'integrationRevision', 'overlaySha256'], 'runtime source component shape');
            if (!namespace || !component.datasetRevision || !component.integrationRevision || !/^[a-f0-9]{64}$/.test(component.overlaySha256)
                || (dataset.sourceRevisions?.[namespace] ?? (dataset.namespace === namespace ? dataset.revision : null)) !== component.datasetRevision)
                throw Error('runtime source component provenance');
        }
    }
    exactKeys(i.scope, ['targets', 'memberships', 'regions'], 'runtime scope shape');
    if (i.scope.targets !== FROZEN_T100_SCOPE.targets || i.scope.memberships !== FROZEN_T100_SCOPE.memberships || i.scope.regions !== FROZEN_T100_SCOPE.regions)
        throw Error('runtime frozen scope');
    exactKeys(i.policy, runtimePolicyKeys, 'runtime policy shape');
    if (i.policy.localOnly !== true || i.policy.publicRedistribution !== 'held' || i.policy.humanReview !== 'not_performed'
        || i.policy.localUseRights !== 'supported_local_prototype' || !i.policy.rightsDecisionId)
        throw Error('runtime global policy');
    const instances = new Map(dataset.instances.map(instance => [instance.sourceKey, instance]));
    if (!Array.isArray(i.objects) || i.objects.length !== dataset.instances.length || instances.size !== dataset.instances.length)
        throw Error('runtime object cardinality');
    const seen = new Set<string>();
    const regions = new Set<string>();
    for (const row of i.objects) {
        const expectedRowKeys = [...runtimeRowKeys.filter(key => key !== 'selectionSuppressSourceKeys'),
            ...(['selectionSuppressSourceKeys', 'nerve', 'depth', 'tissue'] as const).filter(key => row[key] !== undefined)];
        exactKeys(row, expectedRowKeys, 'runtime row shape');
        if (row.depth !== undefined && (!['superficial', 'deep'].includes(row.depth) || !['muscle', 'tendon'].includes(row.kind))
            || row.tissue !== undefined && (typeof row.tissue !== 'string' || !row.tissue)) throw Error('runtime layer fields');
        if (row.kind === 'nerve') {
            exactKeys(row.nerve, ['poseId', 'branchKeys', 'muscleKeys'], 'runtime nerve shape');
            const n = row.nerve!;
            if (!n.poseId || !Array.isArray(n.branchKeys) || !Array.isArray(n.muscleKeys)
                || n.branchKeys.some(key => !i.objects.some(child => child.sourceKey === key && child.kind === 'nerve' && child.side === row.side))
                || n.muscleKeys.some(key => !i.objects.some(muscle => muscle.sourceKey === key && muscle.kind === 'muscle' && muscle.side === row.side && muscle.localDisplayEligible))
                || row.haConceptId !== null || row.learnerConceptKeys.length || row.targetRoutes.length) throw Error('runtime nerve relationships');
        } else if (row.nerve !== undefined) throw Error('runtime nerve typing');
        const instance = instances.get(row.sourceKey);
        const geometryKind = instance ? runtimeKindForDataset(instance.kind) : null;
        if (!row.sourceKey || !instance || seen.has(row.sourceKey) || !geometryKind || (row.kind !== 'accessory' && geometryKind !== row.kind)
            || row.routeAudience !== 'learner'
            || !['bone', 'muscle', 'accessory', 'nerve', 'fascia', 'joint', 'tendon', 'vessel'].includes(row.kind) || !row.searchGroupKey || !row.label
            || !Array.isArray(row.regionIds) || row.regionIds.some(id => typeof id !== 'string' || !id)
            || !Array.isArray(row.aliases) || row.aliases.some(alias => typeof alias !== 'string')
            || !Array.isArray(row.learnerConceptKeys) || row.learnerConceptKeys.some(key => typeof key !== 'string' || !/^LC-[a-f0-9]{20}$/.test(key))
            || new Set(row.learnerConceptKeys).size !== row.learnerConceptKeys.length
            || !Array.isArray(row.targetRoutes) || row.targetRoutes.some(route => !route || typeof route.key !== 'string' || !/^TR-[a-f0-9]{24}$/.test(route.key)
                || typeof route.regionId !== 'string' || !row.regionIds.includes(route.regionId))
            || new Set(row.targetRoutes.map(route => route.key)).size !== row.targetRoutes.length
            || row.selectionSuppressSourceKeys !== undefined && (!Array.isArray(row.selectionSuppressSourceKeys)
                || row.selectionSuppressSourceKeys.some(key => typeof key !== 'string' || !key || key === row.sourceKey || !instances.has(key))
                || new Set(row.selectionSuppressSourceKeys).size !== row.selectionSuppressSourceKeys.length)
            || row.side !== null && typeof row.side !== 'string'
            || row.haConceptId !== null && (typeof row.haConceptId !== 'string' || !/^HA-[A-Z]-[A-Z0-9-]+$/.test(row.haConceptId)))
            throw Error('runtime row identity: ' + JSON.stringify({ sourceKey: row.sourceKey, geometryKind, kind: row.kind,
                searchGroupKey: row.searchGroupKey, regionIds: row.regionIds, side: row.side, haConceptId: row.haConceptId }));
        row.regionIds.forEach(region => regions.add(region));
        for (const alternateKey of row.selectionSuppressSourceKeys ?? []) {
            const alternate = i.objects.find(candidate => candidate.sourceKey === alternateKey);
            if (!alternate || alternate.kind !== row.kind || !alternate.regionIds.some(region => row.regionIds.includes(region)))
                throw Error('selection display alternative reference mismatch');
        }
        exactKeys(row.names, ['koTraditional', 'koModern', 'en'], 'runtime names shape');
        if (typeof row.names.en !== 'string' || ['koTraditional', 'koModern'].some(key => row.names[key as 'koTraditional' | 'koModern'] !== null && typeof row.names[key as 'koTraditional' | 'koModern'] !== 'string'))
            throw Error('runtime names');
        exactKeys(row.sourceHiddenStatePreserved, ['hideRender', 'hideViewport'], 'runtime hidden-state shape');
        if (typeof row.sourceHiddenStatePreserved.hideRender !== 'boolean' || typeof row.sourceHiddenStatePreserved.hideViewport !== 'boolean'
            || typeof row.localDisplayEligible !== 'boolean' || typeof row.inspectionEligible !== 'boolean' || typeof row.defaultVisible !== 'boolean'
            || typeof row.sourceOnly !== 'boolean' || row.humanReview !== 'not_performed' || row.publicRedistribution !== 'held'
            || typeof row.localUseRights !== 'string' || typeof row.displayDecisionBasis !== 'string'
            || !Array.isArray(row.hardHoldReasons) || row.hardHoldReasons.some(reason => typeof reason !== 'string')
            || !Array.isArray(row.bounds) || row.bounds.length !== 2 || row.bounds.some(bound => !Array.isArray(bound) || bound.length !== 3 || bound.some(value => !Number.isFinite(value))))
            throw Error('runtime row policy/geometry');
        if (row.localDisplayEligible !== runtimeCanDisplayLocally(row, i.policy) || row.defaultVisible && !row.localDisplayEligible
            || row.inspectionEligible && !row.localDisplayEligible)
            throw Error('runtime local display decision mismatch');
        if (!Array.isArray(row.relatedMuscles))
            throw Error('runtime related-muscle shape');
        for (const related of row.relatedMuscles) {
            exactKeys(related, ['sourceKey', 'label', 'roles'], 'runtime related-muscle fields');
            if (!related.sourceKey || !instances.has(related.sourceKey) || !related.label || !Array.isArray(related.roles) || related.roles.some(role => typeof role !== 'string'))
                throw Error('runtime related-muscle reference');
        }
        seen.add(row.sourceKey);
    }
    if (seen.size !== instances.size || regions.size !== FROZEN_T100_SCOPE.regions)
        throw Error('runtime missing source record or region');
    return i;
}
type RouteAudience = 'learner' | 'inspection';
type SearchableStructure = Pick<StructureRecord, 'sourceKey' | 'label' | 'names' | 'aliases' | 'localDisplayEligible' | 'regionIds' | 'haConceptId' | 'side'> & { kind?: RuntimeStructureRecord['kind']; defaultVisible?: boolean; sourceName?: string; searchGroupKey?: string; searchApproximate?: boolean; routeAudience?: RouteAudience; inspectionEligible?: boolean; learnerConceptKeys?: string[]; learnerConceptLinks?: StructureRecord['learnerConceptLinks']; targetRoutes?: { key: string; regionId: string }[] };
function routeAllowed(row: SearchableStructure, audience: RouteAudience) {
    return row.localDisplayEligible && row.inspectionEligible !== false && (row.routeAudience ?? 'learner') === audience;
}
export function searchStructures<T extends SearchableStructure>(rows: T[], query: string, regions: string[], audience: RouteAudience = 'learner') {
    // Text search spans the whole atlas; regional attachment expansion is unused here.
    const hasQuery = Boolean(query.trim());
    const context = hasQuery ? new Set<string>() : regionalAttachmentBoneKeys(rows, regions);
    const candidates = rows.filter(r => routeAllowed(r, audience) && (hasQuery || inRegionalScene(r, regions, null) || r.kind === 'bone' && context.has(r.sourceKey)));
    const unique = new Map<string, T>();
    for (const r of candidates) {
        const key = r.searchGroupKey ?? r.sourceName?.replace(/\.[lr]$/, '') ?? r.sourceKey;
        const previous = unique.get(key);
        if (!previous || (!previous.names.koModern && r.names.koModern))
            unique.set(key, r);
    }
    const byKey = new Map([...unique.values()].map(r => [r.sourceKey, r]));
    return searchEntries([...unique.values()].map(r => ({ id: r.sourceKey, label: r.label, aliases: [r.names.en, r.names.koModern ?? '', r.names.koTraditional ?? '', ...r.aliases] })), query.slice(0, 100))
        .map(match => ({ ...byKey.get(match.entry.id)!, searchApproximate: match.approximate }));
}
export interface DatasetRoute {
    regions: string[];
    selected: string | null;
    targetPathKey?: string;
    /** Present only for the dev-only observation route; never used for ordinary learner navigation. */
    audience?: 'inspection';
}
export function readDatasetRoute(search: string, rows: SearchableStructure[], regionIds: string[], audience: RouteAudience = 'learner'): DatasetRoute {
    const p = new URLSearchParams(search);
    let regions = (p.get('regions') ?? p.get('region') ?? '').split(',').filter(id => regionIds.includes(id));
    const id = p.get('source') ?? p.get('id');
    const side = p.get('side');
    let row = id ? rows.find(r => routeAllowed(r, audience) && (r.sourceKey === id || r.haConceptId === id) && (!side || r.side === side)) : undefined;
    const targetPathKey = p.get('targetPathKey');
    if (targetPathKey) {
        const matches = rows.filter(candidate => routeAllowed(candidate, audience)
            && candidate.targetRoutes?.some(route => route.key === targetPathKey)
            && (!id || candidate.sourceKey === id)
            && (!side || candidate.side === side));
        row = matches.length === 1 ? matches[0] : undefined;
        if (row) {
            const routeRegion = row.targetRoutes!.find(route => route.key === targetPathKey)!.regionId;
            if (regions.length && !regions.includes(routeRegion)) row = undefined;
            else regions = [routeRegion];
        }
    } else if (!id) {
        const concept = p.get('concept');
        if (concept && /^LC-[a-f0-9]{20}$/.test(concept)) {
            const matches = rows.filter(r => routeAllowed(r, audience)
                && (r.learnerConceptKeys?.includes(concept) || r.learnerConceptLinks?.some(link => link.conceptKey === concept))
                && (!side || r.side === side));
            if (matches.length === 1)
                row = matches[0];
        }
    }
    const result: DatasetRoute = { regions: [...new Set(regions)], selected: row && inRegionalRoute(row, rows, regions) ? row.sourceKey : null,
        ...(audience === 'inspection' ? { audience: 'inspection' as const } : {}) };
    if (targetPathKey && result.selected) result.targetPathKey = targetPathKey;
    return result;
}
export function datasetRouteQuery(route: DatasetRoute) { const p = new URLSearchParams(); if (route.audience === 'inspection') p.set('view', 'source-observation'); if (route.regions.length)
    p.set('regions', route.regions.join(',')); if (route.selected)
    p.set('source', route.selected); if (route.targetPathKey)
    p.set('targetPathKey', route.targetPathKey); return p.toString(); }
