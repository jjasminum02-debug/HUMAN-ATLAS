import type { Side } from './schema.ts';
import type { LearningCatalog } from './learningCatalog.ts';
export type LearningSide=Side|'both';
export interface PackageRegistration {id:string;channel:string;codes:string[];learnerFile:string;observationFile:string;observationEncoding?:'gzip'|'json';sections:{name:string;codes:string[]}[];learnerSha256?:string;observationSha256?:string}
export interface LearningRegistry {schemaVersion:1;catalogRevision:string;packages:PackageRegistration[]}
export const pointKey=(code:string,side:Side)=>`${code}:${side}`;
export function plannedSides(catalog:LearningCatalog,code:string):Side[] {
 const concept=catalog.concepts.find(c=>c.code===code);if(!concept)throw Error('Unknown catalog point');
 return catalog.channels.find(c=>c.code===concept.channel)!.midline?['midline']:['right','left'];
}
export function selectedSide(side:LearningSide,actual:Side){return side==='both'||actual==='midline'||side===actual;}
/** Catalog identity, package coverage and side are independent of placement approval. */
export function validateLearningRegistry(registry:LearningRegistry,catalog:LearningCatalog){
 if(registry.schemaVersion!==1||registry.catalogRevision!=='who-361-catalog-r1'||!Array.isArray(registry.packages))throw Error('Invalid package registry');
 const ids=new Set<string>(),codes=new Set<string>();
 for(const p of registry.packages){
  const channel=catalog.channels.find(c=>c.code===p.channel);
  if(!channel||!p.id||ids.has(p.id)||!p.codes.length||new Set(p.codes).size!==p.codes.length
    ||!/^[a-z0-9-]+\.json$/.test(p.learnerFile)||!(/^[a-z0-9-]+\.bin$/.test(p.observationFile)?p.observationEncoding==='gzip':/^[a-z0-9-]+\.json$/.test(p.observationFile)&&(!p.observationEncoding||p.observationEncoding==='json'))
    ||p.codes.some(code=>catalog.concepts.find(c=>c.code===code)?.channel!==p.channel||codes.has(code)))throw Error('Unknown/duplicate/conflicting package coverage');
  ids.add(p.id);p.codes.forEach(c=>codes.add(c));const sectionCodes=p.sections.flatMap(s=>s.codes);
  if(p.sections.some(s=>!s.name.trim())||new Set(sectionCodes).size!==sectionCodes.length||sectionCodes.some(c=>!p.codes.includes(c))||sectionCodes.length!==p.codes.length)throw Error('Invalid package sections');
 }
}
export function plannedInstanceCount(catalog:LearningCatalog,codes:string[],side:LearningSide){return codes.reduce((n,code)=>n+plannedSides(catalog,code).filter(s=>selectedSide(side,s)).length,0);}
export function assertUniqueInstances(instances:{code:string;side:Side}[]){const seen=new Set<string>();for(const i of instances){const key=pointKey(i.code,i.side);if(seen.has(key))throw Error('Duplicate/conflicting code+side');seen.add(key);}}
