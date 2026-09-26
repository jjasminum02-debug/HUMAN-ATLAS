import { useEffect, useMemo, useState } from 'react';
import { loadPilotCatalog, linkedEvidence, sourceForEvidence, type PilotCatalog } from '../data/catalog';
import { findMuscles, learningConcepts, nameFor, nameSources, structureSummary } from '../data/learning';
import { GLBViewer } from '../viewer/GLBViewer';
import { attachmentContextById } from '../viewer/attachmentContext';
import './styles.css';

type TabName = '구조' | '기능' | '평가';
export default function App() {
  const [catalog, setCatalog] = useState<PilotCatalog | null>(null);
  const [error, setError] = useState('');
  const [selectedId, setSelectedId] = useState('HA-M-000001');
  const [query, setQuery] = useState('');
  const [tab, setTab] = useState<TabName>('구조');
  const [scope, setScope] = useState<'model' | 'all'>('model');
  const [activeAttachmentId, setActiveAttachmentId] = useState<string | null>(null);
  useEffect(() => { let active = true; loadPilotCatalog().then(c => { if (active) setCatalog(c); }).catch(e => { if (active) setError(String(e)); }); return () => { active = false; }; }, []);
  useEffect(() => {
    const sync = () => { setSelectedId(new URLSearchParams(location.search).get('muscle') ?? 'HA-M-000001'); setTab('구조'); setActiveAttachmentId(null); };
    sync(); window.addEventListener('popstate', sync); return () => window.removeEventListener('popstate', sync);
  }, []);
  const concepts = useMemo(() => catalog ? learningConcepts(catalog) : [], [catalog]);
  const viewerConcepts = useMemo(() => concepts.map(c => ({ id: c.id, entityType: c.entityType, parentId: typeof c.parentId === 'string' ? c.parentId : null })), [concepts]);
  if (error) return <main className="load-state"><h1>자료를 불러오지 못했습니다</h1><p>{error}</p><button onClick={() => location.reload()}>다시 시도</button></main>;
  if (!catalog) return <main className="load-state" role="status">Human Atlas를 준비하고 있습니다…</main>;
  const selected = concepts.find(c => c.id === selectedId);
  const name = nameFor(catalog, selectedId);
  const parent = selected?.entityType === 'muscle_part' && typeof selected.parentId === 'string' ? selected.parentId : selectedId;
  const parts = concepts.filter(c => c.entityType === 'muscle_part' && c.parentId === parent);
  const owners = new Set([selectedId, ...concepts.filter(c => c.parentId === selectedId).map(c => c.id)]);
  const attachments = catalog.attachments.filter(a => owners.has(String(a.muscleOrPartId)));
  const canShow = catalog.pilotMuscleIds.includes(selectedId) || catalog.headPartIds.includes(selectedId);
  const results = findMuscles(catalog, query).filter(r => query.trim() || scope === 'all' || catalog.pilotMuscleIds.includes(r.entry.id));
  function choose(id: string) {
    setSelectedId(id); setTab('구조'); setActiveAttachmentId(null);
    const url = new URL(location.href); url.searchParams.set('muscle', id); history.pushState(null, '', url);
  }
  return <div className="study-shell">
    <a className="skip-link" href="#study-details">근육 설명으로 이동</a>
    <header className="study-header">
      <a className="brand" href="/"><span className="brand-dot"/> HUMAN ATLAS <small>구조를 보고, 움직임을 이해하다</small></a>
      <label className="global-search"><span aria-hidden="true">⌕</span><input type="search" aria-label="구조 검색" placeholder="구조 이름 · 한글, English" value={query} onChange={e => setQuery(e.target.value)} autoComplete="off"/>{query && <button aria-label="검색 지우기" onClick={() => setQuery('')}>×</button>}</label>
    </header>
    <div className="study-layout">
      <aside className="study-sidebar">
        <div className="sidebar-heading"><span className="eyebrow">EXPLORE ANATOMY</span><h1>근육 탐색</h1><p>이름이 달라도, 같은 근육으로.</p></div>
        <div className="scope-control" aria-label="목록 범위"><button aria-pressed={scope === 'model'} onClick={() => setScope('model')}>3D 근육</button><button aria-pressed={scope === 'all'} onClick={() => setScope('all')}>전체 목록</button></div>
        <p className="result-count" role="status">{query ? `검색 결과 ${results.length}` : scope === 'model' ? '오른쪽 종아리 · 6개 근육' : `${results.length}개 항목 · 부분 목록`}</p>
        <nav className="study-list" aria-label="근육 목록">{results.map(({entry, approximate}) => <button key={entry.id} className={entry.id === selectedId || entry.id === parent ? 'selected' : ''} aria-pressed={entry.id === selectedId} onClick={() => choose(entry.id)}><span>{entry.label}</span><small>{nameFor(catalog, entry.id).en}</small>{approximate && <em>비슷한 이름</em>}</button>)}{results.length === 0 && <p className="quiet-note">찾는 이름이 아직 등록되지 않았습니다. 다른 언어 이름으로도 검색해 보세요.</p>}</nav>
        <div className="sidebar-bottom"><span className="small-dot"/> 구조부터 차근차근<small>현재 3D 범위는 오른쪽 종아리입니다.</small></div>
      </aside>
      <div className="study-stage">
        <div className="stage-caption"><span className="eyebrow">INTERACTIVE ANATOMY</span><h2>{canShow ? '오른쪽 종아리' : '근육 사전'}</h2><p>{canShow ? '근육을 선택하고 주변 구조를 살펴보세요.' : '이름을 먼저 익히고, 구조는 차례로 연결합니다.'}</p></div>
        <GLBViewer selectedEntityId={selectedId} activeAttachmentId={activeAttachmentId} concepts={viewerConcepts} attachments={catalog.attachments} claims={catalog.claims} onSelectEntity={choose} onClearAttachment={() => setActiveAttachmentId(null)} studyMode/>
        <div className="stage-credit">BodyParts3D · CC BY 4.0 <details><summary>자료 안내</summary><p>BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International. 원본 형상을 좌표 변환했습니다. 형태와 부착 위치는 검토 중입니다.</p></details></div>
      </div>
      <main className="study-details" id="study-details" tabIndex={-1}>
        {selected ? <>
          <div className="detail-top"><span className="eyebrow">MUSCLE ATLAS</span><span className="status-dot">학습 초안</span></div>
          <h2>{name.label}</h2><p className="english-name"><span>영어명</span> {name.en || '—'}</p>
          <div className="names-card" aria-label="이름"><div><span>우리말명</span><strong>{name.koModern || '—'}</strong></div><div><span>한자어명 (한글 표기)</span><strong>{name.koTraditional || '—'}</strong></div></div>
          <div className="study-tabs" role="tablist" aria-label="학습 내용">{(['구조','기능','평가'] as TabName[]).map(t => <button key={t} role="tab" id={`tab-${t}`} aria-controls="study-tab-panel" aria-selected={tab === t} onClick={() => setTab(t)}>{t}</button>)}</div>
          <section id="study-tab-panel" role="tabpanel" aria-labelledby={`tab-${tab}`}>
          {tab === '구조' ? <>
            {parts.length > 0 && <div className="part-pills" aria-label="근육 부분"><button aria-pressed={selectedId === parent} onClick={() => choose(parent)}>전체</button>{parts.map(part => <button key={part.id} aria-pressed={part.id === selectedId} onClick={() => choose(part.id)}>{nameFor(catalog, part.id).label.split(' · ').at(-1)}</button>)}</div>}
            {(['origin','insertion'] as const).map(role => <section className="attachment-section attachment-summary-block" key={role}>
              <h3><i className={role}/>{role === 'origin' ? '기시' : '정지'}<span>{role === 'origin' ? 'ORIGIN' : 'INSERTION'}</span></h3>
              {structureSummary(selectedId, role) ? <p>{structureSummary(selectedId, role)}</p> : <p className="quiet-note">이 근육의 {role === 'origin' ? '기시' : '정지'} 설명은 준비 중입니다.</p>}
            </section>)}
            {attachments.length > 0 && <details className="attachment-context-disclosure">
              <summary>부착별 관련 뼈와 영문 근거 보기</summary>
              {(['origin','insertion','other_attachment'] as const).filter(role => attachments.some(a => a.role === role)).map(role => {
                const roleAttachments = attachments.filter(a => a.role === role);
                return <section className="attachment-section" key={role}>
                  <h3><i className={role}/>{role === 'origin' ? '기시 문맥' : role === 'insertion' ? '정지 문맥' : '그 외 부착'}</h3>
                  <div className="attachment-candidates">{roleAttachments.map(a => {
                    const context = attachmentContextById.get(a.id);
                    return <button key={a.id} type="button" aria-pressed={activeAttachmentId === a.id} aria-label={`${role === 'origin' ? '기시' : role === 'insertion' ? '정지' : '부착'} 설명 선택`} onClick={() => setActiveAttachmentId(a.id)}>
                      <span>{context?.contextMeshAssetId ? '관련 뼈 강조' : '3D 위치 표시 보류'}</span>
                      <small>{context?.contextMeshAssetId ? '정확한 부착면은 미지정' : '표적 구조 3D 미확보 · 위치 표시 보류'}</small>
                    </button>;
                  })}</div>
                  <details className="attachment-source-detail">
                    <summary>영문 상세 설명과 판본 펼치기</summary>
                    {roleAttachments.map(a => {
                      const claim = catalog.claims.find(c => c.id === a.descriptionClaimId);
                      const value = claim?.value as { summary?: string; edition?: string } | undefined;
                      return <div className="attachment-source-item" key={a.id}>
                        {value?.summary && <p lang="en">{value.summary}</p>}
                        {value?.edition && <small>{value.edition}</small>}
                      </div>;
                    })}
                  </details>
                </section>;
              })}
              <p className="quiet-note">부착 설명은 Gray 1918년판에 근거한 검토 전 요약입니다. 강조된 뼈 전체는 표면 검토 대상이며 정확한 부착 영역은 아직 연결되지 않았습니다.</p>
            </details>}
          </> : <div className="upcoming"><span>{tab === '기능' ? '↗' : '◎'}</span><h3>{tab} 자료를 준비하고 있습니다</h3><p>{tab === '기능' ? '관절의 움직임, 자세에 따른 역할과 안정화 작용을 연결할 예정입니다.' : '검사 목적, 시행 방법과 결과를 해석하는 순서를 연결할 예정입니다.'}</p></div>}
          </section>
          <details className="study-sources"><summary>출처와 자료 상태</summary><p>용어는 웹 자료 대조본이며, 부착 설명은 Gray 1918년판 요약을 AI가 번역한 초안입니다. 현대 문헌 및 사람 검토는 아직 완료되지 않았습니다.</p>{name.sources.map(id => { const s = nameSources[id]; return s && <p key={id}>{s.url ? <a href={s.url} target="_blank" rel="noreferrer">{s.title} ↗</a> : s.title}<small>{s.locator}</small></p>; })}{Array.from(new Set(attachments.flatMap(a => { const c = catalog.claims.find(c => c.id === a.descriptionClaimId); return linkedEvidence(catalog,c?.evidenceIds).map(e => e.sourceId); }))).map(id => { const e = catalog.evidence.find(e => e.sourceId === id); const s = e && sourceForEvidence(catalog,e); return s && <p key={String(id)}><a href={String(s.urlOrLocalRef)} target="_blank" rel="noreferrer">{String(s.title)} ↗</a></p>; })}</details>
        </> : <div className="upcoming"><h2>선택한 근육을 찾지 못했습니다</h2><p>목록에서 근육을 선택해 주세요.</p></div>}
      </main>
    </div>
  </div>;
}
