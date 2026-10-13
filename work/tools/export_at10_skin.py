"""Deterministic offline candidate GLB with complete OBJ corner/topology correspondence."""
from pathlib import Path
import os,json,hashlib,struct,numpy as np
R=Path(__file__).resolve().parents[2];E=Path(os.environ.get('AT10_SKIN_EVIDENCE',str(R/'work/evidence/AT10/2026-10-13-skin-fit-r1')));O=Path(os.environ.get('AT10_SKIN_ARTIFACTS',str(R/'atlas-data/anatomy/skin/at10-fit-r1')));O.mkdir(parents=True,exist_ok=True)
sha=lambda x:hashlib.sha256(x).hexdigest()
d=json.loads((E/'candidates/fit-r9.json').read_text());v=np.array(d['positions'],dtype='<f4');uv=np.array(d['uv'],dtype='<f4');faces=d['faces'];tri=[];triangleMapping=[]
for f in faces:
    x=f['derivedVertices']
    for i in range(1,len(x)-1):tri.append([x[0],x[i],x[i+1]]);triangleMapping.append({'sourceFace':f['sourceFace'],'sourceCorners':[0,i,i+1]})
t=np.array(tri,dtype='<u4');n=np.zeros_like(v)
for a,b,c in t:
    normal=np.cross(v[b]-v[a],v[c]-v[a]);n[[a,b,c]]+=normal
norm=np.linalg.norm(n,axis=1);n/=np.maximum(norm,1e-12)[:,None]
# Split only the original OBJ UV seams; logical vertices and triangles remain canonical.
lookup={};positions=[];normals=[];tex=[];indices=[];emitted=[];cursor=0
for f in faces:
    corner=[]
    for old,vi,ui in zip(f['v'],f['derivedVertices'],f['uv']):
        key=(vi,ui)
        if key not in lookup:
            lookup[key]=len(positions);positions.append(v[vi]);normals.append(n[vi]);tex.append(uv[ui]);emitted.append({'sourceVertex':old,'logicalVertex':vi,'sourceUv':ui})
        corner.append(lookup[key])
    for j in range(1,len(corner)-1):indices.extend([corner[0],corner[j],corner[j+1]])
arrays=[np.array(positions,dtype='<f4'),np.array(normals,dtype='<f4'),np.array(tex,dtype='<f4'),np.array(indices,dtype='<u2')];buffer=b'';views=[];accessors=[]
for i,a in enumerate(arrays):
    buffer+=b'\0'*(-len(buffer)%4);views.append({'buffer':0,'byteOffset':len(buffer),'byteLength':a.nbytes,'target':34963 if i==3 else 34962});buffer+=a.tobytes();ac={'bufferView':i,'componentType':5123 if i==3 else 5126,'count':len(a),'type':['VEC3','VEC3','VEC2','SCALAR'][i]}
    if i==0:ac.update(min=a.min(0).tolist(),max=a.max(0).tolist())
    accessors.append(ac)
j={'asset':{'version':'2.0','generator':'HUMAN ATLAS AT10 offline candidate exporter','copyright':'MakeHuman core assets CC0-1.0; fitted candidate not validated'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':'MakeHuman_AT10_skin_fit_candidate_r9','mesh':0,'extras':{'unit':'m','frame':'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR','poseId':'za-c7010a9-9f08a17ea011-frame0-static','fitAcceptancePassed':False,'learnerEligible':False}}],'meshes':[{'primitives':[{'attributes':{'POSITION':0,'NORMAL':1,'TEXCOORD_0':2},'indices':3,'material':0,'mode':4}]}],'materials':[{'name':'educational-skin-candidate','pbrMetallicRoughness':{'baseColorFactor':[.57,.37,.24,1],'metallicFactor':0,'roughnessFactor':.82},'doubleSided':False}],'buffers':[{'byteLength':len(buffer)}],'bufferViews':views,'accessors':accessors}
jb=json.dumps(j,separators=(',',':')).encode();jb+=b' '*(-len(jb)%4);buffer+=b'\0'*(-len(buffer)%4);out=struct.pack('<III',0x46546c67,2,28+len(jb)+len(buffer))+struct.pack('<II',len(jb),0x4e4f534a)+jb+struct.pack('<II',len(buffer),0x004e4942)+buffer
(O/'skin-candidate-r9.glb').write_bytes(out)
mapping={'schemaVersion':1,'originalSource':'base.obj@a8bc2d54ff0ac92e78ff71431b1023eda42bf482','sourceToMetreScale':.1,'sourceToDerivedAxes':'identity XYZ: +X anatomical left, +Y head, +Z anterior; checked independent joint-l/r groups','derivedWorldTransform':'identity in GLB, source dm conversion already consumed','blenderInspectionTransform':'[x,-z,y] only for Blender draw/import; inverse glTF y-up conversion, not another world-scale','originalVertexIds':d['originalVertexIds'],'logicalTriangles':tri,'triangleMapping':triangleMapping,'emittedVertices':emitted,'faceCornerSourceUvIds':[f['uv'] for f in faces],'sourceFaceIds':[f['sourceFace'] for f in faces],'helperExported':False,'uvPolicy':'original face corner vt indices and values retained; seam split only','normalPolicy':'area weighted smooth normals recomputed from derived canonical topology','sourceInputHashes':d['inputHashes'],'canonicalTopologySha256':sha(np.array(d['originalVertexIds'],dtype='<u4').tobytes()+t.tobytes()),'logicalPositionSha256':sha(v.tobytes()),'glbSha256':sha(out),'acceptancePassed':False}
(O/'source-to-derived-r9.json').write_text(json.dumps(mapping,separators=(',',':'))+'\n')
area=np.linalg.norm(np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]]),axis=1)*.5
cost={'glbBytes':len(out),'logicalVertices':len(v),'emittedVertices':len(positions),'sourceBodyQuads':len(faces),'triangles':len(t),'decodedGpuGeometryBytes':sum(a.nbytes for a in arrays),'materialCount':1,'textureBytes':0,'bufferCount':len(arrays),'degenerateTrianglesBelow1e-12M2':int((area<1e-12).sum()),'boundsM':[v.min(0).tolist(),v.max(0).tolist()],'sha256':sha(out),'topologySha256':mapping['canonicalTopologySha256'],'existingBudgetsChanged':False,'runtimeCostMeasured':False,'runtimeResidentBytes':0,'costKind':'exact emitted buffers; skin-runtime not implemented','perAsset8MiBPassed':len(out)<8*1024**2}
(O/'cost-r9.json').write_text(json.dumps(cost,indent=2)+'\n');print(json.dumps(cost))
