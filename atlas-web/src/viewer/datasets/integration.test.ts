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
