"""Common normalized-resource compiler: content-addressed bounded glTF chunks.
No Blender, anatomical naming, task chain, or display approval logic belongs here.
"""
import hashlib
import json
from pathlib import Path
import struct

MAX_CHUNK=8*1024*1024

def digest(data): return hashlib.sha256(data).hexdigest()
def unpack(data):
    magic,version,length=struct.unpack_from('<III',data)
    assert magic==0x46546c67 and version==2 and length==len(data)
    size,kind=struct.unpack_from('<I4s',data,12); assert kind==b'JSON'
    doc=json.loads(data[20:20+size]); offset=20+size
    size,kind=struct.unpack_from('<I4s',data,offset); assert kind==b'BIN\0'
    return doc,data[offset+8:offset+8+size]
def pack(resources):
    doc={'asset':{'version':'2.0','generator':'HUMAN ATLAS dataset compiler'},'scene':0,'scenes':[{'nodes':[]}],
         'nodes':[],'meshes':[],'accessors':[],'bufferViews':[],'buffers':[]}
    binary=bytearray()
    for key,data in resources:
        source,blob=unpack(data); vo=len(doc['bufferViews']); ao=len(doc['accessors'])
        for v in source['bufferViews']: doc['bufferViews'].append({**v,'byteOffset':v.get('byteOffset',0)+len(binary)})
        for a in source['accessors']: doc['accessors'].append({**a,'bufferView':a['bufferView']+vo})
        primitive=source['meshes'][0]['primitives'][0]
        doc['meshes'].append({'name':key,'primitives':[{'attributes':{k:v+ao for k,v in primitive['attributes'].items()},'indices':primitive['indices']+ao}]})
        doc['scenes'][0]['nodes'].append(len(doc['nodes']))
        doc['nodes'].append({'name':key,'mesh':len(doc['meshes'])-1,'extras':{'resourceKey':key}})
        binary.extend(blob); binary.extend(b'\0'*((-len(binary))%4))
    doc['buffers']=[{'byteLength':len(binary)}]
    j=json.dumps(doc,separators=(',',':')).encode(); j+=b' '*((-len(j))%4)
    return struct.pack('<III',0x46546c67,2,28+len(j)+len(binary))+struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(binary),b'BIN\0')+binary

def compile_dataset(adapter,out):
    """Adapter supplies independent instances, resources and source contracts."""
    out.mkdir(parents=True,exist_ok=True); chunks=[]; references={}
    for level in ['overview','detail']:
        # Shared resource goes in overview once; detail may refer to it as well.
        keys=sorted({i['lods'][level]['resource'] for i in adapter['instances']} - references.keys())
        batch=[]
        def emit_group(group):
            data=pack(group)
            if len(data)>MAX_CHUNK:
                if len(group)==1:raise ValueError('resource exceeds chunk budget: '+group[0][0])
                middle=len(group)//2
                emit_group(group[:middle]);emit_group(group[middle:]);return
            h=digest(data); (out/f'{h}.glb').write_bytes(data)
            chunks.append({'id':h,'url':f'/__atlas/datasets/{adapter["namespace"]}/{h}.glb','sha256':h,'bytes':len(data),'level':level,
                           'resources':[k for k,_ in group],'geometryBytes':sum(adapter['resources'][k]['geometryBytes'] for k,_ in group)})
            for k,_ in group: references[k]=h
        def flush():
            if batch:emit_group(batch)
            batch.clear()
        size=0
        for key in keys:
            r=adapter['resources'][key]; data=Path(r['path']).read_bytes(); assert digest(data)==r['sha256']
            # Individual GLB JSON overhead exceeds combined overhead; final size is still asserted.
            if batch and size+len(data)>MAX_CHUNK-4096: flush();size=0
            batch.append((key,data));size+=len(data)
        flush()
    instances=[]
    for instance in adapter['instances']:
        instances.append({**instance,'lods':{level:{**r,'chunk':references[r['resource']]} for level,r in instance['lods'].items()}})
    result={k:v for k,v in adapter.items() if k not in ['resources','instances']}
    result.update({'schemaVersion':1,'instances':instances,'chunks':chunks})
    result['resources']={k:{f:v for f,v in r.items() if f!='path'} for k,r in adapter['resources'].items()}
    result['metrics']={'overviewBytes':sum(c['bytes'] for c in chunks if c['level']=='overview'),
                       'overviewTriangles':sum(i['lods']['overview']['triangles'] for i in instances),
                       'overviewGeometryBytes':sum(c['geometryBytes'] for c in chunks if c['level']=='overview'),
                       'totalBytes':sum(c['bytes'] for c in chunks),'uniqueResources':len(references),'instances':len(instances)}
    result['budgetPass']=result['metrics']['overviewBytes']<=20*1024*1024 and result['metrics']['overviewTriangles']<=1000000 and result['metrics']['overviewGeometryBytes']<=96*1024*1024
    temporary=out/'manifest.tmp'
    temporary.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n')
    temporary.replace(out/'manifest.json')
    return result
