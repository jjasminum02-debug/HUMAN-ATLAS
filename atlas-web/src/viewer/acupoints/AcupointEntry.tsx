import { useEffect, useRef, useState, type ComponentType } from 'react';
import type { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter.ts';
type ReviewProps={adapter:DatasetSceneAdapter;onClose:()=>void;mode?:'learner'|'review'};
/** Small opt-in entry: heavy module/data absent while OFF; late imports cannot mount. */
export default function AcupointEntry({adapter,surfaceSample=false,developmentReview=false,territoryDevelopmentReview=false,onModeChange}:{adapter:DatasetSceneAdapter;surfaceSample?:boolean;developmentReview?:boolean;territoryDevelopmentReview?:boolean;onModeChange?:(active:boolean)=>void}) {
  const [Review,setReview]=useState<ComponentType<ReviewProps>|null>(null),[loading,setLoading]=useState(false),[error,setError]=useState('');
  const generation=useRef(0);
  useEffect(()=>{onModeChange?.(Boolean(Review)&&!surfaceSample&&!territoryDevelopmentReview);},[Review,onModeChange,surfaceSample,territoryDevelopmentReview]);
  useEffect(()=>()=>onModeChange?.(false),[onModeChange]);
  const inspect=(requested:boolean)=>{adapter.scene.renderer.domElement.dataset.acupointLoading=JSON.stringify({requested,resources:performance.getEntriesByType('resource').filter(e=>/AcupointReview|AcupunctureOverlay|learning.json|lung.json|education-r1|CarrierSample|za-thigh-sample/.test(e.name)).map(e=>({name:e.name,bytes:(e as PerformanceResourceTiming).encodedBodySize}))});};
  useEffect(()=>{inspect(false);return()=>{delete adapter.scene.renderer.domElement.dataset.acupointLoading;};},[adapter]);
  const close=()=>{generation.current++;setReview(null);setLoading(false);};
  useEffect(()=>()=>{generation.current++;},[adapter]);
  const open=async()=>{const token=++generation.current;inspect(true);setLoading(true);setError('');try{const module=import.meta.env.DEV&&territoryDevelopmentReview?await import('./TerritoryEditorReview.tsx'):import.meta.env.DEV&&surfaceSample?await import('./CarrierSampleReview.tsx'):await import('./AcupointReview.tsx');if(token===generation.current){setReview(()=>module.default);inspect(true);}}catch{if(token===generation.current)setError(territoryDevelopmentReview?'영역 검토를 열 수 없습니다. 다시 시도해 주세요.':surfaceSample?'체표 표본을 열 수 없습니다. 다시 시도해 주세요.':'경혈 기능을 열 수 없습니다. 다시 시도해 주세요.');}finally{if(token===generation.current)setLoading(false);}};
  return Review?<Review adapter={adapter} onClose={close} mode={developmentReview?'review':'learner'}/>:<aside className="acupoint-entry"><button onClick={()=>loading?close():void open()}>{loading?(surfaceSample?'표본 연결 취소':'경혈 연결 취소'):territoryDevelopmentReview?'영역 경계 검토':surfaceSample?'체표 표본 검토':developmentReview?'경혈 학습 검토':'경혈'}</button>{error&&<p role="status">{error}</p>}</aside>;
}
