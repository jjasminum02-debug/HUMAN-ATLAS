"""Measure saved r8 new vertex-containment samples, not continuous intersections."""
from pathlib import Path
import json,sys
import numpy as np
R=Path.cwd();E=Path(__file__).resolve().parent
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb,channel_data,node_positions
from author_source_surface_motion import array
from t66_contact_correctives import nearest_surface_details
audit=json.loads((E/'neighbor-contact-comparison-r8.json').read_text());rows=[]
for row in audit['rows']:
    side=row['side'];_,d,b=read_glb(E/f'{side}-candidate-r8/motion.glb');tracks=channel_data(d,b)
    for neighbor in row['neighbors']:
        ni=next(i for i,n in enumerate(d['nodes']) if n.get('extras',{}).get('sourceKey')==neighbor['sourceKey'])
        p=d['meshes'][d['nodes'][ni]['mesh']]['primitives'][0];tri=array(d,b,p['indices']).reshape(-1,3);samples=[]
        for s in neighbor['samples']:
            ids=s['newIndices']
            if not ids:continue
            t=s['seconds'];v=node_positions(d,b,tracks,47,t)[ids];context=node_positions(d,b,tracks,ni,t)
            nearest,_=nearest_surface_details(v,context,tri);depth=np.linalg.norm(v-nearest,axis=1)*1000
            samples.append({'seconds':t,'sourceIndices':ids,'nearestSurfaceDistancesMm':depth.tolist()})
        rows.append({'side':side,'neighbor':neighbor['name'],'maximumNewContainedVertices':max(s['newVsPriorSamePose'] for s in neighbor['samples']),
            'maximumSampledNewPenetrationMm':max((max(s['nearestSurfaceDistancesMm']) for s in samples),default=0),'samples':samples})
        print(side,neighbor['name'],rows[-1]['maximumSampledNewPenetrationMm'],flush=True)
(E/'neighbor-new-depth-r8.json').write_text(json.dumps({'rows':rows,'limitation':'nearest surface distance of saved new contained vertices only; not all triangle intersections, tissue physiology or a modified acceptance threshold'},indent=2)+'\n')
