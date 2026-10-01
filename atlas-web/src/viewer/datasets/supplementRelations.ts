import { createHash } from 'node:crypto';
import type { SourceSupplement } from './sourceSupplement.ts';

export interface SupplementTargetRoute {
    key: string;
    regionId: string;
}

export interface ValidatedSupplementRelation {
    targetId: string;
    sourceKey: string;
    sourceElementFileId: string;
    regionId: string;
    side: string | null;
    sourceFmaId: string;
    targetFmaId: string;
    relationKind: 'source_declared_group_member' | 'exact_target_with_explicit_side_child';
    scope: 'bounded_source_group_member' | 'source_named_target_member';
    targetRouteKey: string;
    proof: string;
    sourceSha256: string;
    evaluatedGeometrySha256: string;
}

export interface SupplementRelationInputs {
    targets: any[];
    sourceElements: any[];
    evidenceHashes: Record<string, string>;
}

function normalizeAnatomicalTerm(value: unknown): string {
    return String(value ?? '').toLocaleLowerCase('en-US').trim()
        .replace(/^musculus\s+/, '')
        .replace(/\s+muscle$/, '')
        .replace(/[^a-z0-9]+/g, '');
}

function sidePrefix(value: unknown): 'left' | 'right' | null {
    const match = String(value ?? '').trim().match(/^(left|right)\b/i);
    return match ? match[1].toLowerCase() as 'left' | 'right' : null;
}

function targetRouteKey(targetId: string, regionId: string, sourceKey: string): string {
    const bytes = createHash('sha256').update(`T100-target-member-route-v1\0${targetId}\0${regionId}\0${sourceKey}`).digest('hex');
    return `TR-${bytes.slice(0, 24)}`;
}

/** Validate exact source-to-target associations without creating HA canonical IDs.
 * Raw TA2 IDs remain in this internal evidence ledger only; learner runtime gets
 * opaque per-source target path keys instead.
 */
export function resolveSupplementTargetRelations(
    supplement: SourceSupplement,
    inputs: SupplementRelationInputs,
): ValidatedSupplementRelation[] {
    const targets = new Map(inputs.targets.map(target => [target.id, target]));
    const sourceElements = new Map(inputs.sourceElements.map(source => [source.id, source]));
    const output: ValidatedSupplementRelation[] = [];
    const seenRoutes = new Set<string>();

    for (const object of supplement.objects) {
        const association = object.targetAssociation as any;
        const target = targets.get(association.targetId);
        const fj = object.sourceIdentity.sourceElementFileId;
        const source = sourceElements.get(fj);
        if (!target || !source || !Array.isArray(target.regionIds) || !Array.isArray(object.regionIds)
            || !object.regionIds.length || object.regionIds.some(region => !target.regionIds.includes(region)))
            throw Error(`supplement target/region relation is not in the frozen target scope: ${object.sourceKey}`);
        if (association.canonicalHaBindingCreated !== false || object.rights.sourceOnly !== true
            || object.rights.humanReview !== 'not_performed' || object.rights.publicRedistribution !== 'held')
            throw Error(`supplement relation cannot promote canonical, review, or rights state: ${object.sourceKey}`);
        const candidates = new Map((source.conceptCandidates ?? []).map((row: any) => [row.id, row.name]));
        const sourceFmaName = String(candidates.get(object.sourceIdentity.sourceFmaId) ?? '');
        if (!sourceFmaName || association.sourceMemberFma !== object.sourceIdentity.sourceFmaId)
            throw Error(`exact source FMA member is not supported by the frozen source catalog: ${object.sourceKey}`);

        let relationKind: ValidatedSupplementRelation['relationKind'];
        let scope: ValidatedSupplementRelation['scope'];
        let targetFmaId: string;
        let proof: string;
        if (association.relationKind === 'source_declared_group_member') {
            const groupId = association.targetFmaGroup;
            const group = supplement.sourceGroupMembership?.[groupId];
            const expectedGroupMembers = [...(association.sourceGroupMemberSet ?? [])].sort();
            const actualGroupMembers = [...(group?.memberElementFileIds ?? [])].sort();
            if (target.semanticKind !== 'bone_group' || object.kind !== 'skeletal_surface' || !group
                || group.targetId !== target.id || expectedGroupMembers.length === 0
                || expectedGroupMembers.join('\n') !== actualGroupMembers.join('\n')
                || !actualGroupMembers.includes(fj) || group.extentStatus !== 'source-declared-three-member-set; not global anatomy completeness'
                || normalizeAnatomicalTerm(association.targetEnglish) !== normalizeAnatomicalTerm(target.term?.english)
                || normalizeAnatomicalTerm(association.targetLatin) !== normalizeAnatomicalTerm(target.term?.latin))
                throw Error(`source-declared group membership does not match the exact frozen group record: ${object.sourceKey}`);
            relationKind = 'source_declared_group_member';
            scope = 'bounded_source_group_member';
            targetFmaId = groupId;
            proof = 'Exact BodyParts3D FMA PART-OF group member and frozen TA2 group wording; member route only, no group extent completion.';
        } else if (association.relationKind === 'exact_target_with_explicit_side_child') {
            targetFmaId = String(association.targetFma ?? '');
            const sourceTargetName = String(candidates.get(targetFmaId) ?? '');
            const englishMatches = normalizeAnatomicalTerm(association.targetEnglish) === normalizeAnatomicalTerm(target.term?.english)
                && normalizeAnatomicalTerm(sourceTargetName) === normalizeAnatomicalTerm(target.term?.english);
            const latinMatches = normalizeAnatomicalTerm(association.targetLatin) === normalizeAnatomicalTerm(target.term?.latin)
                && normalizeAnatomicalTerm(sourceTargetName) === normalizeAnatomicalTerm(target.term?.latin);
            const declaredSide = source.runtime?.side ?? null;
            const memberNameSide = sidePrefix(sourceFmaName);
            const objectNameSide = sidePrefix(object.sourceName);
            if (!['named_muscle', 'muscle_part'].includes(target.semanticKind) || object.kind !== 'muscle_surface_or_part'
                || !sourceTargetName || !englishMatches && !latinMatches
                || (object.side !== 'left' && object.side !== 'right') || declaredSide !== object.side
                || memberNameSide !== object.side || objectNameSide !== object.side
                || source.runtime?.sourceSha256 !== object.sourceIdentity.sourceSha256)
                throw Error(`exact target/explicit child/side relation failed independent checks: ${object.sourceKey}`);
            relationKind = 'exact_target_with_explicit_side_child';
            scope = 'source_named_target_member';
            proof = 'Normalized exact target term to FMA parent plus exact source FMA child, source name, and frozen source-side agreement; not human review or full anatomical extent approval.';
        } else {
            throw Error(`unsupported supplement relation kind: ${object.sourceKey}`);
        }

        for (const regionId of object.regionIds) {
            const routeKey = targetRouteKey(target.id, regionId, object.sourceKey);
            if (seenRoutes.has(routeKey)) throw Error(`duplicate opaque target route: ${object.sourceKey}`);
            seenRoutes.add(routeKey);
            output.push({
                targetId: target.id, sourceKey: object.sourceKey, sourceElementFileId: fj, regionId,
                side: object.side, sourceFmaId: object.sourceIdentity.sourceFmaId, targetFmaId,
                relationKind, scope, targetRouteKey: routeKey, proof,
                sourceSha256: object.sourceIdentity.sourceSha256,
                evaluatedGeometrySha256: String(object.sourceIdentity.compiledMeshAccessorSha256),
            });
        }
    }
    if (output.length !== supplement.objects.reduce((n, object) => n + object.regionIds.length, 0))
        throw Error('each validated supplement object must have one route per explicit target-region membership');
    if (Object.values(inputs.evidenceHashes).some(value => !/^[a-f0-9]{64}$/.test(value)))
        throw Error('supplement relation evidence input hashes are invalid');
    return output;
}

export function targetRoutesBySource(relations: ValidatedSupplementRelation[]): Map<string, SupplementTargetRoute[]> {
    const output = new Map<string, SupplementTargetRoute[]>();
    for (const relation of relations) {
        const paths = output.get(relation.sourceKey) ?? [];
        paths.push({ key: relation.targetRouteKey, regionId: relation.regionId });
        output.set(relation.sourceKey, paths);
    }
    return output;
}
