import * as THREE from 'three';
import type { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter.ts';
import { LUNG_ORDER, LUNG_SECTIONS, PointTour, sectionFor } from './tour.ts';
import type { Carrier, PointInstance } from './schema.ts';
import { resolveAnchor, validateCarrier, verifyCarrierHash, withinOverlayBudget } from './anchorAdapter.ts';
import type { CameraState } from '../wholeBody/cameraObservation.ts';
import { DATASET_BUDGET } from '../datasets/schema.ts';
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
  private reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  static async create(adapter: DatasetSceneAdapter, carrier: Carrier, points: PointInstance[], onSelect: (code: string) => void, onStop: (reason: string) => void, encodedBytes: number, options?: { returnCamera?:CameraState;route: number[]; names: Record<string,string>; changed: (state:PointTour['state'])=>void; cancelled:()=>boolean }) {
    if(options&&(options.route.length%3||!options.route.every(Number.isFinite)))throw Error('Invalid teaching route');
    const d = adapter.resources.dataset;
    validateCarrier(carrier, { datasetRevision:d.revision, frameId:d.frameContract?.targetFrameId ?? '', unit:d.unit, poseId:d.frameContract?.staticReferencePose?.id ?? '' });
    await verifyCarrierHash(carrier); points.forEach(i => resolveAnchor(carrier,i));
    if(options?.cancelled())throw new DOMException('Cancelled','AbortError');
    if(adapter.scene.cameraOwner==='motion'||adapter.resources.motionOverrides.size>0)throw Error('경혈 표시는 복원된 정지 자세에서만 가능합니다.');
    return new AcupunctureOverlay(adapter,carrier,points,onSelect,onStop,encodedBytes,options);
  }
  private constructor(private adapter: DatasetSceneAdapter, readonly carrier: Carrier, readonly points: PointInstance[], private onSelect: (code: string) => void, private onStop: (reason: string) => void, private encodedBytes: number, private options?: { returnCamera?:CameraState;route:number[]; names:Record<string,string>; changed:(state:PointTour['state'])=>void; cancelled:()=>boolean }) {
    const scene = adapter.scene;
    adapter.restoreSourceMotion('acupoint-static-review');
    scene.cancelCameraMotion(); this.savedCamera = structuredClone(options?.returnCamera??scene.cameraState());
    scene.beginObservation('acupoint',()=>this.onStop('다른 관찰 기능으로 경혈 따라보기를 종료했습니다.'));
    this.tour=new PointTour((index,focus)=>{const code=LUNG_ORDER[index];this.onSelect(code);this.select(code);if(focus)this.focusSection(code);},()=>this.restoreCamera(true),state=>options?.changed(state));
    this.label=document.createElement('button');this.label.className='acupoint-selected-label';this.label.setAttribute('aria-label','선택 경혈');this.label.onclick=()=>{if(this.selected)this.onSelect(this.selected);};scene.renderer.domElement.parentElement?.append(this.label);
    const geometry = new THREE.BufferGeometry(); geometry.setAttribute('position',new THREE.Float32BufferAttribute(carrier.positions,3)); geometry.setIndex(carrier.indices); geometry.computeVertexNormals();
    this.carrierMesh = new THREE.Mesh(geometry,new THREE.MeshBasicMaterial({color:0x2b8f99, transparent:true,opacity:.22,side:THREE.DoubleSide,depthWrite:false,forceSinglePass:true}));
    this.carrierMesh.name = 'AcupointTeachingCarrier'; this.carrierMesh.visible = false; this.group.add(this.carrierMesh);
    const markerGeometry=new THREE.SphereGeometry(.0025,12,8),normalMaterial=new THREE.MeshBasicMaterial({color:0xd36b24,depthTest:true}),selectedMaterial=new THREE.MeshBasicMaterial({color:0xed3f16,depthTest:true});
    this.group.userData.markerMaterials=[normalMaterial,selectedMaterial];
    for (const point of points) {
      const anchor=resolveAnchor(carrier,point);
      const marker = new THREE.Mesh(markerGeometry,normalMaterial);if(point.code==='LU11')marker.scale.setScalar(.6);
      marker.position.copy(anchor.position).addScaledVector(anchor.normal,.0008); marker.name=`AC-review-${point.code}-${carrier.side}`; marker.userData.code=point.code;
      this.markers.set(point.code,marker);this.group.add(marker);
    }
    if(options?.route.length) {
      if(options.route.length%3||!options.route.every(Number.isFinite))throw Error('Invalid teaching route');
      const lineGeometry=new THREE.BufferGeometry().setAttribute('position',new THREE.Float32BufferAttribute(options.route,3));
      const line=new THREE.Line(lineGeometry,new THREE.LineBasicMaterial({color:0x508c85,transparent:true,opacity:.8,depthTest:true}));line.name='SurfaceTeachingOrder';this.group.add(line);this.encodedRouteBytes=options.route.length*4;
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
    this.removeUpdate=scene.addUpdate((seconds)=>{
      if (adapter.resources.queue.bytes+cost.geometryBufferBytes > DATASET_BUDGET.geometryBytes || scene.renderer.info.render.triangles > DATASET_BUDGET.triangles) { this.onStop('현재 장면이 기존 그래픽 예산을 초과하여 체표 검토를 종료했습니다.');return false; }
      const changed=this.tour.tick(Math.min(.1,seconds));this.inspect();return changed;
    });this.inspect();
  }
  cost() {
    const geometries=new Set<THREE.BufferGeometry>();let triangles=0,geometryBufferBytes=0;
    this.group.traverse(o=>{if(o instanceof THREE.Mesh||o instanceof THREE.Line){geometries.add(o.geometry);if(o instanceof THREE.Mesh)triangles+=(o.geometry.index?.count??0)/3;}});
    for(const g of geometries){for(const a of Object.values(g.attributes) as THREE.BufferAttribute[])geometryBufferBytes+=a.array.byteLength;geometryBufferBytes+=g.index?.array.byteLength??0;}
    return {encodedBytes:this.encodedBytes,geometryBufferBytes,triangles,textures:0,geometryCount:geometries.size,routeBufferBytes:this.encodedRouteBytes,drawCallsCarrierOff:this.points.length+(this.options?1:0),drawCallsCarrierOn:this.points.length+1+(this.options?1:0)};
  }
  select(code:string) {
    this.selected=code;this.tour.index=LUNG_ORDER.indexOf(code);
    const [normal,selected]=this.group.userData.markerMaterials as THREE.Material[];
    for(const [key,m] of this.markers)m.material=key===code?selected:normal;
    this.label.textContent=`${this.options?.names[code]??code} · ${code}`;
    this.adapter.scene.requestRender();this.inspect();
  }
  setReducedMotion(enabled:boolean){this.reducedMotion=enabled;this.adapter.scene.cancelCameraMotion();}
  play(){this.userMoved=false;this.tour.play();this.adapter.scene.requestRender();}
  pause(){this.tour.pause();this.adapter.scene.cancelCameraMotion();}
  step(delta:number){this.userMoved=false;this.tour.step(delta);}
  choose(code:string){this.userMoved=false;this.tour.choose(LUNG_ORDER.indexOf(code));}
  private safeRect() {
    const r=this.adapter.scene.renderer.domElement.getBoundingClientRect();
    return {left:r.left+20,top:r.top+28,right:r.right-20,bottom:r.bottom-28,width:Math.max(1,r.width-40),height:Math.max(1,r.height-56)};
  }
  /** Existing layout reserves card space; fit a whole section in the remaining canvas. */
  focusSection(code:string,overview=false) {
    const index=sectionFor(code);if(index<0)return;
    const codes=overview?LUNG_ORDER:LUNG_SECTIONS[index].codes;this.section=overview?-1:index;
    const box=new THREE.Box3();for(const c of codes){const m=this.markers.get(c);if(m)box.expandByPoint(m.position);}
    box.expandByScalar(overview?.035:index===3?.012:.025);
    const scene=this.adapter.scene,safe=this.safeRect();
    const center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3()),tan=Math.tan(THREE.MathUtils.degToRad(scene.camera.fov/2));
    const distance=Math.max(.08,1.3*Math.max(size.y/tan,size.x/(tan*(safe.width/safe.height)))/2+size.z);
    const direction=new THREE.Vector3(this.carrier.side==='right'?-.18:.18,.04,1).normalize();
    this.moved=true;this.userMoved=false;this.moveCamera({position:center.clone().addScaledVector(direction,distance).toArray(),target:center.toArray(),zoom:1});
  }
  overview(){this.pause();this.tour.state='ready';this.options?.changed('ready');this.focusSection('LU1',true);}
  showCarrier(enabled:boolean) {this.carrierMesh.visible=enabled;this.adapter.scene.requestRender();}
  focus(code:string, direction:'front'|'oblique'|'side'='front') {
    const marker=this.markers.get(code);if(!marker)return;
    const target=marker.position.clone(), distance=code==='LU1'?.31:code==='LU9'?.16:.07;
    const offset=direction==='front'?new THREE.Vector3(0,0,distance):direction==='oblique'?new THREE.Vector3(-distance*.65,0,distance*.8):new THREE.Vector3(-distance,0,0);
    this.moved=true;this.userMoved=false;this.moveCamera({position:target.clone().add(offset).toArray(),target:target.toArray(),zoom:1});
  }
  private moveCamera(state:CameraState) {
    // Flush leftover OrbitControls damping before an explicit review camera command.
    // Otherwise even a subpixel point click can drift the restored camera afterward.
    const controls=this.adapter.scene.controls, damping=controls.enableDamping;
    controls.enableDamping=false;controls.update();controls.enableDamping=damping;
    this.ownCameraCommand=true;
    try { this.adapter.scene.moveCamera(state,!this.reducedMotion); } finally { this.ownCameraCommand=false; }
  }
  restoreCamera(completed=false) {if(!completed)this.tour.pause();this.moveCamera(this.savedCamera);this.moved=false;this.section=-1;this.userMoved=false;}
  private manual(){this.userMoved=true;this.tour.pause(true);this.adapter.scene.cancelCameraMotion();this.label.hidden=true;}
  private onManual=()=>this.manual();
  private onManualKey=(e:KeyboardEvent)=>{if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','+','-','=','Home'].includes(e.key))this.manual();};
  private onDrag=(e:PointerEvent)=>{if(e.buttons&&Math.hypot(e.clientX-this.down.x,e.clientY-this.down.y)>5)this.manual();};
  private onLost=()=>this.onStop('그래픽 연결 중단으로 체표 검토를 종료했습니다.');
  private onVisibility=()=>{if(document.hidden)this.onStop('화면 비활성화로 체표 검토를 종료했습니다.');};
  private onDown=(e:PointerEvent)=>{this.down={x:e.clientX,y:e.clientY};};
  private onUp=(e:PointerEvent)=>{
    if(e.button!==0||Math.hypot(e.clientX-this.down.x,e.clientY-this.down.y)>5)return;
    const scene=this.adapter.scene,r=scene.renderer.domElement.getBoundingClientRect(),ray=new THREE.Raycaster();
    ray.setFromCamera(new THREE.Vector2((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1),scene.camera);
    const hit=ray.intersectObjects([...this.markers.values()],false)[0];if(!hit)return;
    // Point priority only when it is in front of actual visible anatomy.
    const blocked=ray.intersectObjects([...this.adapter.resources.nodes.values()].filter(n=>n.visible),false)[0];
    if(blocked&&blocked.distance<hit.distance-.0001)return;
    e.stopImmediatePropagation();this.tour.pause();this.onSelect(String(hit.object.userData.code));
  };
  private inspect() {
    const scene=this.adapter.scene,r=scene.renderer.domElement.getBoundingClientRect();scene.camera.updateMatrixWorld();
    if(this.selected){const marker=this.markers.get(this.selected);if(marker){const p=marker.position.clone().project(scene.camera);this.label.hidden=this.userMoved||Math.abs(p.x)>1||Math.abs(p.y)>1||Math.abs(p.z)>1;this.label.style.left=`${(p.x+1)/2*r.width+8}px`;this.label.style.top=`${(1-p.y)/2*r.height-24}px`;}}
    scene.renderer.domElement.dataset.acupointReview=JSON.stringify({root:scene.root.uuid,groupParent:this.group.parent?.name,carrier:this.carrier.id,carrierHash:this.carrier.topologySha256,frame:this.carrier.frameId,unit:'m',pose:this.carrier.poseId,side:this.carrier.side,selection:{kind:'acupoint',code:this.selected,side:this.carrier.side},selected:this.selected,tour:this.tour.state,tourIndex:this.tour.index,autoReturn:this.tour.autoReturn,userMoved:this.userMoved,section:this.section,safeViewport:this.safeRect(),cameraOwner:scene.cameraOwner,reducedMotion:this.reducedMotion,carrierVisible:this.carrierMesh.visible,cost:this.cost(),points:[...this.markers].map(([code,m])=>{const p=m.position.clone().project(scene.camera);return {code,world:m.position.toArray(),screen:[r.left+(p.x+1)/2*r.width,r.top+(1-p.y)/2*r.height],inFrustum:Math.abs(p.x)<=1&&Math.abs(p.y)<=1&&Math.abs(p.z)<=1,locationValidation:'unresolved'};})});
  }
  private releaseGeometry() {
    const geometries=new Set<THREE.BufferGeometry>(),materials=new Set<THREE.Material>();
    this.group.traverse(o=>{if(o instanceof THREE.Mesh||o instanceof THREE.Line){geometries.add(o.geometry);materials.add(o.material as THREE.Material);}});
    for(const m of this.group.userData.markerMaterials??[])materials.add(m);
    geometries.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());
  }
  dispose(restore=true) {
    if(this.dead)return;this.dead=true;this.removeUpdate();this.removeMotion();this.removeCamera();
    const scene=this.adapter.scene,canvas=scene.renderer.domElement,ownsCamera=scene.cameraOwner==='acupoint';if(ownsCamera)scene.cancelCameraMotion();
    canvas.removeEventListener('pointerdown',this.onDown,true);canvas.removeEventListener('pointerup',this.onUp,true);canvas.removeEventListener('pointermove',this.onDrag);canvas.removeEventListener('wheel',this.onManual);canvas.removeEventListener('keydown',this.onManualKey);canvas.removeEventListener('webglcontextlost',this.onLost);document.removeEventListener('visibilitychange',this.onVisibility);
    this.tour.pause();this.label.remove();this.group.removeFromParent();this.releaseGeometry();delete canvas.dataset.acupointReview;scene.endObservation('acupoint',false);
    if(restore&&ownsCamera&&this.moved&&!this.userMoved)this.moveCamera(this.savedCamera);scene.requestRender();
  }
}
