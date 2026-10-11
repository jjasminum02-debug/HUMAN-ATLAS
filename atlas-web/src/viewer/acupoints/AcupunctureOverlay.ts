import * as THREE from 'three';
import type { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter.ts';
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
  private removeUpdate: () => void;
  private removeMotion: () => void;
  private removeCamera: () => void;
  private ownCameraCommand = false;
  private moved = false;
  private userMoved = false;
  private dead = false;
  private down = {x:0,y:0};
  private selected: string | null = null;
  static async create(adapter: DatasetSceneAdapter, carrier: Carrier, points: PointInstance[], onSelect: (code: string) => void, onStop: (reason: string) => void, encodedBytes: number) {
    const d = adapter.resources.dataset;
    validateCarrier(carrier, { datasetRevision:d.revision, frameId:d.frameContract?.targetFrameId ?? '', unit:d.unit, poseId:d.frameContract?.staticReferencePose?.id ?? '' });
    await verifyCarrierHash(carrier); points.forEach(i => resolveAnchor(carrier,i));
    return new AcupunctureOverlay(adapter,carrier,points,onSelect,onStop,encodedBytes);
  }
  private constructor(private adapter: DatasetSceneAdapter, readonly carrier: Carrier, readonly points: PointInstance[], private onSelect: (code: string) => void, private onStop: (reason: string) => void, private encodedBytes: number) {
    const scene = adapter.scene;
    adapter.restoreSourceMotion('acupoint-static-review');
    scene.cancelCameraMotion(); this.savedCamera = scene.cameraState();
    const geometry = new THREE.BufferGeometry(); geometry.setAttribute('position',new THREE.Float32BufferAttribute(carrier.positions,3)); geometry.setIndex(carrier.indices); geometry.computeVertexNormals();
    this.carrierMesh = new THREE.Mesh(geometry,new THREE.MeshBasicMaterial({color:0x2b8f99, transparent:true,opacity:.22,side:THREE.DoubleSide,depthWrite:false,forceSinglePass:true}));
    this.carrierMesh.name = 'AcupointTeachingCarrier'; this.carrierMesh.visible = false; this.group.add(this.carrierMesh);
    for (const point of points) {
      const anchor=resolveAnchor(carrier,point);
      const marker = new THREE.Mesh(new THREE.SphereGeometry(point.code === 'LU11' ? .0015 : .003,12,8),new THREE.MeshBasicMaterial({color:0xd36b24,depthTest:true}));
      marker.position.copy(anchor.position).addScaledVector(anchor.normal,.0008); marker.name=`AC-review-${point.code}-right`; marker.userData.code=point.code;
      this.markers.set(point.code,marker);this.group.add(marker);
    }
    const cost=this.cost();
    const d=adapter.resources.dataset;
    const base={overviewBytes:d.chunks.filter(c=>c.level==='overview'&&!c.selectionScoped).reduce((n,c)=>n+c.bytes,0)+Math.max(0,...d.chunks.filter(c=>c.selectionScoped).map(c=>c.bytes)),geometryBytes:adapter.resources.queue.bytes,triangles:d.instances.reduce((n,i)=>n+i.lods.overview.triangles,0)};
    if (!withinOverlayBudget(base,{bytes:cost.geometryBufferBytes,overviewBytes:encodedBytes,triangles:cost.triangles})) { this.releaseGeometry(); throw Error('경혈 체표가 기존 장면 예산을 초과합니다.'); }
    this.group.name='AcupunctureOverlay';scene.root.add(this.group);scene.requestRender();
    const canvas=scene.renderer.domElement;
    canvas.addEventListener('pointerdown',this.onDown,true);canvas.addEventListener('pointerup',this.onUp,true);
    canvas.addEventListener('pointermove',this.onDrag);canvas.addEventListener('wheel',this.onManual);canvas.addEventListener('keydown',this.onManualKey);
    canvas.addEventListener('webglcontextlost',this.onLost);document.addEventListener('visibilitychange',this.onVisibility);
    this.removeMotion=adapter.onSourceMotionStart(()=>this.onStop('움직임 시작으로 체표 검토를 종료했습니다.'));
    this.removeCamera=scene.onCameraMove(()=>{if(!this.ownCameraCommand)this.userMoved=true;});
    this.removeUpdate=scene.addUpdate(()=>{
      if (adapter.resources.queue.bytes+cost.geometryBufferBytes > DATASET_BUDGET.geometryBytes || scene.renderer.info.render.triangles > DATASET_BUDGET.triangles) { this.onStop('현재 장면이 기존 그래픽 예산을 초과하여 체표 검토를 종료했습니다.');return false; }
      this.inspect();return false;
    });this.inspect();
  }
  cost() {
    let geometryBufferBytes=0,triangles=0;this.group.traverse(o=>{if(o instanceof THREE.Mesh){for(const a of Object.values(o.geometry.attributes) as THREE.BufferAttribute[])geometryBufferBytes+=a.array.byteLength;geometryBufferBytes+=o.geometry.index?.array.byteLength??0;triangles+=(o.geometry.index?.count??0)/3;}});
    return {encodedBytes:this.encodedBytes,geometryBufferBytes,triangles,textures:0,geometryCount:4,drawCallsCarrierOff:3,drawCallsCarrierOn:4};
  }
  select(code:string) { this.selected=code;for(const [key,m] of this.markers)(m.material as THREE.MeshBasicMaterial).color.setHex(key===code?0xed3f16:0xd36b24);this.adapter.scene.requestRender();this.inspect(); }
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
    try { this.adapter.scene.moveCamera(state); } finally { this.ownCameraCommand=false; }
  }
  restoreCamera() {this.moveCamera(this.savedCamera);this.moved=false;}
  private onManual=()=>{this.userMoved=true;};
  private onManualKey=(e:KeyboardEvent)=>{if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','+','-','=','Home'].includes(e.key))this.userMoved=true;};
  private onDrag=(e:PointerEvent)=>{if(e.buttons&&Math.hypot(e.clientX-this.down.x,e.clientY-this.down.y)>5)this.userMoved=true;};
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
    e.stopImmediatePropagation();this.onSelect(String(hit.object.userData.code));
  };
  private inspect() {
    const scene=this.adapter.scene,r=scene.renderer.domElement.getBoundingClientRect();scene.camera.updateMatrixWorld();
    scene.renderer.domElement.dataset.acupointReview=JSON.stringify({root:scene.root.uuid,groupParent:this.group.parent?.name,carrier:this.carrier.id,carrierHash:this.carrier.topologySha256,frame:this.carrier.frameId,unit:'m',pose:this.carrier.poseId,side:'right',selected:this.selected,carrierVisible:this.carrierMesh.visible,cost:this.cost(),points:[...this.markers].map(([code,m])=>{const p=m.position.clone().project(scene.camera);return {code,world:m.position.toArray(),screen:[r.left+(p.x+1)/2*r.width,r.top+(1-p.y)/2*r.height],inFrustum:Math.abs(p.x)<=1&&Math.abs(p.y)<=1&&Math.abs(p.z)<=1,locationValidation:'unresolved'};})});
  }
  private releaseGeometry() {this.group.traverse(o=>{if(o instanceof THREE.Mesh){o.geometry.dispose();(o.material as THREE.Material).dispose();}});}
  dispose(restore=true) {
    if(this.dead)return;this.dead=true;this.removeUpdate();this.removeMotion();this.removeCamera();
    const scene=this.adapter.scene,canvas=scene.renderer.domElement;
    canvas.removeEventListener('pointerdown',this.onDown,true);canvas.removeEventListener('pointerup',this.onUp,true);canvas.removeEventListener('pointermove',this.onDrag);canvas.removeEventListener('wheel',this.onManual);canvas.removeEventListener('keydown',this.onManualKey);canvas.removeEventListener('webglcontextlost',this.onLost);document.removeEventListener('visibilitychange',this.onVisibility);
    this.group.removeFromParent();this.releaseGeometry();delete canvas.dataset.acupointReview;
    if(restore&&this.moved&&!this.userMoved)this.moveCamera(this.savedCamera);scene.requestRender();
  }
}
