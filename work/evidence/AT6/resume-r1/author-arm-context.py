exec((__import__('pathlib').Path(__file__).parent/'author-bilateral.py').read_text().split("for side in ['right','left']:")[0])
doc=read(E/'bilateral-rules-r6.json');units=doc['units'];carriers=doc['inputs']['carriers'];native=doc['inputs']['native'];evidence=doc['inputs']['evidence'];annotations=read(E/'annotations-r6.json');checks=[]
for u in units:
 if u['code'] not in ['LU3','LU4']:continue
 side=u['side'];c=carriers[u['carrierId']];g,a,p=face('Sternocostal head of pectoralis major muscle',side,45)
 meaning='Actual pectoral humeral insertion facet45 establishes the authored axillary measurement plane. Deltoid199 is superficial registration of this plane, not axillary-fold identity; no source skin fold is claimed.'
 record={'sourceKey':g['id'],'native':anchor(g,a,side),'nativeWorld':p.tolist(),'anatomy':'Sternocostal head of pectoralis major muscle insertion','interpretation':meaning,'observed':'Native frozen insertion geometry; model axial plane is AI authored'};annotations.append(record)
 ref={'id':u['id']+'-pectoral-context','anatomy':record['anatomy'],'acquisition':'anatomical_annotation','side':side,'sourceKey':g['id'],'native':record['native'],'evidenceId':note(u['code'],side,c,'landmark_annotation',json.dumps(record,ensure_ascii=False)),'interpretation':meaning};u['observedReferences']=[ref]
 model=u['landmarks'][0];delta=abs(p[1]-at(native[model['sourceKey']],model['native'])[1]);assert delta<.001
 checks.append({'id':u['id'],'sourceKey':g['id'],'native':record['native'],'modelLevelSource':model['native'],'axialCorrespondenceErrorMetres':float(delta),'exactSkinFoldObserved':False})
for name,v in [('bilateral-rules-r7',doc),('annotations-r7',annotations),('axillary-context-validation-r1',checks)]:
 with (E/(name+'.json')).open('x') as f:json.dump(v,f,ensure_ascii=False,separators=(',',':'));f.write('\n')
print('source-bound axial context',checks)
