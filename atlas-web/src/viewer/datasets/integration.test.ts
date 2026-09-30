import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { gzipSync } from 'node:zlib';
import { readFileSync } from 'node:fs';
import { buildRuntimeIntegration, validateRuntimeIntegration, validateIntegration as validateIntegrationWithCatalog, searchStructures, canDisplayLocally, readDatasetRoute, datasetRouteQuery, type Integration, type FrozenTargetLexicon } from './integration.ts';
import type { Dataset } from './schema.ts';
const overlayBytes = readFileSync(new URL('../../../../atlas-data/overlays/za-local-integration.json', import.meta.url));
const raw = JSON.parse(overlayBytes.toString('utf8')) as Integration;
const targetScopeBytes = readFileSync(new URL('../../../../atlas-data/catalog/target-scope-t96.json', import.meta.url));
const targetScope = JSON.parse(targetScopeBytes.toString('utf8')) as {
    targets: Array<{ id: string; term: { english: string; latin: string; sourceSynonyms: Record<string, string[]> }; semanticKind: string; primaryOwner: string; regionIds: string[] }>;
};
const supportContextBytes = readFileSync(new URL('../../../../work/evidence/T78/reference/ta2-scope.json', import.meta.url));
const frozenTargetLexicon: FrozenTargetLexicon = {
    supportContext: { sha256: createHash('sha256').update(supportContextBytes).digest('hex'), terms: JSON.parse(supportContextBytes.toString()) },
    sha256: createHash('sha256').update(targetScopeBytes).digest('hex'),
    targets: targetScope.targets,
};
const validateIntegration = (value: unknown, dataset: Dataset) => validateIntegrationWithCatalog(value, dataset, frozenTargetLexicon);
const semanticBaseline = JSON.parse(readFileSync(new URL('../../../../work/evidence/T100/semantic-relations-2026-09-30/start-baseline.json', import.meta.url), 'utf8')) as {
    preexistingHaConceptBindings: Array<{ sourceKey: string; haConceptId: string }>;
    preservedUnnamedSurfaceState: Array<{ sourceKey: string; [key: string]: unknown }>;
};
const preexistingHaBySource = new Map(semanticBaseline.preexistingHaConceptBindings.map(binding => [binding.sourceKey, binding.haConceptId]));
const preservedUnnamedBySource = new Map(semanticBaseline.preservedUnnamedSurfaceState.map(row => [row.sourceKey, row]));
const directTargetLinkDelta = JSON.parse(readFileSync(new URL('../../../../work/evidence/T100/target-representation-2026-09-30/link-delta.json', import.meta.url), 'utf8')) as {
    change: { addedRows: number; uniqueTargetIds: number; sourceKindCounts: Record<string, number>; sourceOnlyCounts: Record<string, number>; sideCounts: Record<string, number> };
    entries: Array<{ sourceKey: string; sourceName: string; targetId: string; kind: string; side: string | null; regionIds: string[]; conceptKey: string; evaluatedGeometrySha256: string; link: NonNullable<Integration['objects'][number]['learnerConceptLinks']>[number] }>;
};
const targetMembershipContinuation = JSON.parse(readFileSync(new URL('../../../../work/evidence/T100/target-representation-continuation-2026-09-30/target-membership-plan-and-qa.json', import.meta.url), 'utf8')) as {
    addedClassMemberLinks: Array<{ sourceKey: string; targetIds: string[]; memberCode: string; link: NonNullable<Integration['objects'][number]['learnerConceptLinks']>[number] }>;
    taxonomyMemberLinks: Array<{ sourceKey: string; targetId: string; childTargetId: string; link: NonNullable<Integration['objects'][number]['learnerConceptLinks']>[number] }>;
    targetRegionMembershipSelection: Array<{ targetId: string; regionId: string; status: string; selectionRoutes: Array<{ sourceKey: string; side: string | null; relationKind: string; conceptKey: string; routeResolvesToExactSourceAndRegion: boolean }> }>;
    routeFailureCount: number;
    termGapCount: number;
    unresolvedTargetDisposition: Record<string, { status: string }>;
    denominators: { scopeTargets: number; scopeMemberships: number; regions: number; sourceObjects: number; localDisplayEligible: number; existingHaBindings: number; historicalCandidateFree163: number };
    rightsAndIdentityInvariants: { newCanonicalHaBindings: number; humanReview: string; publicRedistribution: string; sourceOnly: boolean; newGeometry: number; TA2DenominatorChanged: boolean };
};
const compiled = JSON.parse(readFileSync(new URL('../../../../atlas-data/source-cache/datasets/za/compiled/manifest.json', import.meta.url), 'utf8')) as {
    revision: string;
    instances: Array<{ sourceKey: string; kind: string; lods: { detail: { resource: string } } }>;
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
        sourceName: row.sourceName,
        kind: datasetInstances.get(row.sourceKey)?.kind,
        lods: { detail: { resource: datasetInstances.get(row.sourceKey)?.lods.detail.resource } },
    })),
} as Dataset;
const runtimeOverlaySha256 = createHash('sha256').update(overlayBytes).digest('hex');
const runtime = buildRuntimeIntegration(raw, fixture, runtimeOverlaySha256, raw.policy.rightsEvidenceSha256, frozenTargetLexicon);
test('whole-source overlay retains records and independent release/review status', () => {
    const overlay = validateIntegration(raw, fixture);
    assert.equal(overlay.objects.length, 960);
    assert.equal(overlay.objects.filter(r => r.localDisplayEligible).length, 672);
    assert(overlay.objects.every(r => r.publicRedistribution === 'held' && r.humanReview === 'not_performed'));
    assert.equal(new Set(overlay.objects.flatMap(r => r.regionIds)).size, 12);
});
test('common projection preserves learner/search/selection fields and strips the developer evidence ledger', () => {
    const projected = validateRuntimeIntegration(runtime, fixture);
    assert.equal(projected.objects.length, 960);
    assert.deepEqual(projected.scope, { targets: 542, memberships: 563, regions: 12 });
    assert.equal(projected.objects.filter(r => r.localDisplayEligible).length, 672);
    assert.equal(projected.objects.filter(r => r.haConceptId).length, 130);
    assert(projected.objects.every(r => r.publicRedistribution === 'held' && r.humanReview === 'not_performed'));
    assert.deepEqual(projected.objects.map(r => r.sourceKey), raw.objects.map(r => r.sourceKey));
    for (let index = 0; index < raw.objects.length; index++) {
        const source = raw.objects[index], output = projected.objects[index];
        assert.deepEqual({ label: output.label, names: output.names, aliases: output.aliases, kind: output.kind, regionIds: output.regionIds,
            side: output.side, haConceptId: output.haConceptId, localDisplayEligible: output.localDisplayEligible,
            inspectionEligible: output.inspectionEligible, defaultVisible: output.defaultVisible, sourceOnly: output.sourceOnly,
            hidden: output.sourceHiddenStatePreserved, localUseRights: output.localUseRights, displayDecisionBasis: output.displayDecisionBasis,
            hardHoldReasons: output.hardHoldReasons, bounds: output.bounds, relatedMuscles: output.relatedMuscles },
        { label: source.label, names: source.names, aliases: source.aliases, kind: source.kind, regionIds: source.regionIds,
            side: source.side, haConceptId: source.haConceptId, localDisplayEligible: source.localDisplayEligible,
            inspectionEligible: source.inspectionEligible, defaultVisible: source.defaultVisible, sourceOnly: source.sourceOnly,
            hidden: source.sourceHiddenStatePreserved, localUseRights: source.localUseRights, displayDecisionBasis: source.displayDecisionBasis,
            hardHoldReasons: source.hardHoldReasons, bounds: source.bounds, relatedMuscles: source.relatedMuscles ?? [] });
        assert.equal(output.searchGroupKey, source.sourceName.replace(/\.[lr]$/, ''));
    }
    const forbidden = /TA2:\d+|targetTerminologyEvidence|targetRelationEvidence|evidenceSources|nameEvidence|locator|work\/evidence|https?:\/\//;
    const serialized = JSON.stringify(projected);
    assert.equal(forbidden.test(serialized), false);
    assert(!('targetId' in projected.objects[0]) && !('sourceName' in projected.objects[0]));
    assert(Buffer.byteLength(serialized) < Math.floor(Buffer.byteLength(JSON.stringify(raw)) * .6));
    assert(gzipSync(serialized).byteLength < Buffer.byteLength(serialized));
});
test('common search and stable routes match the full validated ledger across names, sides and all regions', () => {
    const queries = ['이마뼈', '마루뼈', '고리뼈', '중쇠뼈', '허리뼈', '갈비뼈', '손목뼈', '손허리뼈', '첫째 발허리뼈',
        '승모근 상부', '승모근 하부', '광배근', '넓은등근', 'latissimus', 'spleinus'];
    for (const query of queries) {
        assert.deepEqual(searchStructures(runtime.objects, query, []).map(r => [r.sourceKey, r.searchApproximate]),
            searchStructures(raw.objects, query, []).map(r => [r.sourceKey, r.searchApproximate]), query);
    }
    for (const region of [...new Set(raw.objects.flatMap(row => row.regionIds))]) {
        assert.deepEqual(searchStructures(runtime.objects, '', [region]).map(r => r.sourceKey),
            searchStructures(raw.objects, '', [region]).map(r => r.sourceKey), region);
    }
    for (const row of raw.objects.filter(row => row.localDisplayEligible)) {
        const query = '?source=' + encodeURIComponent(row.sourceKey);
        assert.deepEqual(readDatasetRoute(query, runtime.objects, [...new Set(raw.objects.flatMap(x => x.regionIds))]),
            readDatasetRoute(query, raw.objects, [...new Set(raw.objects.flatMap(x => x.regionIds))]));
    }
    assert.equal(searchStructures(runtime.objects, '승모근 상부', []).map(row => row.names.en).filter(name => /Descending/.test(name)).length, 1);
    assert.equal(searchStructures(runtime.objects, '승모근 하부', []).map(row => row.names.en).filter(name => /Ascending/.test(name)).length, 1);
});
test('runtime projection fails closed on stale inputs, policy drift, forbidden fields and incomplete identity', () => {
    assert.throws(() => buildRuntimeIntegration(raw, fixture, runtimeOverlaySha256, '0'.repeat(64), frozenTargetLexicon));
    assert.throws(() => validateRuntimeIntegration(runtime, { ...fixture, revision: 'stale' } as Dataset));
    for (const mutate of [
        (value: any) => { value.objects.pop(); },
        (value: any) => { value.objects[1] = value.objects[0]; },
        (value: any) => { value.policy.localOnly = false; },
        (value: any) => { value.policy.publicRedistribution = 'allowed'; },
        (value: any) => { value.policy.humanReview = 'reviewed'; },
        (value: any) => { value.objects[0].localDisplayEligible = !value.objects[0].localDisplayEligible; },
        (value: any) => { value.objects[0].targetRelationEvidence = []; },
        (value: any) => { value.objects[0].relatedMuscles = [{ sourceKey: 'missing', label: '근육', roles: ['origin'] }]; },
        (value: any) => { value.rightsEvidenceSha256 = 'bad'; },
    ]) {
        const bad = structuredClone(runtime);
        mutate(bad);
        assert.throws(() => validateRuntimeIntegration(bad, fixture));
    }
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
test('T100 ordinal-composed modern-only names accept field-scoped evidence without inventing legacy or Latin fields', () => {
    const modernOnly = structuredClone(raw);
    const rib = modernOnly.objects.find(row => row.sourceName === 'Eighth rib.l')!;
    assert.equal(rib.names.koModern, '여덟째갈비뼈');
    assert.equal(rib.names.koTraditional, '제8늑골');
    assert.equal(rib.nameEvidence?.koTraditional?.value, rib.names.koTraditional);
    assert.doesNotThrow(() => validateIntegration(modernOnly, fixture));

    const mismatched = structuredClone(modernOnly);
    mismatched.objects.find(row => row.sourceName === 'Eighth rib.l')!.nameEvidence!.koModern!.value = '오른쪽갈비뼈';
    assert.throws(() => validateIntegration(mismatched, fixture));
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
        assert.equal(row.names.en, relation.sourceDataName);
        if (/^(Vertebra L[1-5]|(?:First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Twelfth) rib\.[lr])$/i.test(row.sourceName)) {
            assert(row.nameEvidence?.koModern, `later T100 ordinal naming evidence missing: ${row.sourceName}`);
            assert.equal(row.nameEvidence!.koModern!.value, row.names.koModern);
            assert(row.names.koTraditional === null || row.nameEvidence?.koTraditional?.value === row.names.koTraditional);
        }
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
            const matches = searchStructures(raw.objects, query, []);
            const targetMemberMatches = matches.filter(row => row.targetIds.includes(target.targetId));
            if ((target.targetId === 'TA2:1068' || target.targetId === 'TA2:1118') && (query === target.names.koModern || targetMemberMatches.length > 0)) {
                assert(targetMemberMatches.length > 0,
                    'later T100 exact ordinal member names should search through the existing B03 class-member surfaces');
                assert(targetMemberMatches.every(row => row.nameEvidence?.koModern?.value === row.names.koModern
                    && row.nameEvidence.koModern.sourceIds.length > 0));
            } else {
                assert.equal(targetMemberMatches.length, 0,
                    'target-only B03 terminology or unsupported target names must not create a learner search row: ' + target.targetId + ':' + query);
            }
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
            const matches = searchStructures(raw.objects, query, []);
            for (const row of matches.filter(candidate => candidate.targetIds.some(id => batchIds.has(id)))) {
                // A source surface may independently carry a directly evidenced Korean name.
                // Its exact English locator is distinct from projecting the internal target term.
                assert.equal(row.nameEvidence?.koModern?.value, row.names.koModern,
                    `B04 terminology was projected without surface-level name evidence: ${term.targetId}:${query}`);
                if (row.nameEvidence?.koModern?.sourceIds.some(id => id.startsWith('kli-t100-'))) {
                    assert(row.nameEvidence.koModern.locator.includes('구성명')
                        && row.learnerConceptLinks?.some(link => link.relationKind === 'verified_class_member'),
                    `T100 composed source name lacks member relation evidence: ${term.targetId}:${query}:${row.sourceName}`);
                } else {
                    assert(row.names.en && row.nameEvidence?.koModern?.locator.includes(row.names.en),
                        `B04 query matched a surface without its own exact English locator: ${term.targetId}:${query}:${row.sourceName}`);
                }
            }
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
    const metatarsalSearch = searchStructures(raw.objects, '발허리뼈', []);
    assert.deepEqual(metatarsalSearch.map(row => row.sourceName).sort(), [
        'Fifth metatarsal bone.l', 'First metatarsal bone.l', 'Fourth metatarsal bone.l',
        'Second metatarsal bone.l', 'Third metatarsal bone.l',
    ]);
    const metatarsalByName = new Map(raw.objects.filter(row => /^(First|Second|Third|Fourth|Fifth) metatarsal bone\.[lr]$/i.test(row.sourceName)).map(row => [row.sourceName, row]));
    for (const [sourceName, stableId] of [['First metatarsal bone.l', 'HA-S-METATARSAL-1'], ['Fifth metatarsal bone.l', 'HA-S-METATARSAL-5']] as const)
        assert.equal(metatarsalSearch.find(row => row.sourceName === sourceName)?.haConceptId, stableId,
            'B05 must preserve the pre-existing first/fifth learner rows');
    for (const sourceName of ['Second metatarsal bone.l', 'Third metatarsal bone.l', 'Fourth metatarsal bone.l']) {
        const row = metatarsalByName.get(sourceName)!;
        assert(metatarsalSearch.some(result => result.sourceName === sourceName));
        assert.equal(row.haConceptId, null, 'ordinal display composition must not create a learner binding');
        const rightName = sourceName.replace('.l', '.r');
        assert.equal(metatarsalByName.get(rightName)?.names.koModern, row.names.koModern, 'the same exact ordinal term should stay bilateral on existing source mates');
    }
});
test('T100 B bulk exact group terms and ordinal compositions preserve semantic scope and field-level holds', () => {
    const exactGroups = new Map((raw.targetTerminologyEvidence ?? []).filter(row => [
        'TA2:1067', 'TA2:1104', 'TA2:1106', 'TA2:1113', 'TA2:1114', 'TA2:1495', 'TA2:2192',
    ].includes(row.targetId)).map(row => [row.targetId, row]));
    const expectedGroups = new Map([
        ['TA2:1067', ['lumbar vertebrae', '허리(척추)뼈(첫째-다섯째)', 5]],
        ['TA2:1104', ['bones of thorax', '가슴우리뼈', 27]],
        ['TA2:1106', ['true ribs', '참갈비뼈(첫째-일곱째)', 14]],
        ['TA2:1113', ['false ribs', '거짓갈비뼈(여덟째-열두째)', 10]],
        ['TA2:1114', ['floating ribs', '뜬갈비뼈(열한째-열두째)', 4]],
        ['TA2:1495', ['metatarsal bones', '발허리뼈(첫째-다섯째)', 10]],
        ['TA2:2192', ['laryngeal muscles', '후두근육', 15]],
    ]);
    assert.equal(exactGroups.size, expectedGroups.size);
    for (const [targetId, [english, modern, count]] of expectedGroups) {
        const term = exactGroups.get(targetId)!;
        assert.equal(term.english, english);
        assert.equal(term.names.koModern, modern);
        assert.equal(term.names.koTraditional !== null, true);
        assert.equal((term.existingSurface as { exactSourceObjects?: unknown[] }).exactSourceObjects?.length, count);
        assert.equal(term.learnerBindingCreated, false);
        assert.equal(term.humanReview, 'not_performed');
        assert.equal(term.publicRedistribution, 'held');
        assert.equal(searchStructures(raw.objects, targetId, []).length, 0);
    }

    const ordinalIds = ['kmle-t100-bulk-lumbar-vertebra-opened', 'kmle-t100-bulk-rib-opened', 'kmle-t100-bulk-metatarsal-bones-opened'];
    const ordinalRows = raw.objects.filter(row => row.nameEvidence?.koModern?.sourceIds.some(id => ordinalIds.includes(id)));
    assert.equal(ordinalRows.length, 35);
    assert(ordinalRows.every(row => row.names.koModern === row.nameEvidence?.koModern?.value
        && (row.names.koTraditional === null || row.nameEvidence?.koTraditional?.value === row.names.koTraditional) && row.haConceptId === null
        && row.sourceOnly && row.humanReview === 'not_performed' && row.publicRedistribution === 'held'));
    const laryngealMembers = raw.objects.filter(row => row.targetIds.includes('TA2:2192'));
    assert.equal(laryngealMembers.length, 15);
    assert(laryngealMembers.every(row => !ordinalRows.includes(row) && row.names.koModern !== '후두근육'));
    const rangeObservation = raw.evidenceSources?.find(row => row.id === 'kmle-t100-bulk-rib-opened');
    assert(rangeObservation);
    assert.equal(rangeObservation.openedOriginalDictionaryRecord, false);
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

test('T100 bounded source relations preserve unknown sides independently of a declared-side route', () => {
    const distalRows = raw.objects.filter(row => row.targetRelationEvidence?.some(relation => relation.targetId === 'TA2:1512'));
    assert.equal(distalRows.length, 10);
    assert.equal(new Set(distalRows.map(row => row.sourceName.replace(/\.[lr]$/i, ''))).size, 5);
    assert.equal(distalRows.filter(row => row.side === 'left').length, 5);
    assert.equal(distalRows.filter(row => row.side === 'right').length, 5);
    for (const row of distalRows) {
        const name = row.sourceName;
        const match = name.match(/^Distal phalanx of (first|second|third|fourth|fifth) finger of foot\.([lr])$/);
        assert(match, name);
        const member = `distal:${match[1]}`;
        const side = match[2] === 'l' ? 'left' : 'right';
        const targetLink = row.learnerConceptLinks?.find(link => link.relationKind === 'verified_class_member'
            && link.targetIds.length === 1 && link.targetIds[0] === 'TA2:1512');
        assert(targetLink, name);
        assert.equal(targetLink.memberCode, member);
        assert.equal(targetLink.conceptKey, row.learnerConceptLinks?.find(link => link.relationKind === 'verified_class_member'
            && link.targetIds.length === 1 && link.targetIds[0] === 'TA2:1505')?.conceptKey,
        'the distinct generic TA2:1505 member proof is preserved');
        assert.equal(row.learnerConceptLinks?.filter(link => link.relationKind === 'verified_class_member'
            && link.targetIds.includes('TA2:1505')).length, 1);
        const relation = row.targetRelationEvidence!.find(item => item.targetId === 'TA2:1512')!;
        assert.equal(relation.memberCode, `${member}:${side}`);
        assert.equal(relation.sourceSide, side);
        assert.equal(relation.sourceParent, 'Phalanges of foot.g');
        assert(relation.sourceCollections.includes(side === 'left' ? 'Left lower limb' : 'Right lower limb'));
        assert.equal(relation.directObjectNameMatch, false);
        assert.equal(relation.ancestorNameAloneUsed, false);
        assert.equal(relation.upstreamFjOrTa2IdClaim, false);
    }

    const posteriorRows = raw.objects.filter(row => row.learnerConceptLinks?.some(link => link.relationKind === 'verified_source_crosswalk'
        && link.targetIds.includes('TA2:2196')));
    assert.equal(posteriorRows.length, 2);
    assert.deepEqual(posteriorRows.map(row => row.sourceName).sort(), [
        'Posterior crico-arytenoid muscle.l', 'Posterior crico-arytenoid muscle.r',
    ]);
    assert.deepEqual(posteriorRows.map(row => row.side).sort(), ['left', 'right']);
    for (const row of posteriorRows) {
        const relation = row.targetRelationEvidence!.find(item => item.targetId === 'TA2:2196')!;
        assert.equal(relation.matchedTargetSynonym, 'posterior crico-arytenoid muscle');
        assert.equal(relation.sourceParent, 'Laryngeal muscles.g');
        assert(['Laryngeal muscles', 'Muscles of neck', 'Neck'].every(name => relation.sourceCollections.includes(name)));
        assert(relation.matchEvidenceSourceIds!.includes('fipat-ta2-t78-frozen-full-context'));
        assert.equal(relation.directObjectNameMatch, false);
        assert.equal(relation.humanReview, 'not_performed');
        assert.equal(row.haConceptId, null);
        assert.equal(row.publicRedistribution, 'held');
    }
    const iliocostalis = raw.objects.filter(row => row.targetIds.includes('TA2:2261'));
    assert.equal(iliocostalis.length, 2);
    assert(iliocostalis.every(row => row.learnerConceptLinks?.some(link => link.conceptKey === null
        && link.identityStatus === 'side_conflicted' && link.relationKind === 'normalized_exact_target_term')));
    const unsided = iliocostalis.find(row => row.side === null)!;
    const declaredRight = iliocostalis.find(row => row.sourceName === 'Iliocostalis colli muscle.r')!;
    assert.equal(declaredRight.side, 'right');
    assert(!unsided.learnerConceptLinks?.some(link => link.identityStatus === 'evidence_backed'
        && link.targetIds.includes('TA2:2261')), 'an unsided mate is never inferred to be left');
    const independent = declaredRight.learnerConceptLinks?.filter(link => link.identityStatus === 'evidence_backed'
        && link.targetIds.includes('TA2:2261')) ?? [];
    assert.equal(independent.length, 1);
    assert(independent[0].matchRule.includes('independent explicit source object side'));
    assert.equal(readDatasetRoute(`?regions=back&concept=${independent[0].conceptKey}&side=right`, runtime.objects, ['back']).selected, declaredRight.sourceKey);
    assert.equal(readDatasetRoute(`?regions=back&concept=${independent[0].conceptKey}&side=left`, runtime.objects, ['back']).selected, null);

    const terms = new Map(raw.targetTerminologyEvidence!.map(term => [term.targetId, term]));
    assert.equal(terms.get('TA2:1255')!.names.koModern, '큰마름뼈');
    assert.equal(terms.get('TA2:1255')!.fieldEvidence.koModern.status, 'evidence_backed');
    assert.equal(terms.get('TA2:1255')!.fieldEvidence.koModern.sourceIds[0], 'nikl-trapezium-565982');
    assert.equal(terms.get('TA2:2481')!.names.koModern, '노쪽손목굽힘근');
    assert.equal(terms.get('TA2:2481')!.names.koTraditional, '요 수근 굴근');
    assert.equal(terms.get('TA2:2481')!.fieldEvidence.koModern.sourceIds[0], 'kses-terms-p60');
    assert.equal(terms.get('TA2:2481')!.fieldEvidence.koTraditional.sourceIds[0], 'kses-terms-p60');
    for (const targetId of ['TA2:2056', 'TA2:2532']) {
        assert.equal(terms.get(targetId)!.fieldEvidence.koModern.status, 'missing');
        assert.equal(terms.get(targetId)!.fieldEvidence.koTraditional.status, 'evidence_backed');
    }
    assert.equal(terms.get('TA2:1253')!.fieldEvidence.koModern.status, 'missing');
    assert.equal(terms.get('TA2:1253')!.fieldEvidence.koTraditional.status, 'missing');
    assert.equal(raw.scope.targets, 542);
    assert.equal(raw.scope.memberships, 563);
    assert.equal(raw.scope.regions, 12);
    assert.equal(raw.objects.filter(row => row.haConceptId).length, 130);
    assert.equal(raw.objects.filter(row => row.sourceOnly).length, 830);
    assert(raw.objects.every(row => row.publicRedistribution === 'held' && row.humanReview === 'not_performed'));
});

test('T100 parallel integration rejects wrong foot level and non-exact laryngeal synonym or context', () => {
    const wrongFootMember = structuredClone(raw);
    const distal = wrongFootMember.objects.find(row => row.targetRelationEvidence?.some(relation => relation.targetId === 'TA2:1512'))!;
    distal.targetRelationEvidence!.find(relation => relation.targetId === 'TA2:1512')!.memberCode = 'middle:first:left';
    assert.throws(() => validateIntegration(wrongFootMember, fixture));

    for (const mutate of [
        (relation: NonNullable<Integration['objects'][number]['targetRelationEvidence']>[number]) => { relation.matchedTargetSynonym = 'lateral crico-arytenoid muscle'; },
        (relation: NonNullable<Integration['objects'][number]['targetRelationEvidence']>[number]) => { relation.sourceParent = 'Intrinsic muscles of larynx.g'; },
        (relation: NonNullable<Integration['objects'][number]['targetRelationEvidence']>[number]) => { relation.sourceSide = 'right'; },
    ]) {
        const invalid = structuredClone(raw);
        const row = invalid.objects.find(candidate => candidate.sourceName === 'Posterior crico-arytenoid muscle.l')!;
        mutate(row.targetRelationEvidence!.find(relation => relation.targetId === 'TA2:2196')!);
        assert.throws(() => validateIntegration(invalid, fixture));
    }
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

test('T100 semantic continuation groups the 226 unnamed surfaces without side duplicates and keeps unresolved identities held', () => {
    // Preserve the original 226-row semantic continuation as its own regression cohort.
    const linked = raw.objects.filter(row => preservedUnnamedBySource.has(row.sourceKey));
    assert.equal(linked.length, 226);
    assert(raw.objects.filter(row => row.learnerConceptLinks?.length).length >= 618);
    const groups = new Map<string, typeof linked>();
    for (const row of linked) {
        const label = row.sourceName.replace(/\.[lr]$/i, '');
        const group = groups.get(label) ?? [];
        group.push(row);
        groups.set(label, group);
        const link = row.learnerConceptLinks!.find(candidate => candidate.relationKind !== 'verified_taxonomy_member')!;
        assert(link);
        assert.equal(link.humanReview, 'not_performed');
        if (link.relationKind === 'paired_source_concept')
            assert(link.evidenceIds.includes('za-t99-frozen-source-objects'));
        assert.equal(row.haConceptId ?? null, preexistingHaBySource.get(row.sourceKey) ?? null,
            `T100 must preserve pre-existing HA binding for ${row.sourceName}`);
        assert(!link.conceptKey || !/^HA-/.test(link.conceptKey));
        const baseline = preservedUnnamedBySource.get(row.sourceKey)!;
        for (const key of ['sourceOnly', 'publicRedistribution', 'humanReview', 'mappingStatus', 'regionIds', 'side',
            'aliases', 'localDisplayEligible', 'inspectionEligible', 'defaultVisible'])
            assert.deepEqual((row as unknown as Record<string, unknown>)[key], baseline[key], `${key} changed for ${row.sourceName}`);
        assert.equal(row.names.en, (baseline.names as any).en);
        if (row.names.koTraditional !== (baseline.names as any).koTraditional) {
            assert.equal(row.nameEvidence?.koTraditional?.value, row.names.koTraditional);
            assert(row.nameEvidence?.koTraditional?.sourceIds.includes('t100-explicit-source-part-composition'));
        }
        assert(!/\p{Script=Han}/u.test(row.names.koModern ?? ''));
    }
    assert.equal(groups.size, 113);
    const explicitPairs = [...groups.values()].filter(rows => rows.length === 2
        && rows.some(row => row.side === 'left') && rows.some(row => row.side === 'right')
        && !rows.some(row => row.sourceKey === 'ZA-c7010a9-0e655a17b4dd00a4d206bb71'));
    assert.equal(explicitPairs.length, 111);
    const kinds = linked.reduce((counts, row) => {
        const relation = row.learnerConceptLinks![0].relationKind;
        counts.set(relation, (counts.get(relation) ?? 0) + 1);
        return counts;
    }, new Map<string, number>());
    assert.equal(kinds.get('verified_class_member'), 67);
    assert.equal(kinds.get('normalized_exact_target_term'), 154);
    assert.equal(kinds.get('paired_source_concept'), 4);
    assert.equal(kinds.get('side_or_source_identity_conflict'), 1);

    const handConflict = raw.objects.find(row => row.sourceName === 'Distal phalanx of fifth finger of hand.l')!;
    assert.equal(handConflict.names.koModern, '다섯째손가락 끝마디뼈');
    assert(handConflict.nameEvidence?.koModern?.sourceIds.includes('t100-explicit-source-part-composition'));
    assert.equal(handConflict.learnerConceptLinks![0].conceptKey, null);
    assert.equal(handConflict.learnerConceptLinks![0].identityStatus, 'held');
    const iliocostalis = groups.get('Iliocostalis colli muscle')!;
    assert(iliocostalis.every(row => row.learnerConceptLinks![0].conceptKey === null));
    assert(iliocostalis.every(row => row.learnerConceptLinks![0].identityStatus === 'side_conflicted'));

    const modernNames = linked.filter(row => row.nameEvidence?.koModern?.sourceIds.some(id => id.startsWith('kli-t100-')));
    assert.equal(modernNames.length, 67);
    assert.equal(modernNames.filter(row => /phalanx of/.test(row.sourceName)).length, 55);
    assert.equal(modernNames.filter(row => /metacarpal bone/.test(row.sourceName)).length, 8);
    assert.equal(modernNames.filter(row => /(?:Triquetrum|Trapezium) bone/.test(row.sourceName)).length, 4);
    for (const row of modernNames) {
        assert.equal(row.names.koModern, row.nameEvidence!.koModern!.value);
        assert(row.nameEvidence!.koModern!.sourceIds.every(id => raw.evidenceSources!.some(source => source.id === id)));
    }
    assert.equal(raw.objects.length, 960);
    assert.equal(raw.objects.filter(row => row.localDisplayEligible).length, 672);
    assert.equal(raw.objects.filter(row => row.haConceptId).length, 130);
    assert.equal(raw.scope.targets, 542);
    assert.equal(raw.scope.memberships, 563);
    assert.equal(raw.scope.regions, 12);
});
test('T100 exact direct target links add typed source selection without changing canonical bindings or release holds', () => {
    const entries = directTargetLinkDelta.entries;
    assert.equal(directTargetLinkDelta.change.addedRows, 392);
    assert.equal(directTargetLinkDelta.change.uniqueTargetIds, 203);
    assert.equal(entries.length, 392);
    assert.equal(new Set(entries.map(entry => entry.sourceKey)).size, 392);
    assert.equal(new Set(entries.map(entry => entry.targetId)).size, 203);
    assert.deepEqual(directTargetLinkDelta.change.sourceKindCounts, { bone: 88, muscle: 304 });
    assert.deepEqual(directTargetLinkDelta.change.sourceOnlyCounts, { existing_HA_bound: 112, source_only: 280 });
    assert.deepEqual(directTargetLinkDelta.change.sideCounts, { left: 189, right: 189, unsided: 14 });
    assert.equal(raw.objects.filter(row => row.learnerConceptLinks?.some(link => link.relationKind === 'normalized_exact_target_term')).length, 546);
    assert.equal(raw.objects.filter(row => row.haConceptId).length, 130);
    for (const row of raw.objects)
        assert.equal(row.haConceptId ?? null, preexistingHaBySource.get(row.sourceKey) ?? null, `canonical binding changed for ${row.sourceName}`);
    for (const entry of entries) {
        const row = raw.objects.find(candidate => candidate.sourceKey === entry.sourceKey)!;
        const link = row.learnerConceptLinks?.find(candidate => candidate.relationKind === 'normalized_exact_target_term' && candidate.targetIds.includes(entry.targetId));
        assert(link, entry.sourceKey);
        assert.equal(row.learnerConceptLinks!.filter(candidate => candidate.relationKind === 'normalized_exact_target_term' && candidate.targetIds.includes(entry.targetId)).length, 1);
        assert.equal(row.sourceName, entry.sourceName);
        assert.equal(row.targetId, entry.targetId);
        assert(row.targetIds.includes(entry.targetId));
        assert.equal(row.kind, entry.kind);
        assert.equal(row.side, entry.side);
        assert.deepEqual(row.regionIds, entry.regionIds);
        assert.equal(row.localDisplayEligible, true);
        assert.equal(row.publicRedistribution, 'held');
        assert.equal(row.humanReview, 'not_performed');
        assert.equal(link.relationKind, 'normalized_exact_target_term');
        assert.equal(link.identityStatus, 'evidence_backed');
        assert.equal(link.humanReview, 'not_performed');
        assert.deepEqual(link.targetIds, [entry.targetId]);
        assert.deepEqual(link.evidenceIds, ['fipat-ta2-t96-full-target-catalog', 'za-t99-frozen-source-objects']);
        assert.equal(link.conceptKey, entry.conceptKey);
        assert.match(entry.evaluatedGeometrySha256, /^[a-f0-9]{64}$/);
        assert(!entry.conceptKey.startsWith('HA-'));
    }
    const groups = new Map<string, typeof entries>();
    for (const entry of entries) {
        const group = groups.get(entry.conceptKey) ?? [];
        group.push(entry);
        groups.set(entry.conceptKey, group);
    }
    assert.equal(groups.size, 203);
    const bilateral = [...groups.values()].filter(group => group.length === 2 && new Set(group.map(entry => entry.side)).size === 2
        && group.some(entry => entry.side === 'left') && group.some(entry => entry.side === 'right'));
    const unsided = [...groups.values()].filter(group => group.length === 1 && group[0].side === null);
    assert.equal(bilateral.length, 189);
    assert.equal(unsided.length, 14);
    const pair = bilateral[0];
    const left = pair.find(entry => entry.side === 'left')!;
    const right = pair.find(entry => entry.side === 'right')!;
    const regions = [...new Set(raw.objects.flatMap(row => row.regionIds))];
    assert.equal(readDatasetRoute(`?concept=${left.conceptKey}&side=left`, raw.objects, regions).selected, left.sourceKey);
    assert.equal(readDatasetRoute(`?concept=${right.conceptKey}&side=right`, raw.objects, regions).selected, right.sourceKey);
    const midline = unsided[0][0];
    assert.equal(readDatasetRoute(`?concept=${midline.conceptKey}`, raw.objects, regions).selected, midline.sourceKey);
});
test('T100 target membership continuation adds only evidenced member routes and keeps the frozen denominator partial', () => {
    const plan = targetMembershipContinuation;
    assert.equal(plan.addedClassMemberLinks.length, 72);
    assert.equal(plan.taxonomyMemberLinks.length, 1076);
    assert.deepEqual(plan.denominators, {
        scopeTargets: 542, scopeMemberships: 563, regions: 12, sourceObjects: 960,
        localDisplayEligible: 672, existingHaBindings: 130, sourceOnly: 830,
        publicRedistributionHeld: 960, humanReviewNotPerformed: 960, historicalCandidateFree163: 163,
    });
    assert.equal(plan.termGapCount, 75);
    assert.deepEqual(plan.rightsAndIdentityInvariants, {
        newCanonicalHaBindings: 0, humanReview: 'not_performed', publicRedistribution: 'held',
        sourceOnlyRowsPreserved: true, newGeometry: 0, TA2DenominatorChanged: false,
    });
    assert.equal(raw.scope.targets, 542);
    assert.equal(raw.scope.memberships, 563);
    assert.equal(raw.scope.regions, 12);
    assert.equal(raw.objects.length, 960);
    assert.equal(raw.objects.filter(row => row.localDisplayEligible).length, 672);
    assert.equal(raw.objects.filter(row => row.haConceptId).length, 130);
    assert.equal(raw.objects.filter(row => row.sourceOnly).length, 830);
    assert(raw.objects.every(row => row.publicRedistribution === 'held' && row.humanReview === 'not_performed'));
    assert(raw.objects.every(row => row.sourceOnly === !Boolean(row.haConceptId)), 'per-object source-only/canonical state changed');
    for (const row of raw.objects)
        assert.equal(row.haConceptId ?? null, preexistingHaBySource.get(row.sourceKey) ?? null,
            `canonical HA identity changed for ${row.sourceKey}`);

    for (const entry of plan.addedClassMemberLinks) {
        const row = raw.objects.find(candidate => candidate.sourceKey === entry.sourceKey)!;
        assert(row, entry.sourceKey);
        assert(row.learnerConceptLinks?.some(link => link.relationKind === 'verified_class_member'
            && link.memberCode === entry.memberCode && link.targetIds.join('|') === entry.targetIds.join('|')
            && link.conceptKey === entry.link.conceptKey && link.evidenceIds.join('|') === entry.link.evidenceIds.join('|')),
        `class-member relation missing for ${entry.sourceKey}`);
    }
    const taxonomyLinks = raw.objects.flatMap(row => (row.learnerConceptLinks ?? [])
        .filter(link => link.relationKind === 'verified_taxonomy_member').map(link => ({ row, link })));
    assert(taxonomyLinks.length >= plan.taxonomyMemberLinks.length, 'historical taxonomy links must be preserved');
    const frozenById = new Map(frozenTargetLexicon.targets.map(target => [target.id, target]));
    for (const entry of plan.taxonomyMemberLinks) {
        const row = raw.objects.find(candidate => candidate.sourceKey === entry.sourceKey)!;
        assert(row, entry.sourceKey);
        const link = row.learnerConceptLinks?.find(candidate => candidate.relationKind === 'verified_taxonomy_member'
            && candidate.targetIds.length === 1 && candidate.targetIds[0] === entry.targetId
            && candidate.memberCode === entry.childTargetId);
        assert(link, `${entry.sourceKey} -> ${entry.targetId} member ${entry.childTargetId}`);
        assert(frozenById.get(entry.childTargetId)?.sourceAncestryIds?.includes(Number(entry.targetId.slice('TA2:'.length))),
            `frozen T96 ancestry does not prove ${entry.targetId} -> ${entry.childTargetId}`);
        assert.equal(link.humanReview, 'not_performed');
        assert.equal(link.identityStatus, 'evidence_backed');
        assert(!link.conceptKey?.startsWith('HA-'));
    }

    const memberships = plan.targetRegionMembershipSelection;
    assert.equal(memberships.length, 563);
    assert.equal(memberships.filter(item => item.status === 'selectable_member_surfaces_verified').length, 393);
    assert.equal(memberships.filter(item => item.status === 'no_exact_selectable_member_surface').length, 170);
    assert.equal(plan.routeFailureCount, 0);
    const regions = [...new Set(raw.objects.flatMap(row => row.regionIds))];
    let checkedRoutes = 0;
    for (const membership of memberships) {
        if (membership.status === 'no_exact_selectable_member_surface') {
            assert.equal(membership.selectionRoutes.length, 0);
            continue;
        }
        assert(membership.selectionRoutes.length > 0, `${membership.targetId}/${membership.regionId}`);
        for (const route of membership.selectionRoutes) {
            assert.equal(route.routeResolvesToExactSourceAndRegion, true);
            const query = new URLSearchParams({ concept: route.conceptKey, region: membership.regionId });
            if (route.side)
                query.set('side', route.side);
            const search = '?' + query.toString();
            assert.equal(readDatasetRoute(search, raw.objects, regions).selected, route.sourceKey,
                `developer route mismatch for ${membership.targetId}/${membership.regionId}/${route.sourceKey}`);
            assert.equal(readDatasetRoute(search, runtime.objects, regions).selected, route.sourceKey,
                `learner projection route mismatch for ${membership.targetId}/${membership.regionId}/${route.sourceKey}`);
            checkedRoutes++;
        }
    }
    assert.equal(checkedRoutes, memberships.reduce((sum, item) => sum + item.selectionRoutes.length, 0));

    const rejected = structuredClone(raw);
    const rejectedRow = rejected.objects.find(row => row.learnerConceptLinks?.some(link => link.relationKind === 'verified_taxonomy_member'))!;
    const rejectedLink = rejectedRow.learnerConceptLinks!.find(link => link.relationKind === 'verified_taxonomy_member')!;
    rejectedLink.memberCode = 'TA2:999999';
    assert.throws(() => validateIntegration(rejected, fixture), /taxonomy-member link proof mismatch/);

    const leftTaxonomyRow = raw.objects.find(row => row.side === 'left'
        && row.learnerConceptLinks?.some(link => link.relationKind === 'verified_taxonomy_member'
            && link.memberCode === 'TA2:2672'))!;
    const wrongChildSideLexicon = structuredClone(frozenTargetLexicon);
    const child = wrongChildSideLexicon.targets.find(target => target.id === 'TA2:2672')!;
    child.sourceCardinality = { explicitSourceSide: 'right' };
    assert.equal(leftTaxonomyRow.side, 'left');
    assert.throws(() => validateIntegrationWithCatalog(raw, fixture, wrongChildSideLexicon), /taxonomy-member source side mismatch/);
});
test('opaque learner concept links resolve a selected side and fail closed when a bilateral side is omitted', () => {
    const pair = raw.objects.find(row => row.learnerConceptLinks?.some(link => link.conceptKey && link.relationKind === 'verified_class_member'))!;
    const key = pair.learnerConceptLinks!.find(link => link.conceptKey)!.conceptKey!;
    const sibling = raw.objects.find(row => row !== pair && row.learnerConceptLinks?.some(link => link.conceptKey === key))!;
    assert.notEqual(pair.side, sibling.side);
    const regionIds = [...new Set(raw.objects.flatMap(row => row.regionIds))];
    const left = pair.side === 'left' ? pair : sibling;
    const right = pair.side === 'right' ? pair : sibling;
    assert.equal(readDatasetRoute(`?concept=${key}&side=left`, raw.objects, regionIds).selected, left.sourceKey);
    assert.equal(readDatasetRoute(`?concept=${key}&side=right`, raw.objects, regionIds).selected, right.sourceKey);
    assert.equal(readDatasetRoute(`?concept=${key}`, raw.objects, regionIds).selected, null);
    assert.equal(readDatasetRoute('?concept=LC-00000000000000000000&side=left', raw.objects, regionIds).selected, null);

    const runtimePair = runtime.objects.find(row => row.sourceKey === left.sourceKey)!;
    assert(runtimePair.learnerConceptKeys.includes(key));
    assert.equal(JSON.stringify(runtimePair).includes('TA2:'), false);
    assert.equal(JSON.stringify(runtimePair).includes('targetRelationEvidence'), false);
    assert.equal(readDatasetRoute(`?concept=${key}&side=left`, runtime.objects, regionIds).selected, left.sourceKey);
});
test('composed Korean phalanx and named carpal terms search to one source concept', () => {
    for (const query of ['엄지손가락 끝마디뼈', '둘째발가락 첫마디뼈', '세모뼈', '큰마름뼈']) {
        const results = searchStructures(runtime.objects, query, []);
        assert.equal(results.length, 1, query);
        assert.equal(results[0].searchApproximate, false, query);
    }
    const conflictResult = searchStructures(runtime.objects, '다섯째손가락 끝마디뼈', []);
    assert.equal(conflictResult.length, 1);
    assert.equal(conflictResult[0].names.koModern, '다섯째손가락 끝마디뼈');
    assert.deepEqual(runtime.objects.find(row => row.sourceKey === 'ZA-c7010a9-0e655a17b4dd00a4d206bb71')!.learnerConceptKeys, []);
});

test('contextual names cover visible surfaces without exposing judgment records or promoting holds', () => {
    const visible = runtime.objects.filter(row => row.localDisplayEligible);
    assert(visible.every(row => Object.values(row.names).every(value => typeof value === 'string' && value.trim())));
    assert(visible.every(row => !/[\p{Script=Han}]/u.test(row.names.koModern! + row.names.koTraditional!)));
    assert(!JSON.stringify(runtime).includes('AI contextual'));
    const invalid = structuredClone(raw);
    invalid.evidenceSources!.find(source => source.id === 't100-explicit-source-part-composition')!.url = 'local:../../private.json';
    assert.throws(() => validateIntegration(invalid, fixture));
});

test('pending source crosswalks and child routes require bounded proofs and preserve historical links', () => {
    const delta = JSON.parse(readFileSync(new URL('../../../../work/evidence/T100/target-scope-resolution-2026-09-30/link-delta.json', import.meta.url), 'utf8')) as {
        entries: Array<{ sourceKey: string; side: string | null; targetId: string; link: NonNullable<Integration['objects'][number]['learnerConceptLinks']>[number] }>;
    };
    const regions = [...new Set(raw.objects.flatMap(row => row.regionIds))];
    for (const entry of delta.entries) {
        const row = raw.objects.find(row => row.sourceKey === entry.sourceKey)!;
        assert(row.learnerConceptLinks?.some(link => JSON.stringify(link) === JSON.stringify(entry.link)));
        const query = new URLSearchParams({ concept: entry.link.conceptKey! });
        if (entry.side) query.set('side', entry.side);
        assert.equal(readDatasetRoute('?' + query, runtime.objects, regions).selected, entry.sourceKey);
    }
    for (const rule of ['qualified_synonym', 'corrected_surface', 'direct_term_with_class_context', 'series_member', 'context_part_member']) {
        const rejected = structuredClone(raw);
        const entry = delta.entries.find(entry => entry.link.matchRule.endsWith(': ' + rule))!;
        assert(entry, rule);
        const row = rejected.objects.find(row => row.sourceKey === entry.sourceKey)!;
        const link = row.learnerConceptLinks!.find(link => link.conceptKey === entry.link.conceptKey)!;
        link.targetIds = [rule === 'series_member' ? 'TA2:1115' : 'TA2:819'];
        assert.throws(() => validateIntegration(rejected, fixture), /source-crosswalk proof mismatch/);
    }
    const staleContext = structuredClone(frozenTargetLexicon);
    staleContext.supportContext!.sha256 = '0'.repeat(64);
    assert.throws(() => validateIntegrationWithCatalog(raw, fixture, staleContext), /support context provenance/);
    const wrongName = structuredClone(raw);
    const source = wrongName.objects.find(row => row.learnerConceptLinks?.some(link => link.relationKind === 'verified_source_crosswalk'))!;
    source.sourceName += ' altered';
    assert.throws(() => validateIntegration(wrongName, fixture), /integration identity\/policy/);
    const outsideRange = structuredClone(raw);
    const rib = outsideRange.objects.find(row => row.learnerConceptLinks?.some(link =>
        link.relationKind === 'verified_source_crosswalk' && link.targetIds.includes('TA2:1114')))!;
    const ribLink = rib.learnerConceptLinks!.find(link => link.relationKind === 'verified_source_crosswalk' && link.targetIds.includes('TA2:1114'))!;
    ribLink.memberCode = 'rib:8';
    assert.throws(() => validateIntegration(outsideRange, fixture), /source-crosswalk proof mismatch/);
});
