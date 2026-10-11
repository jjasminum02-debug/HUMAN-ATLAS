import { useEffect, useRef, useState } from 'react';
import type { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter.ts';
import { AcupunctureOverlay } from './AcupunctureOverlay.ts';
import { LUNG_ORDER, LUNG_SECTIONS, sectionFor, type PointTour } from './tour.ts';
import type { Carrier, PointConcept, PointInstance, LearningSelection, ChannelRoute } from './schema.ts';
import { projectLearnerInstances } from './placementPolicy.ts';
import { loadLearningPackage } from './learningPackage.ts';
import './review.css';
type LegacyData={usage:string;carrier:Carrier;instances:PointInstance[];concepts:(PointConcept&{landmarkLabel:string})[];route:ChannelRoute&{positions:number[];carrierHash:string}};
type DisplayData={concepts:{code:string;nameKo:string;romanization:string;location:string;landmarkLabel:string}[];carriers:Carrier[];instances:PointInstance[];route:number[];encodedBytes:number;eligible:number;reasons:Record<string,string>};
/** Shared card/overlay lifecycle; DEV proposals and compiler-only learner positions have distinct inputs. */
export default function AcupointReview({adapter,onClose,mode='review'}:{adapter:DatasetSceneAdapter;onClose:()=>void;mode?:'learner'|'review'}) {
  const review=mode==='review';
  const [loading,setLoading]=useState(true),[side,setSide]=useState<'right'|'left'>('right'),[selection,setSelection]=useState<LearningSelection>({kind:'acupoint',code:'LU1',side:'right'}),[data,setData]=useState<DisplayData|null>(null),[notice,setNotice]=useState(''),[tour,setTour]=useState<PointTour['state']>('ready');
  const [carrierVisible,setCarrierVisible]=useState(false),[reduced,setReduced]=useState(()=>window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  const overlay=useRef<AcupunctureOverlay|null>(null),generation=useRef(0),request=useRef<AbortController|null>(null),returnCamera=useRef(adapter.scene.cameraState());
  useEffect(()=>{const media=window.matchMedia('(prefers-reduced-motion: reduce)');const change=()=>{setReduced(media.matches);overlay.current?.setReducedMotion(media.matches);};media.addEventListener('change',change);return()=>media.removeEventListener('change',change);},[]);
  const selected=selection.kind==='acupoint'?selection.code:'LU1';
  const stop=(reason='')=>{generation.current++;request.current?.abort();overlay.current?.dispose(!reason);overlay.current=null;delete adapter.scene.renderer.domElement.dataset.acupointProjection;setData(null);setLoading(false);setNotice(reason);};
  useEffect(()=>{
    let alive=true;const token=++generation.current,abort=new AbortController();request.current=abort;setLoading(true);setCarrierVisible(false);setNotice('');setData(null);setTour('ready');setSelection({kind:'acupoint',code:'LU1',side});
    const pick=(code:string)=>{if(alive){setSelection({kind:'acupoint',code,side});overlay.current?.select(code);}};
    if(review)adapter.restoreSourceMotion('acupoint-static-learning');
    const removeSelection=adapter.onSourceSelectionChange(()=>stop('해부 구조나 관찰 자세가 바뀌어 경혈 표시를 종료했습니다.'));
    const removeMotion=adapter.onSourceMotionStart(()=>stop('움직임 시작으로 경혈 표시를 종료했습니다. 정지 자세에서 다시 열어 주세요.'));
    void (async()=>{try{
      const d=adapter.resources.dataset,context={datasetRevision:d.revision,frameId:d.frameContract?.targetFrameId??'',unit:d.unit,poseId:d.frameContract?.staticReferencePose?.id??'',motionActive:adapter.resources.motionOverrides.size>0||adapter.scene.cameraOwner==='motion'};
      const cancelled=()=>token!==generation.current||!alive;let next:DisplayData;
      if(import.meta.env.DEV&&review){
        const {default:url}=side==='right'?await import('../../../../work/evidence/acupoint-AC2/right-learning.json?url'):await import('../../../../work/evidence/acupoint-AC2/left-learning.json?url');
        if(cancelled())return;const response=await fetch(url,{signal:abort.signal});if(!response.ok)throw Error('경혈 자료를 열 수 없습니다.');
        const bytes=await response.arrayBuffer();const {migratePlacementDocument}=await import('./placementMigration.ts');
        const migrated=await migratePlacementDocument(new Uint8Array(bytes)),legacy=migrated.document as unknown as LegacyData;
        if(cancelled())return;
        if(legacy.usage!=='development_review_only'||legacy.route.kind!=='surface_teaching'||legacy.route.carrierHash!==legacy.carrier.topologySha256||legacy.route.side!==side||legacy.instances.length!==11||legacy.route.teachingPointOrder.join()!==LUNG_ORDER.join())throw Error('경혈 학습 자료의 연결 기준이 다릅니다.');
        const projection=await projectLearnerInstances(legacy.carrier,legacy.instances,context,cancelled);if(cancelled())return;
        next={concepts:legacy.concepts.map(c=>({code:c.code,nameKo:c.nameKo,romanization:c.romanization,location:c.location?.text??'',landmarkLabel:c.landmarkLabel})),carriers:[legacy.carrier],instances:legacy.instances,route:legacy.route.positions,encodedBytes:bytes.byteLength,eligible:projection.instances.length,reasons:Object.fromEntries(legacy.instances.map(i=>[i.code,'기본 위치 설명과 모형 제안 위치는 구분됩니다. 점의 실제 혈위는 아직 미확정입니다.']))};
      }else{
        if(review)throw Error('검토 자료는 개발 화면에서만 열 수 있습니다.');
        const loaded=await loadLearningPackage(side,context,abort.signal,cancelled);
        next={concepts:loaded.data.concepts,carriers:loaded.carriers,instances:loaded.points,route:[],encodedBytes:loaded.encodedBytes,eligible:loaded.points.length,reasons:Object.fromEntries(loaded.data.availability.filter(a=>a.side===side).map(a=>[a.code,a.reason]))};
      }
      if(cancelled())return;
      if(next.instances.length){
        const created=await AcupunctureOverlay.create(adapter,next.carriers[0],next.instances,pick,reason=>stop(reason),next.encodedBytes,{returnCamera:returnCamera.current,carriers:next.carriers,side,route:next.route,names:Object.fromEntries(next.concepts.map(p=>[p.code,p.nameKo])),changed:state=>{if(alive)setTour(state);},cancelled});
        if(cancelled()){created.dispose(false);return;}overlay.current=created;created.setReducedMotion(reduced);created.select('LU1');created.overview();
      }
      // Empty projection allocates no geometry and owns no camera session.
      setData(next);
    }catch(error){if(token===generation.current&&alive)setNotice(error instanceof Error?error.message:'경혈 연결 실패');}
    finally{if(token===generation.current&&alive)setLoading(false);}})();
    return()=>{alive=false;generation.current++;abort.abort();removeMotion();removeSelection();overlay.current?.dispose();overlay.current=null;delete adapter.scene.renderer.domElement.dataset.acupointProjection;};
  },[adapter,side,mode]);
  useEffect(()=>{if(data)adapter.scene.renderer.domElement.dataset.acupointProjection=JSON.stringify({schemaVersion:2,mode,side,selection,concepts:data.concepts.length,rendered:data.instances.map(p=>p.code),localLearnerEligible:data.eligible,unresolved:11-data.eligible,fixtureExports:0,encodedBytes:data.encodedBytes});},[adapter,data,selection,mode,side]);
  const concept=data?.concepts.find(p=>p.code===selected),index=LUNG_ORDER.indexOf(selected),displayed=Boolean(data?.instances.some(p=>p.code===selected)),complete=Boolean(data?.instances.length===11);
  const choose=(code:string)=>{setSelection({kind:'acupoint',code,side});if(data?.instances.some(p=>p.code===code))overlay.current?.choose(code);else{overlay.current?.pause();overlay.current?.select(code);}};
  if(!data&&!loading&&notice)return <aside className="acupoint-entry" aria-label="경혈 안내"><button onClick={onClose}>경혈 안내 닫기</button><p role="status">{notice}</p></aside>;
  return <aside className="acupoint-review" data-active={Boolean(data)} aria-label="경혈 학습">
    <header><strong>수태음폐경 · LU</strong><button onClick={()=>{stop();onClose();}}>경혈 학습 닫기</button></header>
    <div role="group" aria-label="인체 좌우">{(['right','left'] as const).map(s=><button key={s} aria-pressed={side===s} onClick={()=>{if(s!==side){stop();setSide(s);}}}>{s==='right'?'오른쪽':'왼쪽'}</button>)}{data?.instances.length? <><button disabled={loading} aria-pressed={reduced} onClick={()=>{setReduced(!reduced);overlay.current?.setReducedMotion(!reduced);}}>이동 줄이기</button>{review&&<button disabled={!data} aria-pressed={carrierVisible} onClick={()=>{setCarrierVisible(!carrierVisible);overlay.current?.showCarrier(!carrierVisible);}}>체표 제안 면</button>}</>:null}</div>
    {loading?<p role="status">정지 체표 연결 중…</p>:data&&<>
      <div className="acupoint-codes" role="group" aria-label="폐경 경혈">{LUNG_ORDER.map(code=><button key={code} aria-label={`${code} ${data.concepts.find(p=>p.code===code)?.nameKo}`} aria-pressed={selected===code} onClick={()=>choose(code)}>{code}</button>)}</div>
      {complete&&<div className="acupoint-tour-controls" role="group" aria-label="경혈 따라보기 제어"><button onClick={()=>overlay.current?.play()}>경혈 따라보기</button><button disabled={tour!=='touring'} onClick={()=>overlay.current?.pause()}>정지</button><button disabled={index<=0} onClick={()=>overlay.current?.step(-1)}>이전</button><button disabled={index>=10} onClick={()=>overlay.current?.step(1)}>다음</button><button onClick={()=>overlay.current?.restoreCamera()}>복귀</button><button onClick={()=>overlay.current?.overview()}>전체 경로</button></div>}
      <small className="acupoint-persistent-limit">{review?'체표 학습선 · 위치 미확정':`모형 위 위치 표시 ${data.eligible}/11 · 인체 기준 좌우`}</small>
      <article className="acupoint-card" aria-label="선택 경혈 정보" aria-live="polite">
        <p className="acupoint-section">{LUNG_SECTIONS[sectionFor(selected)]?.name} · {index+1}/11{review&&` · ${tour==='touring'?'따라보는 중':tour==='paused'?'정지':'선택 보기'}`}</p>
        <h3>{concept?.nameKo} · {selected}</h3><p>{concept?.romanization} · {side==='right'?'오른쪽':'왼쪽'} 수태음폐경</p>
        <p>{concept?.location||'위치 설명 준비 중'}</p><p>기준 구조: {concept?.landmarkLabel}</p>
        {!review&&displayed&&<p>기준 구조를 대조한 교육용 개략 위치입니다. 정밀 취혈 위치는 아닙니다.</p>}
        {!displayed&&!review&&<p className="acupoint-limit">모형에서 위치를 표시할 수 없습니다. {data.reasons[selected]}</p>}
        {review&&<p className="acupoint-limit">{data.reasons[selected]}</p>}<p>교과서 설명 준비 중</p>
      </article>
      {review&&<small>점과 선은 정지 자세의 대략적 체표 학습 제안입니다. 전통적 전체 유주·분지·내행은 포함하지 않습니다.</small>}
    </>}{notice&&<p role="status">{notice}</p>}
  </aside>;
}
