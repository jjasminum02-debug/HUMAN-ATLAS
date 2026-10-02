#!/usr/bin/env python3
"""Compile the full evaluated peripheral source set; preserve historical T61/T63 records."""
import hashlib,importlib.util,json,re,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT='work/evidence/T66/implementation-2026-10-02'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads((ROOT/p).read_text())
def save(p,v):
    f=ROOT/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def integral(v):
    if isinstance(v,list):return [integral(x) for x in v]
    return int(v) if isinstance(v,float) and v.is_integer() else v

def build():
    spec=importlib.util.spec_from_file_location('pack',ROOT/'atlas-data/tools/datasets/pack.py');pack=importlib.util.module_from_spec(spec);spec.loader.exec_module(pack)
    evaluated=read(OUT+'/nerve-evaluated-surfaces.json');inputs=read(OUT+'/nerve-export-input.json');sourceBy={r['sourceObjectId']:r for r in inputs['rows']}
    registry=read('atlas-data/overlays/nerve-support-t63.json');oldBy={r['sourceObjectId']:r for r in registry['instances']}
    pose='za-c7010a9-9f08a17ea011-frame0-static';identity=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
    proofpath=OUT+'/nerve-evaluated-surfaces.json';proofhash=sha((ROOT/proofpath).read_bytes())
    rawpath='work/evidence/T98/blender-raw-object-inventory.json';rawhash=sha((ROOT/rawpath).read_bytes())
    resources={};instances=[];rows=[];rejected=[]
    skeleton=[r for r in read('atlas-data/overlays/za-local-integration.json')['objects'] if r['kind']=='bone' and r['localDisplayEligible'] and not r['hardHoldReasons']]
    regionContexts=[]
    for row in evaluated['rows']:
        source=sourceBy[row['sourceObjectId']];sid='za-c7010a9:raw:'+row['sourceObjectId'];row={**row,'instanceId':sid}
        if not row['sideBoundsAgree'] or not all(math.isfinite(v) for b in row['bounds'] for v in b):
            rejected.append({'id':sid,'reason':'actual geometry side/frame mismatch'});continue
        p=ROOT/row['path'];assert sha(p.read_bytes())==row['sha256'];key=row['sourceKey'];c=row['sourceToAtlas']
        resources[key]={**{k:row[k] for k in ['sha256','vertices','triangles','geometryBytes']},'path':str(p)}
        lod={k:row[k] for k in ['vertices','triangles','geometryBytes']};lod['resource']=key
        overview=row['overview'];op=ROOT/overview['path'];assert sha(op.read_bytes())==overview['sha256']
        okey=key+'-overview'
        resources[okey]={**{k:overview[k] for k in ['sha256','vertices','triangles','geometryBytes']},'path':str(op)}
        olod={k:overview[k] for k in ['vertices','triangles','geometryBytes']};olod['resource']=okey
        instances.append({'sourceKey':key,'sourceName':row['name'],'kind':'nerve_surface','matrix':[c[col+rr*4] for col in range(4) for rr in range(4)],
            'lods':{'overview':olod,'detail':lod},'sourceNamespace':'za-c7010a9','geometrySpace':'source_local','canonicalConceptId':None,'learnerBinding':'source_only_unbound','defaultLearnerVisible':False,
            'appDisplayRights':'held_not_approved_by_this_task','publicRedistribution':'held','humanReview':'not_performed','sourceHiddenStatePreserved':{'hideRender':row['hideRender'],'hideViewport':row['hideViewport']}})
        native=re.sub(r'\.[lr]$','',row['name']);collections=set(source['collections'])
        regions=[]
        # Source collection context, not asserted full anatomical course extent.
        if 'Neck' in collections:regions.append('neck')
        if any('upper limb' in t.lower() for t in collections):regions+=['shoulder-scapular','upper-limb']
        if any('lower limb' in t.lower() for t in collections):regions+=['gluteal-hip','thigh','leg','foot']
        if 'Trunk' in collections:regions+=['back','thorax','abdomen-lumbar','pelvis-perineum']
        # Region-list presentation comes from actual source-space overlap with
        # existing regional bone contexts, not the entire upper/lower limb collection.
        # This is a coarse display context, not a clinical course/entrapment coordinate.
        contextual=[]
        for b in skeleton:
            if b['side'] not in [row['side'],None,'midline']:continue
            if all(row['bounds'][0][i]<=b['bounds'][1][i]+.015 and row['bounds'][1][i]>=b['bounds'][0][i]-.015 for i in range(3)):
                contextual.append(b)
        if contextual:regions=sorted({region for b in contextual for region in b['regionIds']})
        if not regions:regions=['back']
        regionContexts.append({'sourceKey':key,'regionIds':regions,'boneContextKeys':[b['sourceKey'] for b in contextual],
            'meaning':'15mm expanded original bone bounds overlap, display context only; no full course extent or entrapment coordinate claim'})
        n=oldBy.get(row['sourceObjectId'])
        if n is None:
            scope='root' if 'root' in native.lower() else 'plexus' if 'plexus' in native.lower() else 'trunk' if 'trunk' in native.lower() else 'branch'
            n={'id':sid,'sourceNamespace':'za-c7010a9','sourceObjectId':row['sourceObjectId'],'conceptId':None,'side':row['side'],'scope':scope,
               'names':{'koTraditional':None,'koModern':None,'en':native},'regionIds':sorted(set(regions)),'identity':'verified_local','evidenceIds':[],
               'geometry':None,'localSelection':'text_only','hardHolds':[],'sourceOnly':True,'humanReview':'not_performed','publicRedistribution':'held'}
            registry['instances'].append(n)
        else:
            n['identity']='verified_local';n['side']=row['side'];n['hardHolds']=[];n['scope']='trunk' if n['scope']=='unresolved' else n['scope']
            n['regionIds']=sorted(set(regions))
        for predicate in ['identity','side','scope']:
            ev={'id':sid+':t66-'+predicate,'sourcePath':rawpath,'sourceSha256':rawhash,'locator':source['rawPointer']+'; exact original Curve name, source-declared .l/.r, peripheral Nerves collection; source-object scope only',
                'subjectId':sid,'predicate':predicate,'objectId':None,'status':'verified_local'}
            registry['evidence'].append(ev);n['evidenceIds'].append(ev['id'])
        g={'kind':'curve','assetPath':row['path'],'assetSha256':row['sha256'],'topologySha256':row['topologySha256'],'sourceNamespace':n['sourceNamespace'],
           'sourceFrameId':'ZA_RH_M_XLEFT_YPOSTERIOR_ZSUPERIOR','sourcePoseId':pose,'sourceUnit':'m','targetFrameId':'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR',
           'geometrySpace':'source_world','sourceObjectToWorld':identity,'sourceToAtlas':c,'transformKind':'same_source_axis_conversion','evidenceIds':[],'registrationEvidenceIds':[],'validatedPoseIds':[pose]}
        signature=json.dumps(integral([g[k] for k in ['assetSha256','topologySha256','sourceNamespace','sourceFrameId','sourcePoseId','sourceUnit','targetFrameId','geometrySpace','sourceObjectToWorld','sourceToAtlas','transformKind']]),separators=(',',':'))
        for predicate in ['frame','placement','pose']:
            ev={'id':sid+':t66-'+predicate,'sourcePath':proofpath,'sourceSha256':proofhash,'locator':'rows[sourceObjectId='+row['sourceObjectId']+']; original evaluated Curve at frame0, source-world bake and one axis conversion',
                'subjectId':sid,'predicate':predicate,'objectId':pose if predicate=='pose' else g['assetSha256'],'status':'verified_local'}
            if predicate=='frame':ev['value']=signature
            registry['evidence'].append(ev);g['evidenceIds'].append(ev['id'])
        n['geometry']=g;n['localSelection']='verified_geometry';rows.append(row)
    # Source tree hierarchy stays candidate until branch identity/continuity is independently checked.
    registry['contractRevision']='T66-source-native-static-course-2026-10-02'
    save('atlas-data/overlays/nerve-support-t66.json',registry)
    datasetPath='atlas-data/assets/derived-glb/za-nerve-t66/chunks/manifest.json'
    dataset=pack.compile_dataset({'namespace':'za-c7010a9','revision':'za-t66-peripheral-source-curves-v1','unit':'m','geometrySpace':'source_local','localOnly':True,'publicRedistribution':'held',
        'instances':instances,'resources':resources},ROOT/Path(datasetPath).parent)
    readme='work/evidence/T98/astra-resolution-2026-09-29/source-readme.md'
    rightsPath=OUT+'/nerve-local-use-rights.json'
    save(rightsPath,{'id':'ZA-t66-peripheral-local-prototype-2026-10-02','sourceSha256':evaluated['sourceSha256'],'sourceRevision':'c7010a903b75a2fd24a13b1c2c4c3546a9223780',
        'readme':{'path':readme,'sha256':sha((ROOT/readme).read_bytes())},'allowedSourceKeys':[r['sourceKey'] for r in rows],
        'exceptionReview':'Each evaluated object is an original bevelled peripheral Curve in source Nerves/Spinal nerves. Exact collections retained in evaluated proof. Cranial-nerve exception collections excluded. No inner-ear/white-matter/kidney geometry added. Pinned family local derivative permission only; original render-hidden flags retained. No public license grant.',
        'localUseRights':'supported_local_prototype','sourceOnly':True,'humanReview':'not_performed','publicRedistribution':'held'})
    paths={proofpath,OUT+'/nerve-export-input.json',rawpath,readme,'atlas-data/overlays/nerve-support-t66.json',rightsPath,datasetPath}
    paths.update(e['sourcePath'] for e in registry['evidence']);paths.update(r['path'] for r in rows)
    paths.update(r['overview']['path'] for r in rows)
    paths.update(str(Path(datasetPath).parent/(c['id']+'.glb')) for c in dataset['chunks'])
    save('atlas-data/manifests/nerve-scene-t66.json',{'schemaVersion':1,'revision':'nerve-scene-t66-v1','registryPath':'atlas-data/overlays/nerve-support-t66.json','datasetPath':datasetPath,'rightsPath':rightsPath,
        'inputSha256':{p:sha((ROOT/p).read_bytes()) for p in sorted(set(paths)|{'atlas-data/overlays/za-local-integration.json'})},'objects':[{k:r[k] for k in ['instanceId','sourceKey','bounds','name','path','sha256','topologySha256']} for r in rows]})
    save(OUT+'/nerve-production.json',{'registeredStaticSourceSurfaces':len(rows),'distinctNativeSourceNames':len({re.sub(r'\.[lr]$','',r['name']) for r in rows}),
        'independentAnatomicalNerveConceptCount':None,'metrics':dataset['metrics'],'rejected':rejected,'dynamicNervePoses':0,'entrapmentCoordinateBindings':0,
        'meaning':'Source-native static course observation; source label groups are not independent anatomical concept counts. Clinical course/entrapment text and source branch taxonomy remain independent.'})
    save(OUT+'/nerve-region-contexts.json',{'rows':regionContexts,'geometryUnchanged':True})
    print(json.dumps({'registeredStaticSourceSurfaces':len(rows),'metrics':dataset['metrics']}))

if __name__=='__main__':build()
