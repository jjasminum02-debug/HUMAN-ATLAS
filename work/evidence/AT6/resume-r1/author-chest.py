exec((__import__('pathlib').Path(__file__).parent/'author-bilateral.py').read_text().split("for side in ['right','left']:")[0])
doc=read(E/'bilateral-rules-r3.json');units=[u for u in doc['units'] if u['code'] not in ['LU1','LU2']];carriers=doc['inputs']['carriers'];native=doc['inputs']['native'];evidence=doc['inputs']['evidence'];annotations=read(E/'annotations-r3.json');audit=[]
for ver in ['lung-local-r7','lung-fossa-r1']:manifests[ver]=read(manifest_path(ver))
def observation(code,side,c,name,i,interpretation):
 g,a,p=face(name,side,i);record={'sourceKey':g['id'],'native':anchor(g,a,side),'nativeWorld':p.tolist(),'anatomy':name,'interpretation':interpretation,'observed':'Native frozen geometry only; no skin surface assertion'}
 annotations.append(record);return {'id':f'{code}-{side}-context-{len(annotations)}','anatomy':name,'acquisition':'anatomical_annotation','side':side,'sourceKey':g['id'],'native':record['native'],'evidenceId':note(code,side,c,'landmark_annotation',json.dumps(record,ensure_ascii=False)),'interpretation':interpretation}
for side in ['right','left']:
 cf=carrier('fossa-'+side+'-0');cc=carrier('chest-indicator-'+side+'-0')
 g,a,pm=face('Clavicle',side,616);w=abs(pm[0])/4;x=pm[0]*1.5
 g,a,p1=face('Clavicular head of pectoralis major muscle',side,388);g,a,p2=face('Clavicular part of deltoid muscle',side,2294);y2=(p1[1]+p2[1])/2;y1=y2-w
 fossa=address(cf,[x,y2,.01],[0,0,1]);q2=at(cf,fossa);chest=address(cc,[x,y1,.01],[0,0,1]);q1=at(cc,chest)
 # Independent native relation checks, in the declared axial model rather than global body bounds.
 _,_,first=face('First rib',side,960);_,_,second=face('Second rib',side,1072);_,_,coracoid=face('Scapula',side,12916)
 assert second[1]<y1<first[1] and y2<pm[1] and abs(q2[0])<abs(coracoid[0]) and q2[2]>coracoid[2]
 v,t=arrays(cf);assert min(fossa['barycentric'])>=0 and np.linalg.norm(q2-q1)>.018
 # WHO p12 defines nipple-to-nipple8; WHO LR14 note uses the midclavicular line as the 4-cun surface reference.
 # Here the native clavicular midshaft defines an explicitly AUTHORED teaching grid. It is never called a native nipple.
 common=f'WHO p12 transverse nipple reference8 B-cun, LR14 note midclavicular surface line4 B-cun; educational model datum at addressed clavicular midshaft616 X={pm[0]} gives 1 B-cun={w}m, 6-cun line X={x}. This is an AI standard teaching grid, not an observed nipple or individualized chest measurement. Native skin/nipple accuracy remains unresolved. Static frame/side only.'
 for code,c,sf,name,i,meaning in [('LU2',cf,fossa,'Clavicular head of pectoralis major muscle',375,'Deltopectoral triangle depression, medial to addressed coracoid and below clavicle'),('LU1',cc,chest,'Clavicular head of pectoralis major muscle',330,'Upper lateral pectoral teaching transfer of native first-intercostal plane, 1 model B-cun below LU2')]:
  ls=[mapped(code,side,c,name,i,sf,meaning,common+' Source upper pectoral boundary supports superficial registration; ray establishes no point meaning.',['The chest grid and lateral rib-plane transfer are AI educational correspondences, not detected nipple/skin landmarks or precise clinical positions.'])]
  unit(code,side,c,ls,{'kind':'landmark','landmark':ls[0]['id']},common+(' WHO p27: infraclavicular deltopectoral triangle, medial to coracoid; candidate is inside three-source fossa membrane and below clavicle.' if code=='LU2' else ' WHO p26: lateral upper chest first-intercostal teaching plane and 1 B-cun inferior to LU2. First960 and second1072 bound the transferred plane; original rib space is not claimed to extend physically to this surface point.'))
  units[-1]['observedReferences']=[observation(code,side,c,n,j,reason) for n,j,reason in [('Clavicle',616,'Actual midshaft observes the midclavicular teaching datum; NOT an observed nipple.'),('First rib',960,'Actual upper boundary for first-intercostal model-plane transfer.'),('Second rib',1072,'Actual lower boundary for first-intercostal model-plane transfer.'),('Scapula',12916,'Actual medial coracoid facet; LU2 is medial and anterior in the static teaching correspondence.')]]
  audit.append({'code':code,'side':side,'surfaceWorld':at(c,sf).tolist(),'gridDatum':pm.tolist(),'cunMetres':w,'model6CunX':x,'firstRibWorld':first.tolist(),'secondRibWorld':second.tolist(),'coracoidWorld':coracoid.tolist(),'checks':{'insideFossaTriangle':min(fossa['barycentric'])>=0,'LU2MedialCoracoid':abs(q2[0])<abs(coracoid[0]),'LU2BelowClavicle':y2<pm[1],'LU1BetweenTransferredRibPlanes':second[1]<y1<first[1],'oneModelCunInferior':abs(y2-y1-w)<1e-9},'limits':['Authored midclavicular 4-cun teaching template, NOT individual nipple datum','Lateral rib-plane correspondence, NOT native skin or literal rib geometry at point','Professor not reviewed; precise clinical location unresolved; public release held']})
result={'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}}
assert read(E/'bilateral-rules-r4.json')==result, 'Immutable prior compiler input changed'
assert read(E/'annotations-r4.json')==annotations, 'Immutable annotations changed'
with (E/'chest-morphology-audit-r3.json').open('x') as f:json.dump(audit,f,ensure_ascii=False,indent=2,default=lambda x: bool(x) if isinstance(x,np.bool_) else float(x));f.write('\n')
print('source-authored units',len(units))
