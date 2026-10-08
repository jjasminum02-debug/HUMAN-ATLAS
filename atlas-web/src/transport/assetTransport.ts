/** One optional hosting map; source manifests and decoded SHA/geometry contracts remain unchanged. */
export interface AssetTransportConfig { revision: string; urls: Record<string,string>; inspection?: boolean }
declare global { interface Window { __ATLAS_ASSET_TRANSPORT__?: AssetTransportConfig } }
// Reuse existing development counters only in the explicit loopback package preview.
// This never enables profiling for the public HTTPS delivery configuration.
export const ASSET_INSPECTION_ENABLED = Boolean(import.meta.env?.DEV || (typeof window !== 'undefined'
  && ['127.0.0.1', 'localhost', '[::1]'].includes(window.location.hostname)
  && window.__ATLAS_ASSET_TRANSPORT__?.inspection === true));
export function resolveAssetUrl(input: string | URL, base: string, config?: AssetTransportConfig): string {
  const source=new URL(input,base);
  if(!config)return source.href;
  if(!config.revision || !config.urls || typeof config.urls!=='object')throw Error('Invalid asset transport configuration');
  // Only exact same-origin logical assets can be redirected. Queries are not dropped silently.
  if(source.origin!==new URL(base).origin || source.search || source.hash)return source.href;
  const target=config.urls[source.pathname];if(target===undefined)return source.href;
  const url=new URL(target);
  const loopback=['127.0.0.1','localhost','[::1]'].includes(url.hostname);
  if(url.username||url.password||url.search||url.hash||!(url.protocol==='https:'||url.protocol==='http:'&&loopback)
    ||!/^\/[a-f0-9]{64}\.glb$/.test(url.pathname))throw Error('Invalid immutable asset URL');
  return url.href;
}
/** Native fetch cancellation and retry behavior; no second cache, proxy, or background fetch. */
export const fetchAtlasAsset: typeof fetch = (input,init) => {
  const base=window.location.href, config=window.__ATLAS_ASSET_TRANSPORT__;
  if(input instanceof Request){
    const mapped=resolveAssetUrl(input.url,base,config);
    return fetch(mapped===input.url?input:new Request(mapped,input),init);
  }
  return fetch(resolveAssetUrl(input,base,config),init);
};
