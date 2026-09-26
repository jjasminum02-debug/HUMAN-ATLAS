import assert from "node:assert/strict";
import test from "node:test";
import { SceneRequestCache } from "./sceneCache.ts";

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason: unknown) => void;
  const promise = new Promise<T>((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

test("same revision shares one request, a changed revision fetches again", async () => {
  const cache = new SceneRequestCache<string>();
  let calls = 0;
  const request = async () => { calls += 1; return `scene-${calls}`; };
  const signal = new AbortController().signal;
  const [a, b] = await Promise.all([cache.acquire("leg@a", request, signal), cache.acquire("leg@a", request, signal)]);
  assert.equal(a, "scene-1");
  assert.equal(b, "scene-1");
  assert.equal(await cache.acquire("leg@a", request, signal), "scene-1");
  assert.equal(await cache.acquire("leg@b", request, signal), "scene-2");
  assert.equal(calls, 2);
});

test("abandoned response cannot enter cache or replace the current scene", async () => {
  const cache = new SceneRequestCache<string>();
  const old = deferred<string>();
  const oldController = new AbortController();
  const pending = cache.acquire("leg@a", () => old.promise, oldController.signal);
  oldController.abort();
  await assert.rejects(pending, { name: "AbortError" });
  assert.equal(await cache.acquire("head@b", async () => "current", new AbortController().signal), "current");
  old.resolve("late old scene");
  let newCalls = 0;
  assert.equal(await cache.acquire("leg@a", async () => { newCalls += 1; return "fresh"; }, new AbortController().signal), "fresh");
  assert.equal(newCalls, 1);
});

test("one caller may cancel a shared request without cancelling the other", async () => {
  const cache = new SceneRequestCache<string>();
  const work = deferred<string>();
  const first = new AbortController();
  const second = new AbortController();
  const a = cache.acquire("leg@a", () => work.promise, first.signal);
  const b = cache.acquire("leg@a", () => { throw new Error("duplicate fetch"); }, second.signal);
  first.abort();
  await assert.rejects(a, { name: "AbortError" });
  work.resolve("shared");
  assert.equal(await b, "shared");
});

test("failed request is removed so reselection can retry", async () => {
  const cache = new SceneRequestCache<string>();
  await assert.rejects(cache.acquire("leg@a", async () => { throw new Error("404"); }, new AbortController().signal), /404/);
  assert.equal(await cache.acquire("leg@a", async () => "ready", new AbortController().signal), "ready");
});

test("resolved CPU cache evicts the oldest revision at capacity", async () => {
  const cache = new SceneRequestCache<string>(2);
  const signal = new AbortController().signal;
  let calls = 0;
  const request = async () => `version-${++calls}`;
  await cache.acquire("a", request, signal);
  await cache.acquire("b", request, signal);
  await cache.acquire("c", request, signal);
  assert.equal(await cache.acquire("a", request, signal), "version-4");
});

test("capacity is enforced after five different in-flight requests resolve together", async () => {
  const cache = new SceneRequestCache<string>(2);
  const keys = ["a", "b", "c", "d", "e"];
  const jobs = new Map(keys.map((key) => [key, deferred<string>()]));
  const calls = new Map(keys.map((key) => [key, 0]));
  const controllers = keys.map(() => new AbortController());
  const pending = keys.map((key, index) => cache.acquire(key, (signal) => {
    calls.set(key, calls.get(key)! + 1);
    signal.addEventListener("abort", () => jobs.get(key)!.reject(new DOMException("aborted", "AbortError")), { once: true });
    return jobs.get(key)!.promise;
  }, controllers[index].signal));

  for (const key of keys) jobs.get(key)!.resolve(`first-${key}`);
  assert.deepEqual(await Promise.all(pending), keys.map((key) => `first-${key}`));

  // The oldest resolved entries must be evicted after their final subscribers leave.
  assert.equal(await cache.acquire("a", async () => { calls.set("a", calls.get("a")! + 1); return "second-a"; }, new AbortController().signal), "second-a");
  assert.equal(calls.get("a"), 2);
});
