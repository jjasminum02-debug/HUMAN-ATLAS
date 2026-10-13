from pathlib import Path
E=Path(__file__).parent
exec((E/'author-corrections-r3.py').read_text().split("\nfor side in ['right','left']:")[0])
d=read(E/'rules-r10.json');units=d['units'];carriers=d['inputs']['carriers'];native=d['inputs']['native'];evidence=d['inputs']['evidence'];annotations=read(E/'annotations-r10.json');failures=read(E/'author-failures-r10.json');audit=[]
for side in ['right','left']:
 sign=-1 if side=='right' else 1;uu=next(u for u in units if u['code']=='TE16' and u['side']==side);l0=uu['landmarks'][0];p=at(native[l0['sourceKey']],l0['native']);candidates=[]
 for cid in ['neck-upper-link-0','head-0']:
  c=carrier(cid)
  for angle in np.linspace(-np.pi*.8,np.pi*.3,18):
   direction=[sign*np.cos(angle),0,np.sin(angle)]
   try:
    a=address(c,p,direction);q=at(c,a);gap=float(np.linalg.norm(q-p));candidates.append({'carrierId':cid,'direction':direction,'address':a,'world':q.tolist(),'gap':gap,'correctSide':bool(q[0]*sign>0),'eligibleRegistration':bool(q[0]*sign>0 and gap<=.02)})
   except ValueError:pass
 viable=[x for x in candidates if x['eligibleRegistration']]
 if viable:
  ch=min(viable,key=lambda c:c['gap']);c=carriers[ch['carrierId']];ng=native[l0['sourceKey']];l=lm('TE16',side,c,ng,l0['native'],ch['address'],'Posterior SCM native mandibular-angle-level indicator','Original semantic source address and its Y-plane stay fixed. Bounded existing-carrier ray fan is only static registration; actual source side and20mm tolerance preserved.');uu['carrierId']=c['id'];uu['landmarks']=[l];uu['rule']={'kind':'landmark','landmark':l['id']};uu['relationEvidenceId']=note('TE16',side,c,'location_relation',uu['originalText']);uu['surfaceEvidenceId']=note('TE16',side,c,'surface_registration','Original posterior SCM + mandibular-angle relation, bounded static carrier registration, no external point coordinate.',maxRegistrationGapMetres=.02)
  for ref in uu.get('observedReferences',[]):ref['evidenceId']=note('TE16',side,c,'landmark_annotation',json.dumps(ref,ensure_ascii=False))
 audit.append({'code':'TE16','side':side,'originalSemanticWorld':p.tolist(),'candidateRegistrations':candidates,'acceptedRegistration':ch if viable else None,'frameAndPoseUnchanged':True,'noLocationFromNearest':True})
for name,data in [('rules-r11',{'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}}),('annotations-r11',annotations),('author-failures-r11',failures),('SCM-final-registration-r1',audit)]:
 (E/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
