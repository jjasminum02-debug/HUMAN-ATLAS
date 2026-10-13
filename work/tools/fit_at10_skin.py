"""AT10 offline source-addressed skin cage. No source writes, downloads, or learner import."""
from pathlib import Path
import os,json, hashlib, importlib.util, argparse
import numpy as np
R=Path(__file__).resolve().parents[2]
E=Path(os.environ.get('AT10_SKIN_EVIDENCE',str(R/'work/evidence/AT10/2026-10-13-skin-fit-r1')))
S=R/'atlas-data/source-cache/datasets/skin-source-review-2026-10-13'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def source():
    pin=json.loads((R/'work/plans/acupoint-surface-posture-2026-10-13/skin-source-review/selection.json').read_text())
    assert pin['primary']['revision']=='a8bc2d54ff0ac92e78ff71431b1023eda42bf482'
    for name in ['base.obj','makehuman-asian-male-young.target','LICENSE.md','makehuman-LICENSE.ASSETS.md']:
        assert sha(S/name)==pin['files'][name]['sha256'],name
    vertices=[];uv=[];faces=[];groups={};g='';fi=0
    for line in (S/'base.obj').read_text().splitlines():
        a=line.split()
        if not a:continue
        if a[0]=='v':vertices.append(list(map(float,a[1:4])))
        elif a[0]=='vt':uv.append(list(map(float,a[1:3])))
        elif a[0]=='g':g=a[1]
        elif a[0]=='f':
            vs=[int(x.split('/')[0])-1 for x in a[1:]];us=[int(x.split('/')[1])-1 for x in a[1:]]
            groups.setdefault(g,set()).update(vs)
            if g=='body':faces.append({'sourceFace':fi,'v':vs,'uv':us})
            fi+=1
    v=np.array(vertices)
    for line in (S/'makehuman-asian-male-young.target').read_text().splitlines():
        a=line.split()
        if a and not a[0].startswith('#'):v[int(a[0])]+=np.array(list(map(float,a[1:4])))
    v*=.1 # official internal decimetres -> metres, exactly once
    ids=np.array(sorted(groups['body']));joint={k:v[list(x)].mean(0) for k,x in groups.items() if k.startswith('joint-')}
    return v,ids,uv,faces,joint,groups

def native_reader():
    s=importlib.util.spec_from_file_location('native',R/'work/evidence/AT8/2026-10-13-r1/native-reader.py')
    n=importlib.util.module_from_spec(s);s.loader.exec_module(n);return n

def prepare(revision='r2'):
    v,ids,uv,faces,joints,groups=source();n=native_reader();controls=[];surfaces={}
    def obs(name,side=None,axis=None,end=None,fraction=.10):
        key=n.find(name,side);p,t=n.world(key)
        sel=np.arange(len(p)) if axis is None else np.flatnonzero(p[:,axis]>=p[:,axis].max()-np.ptp(p[:,axis])*fraction) if end=='max' else np.flatnonzero(p[:,axis]<=p[:,axis].min()+np.ptp(p[:,axis])*fraction)
        return p[sel].mean(0),{'sourceKey':key,'name':name,'side':side,'operator':'vertex-mean' if axis is None else 'observed-cap-mean','axis':axis,'end':end,'fraction':fraction,'sourceVertexIds':sel.tolist()}
    def add(j,target,refs,role):
        controls.append({'id':j,'source':joints[j].tolist(),'target':np.asarray(target).tolist(),'sourceVertexIds':sorted(groups[j]),'nativeReferences':refs,'authorship':'AI-authored joint correspondence from observed source geometry','role':role})
    central=[('pelvis','Hip bone'),('spine-4','Vertebra L3'),('spine-3','Vertebra T12'),('spine-2','Vertebra T9'),('spine-1','Vertebra T5'),('neck','Vertebra C4')]
    for j,name in central:
        if name=='Hip bone':
            a,ra=obs('Femur','left',1,'max');b,rb=obs('Femur','right',1,'max');p=(a+b)/2;refs=[ra,rb]
        else:p,r=obs(name);refs=[r]
        add('joint-'+j,p,refs,'central skeletal cage (educational correspondence, not clinical landmark)')
    p,r=obs('Occipital bone');add('joint-head',[0,p[1],p[2]+.025],[r],'cranial cage centre offset, authored')
    a,ra=obs('Parietal bone','left',1,'max',.04);b,rb=obs('Parietal bone','right',1,'max',.04);add('joint-head-2',(a+b)/2+np.array([0,.006,0]),[ra,rb],'crown skin clearance 6mm')
    p,r=obs('Mandible',None,1,'min',.1);add('joint-jaw',[0,p[1],p[2]],[r],'jaw hinge cage educational correspondence')
    ords=['first','second','third','fourth','fifth'];fingers=['thumb','index','middle','ring','pinky']
    for side,letter in [('left','l'),('right','r')]:
        h,rh=obs('Humerus',side,1,'max',.08);el,re=obs('Humerus',side,1,'min',.09)
        wr,rw=obs('Radius',side,1,'min',.07);wu,ru=obs('Ulna',side,1,'min',.07)
        add(f'joint-{letter}-shoulder',h,[rh],'humeral proximal cap')
        add(f'joint-{letter}-elbow',el,[re],'humeral distal cap')
        add(f'joint-{letter}-hand',(wr+wu)/2,[rw,ru],'bilateral independently observed wrist')
        c,rc=obs('Clavicle',side,0,'min' if side=='left' else 'max',.10);add(f'joint-{letter}-clavicle',c,[rc],'clavicle medial cap')
        h,rh=obs('Femur',side,1,'max',.06);kn,rk=obs('Femur',side,1,'min',.06);an,ran=obs('Tibia',side,1,'min',.06)
        add(f'joint-{letter}-upper-leg',h,[rh],'femoral proximal cap')
        add(f'joint-{letter}-knee',kn,[rk],'femoral condylar cap')
        add(f'joint-{letter}-ankle',an,[ran],'tibial distal cap')
        for i,(o,f) in enumerate(zip(ords,fingers)):
            pref=f'joint-{letter}-finger-{i+1}-'
            # upstream helper labels use numeric finger index, verified below rather than guessed
            actual=[k for k in joints if k.startswith(pref)]
            if not actual:pref=f'joint-{letter}-{f}-'
            if not any(k.startswith(pref) for k in joints):raise ValueError((pref, [k for k in joints if letter+'-' in k and ('finger' in k or 'thumb' in k)]))
            mc,rm=obs(f'{o.title()} metacarpal bone',side,1,'max',.10)
            pp,rp=obs(f'Proximal phalanx of {o} finger of hand',side,1,'max',.1)
            pd,rd=obs(f'Proximal phalanx of {o} finger of hand',side,1,'min',.1)
            dp,rdp=obs(f'Distal phalanx of {o} finger of hand',side,1,'max',.1)
            dt,rt=obs(f'Distal phalanx of {o} finger of hand',side,1,'min',.05)
            targets=[mc,pp,pd,dt+np.array([0,-.002,0])] if i==0 else [pp,pd,dp,dt+np.array([0,-.002,0])]
            refs=[[rm],[rp],[rd],[rt]] if i==0 else [[rp],[rd],[rdp],[rt]]
            for k in range(4):add(pref+str(k+1),targets[k],refs[k],'individual finger rest-pose control; not mirrored')
        ft,rft=obs('First metatarsal bone',side);add(f'joint-{letter}-foot-1',ft,[rft],'forefoot cage')
        ft,rft=obs('Distal phalanx of second finger of foot',side,2,'max',.05);add(f'joint-{letter}-foot-2',ft,[rft],'forefoot tip cage')
        for i,o in enumerate(ords):
            pref=f'joint-{letter}-toe-{i+1}-'
            if not any(k.startswith(pref) for k in joints):continue
            pp,rp=obs(f'Proximal phalanx of {o} finger of foot',side,2,'min',.1)
            pd,rd=obs(f'Proximal phalanx of {o} finger of foot',side,2,'max',.1)
            dt,rt=obs(f'Distal phalanx of {o} finger of foot',side,2,'max',.05)
            for k,tar,rf in [(1,pp,rp),(2,pd,rd),(3,dt,rt)]:
                if pref+str(k) in joints:add(pref+str(k),tar,[rf],'individual toe skeletal cage')
        eye,reye=obs('Orbital part of orbicularis oculi',side);add(f'joint-{letter}-eye',eye-np.array([0,0,.018]),[reye],'orbital centre authored depth offset')
    # Observed source head surface features add shape controls; skeletal correspondence alone
    # does not determine forehead, chin, occiput or ear clearance.
    def surface_control(label,mask,axis,end,target,refs):
        cand=ids[mask(v[ids])]; extreme=(v[cand,axis].max() if end=='max' else v[cand,axis].min())
        chosen=cand[np.abs(v[cand,axis]-extreme)<.002]
        controls.append({'id':label,'source':v[chosen].mean(0).tolist(),'target':np.asarray(target).tolist(),'sourceVertexIds':chosen.tolist(),'nativeReferences':refs,'authorship':'AI-authored surface cage correspondence from observed source extrema','role':'regional adult head shape, not an acupoint'})
    a,ra=obs('Parietal bone','left',1,'max',.025);b,rb=obs('Parietal bone','right',1,'max',.025)
    surface_control('crown',lambda x:x[:,1]>.75,1,'max',(a+b)/2+[0,.006,0],[ra,rb])
    a,ra=obs('Occipital bone',None,2,'min',.045)
    surface_control('occiput',lambda x:(x[:,1]>.64)&(np.abs(x[:,0])<.04),2,'min',a+[0,0,-.006],[ra])
    a,ra=obs('Frontal bone',None,2,'max',.05)
    surface_control('forehead',lambda x:(x[:,1]>.745)&(np.abs(x[:,0])<.025),2,'max',[0,a[1]+.025,a[2]+.004],[ra])
    a,ra=obs('Mandible',None,1,'min',.06)
    surface_control('chin',lambda x:(x[:,1]>.59)&(x[:,1]<.65)&(x[:,2]>.10)&(np.abs(x[:,0])<.02),1,'min',[0,a[1]-.005,.083],[ra])
    a,ra=obs('Nasalis muscle','left',2,'max',.05);b,rb=obs('Nasalis muscle','right',2,'max',.05)
    surface_control('nose-tip',lambda x:(x[:,1]>.65)&(x[:,1]<.74)&(np.abs(x[:,0])<.02),2,'max',(a+b)/2+[0,0,.005],[ra,rb])
    # Geometry never transformed. Use original source-authoritative bone/muscle/tendon surfaces.
    for key,row in n.rows.items():
        name=row['names']['en'].lower()
        if any(term in name for term in ['muscle','bone','humerus','radius','ulna','femur','tibia','fibula','patella','sacrum','vertebra','clavicle','scapula','mandible','maxilla','tendon','fascia','calcaneus','talus','metacarpal','metatarsal','phalanx']):
            p,t=n.world(key);surfaces[key]={'name':row['names']['en'],'side':row['side'],'v':p.tolist(),'t':t.tolist()}
    # Reuse original face/ear probes (not another native investigation).
    d=json.loads((R/'work/evidence/AT8/2026-10-13-r1/evaluated-native-boundaries-r1.json').read_text())
    for o in d['objects']:
        if any(x in o['name'] for x in ['Helix','Lobule','Tragus','Auricular','Philtrum','Nasolabial']):
            key='ZA-original:'+o['name'];surfaces[key]={'name':o['name'],'side':'left' if o['name'].endswith('.l') else 'right','v':o['positions'],'t':o['indices'] if 'indices' in o else o['faces'] if 'faces' in o else o['triangles']}
    E.mkdir(parents=True,exist_ok=True);(E/'candidates').mkdir(exist_ok=True);(E/'screens').mkdir(exist_ok=True);(E/f'native-controls-{revision}.json').write_text(json.dumps({'controls':controls,'nativeInputHashes':n.inputs,'sourceFileHash':sha(S/'base.obj')},indent=2)+'\n')
    (E/'native-surfaces-r1.json').write_text(json.dumps(surfaces,separators=(',',':')))
    # thin-plate polyharmonic cage: matches skeletal controls, carries local source detail.
    a=np.array([c['source'] for c in controls]);b=np.array([c['target'] for c in controls]);p=np.c_[np.ones(len(a)),a]
    k=np.linalg.norm(a[:,None]-a[None,:],axis=2)
    coeff=np.linalg.solve(np.block([[k+np.eye(len(a))*1e-8,p],[p.T,np.zeros((4,4))]]),np.r_[b,np.zeros((4,3))])
    body=v[ids];fit=np.empty_like(body)
    for start in range(0,len(body),500):
        q=body[start:start+500];fit[start:start+500]=np.linalg.norm(q[:,None]-a[None,:],axis=2)@coeff[:len(a)]+np.c_[np.ones(len(q)),q]@coeff[len(a):]
    index={int(old):i for i,old in enumerate(ids)}
    payload={'sourceVertices':body.tolist(),'positions':fit.tolist(),'originalVertexIds':ids.tolist(),'uv':uv,'faces':[dict(f,derivedVertices=[index[x] for x in f['v']]) for f in faces],'sourceGroupCounts':{k:len(x) for k,x in groups.items()},'inputHashes':{str(p.relative_to(R)):sha(p) for p in [S/'base.obj',S/'makehuman-asian-male-young.target',S/'LICENSE.md',S/'makehuman-LICENSE.ASSETS.md']},'controlResidualMaxM':float(np.linalg.norm(k@coeff[:len(a)]+p@coeff[len(a):]-b,axis=1).max())}
    (E/f'candidates/cage-{revision}.json').write_text(json.dumps(payload,separators=(',',':')))
    print('prepared',len(controls),len(surfaces),len(body), 'bounds',fit.min(0),fit.max(0))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--revision',default='r2');prepare(parser.parse_args().revision)
