import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validateIntegration, searchStructures, canDisplayLocally, readDatasetRoute, datasetRouteQuery, type Integration } from './integration.ts';
import type { Dataset } from './schema.ts';
const raw = JSON.parse(readFileSync(new URL('../../../../atlas-data/overlays/za-local-integration.json', import.meta.url), 'utf8')) as Integration;
const compiled = JSON.parse(readFileSync(new URL('../../../../atlas-data/source-cache/datasets/za/compiled/manifest.json', import.meta.url), 'utf8')) as {
    revision: string;
    instances: Array<{ sourceKey: string; lods: { detail: { resource: string } } }>;
};
const skullBatch = JSON.parse(readFileSync(new URL('../../../../work/evidence/T100/batches/2026-09-29-B01-skull-names/term-and-correspondence-ledger.json', import.meta.url), 'utf8')) as {
    targets: Array<{ targetId: string; sourceMembers: string[]; sourceObjectNames: string[]; koModern: string; koTraditional: string; latin: string; kmleSourceId: string }>;
};
const vertebralBatch = JSON.parse(readFileSync(new URL('../../../../work/evidence/T100/batches/2026-09-29-B02-vertebral-variant-coverage/term-and-correspondence-ledger.json', import.meta.url), 'utf8')) as {
    targets: Array<{ targetId: string; names: { koModern: string | null; koTraditional: string | null; en: string }; existingSurface: { status: string } }>;
    crosswalkRelations: Array<{ targetId: string; sourceKey: string; sourceObjectName: string; relationKind: string; sourceSegmentCode: string; matchedTargetSynonym: string | null }>;
};
const lumbarRibHandBatch = JSON.parse(readFileSync(new URL('../../../../work/evidence/T100/batches/2026-09-29-B03-lumbar-ribs-hand-groups/term-and-correspondence-ledger.json', import.meta.url), 'utf8')) as {
    scope: { targetCount: number };
    targets: Array<{ targetId: string; names: { koModern: string | null; koTraditional: string | null; en: string }; existingSurface: { status: string; sourceMembers?: unknown[] }; fieldEvidence: Record<string, { status: string }> }>;
    crosswalkRelations: Array<{ targetId: string; sourceKey: string; sourceObjectName: string; sourceDataName: string | null; sourceSide: string | null; sourceParent: string; sourceCollections: string[]; relationKind: string; memberCode: string; sourceSegmentCode: string | null }>;
    memberCountsByTarget: Record<string, number>;
};
const handPelvisBatch = JSON.parse(readFileSync(new URL('../../../../work/evidence/T100/batches/2026-09-29-B04-hand-pelvis/term-and-correspondence-ledger.json', import.meta.url), 'utf8')) as {
    scope: { targetCount: number };
    targets: Array<{ targetId: string; names: { koModern: string | null; koTraditional: string | null; en: string }; fieldEvidence: Record<string, { status: string }>; existingSurface: { status: string } }>;
    crosswalkRelations: Array<{ targetId: string; sourceKey: string; sourceObjectName: string; sourceDataName: string; sourceSide: string | null; sourceParent: string; sourceCollections: string[]; relationKind: string; memberCode: string; sourceSegmentCode: string | null }>;
    memberCountsByTarget: Record<string, number>;
};
const pelvisLowerLimbBatch = JSON.parse(readFileSync(new URL('../../../../work/evidence/T100/batches/2026-09-29-B05-pelvis-lower-limb-bones/term-and-correspondence-ledger.json', import.meta.url), 'utf8')) as {
    scope: { targetCount: number; requestedTargetIds: string[]; taskTargetDenominator: number; taskRegionMembershipDenominator: number; regions: number };
    sourceEvidence: Array<{ id: string; accessMethod: string; openedOriginalSourcePage?: boolean }>;
    targets: Array<{ targetId: string; names: { koModern: string | null; koTraditional: string | null; en: string }; fieldEvidence: Record<string, { status: string }>; existingSurface: { status: string };
        learnerBindingCreated: boolean; canonicalHaConceptId: string | null; sourceOnly: boolean; humanReview: string; publicRedistribution: string; newGeometryCreated: boolean }>;
    crosswalkRelations: Array<{ targetId: string; sourceKey: string; sourceObjectName: string; sourceDataName: string | null; sourceSide: string | null; sourceParent: string; sourceCollections: string[]; relationKind: string; memberCode: string; sourceSegmentCode: string | null }>;
    memberCountsByTarget: Record<string, number>;
    uniqueSourceObjects: number;
    rightsAndReview: { sourceOnly: boolean; publicRedistribution: string; humanReview: string };
};
const datasetInstances = new Map(compiled.instances.map(instance => [instance.sourceKey, instance]));
const fixture = {
    revision: raw.datasetRevision,
    instances: raw.objects.map(row => ({
        sourceKey: row.sourceKey,
        lods: { detail: { resource: datasetInstances.get(row.sourceKey)?.lods.detail.resource } },
    })),
} as Dataset;
test('whole-source overlay retains records and independent release/review status', () => {
    const overlay = validateIntegration(raw, fixture);
    assert.equal(overlay.objects.length, 960);
    assert.equal(overlay.objects.filter(r => r.localDisplayEligible).length, 672);
    assert(overlay.objects.every(r => r.publicRedistribution === 'held' && r.humanReview === 'not_performed'));
    assert.equal(new Set(overlay.objects.flatMap(r => r.regionIds)).size, 12);
});
test('historical non-approval, public hold and human review do not block evidenced local rendering', () => {
    const row = raw.objects.find(r => r.localDisplayEligible)!;
    assert(canDisplayLocally(row, raw.policy));
    assert(canDisplayLocally({ ...row, humanReview: 'not_performed', publicRedistribution: 'held' }, raw.policy));
    assert(canDisplayLocally({ ...row, humanReview: 'reviewed' }, raw.policy));
    assert(!canDisplayLocally({ ...row, localUseRights: 'unresolved' }, raw.policy));
    assert(!canDisplayLocally({ ...row, hardHoldReasons: ['identity_conflict'] }, raw.policy));
    assert(!canDisplayLocally({ ...row, sourceHiddenStatePreserved: { ...row.sourceHiddenStatePreserved, hideViewport: true } }, raw.policy));
});
test('revision, duplicate/missing keys, local decision mismatch and invented binding fail closed', () => {
    for (const mutate of [x => { x.datasetRevision = 'bad'; }, x => { x.objects[1] = x.objects[0]; }, x => { x.objects.pop(); }, x => { x.objects[0].localDisplayEligible = !x.objects[0].localDisplayEligible; }, x => { x.objects[0].haConceptId = 'HA-M-000001'; x.objects[0].semanticReview = 'candidate_only'; }] as ((x: Integration) => void)[]) {
        const bad = structuredClone(raw);
        mutate(bad);
        assert.throws(() => validateIntegration(bad, fixture));
    }
});
test('all three names search a source pair and regional filters use union', () => {
    assert(searchStructures(raw.objects, 'spleinus', []).some(r => r.names.en.includes('Splenius') && r.searchApproximate));
    for (const q of ['광배근', '넓은등근', 'latissimus'])
        assert(searchStructures(raw.objects, q, []).some(r => r.names.en.includes('Latissimus')));
    const head = searchStructures(raw.objects, '', ['head']), neck = searchStructures(raw.objects, '', ['neck']), both = searchStructures(raw.objects, '', ['head', 'neck']);
    assert.equal(both.length, new Set([...head, ...neck].map(r => r.sourceKey)).size);
});
test('T100 B01 maps ten exact skull targets to fourteen existing source surfaces with field provenance', () => {
    const targets = new Set(skullBatch.targets.map(target => target.targetId));
    const members = raw.objects.filter(row => row.targetRelationEvidence?.some(relation => targets.has(relation.targetId)));
    assert.equal(skullBatch.targets.length, 10);
    assert.equal(new Set([...skullBatch.targets.flatMap(target => target.sourceMembers)]).size, 14);
    assert.equal(members.length, 14);
    assert.equal(new Set(members.map(row => row.sourceKey)).size, 14);
    for (const target of skullBatch.targets) {
        const rows = raw.objects.filter(row => target.sourceMembers.includes(row.sourceKey));
        assert.equal(rows.length, target.sourceMembers.length);
        for (const row of rows) {
            const relation = row.targetRelationEvidence?.[0];
            assert(relation);
            assert.equal(relation.targetId, target.targetId);
            assert.equal(relation.sourceKey, row.sourceKey);
            assert.equal(relation.sourceObjectName, row.sourceName);
            assert.equal(relation.sourceSide, row.side);
            assert.equal(relation.directObjectNameMatch, true);
            assert.equal(relation.ancestorNameAloneUsed, false);
            assert.equal(relation.upstreamFjOrTa2IdClaim, false);
            assert.equal(relation.canonicalHaBindingCreated, false);
            assert.equal(row.haConceptId, null);
            assert.equal(row.sourceOnly, true);
            assert.equal(row.humanReview, 'not_performed');
            assert.equal(row.publicRedistribution, 'held');
            assert.equal(row.names.koModern, target.koModern);
            assert.equal(row.names.koTraditional, target.koTraditional);
            assert.equal(row.names.en.toLocaleLowerCase(), relation.targetEnglish);
            assert(row.aliases.includes(target.latin));
            assert(!/\p{Script=Han}/u.test(row.names.koModern!));
            assert(!/\p{Script=Han}/u.test(row.names.koTraditional!));
            for (const field of ['koModern', 'koTraditional', 'en'] as const) {
                const fieldEvidence = row.nameEvidence?.[field];
                assert(fieldEvidence);
                assert.equal(fieldEvidence.value, row.names[field]);
                assert(fieldEvidence.sourceIds.length > 0);
            }
        }
        for (const query of [target.koModern, target.koTraditional, target.latin])
            assert(searchStructures(raw.objects, query, []).some(row => row.targetId === target.targetId), `${target.targetId}:${query}`);
    }
    assert.equal(raw.objects.length, 960);
    assert.equal(raw.objects.filter(row => row.localDisplayEligible).length, 672);
    assert.equal(raw.objects.filter(row => row.haConceptId).length, 130);
});
test('T100 B01 evidence refs and direct crosswalk proof fail closed when altered', () => {
    const badName = structuredClone(raw);
    const named = badName.objects.find(row => row.nameEvidence)!;
    named.nameEvidence!.koModern!.sourceIds = ['missing-source'];
    assert.throws(() => validateIntegration(badName, fixture));
    const badRelation = structuredClone(raw);
    const mapped = badRelation.objects.find(row => row.targetRelationEvidence)!;
    mapped.targetRelationEvidence![0].ancestorNameAloneUsed = true;
    assert.throws(() => validateIntegration(badRelation, fixture));
});
test('T100 B02 classifies ten exact vertebral/variant targets and links only nineteen verified source members', () => {
    const batchIds = new Set(vertebralBatch.targets.map(target => target.targetId));
    const terms = (raw.targetTerminologyEvidence ?? []).filter(term => batchIds.has(term.targetId));
    const relations = raw.objects.flatMap(row => (row.targetRelationEvidence ?? []).filter(relation => batchIds.has(relation.targetId)).map(relation => ({ row, relation })));
    assert.equal(vertebralBatch.targets.length, 10);
    assert.equal(terms.length, 10);
    assert.equal(vertebralBatch.crosswalkRelations.length, 19);
    assert.equal(relations.length, 19);
    assert.deepEqual([...new Set(relations.map(x => x.relation.targetId))].sort(), ['TA2:1032', 'TA2:1038', 'TA2:1050', 'TA2:1059']);
    assert.equal(relations.filter(x => x.relation.targetId === 'TA2:1032').length, 5);
    assert.equal(relations.filter(x => x.relation.targetId === 'TA2:1038').length, 1);
    assert.equal(relations.filter(x => x.relation.targetId === 'TA2:1050').length, 1);
    assert.equal(relations.filter(x => x.relation.targetId === 'TA2:1059').length, 12);
    for (const { row, relation } of relations) {
        assert.equal(relation.sourceKey, row.sourceKey);
        assert.equal(relation.sourceObjectName, row.sourceName);
        assert.equal(relation.sourceDataName, row.sourceName.replace(/\.[lr]$/i, ''));
        assert.equal(relation.directObjectNameMatch, false);
        assert.equal(relation.ancestorNameAloneUsed, false);
        assert.equal(relation.canonicalHaBindingCreated, false);
        assert.equal(row.haConceptId, null);
        assert.equal(row.sourceOnly, true);
        assert.equal(row.humanReview, 'not_performed');
        assert.equal(row.publicRedistribution, 'held');
        assert(relation.matchEvidenceSourceIds?.length);
        assert(/^[CT](?:[1-9]|1[0-2])$/.test(relation.sourceSegmentCode ?? ''));
    }
    const byId = new Map(terms.map(term => [term.targetId, term]));
    assert.deepEqual([...batchIds].filter(id => !byId.has(id)), []);
    assert.equal(byId.get('TA2:356')?.existingSurface.status, 'group_surface_missing_composition_conflicted');
    assert.equal(byId.get('TA2:819')?.existingSurface.status, 'variant_surface_missing');
    assert.equal(byId.get('TA2:830')?.existingSurface.status, 'group_surface_missing');
    assert.equal(byId.get('TA2:831')?.existingSurface.status, 'exact_surface_missing');
    assert.equal(byId.get('TA2:832')?.existingSurface.status, 'exact_surface_missing');
    assert.equal(byId.get('TA2:1065')?.existingSurface.status, 'subset_membership_unresolved');
    assert.equal(byId.get('TA2:831')?.names.koModern, '봉합뼈'); // evidence only; no source surface binding.
    for (const query of ['고리뼈', '환추골', '셋째 목뼈', '중쇠뼈', '열두째 등뼈']) {
        const results = searchStructures(raw.objects, query, []);
        assert(results.some(row => ['TA2:1032', 'TA2:1038', 'TA2:1050', 'TA2:1059'].some(id => row.targetIds.includes(id))), query);
    }
    assert(!searchStructures(raw.objects, '봉합뼈', []).some(row => row.targetIds.includes('TA2:831')));
    assert.equal(raw.policy.publicRedistribution, 'held');
    assert(terms.every(term => term.sourceOnly && term.learnerBindingCreated === false && term.canonicalHaConceptId === null
        && term.humanReview === 'not_performed' && term.publicRedistribution === 'held' && term.newGeometryCreated === false));
    assert.equal(raw.objects.length, 960);
    assert.equal(raw.objects.filter(row => row.localDisplayEligible).length, 672);
    assert.equal(raw.objects.filter(row => row.haConceptId).length, 130);
});
test('T100 B02 rejects unsupported segment/member relations and target-name evidence without provenance', () => {
    const badMember = structuredClone(raw);
    const member = badMember.objects.find(row => row.sourceName === 'Vertebra C3')!;
    member.targetRelationEvidence![0].sourceSegmentCode = 'C8';
    assert.throws(() => validateIntegration(badMember, fixture));
    const badTerm = structuredClone(raw);
    badTerm.targetTerminologyEvidence![0].fieldEvidence.koModern.sourceIds = ['missing-source'];
    assert.throws(() => validateIntegration(badTerm, fixture));
});
test('T100 B03 adds only ten terminology dispositions and 45 exact lumbar, ordinary-rib and carpal class members', () => {
    const batchIds = new Set(lumbarRibHandBatch.targets.map(target => target.targetId));
    const terms = (raw.targetTerminologyEvidence ?? []).filter(term => batchIds.has(term.targetId));
    const relations = raw.objects.flatMap(row => (row.targetRelationEvidence ?? [])
        .filter(relation => batchIds.has(relation.targetId)).map(relation => ({ row, relation })));
    assert.equal(lumbarRibHandBatch.scope.targetCount, 10);
    assert.equal(terms.length, 10);
    assert.equal(lumbarRibHandBatch.crosswalkRelations.length, 45);
    assert.equal(relations.length, 45);
    assert.equal(new Set(relations.map(x => x.relation.sourceKey)).size, 45);
    assert.deepEqual(lumbarRibHandBatch.memberCountsByTarget, {
        'TA2:1068': 5, 'TA2:1115': 0, 'TA2:1116': 0, 'TA2:1117': 0, 'TA2:1118': 24,
        'TA2:1137': 0, 'TA2:1138': 0, 'TA2:1248': 0, 'TA2:1249': 16, 'TA2:1262': 0,
    });
    assert.deepEqual([...new Set(relations.map(x => x.relation.targetId))].sort(), ['TA2:1068', 'TA2:1118', 'TA2:1249']);
    for (const { row, relation } of relations) {
        assert.equal(relation.sourceKey, row.sourceKey);
        assert.equal(relation.sourceObjectName, row.sourceName);
        assert.equal(relation.sourceSide, row.side);
        assert.equal(relation.relationKind, 'class_member');
        assert.equal(relation.directObjectNameMatch, false);
        assert.equal(relation.ancestorNameAloneUsed, false);
        assert.equal(relation.upstreamFjOrTa2IdClaim, false);
        assert.equal(relation.canonicalHaBindingCreated, false);
        assert.equal(row.haConceptId, null);
        assert.equal(row.sourceOnly, true);
        assert.equal(row.humanReview, 'not_performed');
        assert.equal(row.publicRedistribution, 'held');
        assert(!row.nameEvidence);
        assert.equal(row.names.en, relation.sourceDataName);
    }
    for (const target of terms) {
        assert.equal(target.sourceOnly, true);
        assert.equal(target.learnerBindingCreated, false);
        assert.equal(target.canonicalHaConceptId, null);
        assert.equal(target.humanReview, 'not_performed');
        assert.equal(target.publicRedistribution, 'held');
        assert.equal(target.newGeometryCreated, false);
        for (const value of [target.names.koModern, target.names.koTraditional])
            if (value) assert(!/\p{Script=Han}/u.test(value));
    }
    const byId = new Map(terms.map(term => [term.targetId, term]));
    assert.equal(byId.get('TA2:1117')?.names.koModern, null);
    assert.equal(byId.get('TA2:1137')?.names.koModern, null);
    assert.equal(byId.get('TA2:1262')?.names.koTraditional, null);
    assert.equal(byId.get('TA2:1248')?.existingSurface.status, 'aggregate_surface_missing_descendant_members_not_bound_to_parent');
    assert.equal(byId.get('TA2:1249')?.existingSurface.status, 'partial_eight_named_class_members_sixteen_surfaces_accessory_child_missing');
    assert.equal((byId.get('TA2:1249')?.existingSurface as { sourceMembers?: unknown[] })?.sourceMembers?.length, 16);
    assert.equal(relations.filter(x => x.relation.targetId === 'TA2:1068').length, 5);
    assert.equal(relations.filter(x => x.relation.targetId === 'TA2:1118').length, 24);
    assert.equal(relations.filter(x => x.relation.targetId === 'TA2:1249').length, 16);
    const leftCarpal = relations.find(x => x.relation.sourceObjectName === 'Scaphoid bone.l')!;
    assert.equal(leftCarpal.relation.sourceSide, 'left');
    assert(leftCarpal.relation.sourceCollections.includes('Right hand')); // known collection label conflict; suffix/sourceSide decide side.
    assert(leftCarpal.relation.sourceCollections.includes('Left upper limb'));
    assert.equal(raw.scope.targets, 542);
    assert.equal(raw.scope.memberships, 563);
    assert.equal(raw.scope.regions, 12);
    for (const target of lumbarRibHandBatch.targets) {
        for (const query of [target.names.koModern, target.names.koTraditional].filter(Boolean) as string[]) {
            assert(!searchStructures(raw.objects, query, []).some(row => row.targetIds.includes(target.targetId)),
                'internal B03 terminology leaked into learner search: ' + target.targetId + ':' + query);
        }
    }
});
test('T100 B03 rejects wrong sides, parents, member keys, unsupported variants and missing field provenance', () => {
    const wrongSide = structuredClone(raw);
    const rib = wrongSide.objects.find(row => row.sourceName === 'First rib.l')!;
    rib.targetRelationEvidence!.find(relation => relation.targetId === 'TA2:1118')!.sourceSide = 'right';
    assert.throws(() => validateIntegration(wrongSide, fixture));
    const wrongParent = structuredClone(raw);
    const lumbar = wrongParent.objects.find(row => row.sourceName === 'Vertebra L1')!;
    lumbar.targetRelationEvidence!.find(relation => relation.targetId === 'TA2:1068')!.sourceParent = 'Thoracic vertebrae.g';
    assert.throws(() => validateIntegration(wrongParent, fixture));
    const wrongMember = structuredClone(raw);
    const carpal = wrongMember.objects.find(row => row.sourceName === 'Scaphoid bone.l')!;
    carpal.targetRelationEvidence!.find(relation => relation.targetId === 'TA2:1249')!.memberCode = 'carpal:hamate';
    assert.throws(() => validateIntegration(wrongMember, fixture));
    const wrongVariant = structuredClone(raw);
    const ordinary = wrongVariant.objects.find(row => row.sourceName === 'First rib.l')!;
    ordinary.targetIds.push('TA2:1116');
    ordinary.targetRelationEvidence!.find(relation => relation.targetId === 'TA2:1118')!.targetId = 'TA2:1116';
    assert.throws(() => validateIntegration(wrongVariant, fixture));
    const missingRef = structuredClone(raw);
    missingRef.targetTerminologyEvidence!.find(term => term.targetId === 'TA2:1117')!.fieldEvidence.koModern.sourceIds = ['not-a-source'];
    assert.throws(() => validateIntegration(missingRef, fixture));
});
test('T100 B04 records hand-bone members without leaking internal target terminology to learner search', () => {
    const batchIds = new Set(handPelvisBatch.targets.map(target => target.targetId));
    const terms = (raw.targetTerminologyEvidence ?? []).filter(term => batchIds.has(term.targetId));
    const relations = raw.objects.flatMap(row => (row.targetRelationEvidence ?? [])
        .filter(relation => batchIds.has(relation.targetId)).map(relation => ({ row, relation })));
    assert.equal(handPelvisBatch.scope.targetCount, 10);
    assert.equal(terms.length, 10);
    assert.equal(handPelvisBatch.crosswalkRelations.length, 101);
    assert.equal(relations.length, 101);
    assert.equal(new Set(relations.map(x => x.relation.sourceKey)).size, 37);
    assert.deepEqual(handPelvisBatch.memberCountsByTarget, {
        'TA2:1263': 0, 'TA2:1264': 10, 'TA2:1265': 10, 'TA2:1271': 27, 'TA2:1272': 27,
        'TA2:1277': 10, 'TA2:1278': 8, 'TA2:1279': 9, 'TA2:1281': 0, 'TA2:1282': 0,
    });
    const bySourceTarget = new Set(handPelvisBatch.crosswalkRelations.map(r => `${r.targetId}:${r.sourceKey}`));
    for (const { row, relation } of relations) {
        assert.equal(relation.sourceKey, row.sourceKey);
        assert.equal(relation.sourceObjectName, row.sourceName);
        assert.equal(relation.sourceSide, row.side);
        assert.equal(relation.relationKind, 'class_member');
        assert.equal(relation.directObjectNameMatch, false);
        assert.equal(relation.ancestorNameAloneUsed, false);
        assert.equal(relation.upstreamFjOrTa2IdClaim, false);
        assert.equal(relation.canonicalHaBindingCreated, false);
        assert.equal(row.haConceptId, null);
        assert.equal(row.sourceOnly, true);
        assert.equal(row.humanReview, 'not_performed');
        assert.equal(row.publicRedistribution, 'held');
        assert(bySourceTarget.has(`${relation.targetId}:${relation.sourceKey}`));
        assert(relation.memberCode);
    }
    const byId = new Map(terms.map(term => [term.targetId, term]));
    assert.equal(byId.get('TA2:1264')?.names.koModern, '손허리뼈(첫째-다섯째)');
    assert.equal(byId.get('TA2:1265')?.names.koModern, '손허리뼈');
    for (const targetId of ['TA2:1263', 'TA2:1271', 'TA2:1272', 'TA2:1277', 'TA2:1278', 'TA2:1279', 'TA2:1281', 'TA2:1282']) {
        assert.equal(byId.get(targetId)?.names.koModern, null);
        assert.equal(byId.get(targetId)?.names.koTraditional, null);
    }
    assert.equal(byId.get('TA2:1279')?.existingSurface.status, 'nine_exact_members_one_identity_conflict_excluded');
    assert.equal(byId.get('TA2:1282')?.existingSurface.status, 'candidate_collection_members_observed_not_crosswalked');
    assert.equal(byId.get('TA2:1281')?.existingSurface.status, 'hand_group_surface_missing');
    assert.equal(terms.every(term => term.learnerBindingCreated === false && term.canonicalHaConceptId === null
        && term.sourceOnly && term.humanReview === 'not_performed' && term.publicRedistribution === 'held'
        && term.newGeometryCreated === false), true);
    for (const term of terms) {
        for (const query of [term.names.koModern, term.names.koTraditional].filter(Boolean) as string[]) {
            assert(!searchStructures(raw.objects, query, []).some(row => row.targetIds.some(id => batchIds.has(id))),
                `internal B04 terminology leaked into learner search: ${term.targetId}:${query}`);
        }
    }
});
test('T100 B04 rejects the fifth distal data-name conflict and wrong side/member evidence', () => {
    const knownConflict = structuredClone(raw);
    const conflictRow = knownConflict.objects.find(row => row.sourceName === 'Distal phalanx of fifth finger of hand.l')!;
    assert(!conflictRow.targetRelationEvidence?.some(relation => ['TA2:1271', 'TA2:1272', 'TA2:1279'].includes(relation.targetId)));

    const wronglyLinkedConflict = structuredClone(raw);
    const badConflictRow = wronglyLinkedConflict.objects.find(row => row.sourceName === 'Distal phalanx of fifth finger of hand.l')!;
    const rightDistal = wronglyLinkedConflict.objects.find(row => row.sourceName === 'Distal phalanx of fifth finger of hand.r')!;
    const fakeConflictRelation = structuredClone(rightDistal.targetRelationEvidence!.find(relation => relation.targetId === 'TA2:1279')!);
    fakeConflictRelation.sourceKey = badConflictRow.sourceKey;
    fakeConflictRelation.sourceObjectName = badConflictRow.sourceName;
    fakeConflictRelation.sourceDataName = 'Distal phalanx of fifth finger of hand.r';
    fakeConflictRelation.sourceCollections = ['1: Skeletal system', 'Appendicular skeleton', 'Bonus collection', 'Left upper limb', 'Right hand'];
    fakeConflictRelation.sourceSide = 'left';
    fakeConflictRelation.evaluatedGeometrySha256 = rightDistal.targetRelationEvidence!.find(relation => relation.targetId === 'TA2:1279')!.evaluatedGeometrySha256;
    fakeConflictRelation.memberCode = 'distal:fifth:left';
    badConflictRow.targetIds.push('TA2:1279');
    badConflictRow.targetRelationEvidence = [...(badConflictRow.targetRelationEvidence ?? []), fakeConflictRelation];
    assert.throws(() => validateIntegration(wronglyLinkedConflict, fixture));

    const wrongSide = structuredClone(raw);
    const member = wrongSide.objects.find(row => row.sourceName === 'First metacarpal bone.l')!;
    member.targetRelationEvidence!.find(relation => relation.targetId === 'TA2:1264')!.sourceSide = 'right';
    assert.throws(() => validateIntegration(wrongSide, fixture));

    const wrongMember = structuredClone(raw);
    const middle = wrongMember.objects.find(row => row.sourceName === 'Middle phalanx of second finger of hand.l')!;
    middle.targetRelationEvidence!.find(relation => relation.targetId === 'TA2:1278')!.memberCode = 'middle:first:left';
    assert.throws(() => validateIntegration(wrongMember, fixture));

    const wrongLevel = structuredClone(raw);
    const proximal = wrongLevel.objects.find(row => row.sourceName === 'Proximal phalanx of second finger of hand.l')!;
    proximal.targetRelationEvidence!.find(relation => relation.targetId === 'TA2:1277')!.memberCode = 'distal:second:left';
    assert.throws(() => validateIntegration(wrongLevel, fixture));
});
test('T100 B05 records ten pelvis/knee/foot targets and exact existing class members without search leakage', () => {
    const batchIds = new Set(pelvisLowerLimbBatch.scope.requestedTargetIds);
    const terms = (raw.targetTerminologyEvidence ?? []).filter(term => batchIds.has(term.targetId));
    const relations = raw.objects.flatMap(row => (row.targetRelationEvidence ?? [])
        .filter(relation => batchIds.has(relation.targetId)).map(relation => ({ row, relation })));
    assert.equal(pelvisLowerLimbBatch.scope.targetCount, 10);
    assert.equal(terms.length, 10);
    assert.equal(pelvisLowerLimbBatch.crosswalkRelations.length, 58);
    assert.equal(relations.length, 58);
    assert.equal(pelvisLowerLimbBatch.uniqueSourceObjects, 40);
    assert.equal(new Set(relations.map(x => x.relation.sourceKey)).size, 40);
    assert.deepEqual(pelvisLowerLimbBatch.memberCountsByTarget, {
        'TA2:1317': 0, 'TA2:1339': 0, 'TA2:1346': 0, 'TA2:1389': 2, 'TA2:1493': 0,
        'TA2:1494': 0, 'TA2:1496': 10, 'TA2:1505': 28, 'TA2:1510': 10, 'TA2:1511': 8,
    });
    assert.equal(pelvisLowerLimbBatch.scope.taskTargetDenominator, 542);
    assert.equal(pelvisLowerLimbBatch.scope.taskRegionMembershipDenominator, 563);
    assert.equal(pelvisLowerLimbBatch.scope.regions, 12);
    assert.equal(pelvisLowerLimbBatch.rightsAndReview.sourceOnly, true);
    assert.equal(pelvisLowerLimbBatch.rightsAndReview.publicRedistribution, 'held');
    assert.equal(pelvisLowerLimbBatch.rightsAndReview.humanReview, 'not_performed');
    assert(pelvisLowerLimbBatch.sourceEvidence.some(source => source.accessMethod === 'opened_pdf' && source.openedOriginalSourcePage));
    for (const { row, relation } of relations) {
        assert.equal(relation.sourceKey, row.sourceKey);
        assert.equal(relation.sourceObjectName, row.sourceName);
        assert.equal(relation.sourceSide, row.side);
        assert.equal(relation.relationKind, 'class_member');
        assert.equal(relation.directObjectNameMatch, false);
        assert.equal(relation.ancestorNameAloneUsed, false);
        assert.equal(relation.upstreamFjOrTa2IdClaim, false);
        assert.equal(relation.canonicalHaBindingCreated, false);
        assert.equal(row.humanReview, 'not_performed');
        assert.equal(row.publicRedistribution, 'held');
        assert(relation.memberCode);
    }
    const byId = new Map(terms.map(term => [term.targetId, term]));
    assert.equal(byId.get('TA2:1317')?.names.koModern, '엉덩뼈');
    assert.equal(byId.get('TA2:1317')?.names.koTraditional, '장골');
    assert.equal(byId.get('TA2:1339')?.names.koModern, '궁둥뼈');
    assert.equal(byId.get('TA2:1339')?.names.koTraditional, '좌골');
    assert.equal(byId.get('TA2:1346')?.names.koModern, '두덩뼈');
    assert.equal(byId.get('TA2:1346')?.names.koTraditional, '치골');
    assert.equal(byId.get('TA2:1494')?.names.koModern, '발세모뼈');
    assert.equal(byId.get('TA2:1494')?.names.koTraditional, '삼각골');
    assert.equal(byId.get('TA2:1496')?.names.koModern, '발허리뼈');
    assert.equal(byId.get('TA2:1496')?.names.koTraditional, '중족골');
    for (const targetId of ['TA2:1389', 'TA2:1493', 'TA2:1505', 'TA2:1510', 'TA2:1511']) {
        assert.equal(byId.get(targetId)?.names.koModern, null);
        assert.equal(byId.get(targetId)?.names.koTraditional, null);
    }
    assert.equal(byId.get('TA2:1389')?.existingSurface.status, 'partial_patella_members_only_fabella_and_cyamella_surface_missing');
    assert.equal(byId.get('TA2:1493')?.existingSurface.status, 'no_exact_accessory_tarsal_surface_in_frozen_source');
    assert.equal(byId.get('TA2:1505')?.existingSurface.status, '28_exactly_named_source_class_members');
    assert(terms.every(term => term.learnerBindingCreated === false && term.canonicalHaConceptId === null
        && term.sourceOnly && term.humanReview === 'not_performed' && term.publicRedistribution === 'held'
        && term.newGeometryCreated === false));
    const leftToe = relations.find(x => x.relation.sourceObjectName === 'Proximal phalanx of first finger of foot.l')!;
    assert.equal(leftToe.relation.sourceSide, 'left');
    assert(leftToe.relation.sourceCollections.includes('Right foot'));
    assert(leftToe.relation.sourceCollections.includes('Left lower limb'));
    for (const term of terms) {
        assert.equal(searchStructures(raw.objects, term.targetId, []).length, 0,
            `internal B05 target id leaked into learner search: ${term.targetId}`);
    }
    const existingMetatarsalSearch = searchStructures(raw.objects, '발허리뼈', []);
    assert.deepEqual(existingMetatarsalSearch.map(row => row.sourceName).sort(), ['Fifth metatarsal bone.l', 'First metatarsal bone.l']);
    assert(existingMetatarsalSearch.every(row => ['HA-S-METATARSAL-1', 'HA-S-METATARSAL-5'].includes(row.haConceptId ?? '')),
        'B05 term ledger must not be the source of pre-existing metatarsal learner labels');
});
test('T100 B05 rejects wrong laterality, foot part, member key, and parent', () => {
    const wrongSide = structuredClone(raw);
    const metatarsal = wrongSide.objects.find(row => row.sourceName === 'First metatarsal bone.l')!;
    metatarsal.targetRelationEvidence!.find(relation => relation.targetId === 'TA2:1496')!.sourceSide = 'right';
    assert.throws(() => validateIntegration(wrongSide, fixture));

    const wrongMember = structuredClone(raw);
    const toe = wrongMember.objects.find(row => row.sourceName === 'Middle phalanx of second finger of foot.l')!;
    toe.targetRelationEvidence!.find(relation => relation.targetId === 'TA2:1511')!.memberCode = 'middle:first:left';
    assert.throws(() => validateIntegration(wrongMember, fixture));

    const wrongLevel = structuredClone(raw);
    const proximal = wrongLevel.objects.find(row => row.sourceName === 'Proximal phalanx of first finger of foot.l')!;
    proximal.targetRelationEvidence!.find(relation => relation.targetId === 'TA2:1510')!.sourceObjectName = 'Middle phalanx of first finger of foot.l';
    assert.throws(() => validateIntegration(wrongLevel, fixture));

    const wrongParent = structuredClone(raw);
    const patella = wrongParent.objects.find(row => row.sourceName === 'Patella.l')!;
    patella.targetRelationEvidence!.find(relation => relation.targetId === 'TA2:1389')!.sourceParent = 'Patella.g';
    assert.throws(() => validateIntegration(wrongParent, fixture));

    const fakeAccess = structuredClone(raw);
    (fakeAccess.evidenceSources!.find(source => source.id === 'koa-t100-b05-accessory-tarsal-paper-opened') as unknown as { accessMethod: string }).accessMethod = 'opened_blender';
    assert.throws(() => validateIntegration(fakeAccess, fixture));
});
test('both scapulae belong to arm context and sacrum to lumbar context', () => {
    const scap = raw.objects.filter(r => r.names.en === 'Scapula');
    assert.equal(scap.length, 2);
    assert(scap.every(r => r.regionIds.includes('upper-limb')));
    assert(raw.objects.filter(r => r.names.en === 'Sacrum').every(r => r.regionIds.includes('abdomen-lumbar')));
});
test('accessories remain retained without masquerading as muscle/bone', () => {
    const rows = raw.objects.filter(r => /cartilage|tendon|retinaculum|ligament/i.test(r.sourceName));
    assert(rows.length > 0);
    assert(rows.every(r => r.kind === 'accessory' && !r.localDisplayEligible));
});
test('stable source route roundtrips, old bound HA route resolves side, invalid/filtered keys stay unselected', () => {
    const row = raw.objects.find(r => r.haConceptId && r.side === 'right')!;
    const ids = [...new Set(raw.objects.flatMap(r => r.regionIds))];
    const route = { regions: row.regionIds, selected: row.sourceKey };
    assert.deepEqual(readDatasetRoute('?' + datasetRouteQuery(route), raw.objects, ids), route);
    assert.equal(readDatasetRoute('?id=' + row.haConceptId + '&side=right', raw.objects, ids).selected, row.sourceKey);
    assert.equal(readDatasetRoute('?source=unknown', raw.objects, ids).selected, null);
    assert.deepEqual(readDatasetRoute('', raw.objects, ids), { regions: [], selected: null });
});
