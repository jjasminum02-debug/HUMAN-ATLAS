import assert from "node:assert/strict";
import test from "node:test";
import { createHash } from "node:crypto";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { motionAssetsPlugin } from "./motionAssets.ts";

const repositoryRoot = fileURLToPath(new URL("../../", import.meta.url));

test("registered lazy binary delivery rejects unknown paths and corrupted package bytes", async () => {
  const root = await mkdtemp(join(tmpdir(), "t66-motion-delivery-"));
  try {
    await mkdir(join(root, "atlas-data/motion"), { recursive: true });
    await mkdir(join(root, "atlas-data/assets/motion/test"), { recursive: true });
    const uri = "atlas-data/assets/motion/test/motion.glb";
    const bytes = Buffer.from("glTF-delivery-fixture-only");
    await writeFile(join(root, uri), bytes);
    await writeFile(join(root, "atlas-data/motion/motion-learning.json"), JSON.stringify({
      motionAssets: [{ uri, sha256: createHash("sha256").update(bytes).digest("hex") }],
    }));
    await writeFile(join(root, "atlas-data/motion/t66-wave1-registration.json"), JSON.stringify({
      schemaVersion: "t66-wave1-source-motion-registration-v2",
      authority: {
        sourceOnly: true, publicRedistribution: "held", humanReview: "not_performed",
        canonicalTargetMembershipApproved: false,
      },
      packages: [],
    }));
    let middleware!: (
      req: { url: string },
      res: { statusCode: number; setHeader(name: string, value: unknown): void; end(body: unknown): void },
      next: () => void,
    ) => Promise<void>;
    const plugin = motionAssetsPlugin(root);
    (plugin.configureServer as Function)({
      watcher: { add() {}, on() { return undefined; } },
      middlewares: { use: (handler: typeof middleware) => { middleware = handler; } },
    });
    async function request(path: string) {
      const headers: Record<string, unknown> = {};
      const result = {
        statusCode: 200, body: null as unknown, next: false, headers,
        setHeader(name: string, value: unknown) { headers[name] = value; },
        end(body: unknown) { this.body = body; },
      };
      await middleware({ url: path }, result, () => { result.next = true; });
      return result;
    }
    const valid = await request("/" + uri);
    assert.equal(valid.statusCode, 200);
    assert.equal(valid.headers["Content-Type"], "model/gltf-binary");
    assert.deepEqual(valid.body, bytes);
    assert.equal((await request("/atlas-data/assets/motion/unknown.glb")).statusCode, 404);
    assert.equal((await request("/ordinary-page")).next, true);
    await writeFile(join(root, uri), "corrupt");
    assert.equal((await request("/" + uri)).statusCode, 503);
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

const integrationRoot = repositoryRoot;

function harness() {
  let handler: ((request: any, response: any, next: () => void) => Promise<void>) | null = null;
  const watched: string[] = [];
  const listeners = new Map<string, Array<(path: string) => void>>();
  motionAssetsPlugin(integrationRoot).configureServer!({
    watcher: {
      add: (paths: string[]) => { watched.push(...paths); },
      on: (event: string, listener: (path: string) => void) => {
        listeners.set(event, [...(listeners.get(event) ?? []), listener]);
        return undefined as never;
      },
    } as any,
    middlewares: { use: (...args: any[]) => { handler = args.at(-1); } },
  } as any);
  return {
    watched,
    changed(path: string) { for (const listener of listeners.get("change") ?? []) listener(path); },
    async get(url: string) {
      if (!handler) throw new Error("motion asset middleware was not installed");
      let status = 200;
      const headers: Record<string, string> = {};
      let body = Buffer.alloc(0);
      await handler({ url }, {
        set statusCode(value: number) { status = value; },
        get statusCode() { return status; },
        setHeader(name: string, value: string | number) { headers[name.toLowerCase()] = String(value); },
        end(value?: Buffer | string) { body = Buffer.isBuffer(value) ? value : Buffer.from(value ?? ""); },
      }, () => { status = 404; });
      return { status, headers, body };
    },
  };
}

test("wave-1 source-bound GLBs are served lazily through the shared integrity route", async () => {
  const h = harness();
  const registration = JSON.parse(await readFile(integrationRoot + "atlas-data/motion/t66-wave1-registration.json", "utf8"));
  const pkg = registration.packages.find((row: { id: string }) => row.id === "T66-W1-PKG-030");
  assert.ok(pkg);
  assert.ok(h.watched.includes(integrationRoot + "atlas-data/motion/t66-wave1-registration.json"));
  const response = await h.get(`/${pkg.uri}`);
  const sourceBytes = await readFile(integrationRoot + pkg.uri);
  assert.equal(response.status, 200);
  assert.equal(response.headers["content-type"], "model/gltf-binary");
  assert.equal(response.headers["content-length"], String(sourceBytes.byteLength));
  assert.equal(createHash("sha256").update(response.body).digest("hex"), pkg.sha256);
  assert.equal(response.body.byteLength, sourceBytes.byteLength);
  assert.equal((await h.get("/atlas-data/assets/motion/t66-wave1/not-registered.glb")).status, 404);
});
