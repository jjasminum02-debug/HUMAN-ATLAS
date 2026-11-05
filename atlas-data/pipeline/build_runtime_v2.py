"""Build the v2 runtime data (ROADMAP D2): one structures.json, one relations.json, one geometry set.

  python3 atlas-data/pipeline/build_runtime_v2.py
Inputs: D1 extraction (source-cache/datasets/za-full) and the frozen pre-v2 runtime
(runtime/legacy/runtime-2026-11-03.json). Structures that existed before keep their key, names,
content links, display decision, matrix, resource keys and chunk bytes exactly. New structures
(ligaments, capsules, attachment patches, CNS ...) use D1 geometry packed into small on-demand chunks.
Outputs: atlas-data/runtime/{structures,relations}.json (tracked) and
source-cache/datasets/za-v2/{chunks/,geometry.json} (local geometry, not tracked).
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'atlas-data/tools/datasets'))
from pack import pack  # noqa: E402  (shared chunk packer)

D1 = ROOT / 'atlas-data/source-cache/datasets/za-full'
LEGACY = ROOT / 'atlas-data/runtime/legacy/runtime-2026-11-03.json'
RUNTIME = ROOT / 'atlas-data/runtime'
GEOMETRY = ROOT / 'atlas-data/source-cache/datasets/za-v2'
NAVIGATION = ROOT / 'atlas-data/navigation/atlas-navigation.json'
ON_DEMAND_CHUNK_BYTES = 2 * 1024 * 1024
LEGACY_NAMESPACE, NEW_NAMESPACE = 'za-c7010a9', 'za-v2'

# Display layer per structure (ROADMAP V1, vessels Q2-1). None = not shown as a layer yet (CNS, sense organs,
# attachment patches, sinus/air-cell cavities, heart surface landmarks).
FASCIA_KINDS = {'fascia', 'aponeurosis', 'retinaculum', 'septum', 'raphe', 'sheath', 'connective'}
def layer_of(system, kind):
    if system == 'skeletal': return 'bone' if kind in ('bone', 'cartilage', 'tooth') else None
    if system == 'muscular':
        return 'muscle' if kind in ('muscle', 'tendon') else 'fascia' if kind in FASCIA_KINDS else 'joint' if kind in ('bursa', 'ligament') else None
    if system == 'joint': return 'joint' if kind else None
    if system == 'nervous': return 'nerve' if kind == 'nerve' else None
    if system == 'cardiovascular': return 'vessel' if kind in ('artery', 'vein', 'heart') else None  # Q2-1
    return None
# Korean tissue-type words for search and card labels (type terms, not structure names).
TYPE_TERMS = {'ligament': ['인대'], 'capsule': ['관절주머니', '관절낭'], 'disc': ['원판', '디스크'], 'meniscus': ['반달', '반월판'],
              'labrum': ['관절테두리', '관절순'], 'membrane': ['막'], 'cartilaginous_joint': ['연골결합'], 'cartilage': ['연골'],
              'fat_pad': ['지방체'], 'bursa': ['윤활주머니', '점액낭'], 'fascia': ['근막'], 'aponeurosis': ['널힘줄', '건막'],
              'retinaculum': ['지지띠'], 'septum': ['사이막'], 'raphe': ['솔기'], 'sheath': ['힘줄집', '건초'], 'connective': ['결합조직'],
              'tendon': ['힘줄', '건'], 'tooth': ['치아'], 'artery': ['동맥', '혈관'], 'vein': ['정맥', '혈관'], 'heart': ['심장']}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def centre(bounds):
    lo, hi = (bounds['min'], bounds['max']) if isinstance(bounds, dict) else bounds
    return [(a + b) / 2 for a, b in zip(lo, hi)]


def box_distance(a, b):
    (alo, ahi), (blo, bhi) = a, b
    return sum(max(0., blo[i] - ahi[i], alo[i] - bhi[i]) ** 2 for i in range(3)) ** .5


def geometry_bytes(lod):
    return lod['vertices'] * 24 + lod['triangles'] * 3 * (2 if lod['vertices'] <= 65535 else 4)


def main():
    d1 = json.loads((D1 / 'structures.json').read_text())['structures']
    legacy = json.loads(LEGACY.read_text())
    regions_allowed = [c['id'] for c in json.loads(NAVIGATION.read_text())['categories']]
    rows = {r['sourceKey']: r for r in legacy['rows']}
    legacy_by_name = {i['sourceName']: (i, rows[i['sourceKey']]) for i in legacy['instances']}
    by_id = {s['id']: s for s in d1}
    assert len(legacy_by_name) == len(legacy['instances'])

    key_of = {}
    for s in d1:
        old = legacy_by_name.get(s['sourceName'])
        key_of[s['id']] = old[0]['sourceKey'] if old else 'ZA-' + sha(s['sourceName'].encode())[:24]
    assert len(set(key_of.values())) == len(key_of), 'runtime key collision'
    missing = set(legacy_by_name) - {s['sourceName'] for s in d1}
    assert not missing, f'pre-v2 structures missing from D1: {sorted(missing)[:5]}'

    # Region membership for new structures: the attachment's own bone, else the two nearest pre-v2 bones.
    legacy_bones = [(row['regionIds'], row['bounds'], row['side']) for _, row in legacy_by_name.values()
                    if row['kind'] == 'bone' and row['regionIds']]
    def nearest_bone_regions(bounds, side):
        box = (bounds['min'], bounds['max'])
        pool = [b for b in legacy_bones if side == 'unpaired' or b[2] in (side, None, 'unpaired')] or legacy_bones
        nearest = sorted(pool, key=lambda b: box_distance(box, b[1]))[:2]
        return sorted({r for regions, _, _ in nearest for r in regions}, key=regions_allowed.index)

    nerve_pose = next(row['nerve']['poseId'] for _, row in legacy_by_name.values() if 'nerve' in row)
    # C1: Korean names for structures that had none (names_ko.py; KAA-dictionary-checked where possible).
    names_ko_path = ROOT / 'atlas-data/terminology/structure-names-ko.json'
    names_ko = json.loads(names_ko_path.read_text())['entries'] if names_ko_path.exists() else {}
    def with_korean(record):
        found = names_ko.get(record['names']['en'])
        if found and not record['names']['koModern']:
            record['names'] = {'koTraditional': found['koTraditional'], 'koModern': found['koModern'], 'en': record['names']['en']}
            # Default title is the Sino-Korean term in Hangul (project naming rule), as for pre-v2 muscles and bones.
            record['label'] = found['koTraditional'] or found['koModern']
            record['aliases'] = record['aliases'] + [a for a in found.get('aliases', []) if a not in record['aliases']]
        return record
    structures, new_resources = [], {}
    for s in d1:
        old = legacy_by_name.get(s['sourceName'])
        layer = layer_of(s['system'], s['kind'])
        superficial = any('Superficial muscles' in part for path in s['bonusPaths'] for part in path)
        record = {'id': s['id'], 'key': key_of[s['id']], 'sourceName': s['sourceName'], 'system': s['system'], 'kind': s['kind'],
                  'side': s['side'], 'bodyRegions': s['regions'], 'layer': layer,
                  'depth': ('superficial' if superficial else 'deep') if layer == 'muscle' else None}
        if old:
            instance, row = old
            # Previously hidden accessories (fascia, bursae, cartilage ...) become visible through their layer.
            was_accessory = row['kind'] == 'accessory'
            visible = (layer is not None) if was_accessory else row['localDisplayEligible']
            record.update({
                'regions': row['regionIds'] or (nearest_bone_regions({'min': row['bounds'][0], 'max': row['bounds'][1]}, s['side']) if visible else []),
                'names': row['names'], 'label': row['label'],
                'aliases': row['aliases'] + (TYPE_TERMS.get(s['kind'], []) if was_accessory else []),
                'searchGroup': row['searchGroupKey'],
                'learner': {'visible': visible, 'defaultVisible': visible if was_accessory else row['defaultVisible'],
                            'inspectable': visible if was_accessory else row['inspectionEligible'], 'sourceOnly': row['sourceOnly']},
                'content': {'haConceptId': row['haConceptId'], 'learnerConceptKeys': row['learnerConceptKeys']},
                'geometry': {'namespace': LEGACY_NAMESPACE, 'instanceKind': instance['kind'], 'matrix': instance['matrix'],
                             'bounds': row['bounds'], 'hideRender': row['sourceHiddenStatePreserved']['hideRender'],
                             'lods': {level: {k: instance['lods'][level][k] for k in ('resource', 'chunk', 'triangles', 'vertices', 'geometryBytes')}
                                      for level in ('overview', 'detail')}},
            })
            if 'nerve' in row:
                record['nerve'] = {'poseId': row['nerve']['poseId']}
        else:
            if s['system'] == 'attachment' and s.get('boneId') and by_id[s['boneId']]['sourceName'] in legacy_by_name:
                regions = legacy_by_name[by_id[s['boneId']]['sourceName']][1]['regionIds']
            else:
                regions = nearest_bone_regions(s['bounds'], s['side'])
            lods = {}
            for level in ('overview', 'detail'):
                lod = s['lods'][level]
                new_resources[(lod['sha256'], level)] = {'path': D1 / lod['path'], 'system': s['system'], 'level': level,
                                                'triangles': lod['triangles'], 'vertices': lod['vertices'], 'geometryBytes': geometry_bytes(lod)}
                lods[level] = {'resource': lod['sha256'], 'chunk': None, 'triangles': lod['triangles'], 'vertices': lod['vertices'],
                               'geometryBytes': geometry_bytes(lod)}
            record.update({
                'regions': regions, 'names': {'koTraditional': None, 'koModern': None, 'en': s['name']}, 'label': s['name'],
                'aliases': TYPE_TERMS.get(s['kind'], []), 'searchGroup': s['name'],
                'learner': {'visible': layer is not None, 'defaultVisible': layer is not None, 'inspectable': layer is not None, 'sourceOnly': True},
                'content': {'haConceptId': None, 'learnerConceptKeys': []},
                'geometry': {'namespace': NEW_NAMESPACE, 'instanceKind': 'musculoskeletal_accessory', 'matrix': s['matrix'],
                             'bounds': [s['bounds']['min'], s['bounds']['max']], 'hideRender': False, 'lods': lods},
            })
        if layer == 'nerve' and 'nerve' not in record:
            record['nerve'] = {'poseId': nerve_pose}  # same static frame-0 source pose as the pre-v2 nerves
        structures.append(with_korean(record))

    # Pack new geometry into small on-demand chunks, grouped by system and level so a layer loads only its own.
    (GEOMETRY / 'chunks').mkdir(parents=True, exist_ok=True)
    chunks = [{**c, 'namespace': LEGACY_NAMESPACE, 'onDemand': False} for c in legacy['chunks']]
    for c in chunks:
        assert sha((GEOMETRY / 'chunks' / f"{c['sha256']}.glb").read_bytes()) == c['sha256'], 'frozen chunk changed'
    chunk_of = {}
    groups = {}
    for (key, level), r in sorted(new_resources.items()):
        groups.setdefault((r['system'], level), []).append(key)
    for (system, level), keys in sorted(groups.items()):
        batch, size = [], 0
        def flush():
            if not batch: return
            data = pack([(k, Path(new_resources[(k, level)]['path']).read_bytes()) for k in batch]); h = sha(data)
            (GEOMETRY / 'chunks' / f'{h}.glb').write_bytes(data)
            chunks.append({'id': h, 'sha256': h, 'bytes': len(data), 'level': level, 'resources': list(batch), 'namespace': NEW_NAMESPACE,
                           'onDemand': True, 'system': system, 'geometryBytes': sum(new_resources[(k, level)]['geometryBytes'] for k in batch)})
            for k in batch: chunk_of.setdefault((k, level), h)
            batch.clear()
        for key in keys:
            data_size = Path(new_resources[(key, level)]['path']).stat().st_size
            if batch and size + data_size > ON_DEMAND_CHUNK_BYTES - 4096: flush(); size = 0
            batch.append(key); size += data_size
        flush()
    for record in structures:
        for level, lod in record['geometry']['lods'].items():
            if lod['chunk'] is None: lod['chunk'] = chunk_of[(lod['resource'], level)]
    resources = dict(legacy['resources'])
    for (key, _), r in new_resources.items():
        resources.setdefault(key, {k: r[k] for k in ('triangles', 'vertices', 'geometryBytes')})

    # Relations: ZA attachment patches, plus pre-v2 nerve and related-muscle links (mapped to v2 ids).
    id_of_key = {v: k for k, v in key_of.items()}
    relations = []
    for s in d1:
        if s['system'] == 'attachment':
            relations.append({'type': s['kind'], 'from': s['id'], 'owners': s['ownerIds'], 'bone': s.get('boneId')})
    for _, row in legacy_by_name.values():
        for target in row.get('nerve', {}).get('branchKeys', []):
            relations.append({'type': 'nerve_branch', 'from': id_of_key[row['sourceKey']], 'to': id_of_key[target]})
        for target in row.get('nerve', {}).get('muscleKeys', []):
            relations.append({'type': 'innervates', 'from': id_of_key[row['sourceKey']], 'to': id_of_key[target]})
        for related in row['relatedMuscles']:
            relations.append({'type': 'related_muscle', 'from': id_of_key[row['sourceKey']], 'to': id_of_key[related['sourceKey']],
                              'label': related['label'], 'roles': related['roles']})

    structures.sort(key=lambda r: r['id'])
    RUNTIME.mkdir(parents=True, exist_ok=True)
    def write(path, obj):
        tmp = path.with_suffix('.tmp'); tmp.write_text(json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '\n'); tmp.replace(path)
    revision = sha(json.dumps([structures, relations], sort_keys=True).encode())
    write(RUNTIME / 'structures.json', {'schemaVersion': 2, 'revision': revision, 'frame': 'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR, metres',
                                        'source': 'Z-Anatomy (CC BY-SA 4.0)', 'regions': regions_allowed, 'compat': legacy['compat'],
                                        'structures': structures})
    write(RUNTIME / 'relations.json', {'schemaVersion': 2, 'revision': revision, 'relations': relations})
    write(GEOMETRY / 'geometry.json', {'schemaVersion': 2, 'revision': revision, 'chunks': chunks, 'resources': resources})
    print(json.dumps({'structures': len(structures), 'preV2': sum(r['geometry']['namespace'] == LEGACY_NAMESPACE for r in structures),
                      'relations': len(relations), 'chunks': len(chunks), 'onDemandChunks': sum(c['onDemand'] for c in chunks),
                      'onDemandBytes': sum(c['bytes'] for c in chunks if c['onDemand']), 'revision': revision[:12]}))


if __name__ == '__main__':
    main()
