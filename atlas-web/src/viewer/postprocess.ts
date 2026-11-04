import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/examples/jsm/postprocessing/GTAOPass.js';
import { OutlinePass } from 'three/examples/jsm/postprocessing/OutlinePass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';

/**
 * ROADMAP V2 post-processing for the single anatomy renderer: selection outline on every frame, and
 * ambient occlusion only on a "refine" frame drawn once the camera has settled, so orbiting stays light.
 * Translucent layers (fascia, capsules) are left out of the occlusion depth so they do not darken what lies under them.
 */
export class AnatomyPostprocess {
  private readonly composer: EffectComposer;
  private readonly gtao: GTAOPass;
  private readonly outline: OutlinePass;
  private readonly renderer: THREE.WebGLRenderer;
  ambientOcclusion: boolean;

  constructor(renderer: THREE.WebGLRenderer, scene: THREE.Scene, camera: THREE.Camera, width: number, height: number, ambientOcclusion: boolean) {
    this.renderer = renderer;
    this.ambientOcclusion = ambientOcclusion;
    const target = new THREE.WebGLRenderTarget(1, 1, { type: THREE.HalfFloatType, samples: 4 });
    this.composer = new EffectComposer(renderer, target);
    this.composer.addPass(new RenderPass(scene, camera));
    this.gtao = new GTAOPass(scene, camera, width, height);
    this.gtao.blendIntensity = .75;
    this.gtao.updateGtaoMaterial({ radius: .03, distanceExponent: 1.4, thickness: 1.5, scale: 1, samples: 12 });
    this.gtao.updatePdMaterial({ lumaPhi: 10, depthPhi: 2, normalPhi: 3, radius: 6, rings: 2, samples: 12 });
    this.hideTranslucentFromOcclusion(scene);
    this.composer.addPass(this.gtao);
    this.outline = new OutlinePass(new THREE.Vector2(width, height), scene, camera);
    Object.assign(this.outline, { edgeStrength: 3.5, edgeGlow: 0, edgeThickness: 1.2, pulsePeriod: 0 });
    this.outline.visibleEdgeColor.set('#1d756f'); this.outline.hiddenEdgeColor.set('#1d756f');
    this.composer.addPass(this.outline);
    this.composer.addPass(new OutputPass());
    this.setSize(width, height);
    // Rendering straight to the canvas never tone-mapped the clear colour; through the composer it is.
    if (scene.background instanceof THREE.Color && renderer.toneMapping === THREE.ACESFilmicToneMapping)
      scene.background = preToneMapped(scene.background, renderer.toneMappingExposure);
  }

  /** GTAOPass hides only points/lines while rendering its depth/normal pass; hide translucent meshes too. */
  private hideTranslucentFromOcclusion(scene: THREE.Scene) {
    const pass = this.gtao as unknown as { _overrideVisibility: () => void; _restoreVisibility: () => void };
    const hide = pass._overrideVisibility.bind(this.gtao), restore = pass._restoreVisibility.bind(this.gtao);
    const hidden: THREE.Object3D[] = [];
    pass._overrideVisibility = () => {
      hide();
      scene.traverse(object => {
        const material = (object as THREE.Mesh).material as THREE.Material | undefined;
        if ((object as THREE.Mesh).isMesh && object.visible && material && !Array.isArray(material) && material.transparent) { object.visible = false; hidden.push(object); }
      });
    };
    pass._restoreVisibility = () => { for (const object of hidden) object.visible = true; hidden.length = 0; restore(); };
  }

  setSize(width: number, height: number) {
    this.composer.setPixelRatio(this.renderer.getPixelRatio());
    this.composer.setSize(width, height);
  }

  setOutline(objects: THREE.Object3D[]) { this.outline.selectedObjects = objects; }

  /** refine=true adds ambient occlusion (when enabled); otherwise a light frame for interaction. */
  render(refine: boolean) {
    this.gtao.enabled = refine && this.ambientOcclusion;
    this.composer.render();
  }

  dispose() { this.composer.dispose(); this.gtao.dispose(); this.outline.dispose(); }
}

// three.js ACESFilmicToneMapping (same fit and matrices as its shader chunk), applied to linear RGB.
export function acesFilmic([r, g, b]: number[], exposure: number) {
  const s = exposure / .6; [r, g, b] = [r * s, g * s, b * s];
  const v = [.59719 * r + .35458 * g + .04823 * b, .076 * r + .90834 * g + .01566 * b, .0284 * r + .13383 * g + .83777 * b]
    .map(x => (x * (x + .0245786) - .000090537) / (x * (.983729 * x + .432951) + .238081));
  return [1.60475 * v[0] - .53108 * v[1] - .07367 * v[2], -.10208 * v[0] + 1.10813 * v[1] - .00605 * v[2], -.00327 * v[0] - .07276 * v[1] + 1.07602 * v[2]]
    .map(x => Math.min(1, Math.max(0, x)));
}

/** The linear colour that ACES maps back onto `target`, found by fixed-point iteration (near-neutral colours converge). */
export function preToneMapped(target: THREE.Color, exposure = 1) {
  const goal = [target.r, target.g, target.b];
  let x = [...goal];
  for (let i = 0; i < 60; i++) {
    const y = acesFilmic(x, exposure);
    x = x.map((value, c) => Math.max(1e-4, value * goal[c] / Math.max(1e-4, y[c])));
  }
  return new THREE.Color().setRGB(x[0], x[1], x[2], THREE.LinearSRGBColorSpace);
}

/** Ambient occlusion by default on desktop-class devices; touch/low-core devices start without it. */
export function defaultAmbientOcclusion() {
  if (typeof window === 'undefined') return false;
  const coarse = window.matchMedia?.('(pointer: coarse)').matches;
  return !coarse && (navigator.hardwareConcurrency ?? 4) >= 4;
}
