exec((__import__('pathlib').Path(__file__).parent/'inspect.py').read_text().split("for side in ['right','left']:")[0])
cfg=read(R/'atlas-data/acupoints/carriers/education-special-inputs.json')
for side in ['right','left']:
 specs=[];out=[]
 for component in ['plate','fold']:
  key=f'PROBE-nail-{component}-{side}-'+('0' if component=='plate' else '3');item=next(x for x in cfg['probeInputs'] if x['key']==key);probe=read(R/item['path']);o=next(x for x in probe['objects'] if x['name']==item['object']);v=np.array(o['positions']);ids=item['triangleIds'];t=np.array(o['indices'])[ids];specs.append((component,v,t,ids));out.append({'component':component,'source':item,'faces':[{'triangle':int(ids[j]),'centre':v[f].mean(axis=0).tolist()} for j,f in enumerate(t)]})
 img=Image.new('RGB',(1500,900),'white');d=ImageDraw.Draw(img)
 for panel,dims in enumerate([(0,1),(2,1),(0,2)]):
  pts=np.concatenate([v[t].reshape(-1,3) for name,v,t,ids in specs]);lo=pts[:,dims].min(axis=0);hi=pts[:,dims].max(axis=0);scale=min(440/(hi[0]-lo[0]),690/(hi[1]-lo[1]));project=lambda p:tuple((np.array([panel*500+20,800])+((p[list(dims)]-lo)*[scale,-scale])).tolist())
  for j,(name,v,t,ids) in enumerate(specs):
   for f in t:d.polygon([project(p) for p in v[f]],fill=['#809ba8','#dbb08c'][j])
   for n in range(0,len(t),max(1,len(t)//35)):d.text(project(v[t[n]].mean(axis=0)),str(ids[n]),fill='black')
  d.text((panel*500+20,10),f'{side} native thumb nail axes{dims} plate blue/fold brown',fill='black')
 img.save(E/f'inspect-nail-{side}.png');(E/f'nail-faces-{side}.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
