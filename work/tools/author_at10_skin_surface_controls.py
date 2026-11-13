"""Source-addressed local surface extrema controls on fixed native geometry.

These are dimensional teaching-model fit controls, never acupuncture semantics.
No candidate is modified by QA; all outputs are new revisions.
"""
from pathlib import Path
import argparse,json,numpy as np
R=Path(__file__).resolve().parents[2];p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--revision',default='r21');a=p.parse_args();E=R/a.evidence;B=R/'work/evidence/AT10/2026-10-13-skin-fit-r1'
d=json.loads((E/'candidates/fit-r19.json').read_text());src=np.array(d['sourceVertices']);v=np.array(d['positions']);before=v.copy();control={x['id']:x for x in json.loads((B/'native-controls-r2.json').read_text())['controls']};native=json.loads((B/'native-surfaces-r1.json').read_text());cohorts=[]
def smoothstep(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def gaussian(p,c,r):return np.exp(-np.sum((p[:,None,:]-c[None,:,:])**2,axis=2)/(2*r*r))
def incident_source(vi):return [f['sourceFace'] for f in d['faces'] if vi in f['derivedVertices']]
def cloud(side,terms):
 points=[];refs=[]
 for key,s in native.items():
  if s['side']!=side or not any(w in s['name'].lower() for w in terms):continue
  vertices=np.array(s['v']);tri=np.array(s['t']);centres=vertices[tri].mean(1)
  points.extend(centres);refs.extend([{'sourceKey':key,'nativeTriangle':i,'barycentric':[1/3]*3,'nativeWorldM':vertices[t].tolist()} for i,t in enumerate(tri)])
 return np.array(points),refs
def fit(ids,controls,reference,radius,reg):
 cs=np.array([c['source'] for c in controls]);ct=np.array([c['target'] for c in controls]);k=gaussian(cs,cs,radius);residual=ct-reference(cs);weights=np.linalg.solve(k+np.eye(len(k))*reg,residual);out=reference(src[ids])+gaussian(src[ids],cs,radius)@weights
 return out,float(np.linalg.norm(k@weights-residual,axis=1).max())
for side,letter,sign in [('left','l',1),('right','r',-1)]:
 # Source wrist/MCP planes identify homologous palm stations independently.
 fr=d['articulatedFrames'][side];sw=np.array(fr['sourceWrist']);tw=np.array(fr['targetWrist']);ps=np.array(fr['sourcePalmFrame']);pt=np.array(fr['targetPalmFrame']);scale=np.array(fr['palmScale']);scale[2]=1.25
 cs=[control[f'joint-{letter}-hand']]+[control[f'joint-{letter}-finger-{di}-{pa}'] for di in range(1,6) for pa in range(1,5)]
 sm=np.mean([control[f'joint-{letter}-finger-{di}-1']['source'] for di in range(2,6)],axis=0);tm=np.mean([control[f'joint-{letter}-finger-{di}-1']['target'] for di in range(2,6)],axis=0);sl=np.linalg.norm(sm-sw);tl=np.linalg.norm(tm-tw)
 nc,refs=cloud(side,['metacarpal','palmar','dorsal fascia of hand','common flexor tendon sheath','lumbrical muscles of hand']);sq=(src-sw)@ps;nq=(nc-tw)@pt
 for f in [.25,.55,.82]:
  sourceids=np.flatnonzero((src[:,0]*sign>.38)&(np.abs(sq[:,0]-f*sl)<.006));nativeids=np.flatnonzero((np.abs(nq[:,0]-f*tl)<.007)&(np.abs(nq[:,1])<.055))
  for direction in [-1,1]:
   si=int(sourceids[np.argmax(sq[sourceids,2]*direction)]);matchwidth=sq[si,1]*scale[1];nn=nativeids[np.abs(nq[nativeids,1]-matchwidth)<.016]
   if not len(nn):nn=nativeids
   ni=int(nn[np.argmax(nq[nn,2]*direction)]);allowance=pt[:,2]*direction*.004
   cs.append({'id':f'palm-surface-{side}-{f}-{direction}','source':src[si].tolist(),'target':(nc[ni]+allowance).tolist(),'sourceVertexIds':[d['originalVertexIds'][si]],'sourceObjFaces':incident_source(si),'nativeReferences':[refs[ni]],'authorship':'AI dimensional surface registration; observed facet centroid plus 4 mm skin allowance','anatomicalPointMeaning':False})
 ids=np.flatnonzero((src[:,0]*sign>.37)&(sq[:,0]>-.065));reference=lambda x:tw+((x-sw)@ps*scale)@pt.T;out,residual=fit(ids,cs,reference,.028,.002);w=smoothstep((sq[ids,0]+.065)/.045);v[ids]=v[ids]*(1-w[:,None])+out*w[:,None]
 cohorts.append({'id':'surface-hand-'+side,'controls':cs,'sourceVertices':np.array(d['originalVertexIds'])[ids].tolist(),'radiusM':.028,'regularization':.002,'residualMaxM':residual,'nativeFrame':pt.tolist(),'sourceFrame':ps.tolist(),'referenceScale':scale.tolist()})
 # Fixed foot facet centroids form five authored surface stations, keeping
 # plantar/dorsal and medial/lateral roles distinct from bone joint controls.
 ankle=control[f'joint-{letter}-ankle'];sw=np.array(ankle['source']);tw=np.array(ankle['target']);cs=[ankle]+[control[f'joint-{letter}-toe-{di}-{pa}'] for di in range(1,6) for pa in range(1,4)]
 nc,refs=cloud(side,['tibia','fibula','talus','calcaneus','metatarsal','cuneiform','cuboid','navicular','plantar','foot','calcaneal','retinaculum','tendon sheath','tibialis','fibularis']);ncids=np.flatnonzero((nc[:,1]<.115)&(nc[:,1]>.003)&(nc[:,0]*sign>.025)&(nc[:,0]*sign<.17))
 stations=[(-.030,-.078),(.004,-.041),(.043,-.007),(.083,.042),(.117,.076)]
 for sz,tz in stations:
  sourceids=np.flatnonzero((src[:,0]*sign>.08)&(src[:,0]*sign<.26)&(src[:,1]<-.725)&(np.abs(src[:,2]-sz)<.006));nativeids=ncids[np.abs(nc[ncids,2]-tz)<.006]
  for axis in [0,1]:
   for direction in [-1,1]:
    si=int(sourceids[np.argmax(src[sourceids,axis]*direction)]);ni=int(nativeids[np.argmax(nc[nativeids,axis]*direction)]);offset=np.eye(3)[axis]*direction*.004
    cs.append({'id':f'foot-surface-{side}-{sz}-{axis}-{direction}','source':src[si].tolist(),'target':(nc[ni]+offset).tolist(),'sourceVertexIds':[d['originalVertexIds'][si]],'sourceObjFaces':incident_source(si),'nativeReferences':[refs[ni]],'authorship':'AI dimensional foot station; actual facet centroid plus 4 mm allowance','anatomicalPointMeaning':False})
 ids=np.flatnonzero((src[:,0]*sign>.06)&(src[:,1]<-.68));reference=lambda x:tw+(x-sw)*[.78,.85,.92];out,residual=fit(ids,cs,reference,.038,.012);w=smoothstep((-.68-src[ids,1])/.055);v[ids]=v[ids]*(1-w[:,None])+out*w[:,None]
 cohorts.append({'id':'surface-foot-'+side,'controls':cs,'sourceVertices':np.array(d['originalVertexIds'])[ids].tolist(),'radiusM':.038,'regularization':.012,'residualMaxM':residual,'referenceScale':[.78,.85,.92],'stationsSourceNativeZ':stations})
d['positions']=v.tolist();d['candidateRevision']=a.revision;d['surfaceControlRecipe']=cohorts;d['fitAcceptancePassed']=False;d['learnerEligible']=False
(E/f'candidates/fit-{a.revision}.json').write_text(json.dumps(d,separators=(',',':')))
(E/f'surface-correspondence-{a.revision}.json').write_text(json.dumps({'cohorts':cohorts,'maxChangeFromR19M':float(np.linalg.norm(v-before,axis=1).max()),'nativeUnchanged':True},indent=2)+'\n')
print('SURFACE_FIT',a.revision,[(c['id'],c['residualMaxM']) for c in cohorts])
