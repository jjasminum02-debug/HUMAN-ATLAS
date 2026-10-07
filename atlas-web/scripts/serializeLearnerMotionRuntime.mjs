/** Lossless sharing of immutable family contracts; no IDs, sides or fields are removed. */
export function serializeLearnerMotionRuntime(projected) {
  // Long IDs, hashes and descriptions recur across exact selectors. Store only
  // repeated strings; unique values stay inline and identity is unchanged.
  const counts = new Map(), strings = [], stringIndex = new Map();
  function count(value) {
    if (typeof value === "string" && value.length >= 32) counts.set(value, (counts.get(value) ?? 0) + 1);
    else if (value && typeof value === "object") for (const child of Object.values(value)) count(child);
  }
  count(projected);
  const pools = new Map();
  const indices = new Map();
  const expressions = [];
  const sharedFields = new Set(['members', 'movingStructureIds', 'fixedStructureIds', 'rig', 'staticReference', 'staticBinding', 'poseControl', 'text', 'nodeBindings', 'instanceMatrix']);
  function expression(code) { const token = `__atlas_motion_ref_${expressions.length}__`; expressions.push(code); return token; }
  function intern(name, value) {
    if (!pools.has(name)) { pools.set(name, []); indices.set(name, new Map()); }
    const signature = JSON.stringify(value);
    const index = indices.get(name);
    if (!index.has(signature)) {
      // Reserve the slot before serializing dependent contracts.
      const slot = pools.get(name).length;
      index.set(signature, slot); pools.get(name).push(null);
      pools.get(name)[slot] = serialize(value);
    }
    return `${name}[${index.get(signature)}]`;
  }
  function serialize(value) {
    return JSON.stringify(value, (key, child) => {
      if (typeof child === 'string' && /^__atlas_motion_ref_\d+__$/.test(child)) throw new Error('Reserved generated motion reference in input');
      if (typeof child === "string" && (counts.get(child) ?? 0) > 1) {
        if (!stringIndex.has(child)) { stringIndex.set(child, strings.length); strings.push(child); }
        return expression(`motion_strings[${stringIndex.get(child)}]`);
      }
      if (!child || typeof child !== 'object') return child;
      if (key === 'definition' || key === 'asset' || key === 'sourceBinding') {
        const varying = key === 'definition' ? ['id', 'actionId', 'instanceId', 'side']
          : key === 'asset' ? ['id', 'motionDefinitionId', 'sourceBinding'] : ['subjectKind', 'subjectSourceKey'];
        const base = {}, overrides = {};
        for (const [field, item] of Object.entries(child)) (varying.includes(field) ? overrides : base)[field] = item;
        return expression(`({...${intern(`motion_${key}`, base)},...${serialize(overrides)}})`);
      }
      if (sharedFields.has(key)) return expression(intern(`motion_${key}`, child));
      // Each member is also shared between overlapping family member lists.
      if (/^\d+$/.test(key) && child.sourceKey && child.geometrySha256 && child.role) return expression(intern('motion_member', child));
      return child;
    }).replace(/"__atlas_motion_ref_(\d+)__"/g, (_, i) => expressions[Number(i)]);
  }
  const body = serialize(projected);
  // Emit actual dependencies first, including a pool reused by a later family.
  const declarations = [], emitted = new Set(), visiting = new Set();
  function emit(name) {
    if (emitted.has(name)) return;
    if (visiting.has(name)) throw new Error("Cyclic motion template dependency");
    visiting.add(name);
    const rows = pools.get(name);
    for (const [dependency] of pools) if (dependency !== name && rows.some(row => row.includes(`${dependency}[`))) emit(dependency);
    visiting.delete(name); emitted.add(name);
    declarations.push(`const ${name} = [${rows.join(',')}] as const;`);
  }
  for (const [name] of pools) emit(name);
  return `const motion_strings = ${JSON.stringify(strings)} as const;\n${declarations.join("\n")}\n\nconst learnerMotionRuntime = ${body} as const;\nexport default learnerMotionRuntime;\n`;
}
