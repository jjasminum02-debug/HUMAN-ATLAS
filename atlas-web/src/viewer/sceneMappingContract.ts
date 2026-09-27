/** Check only the mappings referenced by one scene, leaving other regions free to grow. */
export function sceneMappingTargets(
  meshIds: readonly string[],
  assets: readonly { id: string }[],
  instances: readonly { id: string; conceptId: string; side: string }[],
  mappings: readonly { id: string; meshIds: string[]; instanceIds: string[]; partIds: string[]; evidenceIds: string[]; reviewState: string }[],
  side: string,
): Map<string, string> {
  const assetIds = new Set(assets.map((row) => row.id));
  const instanceById = new Map(instances.map((row) => [row.id, row]));
  const targets = new Map<string, string>();
  for (const meshId of meshIds) {
    if (!assetIds.has(meshId)) throw new Error(`scene mesh asset 참조가 없습니다: ${meshId}`);
    const matches = mappings.filter((mapping) => mapping.meshIds.includes(meshId));
    if (matches.length !== 1) throw new Error(`scene muscle mesh mapping이 없거나 중복되었습니다: ${meshId}`);
    const mapping = matches[0];
    if (mapping.instanceIds.length !== 1 || mapping.evidenceIds.length === 0 || mapping.partIds.length > 1) {
      throw new Error(`scene muscle mapping 참조가 불완전합니다: ${mapping.id}`);
    }
    const instance = instanceById.get(mapping.instanceIds[0]);
    if (!instance || instance.side !== side) throw new Error(`scene muscle instance 좌우/참조가 다릅니다: ${mapping.id}`);
    targets.set(meshId, mapping.partIds[0] ?? instance.conceptId);
  }
  return targets;
}
