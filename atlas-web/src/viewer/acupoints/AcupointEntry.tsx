import { useEffect, useRef, useState, type ComponentType } from 'react';
import type { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter.ts';
type ReviewProps={adapter:DatasetSceneAdapter;onClose:()=>void};
/** Small opt-in entry: heavy module/data absent while OFF; late imports cannot mount. */
export default function AcupointEntry({adapter}:{adapter:DatasetSceneAdapter}) {
  const [Review,setReview]=useState<ComponentType<ReviewProps>|null>(null),[loading,setLoading]=useState(false),[error,setError]=useState('');
  const generation=useRef(0);
  const inspect=(requested:boolean)=>{adapter.scene.renderer.domElement.dataset.acupointLoading=JSON.stringify({requested,resources:performance.getEntriesByType('resource').filter(e=>/AcupointReview|AcupunctureOverlay|learning.json/.test(e.name)).map(e=>({name:e.name,bytes:(e as PerformanceResourceTiming).encodedBodySize}))});};
  useEffect(()=>{inspect(false);return()=>{delete adapter.scene.renderer.domElement.dataset.acupointLoading;};},[adapter]);
  const close=()=>{generation.current++;setReview(null);setLoading(false);};
  useEffect(()=>()=>{generation.current++;},[adapter]);
  const open=async()=>{const token=++generation.current;inspect(true);setLoading(true);setError('');try{const module=await import('./AcupointReview.tsx');if(token===generation.current){setReview(()=>module.default);inspect(true);}}catch{if(token===generation.current)setError('경혈 기능을 열 수 없습니다. 다시 시도해 주세요.');}finally{if(token===generation.current)setLoading(false);}};
  return Review?<Review adapter={adapter} onClose={close}/>:<aside className="acupoint-entry"><button onClick={()=>loading?close():void open()}>{loading?'경혈 연결 취소':'경혈 학습 검토'}</button>{error&&<p role="status">{error}</p>}</aside>;
}
