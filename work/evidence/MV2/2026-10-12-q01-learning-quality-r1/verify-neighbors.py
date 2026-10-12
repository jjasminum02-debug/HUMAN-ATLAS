from pathlib import Path
import json,sys
import numpy as np
R=Path.cwd();E=Path(__file__).resolve().parent;revision=sys.argv[1]
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb,channel_data,node_positions,bounded_inside
from author_source_surface_motion import array
names={r['sourceKey']:r['name'] for r in json.loads((R/'atlas-data/source-cache/datasets/za/compiled/manifest.json').read_text())['instances']};out=[]
for side in ['left','right']:
    _,d,b=read_glb(E/f'{side}-candidate-{revision}/motion.glb');tr=channel_data(d,b);_,old,ob=read_glb(R/f'atlas-data/assets/motion/mv2-q01-r1-{side}/motion.glb');ot=channel_data(old,ob);rows=[]
    keys=tr[(47,'weights')][0];times=sorted(set(float(a+(c-a)*k/8) for a,c in zip(keys[:-1],keys[1:]) for k in range(9)))
    for n,node in enumerate(d['nodes']):
        if not names.get(node.get('extras',{}).get('sourceKey'),'').startswith('Vastus'):continue
        p=d['meshes'][node['mesh']]['primitives'][0];tri=array(d,b,p['indices']).reshape(-1,3);samples=[]
        for t in times:
            neighbor=node_positions(d,b,tr,n,t);before=node_positions(old,ob,ot,47,t);after=node_positions(d,b,tr,47,t);a=bounded_inside(before,neighbor,tri);c=bounded_inside(after,neighbor,tri)
            samples.append({'seconds':float(t),'beforeContained':int(a.sum()),'afterContained':int(c.sum()),'newVsPriorSamePose':int((c&~a).sum()),'newIndices':np.flatnonzero(c&~a).tolist()})
        rows.append({'sourceKey':node['extras']['sourceKey'],'name':names[node['extras']['sourceKey']],'samples':samples})
    out.append({'side':side,'neighbors':rows});print(side,[(r['name'],max(x['newVsPriorSamePose'] for x in r['samples'])) for r in rows],flush=True)
(E/f'neighbor-contact-comparison-{revision}.json').write_text(json.dumps({'rows':out,'sampleCountPerNeighbor':len(times),'limitation':'sampled vertex containment against accepted same-pose source overlaps, not complete surface intersections or continuous collision freedom'},indent=2)+'\n')
