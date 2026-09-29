import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { validateDataset } from '../src/viewer/datasets/schema.ts';
import { validateManifest } from '../src/viewer/wholeBody/contract.ts';
const root = fileURLToPath(new URL('../../atlas-data/source-cache/datasets/', import.meta.url));
const sha = (v: Buffer) => createHash('sha256').update(v).digest('hex');
const index = JSON.parse(await readFile(root + 'index.json', 'utf8'));
let checked = 0;
for (const [namespace, relative] of Object.entries(index.datasets)) {
    const registry = JSON.parse(await readFile(root + relative, 'utf8'));
    for (const input of registry.dependencies)
        if (sha(await readFile(input.path)) !== input.sha256)
            throw Error(`changed source dependency ${input.path}`);
    if (namespace === 'bp3d-r4')
        validateManifest(registry.manifest);
    else
        validateDataset(registry.manifest);
    for (const file of registry.files) {
        const bytes = await readFile(file.path);
        if (bytes.length !== file.bytes || sha(bytes) !== file.sha256)
            throw Error(`changed compiled chunk ${file.path}`);
        checked++;
    }
}
console.log(`Current compiled dataset contracts/dependencies/content hashes verified: ${checked} chunks. Historical plan/document freezes are tested separately.`);
