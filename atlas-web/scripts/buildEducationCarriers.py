"""Offline native-envelope compiler. No point authoring, source writes or left mirroring."""
from pathlib import Path
from collections import Counter
import argparse, ast, hashlib, json, struct
import numpy as np
from nativeSurfaceIntersections import SurfaceIndex

R=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--evidence-dir',required=True,help='Workspace-relative evidence directory for this run')
parser.add_argument('--config',help='Optional workspace-relative registered native inputs/region configuration')
parser.add_argument('--output-dir',help='Versioned carrier directory; never overwrite a historical registration')
args=parser.parse_args()
E=(R/args.evidence_dir).resolve()
assert E.is_relative_to(R/'work/evidence'),'Evidence must remain in work/evidence'
A=R/'work/evidence/acupoint-AC1'
OUT=R/'atlas-data/acupoints/carriers/education-r1'
if args.output_dir:
    OUT=(R/args.output_dir).resolve()
    assert OUT.is_relative_to(R/'atlas-data/acupoints/carriers') and not OUT.exists(),'New carrier output must be an unused versioned directory'
read=lambda p:json.loads(p.read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
dataset=read(A/'runtime-dataset.json')
rows={r['sourceKey']:r for r in read(A/'runtime-integration.json')['objects'] if r['sourceKey'].startswith('ZA-c7010a9-')}
cache=R/'atlas-data/source-cache/datasets/za'
inputs,meshes={},{}
reader_path=A/'build_carrier.py'
tree=ast.parse(reader_path.read_text())
reader=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='world')
exec(compile(ast.Module(body=[reader],type_ignores=[]),str(reader_path),'exec'),globals())

def find(name,side):
    ks=[k for k,r in rows.items() if r['names']['en']==name and r['side']==side]
    assert len(ks)==1,(name,side,ks)
    return ks[0]

def eligible(r):
    return not r['hardHoldReasons'] and (r['kind'] in ['muscle','bone'] or 'fascia' in r['names']['en'].lower())

class Native:
    def __init__(self,keys,dimension=1):
        self.keys=keys;self.dimension=dimension
        self.tri=np.concatenate([world(k)[0][world(k)[1]] for k in keys])
        self.ids=np.concatenate([np.full(len(world(k)[1]),i) for i,k in enumerate(keys)])
        self.faces=np.concatenate([np.arange(len(world(k)[1])) for k in keys])
        self.lo=self.tri[:,:,dimension].min(axis=1);self.hi=self.tri[:,:,dimension].max(axis=1)
    def at(self,y):
        mask=(self.lo<=y+1e-9)&(self.hi>=y-1e-9)
        ids=np.flatnonzero(mask)
        return self.tri[ids],ids
    def cast(self,origin,direction,limit):
        tri,ids=self.at(origin[self.dimension]);e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0]
        pv=np.cross(direction,e2);det=np.einsum('ij,ij->i',e1,pv)
        inv=np.divide(1,det,out=np.zeros_like(det),where=np.abs(det)>1e-12)
        tv=origin-tri[:,0];u=np.einsum('ij,ij->i',tv,pv)*inv;q=np.cross(tv,e1)
        v=q@direction*inv;d=np.einsum('ij,ij->i',e2,q)*inv
        hit=(np.abs(det)>1e-12)&(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)&(d>0)&(d<limit)
        chosen=np.flatnonzero(hit)
        if not len(chosen):return None
        n=chosen[np.argmax(d[chosen])];i=ids[n]
        return origin+d[n]*direction,{'sourceKey':self.keys[self.ids[i]],'triangle':int(self.faces[i]),'barycentric':[float(1-u[n]-v[n]),float(u[n]),float(v[n])],'distance':float(d[n])}

def section(keys,y,dimension=1):
    points=[];used=[]
    for k in keys:
        v,t=world(k);tri=v[t]
        if y<tri[:,:,dimension].min() or y>tri[:,:,dimension].max():continue
        p=tri;q=tri[:,[1,2,0]];den=q[:,:,dimension]-p[:,:,dimension]
        hit=(np.abs(den)>1e-12)&((p[:,:,dimension]<=y)!=(q[:,:,dimension]<=y))
        a=np.divide(y-p[:,:,dimension],den,out=np.zeros_like(den),where=np.abs(den)>1e-12)
        pts=(p+a[:,:,None]*(q-p))[hit]
        if len(pts):points.append(pts);used.append(k)
    if not points:return None,[]
    p=np.concatenate(points);c=(p.min(axis=0)+p.max(axis=0))/2;c[dimension]=y
    return c,used

def axis(keys,levels,dimension=1):
    exact=[section(keys,y,dimension) for y in levels];valid=[i for i,(c,k) in enumerate(exact) if c is not None]
    assert valid and valid[0]==0 and valid[-1]==len(levels)-1,'unbracketed axis input'
    centers=[];records=[]
    for i,y in enumerate(levels):
        c,ks=exact[i]
        if c is None:
            a=max(j for j in valid if j<i);b=min(j for j in valid if j>i)
            f=(y-levels[a])/(levels[b]-levels[a]);c=exact[a][0]*(1-f)+exact[b][0]*f;c[dimension]=y
            ks=sorted(set(exact[a][1]+exact[b][1]));kind='bracketed_native_section_interpolation'
        else:kind='native_section_bounds_center'
        centers.append(c);records.append({'level':i,'y':float(y),'center':c.tolist(),'sourceKeys':ks,'kind':kind})
    return np.array(centers),records

configs=[]
trunk=[k for k,r in rows.items() if eligible(r) and set(r['regionIds'])&{'thorax','back','abdomen-lumbar','pelvis-perineum','gluteal-hip'} and r['bounds'][1][1]>.87 and r['bounds'][0][1]<1.43]
spine=[find(f'Vertebra {n}{i}',None) for n,rg in [('L',range(1,6)),('T',range(1,13))] for i in rg] + [find('Sacrum',None)]
configs.append({'id':'trunk','side':'midline','sources':trunk,'axis':spine,'range':(.872,1.423),'angles':64,'steps':48,'limit':.32,'cuts':[1.05,1.24], 'labels':['골반·몸통 아래','배·허리','가슴·등']})
for side in ['right','left']:
    arm=[k for k,r in rows.items() if r['side']==side and eligible(r) and 'upper-limb' in r['regionIds'] and r['bounds'][1][1]>.866 and r['bounds'][0][1]<1.413 and (r['kind']=='muscle' or r['names']['en'] in ['Humerus','Radius','Ulna','Brachial fascia','Antebrachial fascia','Deltoid fascia'])]
    configs.append({'id':f'arm-{side}','side':side,'sources':arm,'axis':[find(n,side) for n in ['Humerus','Radius','Ulna']],'range':(.866,1.402),'angles':40,'steps':64,'limit':.09,'cuts':[1.10],'labels':['아래팔','위팔·어깨 경계']})
    leg=[k for k,r in rows.items() if r['side']==side and eligible(r) and set(r['regionIds'])&{'thigh','leg','gluteal-hip'} and r['bounds'][1][1]>.085 and r['bounds'][0][1]<.866]
    # Accessory region membership is not always learner-facing; select actual named native fascia too.
    leg+= [find(n,side) for n in ['Fascia lata','Crural fascia','Popliteal fascia'] if find(n,side) not in leg]
    configs.append({'id':f'leg-{side}','side':side,'sources':leg,'axis':[find(n,side) for n in ['Femur','Tibia','Patella']],'range':(.085,.866),'angles':48,'steps':100,'limit':.20,'cuts':[.415],'labels':['종아리·무릎 경계','넙다리']})

config_data=None
if args.config:
    config_path=(R/args.config).resolve();assert config_path.is_relative_to(R)
    config_data=read(config_path);inputs[str(config_path.relative_to(R))]=sha(config_path.read_bytes())
    for item in config_data.get('probeInputs',[]):
        path=R/item['path'];assert sha(path.read_bytes())==item['sha256']
        inputs[item['path']]=item['sha256'];probe=read(path)
        assert probe['frame']==dataset['frameContract']['targetFrameId'] and probe['unit']=='m'
        assert probe['sourceSha256']=='9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd'
        obj=next(o for o in probe['objects'] if o['name']==item['object'])
        v=np.array(obj['positions']);t=np.array(obj['indices'],dtype='<u4')
        if 'triangleIds' in item:t=t[item['triangleIds']]
        meshes[item['key']]=(v,t)
        rows[item['key']]={'sourceKey':item['key'],'names':{'en':item['object']},'side':item['side'],'kind':'native_probe','bounds':[v[t].min(axis=(0,1)).tolist(),v[t].max(axis=(0,1)).tolist()],
          'hardHoldReasons':['source-not-in-learner-runtime'],'localDisplayEligible':False,'regionIds':[],
          'probeInput':item,'nativeTriangleIndexMap':item.get('triangleIds')}
    configs=config_data['regions']

rights={'source':'Z-Anatomy CC BY-SA 4.0; BodyParts3D CC BY-SA 2.1 Japan attribution retained; exact ancestry not invented','localObservation':'supported','publicRedistribution':'held','professorReview':'not_performed'}
entries=[];audits=[];all_hits={};seams=[];mapping={}
previous=read(OUT/'manifest.json') if config_data and (OUT/'manifest.json').exists() else None
# Include native anatomy at shoulder/neck/hand boundaries outside ray-source sets.
collision_keys=[k for k,r in rows.items() if eligible(r) and r['bounds'][1][1]>-.02 and r['bounds'][0][1]<1.80]
collision_keys=sorted(set(collision_keys)|{k for cfg in configs for k in cfg['sources']+cfg['axis']})
for k in collision_keys:world(k)
body_surfaces=SurfaceIndex({k:meshes[k] for k in collision_keys})
OUT.mkdir(parents=True,exist_ok=True);E.mkdir(parents=True,exist_ok=True)
for cfg in configs:
    levels=np.array(sorted(set(np.linspace(*cfg['range'],cfg['steps']).tolist()+cfg['cuts'])))
    dimension=cfg.get('dimension',1);clearance=cfg.get('clearanceMetres',.006);max_edge=cfg.get('maxEdgeMetres',.03)
    centers,axis_records=axis(cfg['axis'],levels,dimension);native=Native(cfg['sources'],dimension);na=cfg['angles']
    points=[];directions=[];hits=[];missing=[]
    for j,(y,origin) in enumerate(zip(levels,centers)):
        for a in range(na):
            theta=a/na*2*np.pi;direction=np.array([-np.sin(theta),0,np.cos(theta)]) if dimension==1 else np.array([-np.sin(theta),np.cos(theta),0])
            h=native.cast(origin,direction,cfg['limit'])
            if h is None:
                points.append([0,y,0]);hits.append(None);missing.append([j,a])
            else:
                p,h=h;points.append(p);hits.append({'sample':j*na+a,'level':j,'angle':a,**h})
            directions.append(direction)
    ref=np.array(points);directions=np.array(directions)
    proposed=(ref+clearance*directions).astype('<f4')
    # No faces are allowed to fill missing rays or jump to an adjacent component.
    kept=[];rejected=[];clearances=[]
    weights=np.array([[1/3]*3,[.5,.5,0],[.5,0,.5],[0,.5,.5],[.6,.2,.2],[.2,.6,.2],[.2,.2,.6]])
    def center_at(y):return np.array([np.interp(y,levels,centers[:,k]) for k in range(3)])
    for j in range(len(levels)-1):
        for a in range(na):
            n=(a+1)%na;l=j*na+a;f=j*na+n;u=(j+1)*na+a;un=(j+1)*na+n
            for t in [[l,u,f],[f,u,un]]:
                if dimension==2:t=t[::-1]
                reason=None;verts=proposed[t]
                if any(hits[i] is None for i in t):reason='missing_native_ray'
                elif cfg['side']=='right' and np.any(verts[:,0]>=0) or cfg['side']=='left' and np.any(verts[:,0]<=0):reason='subject_side_crossing'
                elif max(np.linalg.norm(verts[0]-verts[1]),np.linalg.norm(verts[1]-verts[2]),np.linalg.norm(verts[2]-verts[0]))>max_edge:reason='edge_over_30mm_component_jump'
                else:
                    normal=np.cross(verts[1]-verts[0],verts[2]-verts[0]);c=verts.mean(axis=0)
                    if np.linalg.norm(normal)<1e-8 or np.dot(normal,c-center_at(c[dimension]))<=0:reason='inward_or_degenerate'
                distances=[]
                if reason is None:
                    for p in weights@verts:
                        origin=center_at(p[dimension]);direction=p-origin;radius=np.linalg.norm(direction);direction/=radius
                        h=native.cast(origin,direction,cfg['limit'])
                        if h is None:reason='missing_interior_native_ray';break
                        distance=radius-h[1]['distance'];distances.append(distance)
                        if distance<.0005:reason='sampled_penetration_or_low_clearance';break
                intersections=body_surfaces.intersections(verts) if reason is None else []
                if intersections:reason='proper_native_triangle_intersection'
                if reason:rejected.append({'level':j,'angle':a,'triangle':t,'reason':reason,**({'intersectingSourceKeys':intersections} if intersections else {})})
                else:kept.append(t);clearances.extend(distances)
    kept=np.array(kept,dtype='<u4')
    if not len(kept):
        (E/'failed-region.json').write_text(json.dumps({'id':cfg['id'],'rejected':dict(Counter(t['reason'] for t in rejected)),'missing':missing},indent=2)+'\n')
        raise ValueError('No executable surface for '+cfg['id'])
    group_entries=[]
    borders=[0]+[int(np.flatnonzero(levels==cut)[0]) for cut in cfg['cuts']]+[len(levels)-1]
    for part,(lo,hi) in enumerate(zip(borders,borders[1:])):
        indices=kept[(kept.min(axis=1)>=lo*na)&(kept.max(axis=1)<(hi+1)*na)]-lo*na
        pos=proposed[lo*na:(hi+1)*na];basis=ref[lo*na:(hi+1)*na].astype('<f4')
        # Unreferenced missing/crossing vertices do not belong to emitted topology.
        used=np.unique(indices);indices=np.searchsorted(used,indices).astype('<u4');pos=pos[used];basis=basis[used]
        assert len(pos)<65536 and len(indices)>0
        ident=f"{cfg['id']}-{part}";file=f'{ident}.bin'
        content=pos.tobytes()+basis.tobytes()+indices.astype('<u2').tobytes()
        (OUT/file).write_bytes(content)
        h=sha(pos.tobytes()+indices.tobytes());rh=sha(basis.tobytes()+indices.tobytes())
        bounds=[pos.min(axis=0).tolist(),pos.max(axis=0).tolist()]
        entry={'id':ident,'family':cfg.get('family','trunk' if cfg['id']=='trunk' else cfg['id'].split('-')[0]), 'label':cfg['labels'][part],
          'side':cfg['side'],'revision':'education-envelope-r1','topologySha256':h,'referenceHash':rh,
          'file':file,'sha256':sha(content),'bytes':len(content),'vertices':len(pos),'triangles':len(indices),
          'bounds':bounds,'levelsRange':[float(levels[lo]),float(levels[hi])],'clearanceMetres':clearance,
          'geometryBufferBytes':len(pos)*24+len(indices)*6,
          'sourceKeys':sorted(set(hits[lo*na+int(i)]['sourceKey'] for i in used if hits[lo*na+int(i)])),
          'axisSourceKeys':cfg['axis'],'sourceGridOffset':lo*na,'landmarkBasis':cfg.get('landmarkBasis','native bone section bounds; no cun or acupoint coordinates'),'axisDimension':dimension,'maxEdgeMetres':max_edge,'component':cfg.get('component',cfg['id'])}
        entries.append(entry);group_entries.append(entry);mapping[ident]=(used+lo*na).tolist()
    for part,(a,b) in enumerate(zip(group_entries,group_entries[1:])):
        cut=borders[part+1];ring=proposed[cut*na:(cut+1)*na]
        seams.append({'a':a['id'],'b':b['id'],'y':float(levels[cut]),'sharedGridRingSha256':sha(ring.tobytes()),'sharedPositionsMaxDeltaMetres':0,'caps':False})
    all_hits[cfg['id']]=hits
    audits.append({'id':cfg['id'],'side':cfg['side'],'sourceKeys':cfg['sources'],'axis':axis_records,'levels':levels.tolist(),'angles':na,'radiusLimitMetres':cfg['limit'],'axisDimension':dimension,'clearanceMetres':clearance,'maxEdgeMetres':max_edge,
      'missingNativeRays':missing,'nearestFallbackCount':0,'proposedTriangles':2*(len(levels)-1)*na,'emittedTriangles':len(kept),
      'rejectedTriangles':rejected,'sampledClearanceMinMetres':float(min(clearances)),'sampledClearanceMaxMetres':float(max(clearances)),
      'surfaceSamplesPerFace':len(weights),'sourceContributions':dict(Counter(h['sourceKey'] for h in hits if h))})
    print(cfg['id'],len(points),len(kept),'missing',len(missing),'rejected',dict(Counter(t['reason'] for t in rejected)),flush=True)

new_entries=entries.copy()
if previous:
    replaced={cfg.get('family',cfg['id'].split('-')[0]) for cfg in configs}
    entries=[c for c in previous['chunks'] if c['family'] not in replaced]+entries
manifest={'schemaVersion':1,'revision':'education-envelope-r1','usage':'development_review_only','kind':'authored_teaching_surface','precision':'coarse_not_skin',
  'datasetRevision':dataset['revision'],'frameId':dataset['frameContract']['targetFrameId'],'unit':'m','poseId':dataset['frameContract']['staticReferencePose']['id'],
  'rights':rights,'acceptedAcupoints':0,'chunks':entries,'totalBytes':sum(v['bytes'] for v in entries),
  'totalTriangles':sum(v['triangles'] for v in entries),'totalGeometryBufferBytes':sum(v['geometryBufferBytes'] for v in entries),
  'unsupportedRegions':config_data['unsupportedRegions'] if config_data else ['head','neck_above_T1','hand','foot','perineum','oral_mucosa','deforming_pose'],
  'openBoundaries':'trunk neck/pelvis, shoulder/torso and hip/torso junctions, wrists/ankles; no cross-component bridges',
  'inspectionGrade':'native-envelope geometry only; gaps and removed faces are in development evidence; not skin accuracy'}
if config_data and config_data.get('accessFile'):
    access_path=R/config_data['accessFile'];inputs[config_data['accessFile']]=sha(access_path.read_bytes())
    manifest['accessManifest']={'file':access_path.name,'sha256':sha(access_path.read_bytes()),'bytes':access_path.stat().st_size,'usage':'development_review_only'}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':'))+'\n')
meta={'method':'AT2 exact native triangle outermost ray hit + declared per-region visual clearance; segmented binary topology; no nearest fallback or mirror',
  'reader':str(reader_path.relative_to(R))+'::world','readerSha256':sha(reader_path.read_bytes()),'AT2ValidationSha256':sha((R/'work/evidence/AT2/validation.json').read_bytes()),
  'sourceInputs':inputs,'unitInputs':{str((cache/'units'/f'{k}.json').relative_to(R)):sha((cache/'units'/f'{k}.json').read_bytes()) for k in meshes if k.startswith('ZA-c7010a9-')},
  'probeGeometryInputs':config_data.get('probeInputs',[]) if config_data else [],'newChunkIds':[c['id'] for c in new_entries],
  'geometry':{k:{'side':rows[k]['side'],'name':rows[k]['names']['en'],'bounds':[v.min(axis=0).tolist(),v.max(axis=0).tolist()],'matrixAppliedOnce':True,
    'nativeDisplayEligibilityPreserved':rows[k]['localDisplayEligible'],'nativeHoldReasons':rows[k]['hardHoldReasons'],
    'readPurpose':'read-only technical surface basis, not a change to native anatomy visibility'} for k,(v,t) in meshes.items()},
  'groups':audits,'chunkSourceGridMappings':mapping,'seams':seams,'manifestSha256':sha((OUT/'manifest.json').read_bytes()),'rights':rights,
  'collisionSourceKeys':collision_keys,'collisionNativeTriangles':len(body_surfaces.triangles),
  'sourceDownloads':0,'sourceWrites':0,'pointsAuthored':0,'anatomicalSkinAccuracy':'unresolved','nativeFaceInteriorExhaustiveness':'seven radial samples/face plus proper triangle intersections; tangency and closed-volume containment remain outside this check'}
(E/'generation.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
(E/'native-hits.json').write_text(json.dumps(all_hits,ensure_ascii=False,separators=(',',':'))+'\n')
print('chunks',len(entries),'bytes',manifest['totalBytes'],'triangles',manifest['totalTriangles'],flush=True)
