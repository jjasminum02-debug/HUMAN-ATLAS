from pathlib import Path
E=Path(__file__).parent
exec((E/'author-corrections-r3.py').read_text().split("\nfor side in ['right','left']:")[0])
d=read(E/'rules-r18.json');units=d['units'];carriers=d['inputs']['carriers'];native=d['inputs']['native'];evidence=d['inputs']['evidence'];annotations=read(E/'annotations-r11.json');failures=[];prepared={};graphs={}
for u in units:
 if u['rule']['kind']=='landmark':prepared[u['side'],u['code']]=(carriers[u['carrierId']],u['landmarks'][0]['surface'],u['landmarks'])
side='left';rr,ra,rp=facet('Radius',side,1,'min');y=rp[1];epl,ea,ep=slice_point('Extensor pollicis longus',side,y,0,'max');epb,ba,bp=slice_point('Extensor pollicis brevis',side,y,0,'min')
replace('LI5',side,lambda:surface_direct('LI5',side,'wrist-link-left-0',(ep+bp)/2,[1,0,0],[('Extensor pollicis longus',ea,'EPL medial snuffbox border at styloid plane'),('Extensor pollicis brevis',ba,'EPB lateral snuffbox border at styloid plane')],'Extensor retinaculum of wrist','Anatomy-defined native EPL/EPB interval at radial styloid level. Pure radial registration selects outer radial wrist instead of the failed oblique ray inner surface. Frozen-pose educational snuffbox indicator.'))
for code,value in [('LI6',3),('LI7',5),('LI8',8),('LI9',9),('LI10',10)]:replace(code,side,lambda code=code,value=value:proportion(code,side,'LI5','LI11',value,12,['wrist-link-left-0','arm-left-0','arm-left-1'],'Native radial dorsal wrist-to-cubital12 B-cun interval with corrected source-backed radial wrist endpoint; no camera workaround or external coordinates.'))
assert not failures,failures
(E/'rules-r19.json').write_text(json.dumps({'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}},ensure_ascii=False,separators=(',',':'))+'\n')
(E/'radial-wrist-annotations-r19.json').write_text(json.dumps(annotations[-11:],ensure_ascii=False,indent=2)+'\n')
