"""Muscle actions for the movement UI (ROADMAP M3).

  python3 atlas-data/pipeline/build_actions.py
Table: muscle_actions.py (AI-written from standard texts). Independent check: OpenSim moment arms
(opensim_moment_arms.py on the bundled Rajagopal2016 / Arm26 / WristModel, right side), averaged over five angles inside
the rig's range with the other coordinates at 0. A listed action agrees when the OpenSim moment arm has the same sign and
is at least 2 mm - for the muscle as a whole (mean of its model parts), or for one model part (gluteus medius anterior
fibres), or with the hip flexed 45 degrees for the hip's other dofs (rotation moment arms change sign with flexion).
The sidecar records which basis agreed. Actions OpenSim contradicts are left out of the runtime file (listed in the sidecar); OpenSim
actions >= 10 mm missing from the table are reported, not added.
Writes atlas-data/runtime/muscle-actions.json (runtime) and atlas-data/anatomy/muscle-action-checks.json (check sidecar).
"""
import json
import math
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True  # no __pycache__ next to the pipeline
sys.path.insert(0, str(Path(__file__).resolve().parent))
from muscle_actions import ACTIONS, OPENSIM, OUTSIDE  # noqa: E402
from opensim_moment_arms import Model  # noqa: E402
from muscle_content import CONCEPTS, PARTS, TENDONS  # noqa: E402
from second_sources import kenhub_facts, uams_row, uams_rows  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
MODELS = ROOT / 'OpenSim_Models/Models'
TOKEN = re.compile(r'^(\w+):(\w+)([+-]|=ipsi|=contra)([ps])$')
AGREE_MM, UNLISTED_MM, SAMPLES = 2.0, 10.0, 5
MIDLINE = {'back', 'neck', 'head'}
# Joints added in 4-1 step 4 (no OpenSim model covers them) and the toes: an action is kept only when the UAMS table
# or Kenhub key facts name that movement for the muscle. Words per (joint, dof): (positive direction, negative direction).
FLEX, EXT = r'flex', r'extend|extens'
WORDS = {('sternoclavicular', 'elevation'): (r'elevat|raise|shrug', r'depress|lower|downward|inferior'),
         ('sternoclavicular', 'protraction'): (r'protract|forward|abduct', r'retract|adduct|backward'),
         ('acromioclavicular', 'upwardRotation'): (r'upward|superior(ly)? rotat|rotat\w*[^.;]*(upward|superior)', r'downward|inferior(ly)? rotat|rotat\w*[^.;]*(downward|inferior)'),
         ('neck', 'flexion'): (FLEX, EXT), ('head', 'flexion'): (FLEX, EXT),
         ('neck', 'bending'): (r'lateral(ly)?[ -]*(flex|bend)|side|bend', None), ('neck', 'rotation'): (r'rotat|turn', None),
         ('head', 'rotation'): (r'rotat|turn', None),
         ('cmc1', 'flexion'): (r'flex|oppos', EXT), ('cmc1', 'abduction'): (r'abduct', r'adduct'),
         ('mcp1', 'flexion'): (FLEX, EXT), ('ip1', 'flexion'): (FLEX, EXT),
         ('fingers', 'mcpFlexion'): (FLEX, EXT), ('fingers', 'pipFlexion'): (FLEX, EXT), ('fingers', 'dipFlexion'): (FLEX, EXT),
         ('fingers', 'spread'): (r'abduct', r'adduct'),
         ('mtp1', 'extension'): (r'extend|extens|dorsiflex', FLEX), ('mtp', 'extension'): (r'extend|extens|dorsiflex', FLEX),
         ('iphallux', 'flexion'): (FLEX, EXT), ('toes', 'ipFlexion'): (FLEX, EXT)}


def parse(text):
    return [TOKEN.match(token).groups() for token in text.split()]


def main():
    runtime = json.loads((ROOT / 'atlas-data/runtime/structures.json').read_text())['structures']
    rig = json.loads((ROOT / 'atlas-data/runtime/rig.json').read_text())
    dof_range = {d['id']: d['range'] for j in rig['joints'].values() for d in j['dofs']}
    muscles = [s for s in runtime if s['learner']['visible'] and s['layer'] == 'muscle']
    by_name = {}
    for s in muscles: by_name.setdefault(s['names']['en'], []).append(s)
    unknown = sorted(set(ACTIONS) - set(by_name)) + sorted({n for names in OUTSIDE.values() for n in names} - set(by_name))
    assert not unknown, f'names not in runtime: {unknown}'

    # Independent check: OpenSim moment arms (mm, right side) per ZA name and dof.
    opensim, flexed = {}, {}
    for path, spec in OPENSIM.items():
        model = Model(MODELS / path)
        hip_flexion = next((c for c, d in spec['coordinates'].items() if d == 'hip:flexion'), None)
        for muscle, targets in spec['muscles'].items():
            for coordinate, dof in spec['coordinates'].items():
                flip = -1 if dof.startswith('-') else 1; dof = dof.lstrip('-')
                lo, hi = dof_range[f"{dof.split(':')[0]}_r:{dof.split(':')[1]}"]
                angles = [math.radians(lo + (hi - lo) * (i + .5) / SAMPLES) for i in range(SAMPLES)]
                arm = lambda base=None: flip * sum(model.moment_arm(muscle, coordinate, flip * a, base) for a in angles) / SAMPLES * 1000
                bent = arm({hip_flexion: math.radians(45)}) if hip_flexion and dof.startswith('hip:') and coordinate != hip_flexion else None
                for name in targets if isinstance(targets, list) else [targets]:
                    opensim.setdefault(name, {}).setdefault(dof, []).append(arm())
                    if bent is not None: flexed.setdefault(name, {}).setdefault(dof, []).append(bent)
    parts = opensim
    opensim = {name: {dof: sum(v) / len(v) for dof, v in dofs.items()} for name, dofs in parts.items()}
    flexed = {name: {dof: sum(v) / len(v) for dof, v in dofs.items()} for name, dofs in flexed.items()}

    checks, disagreements, unlisted, rejected = {}, [], [], set()
    for name, text in ACTIONS.items():
        rows = parse(text)
        model = opensim.get(name)
        entry = {'actions': text, 'opensim': {dof: round(v, 1) for dof, v in (model or {}).items() if abs(v) >= AGREE_MM}}
        if model:
            for joint, dof, sign, role in rows:
                key = f'{joint}:{dof}'
                if key not in model or sign.startswith('='): continue
                agrees = lambda mm: abs(mm) >= AGREE_MM and (mm > 0) == (sign == '+')
                arm = model[key]
                basis = 'whole' if agrees(arm) else 'part' if any(agrees(a) for a in parts[name][key]) \
                    else 'hipFlexed45' if agrees(flexed.get(name, {}).get(key, 0)) else None
                if basis is None:
                    disagreements.append({'muscle': name, 'action': f'{key}{sign}{role}', 'opensimMm': round(arm, 1)})
                    rejected.add((name, key))
                elif basis != 'whole':
                    entry.setdefault('agreedBy', {})[key] = {'basis': basis, 'parts': [round(a, 1) for a in parts[name][key]],
                                                             'hipFlexed45Mm': round(flexed.get(name, {}).get(key, 0), 1)}
            listed = {f'{j}:{d}' for j, d, _, _ in rows}
            for key, arm in model.items():
                if abs(arm) >= UNLISTED_MM and key not in listed:
                    unlisted.append({'muscle': name, 'dof': key, 'opensimMm': round(arm, 1)})
        checks[name] = entry

    # Second-source check for joints OpenSim cannot speak to.
    second, unconfirmed = uams_rows(), []
    for name, text in ACTIONS.items():
        concept = TENDONS.get(name) or PARTS.get(name, name); wiki = CONCEPTS.get(concept, {}).get('wiki', concept)
        sources = {}
        for joint, dof, sign, role in parse(text):
            key = f'{joint}:{dof}'
            if (joint, dof) not in WORDS or (key in opensim.get(name, {}) and not sign.startswith('=')): continue
            if not sources:
                uams = uams_row(second, name, concept, wiki); facts = kenhub_facts(wiki, concept)
                sources = {'uams': (uams or {}).get('action', ''), 'kenhub': (facts or {}).get('action', ''), '_': 'looked up'}
            positive, negative = WORDS[(joint, dof)]
            pattern = positive if sign in ('+', '=ipsi', '=contra') or negative is None else negative
            found = [by for by in ('uams', 'kenhub') if sources[by] and re.search(pattern, sources[by].lower())]
            if found: checks[name].setdefault('confirmedBy', {})[f'{key}{sign}'] = found
            else:
                unconfirmed.append({'muscle': name, 'action': f'{key}{sign}{role}', 'uams': sources['uams'][:160] or None, 'kenhub': sources['kenhub'][:160] or None})
                rejected.add((name, key))

    out, outside = {}, {}
    for label, names in OUTSIDE.items():
        for name in names: outside.setdefault(name, []).append(label)
    for s in muscles:
        name = s['names']['en']
        if name not in ACTIONS and name not in outside: continue
        suffix = 'l' if s['side'] == 'left' else 'r'
        actions = []
        for joint, dof, sign, role in parse(ACTIONS.get(name, '')):
            if (name, f'{joint}:{dof}') in rejected: continue
            if sign.startswith('='):
                if s['side'] not in ('left', 'right'): continue
                # rig back/neck/head bending and rotation: + = toward the subject's left
                toward_left = (s['side'] == 'left') == (sign == '=ipsi')
                value = 1 if toward_left else -1
            else: value = 1 if sign == '+' else -1
            actions.append({'dof': f'{joint}:{dof}' if joint in MIDLINE else f'{joint}_{suffix}:{dof}', 'sign': value,
                            'role': 'primary' if role == 'p' else 'assist'})
        row = {'actions': actions}
        if name in outside: row['outside'] = outside[name]
        out[s['key']] = row
    for row in out.values():
        for a in row['actions']: assert a['dof'] in dof_range, a

    (ROOT / 'atlas-data/runtime/muscle-actions.json').write_text(json.dumps(
        {'schemaVersion': 1, 'note': 'AI-written action table checked against OpenSim moment arms, or the UAMS / Kenhub tables for the shoulder girdle, '
                 'neck, fingers and toes; see atlas-data/anatomy/muscle-action-checks.json',
         'muscles': out}, ensure_ascii=False, separators=(',', ':')) + '\n')
    checked = sum(1 for n in ACTIONS if n in opensim)
    (ROOT / 'atlas-data/anatomy/muscle-action-checks.json').write_text(json.dumps(
        {'schemaVersion': 1, 'method': __doc__.strip(), 'summary': {'tableMuscles': len(ACTIONS), 'opensimChecked': checked,
         'disagreements': len(disagreements), 'unlisted': len(unlisted), 'unconfirmed': len(unconfirmed)},
         'disagreements': disagreements, 'unlisted': unlisted, 'unconfirmed': unconfirmed, 'muscles': checks}, ensure_ascii=False, indent=1) + '\n')
    print('ACTIONS', json.dumps({'structures': len(out), 'tableMuscles': len(ACTIONS), 'opensimChecked': checked,
                                 'disagreements': len(disagreements), 'unlisted': len(unlisted), 'unconfirmed': unconfirmed}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
