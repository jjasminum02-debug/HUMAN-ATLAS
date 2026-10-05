export type MotionFrameMember = { sourceKey: string; role: string };
export type MotionFrameKind = 'bone' | 'muscle' | 'nerve' | 'accessory' | null | undefined;

/**
 * Keep authored focus keys, but never crop out bones that actually move with the
 * selected source action. Exact verified origin/insertion bones are included as
 * static scene context; this does not infer sides or create anatomy.
 */
export function motionFrameSourceKeys(
  members: readonly MotionFrameMember[],
  declaredFrameKeys: readonly string[] | undefined,
  subjectSourceKey: string,
  kindForSourceKey: (sourceKey: string) => MotionFrameKind,
  attachmentBoneKeys: readonly string[] = [],
): string[] {
  const memberKeys = new Set(members.map(member => member.sourceKey));
  const declared = (declaredFrameKeys ?? []).filter(key => memberKeys.has(key));
  const base = declared.length ? declared : members.map(member => member.sourceKey);
  const movingBones = members.filter(member =>
    (member.role === 'moving_structure' || member.role === 'co_moving_context')
      && kindForSourceKey(member.sourceKey) === 'bone')
    .map(member => member.sourceKey);
  const exactAttachments = attachmentBoneKeys.filter(key => kindForSourceKey(key) === 'bone');
  const subject = memberKeys.has(subjectSourceKey) ? [subjectSourceKey] : [];
  return [...new Set([...base, ...subject, ...movingBones, ...exactAttachments])];
}
