import * as THREE from 'three';
import { installMuscleSurface } from './muscleSurface.ts';

// Tissue identity must come from the source contract. A muscle's pale ends are not tendon labels.
export type Tissue = 'bone' | 'muscle' | 'nerve' | 'accessory' | 'tendon' | 'fascia' | 'joint';
export type MaterialMode = 'normal' | 'selected' | 'dim' | 'translucent' | 'nerveContext' | 'motorContext' | 'innervated' | 'observationContext' | 'motionContext' | 'originContext' | 'insertionContext';
/** variant: fine tissue (ligament, meniscus, tooth ...); layerOpacity: learner's per-layer opacity (0.1-1);
 * role: M3 movement colouring (muscles producing / opposing the shown movement). */
export type MaterialState = { mode?: MaterialMode; phase?: 'action' | 'return' | null; role?: 'agonist' | 'antagonist'; contextOpacity?: number; userTranslucent?: boolean; hovered?: boolean; variant?: string; layerOpacity?: number };
export const ANATOMY_PALETTE = {
  bone: '#e6dbc2', muscle: '#d48b78', nerve: '#dbbb32', accessory: '#c5bdb1', tendon: '#f1ebdc', fascia: '#e1dde9', joint: '#f6f0e1',
  origin: '#476eb4', insertion: '#bc7135', selected: '#237f79', selectedNerve: '#d0c42f', related: '#338fc1', action: '#df8065', return: '#a4aaa8',
  agonist: '#d4472f', antagonist: '#3f7cc4',
};

// Cartilage-like joint tissue reads blue-white; synovial sacs and sheaths blue; fat pads yellow.
const VARIANT_COLORS: Record<string, string> = {
  meniscus: '#a5c5dc', disc: '#a2c1da', labrum: '#a5c5dc', cartilage: '#b1cde0', cartilaginous_joint: '#a5c5dc',
  capsule: '#d3dfc6', membrane: '#e3ddcc', bursa: '#8dbde0', fat_pad: '#ecd28c', sheath: '#a3cad8', tooth: '#f4f1e8',
};
const VARIANT_OPACITY: Record<string, number> = { bursa: .7, capsule: .85, membrane: .85 };

export function anatomyMaterialParameters(tissue: Tissue, state: MaterialState = {}): THREE.MeshStandardMaterialParameters {
  const mode = state.mode ?? 'normal';
  const base = (state.variant && VARIANT_COLORS[state.variant]) || ANATOMY_PALETTE[tissue];
  const color = new THREE.Color(tissue === 'bone' && mode === 'originContext' ? ANATOMY_PALETTE.origin
    : tissue === 'bone' && mode === 'insertionContext' ? ANATOMY_PALETTE.insertion : mode === 'selected' ? tissue === 'nerve' ? ANATOMY_PALETTE.selectedNerve : ANATOMY_PALETTE.selected
    : mode === 'innervated' || mode === 'motorContext' ? ANATOMY_PALETTE.related : base);
  if (tissue === 'muscle' && state.phase) color.set(ANATOMY_PALETTE[state.phase]);
  if ((tissue === 'muscle' || tissue === 'tendon') && state.role) color.set(ANATOMY_PALETTE[state.role]);
  if (mode === 'dim' && tissue !== 'nerve') color.lerp(new THREE.Color('#e5e5dd'), .48);
  const modeOpacity = mode === 'translucent' || state.userTranslucent ? .3 : mode === 'nerveContext' ? .12 : mode === 'motorContext' ? .5
    : mode === 'observationContext' ? .18 : mode === 'motionContext' ? Math.max(.1, Math.min(.6, state.contextOpacity ?? .3)) : 1;
  // Fascia is a sheet over the muscles: translucent by default unless selected.
  const tissueOpacity = tissue === 'fascia' && mode !== 'selected' ? .5 : (mode === 'selected' ? 1 : VARIANT_OPACITY[state.variant ?? ''] ?? 1);
  const opacity = modeOpacity * tissueOpacity * Math.max(.1, Math.min(1, state.layerOpacity ?? 1));
  const nerve = tissue === 'nerve', selected = mode === 'selected';
  return { color, metalness: 0, roughness: nerve ? selected ? .42 : .55 : tissue === 'bone' ? .62 : tissue === 'muscle' ? .64 : tissue === 'joint' || tissue === 'tendon' ? .45 : .8,
    transparent: opacity < 1, opacity, depthTest: true, depthWrite: opacity === 1,
    // Selection also changes luminance/specular response; tissue identity remains yellow for nerves.
    emissive: nerve ? color : state.hovered ? '#628b83' : '#000000',
    emissiveIntensity: nerve ? selected ? .3 : state.hovered ? .24 : .16 : state.hovered ? .16 : 0 };
}

// Fibrous tissue (ligament, tendon, fascia) reads glossier than bone through a soft sheen; cartilage-like
// joint tissue adds a light clearcoat. Both stay untextured and non-metallic like every other tissue.
const SHEEN_TISSUES = new Set<Tissue>(['joint', 'tendon', 'fascia']);
const CARTILAGE_VARIANTS = new Set(['meniscus', 'disc', 'labrum', 'cartilage', 'cartilaginous_joint']);
function createMaterial(tissue: Tissue, state: MaterialState) {
  const parameters = anatomyMaterialParameters(tissue, state);
  if (!SHEEN_TISSUES.has(tissue)) return new THREE.MeshStandardMaterial(parameters);
  const cartilage = CARTILAGE_VARIANTS.has(state.variant ?? '');
  return new THREE.MeshPhysicalMaterial({ ...parameters, sheen: .55, sheenRoughness: .45, sheenColor: '#ffffff',
    clearcoat: cartilage ? .4 : 0, clearcoatRoughness: .35 });
}

/** One bounded palette per scene/resource owner, never a material or shader per source object. */
export class AnatomyMaterials {
  private readonly instances = new Map<string, THREE.MeshStandardMaterial>();
  private readonly owned = new Set<THREE.Material>();
  get(tissue: Tissue, state: MaterialState = {}) {
    const opacity = state.mode === 'motionContext' ? Math.max(.1, Math.min(.6, state.contextOpacity ?? .3)) : '';
    const layerOpacity = state.layerOpacity === undefined ? '' : Math.round(state.layerOpacity * 20) / 20;
    const key = `${tissue}:${state.mode ?? 'normal'}:${state.phase ?? ''}:${state.role ?? ''}:${Boolean(state.hovered)}:${opacity}${state.userTranslucent ? ':user-translucent' : ''}:${state.variant ?? ''}:${layerOpacity}`;
    let material = this.instances.get(key);
    if (!material) {
      material = createMaterial(tissue, { ...state, layerOpacity: layerOpacity === '' ? undefined : layerOpacity });
      if (tissue === 'muscle') installMuscleSurface(material);
      material.name = key; this.instances.set(key, material); this.owned.add(material);
    }
    return material;
  }
  get size() { return this.instances.size; }
  owns(material: THREE.Material) { return this.owned.has(material); }
  dispose() { for (const material of this.instances.values()) material.dispose(); this.instances.clear(); this.owned.clear(); }
}

/** Same three unshadowed lights and standard PBR shader; no textures, AO pass or extra renderer. */
export function installAnatomyLighting(scene: THREE.Scene, renderer: THREE.WebGLRenderer) {
  scene.background = new THREE.Color('#eff1ef');
  scene.add(new THREE.HemisphereLight(0xffffff, 0x9caaa8, 1.15));
  const key = new THREE.DirectionalLight(0xfff5ed, 2.1); key.position.set(-2, 3, 4); scene.add(key);
  const rim = new THREE.DirectionalLight(0xe0eeee, .85); rim.position.set(2, 1, -3); scene.add(rim);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1;
}
