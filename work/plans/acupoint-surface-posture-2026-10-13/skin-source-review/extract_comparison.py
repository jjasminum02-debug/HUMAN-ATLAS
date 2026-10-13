import bpy, json, pathlib, math
from mathutils import Vector
p=pathlib.Path(__import__('sys').argv[__import__('sys').argv.index('--')+1])
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
verts=[];faces=[];g=''
for l in (p/'base.obj').read_text().splitlines():
 if l.startswith('v '): verts.append(tuple(map(float,l.split()[1:4])))
 elif l.startswith('g '):g=l[2:]
 elif l.startswith('f ') and g=='body':faces.append([int(v.split('/')[0])-1 for v in l.split()[1:]])
# Core target comparison only; this is not a fitted anatomy carrier.
for l in (p/'makehuman-asian-male-young.target').read_text().splitlines():
 if not l.strip() or l.startswith('#'):continue
 q=l.split();i=int(q[0]);verts[i]=tuple(verts[i][k]+float(q[k+1]) for k in range(3))
used=sorted({i for f in faces for i in f});remap={v:i for i,v in enumerate(used)}
mesh=bpy.data.meshes.new('MakeHumanBody');mesh.from_pydata([(verts[i][0]*.1,-verts[i][2]*.1,verts[i][1]*.1) for i in used],[],[[remap[i] for i in f] for f in faces]);mesh.update()
a=bpy.data.objects.new('MakeHuman core plus one adult target',mesh);bpy.context.collection.objects.link(a)
with bpy.data.libraries.load(str(p/'MB-Lab-humanoid_library.blend'),link=False) as(src,dst):dst.objects=['MBLab_human_male']
b=dst.objects[0];bpy.context.collection.objects.link(b)
records=[]
for o in [a,b]:
 for m in list(o.modifiers):o.modifiers.remove(m)
 o.data.materials.clear();o.color=(.65,.48,.37,1)
 for f in o.data.polygons:f.use_smooth=True
 bounds=[o.matrix_world@Vector(c) for c in o.bound_box];lo=Vector(tuple(min(v[i] for v in bounds) for i in range(3)));hi=Vector(tuple(max(v[i] for v in bounds) for i in range(3)))
 h=hi.z-lo.z
 o.scale*=1.75/h;o.location=Vector((-((lo.x+hi.x)/2)*1.75/h,-((lo.y+hi.y)/2)*1.75/h,-lo.z*1.75/h))
 records.append({'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'triangles':sum(len(f.vertices)-2 for f in o.data.polygons) if all(len(f.vertices)>=3 for f in o.data.polygons) else None,'sourceBounds':[list(lo),list(hi)],'comparisonNormalization':'visual normalization to 1.75m; not source unit proof or ZA fitting'})

for i,o in enumerate([a,b]):
 d={'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices],'faces':[list(f.vertices) for f in o.data.polygons]}
 (p/f'mesh-{i}.json').write_text(json.dumps(d))
(p/'mesh-inspection.json').write_text(json.dumps(records,indent=2))
print(json.dumps(records))
