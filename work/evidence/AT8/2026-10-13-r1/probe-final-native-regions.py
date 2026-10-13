"""Read-only bounded reuse of AC1 source probe for remaining AT8 native landmarks."""
import bpy,json,hashlib
from pathlib import Path
R=Path('/Users/daniel/Downloads/SIM /HUMAN ATLAS');E=R/'work/evidence/AT8/2026-10-13-r1';S=R/'atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend';h=hashlib.sha256(S.read_bytes()).hexdigest();assert h=='9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd';assert not bpy.context.preferences.filepaths.use_scripts_auto_execute
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False);assert bpy.context.scene.frame_current==0 and bpy.context.scene.unit_settings.scale_length==1
dg=bpy.context.evaluated_depsgraph_get();names=[]
for name in ['Oral region','Temporal region']:
 for suffix in ['.r','.l']:names.append(name+suffix)
out=[]
for name in names:
 obj=bpy.data.objects.get(name)
 if obj is None:out.append({'name':name,'failure':'source_object_absent'});continue
 ev=obj.evaluated_get(dg);m=ev.to_mesh();
 if m is None:out.append({'name':name,'failure':'no_evaluated_mesh'});continue
 m.calc_loop_triangles();pts=[obj.matrix_world@v.co for v in m.vertices];pts=[[p.x,p.z,-p.y] for p in pts]
 out.append({'name':name,'vertices':len(pts),'triangles':len(m.loop_triangles),'positions':pts,'indices':[list(t.vertices) for t in m.loop_triangles],'matrixAppliedOnce':True,'hideViewport':obj.hide_viewport,'hideRender':obj.hide_render,'collections':[c.name for c in obj.users_collection],'modifiers':[m.type for m in obj.modifiers],'constraints':[c.type for c in obj.constraints]});ev.to_mesh_clear()
(E/'evaluated-native-boundaries-r3.json').write_text(json.dumps({'sourceSha256':h,'frame':'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR','unit':'m','pose':'ZA-9f08a17ea0115fed-frame0-autoexec-off','autoExecute':False,'matrixConvention':'source XYZ to[X,Z,-Y], same AC1 reader; evaluated frame0','objects':out,'sourceWrites':0,'sourceDownloads':0},ensure_ascii=False,separators=(',',':'))+'\n');assert hashlib.sha256(S.read_bytes()).hexdigest()==h
print('AT8_EVALUATED',[(o['name'],o.get('vertices'),o.get('triangles'),o.get('failure')) for o in out])
