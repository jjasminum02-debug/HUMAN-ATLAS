import type { BufferAttribute, BufferGeometry, InterleavedBufferAttribute } from "three";

function rawAttribute(attribute: BufferAttribute | InterleavedBufferAttribute): { type: string; bytes: Uint8Array } {
  if ((attribute as InterleavedBufferAttribute).isInterleavedBufferAttribute) {
    const interleaved = attribute as InterleavedBufferAttribute;
    const source = interleaved.data.array as unknown as ArrayLike<number> & { constructor: { new(length: number): ArrayBufferView } };
    const Type = source.constructor;
    const packed = new Type(attribute.count * attribute.itemSize) as unknown as { set(values: ArrayLike<number>, offset?: number): void; buffer: ArrayBufferLike; byteOffset: number; byteLength: number; [index: number]: number };
    let cursor = 0;
    for (let vertex = 0; vertex < attribute.count; vertex++) {
      const start = interleaved.offset + vertex * interleaved.data.stride;
      for (let component = 0; component < attribute.itemSize; component++) packed[cursor++] = Number(source[start + component]);
    }
    return { type: Type.name, bytes: new Uint8Array(packed.buffer, packed.byteOffset, packed.byteLength) };
  }
  const array = attribute.array as unknown as { constructor: { name: string }; buffer: ArrayBufferLike; byteOffset: number; byteLength: number };
  return { type: array.constructor.name, bytes: new Uint8Array(array.buffer, array.byteOffset, array.byteLength) };
}

/**
 * Stable hash for the base attributes of a decoded glTF primitive. Morph target attributes are
 * intentionally excluded so the derived target can be compared with its immutable source mesh.
 */
export async function sourceGeometrySha256(geometry: BufferGeometry): Promise<string> {
  const parts: Uint8Array[] = [new TextEncoder().encode("HUMAN_ATLAS_GEOMETRY_CONTENT_V1\n")];
  for (const name of Object.keys(geometry.attributes).sort()) {
    const attribute = geometry.getAttribute(name) as BufferAttribute | InterleavedBufferAttribute;
    const raw = rawAttribute(attribute);
    parts.push(new TextEncoder().encode(`attribute:${name}|${raw.type}|${attribute.itemSize}|${attribute.normalized ? 1 : 0}|${attribute.count}\n`));
    parts.push(raw.bytes);
  }
  const index = geometry.index;
  if (index) {
    const raw = rawAttribute(index);
    parts.push(new TextEncoder().encode(`index:${raw.type}|${index.itemSize}|${index.normalized ? 1 : 0}|${index.count}\n`));
    parts.push(raw.bytes);
  } else {
    parts.push(new TextEncoder().encode("index:none\n"));
  }
  for (const group of geometry.groups) parts.push(new TextEncoder().encode(`group:${group.start}|${group.count}|${group.materialIndex}\n`));
  const total = parts.reduce((sum, part) => sum + part.byteLength, 0);
  if (total > 64 * 1024 * 1024) throw new Error("source motion base geometry exceeds the 64 MiB verification budget.");
  const input = new Uint8Array(total);
  let offset = 0;
  for (const part of parts) { input.set(part, offset); offset += part.byteLength; }
  if (!globalThis.crypto?.subtle) throw new Error("Web Crypto API가 없어 source motion geometry hash를 확인할 수 없습니다.");
  const digest = await globalThis.crypto.subtle.digest("SHA-256", input);
  return [...new Uint8Array(digest)].map((value) => value.toString(16).padStart(2, "0")).join("");
}
