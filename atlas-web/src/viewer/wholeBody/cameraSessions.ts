import type { CameraState } from './cameraObservation.ts';
/** Independent return values; only the current owner may cause a return movement. */
export class CameraSessions {
  private sessions = new Map<string,{camera:CameraState; revoke?:()=>void}>();
  owner: string | null = null;
  private returning: {owner:string;camera:CameraState}|null=null;
  returnState(owner:string,current:CameraState){return structuredClone(this.sessions.get(owner)?.camera??(this.returning?.owner===owner?this.returning.camera:current));}
  markReturn(owner:string,camera:CameraState){this.returning={owner,camera:structuredClone(camera)};}
  settleReturn(){this.returning=null;}
  begin(owner:string,camera:CameraState,revoke?:()=>void) {
    const previous=this.owner;
    this.owner=owner;
    const fresh=!this.sessions.has(owner);
    if(fresh)this.sessions.set(owner,{camera:structuredClone(camera),revoke});
    if(previous&&previous!==owner)this.sessions.get(previous)?.revoke?.();
    return fresh;
  }
  end(owner:string,restore=true) {
    const session=this.sessions.get(owner),owns=this.owner===owner;
    this.sessions.delete(owner);
    if(owns)this.owner=[...this.sessions.keys()].at(-1)??null;
    return owns&&restore&&session?structuredClone(session.camera):null;
  }
  clear(){this.sessions.clear();this.owner=null;this.settleReturn();}
}
