import { useEffect, useRef, useState } from 'react';
import type { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter.ts';
import { AcupunctureOverlay } from './AcupunctureOverlay.ts';
import type { Carrier, PointInstance } from './schema.ts';
import './review.css';
/** Explicit development entry, never imported in the production learner app. */
export default function AcupointReview({ adapter }: { adapter: DatasetSceneAdapter }) {
  const [active,setActive]=useState(false),[loading,setLoading]=useState(false),[selected,setSelected]=useState('LU1'),[carrier,setCarrier]=useState(false),[notice,setNotice]=useState('');
  const overlay=useRef<AcupunctureOverlay|null>(null),generation=useRef(0),request=useRef<AbortController|null>(null);
  const stop=(reason='')=>{generation.current++;request.current?.abort();overlay.current?.dispose(!reason);overlay.current=null;setActive(false);setLoading(false);setCarrier(false);setNotice(reason);};
  useEffect(()=>()=>{generation.current++;request.current?.abort();overlay.current?.dispose();overlay.current=null;},[adapter]);
  const start=async()=>{
    const token=++generation.current;request.current?.abort();const abort=new AbortController();request.current=abort;setLoading(true);setNotice('');
    try {
      const {default:url}=await import('../../../../work/evidence/acupoint-AC1/prototype.json?url');
      const response=await fetch(url,{signal:abort.signal});if(!response.ok)throw Error('체표 자료를 열 수 없습니다.');
      const bytes=await response.arrayBuffer();const data=JSON.parse(new TextDecoder().decode(bytes)) as {carrier:Carrier;instances:PointInstance[]};
      if(token!==generation.current)return;
      const created=await AcupunctureOverlay.create(adapter,data.carrier,data.instances,code=>{setSelected(code);overlay.current?.select(code);},reason=>stop(reason),bytes.byteLength);
      if(token!==generation.current){created.dispose();return;}
      overlay.current=created;created.select(selected);setActive(true);
    }catch(error){if(token===generation.current)setNotice(error instanceof Error?error.message:'체표 연결 실패');}
    finally{if(token===generation.current)setLoading(false);}
  };
  const names={LU1:'중부',LU9:'태연',LU11:'소상'};
  return <aside className="acupoint-review" aria-label="경혈 체표 검토">
    <button aria-pressed={active} onClick={()=>active||loading?stop():void start()}>{loading?'체표 연결 취소':active?'체표 검토 끄기':'경혈 체표 검토'}</button>
    {active&&<>
      <p>오른쪽 수태음폐경 · 위치 검토용 제안</p>
      <div role="group" aria-label="검토할 경혈">{(['LU1','LU9','LU11'] as const).map(code=><button key={code} aria-pressed={selected===code} onClick={()=>{setSelected(code);overlay.current?.select(code);}}>{names[code]} · {code}</button>)}</div>
      <div role="group" aria-label="혈위 검토 시점">{([['front','전면'],['oblique','사선'],['side','측면']] as const).map(([direction,name])=><button key={direction} onClick={()=>overlay.current?.focus(selected,direction)}>{name}</button>)}<button onClick={()=>overlay.current?.restoreCamera()}>이전 시점</button></div>
      <button aria-pressed={carrier} onClick={()=>{setCarrier(!carrier);overlay.current?.showCarrier(!carrier);}}>학습용 체표 패치</button>
      <p className="acupoint-limit">{selected==='LU1'?'첫째늑간·쇄골 아래 기준 / 비례촌과 체표 미확정':selected==='LU9'?'노뼈·주상골 기준 / 손목 주름·혈관·건 함요 미확정':'엄지 말절골·손톱 기준 / 요측 조갑각·손가락촌 미확정'}</p>
      <small>주황 점: 위치 미확정 제안. 청록 면: 근육·뼈 기준으로 작성한 대략적 체표이며 정확한 피부가 아닙니다.</small>
    </>}
    {notice&&<p role="status">{notice}</p>}
  </aside>;
}
