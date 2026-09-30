#!/usr/bin/env python3
"""Record only T100's audited current result; preserve historical evidence."""
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = 'work/evidence/T100/closure-audit-2026-09-30/'


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def main():
    path = ROOT / 'work/EXECUTION.json'
    execution = read('work/EXECUTION.json')
    before = json.loads(json.dumps(execution))
    task = execution['tasks']['T100']
    p = task['progress']
    b = read(OUT + 'qa-baseline.json')
    qa = read(OUT + 'selection-render-ledger.json')['summary']
    assert hashlib.sha256((ROOT / b['overlay']['path']).read_bytes()).hexdigest() == b['overlay']['sha256']
    assert task['executionStatus'] == 'in_progress' and task['acceptance'] == 'partial'
    assert p['nextUnit'] == 'resolve-target-representation-and-final-scene-qa'
    assert qa['availablePathCaptureComplete'] and qa['actualPhysicalCaptures'] == 696
    p['result'] = (
        'Current T100: 409/542 targets and 427/563 memberships have at least one bounded selectable path; '
        '133 targets and 136 memberships have no path. 672/672 eligible surfaces already have three display names. '
        'All 2,027 current route aliases have actual browser selection/card/raster evidence through 696 physical '
        'region/source captures with verified runtime-response hashes and saved PNGs. This completes available-path '
        'rendering checks only; full target/part/group/side extent acceptance remains pending. One independently '
        'declared right TA2:2261 route was added while both original side-conflicted null links and the unsided mate '
        'were preserved. Direct Korean citation gaps remain 73 and are independent of learner naming. Unavailable '
        'GPU/VRAM/total-memory values are evidence limits; no repeat measurement is required solely by a 25-byte '
        'relation-only runtime delta. T100 remains partial at the same nextUnit because representation/extent gaps remain.'
    )
    p['pendingUnits'] = [
        'Resolve the 133 targets/136 memberships with no selectable path using action-queue.json: new source/correspondence '
        'evidence, exact part segmentation, variant evidence, group extent or explicit side. Do not repeat exhausted '
        'fixed-label scans or infer geometry absence. Six already-cached cross-dataset candidate targets require identity '
        'and frame/registration verification before integration.',
        'Complete anatomical target/part/group/side and whole-extent adjudication separately from successful available-path '
        'raster checks. TA2:2261 unsided mate/bilateral extent remain pending; preserve both historical side_conflicted/null '
        'links. Old C3 overview never counts as localized visual acceptance.',
        'Continue the 73 direct Korean terminology citation gaps and held terminology conflicts in the internal evidence '
        'ledger; all 672 eligible surface display names are already complete. Do not treat direct dictionary quotation '
        'or humanReview not_performed as an automatic learner-name blocker.'
    ]
    p['closureAudit'] = {
        'report': OUT + 'REPORT.md', 'currentQaBaseline': OUT + 'qa-baseline.json',
        'currentActionQueue': OUT + 'action-queue.json', 'selectionRenderLedger': OUT + 'selection-render-ledger.json',
        'currentRouteCounts': {'targetIdsWithPaths': 409, 'targetIdsWithoutPaths': 133,
                              'membershipsWithPaths': 427, 'membershipsWithoutPaths': 136},
        'availablePathRendering': qa, 'directKoreanCitationGapRows': 73, 'displayNameGapFields': 0,
        'cachedUnroutedOtherDatasetCandidateTargets': 6,
        'declaredRightRelationApplied': OUT + 'declared-side-application.json',
        'TA2_2261FullBilateralExtent': 'pending; unsided mate not inferred',
        'dataContractTests': {'passed': 37, 'failed': 0}, 'performanceRemeasured': False
    }
    p['gate'].update({
        'currentTargetsWithSomeTypedMemberRoute': 409, 'currentTargetsWithoutSelectableRoute': 133,
        'selectableMembershipRoutes': 427, 'membershipRowsWithoutExactRoute': 136, 'membershipRouteFailures': 0,
        'currentOverlaySha256': b['overlay']['sha256'], 'currentQaBaseline': OUT + 'qa-baseline.json',
        'availablePathRenderingComplete': True, 'availablePathRouteAliasesChecked': 2027,
        'actualRegionSourceRasterCaptures': 696, 'fullTargetExtentPassesClaimed': 0,
        'exhaustiveTargetMemberVisualSelection': False, 'learnerDisplayNameGapFields': 0,
        'directCitationGapIsNotLearnerNameGap': True,
        'unavailableGpuVramTotalMemoryAreLimitationsNotAutomaticBlockers': True,
        'acceptanceScope': 'T100 partial: 133 targets/136 memberships without paths; anatomical target/group/part/side '
        'extent remains pending. All current available paths have bounded browser render evidence. 73 direct citations '
        'remain separate from complete 672-surface display naming. TA2:2261 independent right route exists; unknown mate '
        'and bilateral extent remain pending.',
        'evidence': OUT + 'selection-render-ledger.json'
    })
    p['runtimeProjection']['historicalMeasurementEvidence'] = (
        'Prior payload/parse/builder/gzip/search and scene figures retain their original input snapshots; '
        'this object is historical measurement evidence, not the current response byte count.'
    )
    p['runtimeProjection']['currentResponse'] = {
        'sourceOverlaySha256': b['overlay']['sha256'], 'sha256': b['runtime']['sha256'],
        'bytes': b['runtime']['bytes'], 'browserResponseHashVerified': True,
        'baseline': OUT + 'qa-baseline.json', 'benchmarkRepeated': False
    }
    for f in ['REPORT.md', 'qa-baseline.json', 'action-queue.json', 'selection-render-ledger.json', 'declared-side-application.json']:
        if OUT + f not in p['evidence']:
            p['evidence'].append(OUT + f)
    if not any(h.get('evidence') == OUT + 'REPORT.md' for h in p['resumeHistory']):
        p['resumeHistory'].append({
            'date': '2026-09-30', 'unit': p['nextUnit'],
            'result': 'Replaced sample-only QA with 2,027 alias selections/696 bounded raster cases and preserved PNGs; '
            'added one independently declared right route without inferring mate. Current 409/542 targets, 427/563 '
            'memberships; representation/extent gaps remain partial.',
            'evidence': OUT + 'REPORT.md', 'nextUnit': p['nextUnit'], 'nextId': 'T100'
        })
    old_t100 = before['tasks'].pop('T100')
    check = json.loads(json.dumps(execution)); check['tasks'].pop('T100')
    assert check == before, 'Only T100 may change'
    path.write_text(json.dumps(execution, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'changedTask': 'T100', 'status': 'partial', 'nextUnit': p['nextUnit']}))


if __name__ == '__main__':
    main()
