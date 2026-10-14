import { useEffect, useRef, useState } from 'react';
import type { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter.ts';
import type { SkinLayer } from './SkinLayer.ts';
import { registeredSkin } from './skinContract.ts';
import { SkinLayerState } from './skinState.ts';

const review = import.meta.env.DEV && new URLSearchParams(window.location.search).get('skinReview')==='1';
export default function SkinControls({adapter,acupoints}:{adapter:DatasetSceneAdapter;acupoints:boolean}) {
  const state=useRef(new SkinLayerState()),layer=useRef<SkinLayer|null>(null),generation=useRef(0);
  const unsubscribe=useRef<(()=>void)|null>(null);
  const [visible,setVisible]=useState(false),[loading,setLoading]=useState(false),[notice,setNotice]=useState('');
  const sync=async()=> {
    const token=++generation.current;
    if(!state.current.visible){layer.current?.off();setLoading(false);setVisible(false);return;}
    if(!registeredSkin&&!review)return;
    setLoading(true);setNotice('');
    try {
      if(!layer.current){
        const module=await import('./SkinLayer.ts');
        const asset=registeredSkin??(import.meta.env.DEV&&review?await (await import('./skinReviewAsset.ts')).skinReviewAsset(adapter.resources.dataset.revision):null);
        if(token!==generation.current||!asset)return;
        layer.current=new module.SkinLayer(adapter,asset,review);
        unsubscribe.current=layer.current.subscribe(()=>setVisible(layer.current?.visible??false));
      }
      await layer.current.on();if(token===generation.current)setVisible(layer.current.visible);
    } catch(error){if(token===generation.current){state.current.suspend();setVisible(false);setNotice(error instanceof Error&&/[가-힣]/.test(error.message)?error.message:'피부 자료의 정합·좌표·파일 검증을 통과하지 못했습니다.');}}
    finally {if(token===generation.current)setLoading(false);}
  };
  useEffect(()=>{state.current.acupoints(acupoints);void sync();},[acupoints,adapter]);
  useEffect(()=>{
    const remove=adapter.onSourceMotionStart(()=>{generation.current++;state.current.suspend();layer.current?.off();setVisible(false);setLoading(false);});
    return()=>{generation.current++;remove();unsubscribe.current?.();unsubscribe.current=null;layer.current?.dispose();layer.current=null;};
  },[adapter]);
  return <>
    <button aria-pressed={visible} disabled={!registeredSkin&&!review} title={!registeredSkin&&!review?'전신 피부 정합 준비 중':review?'미정합 피부의 개발 검토용 표시':'피부 보기'} onClick={()=>{state.current.manual(!(visible||loading));void sync();}}>{loading?'피부 취소':'피부'}</button>
    {review&&<span role="status">미정합 피부 검토 · 경혈 피부 접촉 미검증</span>}
    {notice&&<span role="status">{notice}</span>}
  </>;
}
