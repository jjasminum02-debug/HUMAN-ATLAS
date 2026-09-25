# T04 source access log — 2026-09-25

## Adopted terminology candidate

- IFAA/FIPAT official status page identifies *Terminologia Anatomica*, second edition (TA2), published online in 2019 and approved by the IFAA General Assembly. It describes a seven-column term table that separates official terms, equivalents, synonyms, and related terms. The page states that web-published IFAA terminologies are CC BY-ND 4.0 and may be revised continuously.
- Exact Part 2 publication PDF: `https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf` (Muscular System chapter).
- Official Errata PDF identified: `https://fipat.library.dal.ca/wp-content/uploads/2021/08/FIPAT-TA2-Errata.pdf`. The search result exposed corrections including rows 2646, 2680, 2688; a complete comparison of catalog rows against errata was not performed.
- FIPAT 2025 end-of-year report was published on the IFAA site on 2026-02-08. Its existence is recorded as version-watch context only; it does not establish a new TA edition or a complete catalog source.

## Retrieval limits

- The official PDF's web search index returned table excerpts with printed page and row numbers. The selected excerpts used in the partial data are recorded in `source-locator-register.json` and `atlas-data/catalog/source-crosswalk.json`.
- `curl -I -L --max-time 15 https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf` exited 6: `Could not resolve host: fipat.library.dal.ca`.
- No source PDF was saved locally; there is no local source SHA-256. Search-index text is not a substitute for visually checking row cells, the complete chapter, or a dated file snapshot.
- Source term observations are marked `needs_review`; row-column role (official Latin, English equivalent, synonym, related term) remains unverified in the local source rendering. No translations or anatomy claims were created.

## Captured table ranges

| TA2 Part 2 printed page | Index excerpt area | Captured scope |
|---|---:|---|
| 74 | 2040–2048 | head heading; extraocular group and selected eye muscles |
| 77 | 2104–2134 | mastication and tongue area; only selected muscle/part rows copied to catalog |
| 81 | 2225–2248 | selected dorsal muscle groups, trapezius parts, and back muscles |
| 83 | 2299–2314 | thorax heading and selected pectoral/thoracic rows |
| 86 | 2373–2398 | selected abdominal rows and pelvis heading |
| 89 | 2450–2479 | upper-limb/shoulder groups and selected arm rows |
| 94 | 2592–2627 | lower-limb/gluteal/thigh area; selected rows only |
| 95 | 2643–2655 | leg compartments and pilot ankle-region muscles |
| 96 | 2657–2685 | gastrocnemius heads, posterior leg, foot heading and selected foot rows |

The captured intervals are search-result excerpts, not contiguous full-section extraction. Their presence does not establish that unlisted items do not exist.
