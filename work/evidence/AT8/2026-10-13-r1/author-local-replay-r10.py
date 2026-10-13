from pathlib import Path
E=Path(__file__).parent
exec((E/'author-corrections-r6.py').read_text().split("\nfor side in ['right','left']:")[0])
d=read(E/'rules-r9.json');units=d['units'];carriers=d['inputs']['carriers'];native=d['inputs']['native'];evidence=d['inputs']['evidence'];annotations=read(E/'annotations-r9.json');failures=read(E/'author-failures-r9.json');views=[];rayAudit=[]
for side in ['right','left']:
 sign=-1 if side=='right' else 1
 # Medial attachment crossing is addressed by a preserved original-face view, not a source-side override.
 source_view('Transverse part of trapezius muscle',side)
 uu=next(u for u in units if u['code']=='TE15' and u['side']==side);c=carriers[uu['carrierId']];sf=uu['landmarks'][0]['surface'];ng,na,np0=facet('Transverse part of trapezius muscle',side,near=at(c,sf));l=lm('TE15',side,c,ng,na,sf,'Superficial transverse trapezius at source scapular superior-angle interval','Actual transverse trapezius facet addresses native scapular angle corridor. Ipsilateral source-address view retains original full-object vertex/face mapping. No exact skin or depression claim.');uu['landmarks']=[l];uu['rule']={'kind':'landmark','landmark':l['id']};sg,sa,sp=facet('Scapula',side,1,'max',mask=lambda c:np.abs(c[:,0])<.10);uu['observedReferences']=[reference('TE15',side,c,'Scapula',sa,'Original superior medial scapular angle')]
 # Original semantic SCM facet/mandibular-angle level remains fixed. Vary only a bounded registration ray.
 uu=next(u for u in units if u['code']=='TE16' and u['side']==side);c=carriers[uu['carrierId']];l0=uu['landmarks'][0];p=at(native[l0['sourceKey']],l0['native']);tries=[];chosen=None
 for z in [-.3,-.2,-.1,0,.1,.2,.3]:
  try:
   a=address(c,p,[sign,0,z]);point=at(c,a);gap=float(np.linalg.norm(point-p));correct=point[0]*sign>0;tries.append({'direction':[sign,0,z],'surfaceWorld':point.tolist(),'gap':gap,'correctSubjectSide':bool(correct)})
   if gap<=.02 and correct and chosen is None:chosen=a
  except ValueError as ex:tries.append({'direction':[sign,0,z],'error':str(ex)})
 rayAudit.append({'code':'TE16','side':side,'originalNative':l0['native'],'nativeWorld':p.tolist(),'semanticPointUnchanged':True,'rays':tries,'chosen':chosen,'notNearestLocationEvidence':True})
 if chosen:
  ng=native[l0['sourceKey']];ll=lm('TE16',side,c,ng,l0['native'],chosen,'Posterior SCM at actual mandibular-angle plane','Original SCM posterior facet and native mandibular-angle level fixed; only source-bound ray registration changes, with ipsilateral and20mm checks.');uu['landmarks']=[ll];uu['rule']={'kind':'landmark','landmark':ll['id']}
for name,data in [('rules-r10',{'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}}),('annotations-r10',annotations),('author-failures-r10',failures),('native-address-views-r2',views),('SCM-registration-replay-r1',rayAudit)]:
 (E/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
