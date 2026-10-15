import type { SkinMaterialPackage } from './skinMaterial.ts';
import type { AnchorContext } from '../acupoints/anchorAdapter.ts';
import { DATASET_BUDGET } from '../datasets/schema.ts';

/** Compact delivery contract. Source authoring/evidence stay outside the learner bundle. */
export interface SkinAsset extends AnchorContext {
  appearance?: SkinMaterialPackage;
  schemaVersion: 1;
  id: string;
  revision: string;
  url: string;
  sha256: string;
  topologySha256: string;
  bytes: number;
  geometryBytes: number;
  triangles: number;
  mappingSha256: string;
  landmarkRevision: string | null;
  geometryAccepted: boolean;
  learnerEligible: boolean;
  localObservation: 'supported' | 'held';
  publicRedistribution: 'supported' | 'held';
  author: 'ai' | 'human';
  professorReview: 'not_performed' | 'reviewed';
  staticPoseOnly: true;
}
export interface SkinCost { encodedBytes: number; geometryBytes: number; triangles: number; textureBytes?: number }
export function validateSkinAsset(a: SkinAsset, c: AnchorContext, review = false) {
  if (a.schemaVersion !== 1 || !a.id || !a.revision || !a.url || a.unit !== 'm' || c.unit !== 'm'
    || a.datasetRevision !== c.datasetRevision || a.frameId !== c.frameId || a.poseId !== c.poseId
    || a.staticPoseOnly !== true) throw Error('Skin frame/unit/pose/dataset');
  if (![a.sha256, a.topologySha256, a.mappingSha256].every(h => /^[a-f0-9]{64}$/.test(h))
    || ![a.bytes, a.geometryBytes, a.triangles].every(n => Number.isSafeInteger(n) && n > 0)
    || a.bytes > DATASET_BUDGET.chunkBytes) throw Error('Skin hash/cost contract');
  if (a.localObservation !== 'supported') throw Error('Skin local observation rights');
  if (!review && (!a.geometryAccepted || !a.learnerEligible || !a.landmarkRevision)) throw Error('Fitted whole skin is not learner eligible');
}
export function skinWithinBudget(base: SkinCost, skin: SkinCost, extra: SkinCost = {encodedBytes:0,geometryBytes:0,triangles:0}) {
  return base.encodedBytes + skin.encodedBytes + extra.encodedBytes <= DATASET_BUDGET.overviewBytes
    && base.geometryBytes + skin.geometryBytes + extra.geometryBytes + (base.textureBytes??0) + (skin.textureBytes??0) + (extra.textureBytes??0) <= DATASET_BUDGET.geometryBytes
    && base.triangles + skin.triangles + extra.triangles <= DATASET_BUDGET.triangles;
}
/** No fitted whole skin has passed. A local hand checkpoint must never fill this slot. */
export const registeredSkin: SkinAsset | null = null;
