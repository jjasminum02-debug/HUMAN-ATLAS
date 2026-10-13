from pathlib import Path
E=Path(__file__).parent
exec((E/'author-corrections-r3.py').read_text().split("\nfor side in ['right','left']:")[0])
d=read(E/'rules-r5.json');units=d['units'];carriers=d['inputs']['carriers'];native=d['inputs']['native'];evidence=d['inputs']['evidence'];annotations=read(E/'annotations-r5.json');failures=read(E/'author-failures-r5.json');views=[]
def source_view(name,side):
 """Native original object retains identity; an ipsilateral address view preserves original vertex/face correspondence.
 No learner geometry change, side relabelling or hash waiver. Medial attachment crossing is excluded explicitly.
 """
 k=find(name,side);v,t=world(k);sgn=-1 if side=='right' else 1;ids=np.flatnonzero((v[t][:,:,0]*sgn>0).all(axis=1));vi=np.unique(t[ids]);inv={int(old):i for i,old in enumerate(vi)};indices=np.array([[inv[int(x)] for x in tri] for tri in t[ids]],dtype='<u4');p=v[vi].astype('<f4');native[k]={'id':k,'revision':'native-source-address-view-AT8-r1','topologySha256':sha(p.tobytes()+indices.tobytes()),**context,'side':side,'rights':rights,'positions':p.ravel().tolist(),'indices':indices.ravel().tolist()};views.append({'sourceKey':k,'sourceSide':rows[k]['side'],'sourceFileHash':inputs,'fullTopologyHash':sha(v.astype('<f4').tobytes()+t.astype('<u4').tobytes()),'viewTopologyHash':native[k]['topologySha256'],'originalVertexIds':vi.tolist(),'originalTriangleIds':ids.tolist(),'excludedMedialTriangles':len(t)-len(ids),'frameUnchanged':True,'notPointOrSkinApproval':True});return native[k]
for side in ['right','left']:
 sign=-1 if side=='right' else 1;post=[0,0,-1]
 # Shared trunk surface is checked with native trapezius ipsilateral address view; deep scapular angle remains observed context.
 source_view('Descending part of trapezius muscle',side);sg,sa,sp=facet('Scapula',side,1,'max',mask=lambda c:np.abs(c[:,0])<.10)
 replace('TE15',side,lambda:surface_direct('TE15',side,'trunk-2',sp+np.array([0,.004,0]),post,[('Scapula',sa,'Actual superior medial scapular angle')],'Descending part of trapezius muscle','Source-addressed superior scapular angle interval on local superficial trapezius; native address view preserves original source and excludes actual medial attachment crossing.'))
 # Replace only failed reference registrations, preserve every successful target projection.
 for codes,old_name,new_name in [(['LI13','LI14'],'Clavicular part of deltoid muscle','Deltoid fascia'),(['TE10','TE11','TE12'],'Long head of triceps brachii','Brachial fascia'),(['TE7'],'Extensor digitorum','Antebrachial fascia')]:
  for code in codes:
   uu=next((u for u in units if u['code']==code and u['side']==side),None)
   if not uu:continue
   c=carriers[uu['carrierId']]
   for j,l in enumerate(uu['landmarks']):
    if l['sourceKey']!=find(old_name,side):continue
    cs=carriers[l['surface']['carrierId']];ng,na,np0=facet(new_name,side,near=at(cs,l['surface']));ll=lm(code,side,cs,ng,na,l['surface'],'Superficial native fascial correspondence at independently defined anatomical plane','Fascia facet is registration of original '+old_name+' anatomical plane/interval, not location meaning. Original source address remains an observed reference.')
    ll['id']=l['id'];ll['evidenceId']=note(code,side,c,'landmark_annotation',json.dumps({'old':l,'superficialCorrespondence':ll},ensure_ascii=False));uu['landmarks'][j]=ll
    uu.setdefault('observedReferences',[]).append(reference(code,side,c,old_name,l['native'],'Original independently addressed anatomical calibration/ulnar relation'))
for name,data in [('rules-r6',{'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}}),('annotations-r6',annotations),('author-failures-r6',failures),('native-address-views-r1',views)]:
 (E/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
