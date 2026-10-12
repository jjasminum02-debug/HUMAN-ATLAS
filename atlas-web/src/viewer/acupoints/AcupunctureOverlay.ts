import * as THREE from 'three';
import type { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter.ts';
import { LUNG_ORDER, LUNG_SECTIONS, PointTour } from './tour.ts';
import type { Carrier, PointInstance } from './schema.ts';
import { resolveAnchor, validateCarrier, verifyCarrierHash, withinOverlayBudget } from './anchorAdapter.ts';
import type { CameraState } from '../wholeBody/cameraObservation.ts';
import { contextBounds, observationCamera, projectContext, visibleRect, rect, type ObservationContext } from './observationContext.ts';
import { DATASET_BUDGET } from '../datasets/schema.ts';
import type { TerritoryMaskLayer, TerritoryMode } from './territoryMask.ts';
interface OverlayOptions {returnCamera?:CameraState;carriers?:Carrier[];side?:'right'|'left'|'both';route:number[];names:Record<string,string>;changed:(state:PointTour['state'])=>void;cancelled:()=>boolean;contexts?:ObservationContext[];order?:string[];sections?:{name:string;codes:string[]}[]}
/** A bounded static-pose overlay attached to the sole AnatomySceneRoot. */
export class AcupunctureOverlay {
  readonly group = new THREE.Group();
  readonly markers = new Map<string, THREE.Mesh>();
  readonly carrierMesh: THREE.Mesh;
  private savedCamera: CameraState;
  readonly tour: PointTour;
  private section = -1;
  private label: HTMLButtonElement;
  private encodedRouteBytes = 0;
  private removeUpdate: () => void;
  private removeMotion: () => void;
  private removeCamera: () => void;
  private ownCameraCommand = false;
  private moved = false;
  private userMoved = false;
  private dead = false;
  private down = {x:0,y:0};
  private selected: string | null = null;
  private selectedSide:'right'|'left'='right';
  private resizeObserver:ResizeObserver;
  private removeFit:()=>void;
  private fitHandler=(kind:'all'|'selection')=>{if(kind==='all')this.overview();else if(this.selected)this.observe(this.selected,this.selectedSide,true);};
  private observation:unknown=null;
  private pointsVisible=true;
  private sharedCarriers=new Map<string,{carrier:Carrier;geometry:THREE.BufferGeometry}>();
  private territoryLayer:TerritoryMaskLayer|null=null;
  private territoryRequest:AbortController|null=null;
  private territoryGeneration=0;
  private territoryEncodedBytes=0;
  private territoryLoading=false;
  private territoryMode:TerritoryMode='selected';
  private territoryChannel='LU';
  private loadTerritoryModule=()=>import('./territoryMask.ts');
  private halo:THREE.Mesh;
  private reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  static async create(adapter: DatasetSceneAdapter, carrier: Carrier, points: PointInstance[], onSelect: (code: string,side?:'right'|'left') => void, onStop: (reason: string) => void, encodedBytes: number, options?: OverlayOptions) {
    if(options&&(options.route.length%3||!options.route.every(Number.isFinite)))throw Error('Invalid teaching route');
    const d = adapter.resources.dataset;
    const all=options?.carriers??[carrier],context={datasetRevision:d.revision,frameId:d.frameContract?.targetFrameId??'',unit:d.unit,poseId:d.frameContract?.staticReferencePose?.id??''};
    if(new Set(all.map(c=>c.id)).size!==all.length||!all.some(c=>c.id===carrier.id)||new Set(points.map(p=>`${p.code}:${p.side}`)).size!==points.length)throw Error('Invalid overlay carrier/point set');
    for(const c of all){validateCarrier(c,context);await verifyCarrierHash(c);}
    points.forEach(i=>{const c=all.find(c=>c.id===i.carrierId);if(!c)throw Error('Missing anchor carrier');resolveAnchor(c,i);});
    if(options?.cancelled())throw new DOMException('Cancelled','AbortError');
    if(adapter.scene.cameraOwner==='motion'||adapter.resources.motionOverrides.size>0)throw Error('경혈 표시는 복원된 정지 자세에서만 가능합니다.');
    return new AcupunctureOverlay(adapter,carrier,points,onSelect,onStop,encodedBytes,options);
  }
  private constructor(private adapter: DatasetSceneAdapter, readonly carrier: Carrier, readonly points: PointInstance[], private onSelect: (code: string,side?:'right'|'left') => void, private onStop: (reason: string) => void, private encodedBytes: number, private options?: OverlayOptions) {
    const scene = adapter.scene;
    adapter.restoreSourceMotion('acupoint-static-review');
    this.savedCamera=structuredClone(options?.returnCamera??scene.observationReturnState('acupoint'));scene.cancelCameraMotion();
    scene.beginObservation('acupoint',()=>this.onStop('다른 관찰 기능으로 경혈 따라보기를 종료했습니다.'),this.savedCamera);
    this.tour=new PointTour((index)=>{const code=(options?.order??LUNG_ORDER)[index];this.select(code,this.selectedSide);this.onSelect(code,this.selectedSide);this.observe(code,this.selectedSide);},()=>this.restoreCamera(true),state=>options?.changed(state),options?.order??LUNG_ORDER,options?.sections??LUNG_SECTIONS);
    this.label=document.createElement('button');this.label.className='acupoint-selected-label';this.label.setAttribute('aria-label','선택 경혈');this.label.onclick=()=>{if(this.selected)this.choose(this.selected,this.selectedSide);};scene.renderer.domElement.parentElement?.append(this.label);
    const carrierMaterial=new THREE.MeshBasicMaterial({color:0x2b8f99,transparent:true,opacity:.22,side:THREE.DoubleSide,depthWrite:false,forceSinglePass:true});
    const meshes=(options?.carriers??[carrier]).map(c=>{const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(c.positions,3));geometry.setIndex(c.indices);geometry.computeVertexNormals();
      const mesh=new THREE.Mesh(geometry,carrierMaterial);mesh.name='AcupointTeachingCarrier';mesh.visible=false;this.sharedCarriers.set(c.id,{carrier:c,geometry});this.group.add(mesh);return mesh;});
    this.carrierMesh=meshes[0];
    const markerGeometry=new THREE.SphereGeometry(.0025,12,8),normalMaterial=new THREE.MeshBasicMaterial({color:0xd36b24,depthTest:true}),selectedMaterial=new THREE.MeshBasicMaterial({color:0xed3f16,depthTest:true});
    this.group.userData.markerMaterials=[normalMaterial,selectedMaterial];
    for (const point of points) {
      const anchor=resolveAnchor((options?.carriers??[carrier]).find(c=>c.id===point.carrierId)!,point);
      const marker = new THREE.Mesh(markerGeometry,normalMaterial);
      marker.position.copy(anchor.position).addScaledVector(anchor.normal,.0008); marker.name=`AC-review-${point.code}-${point.side}`; marker.userData.code=point.code;
      this.markers.set(`${point.code}:${point.side}`,marker);this.group.add(marker);
    }
    this.halo=new THREE.Mesh(new THREE.RingGeometry(.0036,.0045,24),new THREE.MeshBasicMaterial({color:0xed8c47,transparent:true,opacity:.35,depthTest:true,depthWrite:false,side:THREE.DoubleSide}));this.halo.name='SelectedPointHalo';this.halo.visible=false;this.group.add(this.halo);
    if(options?.route.length) {
      if(options.route.length%3||!options.route.every(Number.isFinite))throw Error('Invalid teaching route');
      const lineGeometry=new THREE.BufferGeometry().setAttribute('position',new THREE.Float32BufferAttribute(options.route,3));
      const line=new THREE.LineSegments(lineGeometry,new THREE.LineBasicMaterial({color:0x508c85,transparent:true,opacity:.9,depthTest:true,depthWrite:false}));line.name='SurfaceTeachingOrder';line.renderOrder=300;this.group.add(line);this.encodedRouteBytes=options.route.length*4;
    }
    const cost=this.cost();
    const d=adapter.resources.dataset;
    const base={overviewBytes:d.chunks.filter(c=>c.level==='overview'&&!c.selectionScoped).reduce((n,c)=>n+c.bytes,0)+Math.max(0,...d.chunks.filter(c=>c.selectionScoped).map(c=>c.bytes)),geometryBytes:adapter.resources.queue.bytes,triangles:d.instances.reduce((n,i)=>n+i.lods.overview.triangles,0)};
    if (!withinOverlayBudget(base,{bytes:cost.geometryBufferBytes,overviewBytes:encodedBytes,triangles:cost.triangles})) { this.releaseGeometry();this.label.remove();scene.endObservation('acupoint',false); throw Error('경혈 체표가 기존 장면 예산을 초과합니다.'); }
    scene.renderer.domElement.dataset.acupointTransfers=JSON.stringify(performance.getEntriesByType('resource').filter(e=>/AcupointReview|AcupunctureOverlay|learning.json/.test(e.name)).map(e=>({name:e.name,bytes:(e as PerformanceResourceTiming).encodedBodySize})));
    this.group.name='AcupunctureOverlay';scene.root.add(this.group);scene.requestRender();
    const canvas=scene.renderer.domElement;
    canvas.addEventListener('pointerdown',this.onDown,true);canvas.addEventListener('pointerup',this.onUp,true);
    canvas.addEventListener('pointermove',this.onDrag);canvas.addEventListener('wheel',this.onManual);canvas.addEventListener('keydown',this.onManualKey);
    canvas.addEventListener('webglcontextlost',this.onLost);document.addEventListener('visibilitychange',this.onVisibility);
    this.removeMotion=adapter.onSourceMotionStart(()=>this.onStop('움직임 시작으로 체표 검토를 종료했습니다.'));
    this.removeCamera=scene.onCameraMove(()=>{if(!this.ownCameraCommand)this.manual();});
    this.removeFit=scene.registerObservationFit('acupoint',this.fitHandler);
    this.resizeObserver=new ResizeObserver(()=>{if(this.selected&&!this.userMoved)this.observe(this.selected,this.selectedSide);});this.resizeObserver.observe(canvas);const panel=canvas.closest('.whole-body-viewer')?.querySelector('.acupoint-review');if(panel)this.resizeObserver.observe(panel);
    this.removeUpdate=scene.addUpdate((seconds)=>{
      if (adapter.resources.queue.bytes+this.cost().geometryBufferBytes > DATASET_BUDGET.geometryBytes || scene.renderer.info.render.triangles > DATASET_BUDGET.triangles) { this.onStop('현재 장면이 기존 그래픽 예산을 초과하여 체표 검토를 종료했습니다.');return false; }
      const changed=this.tour.tick(Math.min(.1,seconds));this.inspect();return changed;
    });this.inspect();
  }
  cost() {
    const geometries=new Set<THREE.BufferGeometry>(),buffers=new Set<ArrayBufferLike>();let triangles=0;
    this.group.traverse(o=>{if(o instanceof THREE.Mesh||o instanceof THREE.Line){geometries.add(o.geometry);if(o instanceof THREE.Mesh)triangles+=(o.geometry.index?.count??0)/3;}});
    for(const g of geometries){for(const a of Object.values(g.attributes) as THREE.BufferAttribute[])buffers.add(a.array.buffer);if(g.index)buffers.add(g.index.array.buffer);}
    const geometryBufferBytes=[...buffers].reduce((n,b)=>n+b.byteLength,0),maskCalls=this.territoryLayer?.diagnostics().drawCalls??0;
    return {encodedBytes:this.encodedBytes+this.territoryEncodedBytes,geometryBufferBytes,triangles,textures:0,geometryCount:geometries.size,routeBufferBytes:this.encodedRouteBytes,drawCallsCarrierOff:(this.pointsVisible?this.points.length+1:0)+(this.options?.route.length?1:0)+maskCalls,drawCallsCarrierOn:(this.pointsVisible?this.points.length+1:0)+(this.options?.carriers?.length??1)+(this.options?.route.length?1:0)+maskCalls};
  }
  /** OFF/cancel is synchronous. Late module/data completions cannot allocate or reattach. */
  async showTerritories(enabled:boolean,mode:TerritoryMode='selected',channel='LU',fixture:'none'|'overlap'|'revision'='none') {
    if(this.dead)return;
    const token=++this.territoryGeneration;this.territoryRequest?.abort();this.territoryRequest=null;
    this.territoryLayer?.dispose();this.territoryLayer=null;this.territoryEncodedBytes=0;this.territoryLoading=enabled;this.territoryMode=mode;this.territoryChannel=channel;
    this.adapter.scene.requestRender();this.inspect();if(!enabled||this.dead)return;
    const abort=new AbortController();this.territoryRequest=abort;const cancelled=()=>this.dead||token!==this.territoryGeneration||abort.signal.aborted;
    try {
      const module=await this.loadTerritoryModule();if(cancelled())return;
      const c=this.carrier,context={datasetRevision:c.datasetRevision,frameId:c.frameId,unit:c.unit,poseId:c.poseId};
      const loaded=await module.loadTerritoryPackage([...this.sharedCarriers.values()].map(c=>c.carrier),context,abort.signal,cancelled);if(cancelled())return;
      let masks=loaded.masks;
      if(fixture!=='none'&&import.meta.env.DEV) {const qa=await import('./territoryCompositingFixture.ts');if(cancelled())return;masks=await qa.compositingFixtures(masks,fixture);if(cancelled())return;}
      this.installTerritoryLayer(module,masks,loaded.encodedBytes,mode,channel,cancelled);
    }finally {if(!cancelled()){this.territoryLoading=false;this.territoryRequest=null;this.inspect();}}
  }
  /** Revision replacement shares the existing layer, budget, cancellation and camera session. */
  async replaceTerritoryMasks(masks:import('./schema.ts').TerritoryMask[],channel:string,encodedBytes=0,technicalReview=false) {
    if(this.dead)return;
    const token=++this.territoryGeneration;this.territoryRequest?.abort();this.territoryRequest=null;
    const cancelled=()=>this.dead||token!==this.territoryGeneration;
    const module=await this.loadTerritoryModule();if(cancelled())return;
    const c=this.carrier,context={datasetRevision:c.datasetRevision,frameId:c.frameId,unit:c.unit,poseId:c.poseId};
    const allowFixture=technicalReview&&import.meta.env.DEV;
    for(const m of masks){const surface=this.sharedCarriers.get(m.carrierId);if(!surface)throw Error('Missing revision carrier');await module.validateTerritoryMask(m,surface.carrier,context,allowFixture);if(cancelled())return;}
    this.territoryMode='selected';this.territoryChannel=channel;
    this.installTerritoryLayer(module,masks,encodedBytes,'selected',channel,cancelled);
    this.inspect();
  }
  private installTerritoryLayer(module:Awaited<ReturnType<typeof this.loadTerritoryModule>>,masks:import('./schema.ts').TerritoryMask[],encodedBytes:number,mode:TerritoryMode,channel:string,cancelled:()=>boolean) {
    const layer=new module.TerritoryMaskLayer(masks,this.sharedCarriers);layer.show(true,mode,channel);
    const d=this.adapter.resources.dataset,cost=this.cost(),extra=layer.diagnostics(),old=this.territoryLayer?.diagnostics();
    const base={overviewBytes:d.chunks.filter(c=>c.level==='overview'&&!c.selectionScoped).reduce((n,c)=>n+c.bytes,0)+Math.max(0,...d.chunks.filter(c=>c.selectionScoped).map(c=>c.bytes)),geometryBytes:this.adapter.resources.queue.bytes,triangles:d.instances.reduce((n,i)=>n+i.lods.overview.triangles,0)};
    if(!withinOverlayBudget(base,{bytes:cost.geometryBufferBytes-(old?.additionalBufferBytes??0)+extra.additionalBufferBytes,overviewBytes:cost.encodedBytes-this.territoryEncodedBytes+encodedBytes,triangles:cost.triangles-(old?.triangles??0)+extra.triangles})){layer.dispose();throw Error('학습 영역이 기존 그래픽 예산을 초과합니다.');}
    if(cancelled()){layer.dispose();return;}
    this.territoryLayer?.dispose();this.territoryLayer=layer;this.territoryEncodedBytes=encodedBytes;this.group.add(layer.group);this.adapter.scene.requestRender();
  }
  /** Development editing picks the already-owned hidden canonical carrier. */
  reviewCarrierSurface(id:string) {
    if(!import.meta.env.DEV)throw Error('Carrier editing is development-only');
    const surface=this.sharedCarriers.get(id);if(!surface)throw Error('Missing review surface');
    const mesh=this.group.children.find(n=>n instanceof THREE.Mesh&&n.geometry===surface.geometry) as THREE.Mesh;
    return {...surface,mesh};
  }
  select(code:string,side:'right'|'left'=this.selectedSide) {
    this.selectedSide=side;this.selected=this.markers.has(`${code}:${side}`)?code:null;this.label.hidden=!this.selected;this.tour.index=(this.options?.order??LUNG_ORDER).indexOf(code);
    const [normal,selected]=this.group.userData.markerMaterials as THREE.Material[];
    for(const [key,m] of this.markers)m.material=key===`${code}:${side}`?selected:normal;
    this.label.textContent=`${this.options?.names[code]??code} · ${code}`;
    this.adapter.scene.requestRender();this.inspect();
  }
  setReducedMotion(enabled:boolean){this.reducedMotion=enabled;this.adapter.scene.cancelCameraMotion();}
  play(){this.userMoved=false;this.tour.play();this.adapter.scene.requestRender();}
  pause(){this.tour.pause();this.adapter.scene.cancelCameraMotion();}
  step(delta:number){this.userMoved=false;this.tour.step(delta);}
  choose(code:string,side:'right'|'left'=this.selectedSide){this.userMoved=false;this.selectedSide=side;const index=(this.options?.order??LUNG_ORDER).indexOf(code);if(index>=0)this.tour.choose(index);else{this.tour.pause();this.select(code,side);this.onSelect(code,side);this.observe(code,side);}}
  private safeRect() {
    const canvas=this.adapter.scene.renderer.domElement,r=canvas.getBoundingClientRect();
    const panels=[...canvas.closest('.study-layout')?.querySelectorAll('.acupoint-review,.body-tools,.study-header,.study-details')??[]].filter(e=>getComputedStyle(e).visibility!=='hidden').map(e=>{const p=e.getBoundingClientRect();return rect(p.left,p.top,p.right,p.bottom);});
    return visibleRect(rect(r.left,r.top,r.right,r.bottom),panels);
  }
  observe(code:string,side:'right'|'left'=this.selectedSide,force=false) {
    const context=this.options?.contexts?.find(c=>c.code===code&&c.side===side);if(!context)return;
    this.frameContexts([context],force);
  }
  private frameContexts(contexts:ObservationContext[],force=false) {
    if(this.dead||this.adapter.scene.cameraOwner!=='acupoint')return;
    const scene=this.adapter.scene,r=scene.renderer.domElement.getBoundingClientRect(),canvas=rect(r.left,r.top,r.right,r.bottom),safe=this.safeRect();
    const visibleKeys=new Set([...this.adapter.resources.nodes].filter(([,node])=>node.visible).map(([k])=>k));
    const box=contextBounds(contexts);if(box.isEmpty())return;
    const primary=contexts[0],state=scene.cameraState(),normal=new THREE.Vector3().fromArray(primary.preferredNormal).normalize();
    const near=[...this.adapter.resources.nodes.values()].filter(n=>{if(!n.visible)return false;const g=n.geometry;if(!g.boundingBox)g.computeBoundingBox();return g.boundingBox!.clone().applyMatrix4(n.matrixWorld).distanceToPoint(box.getCenter(new THREE.Vector3()))<box.getSize(new THREE.Vector3()).length();});
    const visibleAt=(camera:CameraState,point:THREE.Vector3,glyph=false)=>{const origin=new THREE.Vector3().fromArray(camera.position),delta=point.clone().sub(origin),ray=new THREE.Raycaster(origin,delta.clone().normalize(),0,delta.length());const hit=ray.intersectObjects(near,false)[0];const radius=glyph?delta.length()*Math.tan(THREE.MathUtils.degToRad(scene.camera.fov/2))*8/r.height:0;return !hit||hit.distance>=delta.length()-radius-.0001;};
    const point=primary.point?this.markers.get(`${primary.code}:${primary.side}`)?.position:undefined;
    let fit=observationCamera(box,state,scene.camera.fov,canvas,safe,primary.preferredNormal,contexts.length===1?primary.point:undefined,force);
    const candidates=[fit,...[-.25,.25].map(yaw=>observationCamera(box,state,scene.camera.fov,canvas,safe,normal.clone().applyAxisAngle(new THREE.Vector3(0,1,0),yaw).toArray() as [number,number,number],primary.point,true,false))];
    const evaluated=candidates.map((c,index)=>{const pointVisible=!point||visibleAt(c.state,point,true);const muscles=primary.structures.filter(s=>s.role==='muscle_tendon'&&visibleKeys.has(s.sourceKey)).flatMap(s=>s.samplePositions).slice(0,6);const visibleSamples=muscles.filter(p=>visibleAt(c.state,new THREE.Vector3().fromArray(p))).length;return {index,pointVisible,visibleSamples,score:(pointVisible?100:0)+visibleSamples-(index===0?0:1.5),fit:c};});
    evaluated.sort((a,b)=>b.score-a.score);fit=evaluated[0].fit;
    this.section=(this.options?.sections??LUNG_SECTIONS).findIndex(s=>s.codes.includes(primary.code));
    this.observation={codes:contexts.map(c=>c.code),side:primary.side,mode:primary.mode,worldBounds:[box.min.toArray(),box.max.toArray()],safeViewport:safe,cameraBefore:state,cameraTarget:fit.state,retained:fit.retained,visibilityCandidates:evaluated.map(({fit:_fit,...e})=>e),pointOccluded:!evaluated[0].pointVisible,projectedTarget:fit.after,structures:contexts.flatMap(c=>c.structures.map(s=>({sourceKey:s.sourceKey,name:s.name,bounds:s.bounds,visible:visibleKeys.has(s.sourceKey),role:s.role}))),requestCode:this.selected};
    if(!fit.retained){this.moved=true;this.userMoved=false;this.moveCamera(fit.state);}else this.moveCamera(fit.state,false);scene.requestRender();this.inspect();
  }
  /** Compatibility entry routes through verified local structures, never point-only bounds. */
  focusSection(code:string,overview=false){if(overview)this.overview();else this.observe(code);}
  overview(){this.pause();this.tour.state='ready';this.options?.changed('ready');const contexts=this.options?.contexts?.filter(c=>this.options?.side==='both'||c.side===(this.options?.side??this.carrier.side))??[];if(contexts.length)this.frameContexts(contexts,true);}
  showPoints(enabled:boolean){this.pointsVisible=enabled;for(const m of this.markers.values())m.visible=enabled;this.label.hidden=!enabled;this.halo.visible=enabled;this.adapter.scene.requestRender();}
  showRoute(enabled:boolean){for(const o of this.group.children)if(o.name==='SurfaceTeachingOrder')o.visible=enabled;this.adapter.scene.requestRender();}
  showCarrier(enabled:boolean) {for(const child of this.group.children)if(child.name==='AcupointTeachingCarrier')child.visible=enabled;this.adapter.scene.requestRender();}
  focus(code:string){this.observe(code,this.selectedSide,true);}
  private moveCamera(state:CameraState,smooth=!this.reducedMotion) {
    // Flush leftover OrbitControls damping before an explicit review camera command.
    // Otherwise even a subpixel point click can drift the restored camera afterward.
    const controls=this.adapter.scene.controls, damping=controls.enableDamping;
    controls.enableDamping=false;controls.update();controls.enableDamping=damping;
    this.ownCameraCommand=true;
    try { this.adapter.scene.moveCamera(state,smooth); } finally { this.ownCameraCommand=false; }
  }
  restoreCamera(completed=false) {if(!completed)this.tour.pause();this.moveCamera(this.savedCamera);this.moved=false;this.section=-1;this.userMoved=false;}
  private manual(){this.userMoved=true;this.tour.pause(true);this.adapter.scene.cancelCameraMotion();this.label.hidden=true;this.halo.visible=false;}
  private onManual=()=>this.manual();
  private onManualKey=(e:KeyboardEvent)=>{if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','+','-','=','Home'].includes(e.key))this.manual();};
  private onDrag=(e:PointerEvent)=>{if(e.buttons&&Math.hypot(e.clientX-this.down.x,e.clientY-this.down.y)>5)this.manual();};
  private onLost=()=>this.onStop('그래픽 연결 중단으로 체표 검토를 종료했습니다.');
  private onVisibility=()=>{if(document.hidden)this.onStop('화면 비활성화로 체표 검토를 종료했습니다.');};
  private onDown=(e:PointerEvent)=>{this.down={x:e.clientX,y:e.clientY};this.manual();};
  private onUp=(e:PointerEvent)=>{
    if(e.button!==0||Math.hypot(e.clientX-this.down.x,e.clientY-this.down.y)>5)return;
    const scene=this.adapter.scene,r=scene.renderer.domElement.getBoundingClientRect(),ray=new THREE.Raycaster();
    ray.setFromCamera(new THREE.Vector2((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1),scene.camera);
    if(!this.pointsVisible)return;
    const candidates=[...this.markers.values()].filter(m=>{const p=m.position.clone().project(scene.camera);return Math.abs(p.z)<1&&Math.hypot(r.left+(p.x+1)*r.width/2-e.clientX,r.top+(1-p.y)*r.height/2-e.clientY)<=14;}).sort((a,b)=>{const pa=a.position.clone().project(scene.camera),pb=b.position.clone().project(scene.camera);return Math.hypot((pa.x+1)*r.width/2+r.left-e.clientX,(1-pa.y)*r.height/2+r.top-e.clientY)-Math.hypot((pb.x+1)*r.width/2+r.left-e.clientX,(1-pb.y)*r.height/2+r.top-e.clientY);});
    const marker=candidates[0];if(!marker)return;
    ray.setFromCamera(new THREE.Vector2().fromArray([marker.position.clone().project(scene.camera).x,marker.position.clone().project(scene.camera).y]),scene.camera);
    const blocked=ray.intersectObjects([...this.adapter.resources.nodes.values()].filter(n=>n.visible),false)[0];
    if(blocked&&blocked.distance<scene.camera.position.distanceTo(marker.position)-.0025*marker.scale.x-.0001)return;
    e.stopImmediatePropagation();const side=this.points.find(p=>this.markers.get(`${p.code}:${p.side}`)===marker)?.side;
    this.choose(String(marker.userData.code),side==='left'?'left':'right');
  };
  private inspect() {
    const scene=this.adapter.scene,r=scene.renderer.domElement.getBoundingClientRect();scene.camera.updateMatrixWorld();
    const cameraTarget=(this.observation as {cameraTarget?:CameraState}|null)?.cameraTarget;
    const cameraSettled=!cameraTarget||scene.cameraState().position.every((v,i)=>Math.abs(v-cameraTarget.position[i])<1e-8);
    scene.renderer.domElement.dataset.acupointTerritory=JSON.stringify({loading:this.territoryLoading,cameraSettled,currentCamera:scene.cameraState(),mode:this.territoryMode,channel:this.territoryChannel,encodedBytes:this.territoryEncodedBytes,...this.territoryLayer?.diagnostics()??{maskCount:0,visibleMasks:[],additionalBufferBytes:0,triangles:0,fixtureMasks:0}});
    if(this.selected){const marker=this.markers.get(`${this.selected}:${this.selectedSide}`);if(marker){const p=marker.position.clone().project(scene.camera);this.label.hidden=!this.pointsVisible||this.userMoved||Math.abs(p.x)>1||Math.abs(p.y)>1||Math.abs(p.z)>1;this.label.style.left=`${(p.x+1)/2*r.width+8}px`;this.label.style.top=`${(1-p.y)/2*r.height-24}px`;}}
    for(const marker of this.markers.values()){const radius=scene.camera.position.distanceTo(marker.position)*Math.tan(THREE.MathUtils.degToRad(scene.camera.fov/2))*8/r.height;marker.scale.setScalar(radius/.0025);}
    const marker=this.selected?this.markers.get(`${this.selected}:${this.selectedSide}`):undefined;this.halo.visible=Boolean(marker&&this.pointsVisible&&!this.userMoved);if(marker){this.halo.position.copy(marker.position);this.halo.quaternion.copy(scene.camera.quaternion);this.halo.scale.copy(marker.scale);}
    let actualObservation=null;if(this.observation){const o=this.observation as {worldBounds:[number[],number[]]};const box=new THREE.Box3(new THREE.Vector3().fromArray(o.worldBounds[0]),new THREE.Vector3().fromArray(o.worldBounds[1]));actualObservation=projectContext(box,scene.cameraState(),scene.camera.fov,rect(r.left,r.top,r.right,r.bottom),this.safeRect(),marker?.position.toArray() as [number,number,number]|undefined);}
    scene.renderer.domElement.dataset.acupointReview=JSON.stringify({root:scene.root.uuid,groupParent:this.group.parent?.name,carrier:this.carrier.id,carrierHash:this.carrier.topologySha256,frame:this.carrier.frameId,unit:'m',pose:this.carrier.poseId,side:this.options?.side??this.carrier.side,selection:{kind:'acupoint',code:this.selected,side:this.selectedSide},selected:this.selected,observation:this.observation,actualObservation,pointsVisible:this.pointsVisible,selectedSide:this.selectedSide,tour:this.tour.state,tourIndex:this.tour.index,autoReturn:this.tour.autoReturn,userMoved:this.userMoved,section:this.section,safeViewport:this.safeRect(),cameraOwner:scene.cameraOwner,reducedMotion:this.reducedMotion,carrierVisible:this.carrierMesh.visible,cost:this.cost(),points:[...this.markers].map(([id,m])=>{const [code,side]=id.split(':');const p=m.position.clone().project(scene.camera);return {code,side,world:m.position.toArray(),screen:[r.left+(p.x+1)/2*r.width,r.top+(1-p.y)/2*r.height],inFrustum:Math.abs(p.x)<=1&&Math.abs(p.y)<=1&&Math.abs(p.z)<=1,locationValidation:this.points.find(i=>i.code===code)?.locationValidation};})});
  }
  private releaseGeometry() {
    this.territoryGeneration++;this.territoryRequest?.abort();this.territoryRequest=null;this.territoryLayer?.dispose();this.territoryLayer=null;
    const geometries=new Set<THREE.BufferGeometry>(),materials=new Set<THREE.Material>();
    this.group.traverse(o=>{if(o instanceof THREE.Mesh||o instanceof THREE.Line){geometries.add(o.geometry);materials.add(o.material as THREE.Material);}});
    for(const m of this.group.userData.markerMaterials??[])materials.add(m);
    geometries.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());
  }
  dispose(restore=true) {
    if(this.dead)return;this.dead=true;const scene=this.adapter.scene,canvas=scene.renderer.domElement,ownsCamera=scene.cameraOwner==='acupoint'&&(scene.isObservationFit?.('acupoint',this.fitHandler)??true);this.removeUpdate();this.removeMotion();this.removeCamera();this.removeFit?.();this.resizeObserver?.disconnect();
    const current=ownsCamera?scene.cameraState?.():undefined;const needsReturn=current?[...current.position,...current.target,current.zoom].some((v,i)=>Math.abs(v-[...this.savedCamera.position,...this.savedCamera.target,this.savedCamera.zoom][i])>1e-8):this.moved;
    if(ownsCamera)scene.cancelCameraMotion();
    canvas.removeEventListener('pointerdown',this.onDown,true);canvas.removeEventListener('pointerup',this.onUp,true);canvas.removeEventListener('pointermove',this.onDrag);canvas.removeEventListener('wheel',this.onManual);canvas.removeEventListener('keydown',this.onManualKey);canvas.removeEventListener('webglcontextlost',this.onLost);document.removeEventListener('visibilitychange',this.onVisibility);
    this.tour.pause();this.label.remove();this.group.removeFromParent();this.releaseGeometry();if(ownsCamera||scene.cameraOwner!=='acupoint'){delete canvas.dataset.acupointReview;delete canvas.dataset.acupointTerritory;}if(ownsCamera||scene.cameraOwner!=='acupoint')scene.endObservation('acupoint',restore&&ownsCamera&&needsReturn&&!this.userMoved,!this.reducedMotion);scene.requestRender();
  }
}
