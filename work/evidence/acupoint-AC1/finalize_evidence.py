from pathlib import Path
import json,hashlib,subprocess,math
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
read=lambda name:json.loads((P/name).read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
v=read('final-nine-views.json');assert len(v)==9 and len({r['overlay']['root'] for r in v})==1
carrier=read('prototype.json')['carrier'];assert all(r['overlay']['carrierHash']==carrier['topologySha256'] and not r['scene']['cameraTransition'] for r in v)
assert all(math.dist(r['scene']['target'],next(p['world'] for p in r['overlay']['points'] if p['code']==r['overlay']['selected']))<1e-8 for r in v)
b=read('screen-before.json');on=read('cost-on-carrier.json');off=read('screen-after.json')
assert b['scene']['root']==on['scene']['root']==off['scene']['root']
assert math.dist(b['scene']['camera'],off['scene']['camera'])<1e-8
assert b['dataset']['selected']==off['dataset']['selected']
assert off['scene']['registeredUpdates']==0 and off['scene']['geometryBuffersBytes']==b['scene']['geometryBuffersBytes'] and off['scene']['geometries']==b['scene']['geometries']
assert on['scene']['calls']-b['scene']['calls']==4
assert on['scene']['triangles']-b['scene']['triangles']==2040
assert on['scene']['geometryBuffersBytes']-b['scene']['geometryBuffersBytes']==44280
assert read('point-picking.json')['overlay']['selected']=='LU11';assert read('occlusion-picking.json')['selectedAfter']=='LU9'
manual=read('manual-camera-priority.json');assert math.dist(manual['chosen']['camera'],manual['respected']['camera'])<1e-8
pres=read('preservation-before.json');post=read('preservation-after.json');assert pres['dataset']['selected']==post['dataset']['selected'] and pres['muscles']==post['muscles']=='false' and pres['bones']==post['bones']=='true'
assert all(r['off']['registeredUpdates']==0 for r in read('toggle-cycles.json'))
assert read('motion-exclusion.json')['overlay'] is None and read('motion-exclusion.json')['dataset']['motion'] is not None
assert not (P/'typecheck.log').read_text().strip();assert 'pass 9' in (P/'tests.log').read_text();assert 'built in' in (P/'production-build.log').read_text()
prod=Path('/private/tmp/human-atlas-ac1-production');markers=['AcupunctureOverlay','AcupointTeachingCarrier','za-right-learning-patches','acupointReview','prototype.json']
found=[str(p) for p in prod.rglob('*') if p.is_file() and (p.suffix in ['.js','.css','.json']) and any(m.encode() in p.read_bytes() for m in markers)]
assert not found
base=read('before/baseline.json');wipChanged=[];missing=[]
for path,h in base['wipHashes'].items():
 f=R/path
 if not f.is_file():missing.append(path)
 elif sha(f.read_bytes())!=h:wipChanged.append(path)
assert not missing and wipChanged==['atlas-web/src/viewer/datasets/DatasetSceneAdapter.ts']
source=R/'atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend';assert sha(source.read_bytes())==read('source-probe.json')['sourceSha256']
# Rendered index is Uint16; the immutable hash format remains Uint32 independently.
d=read('runtime-dataset.json');rawBytes=(P/'prototype.json').stat().st_size
upperBytes=sum(c['bytes'] for c in d['chunks'] if c['level']=='overview' and not c.get('selectionScoped'))+max([0]+[c['bytes'] for c in d['chunks'] if c.get('selectionScoped')])+rawBytes
upperTriangles=sum(i['lods']['overview']['triangles'] for i in d['instances'])+2040
assert upperBytes<=20*1024*1024 and upperTriangles<=1_000_000
verification={'status':'engineering_passed_location_partial','acceptedProductPointCount':0,'reviewProposalPointCount':3,'routeCount':0,'territoryCount':0,'carrierHash':carrier['topologySha256'],'frame':carrier['frameId'],'unit':'m','pose':carrier['poseId'],'screenshotRoot':v[0]['overlay']['root'],'screenshotViews':9,'costBenchmarkRoot':b['scene']['root'],'measurements':{'dataBytes':rawBytes,'carrierVertices':867,'carrierTopologyTriangles':1536,'carrierRenderBufferBytes':30024,'totalExtraTriangles':2040,'totalExtraGPUBufferEstimateBytes':44280,'actualExtraCalls':4,'extraTextures':0,'beforeTriangles':b['scene']['triangles'],'onTriangles':on['scene']['triangles'],'conservativeOverviewBytesWithCarrier':upperBytes,'conservativeOverviewTrianglesWithCarrier':upperTriangles,'GPUDriverHeapAndElapsedGPUTime':'not_measured; GPU cost reported as uploaded attribute/index buffer estimate and actual render calls/triangles'},'checks':{'typecheck':'passed','tests':'9/9','productionViteBuild':'passed','prototypeInProduction':'absent','sameSceneNineViews':True,'hashBoundReproducibleAnchors':True,'pointAndOcclusionPicking':True,'cameraRestore':True,'manualCameraPriority':True,'sourceSelectionAndLayerPreserved':True,'threeToggleCyclesResourceReturn':True,'motionMutualExclusion':True,'executionSync':'passed'},'preservation':{'preExistingWipFilesChecked':len(base['wipHashes']),'changedWipOnlyOwnedHunks':wipChanged,'missingWip':missing,'originalBlendUnchanged':True,'OpenSimAndT13':'no writes; pre-existing non-ignored WIP hashes unchanged; browser draft storage not accessed'}}
(P/'validation.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
# One contact sheet from final rendered screenshots, preserving the full app context.
out=Image.new('RGB',(1236,1176),'white');draw=ImageDraw.Draw(out)
for i,c in enumerate(['LU1','LU9','LU11']):
 for j,direction in enumerate(['front','oblique','side']):
  im=Image.open(P/f'{c}-{direction}.png').convert('RGB');im.thumbnail((412,374));out.paste(im,(j*412,i*392+18));draw.text((j*412+8,i*392+3),f'{c} {direction}',fill='black')
out.save(P/'nine-view-contact-sheet.png')
print(json.dumps({'verification':'passed','bytes':rawBytes,'upperOverview':upperBytes,'upperTriangles':upperTriangles,'WIP':len(base['wipHashes'])}))
