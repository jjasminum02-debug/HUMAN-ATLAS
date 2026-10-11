import { useEffect, useRef, useState } from 'react';
import type { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter.ts';
import type { CarrierSample } from './carrierSample.ts';
import { CarrierSampleOverlay } from './CarrierSampleOverlay.ts';
import { loadCarrierSet } from './carrierLoader.ts';
import './carrierSample.css';

export default function CarrierSampleReview({adapter,onClose}:{adapter:DatasetSceneAdapter;onClose:()=>void}) {
  const [ready,setReady]=useState(false),[reference,setReference]=useState(false),[notice,setNotice]=useState('체표 표본 연결 중…');
  const [family,setFamily]=useState<'sample'|'all'|'trunk'|'arm'|'leg'>('sample');
  const overlay=useRef<CarrierSampleOverlay|null>(null);
  useEffect(()=>{
    let alive=true;const abort=new AbortController();
    setReady(false);setReference(false);setNotice('체표 부위를 연결하고 있어요…');
    const stop=(reason:string)=>{alive=false;abort.abort();overlay.current?.dispose();overlay.current=null;setReady(false);setNotice(reason);};
    const removeMotion=adapter.onSourceMotionStart(()=>stop('정지 자세에서 다시 열어 주세요.'));
    const removeSelection=adapter.onSourceSelectionChange(()=>stop('선택 또는 자세 변경으로 표본을 종료했습니다.'));
    const visibility=()=>{if(document.hidden)stop('화면 비활성화로 표본 연결을 종료했습니다.');};
    document.addEventListener('visibilitychange',visibility);visibility();
    void (async()=>{try{
      let samples:CarrierSample[],encodedBytes:number;
      if(family==='sample') {
        const {default:url}=await import('../../../../atlas-data/acupoints/carriers/za-thigh-sample.json?url');
        if(!alive)return;
        const response=await fetch(url,{signal:abort.signal});if(!response.ok)throw Error('체표 표본을 읽을 수 없습니다.');
        const bytes=await response.arrayBuffer();if(!alive)return;
        samples=[JSON.parse(new TextDecoder().decode(bytes)) as CarrierSample];encodedBytes=bytes.byteLength;
      } else {
        const d=adapter.resources.dataset;
        ({samples,encodedBytes}=await loadCarrierSet(family,{datasetRevision:d.revision,frameId:d.frameContract?.targetFrameId??'',unit:d.unit,poseId:d.frameContract?.staticReferencePose?.id??''},abort.signal,()=>!alive));
      }
      const created=await CarrierSampleOverlay.createMany(adapter,samples,encodedBytes,()=>!alive,stop);
      if(!alive){created.dispose();return;}
      overlay.current=created;setReady(true);setNotice('');
    }catch(error){if(alive)setNotice(error instanceof Error?error.message:'체표 표본 연결 실패');}})();
    return()=>{alive=false;abort.abort();document.removeEventListener('visibilitychange',visibility);removeMotion();removeSelection();overlay.current?.dispose();overlay.current=null;};
  },[adapter,family]);
  return <aside className="acupoint-entry carrier-sample-review" aria-label="체표 표본 검토">
    <header><strong>체표 표본</strong><button onClick={onClose}>표본 닫기</button></header>
    <label>검토 부위<select aria-label="체표 검토 부위" value={family} onChange={e=>setFamily(e.target.value as typeof family)}><option value="sample">오른쪽 넙다리 표본</option><option value="all">몸통·양팔·양다리</option><option value="trunk">몸통</option><option value="arm">양팔</option><option value="leg">양다리</option></select></label>
    {ready&&<><p>{family==='sample'?'오른쪽 중간 넙다리':family==='all'?'몸통·양팔·양다리':family==='trunk'?'몸통':family==='arm'?'양팔':'양다리'} · 정지 자세</p><button aria-pressed={reference} onClick={()=>{setReference(!reference);overlay.current?.showReference(!reference);}}>{reference?'교육용 제안 면 보기':'원본 기준 표본 비교'}</button><small>근막·근육·뼈 기준 교육용 면입니다. 피부 스캔이 아니며, 빈 구역과 실제 혈위는 미확정입니다.</small></>}
    {notice&&<p role="status">{notice}</p>}
  </aside>;
}
