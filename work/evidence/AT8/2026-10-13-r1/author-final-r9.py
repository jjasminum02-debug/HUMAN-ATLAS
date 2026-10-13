from pathlib import Path
E=Path(__file__).parent
exec((E/'author-corrections-r3.py').read_text().split("\nfor side in ['right','left']:")[0])
d=read(E/'rules-r8.json');units=d['units'];carriers=d['inputs']['carriers'];native=d['inputs']['native'];evidence=d['inputs']['evidence'];annotations=read(E/'annotations-r8.json');failures=read(E/'author-failures-r8.json');manifests['upper-yang-boundary-AT8-r2']=read(R/'atlas-data/acupoints/carriers/upper-yang-boundary-AT8-r2/manifest.json');extraAudit=[]
for side in ['right','left']:
 sign=-1 if side=='right' else 1
 for code,cid,names in [('TE15','girdle-link-0',['Transverse part of trapezius muscle','Descending part of trapezius muscle','Levator scapulae muscle','Rhomboid minor muscle']),('TE16','neck-upper-link-0',['Platysma','Sternocleidomastoid muscle'])]:
  old=next(u for u in units if u['code']==code and u['side']==side);c=carriers[old['carrierId']];sf=old['landmarks'][0]['surface'];target=at(c,sf);candidates=[]
  for name in names:
   try:ng,na,np0=facet(name,side,near=target);gap=float(np.linalg.norm(np0-target));candidates.append((gap,name,ng,na,np0))
   except AssertionError:continue
  extraAudit.append({'code':code,'side':side,'targetWorld':target.tolist(),'namedRegionalSuperficialRegistrationCandidates':[{'name':n,'gapMetres':gap,'triangle':na['triangle'],'world':np0.tolist()} for gap,n,ng,na,np0 in candidates],'semanticRole':'Original scapular angle or posterior SCM plane remains source-bound observed context; superficial candidate is registration only.'})
  viable=[p for p in candidates if p[0]<=.02 and (p[2]['side']=='midline' or all((x<0 if side=='right' else x>0) for x in p[2]['positions'][::3]))]
  if not viable:continue
  gap,name,ng,na,np0=min(viable,key=lambda x:x[0]);l=lm(code,side,c,ng,na,sf,'Native superficial correspondence of '+('superior scapular-angle interval' if code=='TE15' else 'posterior SCM mandibular-angle plane'),'Named regional superficial structure '+name+' registers independently defined underlying anatomical interval; native feature remains separate and no skin observed.');old['landmarks']=[l];old['rule']={'kind':'landmark','landmark':l['id']}
  if code=='TE15':sg,sa,sp=facet('Scapula',side,1,'max',mask=lambda c:np.abs(c[:,0])<.10);old['observedReferences']=[reference(code,side,c,'Scapula',sa,'Original superior medial scapular-angle facet')]
  else:
   # Preserve already bound original mandibular angle, add independently addressed posterior SCM source facet.
   old['observedReferences'].append(reference(code,side,c,'Sternocleidomastoid muscle',d['units'][d['units'].index(old)]['landmarks'][0]['native'] if False else next(a['native'] for a in reversed(annotations[:-1]) if a['code']==code and a['side']==side),'Original posterior SCM correspondence at mandibular-angle plane'))
# Failures requiring truly absent anatomy or contradictory surface support are still explicit, never relocated.
for name,data in [('rules-r9',{'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}}),('annotations-r9',annotations),('author-failures-r9',failures),('regional-registration-audit-r1',extraAudit)]:
 (E/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
