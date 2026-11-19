// 4-2 step 9: names of the clinical tests that look at this structure, with one line each (no procedure, no animation).
import { useEffect, useState } from 'react';
import type { RuntimeStructureRecord } from '../viewer/datasets/integration';
import { testsFor, type ClinicalTestsFile } from '../data/clinicalTests';

let testFile: Promise<ClinicalTestsFile | null> | undefined;
const loadTests = () => testFile ??= fetch('/__atlas/v2/clinical-tests.json').then(r => r.ok ? r.json() : null).catch(() => { testFile = undefined; return null; });

export function ClinicalTests({ row }: { row: RuntimeStructureRecord }) {
  const [file, setFile] = useState<ClinicalTestsFile | null>(null);
  useEffect(() => { let live = true; void loadTests().then(f => { if (live) setFile(f); }); return () => { live = false; }; }, []);
  const tests = testsFor(file, row.names.en);
  if (!tests.length) return null;
  return <section className="attachment-section clinical-tests" aria-label="검사">
    <h3>{row.kind === 'muscle' ? '이 근육을 보는 검사' : row.kind === 'nerve' ? '이 신경을 보는 검사' : '이 구조를 보는 검사'}</h3>
    <ul>{tests.map(t => <li key={t.id}><strong>{t.name}</strong><span className="clinical-test-en">{t.en}</span><p>{t.what}</p></li>)}</ul>
  </section>;
}
