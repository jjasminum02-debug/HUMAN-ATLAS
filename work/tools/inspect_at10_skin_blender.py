"""Offline AT10 fitted skin/native QA in verified Blender, never loads Startup scripts."""
import bpy,os,json,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
R=Path(__file__).resolve().parents[2];E=Path(os.environ.get('AT10_SKIN_EVIDENCE',str(R/'work/evidence/AT10/2026-10-13-skin-fit-r1')))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
rev=sys.argv[sys.argv.index('--revision')+1] if '--revision' in sys.argv else 'r9'
O=Path(os.environ.get('AT10_SKIN_ARTIFACTS',str(R/'atlas-data/anatomy/skin/at10-fit-r1')))
nativePath=E/'native-surfaces-r1.json'
if not nativePath.exists():nativePath=R/'work/evidence/AT10/2026-10-13-skin-fit-r1/native-surfaces-r1.json'
d=json.loads((E/f'candidates/fit-{rev}.json').read_text());native=json.loads(nativePath.read_text())
tag=os.environ.get('AT10_SKIN_QA_TAG','');suffix=('-'+tag) if tag else ''
supplement=os.environ.get('AT10_NATIVE_SUPPLEMENT')
if supplement:
    extra=json.loads((R/supplement).read_text());assert not set(extra)&set(native);native.update(extra)
v=np.array(d['positions']);faces=[f['derivedVertices'] for f in d['faces']]
t=np.array([[f[0],f[i],f[i+1]] for f in faces for i in range(1,len(f)-1)])
# Geometry in HUMAN ATLAS axes throughout numerical QA. Blender draw conversion only.
def mesh(name,p,t,color):
    m=bpy.data.meshes.new(name);m.from_pydata([(float(x),float(-z),float(y)) for x,y,z in p],[],t);m.update()
    o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o)
    mat=bpy.data.materials.new(name);mat.diffuse_color=color;o.data.materials.append(mat)
    for f in m.polygons:f.use_smooth=True
    return o
original=v.copy()
npv=[];npt=[]
for s in native.values():
    off=len(npv);npv.extend(s['v']);pv=np.array(s['v']);pt=np.array(s['t']);volume=np.einsum('ij,ij->i',pv[pt[:,0]],np.cross(pv[pt[:,1]],pv[pt[:,2]])).sum()/6
    npt.extend([[a+off,b+off,c+off] if volume>=0 else [a+off,c+off,b+off] for a,b,c in s['t']])
print('BVH inputs',len(npv),len(npt),flush=True)
# Build exact fixed native triangle geometry index. No approximation geometry is used for contact QA.
bvh=BVHTree.FromPolygons(npv,npt,all_triangles=True)
# Articulated correspondence provides meaningful centres. Contact is only a final
# fit constraint and is never used as anatomical or acupoint semantic evidence.
region=d['vertexRegions'];contactPasses=[]
near=[]
for p in v:
    q,n,idx,dist=bvh.find_nearest(Vector(p));near.append([dist,float((Vector(p)-q).dot(n))])
near=np.array(near)
(E/f'candidates/fit-{rev}{suffix}-distance.json').write_text(json.dumps({'nativeObjects':len(native),'referenceSupplement':supplement,'contactPasses':contactPasses,'nearestDistanceP50M':float(np.median(near[:,0])),'nearestDistanceP95M':float(np.percentile(near[:,0],95)),'negativeNormalDistances':int((near[:,1]<-.0005).sum()),'maximumDeformationFromCageM':float(np.linalg.norm(v-original,axis=1).max()),'regionStatistics':{r:{'vertices':int(sum(x==r for x in region)),'distanceP50M':float(np.median(near[np.array(region)==r,0])),'distanceP95M':float(np.percentile(near[np.array(region)==r,0],95)),'negativeNormalDistances':int((near[np.array(region)==r,1]<-.0005).sum())} for r in sorted(set(region))},'limitations':'nearest normal sign is not a closed-volume containment proof; contact correction is a geometric constraint after anatomical cage'},indent=2))
bpy.ops.import_scene.gltf(filepath=str(O/f'skin-candidate-{rev}.glb'))
skin=next(o for o in bpy.context.selected_objects if o.type=='MESH');skin.data.materials[0].diffuse_color=(.57,.37,.24,1)
print('EMITTED_GLB_IMPORTED',len(skin.data.vertices),len(skin.data.polygons),flush=True)
# native scene comparison below is exact fixed source geometry
nat=mesh('ZA-fixed-reference',npv,npt,(.7,.15,.1,1))
guide_path=os.environ.get('AT10_SKIN_GUIDES')
if guide_path:
    guides=json.loads((R/guide_path).read_text())['guides']
    def line_object(name,points,color,radius):
        curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.bevel_depth=radius;curve.bevel_resolution=1
        spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
        for p,q in zip(spline.points,points):p.co=(float(q[0]),float(-q[2]),float(q[1]),1)
        obj=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(obj)
        material=bpy.data.materials.new(name);material.diffuse_color=color;obj.data.materials.append(material)
    for i,g in enumerate(guides):
        point=np.array(g['sourceWeights'])@v[np.array(g['sourceLogicalVertices'])]
        target=np.array(g['targetPointM'])
        line_object('source-native-guide-'+str(i),[point,target],(.9,.9,.2,1),.00025)
    for digits in [[1,2],[2,3],[3,4],[4,5]]:
        for branch in ['dorsal','plantar']:
            group=[g for g in guides if g['betweenDigits']==digits and g['branch']==branch]
            line_object('source-chart-'+str(digits)+branch,[np.array(g['sourceWeights'])@v[np.array(g['sourceLogicalVertices'])] for g in group],(.1,1,.25,1),.00055)
            line_object('native-chart-'+str(digits)+branch,[g['targetPointM'] for g in group],(.05,.4,1,1),.00055)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=900;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.3;scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.world.color=(.055,.065,.08)
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.render.image_settings.file_format='PNG'
camera=bpy.data.objects.new('Inspection-camera',bpy.data.cameras.new('Inspection-camera'));scene.collection.objects.link(camera);scene.camera=camera;camera.data.type='ORTHO'
def render(label,centre,direction,scale,shown):
    if tag:label=label.replace('emitted-'+rev,'emitted-'+rev+suffix,1)
    c=Vector((centre[0],-centre[2],centre[1]));dr=Vector((direction[0],-direction[2],direction[1]));camera.location=c+dr.normalized()*3;camera.rotation_euler=(c-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
    skin.hide_render=shown=='native';nat.hide_render=shown=='skin';scene.render.filepath=str(E/'screens'/f'{label}-{shown}.png');bpy.ops.render.render(write_still=True)
for shown in ([] if '--only' in sys.argv else ['skin','overlay']):
    for label,dr in [('front',[0,0,1]),('back',[0,0,-1]),('left',[1,0,0]),('right',[-1,0,0])]:render('emitted-'+rev+'-'+label,[0,.86,0],dr,1.90,shown)
for label,centre,dr,scale in [
 ('face',[0,1.6,0],[0,0,1],.27),('ear-left',[.08,1.585,0],[1,0,.4],.15),('ear-right',[-.08,1.585,0],[-1,0,.4],.15),('neck-back',[0,1.49,-.025],[0,0,-1],.27),('shoulder',[.12,1.36,0],[.3,0,1],.35),
 ('torso',[0,1.17,0],[0,0,1],.65),('sacrum-back',[0,1.11,0],[0,0,-1],.7),('groin',[0,.86,0],[0,0,1],.35),
 ('hand-left',[.28,.8,.06],[0,0,1],.2),('hand-right',[-.28,.8,.06],[0,0,1],.2),('knees',[0,.44,0],[0,0,1],.33),
 ('feet',[0,.045,.05],[0,.7,1],.3),('sole-left',[.09,.025,.04],[0,-1,0],.27),('sole-right',[-.09,.025,.04],[0,-1,0],.27),('palm-left',[.28,.8,.06],[0,0,-1],.2),('palm-right',[-.28,.8,.06],[0,0,-1],.2),('elbow-left',[.22,1.1,0],[.3,0,1],.24),('elbow-right',[-.22,1.1,0],[-.3,0,1],.24),('perineum',[0,.8,0],[0,-1,.3],.28)]:
    if '--only' in sys.argv and label not in sys.argv[sys.argv.index('--only')+1].split(','):continue
    render('emitted-'+rev+'-'+label,centre,dr,scale,'skin');render('emitted-'+rev+'-'+label,centre,dr,scale,'overlay')
if '--whole-back' in sys.argv:
    for shown in ['skin','overlay']:render('emitted-'+rev+'-whole-back',[0,.86,0],[0,0,-1],1.9,shown)
print('QA_RENDERS_DONE',flush=True)
