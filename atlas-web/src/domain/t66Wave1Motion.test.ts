import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import path from "node:path";
import { AnimationMixer } from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { assessMotionCapability } from "./motionLearning.ts";
import { projectT66Wave1MotionOptions, type T66Wave1Registration } from "./t66Wave1Motion.ts";

const root = path.resolve(process.cwd(), "..");
const readJson = async <T>(relativePath: string): Promise<T> => JSON.parse(await readFile(path.join(root, relativePath), "utf8")) as T;
const sha256 = (bytes: Uint8Array) => createHash("sha256").update(bytes).digest("hex");
const asArrayBuffer = (bytes: Buffer) => bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer;

test("T66 wave-1 normalized selectors project through the shared source-motion contract", async () => {
  const registration = await readJson<T66Wave1Registration>("atlas-data/motion/t66-wave1-registration.json");
  const sourceValidation = await readJson<{ result: string; runId: string; candidates: Array<{ rows: Array<{ sourceKey: string; candidateGeometrySha256: string }> }> }>(
    "work/evidence/T66/parallel-completion-2026-10-03/integration-wave1/candidate-source-validation.json");
  assert.equal(registration.schemaVersion, "t66-wave1-source-motion-registration-v2");
  assert.equal(registration.authority.sourceOnly, true);
  assert.equal(registration.authority.publicRedistribution, "held");
  assert.equal(registration.authority.humanReview, "not_performed");
  assert.equal(registration.authority.canonicalTargetMembershipApproved, false);
  assert.equal(sourceValidation.result, "passed");

  const packageById = new Map(registration.packages.map((row) => [row.id, row]));
  const selectorIds = registration.selectors.map((row) => row.actionId);
  assert.equal(new Set(selectorIds).size, selectorIds.length, "selector action IDs must be unique");
  assert.ok(registration.selectors.length > 0);
  assert.ok(registration.packages.length > 0);

  const selectorsBySource = new Map<string, typeof registration.selectors>();
  for (const selector of registration.selectors) {
    assert.ok(packageById.has(selector.packageId), `package missing for ${selector.actionId}`);
    const group = selectorsBySource.get(selector.sourceSubjectKey) ?? [];
    group.push(selector);
    selectorsBySource.set(selector.sourceSubjectKey, group);
    const pkg = packageById.get(selector.packageId)!;
    const member = pkg.sourceBindingTemplate.members.find((row) => row.sourceKey === selector.sourceSubjectKey);
    assert.ok(member, `exact source member missing for ${selector.actionId}`);
    if (selector.subjectKind === "muscle") {
      assert.ok(member.role === "deforming_muscle_surface" || member.role === "deforming_passive_surface");
      assert.equal(member.side, selector.side, "muscle selector must use exact source side");
      if (selector.actionId.startsWith("T66-W1-ACTION-")) {
        assert.doesNotMatch(selector.label, /움직임|MCP|PIP|DIP|CMC/,
          "hand action labels must resolve joint and action into learner Korean");
      }
    } else {
      assert.ok(member.role === "moving_structure" || member.role === "fixed_structure");
      assert.ok(member.side === selector.side || (selector.side === "midline" && member.side === null),
        "bone selector must preserve explicit laterality or explicit unsided midline identity");
      assert.equal(pkg.staticBinding.side, selector.side);
    }
  }

  for (const [sourceKey, expectedSelectors] of selectorsBySource) {
    const side = expectedSelectors[0]?.side ?? null;
    const options = projectT66Wave1MotionOptions(registration, sourceKey, side);
    for (const expected of expectedSelectors.filter((row) => row.side === side || row.side === "midline")) {
      const matches = options.filter((option) => option.id === expected.learnerActionKey);
      assert.equal(matches.length, 1, `exact option not projected once: ${expected.actionId}`);
      assert.ok(matches[0].candidate, `contract rejected accepted selector ${expected.actionId}`);
      assert.deepEqual(matches[0].candidate.asset.sourceBinding?.subjectSourceKey, sourceKey);
      assert.equal(matches[0].candidate.asset.staticBinding.side, expected.side);
      assert.equal(assessMotionCapability(matches[0].candidate.definition.actionId
        ? registrationToAction(expected, packageById.get(expected.packageId)!) : undefined,
        matches[0].candidate.definition, matches[0].candidate.asset).hasTechnicallyCompatibleClip, true);
    }
    const lateral = expectedSelectors.find((row) => row.side === "left" || row.side === "right");
    if (lateral) {
      const opposite = lateral.side === "left" ? "right" : "left";
      assert.equal(projectT66Wave1MotionOptions(registration, sourceKey, opposite).some((row) => row.id === lateral.learnerActionKey), false,
        `wrong-side selector leaked: ${lateral.actionId}`);
    }
  }
});

function registrationToAction(selector: T66Wave1Registration["selectors"][number], pkg: T66Wave1Registration["packages"][number]) {
  return {
    subjectKind: selector.subjectKind, id: selector.actionId, subjectIds: [], sourceSubjectKeys: [selector.sourceSubjectKey],
    learnerActionKey: selector.learnerActionKey, sideApplicability: selector.side, jointBindingState: "source_family_bound" as const,
    sourceFamilyId: pkg.familyId, jointBindingNote: null, targetJointIds: [], actionLabel: selector.label,
    explanation: selector.explanation, postureConditions: [], stabilizationConditions: [], stabilizationNote: null,
    contextRoles: [], sourceRefs: [],
  };
}

test("T66 wave-1 sampled GLBs replay exact muscle morph and midline bone motion, then return to rest", async () => {
  const registration = await readJson<T66Wave1Registration>("atlas-data/motion/t66-wave1-registration.json");
  const packageById = new Map(registration.packages.map((row) => [row.id, row]));
  const muscleSelector = registration.selectors.find((row) => row.subjectKind === "muscle");
  const midlineBoneSelector = registration.selectors.find((row) => row.subjectKind === "bone" && row.side === "midline"
    && packageById.get(row.packageId)?.sourceBindingTemplate.members.some((member) => member.sourceKey === row.sourceSubjectKey && member.side === null));
  assert.ok(muscleSelector);
  assert.ok(midlineBoneSelector, "the actual C spine package must expose an unsided midline bone selector");

  for (const selector of [muscleSelector, midlineBoneSelector]) {
    const template = packageById.get(selector.packageId)!;
    const filePath = path.join(root, template.uri);
    const bytes = await readFile(filePath);
    assert.equal(sha256(bytes), template.sha256, `integrated GLB hash mismatch: ${selector.actionId}`);
    const gltf = await new GLTFLoader().parseAsync(asArrayBuffer(bytes), "");
    const member = template.sourceBindingTemplate.members.find((row) => row.sourceKey === selector.sourceSubjectKey)!;
    const subject = gltf.scene.getObjectByName(member.nodeId);
    assert.ok(subject, `exact selected GLB node missing: ${member.nodeId}`);
    const clip = gltf.animations.find((row) => row.name === template.clip.id);
    assert.ok(clip, `exact clip missing: ${template.clip.id}`);
    const initialMatrix = subject!.matrix.clone();
    const initialInfluences = (subject as any).morphTargetInfluences?.slice?.() as number[] | undefined;
    const mixer = new AnimationMixer(gltf.scene);
    const action = mixer.clipAction(clip!);
    action.play();
    mixer.update(clip!.duration * 0.5);
    gltf.scene.updateMatrixWorld(true);
    if (selector.subjectKind === "muscle") {
      const current = (subject as any).morphTargetInfluences as number[] | undefined;
      assert.ok(current?.length, "muscle candidate must have real morph targets");
      assert.ok(current!.some((value, index) => Math.abs(value - (initialInfluences?.[index] ?? 0)) > 1e-6),
        "mid-pose must alter the selected muscle surface");
    } else {
      assert.ok(subject!.matrix.elements.some((value, index) => Math.abs(value - initialMatrix.elements[index]) > 1e-6),
        "mid-pose must move the selected midline bone structure");
    }
    mixer.setTime(0);
    gltf.scene.updateMatrixWorld(true);
    const rest = subject!.matrix.clone();
    for (let i = 0; i < 16; i++) assert.ok(Math.abs(rest.elements[i] - initialMatrix.elements[i]) < 1e-5,
      "rest pose must restore original transform");
    action.stop();
  }
});
