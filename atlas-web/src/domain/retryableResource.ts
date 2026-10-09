/** Share pending/successful work; a failed request may be explicitly retried. */
export function retryableResource<T>(load: () => Promise<T>): () => Promise<T> {
  let pending: Promise<T> | undefined;
  return () => pending ??= Promise.resolve().then(load).catch(error => {
    pending = undefined;
    throw error;
  });
}
