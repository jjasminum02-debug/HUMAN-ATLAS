"""Explicit named native boundary-region annotations; no external acupoint coordinates.
Uses evaluated frame0 probe and existing compiler/region surfaces, not raw inventory names as geometry evidence.
"""
from pathlib import Path
import shutil
E=Path(__file__).parent
exec((E/'author-corrections-r3.py').read_text().split("\nfor side in ['right','left']:")[0])
d=read(E/'rules-r13.json');units=d['units'];carriers=d['inputs']['carriers'];native=d['inputs']['native'];evidence=d['inputs']['evidence'];annotations=read(E/'annotations-r11.json');failures=read(E/'author-failures-r11.json');probe_mesh={};probe_meta={};baseworld=world;native_audit=[];new_carriers=[]
for file in ['evaluated-native-boundaries-r1.json','evaluated-native-boundaries-r2.json']:
 doc=read(E/file);assert doc['sourceSha256']=='9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd' and doc['unit']=='m' and doc['pose']==context['poseId']
 for o in doc['objects']:
  if not o.get('triangles'):continue
  side='right' if o['name'].endswith('.r') else 'left';name=o['name'][:-2];k='PROBE-boundary-'+name.lower().replace(' ','-')+'-'+side;rows[k]={'sourceKey':k,'names':{'en':name},'side':side,'kind':'native_probe'};probe_mesh[k]=(np.array(o['positions']),np.array(o['indices'],dtype='<u4'));probe_meta[k]={'probeFile':file,'probeFileHash':sha((E/file).read_bytes()),'object':o['name'],'originalBlendHash':doc['sourceSha256'],'matrixAppliedOnce':True,'frame':doc['frame'],'pose':doc['pose'],'unit':'m'}
def world(k):return probe_mesh[k] if k in probe_mesh else baseworld(k)
def source_carrier(name,side):
 ng=geometry(name,side);cid='native-'+name.lower().replace(' ','-')+'-'+side+'-0'
 if cid in carriers:return carriers[cid]
 v,t=arrays(ng);direction=np.array([-1 if side=='right' else 1,0,0]) if 'auricular' in name.lower() else np.array([0,0,1]);clear=.002;p=(v+direction*clear).astype('<f4');tt=t.astype('<u4');c={'id':cid,'revision':'AT8-evaluated-region-r14','topologySha256':sha(p.tobytes()+tt.tobytes()),**context,'side':side,'kind':'authored_teaching_surface','precision':'coarse_not_skin','rights':rights,'positions':p.ravel().tolist(),'indices':tt.ravel().tolist()};carriers[cid]=c;new_carriers.append((c,v.astype('<f4'),name));return c
def region_surface(code,side,name,p,direction,refs,label):
 c=source_carrier(name,side);surface=address(c,p,direction);ng=geometry(name,side);ngv,ngt=arrays(ng)
 # Same actual source facet correspondence. Offset is2mm; all source barycentrics remain explicit.
 na={'triangle':surface['triangle'],'barycentric':surface['barycentric']};l=lm(code,side,c,ng,na,surface,'Original evaluated '+name+' region at '+label,label+' Original regional surface is an anatomical model part, not a skin scan or precise patient fold.');make(code,side,c,[l],{'kind':'landmark','landmark':l['id']},label);units[-1]['observedReferences']=[reference(code,side,c,n,a,anatomy) for n,a,anatomy in refs];prepared[side,code]=(c,surface,[l]);native_audit.append({'code':code,'side':side,'nativePart':name,'nativeAddress':l['native'],'nativeWorld':at(ng,na).tolist(),'surfaceWorld':at(c,surface).tolist(),'source':probe_meta[ng['id']],'construction':label,'precise':False})
def section_candidates(c,value,axis):
 v,t=arrays(c);out=[]
 for i,tri in enumerate(v[t]):
  for a,b in [(0,1),(1,2),(2,0)]:
   if (tri[a,axis]<=value)!=(tri[b,axis]<=value):
    f=(value-tri[a,axis])/(tri[b,axis]-tri[a,axis]);w=np.zeros(3);w[a]=1-f;w[b]=f;out.append((w@tri,{'triangle':i,'barycentric':w.tolist()}))
 return out
for side in ['right','left']:
 sign=-1 if side=='right' else 1;lat=[sign,0,0]
 # Directly inspected source philtrum endpoints now replace the earlier inferred lip/cartilage midpoint.
 phi,pa,pp=facet('Philtrum',side,1,'min');_,pb,pbpos=facet('Philtrum',side,1,'max');y=(pp[1]+pbpos[1])/2
 ala,aa,ap=facet('Major alar cartilage',side,0,'min' if side=='right' else 'max');target=np.array([ap[0],y,pp[2]])
 replace('LI19',side,lambda:region_surface('LI19',side,'Nasolabial sulcus',target,[0,0,1],[('Philtrum',pa,'Original philtrum inferior endpoint'),('Philtrum',pb,'Original philtrum superior endpoint'),('Major alar cartilage',aa,'Actual lateral alar cartilaginous border')],'Source philtrum vertical midpoint, below native lateral nostril/alar boundary. Original local facial region provides model correspondence; original nostril aperture/fold precision not claimed.'))
 # Lateral alar wing midpoint, excluding medial columellar part by actual lateral wing geometry.
 ag,aTop,pTop=facet('Major alar cartilage',side,1,'max',mask=lambda c:c[:,0]*sign>abs(ap[0])*.7);_,aBottom,pBottom=facet('Major alar cartilage',side,1,'min',mask=lambda c:c[:,0]*sign>abs(ap[0])*.7);alY=(pTop[1]+pBottom[1])/2;points=section_candidates(ag,alY,1);pAla,aAla=max(points,key=lambda x:x[0][0]*sign)
 replace('LI20',side,lambda:region_surface('LI20',side,'Nasolabial sulcus',pAla,[0,0,1],[('Major alar cartilage',aAla,'Native lateral alar wing midpoint at original source contour')],'At native lateral alar wing midpoint level on original evaluated nasolabial sulcus part. This is source regional anatomy in static pose, not patient skin or exact groove.'))
 # Correct mandibular angle is the inferior/posterior body-ramus junction, not the superior posterior ramus extreme.
 mg,ma,mp=facet('Mandible',None,1,'min',mask=lambda c:(c[:,0]*sign>.04)&(c[:,2]<.04));sc,sa,sp=slice_point('Sternocleidomastoid muscle',side,mp[1],2,'min')
 replace('TE16',side,lambda:region_surface('TE16',side,'Sternocleidomastoid region',sp,[sign,0,-.2],[('Mandible',ma,'Native inferior posterior mandibular body-ramus angle'),('Sternocleidomastoid muscle',sa,'Actual posterior SCM at corrected mandibular-angle plane')],'Inferior/posterior mandibular angle source facet sets level; posterior SCM border independently read. Previous ramus-height attempt preserved as failed; no whole-neck bounds ratio.'))
 # Source hand-dorsum distal boundary in the gap between independently addressed MCP4/5 joints is an authored web-margin model indicator.
 g4,a4,p4=facet('Proximal phalanx of fourth finger of hand',side,1,'max');g5,a5,p5=facet('Proximal phalanx of fifth finger of hand',side,1,'max');x=(p4[0]+p5[0])/2;dg=geometry('Dorsum of hand',side);candidates=section_candidates(dg,x,0);assert candidates
 margin,ad=min(candidates,key=lambda x:x[0][1]);target=margin+np.array([0,.001,0])
 replace('TE2',side,lambda:region_surface('TE2',side,'Dorsum of hand',target,[0,0,-1],[('Proximal phalanx of fourth finger of hand',a4,'Ring-finger MCP base'),('Proximal phalanx of fifth finger of hand',a5,'Little-finger MCP base'),('Dorsum of hand',ad,'Original distal hand-dorsum contour between ring/little bases')],'Native ring/little base gap and original hand-dorsum distal contour define AI model web margin;1mm proximal correspondence. Skin colour/fold and palpable precision remain unobserved, not fabricated clinical certainty.'))
 # Source auricular components, each independently evaluated for side, now anchor the ear-adjacent original regional surface.
 lob,la,lp=facet('Lobule of auricle',side,2,'min');tem,ta,tp=facet('Temporal bone',side,1,'min',mask=lambda c:(c[:,0]*sign>.04)&(c[:,2]<0));target=(lp+tp)/2;target[2]=min(lp[2]-.002,target[2])
 replace('TE17',side,lambda:region_surface('TE17',side,'Auricular region',target,lat,[('Lobule of auricle',la,'Original posterior lobule contour'),('Temporal bone',ta,'Original inferior mastoid region')],'Original lobule posterior contour and inferior mastoid region define their adjacent neck/head interval; static regional surface, no ear-lobe guess from temporal bounds.'))
 apex,aa,ap=facet('Apex of auricle',side,1,'max');target=ap+np.array([0,.001,0])
 replace('TE20',side,lambda:region_surface('TE20',side,'Auricular region',target,lat,[('Apex of auricle',aa,'Original auricular apex, independently evaluated')],'Source auricular apex height plus adjacent head surface correspondence. Frozen unfolded-ear model indicator; no simulated pressed-ear pose or exact hairline claim.'))
 for code,num in [('TE18',1),('TE19',2)]:
  def fraction(code=code,num=num):
   c0,a0,l0=prepared[side,'TE17'];c1,a1,l1=prepared[side,'TE20'];line=path([c0['id']],{**a0,'carrierId':c0['id']},{**a1,'carrierId':c1['id']},side);ls=[]
   for ll in [l0[0],l1[0]]:
    l=json.loads(json.dumps(ll));l['evidenceId']=note(code,side,c0,'landmark_annotation',json.dumps(l,ensure_ascii=False));ls.append(l)
   ev=note(code,side,c0,'proportion','WHO TE18/TE19: one-third or two-thirds of source-backed posterior ear17-to-apex20 curved surface path. Fraction is not B-cun or a straight through-body branch.',measurement={'kind':'surface_fraction','value':3});make(code,side,c0,ls,{'kind':'surface_fraction','from':ls[0]['id'],'to':ls[1]['id'],'value':num,'denominator':3,'path':line,'evidenceId':ev},'Actual source ear endpoints and connected original auricular regional surface; AI model curve only. Traditional internal course is not rendered.');units[-1]['observedReferences']=[reference(code,side,c0,'Temporal bone',ta,'Original mastoid bony context')]
  replace(code,side,fraction)
 # Superior tragus boundary and anterior notch identify supratragic interval in the closed-mouth source pose.
 tr,tra,trp=facet('Tragus',side,1,'max');nt,nta,ntp=facet('Anterior notch of auricle',side,near=trp+np.array([0,.001,0]));md,mda,mdp=facet('Mandible',None,1,'max',mask=lambda c:c[:,0]*sign>.03);target=(ntp+mdp)/2;target[1]=ntp[1]
 replace('TE21',side,lambda:region_surface('TE21',side,'Auricular region',target,[sign,0,1],[('Tragus',tra,'Original superior tragus margin'),('Anterior notch of auricle',nta,'Original anterior/supratragic notch correspondence'),('Mandible',mda,'Ipsilateral native condylar process')],'Original notch and superior tragus/mandibular condyle relation. Source mouth is closed; open-mouth depression is an AI static correspondence, not an observed pose.'))
 # A model temple-root indicator retains artery context; hairline is not claimed as observed.
 hel,hla,hlp=facet('Helix',side,2,'max',mask=lambda c:c[:,1]>1.58);ar,ara,arp=slice_point('Superficial temporal artery',side,hlp[1],2,'max');target=(hlp+arp)/2;target[2]=min(arp[2]-.002,target[2])
 replace('TE22',side,lambda:region_surface('TE22',side,'Auricular region',target,[sign,0,1],[('Helix',hla,'Original anterior auricular-root contour'),('Superficial temporal artery',ara,'Source native temporal arterial branch at same root height')],'Actual auricular root and native temporal arterial branch define posterior-artery/anterior-root static model interval. Temple hairline is an AI temporal-boundary proxy, not observed scalp hair or pulse.'))
OUT=R/'atlas-data/acupoints/carriers/native-boundaries-AT8-r14';OUT.mkdir(exist_ok=False);m=read(R/'atlas-data/acupoints/carriers/upper-yang-compact-AT8-r13/manifest.json');m['chunks']=[];m['revision']='AT8-evaluated-region-r14'
for c,ref,name in new_carriers:
 v=np.array(c['positions'],dtype='<f4').reshape(-1,3);idx=np.array(c['indices'],dtype='<u4').reshape(-1,3);b=v.tobytes()+ref.tobytes()+idx.astype('<u2').tobytes();f=c['id']+'.bin';(OUT/f).write_bytes(b);m['chunks'].append({'id':c['id'],'family':'hand' if name=='Dorsum of hand' else 'head','label':'원본 '+name+'의 교육용 정합 면','side':c['side'],'revision':c['revision'],'file':f,'vertices':len(v),'triangles':len(idx),'bytes':len(b),'geometryBufferBytes':len(b),'sha256':sha(b),'topologySha256':c['topologySha256'],'referenceHash':sha(ref.tobytes()+idx.tobytes()),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'clearanceMetres':.002,'sourceObject':name,'surfaceRole':'evaluated original anatomical regional part; not skin scan'})
for k,n in [('totalBytes','bytes'),('totalTriangles','triangles'),('totalGeometryBufferBytes','geometryBufferBytes')]:m[k]=sum(c[n] for c in m['chunks'])
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
for name,data in [('rules-r14',{'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}}),('source-boundary-annotations-r1',native_audit),('author-failures-r14',failures),('source-boundary-provenance-r1',probe_meta)]:
 (E/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
print('units',len(units),'native carrier chunks',len(new_carriers),'failed attempts',len(failures));print([(f['code'],f['side'],f['error']) for f in failures])
