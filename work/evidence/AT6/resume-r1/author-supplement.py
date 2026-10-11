exec((__import__('pathlib').Path(__file__).parent/'author-bilateral.py').read_text().split("for side in ['right','left']:")[0])
previous=read(E/'bilateral-rules-r2.json');units=previous['units'];carriers=previous['inputs']['carriers'];native=previous['inputs']['native'];evidence=previous['inputs']['evidence'];annotations=read(E/'annotations-r2.json');audit=[]
for ver in ['lung-local-r6','lung-local-r7']:
 p=manifest_path(ver)
 if p.exists():manifests[ver]=read(p)
# Source probe is an existing world-space snapshot. Its addresses retain original full-object triangle indices.
cfg=read(E/'thenar-nail-config.json')
for spec in cfg['probeInputs']:
 if '-fold-' not in spec['key']:continue
 raw=(R/spec['path']).read_bytes();assert sha(raw)==spec['sha256'];o=next(o for o in json.loads(raw)['objects'] if o['name']==spec['object']);v=np.array(o['positions']);t=np.array(o['indices'],dtype='<u4');k=spec['key'];rows[k]={'sourceKey':k,'side':spec['side'],'names':{'en':spec['object']}}
 native[k]={'id':k,'revision':'native-world-frozen-r1','topologySha256':sha(v.astype('<f4').tobytes()+t.astype('<u4').tobytes()),**context,'side':spec['side'],'positions':v.ravel().tolist(),'indices':t.ravel().tolist(),'rights':rights}
for side in ['right','left']:
 # LU7's longitudinal 1.5/12 level is checked against two actual tendons; a ray cannot create a groove.
 try:
  c=carrier('arm-'+side+'-0');g,a,pa=face('Abductor pollicis longus',side,397);g,b,pb=face('Extensor pollicis brevis',side,487);p=(pa+pb)/2
  old={u['code']:u for u in units if u['side']==side};w=at(carriers[old['LU9']['carrierId']],old['LU9']['landmarks'][3]['surface']);e=at(carriers[old['LU5']['carrierId']],old['LU5']['landmarks'][0]['surface']);level=w[1]+(e[1]-w[1])*1.5/12;assert abs(p[1]-level)<.0015
  surf=address(c,p,side_direction(side,-1,0));ls=[mapped('LU7',side,c,name,i,surf,label,'Two addressed native tendons delimit the radial teaching groove; native longitudinal wrist/cubital level yields 1.5/12. The surface marker registers that groove, not a ray-inferred anatomy.', ['No actual wrist crease or palpable depression; static groove is a model correspondence.']) for name,i,label in [('Abductor pollicis longus',397,'APL tendon at distal radial forearm teaching groove'),('Extensor pollicis brevis',487,'EPB tendon adjacent to APL groove')]]
  relation=f'WHO p29: between APL/EPB, 1.5 B-cun above wrist. Independent native wrist/cubital axial teaching endpoints Y={w[1]}/{e[1]}; 12 B-cun gives Y={level}; actual tendon mean Y={p[1]}, discrepancy={abs(level-p[1])}m. This is a longitudinal structural correspondence, not geodesic winding around wrist or an observed crease.'
  unit('LU7',side,c,ls,{'kind':'landmark','landmark':ls[0]['id']},relation);audit.append({'code':'LU7','side':side,'wrist':w.tolist(),'cubital':e.tolist(),'level1_5of12':level,'nativeTendonLevel':p[1],'errorMetres':abs(level-p[1]),'sourceKeys':[l['sourceKey'] for l in ls]})
 except Exception as ex:failures.append({'code':'LU7','side':side,'error':str(ex),'attempt':'Native APL/EPB facets 397/487 with explicit wrist/cubital 1.5/12 longitudinal check'})
 try:
  c=carrier('thumb-indicator-'+side+'-0');name='Perionyx.'+('r' if side=='right' else 'l');g=geometry(find(name,side),side);a={'triangle':50,'barycentric':[1/3]*3};p=at(g,a);sf=address(c,p,side_direction(side,-1,0))
  l0=landmark('LU11',side,c,name,a,sf,'Native proximal radial nail-fold corner','Actual thumb-component fold facet50 independently read from each side probe; proximal direction checked against distal phalanx base and IP articulation. Model line intersection is at radial nail-base corner, not a painted skin landmark.',['No observed nail-fold skin colour or palpable accuracy; original probe membership retained.'])
  g,a,p=face('Distal phalanx of first finger of hand',side,49);sf1=address(c,p,side_direction(side,-1,0));l1=mapped('LU11',side,c,'Distal phalanx of first finger of hand',49,sf1,'Proximal direction beside radial distal phalanx','Actual distal phalanx facet49 directs the path proximally from nail corner, retaining radial contour.',['Fixed frozen pose only.'])
  ls=[l0,l1]
  for i,d,label in [(10,-1,'Radial IP width boundary'),(140,1,'Ulnar IP width boundary')]:
   g,a,p=face('Proximal phalanx of first finger of hand',side,i);sf2=address(c,p,side_direction(side,d,0));l=mapped('LU11',side,c,'Proximal phalanx of first finger of hand',i,sf2,label,'Native proximal-phalangeal distal articulation facets define an authored thumb IP-level caliper. Full surface width at these addressed sides calibrates 1 F-cun; no source IP skin crease is asserted.',['Teaching joint-width correspondence; individual skin crease and clinical finger-cun accuracy not established.']);l['role']='finger_cun_reference';ls.append(l)
  line=path([c['id']],{**sf,'carrierId':c['id'],'side':side},{**sf1,'carrierId':c['id'],'side':side})
  ev=note('LU11',side,c,'proportion','WHO p13 thumb IP width is 1 F-cun; p31 LU11 is 0.1 F-cun proximal/lateral to radial nail corner. Independent native articulation and nail-corner addresses provide a static structural calibration, not fixed millimetres.',basic['LU11']['standard'],measurement={'kind':'F-cun','value':1})
  unit('LU11',side,c,ls,{'kind':'F-cun','from':l0['id'],'directionTo':l1['id'],'value':.1,'calibration':{'from':ls[2]['id'],'to':ls[3]['id'],'cun':1},'path':line,'evidenceId':ev},'WHO p31 radial thumb nail-base corner, 0.1 F-cun proximally. Existing native thumb nail-fold probe reused; source corner, IP joint caliper and proximal direction are separately addressed; structural educational approximation only.')
  audit.append({'code':'LU11','side':side,'corner':at(c,sf).tolist(),'direction':at(c,sf1).tolist(),'width':np.linalg.norm(at(c,ls[2]['surface'])-at(c,ls[3]['surface'])),'pathSegments':len(line),'probeSha256':next(i['sha256'] for i in cfg['probeInputs'] if i['key']==l0['sourceKey'])})
 except Exception as ex:failures.append({'code':'LU11','side':side,'error':str(ex),'attempt':'Existing native thumb nail corner, source-bound local thumb indicator and actual IP articulation F-cun calibration'})
# Chest construction attempts remain isolated from accepted arm/hand units. No existing proposal coordinate is read.
for side in ['right','left']:
 try:
  c=carrier('chest-indicator-'+side+'-0');cl,claddr,pcm=face('Clavicle',side,616);r1,a,p1=face('First rib',side,960);r2,b,p2=face('Second rib',side,1072)
  x=pcm[0]*1.5;y1=(p1[1]+p2[1])/2;y2=y1+abs(pcm[0])/4
  for code,y in [('LU1',y1),('LU2',y2)]:
   target=np.array([x,y,.01]);sf=address(c,target,[0,0,1]);q=at(c,sf)
   # A specific actual superficial facet must support the teaching transfer. Candidate inspection only, never nearest approval.
   name='Clavicular head of pectoralis major muscle';gg=geometry(find(name,side),side);v,t=arrays(gg);cent=v[t].mean(1);ids=np.flatnonzero((abs(cent[:,0]-x)<.008)&(abs(cent[:,1]-y)<.006));picked=[int(i) for i in ids if np.linalg.norm(cent[i]-q)<.02]
   audit.append({'code':code,'side':side,'status':'candidate_inspection','midclavicle':{'sourceKey':cl['id'],'native':claddr,'xyz':pcm.tolist()},'firstRib':{'sourceKey':r1['id'],'native':a,'xyz':p1.tolist()},'secondRib':{'sourceKey':r2['id'],'native':b,'xyz':p2.tolist()},'model6CunX':x,'modelY':y,'surface':sf,'surfaceWorld':q.tolist(),'superficialFacetsWithinTolerance':picked[:20]})
   failures.append({'code':code,'side':side,'error':'Chest proportional teaching datum is not established: midclavicular shaft is not an observed nipple; projected rib plane needs deltopectoral/first-space homology check before approval.','attempt':'Actual clavicle616/ribs960/1072 -> local native chest patch; computed 6/4 teaching correspondence and explicit surface candidates','neededInput':'Source-addressed chest datum and lateral first-intercostal/deltopectoral correspondence with independent morphology check; do not relabel candidate_inspection as verified.'})
 except Exception as ex:
  failures.extend({'code':code,'side':side,'error':str(ex),'attempt':'Source-bound local chest patch and native clavicle/rib-level teaching correspondence','neededInput':'Specific superficial deltopectoral/first-space native addresses and a justified local B-cun chest datum'} for code in ['LU1','LU2'])
for x in failures:
 if not any(u['code']==x['code'] and u['side']==x['side'] for u in units):
  c=next((c for c in carriers.values() if c['side']==x['side']),None)
  if c:unit(x['code'],x['side'],c,[],{'kind':'unresolved'},'Attempt held: '+json.dumps(x,ensure_ascii=False))
for n,value in [('bilateral-rules-r3',{'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}}),('annotations-r3',annotations),('author-failures-r3',failures),('proportion-audit-r3',audit)]:
 with (E/(n+'.json')).open('x') as f:json.dump(value,f,ensure_ascii=False,separators=(',',':'));f.write('\n')
print('units',len(units),'authored failures',json.dumps(failures,ensure_ascii=False))
