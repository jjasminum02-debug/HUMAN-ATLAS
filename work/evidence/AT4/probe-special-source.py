"""Read-only extension of AC1/AC2 native nail probe; original never saved."""
import bpy,json,hashlib
from pathlib import Path
R=Path('/Users/daniel/Downloads/SIM /HUMAN ATLAS');E=R/'work/evidence/AT4'
S=R/'atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(S)=='9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd'
assert not bpy.context.preferences.filepaths.use_scripts_auto_execute
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False)
assert bpy.context.scene.frame_current==0 and bpy.context.scene.unit_settings.scale_length==1
names=['Nail plate (foot).l','Nail plate (foot).r','Perionyx (foot).l','Perionyx (foot).r','Tongue','Anal region.l','Anal region.r','Urogenital region.l','Urogenital region.r','Regions of perineum.j']
dg=bpy.context.evaluated_depsgraph_get();out=[]
for name in names:
 obj=bpy.data.objects.get(name)
 if obj is None or obj.type!='MESH':out.append({'name':name,'failure':'missing_mesh'});continue
 ev=obj.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles()
 pts=[obj.matrix_world@v.co for v in m.vertices];pts=[[p.x,p.z,-p.y] for p in pts]
 out.append({'name':name,'vertices':len(pts),'triangles':len(m.loop_triangles),'positions':pts,'indices':[list(t.vertices) for t in m.loop_triangles],'hideViewport':obj.hide_viewport,'hideRender':obj.hide_render,'matrixAppliedOnce':True,'collections':[c.name for c in obj.users_collection]});ev.to_mesh_clear()
collections=[]
for name in ['Skin','Dermis','Mucosa of mouth','Mucosa of tongue','Inferior surface of tongue','Perineal membrane','Regions of perineum','Perineal muscles']:
 c=bpy.data.collections.get(name);collections.append({'name':name,'exists':c is not None,'meshObjects':sorted(o.name for o in c.all_objects if o.type=='MESH') if c else [],'directObjects':sorted(o.name for o in c.objects) if c else []})
x={'sourceSha256':sha(S),'frame':'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR','unit':'m','pose':'ZA-9f08a17ea0115fed-frame0-autoexec-off','matrixConvention':'source XYZ to [X,Z,-Y]; same AC1 probe','objects':out,'collections':collections,'sourceWrites':0,'sourceDownloads':0}
(E/'special-source-probe.json').write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
print('AT4_PROBE',[(o['name'],o.get('vertices'),o.get('triangles')) for o in out],collections)
