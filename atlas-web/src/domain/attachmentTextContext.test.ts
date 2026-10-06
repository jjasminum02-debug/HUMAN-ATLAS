import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { namedAttachmentBones } from './attachmentTextContext.ts';
import type { RuntimeStructureRecord } from '../viewer/datasets/integration.ts';
const rows = JSON.parse(readFileSync(new URL('../../../atlas-data/overlays/za-local-integration.json', import.meta.url), 'utf8')).objects as RuntimeStructureRecord[];
test('verified wrist descriptions resolve exact same-side whole bones without inventing a footprint', () => {
  for (const side of ['left', 'right']) {
    const origin = namedAttachmentBones('위팔뼈 가쪽위관절융기능선 아래쪽 3분의 1에서 시작합니다.', side, rows);
    const insertion = namedAttachmentBones('둘째 손허리뼈 바닥 등쪽면에 이어집니다.', side, rows);
    assert.deepEqual(origin.keys, [rows.find(r => r.names.en === 'Humerus' && r.side === side)!.sourceKey]);
    assert.deepEqual(insertion.keys, [rows.find(r => r.names.en === 'Second metacarpal bone' && r.side === side)!.sourceKey]);
  }
});
test('ambiguous, hidden, held, wrong-side or embedded bone words cannot acquire a context link', () => {
  const humerus = rows.find(r => r.names.en === 'Humerus' && r.side === 'left')!;
  const duplicate = { ...humerus, sourceKey: 'other-existing-humerus' };
  assert.equal(namedAttachmentBones('위팔뼈', 'left', [...rows, duplicate]).keys.length, 0);
  for (const patch of [{localDisplayEligible:false}, {hardHoldReasons:['held']}, {side:'right'}]) {
    assert.equal(namedAttachmentBones('위팔뼈', 'left', [ {...humerus, ...patch} ]).keys.length, 0);
  }
  assert.equal(namedAttachmentBones('긴노뼈쪽손목폄근의 힘줄', 'left', rows).keys.length, 0);
});
