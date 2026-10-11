exec((__import__('pathlib').Path(__file__).parent/'author-bilateral.py').read_text().split("for side in ['right','left']:")[0])
doc=read(E/'bilateral-rules-r5.json');units=[u for u in doc['units'] if u['code']!='LU11'];carriers=doc['inputs']['carriers'];native=doc['inputs']['native'];evidence=doc['inputs']['evidence'];annotations=read(E/'annotations-r5.json');audit=[]
manifests['nail-indicator-r1']=read(manifest_path('nail-indicator-r1'))
# Existing probe geometry is loaded from preserved r5 inputs, never reflected to the other side.
for side in ['right','left']:
 old=next(u for u in doc['units'] if u['code']=='LU11' and u['side']==side);c=carrier('nail-indicator-'+side+'-0');base={'triangle':0,'barycentric':[.5,0,.5]};end={'triangle':1,'barycentric':[.5,.5,0]}
 fold=old['landmarks'][0];k=fold['sourceKey'];rows[k]={'sourceKey':k,'side':side,'names':{'en':'Perionyx.'+('r' if side=='right' else 'l')}}
 l0=landmark('LU11',side,c,rows[k]['names']['en'],{'triangle':151,'barycentric':[1/3]*3},base,'Native proximal radial nail-base corner','Source fold facet151 is the independently inspected proximal radial base apex. A tiny model membrane retains this corner, rather than mapping it inward to the coarse envelope. Actual phalangeal axes define radial and proximal directions.',['AI teaching membrane, not observed skin or patient precision.','0.7mm visual separation from source; source corner and generated surface retained separately.'])
 l1=mapped('LU11',side,c,'Distal phalanx of first finger of hand',49,end,'Native distal phalanx proximal direction origin','Facet49 and facet92 define the actual proximal phalangeal axis; surface endpoint is a 4mm source-directed teaching construction.',['Construction is not a measured skin crease.'])
 ls=[l0,l1]
 for i,oldi,label in [(10,2,'Radial IP joint-width reference'),(140,3,'Ulnar IP joint-width reference')]:
  l=old['landmarks'][oldi].copy();l['surface']={**l['surface'],'carrierId':old['carrierId']};g=native[l['sourceKey']]
  obs={'sourceKey':l['sourceKey'],'native':l['native'],'nativeWorld':at(g,l['native']).tolist(),'surface':l['surface'],'surfaceWorld':at(carriers[old['carrierId']],l['surface']).tolist(),'observed':'Actual independently addressed native IP articulation facet','interpretation':l['modelIndicator'],'relation':label};annotations.append(obs);l['evidenceId']=note('LU11',side,c,'landmark_annotation',json.dumps(obs,ensure_ascii=False));ls.append(l)
 l4=mapped('LU11',side,c,'Distal phalanx of first finger of hand',92,end,'Native distal phalanx proximal axis endpoint','Native facet49 to facet92 is the proximal axis, independent of the surface membrane and IP radial-width axis.',['Frozen pose only; no skin crease implied.']);ls.append(l4)
 ev=note('LU11',side,c,'proportion','WHO p13 thumb IP width calibrates 1 F-cun; p31 LU11 is 0.1 F-cun proximal AND lateral to radial thumb nail-base corner. Surface uses two connected triangles; source-derived radial and proximal directions are separately checked.',basic['LU11']['standard'],measurement={'kind':'F-cun','value':1})
 rule={'kind':'F-cun','from':l0['id'],'directionTo':l1['id'],'value':.1,'calibration':{'from':ls[2]['id'],'to':ls[3]['id'],'cun':1},'path':[{'triangle':0,'from':[.5,0,.5],'to':[0,.5,.5]},{'triangle':1,'from':[.5,0,.5],'to':[.5,.5,0]}],'evidenceId':ev,'nativeDirections':[{'origin':l0['id'],'from':ls[3]['id'],'to':ls[2]['id']},{'origin':l0['id'],'from':l1['id'],'to':l4['id']}]}
 unit('LU11',side,c,ls,rule,'WHO p31: 0.1 F-cun proximal and lateral to the radial thumb nail-base corner. Source fold151/IP articulation10,140/distal phalanx49,92 retained; tiny local AI teaching membrane preserves radial/proximal relation, no whole-hand remake.')
 width=np.linalg.norm(at(carriers[old['carrierId']],ls[2]['surface'])-at(carriers[old['carrierId']],ls[3]['surface']));p=at(c,base)+(at(c,end)-at(c,base))*width*.1/.004;corner=at(native[l0['sourceKey']],l0['native'])
 dots=[]
 for d in rule['nativeDirections']:dots.append(float(np.dot(p-corner,at(native[next(l for l in ls if l['id']==d['to'])['sourceKey']],next(l for l in ls if l['id']==d['to'])['native'])-at(native[next(l for l in ls if l['id']==d['from'])['sourceKey']],next(l for l in ls if l['id']==d['from'])['native']))))
 assert min(dots)>0
 audit.append({'side':side,'cornerSourceWorld':corner.tolist(),'modelResultWorld':p.tolist(),'IPWidthMetres':float(width),'nativeDirectionalDots':dots,'nativeRadialAndProximal':True,'targetCarrier':c['id'],'calibrationCarrier':old['carrierId']})
for name,value in [('bilateral-rules-r6',{'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}}),('annotations-r6',annotations),('nail-direction-audit-r3',audit)]:
 with (E/(name+'.json')).open('x') as f:json.dump(value,f,ensure_ascii=False,separators=(',',':'));f.write('\n')
# Preserve the erroneous coarse-surface attempt with the native radial constraint: it must fail, not be renamed.
prior=read(E/'bilateral-rules-r5.json')
for u in prior['units']:
 if u['code']=='LU11':
  ls=u['landmarks'];u['rule']['nativeDirections']=[{'origin':ls[0]['id'],'from':ls[3]['id'],'to':ls[2]['id']}]
with (E/'bilateral-rules-r5-native-rejected.json').open('x') as f:json.dump(prior,f,ensure_ascii=False,separators=(',',':'));f.write('\n')
print(audit)
