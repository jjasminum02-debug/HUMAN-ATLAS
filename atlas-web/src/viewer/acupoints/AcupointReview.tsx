import { useEffect, useRef, useState } from 'react';
import type { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter.ts';
import { AcupunctureOverlay } from './AcupunctureOverlay.ts';
import { LUNG_ORDER, LUNG_SECTIONS, sectionFor, type PointTour } from './tour.ts';
import type { Carrier, PointConcept, PointInstance, LearningSelection, ChannelRoute } from './schema.ts';
import './review.css';
type LearningData={usage:string;carrier:Carrier;instances:PointInstance[];concepts:(PointConcept&{landmarkLabel:string})[];route:ChannelRoute&{positions:number[];carrierHash:string}};
/** Review-only until exact surface placements are accepted; no fixture product projection. */
export default function AcupointReview({adapter,onClose}:{adapter:DatasetSceneAdapter;onClose:()=>void}) {
  const [loading,setLoading]=useState(true),[side,setSide]=useState<'right'|'left'>('right'),[selection,setSelection]=useState<LearningSelection>({kind:'acupoint',code:'LU1',side:'right'}),[data,setData]=useState<LearningData|null>(null),[notice,setNotice]=useState(''),[tour,setTour]=useState<PointTour['state']>('ready');
  const [carrierVisible,setCarrierVisible]=useState(false);
  const [reduced,setReduced]=useState(()=>window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  const overlay=useRef<AcupunctureOverlay|null>(null),generation=useRef(0),request=useRef<AbortController|null>(null);
  useEffect(()=>{const media=window.matchMedia('(prefers-reduced-motion: reduce)');const change=()=>{setReduced(media.matches);overlay.current?.setReducedMotion(media.matches);};media.addEventListener('change',change);return()=>media.removeEventListener('change',change);},[]);
  const selected=selection.kind==='acupoint'?selection.code:'LU1';
  const stop=(reason='')=>{generation.current++;request.current?.abort();overlay.current?.dispose(!reason);overlay.current=null;setData(null);setLoading(false);setNotice(reason);};
  useEffect(()=>{
    let alive=true;
    const token=++generation.current,abort=new AbortController();request.current=abort;setLoading(true);setCarrierVisible(false);setNotice('');setData(null);
    const pick=(code:string)=>{if(alive){setSelection({kind:'acupoint',code,side});overlay.current?.select(code);}};
    // Stop motion through its normal resource/pose restoration before loading a static carrier.
    adapter.restoreSourceMotion('acupoint-static-learning');
    const removeSelection=adapter.onSourceSelectionChange(()=>stop('해부 구조나 관찰 자세가 바뀌어 경혈 표시를 종료했습니다.'));
    const removeMotion=adapter.onSourceMotionStart(()=>{stop('움직임 시작으로 경혈 표시를 종료했습니다. 정지 자세에서 다시 열어 주세요.');});
    void (async()=>{try{
      const {default:url}=side==='right'?await import('../../../../work/evidence/acupoint-AC2/right-learning.json?url'):await import('../../../../work/evidence/acupoint-AC2/left-learning.json?url');
      if(token!==generation.current||!alive)return;
      const response=await fetch(url,{signal:abort.signal});if(!response.ok)throw Error('경혈 자료를 열 수 없습니다.');
      const bytes=await response.arrayBuffer(),next=JSON.parse(new TextDecoder().decode(bytes)) as LearningData;
      if(token!==generation.current||!alive)return;
      if(next.usage!=='development_review_only'||next.route.kind!=='surface_teaching'||next.route.carrierHash!==next.carrier.topologySha256||next.route.side!==side||next.instances.length!==11||next.route.teachingPointOrder.join()!==LUNG_ORDER.join())throw Error('경혈 학습 자료의 연결 기준이 다릅니다.');
      const created=await AcupunctureOverlay.create(adapter,next.carrier,next.instances,pick,reason=>stop(reason),bytes.byteLength,{route:next.route.positions,names:Object.fromEntries(next.concepts.map(p=>[p.code,p.nameKo])),changed:state=>{if(alive)setTour(state);},cancelled:()=>token!==generation.current||!alive});
      if(token!==generation.current||!alive){created.dispose(false);return;}
      overlay.current=created;created.setReducedMotion(reduced);setData(next);pick('LU1');created.overview();
    }catch(error){if(token===generation.current&&alive)setNotice(error instanceof Error?error.message:'경혈 연결 실패');}
    finally{if(token===generation.current&&alive)setLoading(false);}})();
    return()=>{alive=false;generation.current++;abort.abort();removeMotion();removeSelection();overlay.current?.dispose();overlay.current=null;};
  },[adapter,side]);
  const concept=data?.concepts.find(p=>p.code===selected),index=LUNG_ORDER.indexOf(selected);
  if(!data&&!loading&&notice)return <aside className="acupoint-entry" aria-label="경혈 안내"><button onClick={onClose}>경혈 안내 닫기</button><p role="status">{notice}</p></aside>;
  return <aside className="acupoint-review" data-active={Boolean(data)} aria-label="경혈 학습">
    <header><strong>수태음폐경</strong><button onClick={()=>{stop();onClose();}}>경혈 학습 닫기</button></header>
    <div role="group" aria-label="인체 좌우">{(['right','left'] as const).map(s=><button key={s} aria-pressed={side===s} onClick={()=>{if(s!==side){stop();setSide(s);}}}>{s==='right'?'오른쪽':'왼쪽'}</button>)}<button disabled={loading} aria-pressed={reduced} onClick={()=>{setReduced(!reduced);overlay.current?.setReducedMotion(!reduced);}}>이동 줄이기</button><button disabled={!data} aria-pressed={carrierVisible} onClick={()=>{setCarrierVisible(!carrierVisible);overlay.current?.showCarrier(!carrierVisible);}}>체표 제안 면</button></div>
    {loading?<p role="status">정지 체표 연결 중…</p>:data&&<>
      <div className="acupoint-codes" role="group" aria-label="폐경 경혈">{LUNG_ORDER.map(code=><button key={code} aria-label={`${code} ${data.concepts.find(p=>p.code===code)?.nameKo}`} aria-pressed={selected===code} onClick={()=>overlay.current?.choose(code)}>{code}</button>)}</div>
      <div className="acupoint-tour-controls" role="group" aria-label="경혈 따라보기 제어"><button onClick={()=>overlay.current?.play()}>경혈 따라보기</button><button disabled={tour!=='touring'} onClick={()=>overlay.current?.pause()}>정지</button><button disabled={index<=0} onClick={()=>overlay.current?.step(-1)}>이전</button><button disabled={index>=10} onClick={()=>overlay.current?.step(1)}>다음</button><button onClick={()=>overlay.current?.restoreCamera()}>복귀</button><button onClick={()=>overlay.current?.overview()}>전체 경로</button></div>
      <small className="acupoint-persistent-limit">체표 학습선 · 위치 미확정 · 교과서 설명 준비 중</small>
      <article className="acupoint-card" aria-label="선택 경혈 정보" aria-live="polite">
        <p className="acupoint-section">{LUNG_SECTIONS[sectionFor(selected)]?.name} · {index+1}/11 · {tour==='touring'?'따라보는 중':tour==='paused'?'정지':'선택 보기'}</p>
        <h3>{concept?.nameKo} · {selected}</h3><p>{concept?.romanization} · {side==='right'?'오른쪽':'왼쪽'} 수태음폐경</p>
        <p>{concept?.location?.text??'위치 설명 준비 중'}</p><p>기준 구조: {concept?.landmarkLabel}</p><p>교과서 설명 준비 중</p>
        <p className="acupoint-limit">기본 위치 설명과 모형 제안 위치는 구분됩니다. 점의 실제 혈위는 아직 미확정입니다.</p>
      </article>
      <small>점과 선은 정지 자세의 대략적 체표 학습 제안입니다. 전통적 전체 유주·분지·내행은 포함하지 않습니다.</small>
    </>}
    {notice&&<p role="status">{notice}</p>}
  </aside>;
}
