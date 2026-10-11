import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/Users/daniel/Downloads/SIM /HUMAN ATLAS')
S=R/'atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend'
assert hashlib.sha256(S.read_bytes()).hexdigest()=='9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd'
assert not bpy.context.preferences.filepaths.use_scripts_auto_execute
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False)
assert bpy.context.scene.frame_current==0 and bpy.context.scene.unit_settings.scale_length==1
names=['Nail plate.l','Perionyx.l']
dg=bpy.context.evaluated_depsgraph_get();out=[]
for name in names:
 obj=bpy.data.objects[name];ev=obj.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles()
 pts=[obj.matrix_world@v.co for v in m.vertices];pts=[[p.x,p.z,-p.y] for p in pts]
 # connected components reveal whether source name covers all fingers.
 adj=[set() for _ in pts]
 for e in m.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
 unseen=set(range(len(pts)));comps=[]
 while unseen:
  todo=[unseen.pop()];comp=[]
  while todo:
   i=todo.pop();comp.append(i)
   for j in adj[i]&unseen:unseen.remove(j);todo.append(j)
  comps.append({'vertices':len(comp),'bounds':[[min(pts[i][k] for i in comp) for k in range(3)],[max(pts[i][k] for i in comp) for k in range(3)]]})
 out.append({'name':name,'vertices':len(pts),'triangles':len(m.loop_triangles),'components':comps,'positions':pts,'indices':[list(t.vertices) for t in m.loop_triangles]});ev.to_mesh_clear()
(R/'work/evidence/acupoint-AC2/left-source-probe.json').write_text(json.dumps({'sourceSha256':hashlib.sha256(S.read_bytes()).hexdigest(),'frame':'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR','unit':'m','pose':'ZA-9f08a17ea0115fed-frame0-autoexec-off','objects':out},indent=2))
