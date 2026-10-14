/** Point text, model placement, routes and independently authored areas have separate revisions. */
import { localLearnerEligible } from './placementPolicy.ts';
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
  /** Bilateral immutable reference surface; side of each anchor/mask is checked separately. */
  coverage?: 'whole_body';
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
  /** V1 fields remain intact; this independent V2 assessment does not erase AI authorship. */
  assessment?: PlacementAssessment;
}
export interface PlacementAssessment {
  schemaVersion: 2; policyVersion: 'landmark-evidence-v2';
  scope: 'real_input' | 'technical_fixture';
  inputDomain:'real_input'|'technical_fixture';
  technical: 'not_checked' | 'passed' | 'failed';
  precision: 'unresolved' | 'educational_approximation';
  basis: 'landmark' | 'B-cun' | 'F-cun' | 'legacy_unresolved';
  author: 'ai' | 'human' | 'unknown'; inputSha256: string; compilerVersion: string;
  /** Exact frozen binding checked by the compiler, including the barycentric tuple. */
  checkedBinding: string | null;
  contextReferences?: {id:string; sourceKey:string; anatomy:string; evidenceSha256:string}[];
  landmarks: { id: string; anatomy: string; sourceKey: string; evidenceSha256: string;
    modelIndicator?:{kind:'educational_model_indicator';observedSkinLandmark:false;construction:string;limitations:string[]}}[];
  relation: SourceRef[];
  checks: { side: boolean; pose: boolean; frame: boolean; topology: boolean; surface: boolean; anatomicalRelation: boolean };
  failures: string[];
  rights: {localObservation:'supported'|'held';publicRedistribution:'held'|'supported';sourceIds:string[]};
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
/** Compact mask revision on an immutable carrier; density is a visual value only. */
export interface TerritoryMask extends Omit<Territory,'triangleMask'> {
  schemaVersion:1; scope:'real_input'|'technical_fixture';
  carrierId:string; carrierRevision:string; datasetRevision:string; frameId:string; unit:'m'; poseId:string;
  triangleIds:number[]; vertexWeights:[number,number][];
  basisKind:'surface_learning_connection'|'cutaneous'|'sinew_projection'|'professor_interpretation';
  author:'ai'|'human'; precision:'educational_approximation_not_skin'; canonicalBoundaryClaim:false;
  rights:{localObservation:'supported'|'held';publicRedistribution:'held'|'supported';sourceIds:string[]};
  boundaryInputSha256:string; faceSetSha256:string; contentSha256:string;
}
export interface SinewPath { id: string; revision: string; sources: SourceRef[]; branches: SourcedText[]; muscles: { sourceKey: string; part: string | null; evidence: SourcedText }[] }
export interface LearningAssociation { id: string; revision: string; from: string; to: string | null; kind: 'spatial_context' | 'lecture_association'; explanation: SourcedText | null; unresolvedOriginal: string | null }
export type LearningSelection = { kind: 'anatomy'; sourceKey: string } | { kind: 'acupoint'; code: string; side: Side } | { kind: 'territory'; id: string };
/** Metadata policy only. Runtime callers must also verify geometry bytes with projectLearnerInstances. */
export function productInstances(carrier: Carrier, instances: PointInstance[]) {
  return instances.filter(i => localLearnerEligible(carrier, i));
}
