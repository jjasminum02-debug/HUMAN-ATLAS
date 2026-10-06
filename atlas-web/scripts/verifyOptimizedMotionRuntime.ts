import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import runtime from '../src/data/learnerMotionRuntime.generated.ts';
import { projectT66Wave1MotionOptions, type T66Wave1Registration } from '../src/domain/t66Wave1Motion.ts';
const registration = JSON.parse(readFileSync(new URL('../../atlas-data/motion/t66-wave1-registration.json', import.meta.url), 'utf8')) as T66Wave1Registration;
const intents = JSON.parse(readFileSync(new URL('../../atlas-data/motion/t66-motion-learning-intents.json', import.meta.url), 'utf8'));
const rows = runtime.wave1Actions as unknown as Record<string, ReturnType<typeof projectT66Wave1MotionOptions>>;
let cases = 0;
for (const key of new Set([...registration.selectors.map(row => row.sourceSubjectKey), 'missing-source'])) {
  for (const side of [null, 'left', 'right', 'bilateral', 'midline']) {
    const expected = projectT66Wave1MotionOptions(registration, key, side, intents.byActionId).map(option => {
      if (!option.candidate) return option;
      const { poseSourceRefs: _privateRefs, ...definition } = option.candidate.definition;
      return { ...option, candidate: { ...option.candidate, definition } };
    });
    const actual = (rows[key] ?? []).filter(row => !side || row.sideApplicability === 'bilateral' || row.sideApplicability === 'midline' || row.sideApplicability === side);
    assert.deepEqual(JSON.parse(JSON.stringify(actual)), JSON.parse(JSON.stringify(expected)));
    cases++;
  }
}
console.log(JSON.stringify({ status: 'passed', exactSourceSideCases: cases }));
