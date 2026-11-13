"""Proper hand plane and digit-local pose binding. Source thumb is not assigned to forearm."""
from pathlib import Path
import os,json,numpy as np
R=Path(__file__).resolve().parents[2];E=Path(os.environ.get('AT10_SKIN_EVIDENCE',str(R/'work/evidence/AT10/2026-10-13-skin-fit-r1')))
d=json.loads((E/'candidates/fit-r9-base.json').read_text());v=np.array(d['positions']);src=np.array(d['sourceVertices']);cage=np.array(json.loads((E/'candidates/cage-r2.json').read_text())['positions']);regions=np.array(d['vertexRegions']);ctrl={c['id']:c for c in json.loads((E/'native-controls-r2.json').read_text())['controls']};bindings=[]
head=regions=='head';center=np.array([0,1.595,-.012]);v[head]=(cage[head]-center)*[1.20,1.025,1.17]+center+[0,0,.004]
def frame(axis,normal):
    axis=axis/np.linalg.norm(axis);normal=normal-axis*np.dot(normal,axis);normal/=np.linalg.norm(normal);width=np.cross(normal,axis);return np.column_stack([axis,width,normal])
for side,letter in [('left','l'),('right','r')]:
    origin=f'joint-{letter}-hand';prefix=f'joint-{letter}-finger-';aS=np.array(ctrl[origin]['source']);aT=np.array(ctrl[origin]['target']);mS=np.mean([ctrl[prefix+f'{i}-1']['source'] for i in range(2,6)],axis=0);mT=np.mean([ctrl[prefix+f'{i}-1']['target'] for i in range(2,6)],axis=0);wS=np.array(ctrl[prefix+'2-1']['source'])-np.array(ctrl[prefix+'5-1']['source']);wT=np.array(ctrl[prefix+'2-1']['target'])-np.array(ctrl[prefix+'5-1']['target']);nS=np.cross(mS-aS,wS);nT=np.cross(mT-aT,wT);pS=frame(mS-aS,nS);pT=frame(mT-aT,nT);scales=np.array([np.linalg.norm(mT-aT)/np.linalg.norm(mS-aS),np.linalg.norm(wT)/np.linalg.norm(wS),1.2]);beams=[]
    for digit in range(1,6):
        chain=[prefix+f'{digit}-{i}' for i in range(1,5)]
        for part,(aa,bb) in enumerate(zip(chain,chain[1:])):
            sa=np.array(ctrl[aa]['source']);sb=np.array(ctrl[bb]['source']);ta=np.array(ctrl[aa]['target']);tb=np.array(ctrl[bb]['target']);ls=np.linalg.norm(sb-sa);lt=np.linalg.norm(tb-ta);fs=frame(sb-sa,nS);ft=frame(tb-ta,nT);assert np.linalg.det(ft@fs.T)>.999
            beams.append((sa,sb,ta,ls,lt,fs,ft,digit,part))
    for i in np.flatnonzero(regions=='hand-'+side):
        palm=aT+pT@((pS.T@(src[i]-aS))*scales);opts=[]
        for k,(sa,sb,ta,ls,lt,fs,ft,digit,part) in enumerate(beams):
            u=np.dot(src[i]-sa,sb-sa)/ls**2;dist=np.linalg.norm(src[i]-(sa+np.clip(u,0,1)*(sb-sa)));opts.append((dist,k,u))
        dist,k,u=min(opts);digit=beams[k][7];same=[x for x in opts if beams[x[1]][7]==digit];same=sorted(same)[:2];weights=np.array([(x[0]+.004)**-4 for x in same]);weights/=weights.sum();finger=np.zeros(3)
        for weight,(_,kk,uu) in zip(weights,same):
            sa,sb,ta,ls,lt,fs,ft,di,part=beams[kk];q=fs.T@(src[i]-sa);finger+=weight*(ta+ft@np.array([q[0]*lt/ls,q[1]*1.18,q[2]*1.18]))
        start=beams[k][0];base=np.array(ctrl[prefix+f'{digit}-1']['source']);axis=np.array(ctrl[prefix+f'{digit}-2']['source'])-base;progress=np.dot(src[i]-base,axis)/np.dot(axis,axis)
        blend=np.clip((progress+.15)/.55,0,1) if beams[k][8]==0 else 1.
        # wrist-to-palm transfer boundary is separately interpolated in its source joint plane.
        hprogress=np.dot(src[i]-aS,pS[:,0]);seam=np.clip((hprogress+.02)/.035,0,1)
        value=palm*(1-blend)+finger*blend;v[i]=cage[i]*(1-seam)+value*seam
        bindings.append({'derivedVertex':int(i),'sourceVertex':d['originalVertexIds'][i],'digit':digit,'bones':[x[1] for x in same],'weights':weights.tolist(),'fingerBlend':float(blend),'wristBlend':float(seam)})
    d.setdefault('articulatedFrames',{})[side]={'sourceWrist':aS.tolist(),'targetWrist':aT.tolist(),'sourcePalmFrame':pS.tolist(),'targetPalmFrame':pT.tolist(),'palmScale':scales.tolist(),'bones':[{'sourceStart':sa.tolist(),'sourceEnd':sb.tolist(),'targetStart':ta.tolist(),'sourceLength':ls,'targetLength':lt,'sourceFrame':fs.tolist(),'targetFrame':ft.tolist(),'digit':di,'part':part} for sa,sb,ta,ls,lt,fs,ft,di,part in beams]}
# Feet retain the conservative articulated regional envelope; no hand-style cage is used.
foot=np.array([r.startswith('foot') for r in regions]);v[foot,1]=np.maximum(v[foot,1],.001)
d['fitAcceptancePassed']=False;d['learnerEligible']=False;d['candidateRevision']='r9';d['positions']=v.tolist();d['extremityVertexBindings']=bindings;d['headRecipe']={'center':center.tolist(),'scale':[1.20,1.025,1.17],'offsetM':[0,0,.004],'scope':'local craniofacial cage; source relief preserved'}
(E/'candidates/fit-r9.json').write_text(json.dumps(d,separators=(',',':')));print('proper digit bind',len(bindings),v.min(0),v.max(0))
