exec((__import__('pathlib').Path(__file__).parent/'author-bilateral.py').read_text().split("for side in ['right','left']:")[0])
previous=read(E/'bilateral-rules-r2.json');units=previous['units'];carriers=previous['inputs']['carriers'];native=previous['inputs']['native'];evidence=previous['inputs']['evidence'];annotations=read(E/'annotations-r2.json');audit=[]
for ver in ['lung-local-r6','lung-local-r7']:
 p=R/f'atlas-data/acupoints/carriers/{ver}/manifest.json'
 if p.exists():manifests[ver]=read(p)
# Source probe is an existing world-space snapshot. Its addresses retain original full-object triangle indices.
cfg=read(E/'thenar-nail-config.json')
for spec in cfg['probeInputs']:
 if '-fold-' not in spec['key']:continue
 raw=(R/spec['path']).read_bytes();assert sha(raw)==spec['sha256'];o=next(o for o in json.loads(raw)['objects'] if o['name']==spec['object']);v=np.array(o['positions']);t=np.array(o['indices'],dtype='<u4');k=spec['key'];rows[k]={'sourceKey':k,'side':spec['side'],'names':{'en':spec['object']}}
 native[k]={'id':k,'revision':'native-world-frozen-r1','topologySha256':sha(v.astype('<f4').tobytes()+t.astype('<u4').tobytes()),**context,'side':spec['side'],'positions':v.ravel().tolist(),'indices':t.ravel().tolist(),'rights':rights}
doc=read(E/'bilateral-rules-r4.json');units=[u for u in doc['units'] if u['code']!='LU11'];carriers=doc['inputs']['carriers'];native=doc['inputs']['native'];evidence=doc['inputs']['evidence'];annotations=read(E/'annotations-r4.json');audit=[];failures=[]
for side in ['right','left']:
 try:
  c=carrier('thumb-indicator-'+side+'-0');name='Perionyx.'+('r' if side=='right' else 'l');g=geometry(find(name,side),side);a={'triangle':151,'barycentric':[1/3]*3};p=at(g,a);sf=address(c,p,side_direction(side,-1,0))
  l0=landmark('LU11',side,c,name,a,sf,'Native proximal radial nail-fold corner','Actual thumb-component fold proximal radial base apex facet151 independently read from each side probe; proximal direction checked against distal phalanx base and IP articulation. Model line intersection is at radial nail-base corner, not a painted skin landmark.',['No observed nail-fold skin colour or palpable accuracy; original probe membership retained.'])
  g,a,p=face('Distal phalanx of first finger of hand',side,49);sf1=address(c,p,side_direction(side,-1,0));l1=mapped('LU11',side,c,'Distal phalanx of first finger of hand',49,sf1,'Proximal direction beside radial distal phalanx','Actual distal phalanx facet49 directs the path proximally from nail corner, retaining radial contour.',['Fixed frozen pose only.'])
  ls=[l0,l1]
  for i,d,label in [(10,-1,'Radial IP width boundary'),(140,1,'Ulnar IP width boundary')]:
   g,a,p=face('Proximal phalanx of first finger of hand',side,i);sf2=address(c,p,side_direction(side,d,0));l=mapped('LU11',side,c,'Proximal phalanx of first finger of hand',i,sf2,label,'Native proximal-phalangeal distal articulation facets define an authored thumb IP-level caliper. Full surface width at these addressed sides calibrates 1 F-cun; no source IP skin crease is asserted.',['Teaching joint-width correspondence; individual skin crease and clinical finger-cun accuracy not established.']);l['role']='finger_cun_reference';ls.append(l)
  line=path([c['id']],{**sf,'carrierId':c['id'],'side':side},{**sf1,'carrierId':c['id'],'side':side})
  ev=note('LU11',side,c,'proportion','WHO p13 thumb IP width is 1 F-cun; p31 LU11 is 0.1 F-cun proximal/lateral to radial nail corner. Independent native articulation and nail-corner addresses provide a static structural calibration, not fixed millimetres.',basic['LU11']['standard'],measurement={'kind':'F-cun','value':1})
  unit('LU11',side,c,ls,{'kind':'F-cun','from':l0['id'],'directionTo':l1['id'],'value':.1,'calibration':{'from':ls[2]['id'],'to':ls[3]['id'],'cun':1},'path':line,'evidenceId':ev},'WHO p31 radial thumb nail-base corner, 0.1 F-cun proximally. Existing native thumb nail-fold probe reused; source corner, IP joint caliper and proximal direction are separately addressed; structural educational approximation only.')
  audit.append({'code':'LU11','side':side,'corner':at(c,sf).tolist(),'direction':at(c,sf1).tolist(),'width':np.linalg.norm(at(c,ls[2]['surface'])-at(c,ls[3]['surface'])),'pathSegments':len(line),'probeSha256':next(i['sha256'] for i in cfg['probeInputs'] if i['key']==l0['sourceKey'])})
 except Exception as ex:failures.append({'code':'LU11','side':side,'error':str(ex),'attempt':'Existing native thumb nail corner, source-bound local thumb indicator and actual IP articulation F-cun calibration'})
assert not failures,failures
for name,value in [('bilateral-rules-r5',{'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}}),('annotations-r5',annotations),('nail-direction-audit-r2',audit)]:
 with (E/(name+'.json')).open('x') as f:json.dump(value,f,ensure_ascii=False,separators=(',',':'));f.write('\n')
