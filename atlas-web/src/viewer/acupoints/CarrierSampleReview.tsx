import { useEffect, useRef, useState } from 'react';
import type { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter.ts';
import type { CarrierSample } from './carrierSample.ts';
import { CarrierSampleOverlay } from './CarrierSampleOverlay.ts';
import './carrierSample.css';

export default function CarrierSampleReview({adapter,onClose}:{adapter:DatasetSceneAdapter;onClose:()=>void}) {
  const [ready,setReady]=useState(false),[reference,setReference]=useState(false),[notice,setNotice]=useState('체표 표본 연결 중…');
  const overlay=useRef<CarrierSampleOverlay|null>(null);
  useEffect(()=>{
    let alive=true;const abort=new AbortController();
    const stop=(reason:string)=>{alive=false;abort.abort();overlay.current?.dispose();overlay.current=null;setReady(false);setNotice(reason);};
    const removeMotion=adapter.onSourceMotionStart(()=>stop('정지 자세에서 다시 열어 주세요.'));
    const removeSelection=adapter.onSourceSelectionChange(()=>stop('선택 또는 자세 변경으로 표본을 종료했습니다.'));
    const visibility=()=>{if(document.hidden)stop('화면 비활성화로 표본 연결을 종료했습니다.');};
    document.addEventListener('visibilitychange',visibility);visibility();
    void (async()=>{try{
      const {default:url}=await import('../../../../atlas-data/acupoints/carriers/za-thigh-sample.json?url');
      if(!alive)return;
      const response=await fetch(url,{signal:abort.signal});if(!response.ok)throw Error('체표 표본을 읽을 수 없습니다.');
      const bytes=await response.arrayBuffer();if(!alive)return;
      const data=JSON.parse(new TextDecoder().decode(bytes)) as CarrierSample;
      const created=await CarrierSampleOverlay.create(adapter,data,bytes.byteLength,()=>!alive,stop);
      if(!alive){created.dispose();return;}
      overlay.current=created;setReady(true);setNotice('');
    }catch(error){if(alive)setNotice(error instanceof Error?error.message:'체표 표본 연결 실패');}})();
    return()=>{alive=false;abort.abort();document.removeEventListener('visibilitychange',visibility);removeMotion();removeSelection();overlay.current?.dispose();overlay.current=null;};
  },[adapter]);
  return <aside className="acupoint-entry carrier-sample-review" aria-label="체표 표본 검토">
    <header><strong>체표 표본</strong><button onClick={onClose}>표본 닫기</button></header>
    {ready&&<><p>오른쪽 중간 넙다리 · 정지 자세</p><button aria-pressed={reference} onClick={()=>{setReference(!reference);overlay.current?.showReference(!reference);}}>{reference?'교육용 제안 면 보기':'원본 기준 표본 비교'}</button><small>근막·근육 기준의 교육용 면입니다. 실제 피부·점막과 혈위는 미확정입니다.</small></>}
    {notice&&<p role="status">{notice}</p>}
  </aside>;
}
