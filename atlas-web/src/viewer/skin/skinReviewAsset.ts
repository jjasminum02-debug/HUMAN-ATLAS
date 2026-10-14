import type { SkinAsset } from './skinContract.ts';
/** DEV-only checkpoints and scoped F1 candidates. No entry approves a whole skin. */
export async function skinReviewAsset(datasetRevision:string):Promise<SkinAsset> {
  const requested=new URLSearchParams(window.location.search).get('skinCandidate');
  const revision=requested==='f1c7'||requested==='f1c4'||requested==='f1c5'||requested==='f1c1'||requested==='r56'||requested==='r58'?requested:'r41';
  const candidate=revision==='f1c7'?{
    url:(await import('../../../../atlas-data/anatomy/skin/at10-f1-correspondence-r2/skin-candidate-f1c7.glb?url')).default,
    sha256:'fd119f927a59e86e66f1fd145b4848e00aa0904a0969ac9d944aafb62fda0bcb',
    topologySha256:'128db0930d88aad4c9306fb7767f29e997b7efffe0a6dfb1b75f923aaf8741ec',mappingSha256:'ac96729ff2b28e0b4cda676c20a763c4bb766a3d747c39cdaaa4b46050586a27',
  }:revision==='f1c4'?{
    url:(await import('../../../../atlas-data/anatomy/skin/at10-f1-correspondence-r2/skin-candidate-f1c4.glb?url')).default,
    sha256:'9816be26c2dfeb6f97698cd09c3ccba5c9754926923d19ff9f1712e6efbc24cf',
    topologySha256:'9e22b09ef79a1dbef397f666061200106b39ce1f5b5f429333356d7fcb139f31',mappingSha256:'1d530bee531c3c41d513bf6dd0083e95a19fcb77a47556aefb1af668949c6a00',
  }:revision==='f1c5'?{
    url:(await import('../../../../atlas-data/anatomy/skin/at10-f1-correspondence-r2/skin-candidate-f1c5.glb?url')).default,
    sha256:'1e21069d9f8e6411f93278652ca9a595f683c164c18f272771057098078fb07c',
    topologySha256:'6d1cb8a4bd125d7d86bc3600e53f7aadd64773441a2939aff3cabd8b1fdc76a1',mappingSha256:'cd27fd3c59ccb2c3280502ef18737f98308be5786bbf002083cc27ffc25fb144',
  }:revision==='f1c1'?{
    url:(await import('../../../../atlas-data/anatomy/skin/at10-f1-correspondence-r2/skin-candidate-f1c1.glb?url')).default,
    sha256:'1c23865ff0955c33bf61a04172e5204b60c6353cbbb6aae9c350a38eb0922654',
    topologySha256:'1acdfb0bbe1255e08d2d7398859bb582c5d1ec2ca69f59a1a66688f5457b837a',mappingSha256:'f01abf47e1db8508074826beca7d3b5733b35eb29f49c91992945d800c0abd6b',
  }:revision==='r56'?{
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
  return {schemaVersion:1,id:`at10-skin-${revision}-review-only`,revision:revision.startsWith('f1')?revision:revision+'p1',datasetRevision,...candidate,
    bytes:626576,geometryBytes:625080,triangles:26756,
    frameId:'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR',unit:'m',poseId:'ZA-9f08a17ea0115fed-frame0-autoexec-off',
    geometryAccepted:false,learnerEligible:false,landmarkRevision:null,localObservation:'supported',publicRedistribution:'held',author:'ai',professorReview:'not_performed',staticPoseOnly:true};
}
