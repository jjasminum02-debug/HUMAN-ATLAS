export const LUNG_ORDER=Array.from({length:11},(_,i)=>`LU${i+1}`);
export const LUNG_SECTIONS=[{name:'가슴',codes:['LU1','LU2']},{name:'위팔',codes:['LU3','LU4']},{name:'팔꿈치·아래팔',codes:['LU5','LU6','LU7','LU8']},{name:'손목·엄지',codes:['LU9','LU10','LU11']}];
export function sectionFor(code:string,sections:{codes:string[]}[]=LUNG_SECTIONS){return sections.findIndex(s=>s.codes.includes(code));}
/** Deterministic clock, shared with the existing scene update. No timer/RAF owner. */
export class PointTour {
  state:'ready'|'touring'|'paused'='ready'; index=0; elapsed=0; autoReturn=true;
  private select:(index:number,focus:boolean)=>void; private finish:()=>void; private changed:(state:PointTour['state'])=>void;
  readonly order:typeof LUNG_ORDER;readonly sections:{codes:string[]}[];
  constructor(select:(index:number,focus:boolean)=>void,finish:()=>void,changed:(state:PointTour['state'])=>void,order=LUNG_ORDER,sections:{codes:string[]}[]=LUNG_SECTIONS){this.order=order;this.sections=sections;this.select=select;this.finish=finish;this.changed=changed;}
  private section(code:string){return this.sections.findIndex(s=>s.codes.includes(code));}
  play(){if(this.index===this.order.length-1)this.index=0;this.autoReturn=true;this.elapsed=0;this.state='touring';this.select(this.index,true);this.changed(this.state);}
  pause(manual=false){this.state='paused';this.elapsed=0;if(manual)this.autoReturn=false;this.changed(this.state);}
  step(delta:number){this.pause();this.index=Math.max(0,Math.min(this.order.length-1,this.index+delta));this.select(this.index,true);}
  choose(index:number){this.pause();this.index=Math.max(0,Math.min(this.order.length-1,index));this.select(index,true);}
  tick(dt:number){if(this.state!=='touring')return false;this.elapsed+=dt;if(this.elapsed<3.2)return false;this.elapsed=0;
    if(this.index===this.order.length-1){this.state='ready';this.changed(this.state);if(this.autoReturn)this.finish();return false;}
    const previous=this.section(this.order[this.index]);this.index++;this.select(this.index,this.section(this.order[this.index])!==previous);return true;
  }
}
