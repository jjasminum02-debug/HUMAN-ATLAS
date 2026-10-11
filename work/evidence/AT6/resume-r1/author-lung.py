"""AI-authored source-bound structural teaching indicators. No AC2 position input."""
from pathlib import Path
import json,hashlib,ast,struct
import numpy as np
R=Path(__file__).resolve().parents[4];E=Path(__file__).parent;A=R/'work/evidence/acupoint-AC1';cache=R/'atlas-data/source-cache/datasets/za'
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest();inputs={};meshes={}
rows={r['sourceKey']:r for r in read(A/'runtime-integration.json')['objects']}
fn=next(n for n in ast.parse((A/'build_carrier.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='world');exec(compile(ast.Module(body=[fn],type_ignores=[]),'AC1-reader','exec'),globals())
def find(name,side):
 ks=[k for k,r in rows.items() if r['side']==side and r['names']['en']==name];assert len(ks)==1,(name,side);return ks[0]
def manifest_path(v):
 p=R/f'atlas-data/acupoints/carriers/{v}/manifest.json'
 return p if p.exists() else E/f'carrier-candidates/{v}/manifest.json'
manifests={v:read(manifest_path(v)) for v in ['education-r1','lung-local-r1','lung-local-r2']};m=manifests['education-r1'];context={k:m[k] for k in ['datasetRevision','frameId','unit','poseId']};rights=m['rights']
carriers={};native={};annotations=[];evidence=[];units=[]
def carrier(ident):
 if ident in carriers:return carriers[ident]
 ver,c=next((ver,c) for ver,m in manifests.items() for c in m['chunks'] if c['id']==ident)
 b=(manifest_path(ver).parent/c['file']).read_bytes();assert sha(b)==c['sha256']
 v=np.frombuffer(b,dtype='<f4',count=c['vertices']*3).reshape(-1,3);t=np.frombuffer(b,dtype='<u2',offset=c['vertices']*24).reshape(-1,3).astype('<u4')
 carriers[ident]={'id':ident,'revision':c['revision'],'topologySha256':c['topologySha256'],**context,'side':c['side'],'kind':m['kind'],'precision':m['precision'],'rights':rights,'positions':v.ravel().tolist(),'indices':t.ravel().tolist()}
 return carriers[ident]
def geometry(k,side):
 if k not in native:
  v,t=world(k);native[k]={'id':k,'revision':'native-world-frozen-r1','topologySha256':sha(v.astype('<f4').tobytes()+t.astype('<u4').tobytes()),**context,'side':side,'positions':v.ravel().tolist(),'indices':t.ravel().tolist(),'rights':rights}
 return native[k]
def arrays(g):return np.array(g['positions']).reshape(-1,3),np.array(g['indices']).reshape(-1,3)
def address(g,p,direction):
 """Registration only: ray from known semantic section; never establishes anatomy identity."""
 v,t=arrays(g);tri=v[t];o=np.array(p)-np.array(direction)*.10;d=np.array(direction);e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];pv=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,pv);inv=np.divide(1,det,out=np.zeros_like(det),where=np.abs(det)>1e-12);tv=o-tri[:,0];u=np.einsum('ij,ij->i',tv,pv)*inv;q=np.cross(tv,e1);vv=q@d*inv;dist=np.einsum('ij,ij->i',e2,q)*inv
 ids=np.flatnonzero((np.abs(det)>1e-12)&(u>=-1e-8)&(vv>=-1e-8)&(u+vv<=1+1e-8)&(dist>0)&(dist<.2))
 if not len(ids):raise ValueError(('No supported triangle',g['id'],np.array(p).tolist(),direction))
 j=ids[np.argmax(dist[ids])];b=np.maximum([1-u[j]-vv[j],u[j],vv[j]],0);b/=sum(b);return {'triangle':int(j),'barycentric':b.tolist()}
def at(g,a):
 v,t=arrays(g);return np.array(a['barycentric'])@v[t[a['triangle']]]
def anchor(g,a,side):return {'carrierId':g['id'],'carrierRevision':g['revision'],'carrierHash':g['topologySha256'],'frameId':g['frameId'],'unit':'m','poseId':g['poseId'],'side':side,**a}
def note(code,side,c,purpose,text,source=None,**extra):
 ident=f'{code}-{side}-{purpose}-{len(evidence)}';source=source or {'id':'ZA-native-AI-annotation-r1','title':'Source-addressed AI structural teaching indicator','edition':'2026-10-12-r1','locator':'work/evidence/AT6/resume-r1/annotations.json'}
 evidence.append({'id':ident,'purpose':purpose,'source':source,'originalText':text,'author':'ai','status':'confirmed','method':'anatomical_correspondence','side':side,'frameId':c['frameId'],'poseId':c['poseId'],'carrierHash':c['topologySha256'],'pointCode':code,'rights':{'localObservation':'supported','publicRedistribution':'held'},**extra});return ident
concepts=read(R/'work/evidence/acupoint-AC2/point-concepts.json');basic={x['code']:x for x in concepts}
def landmark(code,side,c,name,a,surface,anatomy,construction,limits):
 k=find(name,side);g=geometry(k,side);ident=f'{code}-{side}-{len(annotations)}'
 obs={'sourceKey':k,'sourceName':name,'side':side,'native':anchor(g,a,side),'nativeWorld':at(g,a).tolist(),'surface':surface,'surfaceWorld':at(c,surface).tolist(),'observed':'Actual frozen native mesh address; NOT observed skin crease','interpretation':{'kind':'educational_model_indicator','observedSkinLandmark':False,'construction':construction,'limitations':limits},'relation':anatomy}
 annotations.append(obs)
 return {'id':ident,'anatomy':anatomy,'acquisition':'anatomical_annotation','side':side,'sourceKey':k,'native':obs['native'],'surface':surface,'evidenceId':note(code,side,c,'landmark_annotation',json.dumps(obs,ensure_ascii=False)),'role':'anatomical_landmark','modelIndicator':obs['interpretation']}
def unit(code,side,c,landmarks,rule,relation):
 src=basic[code]['standard'];rid=note(code,side,c,'location_relation',relation,src);sid=note(code,side,c,'surface_registration','Native structural features and AI model indicator correspond in the frozen pose. Ray is only registration; no claim of observed skin.',maxRegistrationGapMetres=.02)
 units.append({'id':f'{code}-{side}','scope':'real_input','code':code,'side':side,'revision':'AT6-native-indicator-r1','context':context,'carrierId':c['id'],'originalText':basic[code]['location']['text'],'originalSources':[src],'author':'ai','professorReview':'not_performed','landmarks':landmarks,'rule':rule,'relationEvidenceId':rid,'surfaceEvidenceId':sid})
# First milestone: LU9. Selected styloid/scaphoid facet addresses after axial and palmar mesh inspection.
# Radius facet 93 is the distal radial styloid; scaphoid facet 120 is its palmar-radial facet.
for side in ['right']:
 c=carrier('wrist-'+side+'-0');r=geometry(find('Radius',side),side);s=geometry(find('Scaphoid bone',side),side);apl=geometry(find('Abductor pollicis longus',side),side)
 ra={'triangle':93,'barycentric':[1/3]*3};sa={'triangle':120,'barycentric':[1/3]*3};aa={'triangle':260,'barycentric':[1/3]*3}
 p=(at(r,ra)+at(s,sa))/2;p[2]=at(s,sa)[2];surface=address(c,p,[0,0,-1])
 ls=[landmark('LU9',side,c,n,a,surface,anatomy,construction,['No wrist skin crease or pulsatile radial artery represented; static structural approximation.','Frozen model palm faces -Z (confirmed by actual palmar/dorsal screen). Transfer of flexed surface crease is an authored model correspondence, not observed skin.']) for n,a,anatomy,construction in [('Radius',ra,'Distal radial styloid bordering radiocarpal interval','Native distal styloid facet is observed; model interval uses independent scaphoid facet.'),('Scaphoid bone',sa,'Scaphoid palmar-radial facet distal to radial styloid','Native scaphoid facet observed; teaching location between radius and scaphoid, ulnar to APL.'),('Abductor pollicis longus',aa,'APL distal tendon radial to teaching interval','Native distal tendon inspected, separate from palmar interval; no radial artery position is claimed.')]]
 unit('LU9',side,c,ls,{'kind':'landmark','landmark':ls[1]['id']},'WHO p30 main structural relation: radiocarpal interval, palmar/anterolateral wrist, ulnar to APL. AI model interval between independently addressed styloid/scaphoid facets; artery/crease note not claimed as observed. Educational structural placement only.')
(E/'first-rules-r2.json').write_text(json.dumps({'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}},ensure_ascii=False,separators=(',',':'))+'\n')
(E/'annotations-first-r2.json').write_text(json.dumps(annotations,ensure_ascii=False,indent=2)+'\n');print([(u['id'],at(carriers[u['carrierId']],u['landmarks'][0]['surface']).tolist()) for u in units])
