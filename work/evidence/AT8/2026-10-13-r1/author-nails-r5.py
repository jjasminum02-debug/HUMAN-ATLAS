from pathlib import Path
E=Path(__file__).parent
exec((E/'author-corrections-r3.py').read_text().split("\nfor side in ['right','left']:")[0])
d=read(E/'rules-r4.json');units=d['units'];carriers=d['inputs']['carriers'];native=d['inputs']['native'];evidence=d['inputs']['evidence'];annotations=read(E/'annotations-r4.json');failures=read(E/'author-failures-r4.json')
config=read(R/'atlas-data/acupoints/carriers/education-special-inputs.json');lung=read(R/'work/evidence/AT6/resume-r1/bilateral-rules-r9.json');membranes=[];nailAudit=[]
for side in ['right','left']:
 sign=-1 if side=='right' else 1
 for code,component,finger,edge in [('LI1',2,'second','radial'),('TE1',4,'fourth','ulnar')]:
  try:
   spec=next(p for p in config['probeInputs'] if p['key']==f'PROBE-nail-fold-{side}-{component}');raw=(R/spec['path']).read_bytes();assert sha(raw)==spec['sha256'];o=next(o for o in json.loads(raw)['objects'] if o['name']==spec['object']);v=np.array(o['positions']);t=np.array(o['indices'],dtype='<u4');ids=spec['triangleIds'];localidx=np.unique(t[ids]);local=v[localidx]
   ng,base,bp=facet(f'Distal phalanx of {finger} finger of hand',side,1,'max');_,tip,tp=facet(f'Distal phalanx of {finger} finger of hand',side,1,'min');prox=bp-tp;prox/=np.linalg.norm(prox);radial=np.array([sign,0,0]);radial-=prox*np.dot(radial,prox);radial/=np.linalg.norm(radial);outward=radial if edge=='radial' else -radial
   # Address actual proximal edge of nail-fold component, then its named radial/ulnar endpoint.
   scores=local@prox;proximal=localidx[scores>=scores.max()-.0015];cornerVertex=int(proximal[np.argmax(v[proximal]@outward)]);j=int(next(i for i in ids if cornerVertex in t[i]));w=np.zeros(3);w[list(t[j]).index(cornerVertex)]=1;a={'triangle':j,'barycentric':w.tolist()};corner=v[cornerVertex]
   key=spec['key'];gn={'id':key,'revision':'native-world-frozen-r1','topologySha256':sha(v.astype('<f4').tobytes()+t.astype('<u4').tobytes()),**context,'side':side,'rights':rights,'positions':v.ravel().tolist(),'indices':t.ravel().tolist()};native[key]=gn
   # Local membrane follows the actual phalangeal proximal/radial directions at the observed corner.
   normal=np.cross(prox,outward);normal/=np.linalg.norm(normal)
   if normal[2]>0:normal=-normal
   direction=prox+(outward if code=='LI1' else np.zeros(3));direction/=np.linalg.norm(direction);width=np.cross(normal,direction);width/=np.linalg.norm(width);p0=corner+normal*.0007;verts=np.array([p0-width*.001,p0+width*.001,p0+direction*.004+width*.001,p0+direction*.004-width*.001],dtype='<f4');tri=np.array([[0,1,3],[1,2,3]],dtype='<u4')
   cid=code.lower()+'-nail-'+side+'-0';c={'id':cid,'revision':'AT8-nail-indicator-r1','topologySha256':sha(verts.tobytes()+tri.tobytes()),**context,'side':side,'kind':'authored_teaching_surface','precision':'coarse_not_skin','rights':rights,'positions':verts.ravel().tolist(),'indices':tri.ravel().tolist()};carriers[cid]=c
   sf={'triangle':0,'barycentric':[.5,.5,0]};end={'triangle':1,'barycentric':[0,.5,.5]};l0=lm(code,side,c,gn,a,sf,'Native proximal '+edge+' nail-base corner','Actual source fold component matched to '+finger+' distal phalanx; proximal edge plus '+edge+' endpoint independently addressed. Not nail bounds converted to body point.');l1=lm(code,side,c,ng,base,end,'Native distal phalangeal base directs proximal path','Actual distal-phalangeal tip/base axis directs local4mm membrane; not a fixed millimetre acupuncture location.')
   old=next(u for u in lung['units'] if u['code']=='LU11' and u['side']==side);ls=[l0,l1]
   for lold in old['landmarks'][2:4]:
    ll=json.loads(json.dumps(lold));cc=lung['inputs']['carriers'][ll['surface'].get('carrierId',old['carrierId'])];carriers[cc['id']]=cc;native[ll['sourceKey']]=lung['inputs']['native'][ll['sourceKey']];ll['surface']['carrierId']=cc['id'];ll['id']=code+'-'+side+'-cal-'+ll['id'];ll['evidenceId']=note(code,side,c,'landmark_annotation',json.dumps({'source':lold,'context':'AT6 independently validated thumb IP caliper retained; transported calibration only, not thumb location copied'}));ls.append(ll)
   widthcal=np.linalg.norm(at(carriers[ls[2]['surface']['carrierId']],ls[2]['surface'])-at(carriers[ls[3]['surface']['carrierId']],ls[3]['surface']));assert widthcal*.1<.004
   ev=note(code,side,c,'proportion','WHO p13 thumb IP width1 F-cun; point at0.1 F-cun from independently observed '+edge+' nail-base corner. Thumb calibration transferred to same subject; no external point coordinates.',measurement={'kind':'F-cun','value':1})
   make(code,side,c,ls,{'kind':'F-cun','from':l0['id'],'directionTo':l1['id'],'value':.1,'calibration':{'from':ls[2]['id'],'to':ls[3]['id'],'cun':1},'path':[{'triangle':0,'from':[.5,.5,0],'to':[0,.5,.5]},{'triangle':1,'from':[.5,0,.5],'to':[0,.5,.5]}],'evidenceId':ev},'Original nail probe and actual subject thumb-IP calibration reused. LI1 advances proximal/radial; TE1 proximal at ulnar base corner; tiny AI membrane is not observed skin.')
   nailAudit.append({'code':code,'side':side,'component':component,'nativeCorner':corner.tolist(),'nativeCornerAddress':a,'sourceProbeSha256':spec['sha256'],'proximalAxis':prox.tolist(),'outward':outward.tolist(),'modelStart':at(c,sf).tolist(),'F_cun':widthcal,'carrier':cid,'noMirror':True});membranes.append((c,corner));failures=[f for f in failures if not (f['code']==code and f['side']==side)]
  except Exception as ex:failures.append({'code':code,'side':side,'attempt':'Existing full native nail fold / independently matched finger / AT6 subject thumb-IP caliper / local membrane','error':str(ex),'neededInput':'See source-addressed nail audit; no nail coordinate promoted after failure.'})
# Versioned encoded registration shares the existing carrier decoder, including immutable native reference array.
OUT=R/'atlas-data/acupoints/carriers/upper-yang-nails-AT8-r1';OUT.mkdir(exist_ok=False);m=json.loads(json.dumps(manifests['lung-AT6-r2']));m['id']='upper-yang-nails-AT8-r1';m['revision']='AT8-nail-indicator-r1';m['chunks']=[]
for c,corner in membranes:
 v=np.array(c['positions'],dtype='<f4').reshape(-1,3);t=np.array(c['indices'],dtype='<u2').reshape(-1,3);b=v.tobytes()+np.tile(corner,(len(v),1)).astype('<f4').tobytes()+t.tobytes();fn=c['id']+'.bin';(OUT/fn).write_bytes(b);template=json.loads(json.dumps(manifests['lung-AT6-r2']['chunks'][0]));template.update({'id':c['id'],'revision':c['revision'],'file':fn,'side':c['side'],'family':'hand','vertices':len(v),'triangles':len(t),'bytes':len(b),'sha256':sha(b),'topologySha256':c['topologySha256'],'bounds':[v.min(0).tolist(),v.max(0).tolist()]});m['chunks'].append(template)
# Remove aggregate claims from donor manifest; compute only new emitted arrays and keep explicit source metadata.
m['kind']='authored_teaching_surface';m['precision']='coarse_not_skin';m['rights']=rights;m['cost']={'bytes':sum(c['bytes'] for c in m['chunks']),'triangles':sum(c['triangles'] for c in m['chunks'])};m['derivation']='AT6 local membrane path reused; actual index/ring nail fold corners and phalangeal directions; not skin scan or precise points.'
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
for name,data in [('rules-r5',{'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}}),('annotations-r5',annotations),('author-failures-r5',failures),('nail-audit-r1',nailAudit)]:
 (E/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
print('native nail units',len(nailAudit),'all units',len(units))
