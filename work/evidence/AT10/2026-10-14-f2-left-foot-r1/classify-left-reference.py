"""Independent left reference inspection, not a mirrored right face list.

Select only the connected distal Crural fascia template by the actual left MTP
cap plane; record cross-digit witnesses and real surface sections. Original
native is untouched and all raw emitted intersections remain mandatory.
"""
from pathlib import Path
import json,sys,hashlib,collections,numpy as np
R=Path.cwd();E=R/'work/evidence/AT10/2026-10-14-f2-left-foot-r1';sys.path.insert(0,str(R/'work/tools'))
from at10_surface_sections import section_loops
load=lambda p:json.loads(p.read_text());native=load(R/'work/evidence/AT10/2026-10-13-skin-fit-r1/native-surfaces-r1.json');native.update(load(R/'work/evidence/AT10/2026-10-14-skin-fit-r5/native-supplement-r1.json'))
f=load(E/'surface-bands-f2controls1.json')['patches'][0];chains=[[c for c in f['nativeJointControls'] if c['id'].startswith(f'joint-l-toe-{d}-')] for d in range(1,6)]
mtp=np.array([x[0]['target'] for x in chains]);axes=np.array([np.array(x[-1]['target'])-x[0]['target'] for x in chains]);axes/=np.linalg.norm(axes,axis=1)[:,None];axis=axes.mean(0);axis/=np.linalg.norm(axis);offset=float((mtp@axis).min())
key=next(k for k,x in native.items() if x['name']=='Crural fascia' and x['side']=='left');n=native[key];v=np.array(n['v']);t=np.array(n['t']);centres=v[t].mean(1);cohort=np.flatnonzero(centres@axis>=offset)
# Face adjacency is read from LEFT native indices; no right policy is an input.
edges=collections.defaultdict(list)
for i in cohort:
 for a,b in zip(t[i],np.roll(t[i],-1)):edges[tuple(sorted([int(a),int(b)]))].append(int(i))
adj=collections.defaultdict(set)
for ff in edges.values():
 for a in ff:adj[a].update(ff)
remaining=set(cohort.tolist());components=[]
while remaining:
 seen={next(iter(remaining))};todo=list(seen)
 while todo:
  for q in adj[todo.pop()]-seen:seen.add(q);todo.append(q)
 remaining-=seen;components.append(sorted(seen))
assert len(components)==1
# Geometric witness only: a sheet facet spans distinct addressed bone axes.
# This nearest-axis test does NOT approve a source-skin correspondence.
dist=[]
for chain in chains:
 aa=np.array(chain[0]['target']);bb=np.array(chain[-1]['target']);ab=bb-aa
 u=np.clip((v-aa)@ab/(ab@ab),0,1);dist.append(np.linalg.norm(v-aa-u[:,None]*ab,axis=1))
assignment=np.argmin(dist,axis=0)+1
seeds=[int(i) for i in cohort if len(set(assignment[t[i]]))>1]
sections=[]
for z in [.088,.105,.120]:
 loops,opened=section_loops(v,t,np.array([0,0,z]),np.array([0,0,1.]),cohort)
 sections.append({'planeZ':z,'closedLoops':len(loops),'openChains':opened,'loops':loops,'meaning':'native fascia cross section; closed aggregate loop is not an individual toe web'})
result={'schemaVersion':1,'revision':'reference-exceptions-left-f2r1','userAuthorized':True,'authorization':'Current F2 user instruction: 오른쪽991 fascia 예외를 왼쪽으로 mirror하지 말고 왼쪽 실제 참조 문제는 주소별 근거로 분리한다. This authorizes task-scoped AI classification; it is not human anatomy or geometry review.','classificationAuthor':'AI','professorReview':'not_performed','rawFullReferenceQaRequired':True,'frameId':'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR','poseId':'ZA-9f08a17ea0115fed-frame0-autoexec-off','unit':'m','rightExceptionListUsedToSelectLeft':False,'facets':[{'sourceKey':key,'sourceName':n['name'],'side':'left','geometrySha256':hashlib.sha256(v.astype('<f8').tobytes()+t.astype('<u4').tobytes()).hexdigest(),'triangleIds':cohort.tolist(),'nativeReferenceTriangles':len(t),'crossDigitSeedTriangleIds':seeds,'selection':'connected distal template sheet; minimum actual LEFT five-MTP-cap axial plane; selected from left coordinates and topology','boundaryPlane':{'axis':axis.tolist(),'offsetM':offset,'sourceControls':[x[0] for x in chains]},'disposition':'simplified_fascia_forefoot_template_not_homologous_individual_skin','reason':'Independently inspected left fascia is a continuous distal sleeve enclosing multiple bone axes with cross-digit facets; source MakeHuman has separate toe/web surfaces. Retain all other facets; do not force separated toes to enclose an aggregate template. Source and raw QA unchanged.','sourceEdited':False,'allOtherFacetsRemainInFit':True,'skinGeometryApproval':False}],'notClinicalBoundary':True,'learnerEligible':False}
(E/'left-reference-sections.json').write_text(json.dumps({'sourceKey':key,'sections':sections,'crossDigitWitnesses':[{'triangle':i,'vertexIds':t[i].tolist(),'worldM':v[t[i]].tolist(),'geometricallyClosestBoneAxes':assignment[t[i]].tolist()} for i in seeds],'mtpCapControls':[x[0] for x in chains],'selectedFacetBounds':[v[t[cohort]].reshape(-1,3).min(0).tolist(),v[t[cohort]].reshape(-1,3).max(0).tolist()]},separators=(',',':'))+'\n')
(E/'reference-exceptions-left-f2r1.json').write_text(json.dumps(result,indent=2)+'\n');print({'key':key,'leftActualFaces':len(cohort),'retained':len(t)-len(cohort),'crossDigitWitnesses':len(seeds),'components':len(components),'sections':[(x['planeZ'],x['closedLoops']) for x in sections]})
