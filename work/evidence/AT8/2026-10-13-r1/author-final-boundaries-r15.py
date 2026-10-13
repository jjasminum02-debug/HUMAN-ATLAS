from pathlib import Path
import shutil
E=Path(__file__).parent
exec((E/'author-source-boundaries-r14.py').read_text().split("\nfor side in ['right','left']:")[0])
d=read(E/'rules-r14.json');units=d['units'];carriers=d['inputs']['carriers'];native=d['inputs']['native'];evidence=d['inputs']['evidence'];annotations=read(E/'annotations-r11.json');failures=read(E/'author-failures-r14.json');native_audit=[];new_carriers=[]
extra=read(E/'evaluated-native-boundaries-r3.json')
for o in extra['objects']:
 if not o.get('triangles'):continue
 side='right' if o['name'].endswith('.r') else 'left';name=o['name'][:-2];k='PROBE-boundary-'+name.lower().replace(' ','-')+'-'+side;rows[k]={'sourceKey':k,'names':{'en':name},'side':side,'kind':'native_probe'};probe_mesh[k]=(np.array(o['positions']),np.array(o['indices'],dtype='<u4'));probe_meta[k]={'probeFile':'evaluated-native-boundaries-r3.json','probeFileHash':sha((E/'evaluated-native-boundaries-r3.json').read_bytes()),'object':o['name'],'originalBlendHash':extra['sourceSha256'],'matrixAppliedOnce':True,'frame':extra['frame'],'pose':extra['pose'],'unit':'m'}
# Exact original surface section at anatomy-defined longitudinal plane. Selection is registration only.
def plane_unit(code,side,name,y,refs,label,target=None,extreme=None):
 c=source_carrier(name,side);ng=geometry(name,side);candidates=section_candidates(ng,y,1);assert candidates,'Missing original region at anatomy-defined plane'
 if extreme is not None:p,a=(min if extreme=='posterior' else max)(candidates,key=lambda x:x[0][2])
 else:p,a=min(candidates,key=lambda x:np.linalg.norm(x[0]-np.array(target)))
 sf=dict(a);l=lm(code,side,c,ng,a,sf,'Original '+name+' at independently defined anatomical plane',label+' Exact section of evaluated source regional surface; nearby source registration never supplies location meaning.');make(code,side,c,[l],{'kind':'landmark','landmark':l['id']},label);units[-1]['observedReferences']=[reference(code,side,c,n,a,anatomy) for n,a,anatomy in refs];native_audit.append({'code':code,'side':side,'nativePart':name,'nativeAddress':l['native'],'nativeWorld':p.tolist(),'surfaceWorld':at(c,sf).tolist(),'planeY':y,'source':probe_meta[ng['id']],'construction':label,'precise':False})
for side in ['right','left']:
 sign=-1 if side=='right' else 1
 ph,a0,p0=facet('Philtrum',side,1,'min');_,a1,p1=facet('Philtrum',side,1,'max');y=(p0[1]+p1[1])/2;ag,aa,ap=facet('Major alar cartilage',side,0,'min' if side=='right' else 'max');target=[ap[0],y,p0[2]]
 replace('LI19',side,lambda:plane_unit('LI19',side,'Oral region',y,[('Philtrum',a0,'Original philtrum inferior boundary'),('Philtrum',a1,'Original philtrum superior boundary'),('Major alar cartilage',aa,'Original lateral alar contour')],'Original philtrum midpoint height below lateral alar/nostril contour; evaluated oral regional surface supports static model skin correspondence, not clinical precision.',target=target))
 ag,aTop,pTop=facet('Major alar cartilage',side,1,'max',mask=lambda c:c[:,0]*sign>abs(ap[0])*.7);_,aBottom,pBottom=facet('Major alar cartilage',side,1,'min',mask=lambda c:c[:,0]*sign>abs(ap[0])*.7);y=(pTop[1]+pBottom[1])/2;pts=section_candidates(ag,y,1);ala,aa=max(pts,key=lambda c:c[0][0]*sign)
 replace('LI20',side,lambda:plane_unit('LI20',side,'Nasolabial sulcus',y,[('Major alar cartilage',aa,'Native lateral alar-wing midpoint level')],'Source nasal alar-wing midpoint defines level; original evaluated nasolabial groove itself defines lateral surface. No fixed alar X copied onto absent groove.',target=ala))
 mg,ma,mp=facet('Mandible',None,1,'min',mask=lambda c:(c[:,0]*sign>.04)&(c[:,2]<.04));sc,sa,sp=slice_point('Sternocleidomastoid muscle',side,mp[1],2,'min')
 replace('TE16',side,lambda:plane_unit('TE16',side,'Sternocleidomastoid region',mp[1],[('Mandible',ma,'Native inferior/posterior body-ramus angle'),('Sternocleidomastoid muscle',sa,'Native posterior SCM boundary')],'Mandibular-angle plane on original posterior SCM regional boundary, rather than the old superior posterior ramus facet. Static educational fold correspondence.',extreme='posterior'))
 tr,tra,trp=facet('Tragus',side,1,'max');nt,nta,ntp=facet('Anterior notch of auricle',side,near=trp+np.array([0,.001,0]));md,mda,mdp=facet('Mandible',None,1,'max',mask=lambda c:c[:,0]*sign>.03);target=(ntp+mdp)/2;target[1]=ntp[1]
 replace('TE21',side,lambda:plane_unit('TE21',side,'Auricular region',ntp[1],[('Tragus',tra,'Actual superior tragus boundary'),('Anterior notch of auricle',nta,'Actual notch immediately superior to tragus'),('Mandible',mda,'Native ipsilateral mandibular condyle')],'Native superior-tragus/notch and mandibular-condyle interval at notch height; original anterior auricular regional surface. Closed-mouth model correspondence, no claimed open-mouth depression.',target=target))
 # Native medial helix attachment, not the outer rim, defines the auricular root.
 hel,hla,hlp=facet('Helix',side,0,'max' if side=='right' else 'min',mask=lambda c:c[:,1]>=trp[1]);ar,ara,arp=slice_point('Superficial temporal artery',side,hlp[1],2,'max');target=(hlp+arp)/2
 replace('TE22',side,lambda:plane_unit('TE22',side,'Temporal region',hlp[1],[('Helix',hla,'Native medial helix attachment at anterior auricular root'),('Superficial temporal artery',ara,'Native temporal arterial branch at root height')],'Source anterior auricular-root attachment and native temporal artery bound the model temporal interval. Anterior temporal boundary is an authored hairline proxy; source skin hairline/palpation remain unobserved.',target=target))
OUT=R/'atlas-data/acupoints/carriers/native-boundaries-AT8-r15';shutil.copytree(R/'atlas-data/acupoints/carriers/native-boundaries-AT8-r14',OUT);m=read(OUT/'manifest.json');m['revision']='AT8-evaluated-region-r15'
for c,ref,name in new_carriers:
 if any(k['id']==c['id'] for k in m['chunks']):continue
 v=np.array(c['positions'],dtype='<f4').reshape(-1,3);idx=np.array(c['indices'],dtype='<u4').reshape(-1,3);b=v.tobytes()+ref.tobytes()+idx.astype('<u2').tobytes();f=c['id']+'.bin';(OUT/f).write_bytes(b);m['chunks'].append({'id':c['id'],'family':'head','label':'원본 '+name+'의 교육용 정합 면','side':c['side'],'revision':c['revision'],'file':f,'vertices':len(v),'triangles':len(idx),'bytes':len(b),'geometryBufferBytes':len(b),'sha256':sha(b),'topologySha256':c['topologySha256'],'referenceHash':sha(ref.tobytes()+idx.tobytes()),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'clearanceMetres':.002,'sourceObject':name,'surfaceRole':'evaluated original regional part; not scanned skin'})
for k,n in [('totalBytes','bytes'),('totalTriangles','triangles'),('totalGeometryBufferBytes','geometryBufferBytes')]:m[k]=sum(c[n] for c in m['chunks'])
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
for name,data in [('rules-r15',{'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}}),('source-plane-annotations-r1',native_audit),('author-failures-r15',failures)]:
 (E/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
