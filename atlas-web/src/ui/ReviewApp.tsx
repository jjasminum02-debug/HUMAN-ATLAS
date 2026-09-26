import "./review.css";
import { useEffect, useMemo, useState } from "react";
import {
  displayTerms,
  linkedEvidence,
  loadPilotCatalog,
  recordLabel,
  sourceForEvidence,
  termText,
  type AtlasRecord,
  type PilotCatalog,
} from "../data/catalog";
import { learnerVisibleTerms, withoutHanScript } from "../domain/search";
import { GLBViewer } from "../viewer/GLBViewer";

const languageNames: Record<string, string> = { en: "English", la: "Latin", ko: "한국어" };
const scriptNames: Record<string, string> = { Hang: "한글", Latn: "로마자" };
const roleNames: Record<string, string> = { origin: "기시", insertion: "정지" };
const typeNames: Record<string, string> = { individual_muscle: "개별 근육", muscle_part: "근육 부분" };
const stateNames: Record<string, string> = { needs_review: "검토 대기", held: "미확인", reviewed: "검토 완료" };

function text(value: unknown): string | null {
  return typeof value === "string" && value.length > 0 ? value : null;
}

function rowValue(row: AtlasRecord, key: string): string | null {
  return text(row[key]);
}

function values(row: AtlasRecord, key: string): string[] {
  const value = row[key];
  return Array.isArray(value) ? value.filter((part): part is string => typeof part === "string") : [];
}

function preferredTerm(catalog: PilotCatalog, id: string): string {
  return termText(catalog, id, "en") ?? termText(catalog, id, "la") ?? id;
}

function termState(row: AtlasRecord): string {
  const state = rowValue(row, "reviewState");
  return state ? stateNames[state] ?? state : "상태 미기록";
}

function sourceName(source: AtlasRecord | undefined): string {
  return source ? rowValue(source, "title") ?? source.id : "출처 정보 없음";
}

function TermList({ catalog, conceptId }: { catalog: PilotCatalog; conceptId: string }) {
  const terms = learnerVisibleTerms(displayTerms(catalog, conceptId));
  if (terms.length === 0) return <p className="muted">등록된 용어가 없습니다.</p>;

  return (
    <ul className="term-list">
      {terms.map((term) => {
        const language = rowValue(term, "language") ?? "";
        const script = rowValue(term, "script") ?? "";
        const missingReason = rowValue(term, "missingReason");
        const linked = linkedEvidence(catalog, term.evidenceIds);
        return (
          <li className="term-row" key={term.id}>
            <div className="term-heading">
              <span className="term-language">
                {languageNames[language] ?? (language || "언어 미기록")}
                {scriptNames[script] ? ` · ${scriptNames[script]}` : ""}
              </span>
              <span className={`badge ${term.reviewState === "needs_review" ? "badge-review" : "badge-muted"}`}>
                {termState(term)}
              </span>
            </div>
            <p className={text(term.text) ? "term-value" : "term-value missing-value"}>
              {withoutHanScript(text(term.text) ?? "용어 미확인")}
            </p>
            {missingReason && <p className="missing-reason">{withoutHanScript(missingReason)}</p>}
            {linked.length > 0 && (
              <div className="term-evidence">
                {linked.map((item) => {
                  const source = sourceForEvidence(catalog, item);
                  return (
                    <div className="evidence-line" key={item.id}>
                      <span>{withoutHanScript(sourceName(source))}</span>
                      <span>{withoutHanScript(rowValue(item, "locator") ?? item.id)}</span>
                      {source && text(source.urlOrLocalRef) && (
                        <a href={text(source.urlOrLocalRef)!} target="_blank" rel="noreferrer">
                          출처 열기
                        </a>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </li>
        );
      })}
    </ul>
  );
}

function ClaimCard({ catalog, claim }: { catalog: PilotCatalog; claim: AtlasRecord }) {
  const value = claim.value && typeof claim.value === "object" ? (claim.value as Record<string, unknown>) : {};
  const summary = text(value.summary);
  const field = rowValue(claim, "field") ?? "기록";
  const evidence = linkedEvidence(catalog, claim.evidenceIds);
  const edition = text(value.edition);
  return (
    <article className="claim-card">
      <div className="claim-heading">
        <span>{field === "attachment_description" ? "부착 설명" : field === "tendon_course_related_structures" ? "건 주행 기록" : field}</span>
        <span className="badge badge-review">{termState(claim)}</span>
      </div>
      <p className="claim-summary">{summary ? withoutHanScript(summary) : "기록된 요약이 없습니다."}</p>
      {edition && <p className="claim-edition">판본: {withoutHanScript(edition)}</p>}
      {evidence.length > 0 ? (
        <ul className="claim-sources">
          {evidence.map((item) => {
            const source = sourceForEvidence(catalog, item);
            const url = text(source?.urlOrLocalRef);
            return (
              <li key={item.id}>
                <span className="source-title">{withoutHanScript(sourceName(source))}</span>
                <span>{withoutHanScript(rowValue(item, "locator") ?? item.id)}</span>
                {url && <a href={url} target="_blank" rel="noreferrer">원문</a>}
              </li>
            );
          })}
        </ul>
      ) : (
        <p className="muted">연결된 근거 항목이 없습니다.</p>
      )}
    </article>
  );
}

function AttachmentList({ catalog, conceptId }: { catalog: PilotCatalog; conceptId: string }) {
  const attachments = catalog.attachments.filter((item) => item.muscleOrPartId === conceptId);
  if (attachments.length === 0) return <p className="empty-note">연결된 기시·정지 기록이 아직 없습니다.</p>;

  return (
    <div className="attachment-list">
      {attachments.map((attachment) => {
        const role = rowValue(attachment, "role") ?? "구조 연결";
        const targetId = rowValue(attachment, "targetStructureId") ?? rowValue(attachment, "landmarkId");
        const claim = catalog.claims.find((row) => row.id === attachment.descriptionClaimId);
        return (
          <article className="attachment-card" key={attachment.id}>
            <div className="attachment-title">
              <span className={`role-tag role-${role}`}>{roleNames[role] ?? role}</span>
              <strong>{targetId ? recordLabel(catalog, targetId) : "대상 구조 미기록"}</strong>
            </div>
            {targetId && <p className="record-id">{targetId}</p>}
            {claim ? (
              <ClaimCard catalog={catalog} claim={claim} />
            ) : (
              <p className="empty-note">설명 claim이 연결되지 않았습니다.</p>
            )}
          </article>
        );
      })}
    </div>
  );
}

function App() {
  const [catalog, setCatalog] = useState<PilotCatalog | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    let active = true;
    loadPilotCatalog()
      .then((loaded) => {
        if (active) setCatalog(loaded);
      })
      .catch((error: unknown) => {
        if (active) setLoadError(error instanceof Error ? error.message : "카탈로그를 불러오지 못했습니다.");
      });
    return () => {
      active = false;
    };
  }, []);

  const availableIds = useMemo(
    () => new Set(catalog?.concepts.map((concept) => concept.id) ?? []),
    [catalog],
  );

  useEffect(() => {
    if (!catalog) return;
    const syncSelection = () => {
      const url = new URL(window.location.href);
      const queryId = url.searchParams.get("muscle");
      if (queryId === null) {
        const fallbackId = catalog.pilotMuscleIds.find((id) => availableIds.has(id)) ?? null;
        setSelectedId(fallbackId);
        if (fallbackId) {
          url.searchParams.set("muscle", fallbackId);
          window.history.replaceState(window.history.state, "", url);
        }
        return;
      }
      setSelectedId(availableIds.has(queryId) ? queryId : null);
    };
    syncSelection();
    window.addEventListener("popstate", syncSelection);
    return () => window.removeEventListener("popstate", syncSelection);
  }, [catalog, availableIds]);

  const concepts = catalog?.concepts ?? [];
  const viewerConcepts = useMemo(() => concepts.map((concept) => ({
    id: concept.id,
    entityType: concept.entityType,
    parentId: rowValue(concept, "parentId"),
  })), [concepts]);
  const primaryConcepts = catalog?.pilotMuscleIds.flatMap((id) => {
    const concept = concepts.find((row) => row.id === id);
    return concept ? [concept] : [];
  }) ?? [];
  const filteredConcepts = primaryConcepts.filter((concept) => {
    const query = search.trim().toLocaleLowerCase();
    if (!query || !catalog) return true;
    const searchable = [concept.id, termText(catalog, concept.id, "en"), termText(catalog, concept.id, "la")]
      .filter((value): value is string => Boolean(value))
      .join(" ")
      .toLocaleLowerCase();
    return searchable.includes(query);
  });
  const selected = concepts.find((concept) => concept.id === selectedId) ?? null;
  const selectedParentId = rowValue(selected ?? ({} as AtlasRecord), "parentId");
  const selectedMainId = selected?.entityType === "muscle_part" ? selectedParentId : selectedId;
  const selectedMain = selectedMainId ? concepts.find((concept) => concept.id === selectedMainId) : null;
  const childParts = selectedMain
    ? catalog?.headPartIds.flatMap((id) => {
        const child = concepts.find((concept) => concept.id === id && concept.parentId === selectedMain.id);
        return child ? [child] : [];
      }) ?? []
    : [];
  const selectedRegionLabels = selected && catalog
    ? values(selected, "regionIds").map((id) => {
        const region = catalog.regions.find((row) => row.id === id);
        return text(region?.label) ?? id;
      })
    : [];
  const claimsForSelected = selected
    ? catalog?.claims.filter((claim) => claim.subjectId === selected.id) ?? []
    : [];
  const missingTerms = selected && catalog
    ? learnerVisibleTerms(displayTerms(catalog, selected.id)).filter((term) => !text(term.text))
    : [];
  const catalogPartial = Boolean(catalog && catalog.catalogStatus.catalogComplete !== true);

  function choose(id: string) {
    const url = new URL(window.location.href);
    url.searchParams.set("muscle", id);
    window.history.pushState(window.history.state, "", url);
    setSelectedId(id);
  }

  if (loadError) {
    return (
      <main className="state-page" role="alert">
        <p className="eyebrow">HUMAN ATLAS · LOCAL STUDY</p>
        <h1>카탈로그를 불러오지 못했습니다</h1>
        <p>{loadError}</p>
        <p className="muted">프로젝트의 atlas-data/catalog 파일 접근 상태를 확인한 뒤 다시 실행해 주세요.</p>
      </main>
    );
  }
  if (!catalog) {
    return (
      <main className="state-page" role="status" aria-live="polite">
        <p className="eyebrow">HUMAN ATLAS · LOCAL STUDY</p>
        <h1>구조 자료를 불러오는 중입니다</h1>
        <p className="muted">파일럿 카탈로그를 읽고 있습니다.</p>
      </main>
    );
  }

  const unknownSelection = new URLSearchParams(window.location.search).has("muscle") && !selected;

  return (
    <div className="app-shell">
      <a className="skip-link" href="#details">선택한 구조 내용으로 건너뛰기</a>
      <header className="topbar">
        <div className="brand-block">
          <p className="eyebrow">LOCAL ANATOMY STUDY</p>
          <a className="brand" href="/" aria-label="HUMAN ATLAS 시작">HUMAN ATLAS</a>
        </div>
        <div className="topbar-meta">
          <span className="revision-pill">{catalog.revision ?? "revision 미기록"}</span>
          <span className="scope-pill">정적 3D 파일럿 · 검토 대기</span>
        </div>
      </header>

      <div className="catalog-notice" role="status">
        <span className="notice-mark" aria-hidden="true">i</span>
        <div>
          <strong>{catalogPartial ? "부분 카탈로그" : "카탈로그 상태 확인"}</strong>
          <p>
            현재 파일럿 ID {catalog.pilotMuscleIds.length}개를 표시합니다. 전체 근육 목록을 뜻하지 않으며,
            기록된 해부학 내용은 사람 검토 전 상태입니다.
          </p>
          {catalog.missingConceptIds.length > 0 && (
            <p>카탈로그에서 찾지 못한 ID: {catalog.missingConceptIds.join(", ")}</p>
          )}
          {catalog.warnings.includes("claims_need_review") && <p>연결된 구조 claim은 모두 검토 대기 상태입니다.</p>}
        </div>
      </div>

      <div className="explorer-layout">
        <aside className="catalog-panel" aria-label="근육 파일럿 목록">
          <div className="panel-intro">
            <p className="eyebrow">CATALOG</p>
            <h1>근육 찾아보기</h1>
            <p className="muted">이름이나 안정 ID로 검색합니다.</p>
          </div>
          <label className="search-label" htmlFor="muscle-search">검색</label>
          <input
            id="muscle-search"
            className="search-input"
            type="search"
            value={search}
            onChange={(event) => setSearch(event.currentTarget.value)}
            placeholder="이름 또는 HA-M ID"
            autoComplete="off"
          />
          <p className="list-count" aria-live="polite">표시 {filteredConcepts.length} / {primaryConcepts.length}</p>
          <nav className="muscle-list" aria-label="파일럿 근육">
            {filteredConcepts.map((concept) => {
              const mainName = preferredTerm(catalog, concept.id);
              const latin = termText(catalog, concept.id, "la");
              const partsCount = catalog.headPartIds.filter((id) =>
                concepts.some((part) => part.id === id && part.parentId === concept.id),
              ).length;
              return (
                <button
                  className={`muscle-option ${selectedMainId === concept.id ? "is-selected" : ""}`}
                  key={concept.id}
                  type="button"
                  aria-pressed={selectedMainId === concept.id}
                  onClick={() => choose(concept.id)}
                >
                  <span className="option-name">{mainName}</span>
                  {latin && latin !== mainName && <span className="option-secondary">{latin}</span>}
                  <span className="option-id">{concept.id}</span>
                  {partsCount > 0 && <span className="option-parts">부분 {partsCount}</span>}
                </button>
              );
            })}
            {filteredConcepts.length === 0 && <p className="empty-note">검색 결과가 없습니다.</p>}
          </nav>
          <p className="panel-footnote">오른쪽 종아리의 정적 mesh만 연결되어 있습니다. 이름·대상 연결은 검토 대기입니다.</p>
        </aside>

        <GLBViewer
          selectedEntityId={selectedId}
          concepts={viewerConcepts}
          attachments={catalog.attachments}
          claims={catalog.claims}
          onSelectEntity={choose}
        />

        <main className="detail-panel" id="details" tabIndex={-1}>
          {unknownSelection ? (
            <section className="empty-state" role="status">
              <p className="eyebrow">UNAVAILABLE ID</p>
              <h2>선택한 ID를 이 파일럿에서 찾을 수 없습니다</h2>
              <p>주소의 <code>muscle</code> 값을 확인하거나 왼쪽 목록에서 자료를 선택해 주세요.</p>
            </section>
          ) : selected ? (
            <>
              <section className="detail-heading">
                <div className="detail-title-row">
                  <div>
                    <p className="eyebrow">{typeNames[String(selected.entityType)] ?? "구조 항목"}</p>
                    <h2>{preferredTerm(catalog, selected.id)}</h2>
                    {termText(catalog, selected.id, "la") && termText(catalog, selected.id, "la") !== preferredTerm(catalog, selected.id) && (
                      <p className="latin-title">{termText(catalog, selected.id, "la")}</p>
                    )}
                  </div>
                  <span className="stable-id">{selected.id}</span>
                </div>
                <div className="detail-meta">
                  {selectedRegionLabels.map((label) => <span className="region-chip" key={label}>{label}</span>)}
                  <span className="badge badge-review">내용 검토 대기</span>
                </div>
              </section>

              {missingTerms.length > 0 && (
                <section className="missing-banner" aria-label="미확인 용어">
                  <strong>한국어 용어 미확인</strong>
                  <p>정확한 1차 용어 출처와 항목 위치가 아직 연결되지 않았습니다. 번역어를 추정해 표시하지 않습니다.</p>
                </section>
              )}

              {childParts.length > 0 && (
                <section className="content-section part-section" aria-labelledby="parts-heading">
                  <div className="section-heading">
                    <div>
                      <p className="eyebrow">CHILD RECORDS</p>
                      <h3 id="parts-heading">하위 근육 부분</h3>
                    </div>
                    <span className="section-count">{childParts.length}</span>
                  </div>
                  <div className="part-list">
                    {childParts.map((part) => (
                      <button
                        className={`part-option ${selected.id === part.id ? "is-current" : ""}`}
                        key={part.id}
                        type="button"
                        aria-pressed={selected.id === part.id}
                        onClick={() => choose(part.id)}
                      >
                        <span>{preferredTerm(catalog, part.id)}</span>
                        <span className="option-id">{part.id}</span>
                      </button>
                    ))}
                  </div>
                </section>
              )}

              <section className="content-section" aria-labelledby="terms-heading">
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">TERMS & SOURCES</p>
                    <h3 id="terms-heading">용어와 출처</h3>
                  </div>
                  <span className="section-count">{displayTerms(catalog, selected.id).length}</span>
                </div>
                <TermList catalog={catalog} conceptId={selected.id} />
              </section>

              <section className="content-section" aria-labelledby="attachments-heading">
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">ATTACHMENTS</p>
                    <h3 id="attachments-heading">기시와 정지 기록</h3>
                  </div>
                  <span className="section-count">{catalog.attachments.filter((item) => item.muscleOrPartId === selected.id).length}</span>
                </div>
                <AttachmentList catalog={catalog} conceptId={selected.id} />
              </section>

              {claimsForSelected.length > 0 && (
                <section className="content-section" aria-labelledby="course-heading">
                  <div className="section-heading">
                    <div>
                      <p className="eyebrow">RELATED CLAIMS</p>
                      <h3 id="course-heading">연결된 추가 구조 기록</h3>
                    </div>
                    <span className="section-count">{claimsForSelected.length}</span>
                  </div>
                  <div className="claim-list">
                    {claimsForSelected.map((claim) => <ClaimCard key={claim.id} catalog={catalog} claim={claim} />)}
                  </div>
                </section>
              )}

              <section className="content-section source-state" aria-labelledby="review-heading">
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">REVIEW STATE</p>
                    <h3 id="review-heading">검토 상태</h3>
                  </div>
                  <span className="badge badge-review">needs_review</span>
                </div>
                <p>이 화면은 출처 연결과 데이터 구조를 보여 줍니다. 등록된 내용의 해부학적 검토 완료를 뜻하지 않습니다.</p>
                <p className="record-id">원본 레코드 ID: {selected.id}</p>
              </section>
            </>
          ) : (
            <section className="empty-state" role="status">
              <p className="eyebrow">NO PILOT RECORD</p>
              <h2>표시할 구조가 없습니다</h2>
              <p>카탈로그 데이터에 파일럿 ID가 있는지 확인해 주세요.</p>
            </section>
          )}
        </main>
      </div>
      <footer className="page-footer">
        <span>HUMAN ATLAS · 로컬 학습 자료</span>
        <span>임상 진단·치료 목적이 아닙니다.</span>
      </footer>
    </div>
  );
}

export default App;
