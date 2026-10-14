import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path.cwd();E=R/'work/evidence/AT10/2026-10-14-f1-correspondence-r2'
d=json.load(open(R/'work/evidence/AT10/2026-10-14-skin-fit-r5/candidates/fit-r41.json'));f=json.load(open(R/'work/evidence/AT10/2026-10-14-skin-fit-r5/surface-bands-r52.json'))['patches'][0];s=np.array(d['sourceVertices']);ids=set(f['sourceVertices']);faces=[z['derivedVertices'] for z in d['faces'] if set(z['derivedVertices'])<=ids];controls=json.load(open(E/'control-input-f1c2.json'))['controls']
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
skinmat=mat('Original source skin',(.63,.44,.3));green=mat('Unmodified rig helpers',(.1,.8,.2));red=mat('Authored outer surface support',(1,.15,.03));blue=mat('Actual calf topology boundary',(.05,.35,1))
def mesh(name,p,t,material):
 m=bpy.data.meshes.new(name);m.from_pydata([(x,-z,y) for x,y,z in p],[],t);m.update();o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);o.data.materials.append(material)
 for z in m.polygons:z.use_smooth=True
 return o
source=mesh('Original MakeHuman source skin in metres',s.tolist(),faces,skinmat)
for c in controls:
 point=c['source'];bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.0015,location=(point[0],-point[2],point[1]));o=bpy.context.object;o.data.materials.append(blue if c['id'].startswith('actual-calf') else green if c['id'].startswith('joint-') else red)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.color_type='MATERIAL';scene.display.shading.light='STUDIO';scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.world.color=(.065,.075,.09);scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='Standard'
cam=bpy.data.objects.new('Read-only source inspection camera',bpy.data.cameras.new('Read-only source inspection camera'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO'
for name,centre,direction,scale in [('calf-boundary',[-.18,-.62,.03],[-1,.15,.2],.46),('source-dorsal',[-.185,-.795,.070],[0,1,.3],.27),('source-plantar',[-.185,-.795,.070],[0,-1,0],.27),('source-medial',[-.185,-.795,.070],[1,0,.05],.27)]:
 c=Vector((centre[0],-centre[2],centre[1]));dr=Vector((direction[0],-direction[2],direction[1]));cam.location=c+dr.normalized()*3;cam.rotation_euler=(c-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;scene.render.filepath=str(E/'screens'/('original-'+name+'.png'));bpy.ops.render.render(write_still=True)
