"""Reuse the original AC1/AT8 evaluated reader contract for bounded face surfaces."""
import bpy,json,hashlib
from pathlib import Path
R=Path.cwd();E=R/'work/evidence/AT10/2026-10-15-f3-head-r1';S=R/'atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend';h=hashlib.sha256(S.read_bytes()).hexdigest();assert h=='9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd';assert not bpy.context.preferences.filepaths.use_scripts_auto_execute
assert not (E/'native-eye-components-v2.json').exists(), 'Pinned extraction exists; reuse it or choose a new evidence version.'
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False);assert bpy.context.scene.frame_current==0;dg=bpy.context.evaluated_depsgraph_get();names=['Lens.l','Lens.r','Sclera.l','Sclera.r','Iris.l','Iris.r','Cornea.l','Cornea.r','Gingiva','Tongue','Soft palate','Teeth.g','Teeth.j','Auricular region.l','Auricular region.r','Helix.l','Helix.r','Tragus.l','Tragus.r','Lobule of auricle.l','Lobule of auricle.r','Posterior auricular groove.l','Posterior auricular groove.r'];out=[]
for name in names:
 obj=bpy.data.objects.get(name)
 if obj is None:out.append({'name':name,'failure':'source_absent'});continue
 ev=obj.evaluated_get(dg);m=ev.to_mesh()
 if m is None:out.append({'name':name,'failure':'no_mesh'});continue
 m.calc_loop_triangles();pts=[obj.matrix_world@v.co for v in m.vertices];v=[[p.x,p.z,-p.y] for p in pts];t=[list(x.vertices) for x in m.loop_triangles];materials=[{'name':a.name,'color':list(a.diffuse_color)} for a in m.materials if a];out.append({'sourceKey':'ZA-original:'+name,'name':name,'side':'left' if name.endswith('.l') else 'right' if name.endswith('.r') else None,'v':v,'t':t,'materials':materials,'matrixAppliedOnce':True,'bounds':[[min(x[k] for x in v) for k in range(3)],[max(x[k] for x in v) for k in range(3)]],'hideSource':obj.hide_viewport});ev.to_mesh_clear()
(E/'native-eye-components-v2.json').write_text(json.dumps({'sourceSha256':h,'frameId':'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR','poseId':'ZA-9f08a17ea0115fed-frame0-autoexec-off','unit':'m','objects':out,'sourceReadOnly':True,'providerSurfacesNotSkinOrAcupointApproval':True},separators=(',',':'))+'\n');print([(x['name'],len(x.get('t',[])),x.get('bounds'),x.get('materials')) for x in out],flush=True)
