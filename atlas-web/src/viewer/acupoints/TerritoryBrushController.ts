import * as THREE from 'three';
import type {DatasetSceneAdapter} from '../datasets/DatasetSceneAdapter.ts';
import type {AcupunctureOverlay} from './AcupunctureOverlay.ts';
import {TerritoryEditSession} from './territoryEditor.ts';
export type BrushTool='orbit'|'paint'|'erase';
/** Capture only explicit DEV brush strokes; orbit/native selection remain the default. */
export class TerritoryBrushController {
  private tool:BrushTool='orbit';private radius=.016;private pointer:number|null=null;private generation=0;private dead=false;private comparing=false;
  private readonly canvas:HTMLCanvasElement;private readonly parent:HTMLElement;private readonly surface:ReturnType<AcupunctureOverlay['reviewCarrierSurface']>;
  constructor(private adapter:DatasetSceneAdapter,private overlay:AcupunctureOverlay,readonly model:TerritoryEditSession,private changed:()=>void,private failed:(error:unknown)=>void) {
    this.canvas=adapter.scene.renderer.domElement;this.parent=this.canvas.parentElement!;this.surface=overlay.reviewCarrierSurface(model.carrier.id);
    for(const type of ['pointerdown','pointermove','pointerup','pointercancel','lostpointercapture'] as const)this.parent.addEventListener(type,this.pointerEvent,true);
    this.parent.addEventListener('keydown',this.key,true);
  }
  setTool(tool:BrushTool){this.cancelStroke();this.tool=tool;this.canvas.style.cursor=tool==='orbit'?'grab':'crosshair';}
  setRadius(mm:number){if(!Number.isFinite(mm)||mm<6||mm>40)throw Error('Brush radius');this.radius=mm/1000;}
  private pick(e:PointerEvent) {
    const r=this.canvas.getBoundingClientRect(),ray=new THREE.Raycaster();ray.setFromCamera(new THREE.Vector2((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1),this.adapter.scene.camera);this.surface.mesh.updateWorldMatrix(true,false);
    const hit=ray.intersectObject(this.surface.mesh,false)[0];if(hit?.faceIndex==null)return null;
    const native=ray.intersectObjects([...this.adapter.resources.nodes.values()].filter(n=>n.visible),false)[0];if(native&&native.distance+.008<hit.distance)return null;
    return hit.faceIndex;
  }
  private paint(e:PointerEvent){const face=this.pick(e);if(face===null)return;this.model.apply(this.model.brushFaces(face,this.radius),this.tool==='erase');void this.preview();}
  private pointerEvent=(e:PointerEvent)=>{
    if(this.dead||e.target!==this.canvas||this.tool==='orbit'||(e.type==='pointerdown'&&e.button!==0))return;
    if(e.type==='pointerdown'){e.preventDefault();e.stopImmediatePropagation();this.canvas.focus();this.pointer=e.pointerId;this.model.beginStroke();this.canvas.setPointerCapture(e.pointerId);this.paint(e);}
    else if(this.pointer===e.pointerId){e.preventDefault();e.stopImmediatePropagation();if(e.type==='pointermove')this.paint(e);else if(e.type==='pointerup'){this.pointer=null;this.model.endStroke();this.canvas.releasePointerCapture(e.pointerId);void this.preview();}else this.cancelStroke();}
  };
  private key=(e:KeyboardEvent)=>{if(e.target!==this.canvas||!(e.ctrlKey||e.metaKey))return;if(e.key.toLowerCase()==='z'||e.key.toLowerCase()==='y'){e.preventDefault();e.stopImmediatePropagation();if(this.comparing)return;this.cancelStroke();if(e.key.toLowerCase()==='y'||e.shiftKey)this.model.redo();else this.model.undo();void this.preview();}};
  cancelStroke(){if(this.pointer!==null){const pointer=this.pointer;this.pointer=null;if(this.canvas.hasPointerCapture(pointer))this.canvas.releasePointerCapture(pointer);this.model.cancelStroke();void this.preview();}}
  async preview(before=false){this.comparing=before;const token=++this.generation;try{const mask=before?this.model.base:await this.model.snapshot();if(this.dead||token!==this.generation)return;await this.overlay.replaceTerritoryMasks(mask.triangleIds.length?[mask]:[],mask.channel,JSON.stringify(mask).length,true);if(!this.dead&&token===this.generation)this.changed();}catch(e){if(!this.dead&&token===this.generation)this.failed(e);}}
  dispose(){this.dead=true;this.generation++;this.cancelStroke();for(const type of ['pointerdown','pointermove','pointerup','pointercancel','lostpointercapture'] as const)this.parent.removeEventListener(type,this.pointerEvent,true);this.parent.removeEventListener('keydown',this.key,true);this.canvas.style.cursor='grab';}
}
