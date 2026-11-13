import {useEffect,useRef,useState} from 'react';
import type {DatasetSceneAdapter} from '../datasets/DatasetSceneAdapter.ts';
import {loadCarrierSet} from './carrierLoader.ts';
import {AcupunctureOverlay} from './AcupunctureOverlay.ts';
import {widthFixture,EDITOR_CARRIER} from './territoryEditorFixture.ts';
import {TerritoryEditSession,type TerritoryRevision} from './territoryEditor.ts';
import {TerritoryBrushController,type BrushTool} from './TerritoryBrushController.ts';
import './review.css';import './territoryEditor.css';
const storageKey='human-atlas-territory-review-revision-v1';
export default function TerritoryEditorReview({adapter,onClose}:{adapter:DatasetSceneAdapter;onClose:()=>void}) {
  const [ready,setReady]=useState(false),[notice,setNotice]=useState('검토 표면을 연결하고 있어요…'),[tool,setTool]=useState<BrushTool>('orbit'),[radius,setRadius]=useState(16),[before,setBefore]=useState(false),[collapsed,setCollapsed]=useState(false),[tick,setTick]=useState(0),[saved,setSaved]=useState(false);
  const overlay=useRef<AcupunctureOverlay|null>(null),brush=useRef<TerritoryBrushController|null>(null),model=useRef<TerritoryEditSession|null>(null),alive=useRef(false),generation=useRef(0);
  const failure=(e:unknown)=>{if(alive.current)setNotice(e instanceof Error?e.message:'검토 작업 실패');};
  const changed=()=>{if(!alive.current)return;setTick(n=>n+1);const m=model.current;if(m){const c=adapter.scene.renderer.domElement;c.dataset.territoryEditor=JSON.stringify({scope:'technical_fixture',channel:'ST',realSTPoints:0,carrierId:m.carrier.id,carrierHash:m.bindings.carrierHash,pointHash:m.bindings.pointHash,routeHash:m.bindings.routeHash,baseFaces:m.base.triangleIds.length,currentFaces:m.faceIds.length,canUndo:m.canUndo,canRedo:m.canRedo,camera:adapter.scene.cameraState(),root:adapter.scene.root.uuid,maskRevisionOnly:true});}};
  useEffect(()=>{if(!import.meta.env.DEV)return;alive.current=true;const token=++generation.current,abort=new AbortController(),cancelled=()=>!alive.current||token!==generation.current||abort.signal.aborted;
    const stop=()=>{alive.current=false;generation.current++;abort.abort();brush.current?.dispose();overlay.current?.dispose();onClose();};
    const motion=adapter.onSourceMotionStart(stop),selection=adapter.onSourceSelectionChange(stop);const visibility=()=>{if(document.hidden)stop();};document.addEventListener('visibilitychange',visibility);
    void (async()=>{try{const d=adapter.resources.dataset,context={datasetRevision:d.revision,frameId:d.frameContract?.targetFrameId??'',unit:d.unit,poseId:d.frameContract?.staticReferencePose?.id??''};const loaded=await loadCarrierSet([EDITOR_CARRIER],context,abort.signal,cancelled);if(cancelled())return;const c=loaded.samples[0].carrier,fixture=await widthFixture(c);if(cancelled())return;
      const created=await AcupunctureOverlay.create(adapter,c,fixture.points,()=>{},stop,loaded.encodedBytes,{carriers:[c],route:fixture.route,names:{'PROBE-1':'기술 기준 A','PROBE-2':'기술 기준 B'},changed:()=>{},cancelled,order:fixture.points.map(p=>p.code),sections:[],side:'right',contexts:fixture.contexts});if(cancelled()){created.dispose();return;}
      overlay.current=created;model.current=new TerritoryEditSession(c,fixture.mask,fixture.bindings);brush.current=new TerritoryBrushController(adapter,created,model.current,changed,failure);await brush.current.preview();if(cancelled())return;setReady(true);setNotice('위경 폭 편집 기술 표본 · 실제 위경 영역/혈위 검증 아님');try{setSaved(Boolean(localStorage.getItem(storageKey)));}catch{setNotice('저장 공간을 사용할 수 없습니다. 현재 편집은 유지됩니다.');}
    }catch(e){if(!cancelled())failure(e);}})();
    return()=>{alive.current=false;generation.current++;abort.abort();document.removeEventListener('visibilitychange',visibility);motion();selection();brush.current?.dispose();brush.current=null;overlay.current?.dispose();overlay.current=null;model.current=null;delete adapter.scene.renderer.domElement.dataset.territoryEditor;};
  },[adapter]);
  function chooseTool(next:BrushTool){setBefore(false);setTool(next);brush.current?.setTool(next);void brush.current?.preview();}
  async function compare(value:boolean){setBefore(value);setTool('orbit');brush.current?.setTool('orbit');await brush.current?.preview(value);}
  async function save(){const token=generation.current;try{const revision=await model.current!.revision();if(!alive.current||token!==generation.current)return;localStorage.setItem(storageKey,JSON.stringify(revision));setSaved(true);setNotice('검토 revision을 이 브라우저에 저장했습니다. learner에는 적용되지 않습니다.');}catch(e){failure(e);}}
  async function reload(){const token=generation.current;try{const text=localStorage.getItem(storageKey);if(!text||text.length>2_000_000)throw Error('저장본이 없거나 크기가 잘못됐습니다.');const m=model.current!;await m.loadRevision(JSON.parse(text));if(!alive.current||token!==generation.current)return;setBefore(false);setTool('orbit');brush.current?.setTool('orbit');await brush.current?.preview();setNotice('저장본을 검증해 재로드했습니다. point/route/carrier는 그대로입니다.');}catch(e){failure(e);}}
  async function exportRevision(){const token=generation.current;try{const r:TerritoryRevision=await model.current!.revision();if(!alive.current||token!==generation.current)return;const url=URL.createObjectURL(new Blob([JSON.stringify(r,null,2)+'\n'],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='territory-review-revision.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),0);}catch(e){failure(e);}}
  void tick;const m=model.current;
  return <aside className="acupoint-review territory-editor-review" data-active={ready} data-collapsed={collapsed} aria-label="영역 경계 개발 검토">
    <header><strong>영역 경계 검토</strong><button className="acupoint-collapse" aria-expanded={!collapsed} onClick={()=>setCollapsed(!collapsed)}>{collapsed?'펼치기':'접기'}</button><button onClick={onClose}>검토 닫기</button></header>
    <p className="acupoint-persistent-limit">ST 폭 기술 fixture · 교육용 넙다리 carrier. 실제 위경 영역·경혈은 0개입니다.</p>
    <div role="group" aria-label="triangle 편집 도구">{(['orbit','paint','erase'] as const).map(t=><button key={t} disabled={!ready} aria-pressed={tool===t&&!before} onClick={()=>chooseTool(t)}>{t==='orbit'?'회전·해부 선택':t==='paint'?'칠하기':'지우기'}</button>)}</div>
    <label>브러시 반경 {radius}mm<input aria-label="브러시 반경" type="range" min="6" max="40" value={radius} onChange={e=>{const r=Number(e.target.value);setRadius(r);brush.current?.setRadius(r);}}/></label>
    <div role="group" aria-label="편집 이력"><button disabled={!m?.canUndo||before} onClick={()=>{m?.undo();void brush.current?.preview();}}>되돌리기</button><button disabled={!m?.canRedo||before} onClick={()=>{m?.redo();void brush.current?.preview();}}>다시 실행</button><button disabled={!ready} onClick={()=>overlay.current?.overview()}>표본 맞춤</button></div>
    <div role="group" aria-label="같은 시점 전후 비교"><button disabled={!ready} aria-pressed={before} onClick={()=>void compare(true)}>수정 전</button><button disabled={!ready} aria-pressed={!before} onClick={()=>void compare(false)}>수정 후</button></div>
    <output aria-label="mask face 개수">원본 {m?.base.triangleIds.length??0}면 · 현재 {m?.faceIds.length??0}면{before?' · 원본 표시':' · 편집본 표시'}</output>
    <div role="group" aria-label="review revision 저장"><button disabled={!ready||!m?.faceIds.length} onClick={()=>void save()}>revision 저장</button><button disabled={!ready||!saved} onClick={()=>void reload()}>저장본 재로드</button><button disabled={!ready||!m?.faceIds.length} onClick={()=>void exportRevision()}>JSON 내보내기</button></div>
    <p role="status">{notice}</p><small>브러시에서만 canvas 드래그를 편집에 사용합니다. 회전 모드는 기존 해부 클릭을 유지합니다. Ctrl/⌘+Z 및 Shift+Z로 이력을 조절합니다. 저장은 위치·권리·교수 승인과 별개입니다.</small>
  </aside>;
}
