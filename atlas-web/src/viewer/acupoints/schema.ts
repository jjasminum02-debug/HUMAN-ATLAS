/** Point text, model placement, routes and independently authored areas have separate revisions. */
export type Side = 'right' | 'left' | 'midline';
export type Vec3 = [number, number, number];
export interface SourceRef { id: string; title: string; edition: string | null; locator: string | null; url?: string }
export interface SourcedText { text: string; sources: SourceRef[]; interpretation: 'source_summary' | 'ai_proposal' | 'lecture' }
export interface PointConcept {
  code: string; nameKo: string; romanization: string; aliases: string[]; channel: string; revision: string;
  nameSources?: SourceRef[]; standard: SourceRef; textbook: SourceRef | null;
  location: SourcedText | null; posture: SourcedText | null; explanation: SourcedText | null;
  measurements: { kind: 'B-cun' | 'F-cun' | 'landmark'; value: number | null; reference: string }[];
}
export interface Carrier {
  id: string; revision: string; topologySha256: string; datasetRevision: string;
  frameId: string; unit: 'm'; poseId: string; side: Side;
  kind: 'source_skin' | 'registered_skin' | 'authored_teaching_surface'; precision: 'coarse_not_skin' | 'landmarks_verified';
  positions: number[]; indices: number[];
  rights: { source: string; localObservation: 'supported' | 'held'; publicRedistribution: 'held' | 'supported'; professorReview: 'not_performed' | 'reviewed' };
}
export interface PointInstance {
  code: string; side: Side; revision: string; carrierId: string; carrierRevision: string; carrierHash: string;
  frameId: string; unit: 'm'; poseId: string;
  triangle: number; barycentric: Vec3; landmarkSourceKeys: string[];
  locationValidation: 'unresolved' | 'landmarks_verified'; aiProposal: boolean;
  professorReview: 'not_performed' | 'reviewed'; missing: string[];
}
export interface ChannelRoute {
  id: string; channel: string; side: Side; revision: string;
  kind: 'surface_teaching' | 'classical_external' | 'internal'; sources: SourceRef[];
  segments: { id: string; branchOf: string | null; direction: 'forward' | 'reverse' | 'unspecified'; anchors: PointInstance[] }[];
  teachingPointOrder: string[];
}
export interface Territory {
  id: string; channel: string; side: Side; revision: string;
  kind: 'teaching_region' | 'cutaneous' | 'sinew_projection'; carrierHash: string; boundaryRevision: string;
  triangleMask: { triangle: number; weight: number }[]; sources: SourceRef[];
  interpretation: 'source_summary' | 'ai_proposal' | 'lecture'; professorReview: 'not_performed' | 'reviewed';
}
export interface SinewPath { id: string; revision: string; sources: SourceRef[]; branches: SourcedText[]; muscles: { sourceKey: string; part: string | null; evidence: SourcedText }[] }
export interface LearningAssociation { id: string; revision: string; from: string; to: string | null; kind: 'spatial_context' | 'lecture_association'; explanation: SourcedText | null; unresolvedOriginal: string | null }
export type LearningSelection = { kind: 'anatomy'; sourceKey: string } | { kind: 'acupoint'; code: string; side: Side } | { kind: 'territory'; id: string };
/** Only independently verified placements qualify; development proposals cannot be exported as learner points. */
export function productInstances(carrier: Carrier, instances: PointInstance[]) {
  return carrier.precision === 'landmarks_verified' && carrier.rights.localObservation === 'supported'
    ? instances.filter(i => i.locationValidation === 'landmarks_verified' && !i.aiProposal && i.missing.length === 0) : [];
}
