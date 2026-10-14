import type { SkinAsset } from './skinContract.ts';
/** Imported only by a DEV URL. This is the preserved hand checkpoint, NOT a fitted whole skin. */
export async function skinReviewAsset(datasetRevision:string):Promise<SkinAsset> {
  const requested=new URLSearchParams(window.location.search).get('skinCandidate');
  const revision=requested==='r56'||requested==='r58'?requested:'r41';
  const candidate=revision==='r56'?{
    url:(await import('../../../../atlas-data/anatomy/skin/at10-completion-r1/skin-candidate-r56p1.glb?url')).default,
    sha256:'66be5e641fdf318ae9d47a1890556005da2aa0d90e418f32dcb9683fdc822665',
    topologySha256:'503a429c096697bf80b22bcac0e44b2696eff9aff1cbbbe7063fc5840104118d',mappingSha256:'3bf6b8334ff4f64536b1b29eea20bd46db51df3437eed1b3c99abc5ebfc96690',
  }:revision==='r58'?{
    url:(await import('../../../../atlas-data/anatomy/skin/at10-completion-r1/skin-candidate-r58p1.glb?url')).default,
    sha256:'06f6a9216165fc7f5e701a426acbe24778ee116d81c3afcf5804ae3b80695efe',
    topologySha256:'7ebe77d34cc001b04b661cf8d903f5f523c55d47df66e8c012f73c99711e4b83',mappingSha256:'3af1eed712f76a4119a4af5b1e9f08022e8d9a74e90a5db7c8ed850a4ec1e707',
  }:{
    url:(await import('../../../../atlas-data/anatomy/skin/at10-completion-r1/skin-candidate-r41p1.glb?url')).default,
    sha256:'4eb7dd0b75d510cb3f6f4f249de549bc3ec5c6f59feb6880c7261a86d967b529',
    topologySha256:'6980bfdf6a90a1a1bcf23d7462b0c3645f2b5e7ad50a28a93ab555e9d6cc9d14',mappingSha256:'271193d59f2e80f1cff32a476d9b214f2d6088cd10ec7af2d16f0d7b5d4c85ff',
  };
  return {schemaVersion:1,id:`at10-skin-${revision}-review-only`,revision:revision+'p1',datasetRevision,...candidate,
    bytes:626576,geometryBytes:625080,triangles:26756,
    frameId:'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR',unit:'m',poseId:'ZA-9f08a17ea0115fed-frame0-autoexec-off',
    geometryAccepted:false,learnerEligible:false,landmarkRevision:null,localObservation:'supported',publicRedistribution:'held',author:'ai',professorReview:'not_performed',staticPoseOnly:true};
}
