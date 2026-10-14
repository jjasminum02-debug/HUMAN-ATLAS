import json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path.cwd();E=R/'work/evidence/AT10/2026-10-14-f1-correspondence-r2';d=json.load(open(E/'candidates/fit-f1c7.json'));s=np.array(d['sourceVertices']);t=np.array([[f['derivedVertices'][0],f['derivedVertices'][j],f['derivedVertices'][j+1]] for f in d['faces'] for j in range(1,len(f['derivedVertices'])-1)]);tree=BVHTree.FromPolygons(s.tolist(),t.tolist(),all_triangles=True);recipe=json.load(open(E/'recipe-f1c5.json'));rows=[]
for c in recipe['controls']:
 if not c['id'].startswith('joint-'):continue
 votes=[]
 for dr in [(1,.137,.231),(-1,-.217,.113),(-1,.219,-.117)]:
  direction=Vector(dr).normalized();origin=Vector(c['source']);count=0
  for _ in range(80):
   hit,_,_,_=tree.ray_cast(origin,direction,4.)
   if hit is None:break
   count+=1;origin=hit+direction*.000002
  votes.append(count%2)
 rows.append({'id':c['id'],'sourceM':c['source'],'oddRayVotes':votes,'insideSourceSkinMajority':sum(votes)>=2,'kind':'authored inner axis' if 'sourceInnerModelIndicator' in c else 'original ankle helper' if c['id']=='joint-r-ankle' else 'outer tip model control; not required to be interior'})
(E/'source-control-interiority.json').write_text(json.dumps({'checks':rows,'insideCount':sum(x['insideSourceSkinMajority'] for x in rows),'controlCount':len(rows),'sourceUnmodified':True,'notClinicalLandmarkValidation':True},indent=2)+'\n');print('inside',sum(x['insideSourceSkinMajority'] for x in rows),'of',len(rows))
