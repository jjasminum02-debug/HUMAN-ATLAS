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
    const instances = new Map(dataset.instances.map(x => [x.sourceKey, x]));
    const evidenceSources = new Map<string, IntegrationEvidenceSource>();
    for (const source of i.evidenceSources ?? []) {
        if (!source.id || evidenceSources.has(source.id) || !/^https?:\/\//.test(source.url)
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
        if (!keys.has(row.sourceKey) || seen.has(row.sourceKey) || row.publicRedistribution !== 'held')
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
            const allowedClassTargetKind = relation.relationKind === 'class_member'
                && ((relation.targetId === 'TA2:1249' && relation.targetSemanticKind === 'bone_group')
                    || (relation.targetId === 'TA2:1389' && relation.targetSemanticKind === 'bone_group')
                    || (['TA2:1264', 'TA2:1271'].includes(relation.targetId) && relation.targetSemanticKind === 'bone_series'));
            if (relation.sourceKey !== row.sourceKey || relation.sourceObjectName !== row.sourceName
                || !row.targetIds.includes(relation.targetId)
                || relation.targetSemanticKind !== 'bone' && relation.targetSemanticKind !== 'muscle' && !allowedClassTargetKind
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
                if (!term || !relation.matchEvidenceSourceIds?.length || (!relation.sourceSegmentCode && !relation.memberCode))
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
                    const footPhalanxTarget = relation.targetId === 'TA2:1505' || relation.targetId === 'TA2:1510' || relation.targetId === 'TA2:1511';
                    const footPhalanxLevel = relation.targetId === 'TA2:1510' ? 'Proximal'
                        : relation.targetId === 'TA2:1511' ? 'Middle' : null;
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
    const trapeziusCorrections = i.objects.filter(row => row.surfaceAssignmentCorrection?.correctionId === 'T100-TRAPEZIUS-SURFACE-ASSIGNMENT-2026-09-29-v1');
    if (trapeziusCorrections.length && (trapeziusCorrections.length !== 4
        || ['left', 'right'].some(side => !['superior', 'inferior'].every(part => trapeziusCorrections.some(row => row.side === side && row.surfaceAssignmentCorrection?.displayedPart === part)))))
        throw Error('incomplete trapezius surface-assignment correction pair');
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
