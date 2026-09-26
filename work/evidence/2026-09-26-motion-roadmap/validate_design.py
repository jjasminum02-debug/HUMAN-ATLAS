"""Validate this design package; does not certify anatomy or motion implementation."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
D = ROOT / 'design/2026-09-25-muscle-atlas'
BASELINE = (HERE / 'head-before.txt').read_text().strip()

def read_json(path):
    return json.loads(path.read_text())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

PRIOR_PLAN_HASHES = read_json(HERE / 'prior-task-plan-hashes.json')['sha256']
registry = read_json(ROOT / 'work/task-registry-r13.json')
expected = [f'T{n}' for n in range(16, 41)]
example = read_json(D / 'examples/pectoralis-minor-learning-example.json')
sources = {source['id'] for source in example['sources']}
claims = {claim['id'] for claim in example['claims']}
checks = {
    'independent_task_ids_16_to_40': [task['id'] for task in registry['tasks']] == expected,
    'planned_order_matches_specs': registry['plannedOrder'] == expected,
    'task_specs_exist': all((ROOT / task['spec']).is_file() for task in registry['tasks']),
    'no_false_implementation_status': all(task['status'] == 'planned_not_started' for task in registry['tasks']),
    'default_successors_exist': all(task['defaultNext'] in expected or task['defaultNext'] is None for task in registry['tasks']),
    't15_flow_preserved': registry['t15FlowPreserved'] == [f'T15{suffix}' for suffix in 'abcdefg'],
    'next_new_numeric_id_is_41': registry['nextUnallocatedNumericId'] == 41,
    'source_locator_and_access_recorded': all(source.get('locator') and source.get('accessed') and source['opened'] for source in example['sources']),
    'claim_source_references_exist': all(set(claim['sourceIds']) <= sources for claim in example['claims']),
    'option_claim_references_exist': all(option['claimId'] in claims for option in example['learnerCard']['motionOptions']),
    'example_has_no_fabricated_human_review': example['humanReview'] is None,
    'example_has_no_fabricated_geometry': example['exactAttachmentGeometry'] is None,
    'example_has_no_fabricated_clip': example['motion']['status'] == 'absent' and all(example['motion'][field] is None for field in ['assetId', 'clipId', 'rigId', 'rangeDegrees']),
    'example_is_not_runtime_data': example['status'] == 'design_example_not_runtime_data',
    'prior_task_plans_preserved': all(
        digest(ROOT / f'work/tasks/archive/R12-before-motion-roadmap/T{n}.md') ==
        PRIOR_PLAN_HASHES[f'T{n}.md']
        for n in range(16, 25)
    ),
    'report_exists': (ROOT / 'work/reports/R13-AI-MOTION-ROADMAP-2026-09-26.md').is_file(),
}
diff_check = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
checks['diff_check'] = diff_check.returncode == 0
before = read_json(HERE / 'protected-before.json')
changed = [{'path': path, 'before': value, 'after': digest(ROOT / path)} for path, value in before.items() if digest(ROOT / path) != value]
result = {
    'scope': 'design consistency only; no anatomy or animation certification',
    'passed': all(checks.values()),
    'checks': checks,
    'prior_task_plan_hashes': PRIOR_PLAN_HASHES,
    'protected_file_count': len(before),
    'observed_runtime_changes_during_concurrent_T15a': changed,
    'runtime_changes_authored_by_this_design_task': [],
    'head_before': BASELINE,
    'head_after': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'diff_check_output': diff_check.stdout + diff_check.stderr,
    'app_tests_rerun': False,
    'application_browser_tests_run': False,
    'reference_site_images_visually_inspected': True,
    'commit_push_deploy_by_this_task': False,
}
(HERE / 'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(0 if result['passed'] else 1)
