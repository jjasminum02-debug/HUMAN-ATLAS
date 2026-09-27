#!/usr/bin/env python3
"""Reproducible T43 metadata consistency checks; does not validate anatomy truth."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

def read(rel):
    return json.loads((ROOT / rel).read_text())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

nav = read('atlas-data/navigation/atlas-navigation.json')
inv = read('atlas-data/catalog/whole-body-inventory-t15g.json')
names = read('atlas-data/terminology/learning-names.json')
cross = read('atlas-data/catalog/source-crosswalk.json')
matrix_rel = 'work/review-queue/region-acquisition-matrix-t43.json'
gaps_rel = 'work/review-queue/region-acquisition-gaps-t43.json'
t32_rel = 'work/review-queue/t32-input-t43.json'
matrix = read(matrix_rel)
gaps = read(gaps_rel)
t32 = read(t32_rel)
access = read('work/evidence/T43/source-access.json')
rows = matrix['regionRows']

assert [r['id'] for r in nav['categories']] == [r['categoryId'] for r in rows]
assert len(rows) == 12 and matrix['productTaxonomy']['categoryCount'] == 12
assert all(r['visibleSubcategoriesAdded'] is False for r in rows)
assert matrix['wholeBodyComplete'] is False
assert matrix['inventorySnapshot']['denominatorFrozen'] is False
assert matrix['inventorySnapshot']['wholeBodyIndividualMuscleCount'] is None
assert matrix['inventorySnapshot']['coveragePercent'] is None
assert matrix['inventorySnapshot']['uniqueStableMuscleConceptIds'] == 85
assert matrix['inventorySnapshot']['individualMuscleConcepts'] == 48
assert matrix['inventorySnapshot']['muscleGroups'] == 16
assert matrix['inventorySnapshot']['muscleParts'] == 21
assert matrix['inventorySnapshot']['productMuscleMembershipRows'] == 6
assert matrix['inventorySnapshot']['productBoneMembershipRows'] == 0
assert len(cross['catalogItems']) == 85

membership = nav['memberships']
name_by_id = {x['id']: x for x in names['entries']}
for row in rows:
    cid = row['categoryId']
    assert row['labelKo'] and row['labelEn']
    assert all(row.get(key) is not None for key in (
        'sourceRegions', 'partialSourceInventory', 'currentDisplayNameOverlay',
        'currentProductInventory', 'structureText', 'muscleGeometry',
        'boneGeometry', 'laterality', 'licenseAndRights', 'rigAndMotion',
        'gapsAndNextActions'
    )), cid
    assert row['structureText'].get('termsAndNameCandidatesInB3DIndex') is not None, cid
    assert row['structureText'].get('fullOriginInsertionFunctionText') is not None, cid
    assert row['structureText'].get('TA2AuthorityAccess') is not None, cid
    assert row['structureText'].get('humanAnatomyReview') == 'not_performed', cid
    assert row['muscleGeometry'].get('officialMetadataCandidates') is not None, cid
    assert row['muscleGeometry'].get('localProductAssetStatus'), cid
    assert row['boneGeometry'].get('officialMetadataCandidates') is not None, cid
    assert row['boneGeometry'].get('localProductAssetStatus'), cid
    assert row['laterality'].get('observedOfficialIndexExamples') is not None, cid
    assert row['licenseAndRights'].get('bodyParts3d') is not None, cid
    assert row['licenseAndRights'].get('openSimModels') is not None, cid
    assert row['licenseAndRights'].get('perFileRedistributionAudit') is not None, cid
    assert row['gapsAndNextActions'], cid
    members = [m for m in membership if m['categoryId'] == cid]
    muscles = {m['entityId'] for m in members if m['entityKind'] == 'muscle'}
    bones = {m['entityId'] for m in members if m['entityKind'] == 'bone'}
    assert row['currentProductInventory']['muscleMembershipRows'] == sum(m['entityKind'] == 'muscle' for m in members)
    assert row['currentProductInventory']['boneMembershipRows'] == sum(m['entityKind'] == 'bone' for m in members)
    assert set(row['currentProductInventory']['uniqueMuscleStableIds']) == muscles
    assert set(row['currentProductInventory']['uniqueBoneStableIds']) == bones
    candidates = row['partialSourceInventory']['candidateStableIds']
    assert len(candidates) == len(set(candidates))
    assert row['partialSourceInventory']['candidateUniqueStableIdCount'] == len(candidates)
    assert set(row['currentDisplayNameOverlay']['candidateStableIdsWithOverlay']) == set(candidates) & set(name_by_id)
    assert set(row['currentDisplayNameOverlay']['candidateStableIdsMissingOverlay']) == set(candidates) - set(name_by_id)
    assert row['currentDisplayNameOverlay']['candidateOverlayCount'] + row['currentDisplayNameOverlay']['missingOverlayCount'] == len(candidates)
    for sid, triplet in row['currentDisplayNameOverlay']['existingTriplets'].items():
        source = name_by_id[sid]
        assert triplet['koModern'] == source.get('korean')
        assert triplet['koTraditional'] == source.get('label')
        assert triplet['en'] == source.get('english')
        assert triplet['humanReviewed'] == source.get('humanReviewed', False)
    assert row['productAcquisitionStatus'] in {'usable', 'static_only', 'additional_build_needed', 'unknown'}
    assert row['rigAndMotion']['productionMotionDefinitions'] == 0
    assert row['rigAndMotion']['productionMotionAssetsOrClips'] == 0
    assert row['rigAndMotion']['viewerReadyRig'] == 'none verified for this category'
    assert row['muscleGeometry']['meshDownloadedInT43'] is False
    assert row['boneGeometry']['meshDownloadedInT43'] is False
    assert row['laterality']['regionWideBilateralCompletenessAudited'] is False
    assert row['laterality']['mirroringAssumed'] is False

leg = next(r for r in rows if r['categoryId'] == 'leg')
assert leg['productAcquisitionStatus'] == 'static_only'
assert leg['currentProductInventory']['muscleMembershipRows'] == 6
assert leg['currentProductInventory']['boneMembershipRows'] == 0
assert len(inv['knownUnmappedMeshContexts']) == 4
lower_ids = {x['stableConceptId'] for x in cross['catalogItems'] if 'lower_extremity' in x.get('regionIds', [])}
leg_ids = {m['entityId'] for m in membership if m['categoryId'] == 'leg' and m['entityKind'] == 'muscle'}
assert len(lower_ids) == 12 and len(leg_ids) == 6
assert set(matrix['denominatorFreezeInputs']['unassignedLowerExtremitySourceIds']) == lower_ids - leg_ids
assert len(lower_ids - leg_ids) == 6
assert len(matrix['sharedMotionGroupCandidates']) >= 5
assert matrix['firstExpansionRecommendation']['categoryId'] == 'shoulder-scapular'
assert matrix['firstExpansionRecommendation']['status'] == 'recommendation_for_T32_evaluation_only'
assert 'not_frozen' == t32['denominatorCandidate']['status']
assert t32['denominatorCandidate']['wholeBodyIndividualMuscleCount'] is None
assert t32['notAnImplementationOrApproval'] is True

access_by_id = {s['id']: s for s in access['sources']}
assert access_by_id['BODYParts3D-LATEST-ISA']['accessStatus'] == 'opened_successfully_metadata_only'
assert access_by_id['BODYParts3D-license']['accessStatus'] == 'opened_successfully'
assert access_by_id['BODYParts3D-download-inventory']['accessStatus'] == 'opened_successfully_inventory_only'
assert access_by_id['FIPAT-TA2-Part-2']['accessStatus'] == 'direct_open_failed_502_search_index_only'
assert 'editionOrVersion' in access_by_id['FIPAT-TA2-Part-2']
assert all(s.get('locator') and s.get('checkedOn') and s.get('accessMethod') for s in access['sources'])
for row in rows:
    assert row['categoryId'] in access['regionIndexLookups']
    assert access['regionIndexLookups'][row['categoryId']]['muscleLocator']
    assert access['regionIndexLookups'][row['categoryId']]['boneLocator']

input_hashes = access['localInputHashes']
for rel, expected in input_hashes.items():
    assert digest(ROOT / rel) == expected, rel
assert matrix['inventorySnapshot']['sha256'] == input_hashes['atlas-data/catalog/whole-body-inventory-t15g.json']
assert t32['reuseInputs']['regionMatrixSha256'] == digest(ROOT / matrix_rel)
assert t32['reuseInputs']['regionCrosswalkSha256'] == input_hashes['work/review-queue/region-crosswalk-t15g.json']

result = {
    'task': 'T43', 'status': 'passed', 'checkedOn': '2026-09-27',
    'checks': {
        'exact12ProductCategories': 'passed',
        'noVisibleSubcategoriesAdded': 'passed',
        'candidateIDsDistinctFromProductMembershipRows': 'passed',
        'all12RowsCoverTextGeometryLateralityRightsMotionAndGaps': 'passed',
        'perRegionAcquisitionStatusAndNextActionRecorded': 'passed',
        'perRegionNameOverlayCoverageMatchesCurrentProjection': 'passed',
        'allRegionsHaveOpenedBodyParts3DIndexLocators': 'passed',
        'sourceAccessEditionLocatorDateMethodRecorded': 'passed',
        'TA2DirectOpenFailureNotPromotedToSuccess': 'passed',
        'denominatorRemainsFalseNullNull': 'passed',
        'lowerExtremityRoutingNotFannedOut': 'passed',
        'noProductionMotionOrViewerReadyRigClaimed': 'passed',
        'noBulkMeshDownloadClaimed': 'passed',
        'T32InputHashAndNotStartedGate': 'passed'
    },
    'counts': {'regions': len(rows), 'partialUniqueCandidateIDs': 85,
               'productMuscleMembershipRows': 6, 'productBoneMembershipRows': 0,
               'lowerExtremityUnassignedIDs': len(lower_ids - leg_ids),
               'humanAnatomyReview': 'not_performed'},
    'limitation': 'This script verifies data shape, counts, provenance/access records and preservation inputs. It does not establish anatomy truth, full source completeness, asset quality, or human approval.'
}
(ROOT / 'work/evidence/T43/validation-results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print('T43 validation passed: 12 regions; inventory denominator remains null; 6 leg memberships / 0 bone memberships; 6 lower_extremity IDs held.')
