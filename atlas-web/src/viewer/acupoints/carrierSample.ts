import type { Carrier } from './schema.ts';
import { validateCarrier, verifyCarrierHash, type AnchorContext } from './anchorAdapter.ts';

export interface CarrierSample {
  schemaVersion: 1; usage: 'development_review_only'; carrier: Carrier;
  referencePositions: number[]; referenceHash: string; label: string; clearanceMetres: number;
  acceptedAcupoints: 0;
}
/** The native basis is fascia/muscle, not skin. Both modes retain one fixed sampled topology. */
export async function validateCarrierSample(data: CarrierSample, context: AnchorContext) {
  if (data.schemaVersion !== 1 || data.usage !== 'development_review_only' || data.acceptedAcupoints !== 0
    || data.carrier.kind !== 'authored_teaching_surface' || data.carrier.precision !== 'coarse_not_skin'
    || !Number.isFinite(data.clearanceMetres) || data.clearanceMetres <= 0 || data.clearanceMetres > .01
    || data.referencePositions.length !== data.carrier.positions.length) throw Error('Invalid bounded surface sample');
  validateCarrier(data.carrier, context);
  await verifyCarrierHash(data.carrier);
  const reference = { ...data.carrier, positions: data.referencePositions, topologySha256: data.referenceHash };
  validateCarrier(reference, context);
  await verifyCarrierHash(reference);
  for (let i=0;i<data.referencePositions.length;i+=3) {
    const distance=Math.hypot(...[0,1,2].map(k=>data.carrier.positions[i+k]-data.referencePositions[i+k]));
    if (Math.abs(distance-data.clearanceMetres) > 1e-6) throw Error('Surface sample offset/unit mismatch');
  }
}
