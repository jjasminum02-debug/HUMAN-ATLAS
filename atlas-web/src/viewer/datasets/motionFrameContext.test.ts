import { test } from 'node:test';
import assert from 'node:assert/strict';
import { motionFrameSourceKeys } from './motionFrameContext.ts';

test('motion frame keeps authored attachments and includes the complete moving arm through hand', () => {
  const members = [
    { sourceKey: 'c3', role: 'fixed_structure' },
    { sourceKey: 'scapula-left', role: 'moving_structure' },
    { sourceKey: 'humerus-left', role: 'moving_structure' },
    { sourceKey: 'radius-left', role: 'moving_structure' },
    { sourceKey: 'ulna-left', role: 'moving_structure' },
    { sourceKey: 'metacarpals-left', role: 'moving_structure' },
    { sourceKey: 'phalanges-left', role: 'moving_structure' },
    { sourceKey: 'levator-left', role: 'deforming_muscle_surface' },
    { sourceKey: 'rhomboid-left', role: 'deforming_passive_surface' },
    { sourceKey: 'right-radius', role: 'fixed_structure' },
  ];
  const kind = (key: string) => key.includes('radius') || key.includes('ulna') || key.includes('humerus')
    || key.includes('scapula') || key.includes('metacarpals') || key.includes('phalanges') || key === 'c3' || key === 'c1'
    ? 'bone' as const : 'muscle' as const;
  const keys = motionFrameSourceKeys(members, ['c3', 'scapula-left', 'levator-left'], 'levator-left', kind, ['c1', 'scapula-left']);
  assert.deepEqual(keys, ['c3', 'scapula-left', 'levator-left', 'humerus-left', 'radius-left', 'ulna-left', 'metacarpals-left', 'phalanges-left', 'c1']);
  assert.equal(keys.includes('right-radius'), false);
  assert.equal(keys.includes('rhomboid-left'), false);
});

test('assets without a focus list retain their whole package frame and exact attachment context', () => {
  const members = [
    { sourceKey: 'left-femur', role: 'moving_structure' },
    { sourceKey: 'left-patella', role: 'co_moving_context' },
    { sourceKey: 'rectus-left', role: 'deforming_muscle_surface' },
  ];
  const keys = motionFrameSourceKeys(members, undefined, 'rectus-left', key => key === 'rectus-left' ? 'muscle' : 'bone', ['left-hip-bone']);
  assert.deepEqual(keys, ['left-femur', 'left-patella', 'rectus-left', 'left-hip-bone']);
});
