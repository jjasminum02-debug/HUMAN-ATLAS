// Serve the built app over HTTPS on the local network, for measuring on a real iPad or laptop (ROADMAP 4-1 step 2).
//   pnpm build && pnpm preview:lan
// The app checks geometry hashes with crypto.subtle, which browsers only allow on https (or localhost), so plain
// http://<LAN IP> does not work. A self-signed certificate for this machine's LAN addresses is made with openssl in
// atlas-web/.cert (git-ignored) and remade when the addresses change. The device shows a warning once; continue to the
// site. Nothing leaves the local network.
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { networkInterfaces } from 'node:os';
import { fileURLToPath } from 'node:url';
import { preview } from 'vite';

const web = fileURLToPath(new URL('..', import.meta.url));
const dir = new URL('../.cert/', import.meta.url);
const ips = Object.values(networkInterfaces()).flat().filter(a => a && a.family === 'IPv4' && !a.internal).map(a => a.address);
if (!ips.length) throw new Error('No LAN address: connect to Wi-Fi first.');
const names = ['localhost', '127.0.0.1', ...ips];
const key = new URL('lan.key', dir), cert = new URL('lan.crt', dir), stamp = new URL('names.txt', dir);
if (!existsSync(cert) || !existsSync(stamp) || readFileSync(stamp, 'utf8') !== names.join(',')) {
  mkdirSync(dir, { recursive: true });
  const san = names.map(n => (/^\d+\.\d+\.\d+\.\d+$/.test(n) ? `IP:${n}` : `DNS:${n}`)).join(',');
  execFileSync('openssl', ['req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-days', '30', '-subj', '/CN=HUMAN ATLAS local preview',
    '-addext', `subjectAltName=${san}`, '-keyout', fileURLToPath(key), '-out', fileURLToPath(cert)], { stdio: 'ignore' });
  writeFileSync(stamp, names.join(','));
}
const port = Number(process.env.PORT ?? 4173);
const server = await preview({ root: web, preview: { host: '0.0.0.0', port, strictPort: true,
  https: { key: readFileSync(key), cert: readFileSync(cert) } } });
console.log('\n기기에서 같은 Wi-Fi로 아래 주소를 엽니다(처음 한 번 인증서 경고가 나오면 계속 진행):');
for (const ip of ips) console.log(`  https://${ip}:${port}/?perf=1`);
console.log('끝내려면 Ctrl+C\n');
process.on('SIGINT', () => { server.httpServer.close(); process.exit(0); });
