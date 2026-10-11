import * as THREE from 'three';
import type { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter.ts';
import { DATASET_BUDGET } from '../datasets/schema.ts';
import { withinOverlayBudget } from './anchorAdapter.ts';
import { validateCarrierSample, type CarrierSample } from './carrierSample.ts';

/** Bounded carrier chunks in the existing scene, with no camera or picking ownership. */
export class CarrierSampleOverlay {
  private readonly group = new THREE.Group();
  private readonly geometries: THREE.BufferGeometry[] = [];
  private readonly material: THREE.MeshBasicMaterial;
  private readonly removeUpdate: () => void;
  private readonly removeMotion: () => void;
  private readonly removeSelection: () => void;
  private dead = false;
  private reference = false;
  private readonly adapter: DatasetSceneAdapter;
  private readonly data: CarrierSample[];
  private readonly stop: (reason:string)=>void;
  readonly cost: { encodedBytes:number; geometryBufferBytes:number; triangles:number; textures:number; drawCalls:number };

  static async create(adapter:DatasetSceneAdapter, data:CarrierSample, encodedBytes:number, cancelled:()=>boolean, stop:(reason:string)=>void) {
    return this.createMany(adapter,[data],encodedBytes,cancelled,stop);
  }
  static async createMany(adapter:DatasetSceneAdapter, data:CarrierSample[], encodedBytes:number, cancelled:()=>boolean, stop:(reason:string)=>void) {
    const d=adapter.resources.dataset;
    if(!data.length)throw Error('Empty carrier set');
    for(const chunk of data) {
      await validateCarrierSample(chunk,{datasetRevision:d.revision,frameId:d.frameContract?.targetFrameId??'',unit:d.unit,poseId:d.frameContract?.staticReferencePose?.id??''});
      if(cancelled())throw new DOMException('Cancelled','AbortError');
    }
    if(cancelled())throw new DOMException('Cancelled','AbortError');
    if(adapter.scene.cameraOwner==='motion'||adapter.scene.cameraOwner==='acupoint'||(adapter.resources.motionOverrides?.size??0)>0)throw Error('다른 관찰 기능을 닫고 정지 자세에서 표본을 열어 주세요.');
    return new CarrierSampleOverlay(adapter,data,encodedBytes,stop);
  }

  private constructor(adapter:DatasetSceneAdapter, data:CarrierSample[], encodedBytes:number, stop:(reason:string)=>void) {
    this.adapter=adapter;this.data=data;this.stop=stop;
    this.material=new THREE.MeshBasicMaterial({color:0x238f9c,transparent:true,opacity:data.length===1?.38:.18,side:THREE.DoubleSide,forceSinglePass:true,depthWrite:false});
    this.group.name='CarrierSurfaceSample';
    for(const sample of data) {
      const c=sample.carrier,geometry=new THREE.BufferGeometry();
      geometry.setAttribute('position',new THREE.Float32BufferAttribute(c.positions,3));
      geometry.setIndex(c.indices);geometry.computeVertexNormals();this.geometries.push(geometry);
      const mesh=new THREE.Mesh(geometry,this.material);mesh.name=c.id;this.group.add(mesh);
    }
    const buffers=this.geometries.flatMap(g=>[...Object.values(g.attributes).map(a=>a.array.byteLength),g.index?.array.byteLength??0]);
    this.cost={encodedBytes,geometryBufferBytes:buffers.reduce((a,b)=>a+b,0),triangles:data.reduce((n,s)=>n+s.carrier.indices.length/3,0),textures:0,drawCalls:data.length};
    const d=adapter.resources.dataset;
    const base={overviewBytes:d.chunks.filter(c=>c.level==='overview'&&!c.selectionScoped).reduce((n,c)=>n+c.bytes,0)+Math.max(0,...d.chunks.filter(c=>c.selectionScoped).map(c=>c.bytes)),geometryBytes:adapter.resources.queue.bytes,triangles:d.instances.reduce((n,i)=>n+i.lods.overview.triangles,0)};
    if(!withinOverlayBudget(base,{bytes:this.cost.geometryBufferBytes,overviewBytes:encodedBytes,triangles:this.cost.triangles})) {
      this.geometries.forEach(g=>g.dispose());this.material.dispose();throw Error('표본이 기존 장면 예산을 초과합니다.');
    }
    this.joinSeamNormals();
    const scene=adapter.scene;scene.root.add(this.group);scene.requestRender();
    scene.renderer.domElement.dataset.carrierSampleTransfers=JSON.stringify(performance.getEntriesByType('resource').filter(e=>/CarrierSample|za-thigh-sample|education-r1/.test(e.name)).map(e=>({name:e.name,bytes:(e as PerformanceResourceTiming).encodedBodySize})));
    this.removeMotion=adapter.onSourceMotionStart(()=>stop('움직임 시작으로 정지 체표 표본을 종료했습니다.'));
    this.removeSelection=adapter.onSourceSelectionChange(()=>stop('선택 또는 자세 변경으로 표본을 종료했습니다.'));
    this.removeUpdate=scene.addUpdate(()=>{
      if(adapter.resources.queue.bytes+this.cost.geometryBufferBytes>DATASET_BUDGET.geometryBytes || scene.renderer.info.render.triangles>DATASET_BUDGET.triangles) {
        stop('기존 장면 예산 초과로 표본을 종료했습니다.');return false;
      }
      this.inspect();return false;
    });
    scene.renderer.domElement.addEventListener('webglcontextlost',this.onLost);
    document.addEventListener('visibilitychange',this.onVisibility);
    this.inspect();
  }

  showReference(enabled:boolean) {
    if(this.dead)return;
    this.reference=enabled;
    this.geometries.forEach((geometry,i)=>{
      const position=geometry.getAttribute('position') as THREE.BufferAttribute;
      position.copyArray(enabled?this.data[i].referencePositions:this.data[i].carrier.positions);position.needsUpdate=true;
      geometry.computeVertexNormals();geometry.computeBoundingSphere();
    });
    this.joinSeamNormals();
    this.material.color.set(enabled?0xc59335:0x238f9c);
    this.adapter.scene.requestRender();this.inspect();
  }
  private onLost=()=>this.stop('그래픽 연결 중단으로 표본을 종료했습니다.');
  private onVisibility=()=>{if(document.hidden)this.stop('화면 비활성화로 표본을 종료했습니다.');};
  private seamVertices=0;
  private joinSeamNormals() {
    const shared=new Map<string,{g:THREE.BufferGeometry;i:number;n:THREE.Vector3}[]>();
    for(const g of this.geometries) {
      const p=g.getAttribute('position'),n=g.getAttribute('normal');
      for(let i=0;i<p.count;i++) {
        const key=`${p.getX(i)},${p.getY(i)},${p.getZ(i)}`;
        const list=shared.get(key)??[];list.push({g,i,n:new THREE.Vector3().fromBufferAttribute(n,i)});shared.set(key,list);
      }
    }
    this.seamVertices=0;
    for(const list of shared.values())if(list.length>1) {
      const sum=list.reduce((n,v)=>n.add(v.n),new THREE.Vector3()).normalize();this.seamVertices+=list.length;
      list.forEach(v=>{const n=v.g.getAttribute('normal') as THREE.BufferAttribute;n.setXYZ(v.i,sum.x,sum.y,sum.z);n.needsUpdate=true;});
    }
  }
  private inspect() {
    const scene=this.adapter.scene,canvas=scene.renderer.domElement,r=canvas.getBoundingClientRect();scene.camera.updateMatrixWorld();
    const samples=this.geometries.flatMap((g,i)=>{const positions=g.getAttribute('position');
      const indices=this.data.length===1&&positions.count===1024?[0,16,32,48,512,528,544,560,960,976,992,1008]:[0,Math.floor(positions.count/4),Math.floor(positions.count/2),Math.floor(3*positions.count/4),positions.count-1];
      return indices.map(index=>{
      const world=new THREE.Vector3().fromBufferAttribute(positions,index),screen=world.clone().project(scene.camera);
      return {chunk:this.data[i].carrier.id,index,world:world.toArray(),screen:[r.left+(screen.x+1)*r.width/2,r.top+(1-screen.y)*r.height/2],inFrustum:Math.abs(screen.x)<=1&&Math.abs(screen.y)<=1&&Math.abs(screen.z)<=1};
    });});
    const first=this.data[0];
    canvas.dataset.carrierSample=JSON.stringify({root:scene.root.uuid,renderer:canvas.id,parent:this.group.parent?.name,
      meshCount:this.group.children.length,mode:this.reference?'native_surface_samples':'authored_teaching_surface',
      frame:first.carrier.frameId,unit:'m',pose:first.carrier.poseId,side:this.data.length===1?first.carrier.side:'multiple',
      topologyHash:this.reference?first.referenceHash:first.carrier.topologySha256,
      chunks:this.data.map(s=>({id:s.carrier.id,side:s.carrier.side,hash:this.reference?s.referenceHash:s.carrier.topologySha256})),
      seamVerticesWithSharedNormals:this.seamVertices,cameraOwner:scene.cameraOwner,acceptedAcupoints:0,cost:this.cost,samples});
  }
  dispose() {
    if(this.dead)return;this.dead=true;
    this.removeUpdate();this.removeMotion();this.removeSelection();
    const canvas=this.adapter.scene.renderer.domElement;
    canvas.removeEventListener('webglcontextlost',this.onLost);document.removeEventListener('visibilitychange',this.onVisibility);
    this.group.removeFromParent();this.geometries.forEach(g=>g.dispose());this.material.dispose();delete canvas.dataset.carrierSample;
    this.adapter.scene.requestRender();
  }
}
