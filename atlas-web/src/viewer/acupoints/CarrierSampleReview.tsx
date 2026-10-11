import { useEffect, useRef, useState } from 'react';
import type { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter.ts';
import type { CarrierSample, CarrierFamily } from './carrierSample.ts';
import { CarrierSampleOverlay } from './CarrierSampleOverlay.ts';
import { loadCarrierSet } from './carrierLoader.ts';
import './carrierSample.css';

const familyLabels:Record<'sample'|'all'|CarrierFamily,string>={sample:'오른쪽 넙다리 표본',all:'전체 교육용 표본',trunk:'몸통',arm:'양팔',leg:'양다리',head:'머리·얼굴',hand:'양손·손가락',foot:'양발·발가락',nail:'손톱·발톱',oral:'혀 기준 표본',perineum:'회음 기준 표본'};
export default function CarrierSampleReview({adapter,onClose}:{adapter:DatasetSceneAdapter;onClose:()=>void}) {
  const [ready,setReady]=useState(false),[reference,setReference]=useState(false),[notice,setNotice]=useState('체표 표본 연결 중…');
  const [family,setFamily]=useState<'sample'|'all'|CarrierFamily>('sample');
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
    <label>검토 부위<select aria-label="체표 검토 부위" value={family} onChange={e=>setFamily(e.target.value as typeof family)}>{(Object.entries(familyLabels) as [typeof family,string][]).map(([value,label])=><option key={value} value={value}>{label}</option>)}</select></label>
    {ready&&<><p>{familyLabels[family]} · 정지 자세</p>{family==='head'||family==='oral'||family==='sample'?<button onClick={()=>overlay.current?.fit()}>표본 맞춤</button>:<><button onClick={()=>overlay.current?.fit('right')}>오른쪽 표본 맞춤</button><button onClick={()=>overlay.current?.fit('left')}>왼쪽 표본 맞춤</button></>}<button aria-pressed={reference} onClick={()=>{setReference(!reference);overlay.current?.showReference(!reference);}}>{reference?'교육용 제안 면 보기':'원본 기준 표본 비교'}</button><small>원본 구조를 기준으로 만든 교육용 면입니다. 피부 스캔이 아니며, 빈 구역과 실제 혈위는 미확정입니다.</small></>}
    {ready&&family==='oral'&&<small>혀 표본만 지원합니다. 잇몸·소대 점막 위치는 지원하지 않습니다.</small>}{ready&&family==='perineum'&&<small>회음 구역 기준 표본입니다. 피부·정확한 혈위는 지원하지 않습니다.</small>}
    {notice&&<p role="status">{notice}</p>}
  </aside>;
}
