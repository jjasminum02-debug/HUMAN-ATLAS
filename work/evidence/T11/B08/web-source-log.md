# T11-B08 source access log

Checked: 2026-09-25. Scope: the ten existing IDs `HA-P-000004`–`HA-P-000013` only.

## T04 crosswalk inspection

The T04 source crosswalk and locator register were read before entry. Each assigned row, printed page, Latin string, English string, part/head class, and parent ID matched the corresponding canonical item. The prior T04 evidence said only that the official PDF search index had been observed and the source table had not been opened. T04 files were left unchanged. The B08 coverage overlay now records the prior indexed observation and the independent original-PDF text-cell observation.

| Existing ID | Parent | T04 row / printed page | Direct TA2 Latin term | Direct TA2 UK English |
|---|---|---:|---|---|
| HA-P-000004 | HA-M-000012 | 2107 / 77 | Pars profunda masseteris | Deep part of masseter |
| HA-P-000005 | HA-M-000014 | 2110 / 77 | Caput superius musculi pterygoidei lateralis | Superior head of lateral pterygoid muscle |
| HA-P-000006 | HA-M-000014 | 2111 / 77 | Caput inferius musculi pterygoidei lateralis | Inferior head of lateral pterygoid muscle |
| HA-P-000007 | HA-M-000015 | 2114 / 77 | Caput profundum musculi pterygoidei medialis | Deep head of medial pterygoid muscle |
| HA-P-000008 | HA-M-000015 | 2115 / 77 | Caput superficiale musculi pterygoidei medialis | Superficial head of medial pterygoid muscle |
| HA-P-000009 | HA-M-000019 | 2227 / 81 | Pars descendens musculi trapezii | Descending part of trapezius muscle |
| HA-P-000010 | HA-M-000019 | 2228 / 81 | Pars transversa musculi trapezii | Transverse part of trapezius muscle |
| HA-P-000011 | HA-M-000019 | 2229 / 81 | Pars ascendens musculi trapezii | Ascending part of trapezius muscle |
| HA-P-000012 | HA-M-000024 | 2302 / 83 | Pars clavicularis musculi pectoralis majoris | Clavicular head of pectoralis major muscle |
| HA-P-000013 | HA-M-000024 | 2303 / 83 | Pars sternocostalis musculi pectoralis majoris | Sternocostal head of pectoralis major muscle |

## Accessed sources

| Source ID | URL | Edition | Locator | Access mode |
|---|---|---|---|---|
| `fipat-ta2-b08-opened-original-pdf` | <https://cdn.dal.ca/content/dam/dalhousie/pdf/library/FIPAT/TA2/FIPAT-TA2-Part-2.pdf> | TA2 Second Edition 2.07; bibliographic citation 2019; approved/adopted by IFAA in 2020 | PDF text front matter P0 lines 0–15; Chapter 4 header P52 / printed p.73 lines 3494–3495; rows on PDF text P56/printed p.77, P60/printed p.81, P62/printed p.83 as table above | Official Dalhousie-hosted original PDF directly opened. Text layer read. No rendered table-page inspection. Checked 2026-09-25. |
| `kmle-b08-masseter-index` | <https://m.kmle.co.kr/search.php?Search=deep+part+of+masseter+muscle> | KMLE aggregate; exact underlying Korean source edition/revision not exposed | Search excerpt for exact query; parent masseter description contains “심부 교근은”; no exact part Hanja. The phrase is description text, not a dedicated term row. | Search-index excerpt only; direct HTML open failed with a Unicode decoding error. Checked 2026-09-25. |
| `kmle-b08-lateral-pterygoid-index` | <https://m.kmle.co.kr/search.php?Search=pterygoid+muscle%2C+lateral> | KMLE aggregate; exact underlying dental dictionary edition/revision not exposed | Search excerpt under 경북대 치과대학 구강내과 교실 사전: superior lateral pterygoid muscle → 외익돌근 상두; inferior lateral pterygoid → 외익돌근 하두. | Search-index excerpt only; direct HTML was not opened. Checked 2026-09-25. |
| `kmle-b08-medial-pterygoid-index` | <https://m.kmle.co.kr/search.php?Search=medial+pterygoid+m> | KMLE aggregate; exact underlying Korean source edition/revision not exposed | Bounded lookup showed parent terms but no exact Korean or Hanja for either head. Exact part-phrase lookup produced no attestable Korean result. This is a search gap, not proof of absence. | Search-index parent results only; direct HTML was not opened. Checked 2026-09-25. |
| `kmle-b08-trapezius-opened-html` | <https://m.kmle.co.kr/search.php?Search=descending+part+of+trapezius> | KMLE aggregate; exact underlying dictionary edition/revision not exposed | Opened HTML lines 282–295: parent Trapezius m. → 등세모근 [old] 승모근. Lines 214–240 show parent Hanja 僧帽筋; lines 302–310 show generic “Descending part” terms. No part-specific Hanja row. | KMLE aggregate HTML directly opened. Used only to delimit parent versus part evidence; parent Hanja is not inherited. Checked 2026-09-25. |
| `yes24-b08-2018-textbook-toc-index` | <https://www.yes24.com/product/goods/58476950> | Kuribara Osamu, Korean translation, 신흥메드싸이언스, 2018-02-15 (product listing); detailed edition metadata beyond the listing is not exposed | Directly opened product page, displayed Table of contents at page lines 535 onward: trapezius entries pp.40/42/44 and pectoralis major part entries pp.22/24; current Korean, customary Korean, and English are paired in the listing. | YES24 product listing directly opened; its TOC excerpt read. The textbook body text was not accessed. Checked 2026-09-25. |

## Field-level application and limits

Every row below has individual `fieldEvidence` with the source URL, edition status, locator, access mode and check date in `term-review-batches.json`. English and Latin values are from opened FIPAT text cells. `aliases[0]` is the Latin term. Additional TA2 Other-cell aliases are recorded separately for P5, P6 and P9–P11.

| IDs | `label` source | `korean` source/state | `hanja` | `english` / Latin | Human anatomy review |
|---|---|---|---|---|---|
| P4 | KMLE indexed phrase “심부 교근”; descriptive usage, not a dedicated headword | Null: current part-specific Korean term not attested | Null: part Hanja not attested | FIPAT opened cells | Not performed |
| P5–P6 | KMLE indexed older head phrases 외익돌근 상두/하두 | Null: no current part-specific Korean term attested | Null: head-specific Hanja not attested | FIPAT opened cells and Other-cell English synonym | Not performed |
| P7–P8 | FIPAT English display fallback | Null: exact Korean head term not found in bounded lookup | Null: head-specific Hanja not found | FIPAT opened cells | Not performed |
| P9–P11 | YES24 product-listing TOC pairs Korean customary terms 승모근 상부/중부/하부 with current forms 등세모근 위부분/중간부분/아래부분 | Same directly opened TOC paired forms | Null: opened KMLE page shows parent Hanja only | FIPAT opened cells and Other-cell synonym | Not performed |
| P12–P13 | YES24 product-listing TOC pairs Korean customary terms 대흉근 쇄골부/흉늑부 with current forms 큰가슴근 빗장부분/복장갈비부분 | Same directly opened TOC paired forms | Null: no part-specific source Hanja | FIPAT opened cells | Not performed |

No patient or treatment information was gathered. No attachment, function, or assessment claim was entered. No UI or search implementation was changed.
