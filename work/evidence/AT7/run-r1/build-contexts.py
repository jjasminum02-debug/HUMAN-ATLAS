from pathlib import Path
import json,hashlib,ast,struct
import numpy as np
R=Path(__file__).resolve().parents[4]; E=Path(__file__).parent; A=R/'work/evidence/acupoint-AC1'; cache=R/'atlas-data/source-cache/datasets/za'
read=lambda p:json.loads(p.read_text()); sha=lambda b:hashlib.sha256(b).hexdigest();inputs={};meshes={}
fn=next(n for n in ast.parse((A/'build_carrier.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='world');exec(compile(ast.Module(body=[fn],type_ignores=[]),'AC1-reader','exec'),globals())
rows={r['sourceKey']:r for r in read(A/'runtime-integration.json')['objects']}
source=read(R/'work/evidence/AT6/resume-r1/bilateral-rules-r9.json'); ledger=read(R/'work/evidence/AT6/resume-r1/bilateral-compiler-r8/ledger.json'); contexts=[];audits=[]
regions=[('chest',['LU1','LU2'],[.085,.075,.080],['Clavicle','Clavicular head of pectoralis major muscle','Clavicular part of deltoid muscle','Scapula']),('upper-arm',['LU3','LU4'],[.052,.072,.048],['Long head of biceps brachii','Clavicular part of deltoid muscle','Humerus']),('elbow',['LU5'],[.054,.070,.050],['Long head of biceps brachii','Brachioradialis muscle','Humerus','Radius','Ulna']),('forearm',['LU6','LU7','LU8'],[.040,.050,.040],['Brachioradialis muscle','Abductor pollicis longus','Extensor pollicis brevis','Radius','Ulna']),('wrist',['LU9'],[.033,.040,.030],['Abductor pollicis longus','Abductor pollicis brevis','Radius','Scaphoid bone','First metacarpal bone']),('thenar',['LU10'],[.025,.030,.024],['Abductor pollicis brevis','First metacarpal bone','Proximal phalanx of first finger of hand']),('thumb-tip',['LU11'],[.014,.020,.013],['Distal phalanx of first finger of hand','Proximal phalanx of first finger of hand'])]
for u in source['units']:
 instance=ledger['units'][u['id']]['instance']; c=source['inputs']['carriers'][instance['carrierId']]; positions=np.array(c['positions']).reshape(-1,3);indices=np.array(c['indices']).reshape(-1,3);tri=positions[indices[instance['triangle']]];point=np.array(instance['barycentric'])@tri
 region,_,half,names=next(r for r in regions if u['code'] in r[1]); lo,hi=point-np.array(half),point+np.array(half);parts=[]
 for name in names:
  keys=[k for k,r in rows.items() if r['side']==u['side'] and r['names']['en']==name];assert len(keys)==1,(name,u['side']);key=keys[0];v,t=world(key);inside=((v>=lo)&(v<=hi)).all(axis=1);ids=np.flatnonzero(inside[t].all(axis=1))
  if not len(ids):continue
  verts=v[np.unique(t[ids])];bounds=[verts.min(axis=0).tolist(),verts.max(axis=0).tolist()];samples=v[t[ids[np.linspace(0,len(ids)-1,min(3,len(ids))).astype(int)]]].mean(axis=1).tolist();unit=read(cache/'units'/f'{key}.json')
  parts.append({'sourceKey':key,'name':name,'bounds':bounds,'samplePositions':samples,'sourceSha256':unit['lods']['detail']['sha256'],'role':'bone' if name in ['Clavicle','Scapula','Humerus','Radius','Ulna','Scaphoid bone','First metacarpal bone'] or 'phalanx' in name else 'muscle_tendon'})
  audits.append({'point':u['id'],'sourceKey':key,'side':u['side'],'triangleIds':ids.tolist(),'bounds':bounds,'clipBounds':[lo.tolist(),hi.tolist()],'sourceMatrix':unit['matrix'],'fullBounds':[v.min(axis=0).tolist(),v.max(axis=0).tolist()]})
 if u['code']=='LU11':
  native=source['inputs']['native'][f'PROBE-nail-fold-{u["side"]}-3'];v=np.array(native['positions']).reshape(-1,3);t=np.array(native['indices']).reshape(-1,3);ids=np.flatnonzero(((v[t]>=lo)&(v[t]<=hi)).all(axis=(1,2)));verts=v[np.unique(t[ids])];parts.append({'sourceKey':native['id'],'name':'Native nail fold probe','bounds':[verts.min(axis=0).tolist(),verts.max(axis=0).tolist()],'samplePositions':[],'sourceSha256':native['topologySha256'],'role':'native_probe'})
 assert len(parts)>=2,(u['id'],parts)
 contexts.append({'code':u['code'],'side':u['side'],'point':point.tolist(),'placementBinding':{'carrierId':instance['carrierId'],'carrierHash':instance['carrierHash'],'triangle':instance['triangle'],'barycentric':instance['barycentric']},'region':region,'structures':parts,'preferredNormal':[-.22 if u['side']=='right' else .22,.04,1],'minimumSpan':float(max(np.ptp(np.concatenate([np.array(s['bounds']) for s in parts]),axis=0))),'mode':'point_and_structures','limitations':['Source-native local geometry, not observed skin; deep bone may be occluded by unchanged muscles.']})
product=R/'atlas-data/acupoints/observation';product.mkdir(exist_ok=True)
paths=[]
for u in source['units']:
 if u['rule']['kind'] not in ['B-cun','F-cun']:continue
 for segment in u['rule']['path']:
  c=source['inputs']['carriers'][segment.get('carrierId',u['carrierId'])];v=np.array(c['positions']).reshape(-1,3);t=np.array(c['indices']).reshape(-1,3);tri=v[t[segment['triangle']]];normal=np.cross(tri[1]-tri[0],tri[2]-tri[0]);normal/=np.linalg.norm(normal);a=np.array(segment['from'])@tri+normal*.001;b=np.array(segment['to'])@tri+normal*.001
  paths.append({'side':u['side'],'from':a.tolist(),'to':b.tolist()})
out={'schemaVersion':1,'teachingPaths':paths,**source['context'],'placementInputSha256':sha((R/'work/evidence/AT6/resume-r1/bilateral-rules-r9.json').read_bytes()),'contexts':contexts};(product/'lung-context-r1.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n')
cat=read(R/'atlas-data/acupoints/who-361-catalog.json');(product/'catalog-r1.json').write_text(json.dumps({'schemaVersion':1,'catalogSha256':sha((R/'atlas-data/acupoints/who-361-catalog.json').read_bytes()),'channels':[{'code':c['code'],'nameKo':c['nameKo'],'midline':c['lateralityRule']=='midline'} for c in cat['channels']],'concepts':[{'code':c['code'],'nameKo':c['nameKo'],'channel':c['channelCode']} for c in cat['concepts']]},ensure_ascii=False,separators=(',',':'))+'\n')
(E/'context-geometry-audit-r1.json').write_text(json.dumps({'sourceReadHashes':inputs,'parts':audits,'contexts':len(contexts),'onlyActualVerticesInsideLocalClip':True,'newGeometry':False},indent=2)+'\n');print('22 contexts, native local source parts',len(audits),'bytes', (product/'lung-context-r1.json').stat().st_size)
