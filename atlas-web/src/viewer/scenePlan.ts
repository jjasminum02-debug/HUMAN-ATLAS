import type { SceneManifest } from "../domain/navigation.ts";

export function sceneRevision(scenes: readonly SceneManifest[]): string {
  return scenes.map((scene) => `${scene.id}@${scene.revision}:${scene.assetRefs.map((asset) => asset.sha256).join(",")}`).join("|");
}

export function assertCompatibleSceneGroup(scenes: readonly SceneManifest[]): void {
  if (scenes.length === 0) throw new Error("scene이 없습니다.");
  const reference = scenes[0];
  const models = new Set<string>();
  const meshIds = new Set<string>();
  for (const scene of scenes) {
    if (scene.availability === "unavailable" || scene.categoryId !== reference.categoryId ||
      scene.frameId !== reference.frameId || scene.units !== reference.units || scene.poseId !== reference.poseId ||
      scene.defaultView.side !== reference.defaultView.side) {
      throw new Error("서로 다른 부위·좌표계·자세·좌우의 scene을 함께 표시할 수 없습니다.");
    }
    if (scene.assetRefs.length === 0) throw new Error(`scene 자산이 없습니다: ${scene.id}`);
    for (const asset of scene.assetRefs) {
      if (asset.modelId !== scene.modelId || !asset.uri || !/^[a-f0-9]{64}$/.test(asset.sha256) || asset.meshAssetIds.length === 0 || models.has(asset.modelId)) {
        throw new Error(`scene 자산 참조가 불완전하거나 중복되었습니다: ${scene.id}`);
      }
      models.add(asset.modelId);
      for (const id of asset.meshAssetIds) {
        if (meshIds.has(id)) throw new Error(`scene 간 mesh ID가 중복되었습니다: ${id}`);
        meshIds.add(id);
      }
    }
  }
}
