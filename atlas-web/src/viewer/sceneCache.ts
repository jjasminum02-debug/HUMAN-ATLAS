/** CPU-only scene cache. WebGL resources belong to the mounted ThreeViewer. */
export class SceneRequestCache<T> {
  private readonly capacity: number;
  private readonly entries = new Map<string, {
    controller: AbortController;
    promise: Promise<T>;
    pending: boolean;
    subscribers: number;
  }>();

  constructor(capacity = 2) { this.capacity = capacity; }

  acquire(key: string, request: (signal: AbortSignal) => Promise<T>, signal: AbortSignal): Promise<T> {
    if (signal.aborted) return Promise.reject(new DOMException("Scene loading cancelled", "AbortError"));
    let entry = this.entries.get(key);
    if (!entry) {
      const controller = new AbortController();
      entry = { controller, pending: true, subscribers: 0, promise: undefined as unknown as Promise<T> };
      const current = entry;
      current.promise = request(controller.signal).then((value) => {
        if (controller.signal.aborted) throw new DOMException("Scene loading cancelled", "AbortError");
        current.pending = false;
        this.trim();
        return value;
      }, (error: unknown) => {
        if (this.entries.get(key) === current) this.entries.delete(key);
        throw error;
      });
      this.entries.set(key, current);
    }
    entry.subscribers += 1;
    const current = entry;
    return new Promise<T>((resolve, reject) => {
      let done = false;
      const finish = () => {
        if (done) return false;
        done = true;
        signal.removeEventListener("abort", onAbort);
        current.subscribers -= 1;
        if (current.subscribers === 0 && current.pending) {
          current.controller.abort();
          if (this.entries.get(key) === current) this.entries.delete(key);
        }
        this.trim();
        return true;
      };
      const onAbort = () => {
        if (finish()) reject(new DOMException("Scene loading cancelled", "AbortError"));
      };
      signal.addEventListener("abort", onAbort, { once: true });
      current.promise.then((value) => { if (finish()) resolve(value); }, (error: unknown) => { if (finish()) reject(error); });
      if (signal.aborted) onAbort();
    });
  }

  private trim(): void {
    while (this.entries.size > this.capacity) {
      const first = [...this.entries].find(([, entry]) => !entry.pending && entry.subscribers === 0);
      if (!first) break;
      this.entries.delete(first[0]);
    }
  }
}
