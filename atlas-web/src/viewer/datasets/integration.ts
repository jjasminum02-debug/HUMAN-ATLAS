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
export interface IntegrationEvidenceSource {
    id: string;
    url: string;
    sourceLabel: string;
    exactEdition: string | null;
    editionExposure: string;
    accessDate: string;
    accessMethod: 'opened_html' | 'opened_pdf' | 'search_index_excerpt' | 'local_frozen_metadata';
    locator: string;
    retrievalLayer?: string;
    openedOriginalDictionaryRecord?: boolean;
    openedOriginalSourcePage?: boolean;
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
    sourceParentId: number | null;
    sourceAncestryIds: number[];
    sourceFlags: Record<string, unknown>;
    classification: Record<string, unknown>;
    names: { koModern: string | null; koTraditional: string | null; en: string };
    fieldEvidence: Record<'koModern' | 'koTraditional' | 'en' | 'latin', {
        value: string | null;
        sourceIds: string[];
        locator: string | null;
        status: 'evidence_backed' | 'missing';
        missingReason?: string | null;
    }> & {
        sourceSynonyms?: { language: string; value: string; sourceIds: string[]; locator: string; status: 'evidence_backed' }[];
        hanja?: { value: null; sourceIds: string[]; locator: null; status: 'not_collected'; missingReason: string };
    };
    unappliedTermCandidates?: { value: string; sourceId: string; locator: string; status: string; reason: string }[];
    existingSurface: Record<string, unknown>;
    observedSurfacesNotBound: Record<string, unknown>[];
    learnerBindingCreated: false;
    canonicalHaConceptId: null;
    sourceOnly: true;
    humanReview: 'not_performed';
    publicRedistribution: 'held';
    newGeometryCreated: false;
}
/** Frozen T96 lexical authority supplied to the local validator, never emitted to learner runtime. */
export interface FrozenTargetLexicon {
    sha256: string;
    supportContext?: {
        sha256: string;
        terms: {
            id: number;
            parent: number | null;
            term: { en?: string; en_US?: string; en_GB?: string; la: string };
            synonyms?: Record<string, string[]>;
        }[];
    };
    targets: {
        id: string;
        term: { english: string; latin: string; sourceSynonyms: Record<string, string[]> };
        semanticKind: string;
        primaryOwner: string;
        regionIds: string[];
        sourceAncestryIds?: number[];
        sourceCardinality?: { explicitSourceSide?: string | null };
    }[];
}
export interface Integration {
    schemaVersion: 1;
    revision: string;
    datasetRevision: string;
    sourceHash: string;
    scope: { targets: number; memberships: number; regions: number };
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
/** Learner/runtime rows intentionally exclude developer evidence, target IDs, locators and local paths. */
export interface RuntimeStructureRecord {
    sourceKey: string;
    /** Separates learner-ready routes from local-only source inspection routes. */
    routeAudience: 'learner' | 'inspection';
    searchGroupKey: string;
    kind: 'bone' | 'muscle' | 'accessory' | 'nerve';
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
/** Historical non-approval, public-release holds and optional human review are NOT local display gates. */
export function canDisplayLocally(row: StructureRecord, policy: Integration['policy']) {
    return policy.localOnly && policy.localUseRights === 'supported_local_prototype'
        && row.localUseRights === 'supported_local_prototype' && row.displayDecisionBasis === policy.rightsDecisionId
        && row.hardHoldReasons.length === 0 && !row.sourceHiddenStatePreserved.hideViewport
        && row.kind !== 'accessory' && row.regionIds.length > 0;
}
function normalizeConceptTerm(value: string) {
    return Array.from(value.normalize('NFKC').toLocaleLowerCase()).filter(char => /[\p{L}\p{N}]/u.test(char)).join('');
}
export function validateIntegration(value: unknown, dataset: Dataset, frozenTargetLexicon: FrozenTargetLexicon): Integration {
    const i = value as Integration;
    if (i?.schemaVersion !== 1 || i.datasetRevision !== dataset.revision || !i.policy.localOnly || i.policy.publicRedistribution !== 'held'
        || i.policy.humanReview !== 'not_performed' || i.policy.localUseRights !== 'supported_local_prototype'
        || !/^[a-f0-9]{64}$/.test(i.policy.rightsEvidenceSha256))
        throw Error('integration provenance');
    if (!frozenTargetLexicon || !/^[a-f0-9]{64}$/.test(frozenTargetLexicon.sha256)
        || frozenTargetLexicon.targets.length !== FROZEN_T100_SCOPE.targets)
        throw Error('frozen target lexicon provenance');
    const context = frozenTargetLexicon.supportContext;
    if (context && (context.sha256 !== 'f789725cf0206d6096abfffbc2657e309bd62bab0f89451f413468d8738da983'
        || context.terms.length !== 2422 || new Set(context.terms.map(term => term.id)).size !== 2422))
        throw Error('frozen support context provenance');
    const contextTerms = new Map(context?.terms.map(term => [term.id, term]) ?? []);
    const hasExactPosteriorCricoarytenoidContext = (relation: NonNullable<StructureRecord['targetRelationEvidence']>[number], sourceName: string, side: string | null) => {
        const contextTarget = contextTerms.get(2196);
        const exactEnglish = contextTarget?.term.en_GB;
        const suffixSide = sourceName.match(/\.([lr])$/i)?.[1]?.toLocaleLowerCase();
        return relation.targetId === 'TA2:2196' && exactEnglish === 'posterior crico-arytenoid muscle'
            && relation.matchedTargetSynonym === exactEnglish
            && normalizeConceptTerm(sourceName.replace(/\.[lr]$/i, '')) === normalizeConceptTerm(exactEnglish)
            && (suffixSide === 'l' ? 'left' : suffixSide === 'r' ? 'right' : null) === side
            && (side === 'left' || side === 'right')
            && relation.sourceObjectName === sourceName && relation.sourceSide === side
            && relation.sourceParent === 'Laryngeal muscles.g'
            && ['Laryngeal muscles', 'Muscles of neck', 'Neck'].every(name => relation.sourceCollections.includes(name))
            && relation.matchEvidenceSourceIds?.includes('fipat-ta2-t78-frozen-full-context') === true;
    };
    const frozenTargets = new Map(frozenTargetLexicon.targets.map(target => [target.id, target]));
    if (frozenTargets.size !== frozenTargetLexicon.targets.length
        || [...frozenTargets.values()].some(target => !/^TA2:\d+$/.test(target.id) || !target.term?.english
            || typeof target.term.latin !== 'string' || !target.semanticKind || !target.primaryOwner || !Array.isArray(target.regionIds)))
        throw Error('frozen target lexicon shape');
    // Build the frozen vocabulary index once per validation run; never rescan 542 targets for each surface.
    const exactLexiconIndex = new Map<string, Map<string, Set<string>>>();
    for (const target of frozenTargetLexicon.targets) {
        const values = [target.term.english, target.term.latin, ...Object.values(target.term.sourceSynonyms).flat()];
        for (const value of new Set(values.filter(Boolean))) {
            const key = normalizeConceptTerm(value);
            const byTarget = exactLexiconIndex.get(key) ?? new Map<string, Set<string>>();
            const matchedValues = byTarget.get(target.id) ?? new Set<string>();
            matchedValues.add(value);
            byTarget.set(target.id, matchedValues);
            exactLexiconIndex.set(key, byTarget);
        }
    }
    const keys = new Set(dataset.instances.map(x => x.sourceKey));
    const instances = new Map(dataset.instances.map(x => [x.sourceKey, x]));
    const evidenceSources = new Map<string, IntegrationEvidenceSource>();
    for (const source of i.evidenceSources ?? []) {
        if (!source.id || evidenceSources.has(source.id) || !(/^https?:\/\//.test(source.url) || source.accessMethod === 'local_frozen_metadata' && /^local:atlas-data\/terminology\/rules\/[a-z0-9-]+\.json$/.test(source.url))
            || !/^\d{4}-\d{2}-\d{2}$/.test(source.accessDate) || !source.locator.trim()
            || !['opened_html', 'opened_pdf', 'search_index_excerpt', 'local_frozen_metadata'].includes(source.accessMethod))
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
            if (evidence.sourceIds.some(id => !evidenceSources.has(id)))
                throw Error('target terminology field references missing source');
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
        if (!keys.has(row.sourceKey) || instances.get(row.sourceKey)?.sourceName !== row.sourceName
            || seen.has(row.sourceKey) || row.publicRedistribution !== 'held')
            throw Error('integration identity/policy');
        if (row.localDisplayEligible !== Boolean(canDisplayLocally(row, i.policy)) || row.defaultVisible !== row.localDisplayEligible)
            throw Error('local decision mismatch');
        if (row.haConceptId && row.semanticReview !== 'ai_crosschecked_exact_term_system_region_side_and_source_identity'
            && !(row.surfaceAssignmentCorrection && row.semanticReview === 'ai_crosschecked_geometry_location_with_upstream_source_label_conflict'))
            throw Error('unreviewed concept binding');
        if (row.surfaceAssignmentCorrection) {
            const correction = row.surfaceAssignmentCorrection;
            const instance = instances.get(row.sourceKey);
            const isAscendingSource = row.sourceName.startsWith('Ascending part of trapezius muscle.');
            const isDescendingSource = row.sourceName.startsWith('Descending part of trapezius muscle.');
            const expected = isAscendingSource ? {
                displayedPart: 'superior', label: '승모근 상부', koModern: '등세모근 위부분',
                english: 'Descending part of trapezius muscle', concept: 'HA-P-000009', target: 'TA2:2227',
                geometry: '576353abfdb0fd286ce49a9ca454da5ff5f4d6d1ef03a33955ebcc901593846b',
                region: 'neck',
            } : isDescendingSource ? {
                displayedPart: 'inferior', label: '승모근 하부', koModern: '등세모근 아래부분',
                english: 'Ascending part of trapezius muscle', concept: 'HA-P-000011', target: 'TA2:2229',
                geometry: 'bba204c6fac7acb06200db7ad8eef4e88ec8694c32c0ab60b2147bbbeed3df43',
                region: null,
            } : null;
            if (!expected || !instance || correction.correctionId !== 'T100-TRAPEZIUS-SURFACE-ASSIGNMENT-2026-09-29-v1'
                || correction.sourceNameObservation !== row.sourceName || correction.sourceLabelConflict !== true
                || correction.displayedPart !== expected.displayedPart || correction.evaluatedGeometrySha256 !== expected.geometry
                || correction.detailResourceSha256 !== instance.lods.detail.resource
                || correction.worldYBoundsMetres.length !== 2 || correction.worldYBoundsMetres.some((v, index) => Math.abs(v - row.bounds[index][1]) > 1e-6)
                || !correction.evidencePath.startsWith('work/evidence/T100/geometry-corrections/2026-09-29-trapezius-assignment/')
                || row.semanticReview !== 'ai_crosschecked_geometry_location_with_upstream_source_label_conflict'
                || row.mappingStatus !== 'source_name_geometry_conflict_resolved_for_local_display'
                || row.label !== expected.label || row.names.koTraditional !== expected.label
                || row.names.koModern !== expected.koModern || row.names.en !== expected.english
                || row.haConceptId !== expected.concept || row.targetId !== expected.target
                || !row.targetIds.includes(expected.target) || (expected.region ? !row.regionIds.includes(expected.region) : row.regionIds.includes('neck'))
                || !['left', 'right'].includes(row.side ?? ''))
                throw Error('trapezius surface-assignment correction');
        }
        if (row.inspectionEligible && (row.sourceHiddenStatePreserved.hideViewport || row.kind === 'accessory' || !row.regionIds.length))
            throw Error('held inspection');
        if (row.bounds.length !== 2 || row.bounds.some(b => b.length !== 3 || !b.every(Number.isFinite)))
            throw Error('bounds');
        if (row.nameEvidence) {
            if (!Object.keys(row.nameEvidence).length)
                throw Error('empty name evidence');
            for (const field of ['koModern', 'koTraditional', 'en'] as const) {
                const evidence = row.nameEvidence[field];
                if (!evidence)
                    continue;
                const fieldValue = row.names[field];
                if (!evidence || !fieldValue || evidence.value !== fieldValue || !evidence.locator.trim()
                    || !evidence.sourceIds.length || evidence.sourceIds.some(id => !evidenceSources.has(id)))
                    throw Error('name field provenance');
            }
        }
        for (const link of row.learnerConceptLinks ?? []) {
            exactKeys(link, ['conceptKey', 'relationKind', 'targetIds', 'memberCode', 'targetTermMatches', 'matchRule', 'evidenceIds', 'identityStatus', 'humanReview'], 'learner concept link fields');
            if (link.conceptKey !== null && !/^LC-[a-f0-9]{20}$/.test(link.conceptKey)
                || !['verified_source_crosswalk', 'verified_class_member', 'verified_taxonomy_member', 'normalized_exact_target_term', 'paired_source_concept', 'side_or_source_identity_conflict'].includes(link.relationKind)
                || !Array.isArray(link.targetIds) || link.targetIds.some(id => !/^TA2:\d+$/.test(id))
                || new Set(link.targetIds).size !== link.targetIds.length
                || !Array.isArray(link.targetTermMatches) || !Array.isArray(link.evidenceIds)
                || link.evidenceIds.some(id => !evidenceSources.has(id))
                || typeof link.matchRule !== 'string' || !link.matchRule
                || link.humanReview !== 'not_performed')
                throw Error('learner concept link shape/provenance');
            for (const match of link.targetTermMatches) {
                exactKeys(match, ['targetId', 'matchedValues'], 'learner target-term match fields');
                if (!link.targetIds.includes(match.targetId) || !Array.isArray(match.matchedValues) || !match.matchedValues.length
                    || match.matchedValues.some(value => normalizeConceptTerm(value) !== normalizeConceptTerm(row.sourceName.replace(/\.[lr]$/i, ''))))
                    throw Error('learner exact target-term relation');
            }
            if (link.relationKind === 'normalized_exact_target_term') {
                if (link.targetIds.length !== 1 || !link.targetTermMatches.length
                    || link.identityStatus !== 'evidence_backed' && link.identityStatus !== 'side_conflicted'
                    || !link.evidenceIds.includes('fipat-ta2-t96-full-target-catalog')
                    || !link.matchRule.includes('punctuation_fold_exact'))
                    throw Error('learner exact-term link unsupported');
                const sourceLabel = row.sourceName.replace(/\.[lr]$/i, '');
                const lexicalMatches = [...(exactLexiconIndex.get(normalizeConceptTerm(sourceLabel)) ?? new Map())]
                    .map(([targetId, values]) => ({ targetId, values: [...values].sort() }))
                    .sort((left, right) => left.targetId.localeCompare(right.targetId));
                if (lexicalMatches.length !== 1 || lexicalMatches[0].targetId !== link.targetIds[0]
                    || link.targetTermMatches.length !== 1 || link.targetTermMatches[0].targetId !== lexicalMatches[0].targetId
                    || JSON.stringify([...link.targetTermMatches[0].matchedValues].sort()) !== JSON.stringify(lexicalMatches[0].values))
                    throw Error('learner exact-term relation differs from frozen target lexicon');
                const target = frozenTargets.get(link.targetIds[0])!;
                if (!target.semanticKind.includes(row.kind) || !target.regionIds.some(region => row.regionIds.includes(region)))
                    throw Error('learner exact-term kind/region mismatch');
            } else if (link.relationKind === 'verified_class_member') {
                const rows = row.targetRelationEvidence ?? [];
                const matching = rows.filter(relation => link.targetIds.includes(relation.targetId)
                    && relation.relationKind === 'class_member'
                    && (relation.memberCode === link.memberCode + ':' + row.side
                        || relation.memberCode === link.memberCode && relation.sourceSide === row.side));
                const segmentCode = link.memberCode?.match(/^(?:segment|lumbar):([CTL]\d+)$/)?.[1] ?? null;
                const exactUnsidedSegment = row.side === null && !!segmentCode
                    && rows.some(relation => link.targetIds.includes(relation.targetId)
                        && relation.relationKind === 'class_member' && relation.sourceSide === null
                        && relation.sourceSegmentCode === segmentCode
                        && /^Vertebra (?:C[3-7]|T(?:[1-9]|1[0-2])|L[1-5])$/.test(relation.sourceObjectName)
                        && relation.sourceObjectName === `Vertebra ${segmentCode}`);
                if (!link.conceptKey || !link.targetIds.length || link.targetIds.some(id => !frozenTargets.has(id)) || !link.memberCode
                    || link.targetTermMatches.length || (!['left', 'right'].includes(row.side ?? '') && !exactUnsidedSegment))
                    throw Error('learner class-member link shape');
                if (!link.matchRule.startsWith('exact frozen T96 class_member'))
                    throw Error('learner class-member rule provenance');
                const evidenced = matching.length > 0 && link.evidenceIds.every(id => matching.some(relation => relation.matchEvidenceSourceIds?.includes(id)));
                const segmentEvidence = exactUnsidedSegment && link.targetIds.every(targetId => rows.some(relation =>
                    relation.targetId === targetId && relation.relationKind === 'class_member'
                    && relation.sourceSegmentCode === segmentCode && relation.matchEvidenceSourceIds?.some(id => link.evidenceIds.includes(id))));
                if ((!evidenced && !segmentEvidence) || link.evidenceIds.some(id => !rows.some(relation =>
                    link.targetIds.includes(relation.targetId) && relation.relationKind === 'class_member'
                    && relation.matchEvidenceSourceIds?.includes(id))))
                    throw Error('learner class-member proof mismatch');
                if (link.targetIds.some(id => {
                    const target = frozenTargets.get(id)!;
                    return !target.semanticKind.includes(row.kind) || !target.regionIds.some(region => row.regionIds.includes(region));
                }))
                    throw Error('learner class-member kind/region mismatch');
            } else if (link.relationKind === 'verified_source_crosswalk') {
                const target = frozenTargets.get(link.targetIds[0]);
                const qualified = (row.targetRelationEvidence ?? []).some(relation =>
                    relation.targetId === target?.id && relation.relationKind === 'qualified_target_synonym'
                    && (Object.values(target.term.sourceSynonyms).flat().includes(relation.matchedTargetSynonym ?? '')
                        || hasExactPosteriorCricoarytenoidContext(relation, row.sourceName, row.side))
                    && relation.sourceObjectName === row.sourceName && relation.sourceSide === row.side
                    && relation.matchEvidenceSourceIds?.every(id => link.evidenceIds.includes(id)));
                const corrected = !!row.surfaceAssignmentCorrection && row.targetId === target?.id
                    && normalizeConceptTerm(row.names.en) === normalizeConceptTerm(target.term.english);
                const exact = row.targetId === target?.id && !row.surfaceAssignmentCorrection
                    && exactLexiconIndex.get(normalizeConceptTerm(row.sourceName.replace(/\.[lr]$/i, '')))?.size === 1
                    && exactLexiconIndex.get(normalizeConceptTerm(row.sourceName.replace(/\.[lr]$/i, '')))?.has(target.id)
                    && row.learnerConceptLinks?.some(proof => proof.relationKind === 'verified_class_member'
                        && proof.identityStatus === 'evidence_backed'
                        && proof.targetIds.some(id => target.sourceAncestryIds?.slice(1).includes(Number(id.slice(4)))));
                const range = Object.values(target?.term.sourceSynonyms ?? {}).flat()
                    .map(value => value.match(/^ribs (\d+)-(\d+)$/)).find(Boolean);
                const index = Number(link.memberCode?.match(/^rib:(\d+)$/)?.[1]);
                const series = target?.semanticKind === 'bone_series' && !!range
                    && index >= Number(range[1]) && index <= Number(range[2])
                    && row.learnerConceptLinks?.some(proof => proof.relationKind === 'verified_class_member'
                        && proof.identityStatus === 'evidence_backed' && proof.memberCode === link.memberCode
                        && proof.targetIds.some(id => frozenTargets.get(id)?.semanticKind === 'bone'));
                const contextChild = contextTerms.get(Number(link.memberCode?.match(/^TA2:(\d+)$/)?.[1]));
                const contextAncestry = new Set<number>();
                let contextParent = contextChild?.parent;
                while (contextParent != null && !contextAncestry.has(contextParent)) {
                    contextAncestry.add(contextParent);
                    contextParent = contextTerms.get(contextParent)?.parent;
                }
                const contextMember = !!contextChild && !!target && !frozenTargets.has(link.memberCode!)
                    && !row.surfaceAssignmentCorrection && row.targetIds.includes(target.id)
                    && contextAncestry.has(Number(target.id.slice(4)))
                    && [contextChild.term.en, contextChild.term.la, ...Object.values(contextChild.synonyms ?? {}).flat()]
                        .filter((value): value is string => typeof value === 'string')
                        .some(value => normalizeConceptTerm(value) === normalizeConceptTerm(row.sourceName.replace(/\.[lr]$/i, '')));
                const ruleProof = link.matchRule === 'exact frozen target representation: qualified_synonym' && qualified
                    || link.matchRule === 'exact frozen target representation: corrected_surface' && corrected
                    || link.matchRule === 'exact frozen target representation: direct_term_with_class_context' && exact
                    || link.matchRule === 'exact frozen target representation: series_member' && series
                    || link.matchRule === 'exact frozen target representation: context_part_member' && contextMember;
                if (!link.conceptKey || link.targetIds.length !== 1 || !target || !row.localDisplayEligible || !row.inspectionEligible
                    || !target.semanticKind.includes(row.kind) || !target.regionIds.some(region => row.regionIds.includes(region))
                    || target.sourceCardinality?.explicitSourceSide && target.sourceCardinality.explicitSourceSide !== row.side
                    || link.targetTermMatches.length || link.identityStatus !== 'evidence_backed' || !ruleProof
                    || !link.evidenceIds.includes('fipat-ta2-t96-full-target-catalog')
                    || !link.evidenceIds.includes('za-t99-frozen-source-objects'))
                    throw Error('learner source-crosswalk proof mismatch');
            } else if (link.relationKind === 'verified_taxonomy_member') {
                const parentId = link.targetIds[0];
                const childId = link.memberCode;
                const parent = frozenTargets.get(parentId);
                const child = childId ? frozenTargets.get(childId) : undefined;
                const childNumber = childId?.match(/^TA2:(\d+)$/)?.[1];
                const parentNumber = parentId?.match(/^TA2:(\d+)$/)?.[1];
                const ancestryHasParent = !!child?.sourceAncestryIds?.includes(Number(parentNumber));
                const exactChildProof = row.learnerConceptLinks?.some(proof => proof !== link
                    && proof.relationKind === 'normalized_exact_target_term'
                    && proof.identityStatus === 'evidence_backed' && proof.targetIds.length === 1
                    && proof.targetIds[0] === childId && proof.evidenceIds.includes('fipat-ta2-t96-full-target-catalog'));
                const crosswalkChildProof = row.learnerConceptLinks?.some(proof => proof !== link
                    && proof.relationKind === 'verified_source_crosswalk' && proof.identityStatus === 'evidence_backed'
                    && proof.targetIds.includes(childId!));
                const classChildProof = row.learnerConceptLinks?.some(proof => proof !== link
                    && proof.relationKind === 'verified_class_member'
                    && proof.identityStatus === 'evidence_backed' && proof.targetIds.includes(childId!)
                    && (row.targetRelationEvidence ?? []).some(relation => relation.targetId === childId
                        && relation.relationKind === 'class_member'
                        && relation.matchEvidenceSourceIds?.some(id => proof.evidenceIds.includes(id))));
                if (!link.conceptKey || link.targetIds.length !== 1 || !parent || !child || parentId === childId
                    || !childNumber || !parentNumber || !ancestryHasParent || !link.memberCode
                    || link.targetTermMatches.length || link.identityStatus !== 'evidence_backed'
                    || !link.evidenceIds.includes('fipat-ta2-t96-full-target-catalog')
                    || !link.evidenceIds.includes('za-t99-frozen-source-objects')
                    || !link.matchRule.startsWith('exact frozen T96 sourceAncestryIds')
                    || (!exactChildProof && !classChildProof && !crosswalkChildProof))
                    throw Error('learner taxonomy-member link proof mismatch');
                if (!parent.semanticKind.includes(row.kind) || !parent.regionIds.some(region => row.regionIds.includes(region))
                    || !child.semanticKind.includes(row.kind) || !child.regionIds.some(region => row.regionIds.includes(region)))
                    throw Error('learner taxonomy-member kind/region mismatch');
                const explicitParentSide = parent.sourceCardinality?.explicitSourceSide;
                const explicitChildSide = child.sourceCardinality?.explicitSourceSide;
                if (explicitParentSide && row.side !== explicitParentSide
                    || explicitChildSide && row.side !== explicitChildSide)
                    throw Error('learner taxonomy-member source side mismatch');
            } else if (link.relationKind === 'paired_source_concept') {
                const sideSuffix = row.sourceName.match(/\.([lr])$/i)?.[1]?.toLocaleLowerCase();
                if (!link.conceptKey || link.targetIds.length || link.memberCode !== null || link.targetTermMatches.length
                    || !link.evidenceIds.includes('za-t99-frozen-source-objects') || link.identityStatus !== 'source_label_pair_only'
                    || !link.matchRule.startsWith('exact source base label')
                    || !sideSuffix || (sideSuffix === 'l' ? 'left' : 'right') !== row.side)
                    throw Error('learner source-pair link unsupported');
            } else if (link.conceptKey !== null || link.memberCode !== null || link.targetTermMatches.length
                || link.identityStatus !== 'held') {
                throw Error('learner identity conflict must stay held');
            }
        }
        for (const relation of row.targetRelationEvidence ?? []) {
            const baseName = row.sourceName.replace(/\.[lr]$/i, '').trim().toLocaleLowerCase();
            const frozenRelationTarget = frozenTargets.get(relation.targetId);
            const exactFrozenSemanticKind = !!frozenRelationTarget
                && relation.targetSemanticKind === frozenRelationTarget.semanticKind
                && frozenRelationTarget.semanticKind.includes(row.kind);
            const allowedClassTargetKind = relation.relationKind === 'class_member'
                && ((relation.targetId === 'TA2:1249' && relation.targetSemanticKind === 'bone_group')
                    || (relation.targetId === 'TA2:1389' && relation.targetSemanticKind === 'bone_group')
                    || (['TA2:1264', 'TA2:1271'].includes(relation.targetId) && relation.targetSemanticKind === 'bone_series'));
            if (relation.sourceKey !== row.sourceKey || relation.sourceObjectName !== row.sourceName
                || !row.targetIds.includes(relation.targetId)
                || relation.targetSemanticKind !== 'bone' && relation.targetSemanticKind !== 'muscle'
                    && !allowedClassTargetKind && !exactFrozenSemanticKind
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
                const exactT78PosteriorContext = relation.relationKind === 'qualified_target_synonym'
                    && hasExactPosteriorCricoarytenoidContext(relation, row.sourceName, row.side);
                const frozenClassTarget = frozenTargets.get(relation.targetId);
                const exactFrozenClassContext = relation.relationKind === 'class_member' && !!frozenClassTarget
                    && relation.targetEnglish === frozenClassTarget.term.english
                    && relation.targetLatin === frozenClassTarget.term.latin
                    && relation.targetSemanticKind === frozenClassTarget.semanticKind
                    && relation.targetPrimaryOwner === frozenClassTarget.primaryOwner
                    && relation.targetRegionIds.length === frozenClassTarget.regionIds.length
                    && relation.targetRegionIds.every((region, index) => region === frozenClassTarget.regionIds[index])
                    && relation.matchEvidenceSourceIds?.includes('fipat-ta2-t96-full-target-catalog') === true;
                if ((!term && !exactT78PosteriorContext && !exactFrozenClassContext) || !relation.matchEvidenceSourceIds?.length
                    || (relation.relationKind !== 'qualified_target_synonym' && !relation.sourceSegmentCode && !relation.memberCode))
                    throw Error('target relation missing target/member evidence');
                if (relation.relationKind === 'qualified_target_synonym') {
                    const exact = (relation.targetId === 'TA2:1038' && relation.sourceObjectName === 'Atlas (C1)' && relation.matchedTargetSynonym === 'vertebra C1' && relation.sourceSegmentCode === 'C1')
                        || (relation.targetId === 'TA2:1050' && relation.sourceObjectName === 'Axis (C2)' && relation.matchedTargetSynonym === 'vertebra C2' && relation.sourceSegmentCode === 'C2');
                    const exactPosteriorCricoarytenoid = hasExactPosteriorCricoarytenoidContext(relation, row.sourceName, row.side);
                    if ((!exact && !exactPosteriorCricoarytenoid)
                        || (exact && (!relation.sourceCollections.some(x => /cervical vertebrae/i.test(x)) || relation.sourceParent !== 'Cervical vertebrae.g')))
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
                    const lumbar = relation.targetId === 'TA2:1068' && relation.targetSemanticKind === 'bone'
                        && /^Vertebra L[1-5]$/.test(relation.sourceObjectName)
                        && relation.sourceSegmentCode === relation.sourceObjectName.match(/L[1-5]$/)?.[0]
                        && relation.memberCode === 'lumbar:' + relation.sourceSegmentCode
                        && relation.sourceParent === 'Lumbar vertebrae.g'
                        && relation.sourceSide === null
                        && ['Back', 'Lumbar vertebrae', 'Vertebral column'].every(x => relation.sourceCollections.includes(x));
                    const ribOrdinals = ['First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth',
                        'Seventh', 'Eighth', 'Ninth', 'Tenth', 'Eleventh', 'Twelfth'];
                    const ribMatch = relation.sourceObjectName.match(/^(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Twelfth) rib\.([lr])$/);
                    const ribIndex = ribMatch ? ribOrdinals.indexOf(ribMatch[1]) + 1 : 0;
                    const ribSide = ribMatch?.[2] === 'l' ? 'left' : ribMatch?.[2] === 'r' ? 'right' : null;
                    const ribParent = ribIndex >= 1 && ribIndex <= 7 ? 'True ribs.g'
                        : ribIndex >= 8 && ribIndex <= 10 ? 'False ribs.g'
                            : ribIndex >= 11 && ribIndex <= 12 ? 'Floating ribs.g' : null;
                    const ordinaryRib = relation.targetId === 'TA2:1118' && relation.targetSemanticKind === 'bone'
                        && !!ribMatch && relation.sourceSegmentCode === null
                        && relation.memberCode === 'rib:' + String(ribIndex).padStart(2, '0')
                        && relation.sourceParent === ribParent && relation.sourceSide === ribSide
                        && ['Ribs', 'Thorax'].every(x => relation.sourceCollections.includes(x));
                    const carpalMatch = relation.sourceObjectName.match(/^(Scaphoid|Lunate|Triquetrum|Pisiform|Trapezium|Trapezoid|Capitate|Hamate) bone\.([lr])$/);
                    const carpalSide = carpalMatch?.[2] === 'l' ? 'left' : carpalMatch?.[2] === 'r' ? 'right' : null;
                    const limbCollection = carpalSide === 'left' ? 'Left upper limb' : 'Right upper limb';
                    const carpal = relation.targetId === 'TA2:1249' && relation.targetSemanticKind === 'bone_group'
                        && !!carpalMatch && relation.sourceSegmentCode === null
                        && relation.memberCode === 'carpal:' + carpalMatch[1].toLocaleLowerCase()
                        && relation.sourceParent === 'Bones of free part of upper limb.g'
                        && relation.sourceSide === carpalSide
                        && relation.sourceCollections.includes(limbCollection)
                        && relation.sourceCollections.includes('Right hand');
                    const metacarpalMatch = relation.sourceObjectName.match(/^(First|Second|Third|Fourth|Fifth) metacarpal bone\.([lr])$/);
                    const metacarpalSide = metacarpalMatch?.[2] === 'l' ? 'left' : metacarpalMatch?.[2] === 'r' ? 'right' : null;
                    const metacarpalLimb = metacarpalSide === 'left' ? 'Left upper limb' : 'Right upper limb';
                    const metacarpal = ['TA2:1264', 'TA2:1265'].includes(relation.targetId)
                        && (relation.targetId !== 'TA2:1264' || relation.targetSemanticKind === 'bone_series')
                        && (relation.targetId !== 'TA2:1265' || relation.targetSemanticKind === 'bone')
                        && !!metacarpalMatch && relation.memberCode === 'metacarpal:' + metacarpalMatch[1].toLocaleLowerCase() + ':' + metacarpalSide
                        && relation.sourceParent === 'Bones of free part of upper limb.g'
                        && relation.sourceSide === metacarpalSide && relation.sourceCollections.includes(metacarpalLimb)
                        && relation.sourceCollections.includes('Right hand');
                    const phalanxMatch = relation.sourceObjectName.match(/^(Proximal|Middle|Distal) phalanx of (first|second|third|fourth|fifth) finger of hand\.([lr])$/);
                    const phalanxSide = phalanxMatch?.[3] === 'l' ? 'left' : phalanxMatch?.[3] === 'r' ? 'right' : null;
                    const phalanxLimb = phalanxSide === 'left' ? 'Left upper limb' : 'Right upper limb';
                    const phalanxClass = relation.targetId === 'TA2:1271' || relation.targetId === 'TA2:1272';
                    const expectedPhalanxLevel = relation.targetId === 'TA2:1277' ? 'Proximal'
                        : relation.targetId === 'TA2:1278' ? 'Middle'
                            : relation.targetId === 'TA2:1279' ? 'Distal' : null;
                    const phalanx = (phalanxClass || !!expectedPhalanxLevel)
                        && (relation.targetId !== 'TA2:1271' || relation.targetSemanticKind === 'bone_series')
                        && (relation.targetId !== 'TA2:1272' && relation.targetId !== 'TA2:1277' && relation.targetId !== 'TA2:1278' && relation.targetId !== 'TA2:1279' || relation.targetSemanticKind === 'bone')
                        && !!phalanxMatch && (phalanxClass || phalanxMatch[1] === expectedPhalanxLevel)
                        && relation.sourceObjectName !== 'Distal phalanx of fifth finger of hand.l'
                        && relation.memberCode === phalanxMatch[1].toLocaleLowerCase() + ':' + phalanxMatch[2].toLocaleLowerCase() + ':' + phalanxSide
                        && relation.sourceParent === 'Bones of free part of upper limb.g'
                        && relation.sourceSide === phalanxSide && relation.sourceCollections.includes(phalanxLimb)
                        && relation.sourceCollections.includes('Right hand')
                        && !(relation.sourceObjectName === 'Distal phalanx of fifth finger of hand.l'
                            && relation.sourceDataName === 'Distal phalanx of fifth finger of hand.r');
                    const footMetatarsalMatch = relation.sourceObjectName.match(/^(First|Second|Third|Fourth|Fifth) metatarsal bone\.([lr])$/);
                    const footMetatarsalSide = footMetatarsalMatch?.[2] === 'l' ? 'left' : footMetatarsalMatch?.[2] === 'r' ? 'right' : null;
                    const footMetatarsalCollection = footMetatarsalSide === 'left' ? 'Left lower limb' : 'Right lower limb';
                    const footMetatarsal = relation.targetId === 'TA2:1496' && relation.targetSemanticKind === 'bone'
                        && !!footMetatarsalMatch && relation.sourceSegmentCode === null
                        && relation.memberCode === 'metatarsal:' + footMetatarsalMatch[1].toLocaleLowerCase() + ':' + footMetatarsalSide
                        && relation.sourceParent === 'Metatarsal bones.g'
                        && relation.sourceSide === footMetatarsalSide
                        && relation.sourceCollections.includes(footMetatarsalCollection);
                    const footPhalanxMatch = relation.sourceObjectName.match(/^(Proximal|Middle|Distal) phalanx of (first|second|third|fourth|fifth) finger of foot\.([lr])$/);
                    const footPhalanxSide = footPhalanxMatch?.[3] === 'l' ? 'left' : footPhalanxMatch?.[3] === 'r' ? 'right' : null;
                    const footPhalanxCollection = footPhalanxSide === 'left' ? 'Left lower limb' : 'Right lower limb';
                    const footPhalanxTarget = relation.targetId === 'TA2:1505' || relation.targetId === 'TA2:1510'
                        || relation.targetId === 'TA2:1511' || relation.targetId === 'TA2:1512';
                    const footPhalanxLevel = relation.targetId === 'TA2:1510' ? 'Proximal'
                        : relation.targetId === 'TA2:1511' ? 'Middle'
                            : relation.targetId === 'TA2:1512' ? 'Distal' : null;
                    const footPhalanx = footPhalanxTarget && relation.targetSemanticKind === 'bone'
                        && !!footPhalanxMatch && (!footPhalanxLevel || footPhalanxMatch[1] === footPhalanxLevel)
                        && relation.memberCode === footPhalanxMatch[1].toLocaleLowerCase() + ':' + footPhalanxMatch[2] + ':' + footPhalanxSide
                        && relation.sourceParent === 'Phalanges of foot.g'
                        && relation.sourceSide === footPhalanxSide
                        && relation.sourceCollections.includes(footPhalanxCollection);
                    const patellaMatch = relation.sourceObjectName.match(/^Patella\.([lr])$/);
                    const patellaSide = patellaMatch?.[1] === 'l' ? 'left' : patellaMatch?.[1] === 'r' ? 'right' : null;
                    const patellaCollection = patellaSide === 'left' ? 'Left lower limb' : 'Right lower limb';
                    const kneeSesamoid = relation.targetId === 'TA2:1389' && relation.targetSemanticKind === 'bone_group'
                        && !!patellaMatch && relation.sourceSegmentCode === null
                        && relation.memberCode === 'sesamoid:patella:' + patellaSide
                        && relation.sourceParent === 'Bones of free part of lower limb.g'
                        && relation.sourceSide === patellaSide
                        && relation.sourceCollections.includes(patellaCollection);
                    if (!cervical && !thoracic && !lumbar && !ordinaryRib && !carpal && !metacarpal && !phalanx
                        && !footMetatarsal && !footPhalanx && !kneeSesamoid)
                        throw Error('target relation class member mismatch: ' + relation.targetId + ' / ' + relation.sourceObjectName);
                } else {
                    throw Error('target relation unsupported non-name match');
                }
            }
        }
        seen.add(row.sourceKey);
    }
    if (seen.size !== keys.size)
        throw Error('missing source records');
    const sourcePairGroups = new Map<string, StructureRecord[]>();
    for (const row of i.objects) {
        for (const link of row.learnerConceptLinks ?? []) {
            if (link.relationKind === 'paired_source_concept' && link.conceptKey) {
                const group = sourcePairGroups.get(link.conceptKey) ?? [];
                group.push(row);
                sourcePairGroups.set(link.conceptKey, group);
            }
        }
    }
    for (const rows of sourcePairGroups.values()) {
        if (rows.length !== 2 || new Set(rows.map(row => row.side)).size !== 2
            || rows.some(row => row.sourceName.replace(/\.[lr]$/i, '') !== rows[0].sourceName.replace(/\.[lr]$/i, '')))
            throw Error('learner source-pair must be one explicit bilateral source label');
    }
    const trapeziusCorrections = i.objects.filter(row => row.surfaceAssignmentCorrection?.correctionId === 'T100-TRAPEZIUS-SURFACE-ASSIGNMENT-2026-09-29-v1');
    if (trapeziusCorrections.length && (trapeziusCorrections.length !== 4
        || ['left', 'right'].some(side => !['superior', 'inferior'].every(part => trapeziusCorrections.some(row => row.side === side && row.surfaceAssignmentCorrection?.displayedPart === part)))))
        throw Error('incomplete trapezius surface-assignment correction pair');
    return i;
}
const RUNTIME_SCHEMA = 'whole-body-local-runtime-v5' as const;
const FROZEN_T100_SCOPE = { targets: 542, memberships: 563, regions: 12 } as const;
const projectionKeys = ['schemaVersion', 'projectionSchema', 'revision', 'datasetRevision', 'sourceOverlaySha256', 'rightsEvidenceSha256', 'scope', 'policy', 'objects'];
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
            : kind === 'musculoskeletal_accessory' ? 'accessory' : kind === 'nerve_surface' ? 'nerve' : null;
}
/** Strictly validate the developer ledger first, then emit one allowlisted learner projection. */
export function buildRuntimeIntegration(value: unknown, dataset: Dataset, sourceOverlaySha256: string, rightsEvidenceSha256: string, frozenTargetLexicon: FrozenTargetLexicon): RuntimeIntegration {
    const full = validateIntegration(value, dataset, frozenTargetLexicon);
    if (!/^[a-f0-9]{64}$/.test(sourceOverlaySha256) || rightsEvidenceSha256 !== full.policy.rightsEvidenceSha256)
        throw Error('runtime projection source hashes');
    const projection: RuntimeIntegration = {
        schemaVersion: 1,
        projectionSchema: RUNTIME_SCHEMA,
        revision: full.revision,
        datasetRevision: full.datasetRevision,
        sourceOverlaySha256,
        rightsEvidenceSha256,
        scope: { ...full.scope },
        policy: {
            localOnly: full.policy.localOnly as true,
            publicRedistribution: full.policy.publicRedistribution as 'held',
            humanReview: full.policy.humanReview as 'not_performed',
            localUseRights: full.policy.localUseRights as 'supported_local_prototype',
            rightsDecisionId: full.policy.rightsDecisionId,
        },
        objects: full.objects.map(row => ({
            sourceKey: row.sourceKey,
            routeAudience: 'learner',
            searchGroupKey: row.sourceName.replace(/\.[lr]$/, ''),
            kind: row.kind,
            regionIds: [...row.regionIds],
            side: row.side,
            label: row.label,
            names: { ...row.names },
            aliases: [...row.aliases],
            haConceptId: row.haConceptId,
            learnerConceptKeys: [...new Set((row.learnerConceptLinks ?? []).flatMap(link => link.conceptKey ? [link.conceptKey] : []))].sort(),
            targetRoutes: [],
            localDisplayEligible: row.localDisplayEligible,
            inspectionEligible: row.inspectionEligible,
            defaultVisible: row.defaultVisible,
            sourceOnly: row.sourceOnly,
            humanReview: row.humanReview as 'not_performed',
            publicRedistribution: row.publicRedistribution as 'held',
            sourceHiddenStatePreserved: { ...row.sourceHiddenStatePreserved },
            localUseRights: row.localUseRights,
            displayDecisionBasis: row.displayDecisionBasis,
            hardHoldReasons: [...row.hardHoldReasons],
            bounds: [[...row.bounds[0]], [...row.bounds[1]]] as RuntimeStructureRecord['bounds'],
            relatedMuscles: (row.relatedMuscles ?? []).map(related => ({ sourceKey: related.sourceKey, label: related.label, roles: [...related.roles] })),
        })),
    };
    return validateRuntimeIntegration(projection, dataset);
}
/** Client-side defense for the compact endpoint: exact field allowlist, fixed denominator and display policy. */
export function validateRuntimeIntegration(value: unknown, dataset: Dataset): RuntimeIntegration {
    exactKeys(value, projectionKeys, 'runtime projection shape');
    const i = value as unknown as RuntimeIntegration;
    if (i.schemaVersion !== 1 || i.projectionSchema !== RUNTIME_SCHEMA || !i.revision
        || i.datasetRevision !== dataset.revision || !/^[a-f0-9]{64}$/.test(i.sourceOverlaySha256)
        || !/^[a-f0-9]{64}$/.test(i.rightsEvidenceSha256))
        throw Error('runtime projection provenance');
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
        const expectedRowKeys = row.selectionSuppressSourceKeys === undefined
            ? runtimeRowKeys.filter(key => key !== 'selectionSuppressSourceKeys') : runtimeRowKeys;
        exactKeys(row, row.nerve === undefined ? expectedRowKeys : [...expectedRowKeys, 'nerve'], 'runtime row shape');
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
            || row.routeAudience !== (instance.sourceNamespace === 'bp3d-r4' ? 'inspection' : 'learner')
            || !['bone', 'muscle', 'accessory', 'nerve'].includes(row.kind) || !row.searchGroupKey || !row.label
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
type SearchableStructure = Pick<StructureRecord, 'sourceKey' | 'label' | 'names' | 'aliases' | 'localDisplayEligible' | 'regionIds' | 'haConceptId' | 'side'> & { sourceName?: string; searchGroupKey?: string; searchApproximate?: boolean; routeAudience?: RouteAudience; inspectionEligible?: boolean; learnerConceptKeys?: string[]; learnerConceptLinks?: StructureRecord['learnerConceptLinks']; targetRoutes?: { key: string; regionId: string }[] };
function routeAllowed(row: SearchableStructure, audience: RouteAudience) {
    return row.localDisplayEligible && row.inspectionEligible !== false && (row.routeAudience ?? 'learner') === audience;
}
export function searchStructures<T extends SearchableStructure>(rows: T[], query: string, regions: string[], audience: RouteAudience = 'learner') {
    const candidates = rows.filter(r => routeAllowed(r, audience) && (query.trim() || !regions.length || r.regionIds.some(x => regions.includes(x))));
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
    const result: DatasetRoute = { regions: [...new Set(regions)], selected: row && (!regions.length || row.regionIds.some(r => regions.includes(r))) ? row.sourceKey : null,
        ...(audience === 'inspection' ? { audience: 'inspection' as const } : {}) };
    if (targetPathKey && result.selected) result.targetPathKey = targetPathKey;
    return result;
}
export function datasetRouteQuery(route: DatasetRoute) { const p = new URLSearchParams(); if (route.audience === 'inspection') p.set('view', 'source-observation'); if (route.regions.length)
    p.set('regions', route.regions.join(',')); if (route.selected)
    p.set('source', route.selected); if (route.targetPathKey)
    p.set('targetPathKey', route.targetPathKey); return p.toString(); }
