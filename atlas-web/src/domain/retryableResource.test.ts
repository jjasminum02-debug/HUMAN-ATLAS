import assert from 'node:assert/strict';
import test from 'node:test';
import { retryableResource } from './retryableResource.ts';

test('concurrent feature requests share work and retain the successful module', async () => {
  let calls = 0;
  const feature = { version: 1 };
  let resolve!: (value: typeof feature) => void;
  const load = retryableResource(() => { calls++; return new Promise<typeof feature>(done => { resolve = done; }); });
  assert.equal(calls, 0);
  const first = load(), second = load();
  assert.equal(first, second);
  await Promise.resolve();
  assert.equal(calls, 1);
  resolve(feature);
  assert.equal(await first, feature);
  assert.equal(await load(), feature);
  assert.equal(calls, 1);
});

test('failed feature requests reject all callers and allow one fresh retry', async () => {
  let calls = 0;
  const load = retryableResource(async () => { if (++calls === 1) throw Error('offline'); return 'ready'; });
  const results = await Promise.allSettled([load(), load()]);
  assert.ok(results.every(result => result.status === 'rejected'));
  assert.equal(calls, 1);
  assert.deepEqual(await Promise.all([load(), load()]), ['ready', 'ready']);
  assert.equal(calls, 2);
});

test('synchronous loader failures also release the retry slot', async () => {
  let calls = 0;
  const load = retryableResource(() => { if (++calls === 1) throw Error('setup'); return Promise.resolve(true); });
  await assert.rejects(load(), /setup/);
  assert.equal(await load(), true);
});
