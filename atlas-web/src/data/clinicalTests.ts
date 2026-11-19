// 4-2 step 9: clinical test names per structure. Data: atlas-data/runtime/clinical-tests.json
// (built by atlas-data/pipeline/clinical_tests.py; sources in atlas-data/anatomy/clinical-test-checks.json).
export interface ClinicalTest { id: string; name: string; en: string; what: string; targets: string[] }
export interface ClinicalTestsFile { schemaVersion: 1; tests: ClinicalTest[] }

/** Tests whose targets name this structure (English name; both sides share it). */
export function testsFor(file: ClinicalTestsFile | null, englishName: string) {
  return file?.tests.filter(t => t.targets.includes(englishName)) ?? [];
}
