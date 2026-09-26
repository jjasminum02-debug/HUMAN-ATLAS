import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { mergeLearningConcepts, searchEntries } from './search.ts';
const names = JSON.parse(readFileSync(new URL('../../../atlas-data/terminology/learning-names.json', import.meta.url),'utf8')).entries;
const entries = names.map((n: { id:string; label:string; korean:string;english:string;hanja:string;aliases:string[] }) => ({id:n.id,label:n.label,aliases:[n.korean,n.english,n.hanja,...n.aliases].filter(Boolean)}));
const catalog = JSON.parse(readFileSync(new URL('../../../atlas-data/catalog/canonical-catalog.json', import.meta.url),'utf8')).entities;
const b02Ids = Array.from({length:10},(_,i)=>`HA-G-${String(i+1).padStart(6,'0')}`);
const b02Names = names.filter((name:{id:string})=>b02Ids.includes(name.id));
const b02Concepts = mergeLearningConcepts(catalog.muscleConcepts.filter((concept:{id:string})=>b02Ids.includes(concept.id)),b02Names);
const b02SearchEntries = b02Concepts.map((concept:{id:string;label?:string}) => {
 const id=concept.id;
 const overlay = names.find((n:{id:string})=>n.id===id) as {label:string;korean:string;english:string;hanja:string;aliases:string[]}|undefined;
 const terms = catalog.terms.filter((term:{conceptId:string})=>term.conceptId===id);
 const korean = terms.find((term:{language:string;text:string|null})=>term.language==='ko'&&term.text)?.text;
 const english = terms.find((term:{language:string;text:string|null})=>term.language==='en'&&term.text)?.text;
 const latin = terms.find((term:{language:string;text:string|null})=>term.language==='la'&&term.text)?.text;
 return {id,label:overlay?.label ?? korean ?? english ?? latin ?? concept.label ?? id,aliases:[overlay?.korean,overlay?.english,overlay?.hanja,...overlay?.aliases ?? [],...terms.map((term:{text:string|null})=>term.text)].filter(Boolean)};
});
const b03Ids = [...Array.from({length:6},(_,i)=>`HA-G-${String(i+11).padStart(6,'0')}`),...Array.from({length:4},(_,i)=>`HA-M-${String(i+7).padStart(6,'0')}`)];
const b03Names = names.filter((name:{id:string})=>b03Ids.includes(name.id));
const b03Concepts = mergeLearningConcepts(catalog.muscleConcepts.filter((concept:{id:string})=>b03Ids.includes(concept.id)),b03Names);
const b03SearchEntries = b03Concepts.map((concept:{id:string;label?:string}) => {
 const id=concept.id;
 const overlay = names.find((n:{id:string})=>n.id===id) as {label:string;korean:string;english:string;hanja:string;aliases:string[]}|undefined;
 const terms = catalog.terms.filter((term:{conceptId:string})=>term.conceptId===id);
 const korean = terms.find((term:{language:string;text:string|null})=>term.language==='ko'&&term.text)?.text;
 const english = terms.find((term:{language:string;text:string|null})=>term.language==='en'&&term.text)?.text;
 const latin = terms.find((term:{language:string;text:string|null})=>term.language==='la'&&term.text)?.text;
 return {id,label:overlay?.label ?? korean ?? english ?? latin ?? concept.label ?? id,aliases:[overlay?.korean,overlay?.english,overlay?.hanja,...overlay?.aliases ?? [],...terms.map((term:{text:string|null})=>term.text)].filter(Boolean)};
});
for (const query of ['승모근','등세모근','僧帽筋','TRAPEZIUS','  등 세모근  ']) test(`same muscle: ${query}`,()=>assert.equal(searchEntries(entries,query)[0]?.entry.id,'HA-M-000019'));
for (const query of ['전경골근','앞정강근','前脛骨筋','tibialis anterior']) test(`tibialis: ${query}`,()=>assert.equal(searchEntries(entries,query)[0]?.entry.id,'HA-M-000003'));
test('transposed typo returns both splenius muscles, never a false single identity',()=>assert.deepEqual(new Set(searchEntries(entries,'spleinus').map(r=>r.entry.id)),new Set(['LOOKUP-SPLENIUS-CAPITIS','LOOKUP-SPLENIUS-CERVICIS'])));
test('deltoid portion stays separate',()=>assert.equal(searchEntries(entries,'측면삼각극')[0]?.entry.id,'HA-P-000015'));
test('user Korean name lateral deltoid maps to the acromial part',()=>assert.equal(searchEntries(entries,'측면삼각근')[0]?.entry.id,'HA-P-000015'));
test('named acromial part is included in the learner search projection',()=>{
 const canonical=[{id:'HA-M-000030',entityType:'individual_muscle',label:'삼각근'}];
 const projected=mergeLearningConcepts(canonical,names);
 assert.ok(projected.some(row=>row.id==='HA-P-000015'));
 const projectedEntries=projected.map(row=>{
  const n=names.find((item:{id:string})=>item.id===row.id);
  return {id:row.id,label:n?.label ?? (row as {label?:string}).label ?? row.id,aliases:n?[n.korean,n.english,n.hanja,...n.aliases].filter(Boolean):[]};
 });
 assert.equal(searchEntries(projectedEntries,'측면삼각근')[0]?.entry.id,'HA-P-000015');
});
test('splenius capitis names share one lookup candidate',()=>{for(const q of ['머리널판근','頭板狀筋','Splenius capitis muscle','musculus splenius capitis']) assert.equal(searchEntries(entries,q)[0]?.entry.id,'LOOKUP-SPLENIUS-CAPITIS',q)});
test('splenius cervicis and colli names share one lookup candidate',()=>{for(const q of ['목널판근','頸板狀筋','Splenius cervicis muscle','Splenius colli muscle','musculus splenius colli']) assert.equal(searchEntries(entries,q)[0]?.entry.id,'LOOKUP-SPLENIUS-CERVICIS',q)});
test('short Korean typo does not fuzzily match unrelated muscles',()=>assert.equal(searchEntries(entries,'승무').length,0));
test('unrelated query has no results',()=>assert.equal(searchEntries(entries,'unrelatedmuscle').length,0));
test('historical peroneus synonym resolves to fibularis',()=>assert.equal(searchEntries(entries,'peroneus longus')[0]?.entry.id,'HA-M-000005'));
test('T11-B02 learner catalog English and Latin terms stay attached to their ten existing group IDs',()=>{
 for(const id of b02Ids){
  const terms=catalog.terms.filter((term:{conceptId:string;language:string;text:string|null})=>term.conceptId===id&&['en','la'].includes(term.language)&&term.text);
  assert.equal(terms.length,2,id);
  for(const term of terms) assert.equal(searchEntries(b02SearchEntries,term.text)[0]?.entry.id,id,`${id}: ${term.text}`);
 }
});
test('T11-B02 attested Korean/Hanja names resolve to existing groups and unresolved near-matches stay withheld',()=>{
 for(const [query,id] of [
  ['두부근','HA-G-000001'],['머리근육','HA-G-000001'],['頭部筋','HA-G-000001'],
  ['외안근','HA-G-000002'],['바깥눈근육','HA-G-000002'],['外眼筋','HA-G-000002'],
  ['저작근','HA-G-000003'],['씹기근육','HA-G-000003'],['咀嚼筋','HA-G-000003'],
  ['혀근육','HA-G-000004'],['흉부근','HA-G-000006'],['胸部筋','HA-G-000006'],
  ['팔근육','HA-G-000007'],['다리근육','HA-G-000010'],
 ] as [string,string][]){
  assert.equal(searchEntries(b02SearchEntries,query)[0]?.entry.id,id,query);
 }
 for(const query of ['설근','가슴근육','어깨위팔근육','회전근개','돌림근띠','回旋腱板']){
  assert.equal(searchEntries(b02SearchEntries,query).length,0,`${query} must remain unassigned pending source/group review`);
 }
});
test('T11-B03 English and Latin index terms stay attached to the ten assigned existing IDs',()=>{
 for(const id of b03Ids){
  const terms=catalog.terms.filter((term:{conceptId:string;language:string;text:string|null})=>term.conceptId===id&&['en','la'].includes(term.language)&&term.text);
  assert.equal(terms.length,2,id);
  for(const term of terms) assert.equal(searchEntries(b03SearchEntries,term.text)[0]?.entry.id,id,`${id}: ${term.text}`);
 }
});
test('T11-B03 attested Korean and source Hanja resolve to their same existing IDs',()=>{
 for(const [query,id] of [
  ['종아리앞칸','HA-G-000013'],['종아리가쪽칸','HA-G-000014'],['종아리뒤칸','HA-G-000015'],
  ['상직근','HA-M-000007'],['위곧은근','HA-M-000007'],['上直筋','HA-M-000007'],
  ['하직근','HA-M-000008'],['아래곧은근','HA-M-000008'],['下直筋','HA-M-000008'],
  ['내직근','HA-M-000009'],['안쪽곧은근','HA-M-000009'],['內直筋','HA-M-000009'],
  ['외직근','HA-M-000010'],['가쪽곧은근','HA-M-000010'],['外直筋','HA-M-000010'],
 ] as [string,string][]){
  assert.equal(searchEntries(b03SearchEntries,query)[0]?.entry.id,id,query);
 }
});
test('T11-B03 generic or narrower gluteal/foot candidates remain unlinked to the three withheld groups',()=>{
 for(const query of ['볼기근','둔근','臀筋']) assert.ok(!searchEntries(b03SearchEntries,query).some(r=>['HA-G-000011','HA-G-000012'].includes(r.entry.id)),query);
 assert.ok(!searchEntries(b03SearchEntries,'intrinsic muscles of foot').some(r=>r.entry.id==='HA-G-000016'));
});
const b04Ids = [11,12,13,14,15,16,17,18,20,21].map(number=>`HA-M-${String(number).padStart(6,'0')}`);
const b04Names = names.filter((name:{id:string})=>b04Ids.includes(name.id));
const b04Concepts = mergeLearningConcepts(catalog.muscleConcepts.filter((concept:{id:string})=>b04Ids.includes(concept.id)),b04Names);
const b04SearchEntries = b04Concepts.map((concept:{id:string;label?:string})=>{
 const id=concept.id;
 const overlay=names.find((n:{id:string})=>n.id===id) as {label:string;korean:string;english:string;hanja:string;aliases:string[]}|undefined;
 const terms=catalog.terms.filter((term:{conceptId:string})=>term.conceptId===id);
 const korean=terms.find((term:{language:string;text:string|null})=>term.language==='ko'&&term.text)?.text;
 const english=terms.find((term:{language:string;text:string|null})=>term.language==='en'&&term.text)?.text;
 const latin=terms.find((term:{language:string;text:string|null})=>term.language==='la'&&term.text)?.text;
 return {id,label:overlay?.label ?? korean ?? english ?? latin ?? concept.label ?? id,aliases:[overlay?.korean,overlay?.english,overlay?.hanja,...overlay?.aliases ?? [],...terms.map((term:{text:string|null})=>term.text)].filter(Boolean)};
});
test('T11-B04 English and Latin TA2 observations stay attached to the ten assigned existing muscle IDs',()=>{
 for(const id of b04Ids){
  const terms=catalog.terms.filter((term:{conceptId:string;language:string;text:string|null})=>term.conceptId===id&&['en','la'].includes(term.language)&&term.text);
  assert.equal(terms.length,2,id);
  for(const term of terms) assert.equal(searchEntries(b04SearchEntries,term.text)[0]?.entry.id,id,`${id}: ${term.text}`);
 }
});
test('T11-B04 attested Korean names and source Hanja resolve to the same existing IDs; incomplete Hanja stays withheld',()=>{
 for(const [query,id] of [
  ['상사근','HA-M-000011'],['위빗근','HA-M-000011'],['上斜筋','HA-M-000011'],
  ['교근','HA-M-000012'],['깨물근','HA-M-000012'],['咬筋','HA-M-000012'],
  ['측두근','HA-M-000013'],['관자근','HA-M-000013'],['側頭筋','HA-M-000013'],
  ['외측익돌근','HA-M-000014'],['가쪽날개근','HA-M-000014'],['外側翼突筋','HA-M-000014'],
  ['내측익돌근','HA-M-000015'],['안쪽날개근','HA-M-000015'],['內側翼突筋','HA-M-000015'],
  ['이설근','HA-M-000016'],['턱끝혀근','HA-M-000016'],
  ['설골설근','HA-M-000017'],['목뿔혀근','HA-M-000017'],['舌骨舌筋','HA-M-000017'],
  ['경돌설근','HA-M-000018'],['붓혀근','HA-M-000018'],['莖突舌筋','HA-M-000018'],
  ['광배근','HA-M-000020'],['넓은등근','HA-M-000020'],['廣背筋','HA-M-000020'],
  ['대능형근','HA-M-000021'],['큰마름근','HA-M-000021'],['大菱形筋','HA-M-000021'],
 ] as [string,string][]){
  assert.equal(searchEntries(b04SearchEntries,query)[0]?.entry.id,id,query);
 }
 // The generic substring search can match complete Hanja compounds for other muscles; it must not assign this fragment to genioglossus.
 assert.ok(!searchEntries(b04SearchEntries,'舌筋').some(result=>result.entry.id==='HA-M-000016'),'partial Hanja fragment must not become a genioglossus synonym');
});
const b05Ids = Array.from({length:10},(_,i)=>`HA-M-${String(i+22).padStart(6,'0')}`);
const b05Names = names.filter((name:{id:string})=>b05Ids.includes(name.id));
const b05Concepts = mergeLearningConcepts(catalog.muscleConcepts.filter((concept:{id:string})=>b05Ids.includes(concept.id)),b05Names);
const b05SearchEntries = b05Concepts.map((concept:{id:string;label?:string})=>{
 const id=concept.id;
 const overlay=names.find((n:{id:string})=>n.id===id) as {label:string;korean:string;english:string;hanja:string;aliases:string[]}|undefined;
 const terms=catalog.terms.filter((term:{conceptId:string})=>term.conceptId===id);
 const korean=terms.find((term:{language:string;text:string|null})=>term.language==='ko'&&term.text)?.text;
 const english=terms.find((term:{language:string;text:string|null})=>term.language==='en'&&term.text)?.text;
 const latin=terms.find((term:{language:string;text:string|null})=>term.language==='la'&&term.text)?.text;
 return {id,label:overlay?.label ?? korean ?? english ?? latin ?? concept.label ?? id,aliases:[overlay?.korean,overlay?.english,overlay?.hanja,...overlay?.aliases ?? [],...terms.map((term:{text:string|null})=>term.text)].filter(Boolean)};
});
test('T11-B05 direct TA2 English and Latin observations resolve to their ten assigned existing IDs',()=>{
 for(const id of b05Ids){
  const terms=catalog.terms.filter((term:{conceptId:string;language:string;text:string|null})=>term.conceptId===id&&['en','la'].includes(term.language)&&term.text);
  assert.equal(terms.length,2,id);
  for(const term of terms) assert.equal(searchEntries(b05SearchEntries,term.text)[0]?.entry.id,id,`${id}: ${term.text}`);
 }
});
test('T11-B05 attested customary Korean names, current Korean names and source Hanja stay on their assigned IDs',()=>{
 for(const [query,id] of [
  ['소능형근','HA-M-000022'],['작은마름근','HA-M-000022'],['小菱形筋','HA-M-000022'],
  ['견갑거근','HA-M-000023'],['어깨올림근','HA-M-000023'],['肩甲擧筋','HA-M-000023'],
  ['대흉근','HA-M-000024'],['큰가슴근','HA-M-000024'],['大胸筋','HA-M-000024'],
  ['소흉근','HA-M-000025'],['작은가슴근','HA-M-000025'],['小胸筋','HA-M-000025'],
  ['쇄골하근','HA-M-000026'],['빗장밑근','HA-M-000026'],['鎖骨下筋','HA-M-000026'],
  ['전거근','HA-M-000027'],['앞톱니근','HA-M-000027'],['前鋸筋','HA-M-000027'],
  ['내복사근','HA-M-000028'],['배속빗근','HA-M-000028'],['內腹斜筋','HA-M-000028'],
  ['복횡근','HA-M-000029'],['배가로근','HA-M-000029'],['腹橫筋','HA-M-000029'],
  ['삼각근','HA-M-000030'],['어깨세모근','HA-M-000030'],['三角筋','HA-M-000030'],['Deltoid','HA-M-000030'],
  ['극상근','HA-M-000031'],['가시위근','HA-M-000031'],['棘上筋','HA-M-000031'],
 ] as [string,string][]){
  assert.equal(searchEntries(b05SearchEntries,query)[0]?.entry.id,id,query);
 }
});
const b06Ids = Array.from({length:10},(_,i)=>`HA-M-${String(i+32).padStart(6,'0')}`);
const b06Names = names.filter((name:{id:string})=>b06Ids.includes(name.id));
const b06Concepts = mergeLearningConcepts(catalog.muscleConcepts.filter((concept:{id:string})=>b06Ids.includes(concept.id)),b06Names);
const b06SearchEntries = b06Concepts.map((concept:{id:string;label?:string})=>{
 const id=concept.id;
 const overlay=names.find((n:{id:string})=>n.id===id) as {label:string;korean:string;english:string;hanja:string|null;aliases:string[]}|undefined;
 const terms=catalog.terms.filter((term:{conceptId:string})=>term.conceptId===id);
 const korean=terms.find((term:{language:string;text:string|null})=>term.language==='ko'&&term.text)?.text;
 const english=terms.find((term:{language:string;text:string|null})=>term.language==='en'&&term.text)?.text;
 const latin=terms.find((term:{language:string;text:string|null})=>term.language==='la'&&term.text)?.text;
 return {id,label:overlay?.label ?? korean ?? english ?? latin ?? concept.label ?? id,aliases:[overlay?.korean,overlay?.english,overlay?.hanja,...overlay?.aliases ?? [],...terms.map((term:{text:string|null})=>term.text)].filter(Boolean) as string[]};
});
test('T11-B06 opened TA2 English/Latin terms and sourced synonyms stay on their ten existing IDs',()=>{
 for(const id of b06Ids){
  const terms=catalog.terms.filter((term:{conceptId:string;language:string;text:string|null})=>term.conceptId===id&&['en','la'].includes(term.language)&&term.text);
  assert.equal(terms.length,2,id);
  for(const term of terms) assert.equal(searchEntries(b06SearchEntries,term.text)[0]?.entry.id,id,`${id}: ${term.text}`);
 }
 for(const [query,id] of [
  ["Casserio's muscle",'HA-M-000036'],["Casser's perforated muscle",'HA-M-000036'],['coracobrachial muscle','HA-M-000036'],
  ['subscapular muscle','HA-M-000034'],['brachial muscle','HA-M-000037'],['triceps muscle of arm','HA-M-000038'],
  ['Musculus glutaeus maximus','HA-M-000039'],['Musculus glutaeus medius','HA-M-000040'],['mesogluteus','HA-M-000040'],['Musculus glutaeus minimus','HA-M-000041'],
 ] as [string,string][]){
  assert.equal(searchEntries(b06SearchEntries,query)[0]?.entry.id,id,query);
 }
});
test('T11-B06 attested Korean names/Hanja resolve to their assigned IDs; conflicting and unverified forms stay withheld',()=>{
 for(const [query,id] of [
  ['극하근','HA-M-000032'],['가시아래근','HA-M-000032'],['棘下筋','HA-M-000032'],
  ['소원근','HA-M-000033'],['작은원근','HA-M-000033'],['小圓筋','HA-M-000033'],
  ['견갑하근','HA-M-000034'],['어깨밑근','HA-M-000034'],['肩甲下筋','HA-M-000034'],
  ['상완이두근','HA-M-000035'],['위팔두갈래근','HA-M-000035'],['上腕二頭筋','HA-M-000035'],
  ['오훼완근','HA-M-000036'],['부리위팔근','HA-M-000036'],
  ['상완근','HA-M-000037'],['위팔근','HA-M-000037'],['上腕筋','HA-M-000037'],
  ['상완삼두근','HA-M-000038'],['위팔세갈래근','HA-M-000038'],['上腕三頭筋','HA-M-000038'],
  ['대둔근','HA-M-000039'],['큰볼기근','HA-M-000039'],['大臀筋','HA-M-000039'],
  ['중둔근','HA-M-000040'],['중간볼기근','HA-M-000040'],['中臀筋','HA-M-000040'],
  ['소둔근','HA-M-000041'],['작은볼기근','HA-M-000041'],['小臀筋','HA-M-000041'],
 ] as [string,string][]){
  assert.equal(searchEntries(b06SearchEntries,query)[0]?.entry.id,id,query);
 }
 assert.equal(b06Names.find((name:{id:string})=>name.id==='HA-M-000036')?.hanja,null,'coracobrachialis Hanja candidate remains unadopted');
 for(const query of ['極下筋','Muculus infra spinam','小園筋','小圓形筋','烏喙腕筋','烏口腕筋']){
  assert.ok(!searchEntries(b06SearchEntries,query).some(result=>b06Ids.includes(result.entry.id)),`${query} must remain unlinked pending source review`);
 }
});
const b07Ids = [...Array.from({length:7},(_,i)=>`HA-M-${String(i+42).padStart(6,'0')}`),...Array.from({length:3},(_,i)=>`HA-P-${String(i+1).padStart(6,'0')}`)];
const b07Names = names.filter((name:{id:string})=>b07Ids.includes(name.id));
const b07Concepts = mergeLearningConcepts(catalog.muscleConcepts.filter((concept:{id:string})=>b07Ids.includes(concept.id)),b07Names);
const b07SearchEntries = b07Concepts.map((concept:{id:string;label?:string})=>{
 const id=concept.id;
 const overlay=names.find((n:{id:string})=>n.id===id) as {label:string;korean:string|null;english:string;hanja:string|null;aliases:string[]}|undefined;
 const terms=catalog.terms.filter((term:{conceptId:string})=>term.conceptId===id);
 return {id,label:overlay?.label ?? (concept as {label?:string}).label ?? id,aliases:[overlay?.korean,overlay?.english,overlay?.hanja,...overlay?.aliases ?? [],...terms.map((term:{text:string|null})=>term.text)].filter(Boolean) as string[]};
});
const b07Ledger = JSON.parse(readFileSync(new URL('../../../atlas-data/terminology/term-review-batches.json',import.meta.url),'utf8'));
test('T11-B07 TA2 direct English/Latin preferred cells and synonyms resolve to their ten existing IDs',()=>{
 for(const id of b07Ids){
  const coverage=b07Ledger.canonicalCoverage.find((row:{id:string})=>row.id===id);
  const cells=coverage.sourceCrosswalkLocator.observedTableCells as Record<string,string|null>;
  for(const term of [cells.latinTerm,cells.ukEnglish,cells.usEnglish,cells.latinSynonym,cells.englishSynonym,cells.other].filter(Boolean) as string[]){
   assert.equal(searchEntries(b07SearchEntries,term)[0]?.entry.id,id,`${id}: ${term}`);
  }
  const catalogTerms=catalog.terms.filter((term:{conceptId:string;language:string;text:string|null})=>term.conceptId===id&&['en','la'].includes(term.language)&&term.text);
  for(const term of catalogTerms) assert.equal(searchEntries(b07SearchEntries,term.text)[0]?.entry.id,id,`${id}: prior crosswalk ${term.text}`);
 }
 for(const query of ['piriform muscle','musculus pyriformis','quadrate muscle of thigh','short flexor muscle of great toe','adductor muscle of great toe']){
  const expected=query==='piriform muscle'||query==='musculus pyriformis'?'HA-M-000042':query==='quadrate muscle of thigh'?'HA-M-000046':query==='short flexor muscle of great toe'?'HA-M-000047':'HA-M-000048';
  assert.equal(searchEntries(b07SearchEntries,query)[0]?.entry.id,expected,query);
 }
});
test('T11-B07 attested customary Korean/current Korean/source Hanja stay on the assigned ID',()=>{
 for(const [query,id] of [
  ['이상근','HA-M-000042'],['궁둥구멍근','HA-M-000042'],['梨狀筋','HA-M-000042'],
  ['내폐쇄근','HA-M-000043'],['속폐쇄근','HA-M-000043'],
  ['상쌍자근','HA-M-000044'],['위쌍동이근','HA-M-000044'],['上雙子筋','HA-M-000044'],
  ['하쌍자근','HA-M-000045'],['아래쌍동이근','HA-M-000045'],['下雙子筋','HA-M-000045'],
  ['대퇴방형근','HA-M-000046'],['넙다리네모근','HA-M-000046'],
  ['단무지굴근','HA-M-000047'],['짧은엄지굽힘근','HA-M-000047'],
  ['무지내전근','HA-M-000048'],['엄지모음근','HA-M-000048'],['拇趾內轉筋','HA-M-000048'],
  ['비복근 · 외측두','HA-P-000001'],['비복근 · 내측두','HA-P-000002'],['교근의 천부','HA-P-000003'],
 ] as [string,string][]){
  assert.equal(searchEntries(b07SearchEntries,query)[0]?.entry.id,id,query);
 }
});
test('T11-B07 conflicting Hanja and unsupported part translations remain unlinked',()=>{
 for(const query of ['內閉鎖筋','大槌方形筋','短母指屈筋','短足拇趾屈筋','母趾內轉筋','장딴지근 · 가쪽갈래','장딴지근 · 안쪽갈래','깨물근의 얕은 부분','咬筋']){
  assert.ok(!searchEntries(b07SearchEntries,query).some(result=>b07Ids.includes(result.entry.id)),`${query} must remain withheld pending source review`);
 }
});
const b08Ids = Array.from({length:10},(_,i)=>`HA-P-${String(i+4).padStart(6,'0')}`);
const b08Names = names.filter((name:{id:string})=>b08Ids.includes(name.id));
const b08Concepts = mergeLearningConcepts(catalog.muscleConcepts.filter((concept:{id:string})=>b08Ids.includes(concept.id)),b08Names);
const b08SearchEntries = b08Concepts.map((concept:{id:string;label?:string})=>{
 const id=concept.id;
 const overlay=names.find((n:{id:string})=>n.id===id) as {label:string;korean:string|null;english:string;hanja:string|null;aliases:string[]}|undefined;
 const terms=catalog.terms.filter((term:{conceptId:string})=>term.conceptId===id);
 return {id,label:overlay?.label ?? (concept as {label?:string}).label ?? id,aliases:[overlay?.korean,overlay?.english,overlay?.hanja,...overlay?.aliases ?? [],...terms.map((term:{text:string|null})=>term.text)].filter(Boolean) as string[]};
});
const b08Ledger = JSON.parse(readFileSync(new URL('../../../atlas-data/terminology/term-review-batches.json',import.meta.url),'utf8'));
test('T11-B08 direct TA2 English/Latin terms and recorded synonyms resolve to the ten assigned part IDs',()=>{
 for(const id of b08Ids){
  const coverage=b08Ledger.canonicalCoverage.find((row:{id:string})=>row.id===id);
  const cells=coverage.sourceCrosswalkLocator.observedTableCells as Record<string,string|null>;
  const other=(cells.other ?? '').split(';').map(value=>value.trim()).filter(Boolean);
  for(const term of [cells.latinTerm,cells.ukEnglish,cells.usEnglish,cells.latinSynonym,cells.englishSynonym,...other].filter(Boolean) as string[]){
   assert.equal(searchEntries(b08SearchEntries,term)[0]?.entry.id,id,`${id}: ${term}`);
  }
 }
});
test('T11-B08 source-attested Korean customary and current names remain attached to their existing part IDs',()=>{
 for(const [query,id] of [
  ['심부 교근','HA-P-000004'],['외익돌근 상두','HA-P-000005'],['외익돌근 하두','HA-P-000006'],
  ['승모근 상부','HA-P-000009'],['등세모근 위부분','HA-P-000009'],
  ['승모근 중부','HA-P-000010'],['등세모근 중간부분','HA-P-000010'],
  ['승모근 하부','HA-P-000011'],['등세모근 아래부분','HA-P-000011'],
  ['대흉근 쇄골부','HA-P-000012'],['큰가슴근 빗장부분','HA-P-000012'],
  ['대흉근 흉늑부','HA-P-000013'],['큰가슴근 복장갈비부분','HA-P-000013'],
 ] as [string,string][]){
  assert.equal(searchEntries(b08SearchEntries,query)[0]?.entry.id,id,query);
 }
});
test('T11-B08 missing medial-pterygoid Korean/Hanja and inherited parent Hanja remain unlinked',()=>{
 for(const query of ['안쪽날개근 깊은부분','안쪽날개근 얕은부분','내익돌근 심두','내익돌근 천두','咬筋','外翼突筋','內翼突筋','僧帽筋','大胸筋']){
  assert.ok(!searchEntries(b08SearchEntries,query).some(result=>b08Ids.includes(result.entry.id)),`${query} must remain withheld pending exact part source`);
 }
 assert.equal(b08Names.find((name:{id:string})=>name.id==='HA-P-000007')?.korean,null);
 assert.equal(b08Names.find((name:{id:string})=>name.id==='HA-P-000008')?.korean,null);
 assert.ok(b08Names.every((name:{hanja:string|null})=>name.hanja===null),'no parent Hanja may be inherited as part-specific Hanja');
});
const b09Ids = ['HA-P-000014','HA-P-000016','HA-P-000017','HA-P-000018','HA-P-000019','HA-P-000020','HA-P-000021'];
const b09Names = names.filter((name:{id:string})=>b09Ids.includes(name.id));
const b09Concepts = mergeLearningConcepts(catalog.muscleConcepts.filter((concept:{id:string})=>b09Ids.includes(concept.id)),b09Names);
const b09SearchEntries = b09Concepts.map((concept:{id:string;label?:string})=>{
 const id=concept.id;
 const overlay=names.find((n:{id:string})=>n.id===id) as {label:string;korean:string|null;english:string;hanja:string|null;aliases:string[]}|undefined;
 const terms=catalog.terms.filter((term:{conceptId:string})=>term.conceptId===id);
 return {id,label:overlay?.label ?? (concept as {label?:string}).label ?? id,aliases:[overlay?.korean,overlay?.english,overlay?.hanja,...overlay?.aliases ?? [],...terms.map((term:{text:string|null})=>term.text)].filter(Boolean) as string[]};
});
const b09Ledger = JSON.parse(readFileSync(new URL('../../../atlas-data/terminology/term-review-batches.json',import.meta.url),'utf8'));
test('T11-B09 direct TA2 English/Latin cells and synonyms resolve to their seven existing part IDs',()=>{
 for(const id of b09Ids){
  const coverage=b09Ledger.canonicalCoverage.find((row:{id:string})=>row.id===id);
  const cells=coverage.sourceCrosswalkLocator.observedTableCells as Record<string,string|null>;
  const other=(cells.other ?? '').split(';').map(value=>value.trim()).filter(Boolean);
  for(const term of [cells.latinTerm,cells.ukEnglish,cells.usEnglish,cells.latinSynonym,cells.englishSynonym,...other].filter(Boolean) as string[]){
   assert.equal(searchEntries(b09SearchEntries,term)[0]?.entry.id,id,id + ': ' + term);
  }
 }
});
test('T11-B09 attested Korean terms resolve to their exact existing part IDs, while the generic long-head term stays contextual',()=>{
 for(const [query,id] of [
  ['쇄골부','HA-P-000014'],['빗장부분','HA-P-000014'],
  ['Scapular spinal part of deltoid muscle','HA-P-000016'],
  ['상완이두근장두','HA-P-000017'],['상완 이두근 장 두','HA-P-000017'],
  ['상완두갈래근짧은갈래','HA-P-000018'],['위팔 두 갈래근 짧은 갈래','HA-P-000018'],['짧은갈래','HA-P-000018'],['상완이두박근단두','HA-P-000018'],
  ['상완삼두근장두','HA-P-000019'],['상완 삼두근 장 두','HA-P-000019'],
  ['상완 삼두근 외측두','HA-P-000020'],['위팔 세 갈래 근 가쪽 갈래','HA-P-000020'],['가쪽갈래','HA-P-000020'],['외측두','HA-P-000020'],
  ['안쪽갈래','HA-P-000021'],['내측두','HA-P-000021'],
 ] as [string,string][]){
  assert.equal(searchEntries(b09SearchEntries,query)[0]?.entry.id,id,query);
 }
 assert.deepEqual(
  new Set(searchEntries(b09SearchEntries,'긴갈래').map(result=>result.entry.id)),
  new Set(['HA-P-000017','HA-P-000019']),
  'generic long-head term must remain an explicit multi-candidate descriptor',
 );
});
test('T11-B09 unsupported deltoid wording, misleading legacy lateral-head mapping, and parent Hanja stay withheld',()=>{
 for(const query of [
  '척수부분','삼각근 척수부분','상완삼두근의 장두','lateral head of triceps muscle of arm',
  '上腕二頭筋','上腕三頭筋','三角筋','上腕三頭筋外側頭',
 ]){
  assert.ok(!searchEntries(b09SearchEntries,query).some(result=>b09Ids.includes(result.entry.id)),query + ' must remain withheld pending exact part evidence');
 }
 assert.ok(b09Names.every((name:{hanja:string|null})=>name.hanja===null),'no part-specific Hanja was verified for this batch');
});
