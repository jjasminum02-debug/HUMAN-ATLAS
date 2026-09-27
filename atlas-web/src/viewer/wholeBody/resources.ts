/** One bounded queue; demand changes cancel stale work without discarding loaded resources. */
export class ResourceQueue<T> {
  loaded = new Map<string, T>();
  failed = new Set<string>();
  pending = new Map<string, AbortController>();
  wanted = new Set<string>();
  disposed = false;
  readonly load: (id: string, signal: AbortSignal) => Promise<T>;
  readonly release: (item: T) => void;
  readonly changed: () => void;
  readonly limit: number;
  constructor(load: (id: string, signal: AbortSignal) => Promise<T>, release: (item: T) => void, changed: () => void, limit = 2) {
    this.load = load; this.release = release; this.changed = changed; this.limit = limit;
  }
  demand(ids: string[]) {
    this.wanted = new Set(ids);
    for (const [id, controller] of this.pending) if (!this.wanted.has(id)) controller.abort();
    this.pump();
  }
  retry() { this.failed.clear(); this.pump(); }
  pump() {
    if (this.disposed) return;
    for (const id of this.wanted) {
      if (this.pending.size >= this.limit) break;
      if (this.loaded.has(id) || this.failed.has(id) || this.pending.has(id)) continue;
      const controller = new AbortController(); this.pending.set(id, controller);
      void this.load(id, controller.signal).then(item => {
        if (this.disposed || controller.signal.aborted || !this.wanted.has(id)) this.release(item);
        else this.loaded.set(id, item);
      }).catch(() => { if (!controller.signal.aborted && !this.disposed) this.failed.add(id); })
        .finally(() => { this.pending.delete(id); if (!this.disposed) { this.changed(); this.pump(); } });
    }
    this.changed();
  }
  dispose() {
    this.disposed = true;
    for (const controller of this.pending.values()) controller.abort();
    for (const item of this.loaded.values()) this.release(item);
    this.loaded.clear();
  }
}
