"""Native source inspection and explicit engineering masks for passive latissimus.

The old family carried this broad muscle rigidly with the arm. Hold the lower/
medial native origin region and follow its observed humeral end instead. These
are authored surface masks, not measured attachment footprints.
"""
import pathlib,sys,json,numpy as np
from PIL import Image,ImageDraw
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent
sys.path.insert(0,str(R/'work/tools'))
from author_source_surface_motion import source_geometry
from t66_contact_correctives import nearest_surface
src={r['sourceKey']:r for r in json.loads((R/'atlas-data/source-cache/datasets/za/compiled/manifest.json').read_text())['instances']};byname={r['name']:r for r in src.values()};fields=[]
for side in ['left','right']:
 row=byname['Latissimus dorsi muscle.'+side[0]];key=row['sourceKey'];*_,tri,M,w=source_geometry(row,'overview');h=byname['Humerus.'+side[0]];*_,ht,hM,hw=source_geometry(h,'overview')
 distance=np.linalg.norm(w-nearest_surface(w,hw,ht),axis=1);moving=np.argsort(distance)[:max(6,len(w)//40)].tolist()
 # Broad axial/lower source edge, inspected below, is an engineering fixation
 # region. Its exact physiological footprint is expressly not asserted.
 fixed=np.flatnonzero((w[:,1]<=np.quantile(w[:,1],.25)) | (np.abs(w[:,0])<=np.quantile(np.abs(w[:,0]),.18))).tolist();fixed=[v for v in fixed if v not in moving]
 edges=np.unique(np.sort(np.r_[tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]],axis=1),axis=0);ew=1/np.maximum(np.linalg.norm(w[edges[:,0]]-w[edges[:,1]],axis=1),1e-8);degree=np.bincount(edges.ravel(),weights=np.repeat(ew,2),minlength=len(w));weights=np.clip((w[:,1]-w[:,1].min())/np.ptp(w[:,1]),0,1)*.5;weights[fixed]=0;weights[moving]=1
 for _ in range(2000):
  sums=np.zeros(len(w));np.add.at(sums,edges[:,0],ew*weights[edges[:,1]]);np.add.at(sums,edges[:,1],ew*weights[edges[:,0]]);weights=.5*weights+.5*sums/np.maximum(degree,1);weights[fixed]=0;weights[moving]=1
 im=Image.new('RGB',(1000,1000),'white');dr=ImageDraw.Draw(im);lo=w[:,[0,1]].min(0);scale=820/max(np.ptp(w[:,0]),np.ptp(w[:,1]));xy=(w[:,[0,1]]-lo)*scale;xy[:,0]+=80;xy[:,1]=930-xy[:,1]
 for t in tri:dr.line([tuple(xy[v]) for v in [*t,t[0]]],fill=(170,170,170),width=1)
 for ids,color in [(fixed,'blue'),(moving,'green')]:
  for v in ids:dr.ellipse((*tuple(xy[v]-3),*tuple(xy[v]+3)),fill=color)
 dr.text((20,20),side+' native passive latissimus / blue held axial-lower mask / green humeral mask',fill='black');im.save(O/('latissimus-native-mask-'+side+'.png'))
 fields.append({'sourceKey':key,'side':side,'lod':'overview','role':'deforming_passive_surface','weights':weights.tolist(),'fixedVertexIndices':fixed,'movingVertexIndices':moving,'fixedBoneKeys':[byname['Vertebra T8']['sourceKey'],byname['Vertebra T9']['sourceKey']],'movingBoneKeys':[h['sourceKey']],'contactWeightPolicy':'source-phase-contact-and-shape-feasible-weight-fields','sourceBounds':[w.min(0).tolist(),w.max(0).tolist()],'humeralMaskNearestDistanceMetres':[float(distance[moving].min()),float(distance[moving].max())],'measuredAttachmentFootprints':False,'anatomicalMotorRoleClaimed':False})
(O/'latissimus-passive-source-fields.json').write_text(json.dumps(fields,ensure_ascii=False,indent=2)+'\n');print([(r['side'],len(r['weights']),len(r['fixedVertexIndices']),len(r['movingVertexIndices'])) for r in fields])
