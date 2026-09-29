import { searchEntries } from '../../domain/search.ts';
import type { Dataset } from './schema.ts';
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
    /** Name and taxonomy evidence for an AI project crosswalk; never an HA learner binding. */
    nameEvidence?: Partial<Record<'koModern' | 'koTraditional' | 'en', {
        value: string;
        sourceIds: string[];
        locator: string;
    }>>;
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
export interface IntegrationEvidenceSource {
    id: string;
    url: string;
    sourceLabel: string;
    exactEdition: string | null;
    editionExposure: string;
    accessDate: string;
    accessMethod: 'opened_html' | 'search_index_excerpt' | 'local_frozen_metadata';
    locator: string;
}
export interface TargetTerminologyEvidence {
    targetId: string;
    targetTermSourceIds: string[];
    english: string;
    latin: string;
    sourceSynonyms: Record<string, string[]>;
    relatedTerms: string[];
    semanticKind: string;
    primaryOwner: string;
    regionIds: string[];
    sourceParentId: string | null;
    sourceAncestryIds: string[];
    sourceFlags: Record<string, unknown>;
    classification: Record<string, unknown>;
    names: { koModern: string | null; koTraditional: string | null; en: string };
    fieldEvidence: Record<'koModern' | 'koTraditional' | 'en' | 'latin', {
        value: string | null;
        sourceIds: string[];
        locator: string | null;
        status: 'evidence_backed' | 'missing';
        missingReason?: string | null;
    }>;
    existingSurface: Record<string, unknown>;
    observedSurfacesNotBound: Record<string, unknown>[];
    learnerBindingCreated: false;
    canonicalHaConceptId: null;
    sourceOnly: true;
    humanReview: 'not_performed';
    publicRedistribution: 'held';
    newGeometryCreated: false;
}
export interface Integration {
    schemaVersion: 1;
    revision: string;
    datasetRevision: string;
    sourceHash: string;
    policy: {
        localOnly: boolean;
        publicRedistribution: string;
        humanReview: string;
        rightsEvidence: string;
        rightsEvidenceSha256: string;
        rightsDecisionId: string;
        localUseRights: string;
    };
    evidenceSources?: IntegrationEvidenceSource[];
    /** Internal target-name and unresolved-surface evidence; never projected to learner UI/search. */
    targetTerminologyEvidence?: TargetTerminologyEvidence[];
    objects: StructureRecord[];
}
/** Historical non-approval, public-release holds and optional human review are NOT local display gates. */
export function canDisplayLocally(row: StructureRecord, policy: Integration['policy']) {
    return policy.localOnly && policy.localUseRights === 'supported_local_prototype'
        && row.localUseRights === 'supported_local_prototype' && row.displayDecisionBasis === policy.rightsDecisionId
        && row.hardHoldReasons.length === 0 && !row.sourceHiddenStatePreserved.hideViewport
        && row.kind !== 'accessory' && row.regionIds.length > 0;
}
export function validateIntegration(value: unknown, dataset: Dataset): Integration {
    const i = value as Integration;
    if (i?.schemaVersion !== 1 || i.datasetRevision !== dataset.revision || !i.policy.localOnly || i.policy.publicRedistribution !== 'held' || !/^[a-f0-9]{64}$/.test(i.policy.rightsEvidenceSha256))
        throw Error('integration provenance');
    const keys = new Set(dataset.instances.map(x => x.sourceKey));
    const evidenceSources = new Map<string, IntegrationEvidenceSource>();
    for (const source of i.evidenceSources ?? []) {
        if (!source.id || evidenceSources.has(source.id) || !/^https?:\/\//.test(source.url)
            || !/^\d{4}-\d{2}-\d{2}$/.test(source.accessDate) || !source.locator.trim()
            || !['opened_html', 'search_index_excerpt', 'local_frozen_metadata'].includes(source.accessMethod))
            throw Error('integration evidence source');
        evidenceSources.set(source.id, source);
    }
    const targetTerms = new Map<string, TargetTerminologyEvidence>();
    for (const term of i.targetTerminologyEvidence ?? []) {
        if (!/^TA2:\d+$/.test(term.targetId) || targetTerms.has(term.targetId)
            || !term.targetTermSourceIds.length || term.targetTermSourceIds.some(id => !evidenceSources.has(id))
            || !term.english.trim() || !term.latin.trim() || !term.semanticKind.trim()
            || term.learnerBindingCreated !== false || term.canonicalHaConceptId !== null
            || term.sourceOnly !== true || term.humanReview !== 'not_performed'
            || term.publicRedistribution !== 'held' || term.newGeometryCreated !== false)
            throw Error('target terminology evidence identity/policy');
        for (const field of ['koModern', 'koTraditional', 'en', 'latin'] as const) {
            const evidence = term.fieldEvidence[field];
            const value = field === 'latin' ? term.latin : term.names[field];
            if (!evidence || evidence.value !== value || !['evidence_backed', 'missing'].includes(evidence.status))
                throw Error('target terminology field shape');
            if (evidence.status === 'evidence_backed') {
                if (!value || !evidence.locator?.trim() || !evidence.sourceIds.length
                    || evidence.sourceIds.some(id => !evidenceSources.has(id)))
                    throw Error('target terminology field provenance');
            } else if (value !== null || evidence.locator !== null || !evidence.missingReason?.trim()) {
                throw Error('target terminology missing field');
            }
        }
        if (term.names.en !== term.english || term.names.koModern && /\p{Script=Han}/u.test(term.names.koModern)
            || term.names.koTraditional && /\p{Script=Han}/u.test(term.names.koTraditional))
            throw Error('target terminology learner-safe names');
        targetTerms.set(term.targetId, term);
    }
    const seen = new Set<string>();
    for (const row of i.objects) {
        if (!keys.has(row.sourceKey) || seen.has(row.sourceKey) || row.publicRedistribution !== 'held')
            throw Error('integration identity/policy');
        if (row.localDisplayEligible !== Boolean(canDisplayLocally(row, i.policy)) || row.defaultVisible !== row.localDisplayEligible)
            throw Error('local decision mismatch');
        if (row.haConceptId && row.semanticReview !== 'ai_crosschecked_exact_term_system_region_side_and_source_identity')
            throw Error('unreviewed concept binding');
        if (row.inspectionEligible && (row.sourceHiddenStatePreserved.hideViewport || row.kind === 'accessory' || !row.regionIds.length))
            throw Error('held inspection');
        if (row.bounds.length !== 2 || row.bounds.some(b => b.length !== 3 || !b.every(Number.isFinite)))
            throw Error('bounds');
        if (row.nameEvidence) {
            for (const field of ['koModern', 'koTraditional', 'en'] as const) {
                const evidence = row.nameEvidence[field];
                const fieldValue = row.names[field];
                if (!evidence || !fieldValue || evidence.value !== fieldValue || !evidence.locator.trim()
                    || !evidence.sourceIds.length || evidence.sourceIds.some(id => !evidenceSources.has(id)))
                    throw Error('name field provenance');
            }
        }
        for (const relation of row.targetRelationEvidence ?? []) {
            const baseName = row.sourceName.replace(/\.[lr]$/i, '').trim().toLocaleLowerCase();
            if (relation.sourceKey !== row.sourceKey || relation.sourceObjectName !== row.sourceName
                || !row.targetIds.includes(relation.targetId)
                || relation.targetSemanticKind !== 'bone' && relation.targetSemanticKind !== 'muscle'
                || relation.ancestorNameAloneUsed || relation.upstreamFjOrTa2IdClaim
                || relation.canonicalHaBindingCreated || relation.humanReview !== 'not_performed'
                || !/^[a-f0-9]{64}$/.test(relation.evaluatedGeometrySha256)
                || !/^[a-f0-9]{64}$/.test(relation.sourceHash) || !relation.sourceRevision
                || relation.matchEvidenceSourceIds?.some(id => !evidenceSources.has(id)))
                throw Error('target relation evidence');
            if (relation.directObjectNameMatch) {
                if (baseName !== relation.targetEnglish.trim().toLocaleLowerCase())
                    throw Error('target relation exact name mismatch');
            } else {
                const term = targetTerms.get(relation.targetId);
                if (!term || !relation.matchEvidenceSourceIds?.length || !relation.sourceSegmentCode)
                    throw Error('target relation missing target/member evidence');
                if (relation.relationKind === 'qualified_target_synonym') {
                    const exact = (relation.targetId === 'TA2:1038' && relation.sourceObjectName === 'Atlas (C1)' && relation.matchedTargetSynonym === 'vertebra C1' && relation.sourceSegmentCode === 'C1')
                        || (relation.targetId === 'TA2:1050' && relation.sourceObjectName === 'Axis (C2)' && relation.matchedTargetSynonym === 'vertebra C2' && relation.sourceSegmentCode === 'C2');
                    if (!exact || !relation.sourceCollections.some(x => /cervical vertebrae/i.test(x)) || relation.sourceParent !== 'Cervical vertebrae.g')
                        throw Error('target relation qualified synonym mismatch');
                } else if (relation.relationKind === 'class_member') {
                    const cervical = relation.targetId === 'TA2:1032' && /^Vertebra C[3-7]$/.test(relation.sourceObjectName)
                        && relation.sourceSegmentCode === relation.sourceObjectName.match(/C[3-7]$/)?.[0]
                        && relation.sourceParent === 'Cervical vertebrae.g'
                        && relation.sourceCollections.some(x => /cervical vertebrae/i.test(x));
                    const thoracic = relation.targetId === 'TA2:1059' && /^Vertebra T(?:[1-9]|1[0-2])$/.test(relation.sourceObjectName)
                        && relation.sourceSegmentCode === relation.sourceObjectName.match(/T(?:[1-9]|1[0-2])$/)?.[0]
                        && relation.sourceParent === 'Thoracic vertebrae.g'
                        && relation.sourceCollections.some(x => /thoracic vertebrae/i.test(x));
                    if (!cervical && !thoracic)
                        throw Error('target relation class member mismatch');
                } else {
                    throw Error('target relation unsupported non-name match');
                }
            }
        }
        seen.add(row.sourceKey);
    }
    if (seen.size !== keys.size)
        throw Error('missing source records');
    return i;
}
export function searchStructures(rows: StructureRecord[], query: string, regions: string[]) {
    const candidates = rows.filter(r => r.localDisplayEligible && (query.trim() || !regions.length || r.regionIds.some(x => regions.includes(x))));
    const unique = new Map<string, StructureRecord>();
    for (const r of candidates) {
        const key = r.sourceName.replace(/\.[lr]$/, '');
        if (!unique.has(key))
            unique.set(key, r);
    }
    const byKey = new Map([...unique.values()].map(r => [r.sourceKey, r]));
    return searchEntries([...unique.values()].map(r => ({ id: r.sourceKey, label: r.label, aliases: [r.names.en, r.names.koModern ?? '', r.names.koTraditional ?? '', ...r.aliases] })), query.slice(0, 100))
        .map(match => ({ ...byKey.get(match.entry.id)!, searchApproximate: match.approximate }));
}
export interface DatasetRoute {
    regions: string[];
    selected: string | null;
}
export function readDatasetRoute(search: string, rows: StructureRecord[], regionIds: string[]): DatasetRoute {
    const p = new URLSearchParams(search);
    const regions = (p.get('regions') ?? p.get('region') ?? '').split(',').filter(id => regionIds.includes(id));
    const id = p.get('source') ?? p.get('id');
    const side = p.get('side');
    const row = id ? rows.find(r => r.localDisplayEligible && (r.sourceKey === id || r.haConceptId === id) && (!side || r.side === side)) : undefined;
    return { regions: [...new Set(regions)], selected: row && (!regions.length || row.regionIds.some(r => regions.includes(r))) ? row.sourceKey : null };
}
export function datasetRouteQuery(route: DatasetRoute) { const p = new URLSearchParams(); if (route.regions.length)
    p.set('regions', route.regions.join(',')); if (route.selected)
    p.set('source', route.selected); return p.toString(); }
