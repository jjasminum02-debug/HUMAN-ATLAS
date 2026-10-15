import type { SkinAsset } from './skinContract.ts';
/** DEV-only checkpoints and scoped foot candidates. No entry approves a whole skin. */
export async function skinReviewAsset(datasetRevision:string,params:URLSearchParams):Promise<SkinAsset> {
  const requested=params.get('skinCandidate');
  const revision=requested==='f3c11'||requested==='f2c3'||requested==='f2c2'||requested==='f2c1'||requested==='f1c7'||requested==='f1c4'||requested==='f1c5'||requested==='f1c1'||requested==='r56'||requested==='r58'?requested:'r41';
  const candidate=revision==='f3c11'?{
    url:(await import('../../../../atlas-data/anatomy/skin/at10-f3-head-r1/skin-candidate-f3c11.glb?url')).default,
    sha256:'0999bebef773bd842f93429a8b183ea397dc8011bf47cec2c579aec6a73b30da',topologySha256:'5431c6545e12ed5a5abe47f836ce8536579fa5de67e7d3fd73ccc115a098a1b5',mappingSha256:'4129f5dfac7bb3eacedb2c21e4ff75d4c9990dd132c8651a1f6a936b0e8c3fc5',
    appearanceBinding:(await import('../../../../atlas-data/anatomy/skin/at10-f3-head-r1/material-f3c11.json')).default,
    components:{...(await import('../../../../atlas-data/anatomy/skin/at10-f3-head-r1/ocular-components-r1.json')).default,datasetRevision,url:(await import('../../../../atlas-data/anatomy/skin/at10-f3-head-r1/ocular-components-r1.glb?url')).default,unit:'m' as const},
  }:revision==='f2c3'?{
    url:(await import('../../../../atlas-data/anatomy/skin/at10-f2-left-foot-r1/skin-candidate-f2c3.glb?url')).default,
    sha256:'07ab569e3a3a3453ed825e9bc583869394e5e94babdee7edec6b6c437836586f',
    topologySha256:'34146f987e073e14863c91e0d8003356b1a42235e82f9684611965a140a6d4b2',mappingSha256:'61f329005c20aa523877b0817b1121be39abf0fa7071a6f4e77d3498d6ed3c70',
  }:revision==='f2c2'?{
    url:(await import('../../../../atlas-data/anatomy/skin/at10-f2-left-foot-r1/skin-candidate-f2c2.glb?url')).default,
    sha256:'f6c50ab1cea1ffa9d7b5d4d3d280859936ee81f73a3a834ded1ac8e694bf2122',
    topologySha256:'a359f1d1381b0cddb29caabe36f62b3b69f1b864f5c2ef5851a4da320c50d2e5',mappingSha256:'b4dcb213338dcab8fd179ee21491813770681330b25bcb6759704c47f1a71894',
  }:revision==='f2c1'?{
    url:(await import('../../../../atlas-data/anatomy/skin/at10-f2-left-foot-r1/skin-candidate-f2c1.glb?url')).default,
    sha256:'541914c44f256b58f58833cd0a320ca377ae972a0c5b1a6f3b2ec6c8c6ebafec',
    topologySha256:'c1f9c5d1b1ba402e7bdf784451a943c2217340ada487a2ce5ca884605118d722',mappingSha256:'f406fa62755a7aff411632e30f9c9ed58711b5e10b68727cedad1e10bd77345a',
  }:revision==='f1c7'?{
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
  const appearance=params.get('skinAppearance')==='v1' && (revision==='f2c3'||'appearanceBinding' in candidate)
    ? (await import('./skinAppearanceReview.ts')).skinAppearanceReviewFor('appearanceBinding' in candidate?candidate.appearanceBinding:undefined) : undefined;
  return {appearance,schemaVersion:1,id:`at10-skin-${revision}-review-only`,revision:revision.startsWith('f')?revision:revision+'p1',datasetRevision,...candidate,
    bytes:626576,geometryBytes:625080,triangles:26756,
    frameId:'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR',unit:'m',poseId:'ZA-9f08a17ea0115fed-frame0-autoexec-off',
    geometryAccepted:false,learnerEligible:false,landmarkRevision:null,localObservation:'supported',publicRedistribution:'held',author:'ai',professorReview:'not_performed',staticPoseOnly:true};
}
