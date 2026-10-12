"""Compare actual Three loader world vertices with independent saved GLB replay."""
from pathlib import Path
import sys,json
import numpy as np
R=Path.cwd();E=Path(__file__).resolve().parent
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb,channel_data,node_positions
rows=[]
for side in ['left','right']:
    _,d,b=read_glb(R/f'atlas-data/assets/motion/mv2-q01-learning-r1-{side}/motion.glb');tracks=channel_data(d,b)
    samples=json.loads((E/f'loader-world/r9-real-loader-world-{side}.json').read_text());maximum=0
    for s in samples:
        expected=node_positions(d,b,tracks,47,s['seconds']);actual=np.asarray(s['positions'])
        maximum=max(maximum,float(np.linalg.norm(actual-expected,axis=1).max()))
    assert len(samples)==193 and maximum<1e-7
    rows.append({'side':side,'times':len(samples),'maximumWorldDifferenceMetres':maximum})
(E/'actual-independent-replay-r9.json').write_text(json.dumps({'passed':True,'rows':rows},indent=2)+'\n');print(rows)
