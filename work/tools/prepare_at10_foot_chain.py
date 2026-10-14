"""Repair source/native toe-chain roles, not source geometry or clinical points.

The hallux has 3 handles; lesser toes have 4. Original source rig handles and
derived interior model controls remain different records. Actual native cap
addresses are used independently for each side. Helpers/UV/IDs are never edited.
"""
from pathlib import Path
import json,sys,argparse,copy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'work/tools'))
from at10_skin_field_math import cubic_operator
p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--revision',required=True);p.add_argument('--side',choices=['right','left'],required=True);p.add_argument('--base',default='r41');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
E=R/a.evidence;load=lambda p:json.loads(p.read_text());letter='r' if a.side=='right' else 'l'
d=load(E/f'candidates/fit-{a.base}.json');s=np.array(d['sourceVertices']);v=np.array(d['positions'])
f=copy.deepcopy(next(x for x in load(E/'initial-foot-fields-r31.json')['patches'] if x['patch']=='foot-'+a.side))
native=load(R/'work/evidence/AT10/2026-10-13-skin-fit-r1/native-surfaces-r1.json');native.update(load(E/'native-supplement-r1.json'))
source_path=R/'atlas-data/source-cache/datasets/skin-source-review-2026-10-13'
raw=[];groups={};current=''
for line in (source_path/'base.obj').read_text().splitlines():
    z=line.split()
    if not z:continue
    if z[0]=='v':raw.append(list(map(float,z[1:4])))
    elif z[0]=='g':current=z[1]
    elif z[0]=='f' and current.startswith('joint-'):
        groups.setdefault(current,set()).update(int(x.split('/')[0])-1 for x in z[1:])
raw=np.array(raw)
for line in (source_path/'makehuman-asian-male-young.target').read_text().splitlines():
    z=line.split()
    if z and not z[0].startswith('#'):raw[int(z[0])]+=np.array(list(map(float,z[1:4])))
raw*=.1
assert np.abs(raw[np.array(d['originalVertexIds'])]-s).max()<1e-10,'This extremity recipe requires the preserved source-morph coordinates.'
t=np.array([[z['derivedVertices'][0],z['derivedVertices'][j],z['derivedVertices'][j+1]] for z in d['faces'] for j in range(1,len(z['derivedVertices'])-1)])
tree=BVHTree.FromPolygons(s.tolist(),t.tolist(),all_triangles=True)
def embedding(point):
    votes=[]
    for dr in [(-1,.137,.231),(-1,-.217,.113),(-1,.219,-.117)]:
        direction=Vector(dr).normalized();origin=Vector(point);count=0
        for _ in range(40):
            hit,_,_,_=tree.ray_cast(origin,direction,4.)
            if hit is None:break
            count+=1;origin=hit+direction*.000002
        votes.append(count%2)
    return votes
def cap(name,end):
    key=next(k for k,x in native.items() if x['name']==name and x['side']==a.side)
    item=native[key];nv=np.array(item['v']);nt=np.array(item['t']);fraction=.10 if end=='proximal' else .07
    if end=='proximal':ids=np.flatnonzero(nv[:,2]<=nv[:,2].min()+np.ptp(nv[:,2])*fraction)
    else:ids=np.flatnonzero(nv[:,2]>=nv[:,2].max()-np.ptp(nv[:,2])*fraction)
    return nv[ids].mean(0),{'nativeSourceKey':key,'name':name,'side':a.side,'nativeVertexIds':ids.tolist(),'nativeTriangleIds':np.flatnonzero(np.isin(nt,ids).any(1)).tolist(),
        'operator':'observed longitudinal cap vertex mean','frame':'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR','longitudinalAxis':2,'end':end,'fraction':fraction,'anatomicalPrecision':'educational model joint/cap estimate; not cartilage segmentation'}
def source_control(identifier,target,refs,role):
    helper_ids=sorted(groups[identifier]);point=raw[helper_ids].mean(0);original=point.copy();votes=embedding(point)
    record={'id':identifier,'source':point.tolist(),'target':target.tolist(),'sourceVertexIds':helper_ids,'nativeReferences':refs,'role':role,
        'authorship':'AI-authored static model correspondence from observed source chain and actual native bones','sourceOriginalHelperM':original.tolist(),'sourceOriginalEmbeddingVotes':votes,'clinicalLandmarkApproval':False}
    if sum(votes)<2:
        q,n,face,distance=tree.find_nearest(Vector(point));q=np.array(q);verts=t[face]
        normal=np.cross(s[verts[1]]-s[verts[0]],s[verts[2]]-s[verts[0]]);normal/=np.linalg.norm(normal)
        point=q-normal*.0015;assert embedding(point)==[1,1,1]
        record['source']=point.tolist();record['derivedInteriorModelControl']={'originalRigHandlePreserved':True,'sourceTriangle':int(face),'sourceObjFace':d['faces'][face//2]['sourceFace'],
            'sourceOriginalVertexIds':[d['originalVertexIds'][int(i)] for i in verts],'sourceFacetM':s[verts].tolist(),'closestPointM':q.tolist(),
            'inwardDirection':(-normal).tolist(),'modelInwardOffsetM':.0015,'originalOutsideDistanceM':distance,'insideVotes':[1,1,1],
            'meaning':'authored interior control for bone endpoint; original outside rig handle is not a physical bone point'}
    return record
controls=[copy.deepcopy(f['nativeJointControls'][0])]
words=['first','second','third','fourth','fifth']
roles=[]
for digit,word in enumerate(words,1):
    proximal=f'Proximal phalanx of {word} finger of foot';distal=f'Distal phalanx of {word} finger of foot'
    middle=f'Middle phalanx of {word} finger of foot'
    pp,rpp=cap(proximal,'proximal');pd,rpd=cap(proximal,'distal');dp,rdp=cap(distal,'proximal');dt,rdt=cap(distal,'distal')
    if digit==1:
        targets=[(pp,[rpp],'MTP source handle to proximal phalanx proximal cap'),((pd+dp)/2,[rpd,rdp],'IP joint gap between actual proximal/distal phalanx caps'),(dt,[rdt],'distal hallux bone endpoint; outside source tip handle uses separate interior model control')]
    else:
        mp,rmp=cap(middle,'proximal');md,rmd=cap(middle,'distal')
        targets=[(pp,[rpp],'MTP source handle to proximal phalanx proximal cap'),((pd+mp)/2,[rpd,rmp],'PIP joint gap between actual proximal/middle phalanx caps'),
            ((md+dp)/2,[rmd,rdp],'DIP joint gap between actual middle/distal phalanx caps'),(dt,[rdt],'distal bone endpoint, fourth source handle')]
    for part,(target,refs,role) in enumerate(targets,1):
        identifier=f'joint-{letter}-toe-{digit}-{part}';controls.append(source_control(identifier,target,refs,role))
        roles.append({'sourceHandle':identifier,'role':role,'omittedByOldThreeHandleRecipe':digit>1 and part==4,
            'oldDIPToTipMisassignmentCorrected':digit>1 and part==3,'nativeSources':[x['nativeSourceKey'] for x in refs]})
roots=np.array([x['sourceVertex'] for x in f['sharedBoundary']]);ids=np.array(f['sourceVertices'])
centers=np.vstack([s[roots],np.array([x['source'] for x in controls])]);targets=np.vstack([v[roots],np.array([x['target'] for x in controls])]);reg=np.r_[np.full(len(roots),1e-10),np.full(len(controls),1e-8)]
op=cubic_operator(centers,targets,reg);mapped,jac=op(s[ids]);old=v.copy();v[ids]=mapped;v[roots]=old[roots]
f.update(nativeJointControls=controls,sourceFieldCentersM=centers.tolist(),nativeFieldTargetsM=targets.tolist(),regularization=reg.tolist(),
    minimumInitialSampledJacobian=float(np.linalg.det(jac).min()),nonPositiveJacobianCount=int((np.linalg.det(jac)<=0).sum()),sourceToeRoleAudit=roles,
    sourceHelperCounts={'hallux':3,'lesserToesEach':4,'allToeHandles':19},originalSourceHelpersChanged=False,wholeSkinAcceptance=False)
d['positions']=v.tolist();d['candidateRevision']=a.revision;d['fitAcceptancePassed']=False;d['learnerEligible']=False;d['sourceToeRoleAudit']=roles
for path,payload in [(E/f'candidates/fit-{a.revision}.json',d),(E/f'surface-bands-{a.revision}.json',{'patches':[f]})]:
    assert not path.exists();path.write_text(json.dumps(payload,separators=(',',':')))
print({'revision':a.revision,'side':a.side,'toeHandles':19,'nativeControls':len(controls),'minimumJacobian':f['minimumInitialSampledJacobian'],'nonPositive':f['nonPositiveJacobianCount'],
    'derivedInteriorControlCount':sum('derivedInteriorModelControl' in c for c in controls)},flush=True)
