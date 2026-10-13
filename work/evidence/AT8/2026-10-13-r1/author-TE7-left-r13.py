from pathlib import Path
import shutil
E=Path(__file__).parent
exec((E/'author-corrections-r3.py').read_text().split("\nfor side in ['right','left']:")[0])
d=read(E/'rules-r12.json');units=d['units'];carriers=d['inputs']['carriers'];native=d['inputs']['native'];evidence=d['inputs']['evidence'];annotations=read(E/'annotations-r11.json');failures=read(E/'author-failures-r11.json');audit=[]
# Explicit semantic dorsal check rejects the saved wrong palmar registration; it is not a camera-only problem.
for u in units:
 if u['code']=='TE7':next(e for e in evidence if e['id']==u['surfaceEvidenceId'])['surfaceOrientation']={'direction':[0,0,-1],'minimumDot':.3}
(E/'rules-r12-orientation-rejected.json').write_text(json.dumps({'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}},ensure_ascii=False,separators=(',',':'))+'\n')
u=next(u for u in units if u['id']=='TE7-left');ulref=next(r for r in u['observedReferences'] if r['sourceKey']==find('Ulna','left'));ulna=native[ulref['sourceKey']];ulp=at(ulna,ulref['native']);y=ulp[1];x=ulp[0]+.003
# Two exact semantic planes intersect original left antebrachial fascia, selecting only posterior native intersections.
g=geometry('Antebrachial fascia','left');v,t=arrays(g);candidates=[]
for j,tri in enumerate(v[t]):
 hits=[]
 for a,b in [(0,1),(1,2),(2,0)]:
  if (tri[a,1]<=y)!=(tri[b,1]<=y):
   f=(y-tri[a,1])/(tri[b,1]-tri[a,1]);w=np.zeros(3);w[a]=1-f;w[b]=f;hits.append(w)
 if len(hits)==2:
  p,q=hits[0]@tri,hits[1]@tri
  if abs(q[0]-p[0])<1e-10:continue
  f=(x-p[0])/(q[0]-p[0])
  if 0<=f<=1:w=hits[0]*(1-f)+hits[1]*f;point=w@tri;candidates.append((point,j,w))
assert candidates,'No original fascia support at native radial-ulnar3B plane';p,j,w=min(candidates,key=lambda c:c[0][2]);assert p[2]<-.01,'No posterior native fascia at fixed semantic planes'
tri=v[t[j]].astype('<f4');pos=(tri+np.array([0,0,-.006])).astype('<f4');idx=np.array([[0,1,2]],dtype='<u4');normal=np.cross(pos[1]-pos[0],pos[2]-pos[0]);sfw=w.copy()
if normal[2]>0:idx=np.array([[0,2,1]],dtype='<u4');sfw=w[[0,2,1]]
cid='ulnar-posterior-indicator-left-0';c={'id':cid,'revision':'AT8-native-posterior-r13','topologySha256':sha(pos.tobytes()+idx.tobytes()),**context,'side':'left','kind':'authored_teaching_surface','precision':'coarse_not_skin','rights':rights,'positions':pos.ravel().tolist(),'indices':idx.ravel().tolist()};carriers[cid]=c;sf={'triangle':0,'barycentric':sfw.tolist()};a={'triangle':j,'barycentric':w.tolist()};l=lm('TE7','left',c,g,a,sf,'Native posterior fascia just radial to ulna at independently calibrated3B plane','Original left ulna radial border determines X+3mm structural correspondence; verified TE6 anatomical3B longitudinal plane determines Y. Exact original posterior fascia intersection determines Z;6mm teaching-envelope offset, not actual skin or precision. No left/right mirror.');u['landmarks']=[l];u['rule']={'kind':'landmark','landmark':l['id']};u['carrierId']=cid;u['revision']='AT8-posterior-correction-r13';u['relationEvidenceId']=note('TE7','left',c,'location_relation',u['originalText']+' Original dorsal/posterior relation separately checked; saved palmar projection is rejected, not camera-adjusted.');u['surfaceEvidenceId']=note('TE7','left',c,'surface_registration','Original source fascia intersection of named anatomical planes, outward posterior envelope6mm; no external coordinate.',maxRegistrationGapMetres=.02,surfaceOrientation={'direction':[0,0,-1],'minimumDot':.3})
for ref in u['observedReferences']:ref['evidenceId']=note('TE7','left',c,'landmark_annotation',json.dumps(ref,ensure_ascii=False))
OUT=R/'atlas-data/acupoints/carriers/upper-yang-compact-AT8-r13';shutil.copytree(R/'atlas-data/acupoints/carriers/upper-yang-compact-AT8-r12',OUT);m=read(OUT/'manifest.json');content=pos.tobytes()+tri.tobytes()+idx.astype('<u2').tobytes();f=cid+'.bin';(OUT/f).write_bytes(content);template=dict(m['chunks'][0]);template.update({'id':cid,'family':'arm','label':'자뼈 노쪽의 등쪽 체표 지표','side':'left','revision':c['revision'],'file':f,'vertices':3,'triangles':1,'bytes':len(content),'geometryBufferBytes':len(content),'sha256':sha(content),'topologySha256':c['topologySha256'],'referenceHash':sha(tri.tobytes()+idx.tobytes()),'bounds':[pos.min(0).tolist(),pos.max(0).tolist()],'clearanceMetres':.006});m['chunks'].append(template);m['revision']='AT8-native-posterior-r13'
for k,n in [('totalBytes','bytes'),('totalTriangles','triangles'),('totalGeometryBufferBytes','geometryBufferBytes')]:m[k]=sum(c[n] for c in m['chunks'])
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');audit={'unit':'TE7-left','originalUlnaRadialAddress':ulref['native'],'native3B_y':y,'nativeRadial_x':ulp[0],'modelRadialSeparationMetres':.003,'nativeFasciaAddress':a,'nativeWorld':p.tolist(),'modelWorld':at(c,sf).tolist(),'sourceHash':g['topologySha256'],'offsetMetres':.006,'posteriorNotPalmar':True,'notPrecisionOrSkinClaim':True}
for name,data in [('rules-r13',{'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}}),('TE7-left-native-correction-r1',audit)]:
 (E/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
