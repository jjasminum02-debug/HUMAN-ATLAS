"""Validate the entire compiled snapshot, independently of Blender and UI."""
import json, math, struct
from pathlib import Path
from collections import Counter
from pack import unpack,digest
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'atlas-data/source-cache/datasets/za/compiled'
INPUT=ROOT/'work/evidence/T98/astra-resolution-2026-09-29'
checks=[]
def check(name,ok):
    checks.append({'name':name,'passed':bool(ok)})
    if not ok:raise AssertionError(name)
def values(doc,blob,index):
    a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']];offset=v.get('byteOffset',0)+a.get('byteOffset',0)
    fmt={5126:'f',5125:'I',5123:'H'}[a['componentType']];width={'VEC3':3,'SCALAR':1}[a['type']]
    return list(struct.iter_unpack('<'+fmt*width,blob[offset:offset+a['count']*width*struct.calcsize(fmt)]))
def main():
    d=json.loads((BASE/'manifest.json').read_text());catalog=json.loads((INPUT/'source-catalog.json').read_text())
    probe=json.loads((INPUT/'evaluated-base-probe.json').read_text())
    # Probe row key is discovered by its actual serialized shape, not inferred source names.
    rows=next(v for v in probe.values() if isinstance(v,list) and v and isinstance(v[0],dict) and 'matrixWorld' in v[0]);byname={r['name']:r for r in rows}
    check('source catalog hash',d['catalogHash']==digest((INPUT/'source-catalog.json').read_bytes()))
    check('target overlay unchanged',d['targetOverlay']==catalog['targetOverlay'])
    check('exclusions unchanged',d['exclusions']==catalog['exclusions'])
    check('classification counts',Counter(i['kind'] for i in d['instances'])=={'muscle_surface_or_part':509,'skeletal_surface':277,'musculoskeletal_accessory':174})
    check('exact source keys',set(i['sourceKey'] for i in d['instances'])==set(i['sourceKey'] for i in catalog['objects']))
    resources={}
    for c in d['chunks']:
        data=(BASE/(c['id']+'.glb')).read_bytes()
        check('chunk '+c['id'],len(data)==c['bytes'] and digest(data)==c['sha256'] and len(data)<=8*1024*1024)
        doc,blob=unpack(data)
        for node in doc['nodes']:
            key=node['extras']['resourceKey'];check('unique resource '+key,key not in resources)
            prim=doc['meshes'][node['mesh']]['primitives'][0]
            p=values(doc,blob,prim['attributes']['POSITION']);n=values(doc,blob,prim['attributes']['NORMAL']);idx=values(doc,blob,prim['indices'])
            check('finite indexed smooth '+key,all(math.isfinite(x) for row in p+n for x in row) and all(abs(sum(x*x for x in v)-1)<1e-3 for v in n) and len(idx)%3==0 and max(v[0] for v in idx)<len(p))
            resources[key]={'positions':p,'triangles':len(idx)//3}
    for i in d['instances']:
        source=next(r for r in catalog['objects'] if r['sourceKey']==i['sourceKey']);old=byname[source['name']]
        for key in source:check(i['sourceKey']+' preserved '+key,i[key]==source[key])
        m=old['matrixWorld'];expected=[m[0],m[2],[-x for x in m[1]],m[3]]
        check(i['sourceKey']+' axis/world exactly once',i['matrix']==[expected[row][col] for col in range(4) for row in range(4)] and not i['transformAppliedToGeometry'])
        check(i['sourceKey']+' detail triangles retained',resources[i['lods']['detail']['resource']]['triangles']==old['triangles'])
        check(i['sourceKey']+' LOD quality',i['quality']['sampledSymmetricErrorMetres']<=i['quality']['toleranceMetres'])
    check('fixed budgets',d['budgetPass'] and d['metrics']['overviewBytes']<=20*1024*1024 and d['metrics']['overviewTriangles']<=1000000 and d['metrics']['overviewGeometryBytes']<=96*1024*1024)
    summary={'passed':True,'checks':len(checks),'instances':len(d['instances']),'chunks':len(d['chunks']),'metrics':d['metrics'],
             'compiledManifestSha256':digest((BASE/'manifest.json').read_bytes()),'quality':'symmetric sampled distance, not guaranteed Hausdorff or anatomical approval',
             'maxSampledErrorMetres':max(i['quality']['sampledSymmetricErrorMetres'] for i in d['instances'])}
    (ROOT/'work/evidence/T99/validation.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
if __name__=='__main__':main()
