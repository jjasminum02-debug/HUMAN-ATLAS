import type { SkinAsset } from './skinContract.ts';
/** Imported only by a DEV URL. This is the preserved hand checkpoint, NOT a fitted whole skin. */
export async function skinReviewAsset(datasetRevision:string):Promise<SkinAsset> {
  const {default:url}=await import('../../../../atlas-data/anatomy/skin/at10-fit-r5/skin-candidate-r41.glb?url');
  return {schemaVersion:1,id:'at10-skin-r41-review-only',revision:'r41',datasetRevision,url,
    sha256:'52b23499e52d1b3b0d64448ebe5d1973508e24b419bf1c1e068ad10b00a54e4d',
    topologySha256:'6980bfdf6a90a1a1bcf23d7462b0c3645f2b5e7ad50a28a93ab555e9d6cc9d14',mappingSha256:'292d80fb1253e8cdcfcc9f3dc1ed57e6360318925de20cde6f374e773523249b',
    bytes:626572,geometryBytes:625080,triangles:26756,
    frameId:'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR',unit:'m',poseId:'za-c7010a9-9f08a17ea011-frame0-static',
    geometryAccepted:false,learnerEligible:false,landmarkRevision:null,localObservation:'supported',publicRedistribution:'held',author:'ai',professorReview:'not_performed',staticPoseOnly:true};
}
