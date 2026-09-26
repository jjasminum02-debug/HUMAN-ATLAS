# T11-B09 source access log

Checked: 2026-09-25. Fixed scope: seven existing IDs `HA-P-000014`, `HA-P-000016`–`HA-P-000021`.

## T04 crosswalk and overlay review

Before entry, compared the seven canonical IDs and their parent/entity types with `atlas-data/catalog/canonical-catalog.json`, `atlas-data/catalog/source-crosswalk.json`, the T04-derived `canonicalCoverage` locators, and existing entries in `learning-names.json`. All seven T04 crosswalk records had row/page/Latin/English observations corresponding to the assigned catalog parts. No learner overlay or field evidence existed for these seven IDs at baseline. The original T04 crosswalk file was left unchanged; its SHA-256 before and after is `26891c9c301b79911220d491201d639cbe4a78e5d3b1fdf3df6373cd4d68238b`.

| Existing ID | Parent | TA2 row / printed page | Latin term | UK/US English | Additional TA2 cells |
|---|---|---:|---|---|---|
| HA-P-000014 | HA-M-000030 | 2453 / 89 | `Pars clavicularis musculi deltoidei` | Clavicular part of deltoid muscle | — |
| HA-P-000016 | HA-M-000030 | 2455 / 89 | `Pars spinalis scapularis musculi deltoidei` | Scapular spinal part of deltoid muscle | Latin synonym `Pars spinalis musculi deltoidei`; English synonym `Spinal part of deltoid muscle` |
| HA-P-000017 | HA-M-000035 | 2465 / 89 | `Caput longum musculi bicipitis brachii` | Long head of biceps brachii | — |
| HA-P-000018 | HA-M-000035 | 2466 / 89 | `Caput breve musculi bicipitis brachii` | Short head of biceps brachii | — |
| HA-P-000019 | HA-M-000038 | 2472 / 89 | `Caput longum musculi tricipitis brachii` | Long head of triceps brachii | — |
| HA-P-000020 | HA-M-000038 | 2473 / 89 | `Caput laterale musculi tricipitis brachii` | Lateral head of triceps brachii | Other `Caput radiale musculi tricipitis brachii` |
| HA-P-000021 | HA-M-000038 | 2474 / 89 | `Caput mediale musculi tricipitis brachii` | Medial head of triceps brachii | Latin synonym `Caput profundum musculi tricipitis brachii`; English synonym `Deep head of triceps brachii`; Other `Caput ulnare musculi tricipitis brachii` |

## Sources opened or indexed

| Source ID | URL | Edition status | Locator | Access method / check date |
|---|---|---|---|---|
| `fipat-ta2-b09-opened-original-pdf` | [FIPAT TA2 Part II PDF](https://cdn.dal.ca/content/dam/dalhousie/pdf/library/FIPAT/TA2/FIPAT-TA2-Part-2.pdf) | *Terminologia Anatomica*, Second Edition (2.07), TA2 Part II; bibliographic citation 2019; IFAA approval/adoption in 2020 | PDF text P0 front matter identifies edition/citation/approval; Chapter 4 column header PDF text P52 / printed p.73; assigned rows 2453, 2455, 2465–2466, 2472–2474 on PDF text P68 / printed p.89. Header roles: Latin term, Latin synonym, UK English, US English, English synonym, Other. | Official Dalhousie-hosted original PDF directly opened; front matter, header and exact row text read from text layer. Rendered page image/table layout not inspected. 2026-09-25. |
| `kmle-b09-biceps-opened-html` | https://m.kmle.co.kr/search.php?Search=long+head+of+biceps+brachii+muscle | KMLE aggregation; underlying dictionaries' exact editions/revisions are not exposed | Direct HTML lines 297–318: old Korean Medical Association rows for long/short biceps heads and spaced variants. Lines 376–384: named 대한해부학회 Biceps brachii m. → 위팔두갈래근; Long head → 긴갈래 [old term 장두]. | Aggregate HTML directly opened; named sections and exact visible rows read. 2026-09-25. |
| `kmle-b09-short-biceps-index` | https://m.kmle.co.kr/search.php?Page=1&Search=short+head+of+biceps+brachii+muscle | KMLE aggregation; exact underlying dictionary editions/revisions not exposed | Search-index excerpts: current 대한해부학회 Short head → 짧은갈래 [old term 단두], and named dental dictionary `caput breve musculi bicipitis brachii` → `상완 이두근 단두, 위팔 두 갈래근 짧은 갈래`. | Search-index excerpts only. Opening the exact query HTML returned Internal Error; this is not logged as an opened page. 2026-09-25. |
| `kmle-b09-triceps-lateral-opened-html` | https://m.kmle.co.kr/search.php?Search=lateral+head+of+triceps+brachii+muscle | KMLE aggregation; exact underlying dictionary editions/revisions not exposed | Direct HTML lines 302–312 include a legacy row wrongly pairing lateral triceps head with `caput longum` / 장두 (withheld conflict). Lines 368–390: named 대한해부학회 Triceps brachii m. → 위팔세갈래근; Lateral head → 가쪽갈래 [old term 외측두]. Lines 663–675: named dental dictionary `caput laterale musculii tricipitis brachii` → `상완 삼두근 외측두, 위팔 세 갈래 근 가쪽 갈래`. | Aggregate HTML directly opened; conflict and named dictionary rows read separately. 2026-09-25. |
| `kmle-b09-medial-head-index` | https://m.kmle.co.kr/search.php?Search=medial+canthus | KMLE aggregation; exact underlying dictionary editions/revisions not exposed | Search-index excerpt in named 대한해부학회 section: generic Medial head → 안쪽갈래 [old term 내측두]. It is not a triceps-specific row; the exact TA2 row provides the assigned concept context. | Search-index excerpt only; direct HTML not opened. 2026-09-25. |
| `kmle-b09-clavicular-part-index` | https://m.kmle.co.kr/search.php?Search=clav | KMLE aggregation; exact underlying dictionary editions/revisions not exposed | Search-index excerpt in named 대한해부학회 section: generic Clavicular part → 빗장부분 [old term 쇄골부]. Linked only to the exact TA2 deltoid-part row. | Search-index excerpt only; direct HTML not opened. 2026-09-25. |
| `kmle-b09-deltoid-part-gap-index` | https://m.kmle.co.kr/search.php?Search=deltoid+muscle | KMLE aggregation; exact underlying dictionary editions/revisions not exposed | Bounded deltoid query showed no attestable Korean/Hanja for the two assigned deltoid parts. A nearby clavicular part described pectoralis major and was not transferred. This is a bounded search gap, not proof of absence. | Search-index lookup only; exact deltoid part gap and candidate exclusion recorded. 2026-09-25. |
| `kmle-b09-spinal-part-gap-index` | https://m.kmle.co.kr/search.php?Search=spinal | KMLE aggregation; exact underlying dictionary editions/revisions not exposed | Named 대한해부학회 generic Spinal part → 척수부분 [old term 척수부]. Context is ambiguous and does not attest the scapular spinal part of deltoid. | Search-index excerpt only; candidate retained as an unadopted conflict, not a learner alias. 2026-09-25. |

## Field decisions and review boundary

- All field-level records in `term-review-batches.json` contain their own source URL, edition status, exact item/cell locator or missing-reason search scope, access mode and checked date. FIPAT English/Latin cell roles are based on the opened text-layer header and rows; visual table alignment and errata were not audited.
- P14 uses the observed legacy Korean `쇄골부` as its Korean display label and records current generic `빗장부분` in `korean`. Neither source supplies a full deltoid-specific Korean phrase, so no parent wording is composed.
- P16 falls back to the exact TA2 English display value because no exact full Korean term was attested. The generic `척수부분` candidate is excluded as contextually mismatched.
- P17/P18 and P19–P21 use only visible KMLE Korean strings or generic KAA head descriptors linked to the exact TA2 assigned row. `긴갈래` is shared and intentionally remains a multi-candidate search result for biceps and triceps long heads.
- P20's legacy KMLE lateral-head→long-head mapping is preserved as a conflict in evidence and excluded from learner search. FIPAT's assigned row directly says `Caput laterale`.
- Part-specific Hanja is not attested for any of the seven IDs. No parent-muscle Hanja was inherited. All Hanja values remain null.
- Search-index observations, directly opened HTML/PDF text, and human anatomy review are different states. Human anatomy review was not performed; all seven records remain `humanReviewed=false` and `humanAnatomyReviewStatus=not_performed`.
