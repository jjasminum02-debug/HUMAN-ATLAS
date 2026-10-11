#!/usr/bin/env node
import { createServer } from "node:http";
import { createReadStream } from "node:fs";
import { mkdir, readFile, stat, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { dirname, extname, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "../../../..");
const run = resolve(here, "../2026-10-11-run-01");
const port = Number(process.env.MV1_REVIEW_PORT ?? 5184);
const mime = { ".html":"text/html; charset=utf-8", ".json":"application/json; charset=utf-8", ".mjs":"text/javascript; charset=utf-8", ".js":"text/javascript; charset=utf-8", ".css":"text/css; charset=utf-8", ".png":"image/png", ".jpg":"image/jpeg", ".webm":"video/webm" };
const send = (res, status, type, body) => { res.writeHead(status, { "content-type": type, "cache-control":"no-store" }); res.end(body); };
const digest = (bytes) => createHash("sha256").update(bytes).digest("hex");
const safeFile = (name) => /^[a-zA-Z0-9][a-zA-Z0-9._/-]{0,220}$/.test(name) && !name.split("/").includes("..") && !name.startsWith("/");

const server = createServer(async (req, res) => {
  try {
    const url = new URL(req.url ?? "/", `http://127.0.0.1:${port}`);
    if (req.method === "GET" && url.pathname === "/") {
      return send(res, 200, mime[".html"], await readFile(resolve(here, "review.html")));
    }
    if (req.method === "GET" && url.pathname === "/inventory.json") {
      return send(res, 200, mime[".json"], await readFile(resolve(run, "inventory.json")));
    }
    if (req.method === "GET" && url.pathname === "/playback-v3.webm") {
      const file = resolve(run, "visual/full-playback/muscle-playback-cycle-v3.webm");
      const info = await stat(file);
      const range = req.headers.range;
      if (range) {
        const match = /^bytes=(\d*)-(\d*)$/.exec(range);
        if (!match) return send(res, 416, "text/plain", "invalid range");
        const start = match[1] ? Number(match[1]) : 0;
        const end = match[2] ? Math.min(Number(match[2]), info.size - 1) : info.size - 1;
        if (start > end || start >= info.size) return send(res, 416, "text/plain", "range outside video");
        res.writeHead(206, { "content-type":"video/webm", "content-length":end-start+1, "content-range":`bytes ${start}-${end}/${info.size}`, "accept-ranges":"bytes", "cache-control":"no-store" });
        return createReadStream(file, { start, end }).pipe(res);
      }
      res.writeHead(200, { "content-type":"video/webm", "content-length":info.size, "accept-ranges":"bytes", "cache-control":"no-store" });
      return createReadStream(file).pipe(res);
    }
    if (req.method === "GET" && url.pathname === "/playback-v3") {
      const html = `<!doctype html><meta charset="utf-8"><title>MV1 full-cycle visual review</title><style>html,body{margin:0;background:#10161b;color:#eef4f5;font:14px system-ui}main{padding:12px}video{width:min(96vw,1280px);height:auto;display:block;margin-top:10px}p{margin:4px 0;color:#aebfc4}</style><main><b>MV1 · 74 muscle playback groups · emitted GLB source-bound render</b><p>Continuous 12 fps review recording. Technical rendering does not approve physiological naturalness.</p><video id="v" controls autoplay muted playsinline src="/playback-v3.webm"></video><script>const q=new URLSearchParams(location.search),v=document.getElementById('v'),rate=Number(q.get('rate')||1),start=Number(q.get('start')||0);v.playbackRate=Number.isFinite(rate)&&rate>0?rate:1;v.addEventListener('loadedmetadata',()=>{if(start>0)try{v.currentTime=start}catch{};v.play().catch(()=>{})},{once:true});</script></main>`;
      return send(res, 200, "text/html; charset=utf-8", html);
    }
    if (req.method === "GET" && url.pathname.startsWith("/vendor/three/")) {
      const name = decodeURIComponent(url.pathname.slice("/vendor/three/".length));
      if (!safeFile(name)) return send(res, 400, "text/plain", "invalid path");
      const file = resolve(root, "atlas-web/node_modules/three", name);
      if (!file.startsWith(resolve(root, "atlas-web/node_modules/three") + sep)) return send(res, 403, "text/plain", "outside package");
      return send(res, 200, mime[extname(file)] ?? "application/octet-stream", await readFile(file));
    }
    if (req.method === "GET" && url.pathname.startsWith("/asset/")) {
      const name = decodeURIComponent(url.pathname.slice("/asset/".length));
      if (!safeFile(name) || !name.endsWith(".glb")) return send(res, 400, "text/plain", "invalid asset path");
      const file = resolve(root, name);
      if (!file.startsWith(resolve(root, "atlas-data/assets/motion") + sep)) return send(res, 403, "text/plain", "outside motion assets");
      const info = await stat(file);
      res.writeHead(200, { "content-type":"model/gltf-binary", "content-length":info.size, "cache-control":"no-store" });
      return createReadStream(file).pipe(res);
    }
    if (req.method === "POST" && url.pathname === "/save") {
      const rel = decodeURIComponent(url.searchParams.get("path") ?? "");
      if (!safeFile(rel) || !["visual/", "metrics/", "runtime/"].some((prefix) => rel.startsWith(prefix))) return send(res, 400, "text/plain", "evidence path rejected");
      const chunks = []; let size = 0;
      for await (const chunk of req) { size += chunk.length; if (size > 80 * 1024 * 1024) return send(res, 413, "text/plain", "evidence too large"); chunks.push(chunk); }
      const bytes = Buffer.concat(chunks);
      const file = resolve(run, rel);
      if (!file.startsWith(run + sep)) return send(res, 403, "text/plain", "outside evidence root");
      await mkdir(dirname(file), { recursive: true });
      await writeFile(file, bytes);
      return send(res, 200, mime[extname(file)] ?? "application/octet-stream", JSON.stringify({ path: rel, bytes: bytes.length, sha256: digest(bytes) }));
    }
    return send(res, 404, "text/plain", "not found");
  } catch (error) { return send(res, 500, "text/plain", String(error?.stack ?? error)); }
});
server.listen(port, "127.0.0.1", () => console.log(JSON.stringify({ status:"listening", origin:`http://127.0.0.1:${port}`, runDirectory:run, repositoryRoot:root })));
