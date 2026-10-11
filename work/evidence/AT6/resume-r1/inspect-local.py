exec((__import__('pathlib').Path(__file__).parent/'inspect.py').read_text().split("for side in ['right','left']:")[0])
for side in ['right','left']:
 sign=-1 if side=='right' else 1
 specs=[('Radius',native('Radius',side)),('Scaphoid bone',native('Scaphoid bone',side)),('Abductor pollicis longus',native('Abductor pollicis longus',side)),('Extensor pollicis brevis',native('Extensor pollicis brevis',side)),('First metacarpal bone',native('First metacarpal bone',side)),('Abductor pollicis brevis',native('Abductor pollicis brevis',side))]
 img=Image.new('RGB',(1500,1000),'white');d=ImageDraw.Draw(img);out=[]
 for panel,dims in enumerate([(0,1),(2,1),(0,2)]):
  lo=np.array([-.335,.805]) if panel==0 and sign<0 else np.array([.25,.805]) if panel==0 else np.array([-.045,.805]) if panel==1 else np.array([-.335,-.045]) if sign<0 else np.array([.25,-.045])
  scale=480/.085
  project=lambda p:tuple((np.array([panel*500+10,940])+((p[list(dims)]-lo)*[scale,-scale])).tolist())
  colors=['#d9c3a3','#9ab49a','#d78787','#829dbd','#cab481','#af8fae']
  for j,(name,(v,t)) in enumerate(specs):
   ids=np.flatnonzero((v[t][:,:,1].min(axis=1)<.885)&(v[t][:,:,1].max(axis=1)>.805))
   for i in ids:d.polygon([project(p) for p in v[t[i]]],fill=colors[j],outline=colors[j])
   for i in ids[::max(1,len(ids)//18)]:d.text(project(v[t[i]].mean(axis=0)),f'{j}:{i}',fill='black')
   d.text((panel*500+10,10+15*j),f'{j} {name}',fill='black')
  for y in np.arange(.81,.89,.01):
   if panel<2:
    yy=940-(y-lo[1])*scale;d.line((panel*500,yy,(panel+1)*500,yy),fill='#888888');d.text((panel*500+400,yy),f'y={y:.3f}',fill='black')
 img.save(E/f'inspect-wrist-{side}.png')
 for name,(v,t) in specs:
  ids=np.flatnonzero((v[t][:,:,1].min(axis=1)<.872)&(v[t][:,:,1].max(axis=1)>.848))
  out.append({'name':name,'sourceKey':find(name,side),'faces':[{'triangle':int(i),'centre':v[t[i]].mean(axis=0).tolist()} for i in ids]})
 (E/f'wrist-faces-{side}.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
