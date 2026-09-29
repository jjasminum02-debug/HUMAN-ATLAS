export interface ResourceBudget<T> { maxBytes: number; measure: (item: T) => number }
/** Bounded concurrency and LRU. Wanted/pinned entries cannot be evicted to admit other work. */
export class ResourceQueue<T> {
  loaded = new Map<string,T>(); failed = new Set<string>();
  pending = new Map<string,AbortController>(); wanted = new Set<string>(); pinned = new Set<string>();
  disposed=false; bytes=0; evictions=0;
  private sizes=new Map<string,number>();
  readonly load: (id:string,signal:AbortSignal)=>Promise<T>;
  readonly release:(item:T)=>void; readonly changed:()=>void; readonly limit:number;
  readonly budget:ResourceBudget<T>;
  constructor(load:(id:string,signal:AbortSignal)=>Promise<T>,release:(item:T)=>void,changed:()=>void,limit=2,budget:ResourceBudget<T>={maxBytes:Infinity,measure:()=>0}) {
    if(limit<1 || budget.maxBytes<0) throw Error('invalid resource budget');
    this.load=load;this.release=release;this.changed=changed;this.limit=limit;this.budget=budget;
  }
  demand(ids:string[],pins:string[]=[]) {
    if(this.disposed) return;
    this.pinned=new Set(pins);this.wanted=new Set([...ids,...pins]);
    for(const id of this.wanted) {const item=this.loaded.get(id);if(item!==undefined) {this.loaded.delete(id);this.loaded.set(id,item);}}
    for(const [id,c] of this.pending) if(!this.wanted.has(id)) c.abort();
    this.pump();
  }
  retry() {this.failed.clear();this.pump();}
  private admit(id:string,item:T) {
    const bytes=this.budget.measure(item);
    if(!Number.isFinite(bytes) || bytes<0 || bytes>this.budget.maxBytes) return false;
    for(const [key,old] of this.loaded) {
      if(this.bytes+bytes<=this.budget.maxBytes) break;
      if(this.wanted.has(key)||this.pinned.has(key)) continue;
      this.loaded.delete(key);this.bytes-=this.sizes.get(key)??0;this.sizes.delete(key);this.release(old);this.evictions++;
    }
    if(this.bytes+bytes>this.budget.maxBytes) return false;
    this.loaded.set(id,item);this.sizes.set(id,bytes);this.bytes+=bytes;return true;
  }
  pump() {
    if(this.disposed) return;
    for(const id of this.wanted) {
      if(this.pending.size>=this.limit) break;
      if(this.loaded.has(id)||this.failed.has(id)||this.pending.has(id)) continue;
      const c=new AbortController();this.pending.set(id,c);
      let loading:Promise<T>;
      try {loading=this.load(id,c.signal);}catch(error){loading=Promise.reject(error);}
      void loading.then(item=> {
        if(this.disposed||c.signal.aborted||!this.wanted.has(id)) this.release(item);
        else if(!this.admit(id,item)) {this.release(item);this.failed.add(id);}
      }).catch(()=> {if(!c.signal.aborted&&!this.disposed) this.failed.add(id);})
        .finally(()=> {if(this.pending.get(id)===c)this.pending.delete(id);if(!this.disposed){this.changed();this.pump();}});
    }
    this.changed();
  }
  dispose() {
    if(this.disposed) return;this.disposed=true;
    for(const c of this.pending.values())c.abort();
    this.pending.clear();
    for(const item of this.loaded.values())this.release(item);
    this.loaded.clear();this.sizes.clear();this.wanted.clear();this.pinned.clear();this.bytes=0;
  }
}
