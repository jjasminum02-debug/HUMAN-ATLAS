# Local source research tool

`source_research.py` is an offline manifest validator and report compiler. It does not search the web, call a model, read browser history, fetch URLs, or write the canonical catalog, canonical claims/reviews, learner data, or `atlas-data/terminology/ai-evidence-overlay.json`.

## Manual input path

When no search API or account is available, record only pages that were actually opened in the local JSON manifest. Add each search-results page as its own `source` and `access` row with `accessMethod: "search_index"` and `textAccess: "index_only"`. `accessOutcome: "opened"` means the listed page opened; it does not mean the underlying original text opened. A blocked, paywalled, missing, or failed original is `accessOutcome: "failed"`, `textAccess: "unavailable"`, and a non-empty `failureReason`.

For each opened original, enter a source URL, the exact edition (`editionStatus: "verified"`) or explicitly record that the edition was not exposed (`editionStatus: "not_exposed", edition: null`), the actual field locator, local access date, and method. `underlyingWorkId` and the accompanying `workIdentityBasis` are entered explicitly by the researcher. The tool never infers independence from hostnames, titles, or URL count. Two pages that rehost or cite the same work must use the same `underlyingWorkId`; if the work cannot be identified, use `null` and explain that in `workIdentityBasis`.

Each `extraction` must point to the exact opened `accessId`, `sourceId`, and `locator`. Its `valueHash` is SHA-256 of canonical JSON. Use `--hash-value` to prepare it, for example:

```sh
python3 atlas-data/sources/source_research.py --hash-value '"Short paraphrase entered from the opened source"'
```

Keep the value as a short paraphrase or structured field value. Do not paste long copyrighted passages. The hash is a tamper check, not proof that the source supports the value.

Comparison classes are explicitly entered: `agreement`, `wording_difference`, `variation`, `substantive_conflict`, or `not_comparable`. The tool records the classification and rationale; it does not infer anatomical equivalence or resolve conflicts. `assessmentMode` distinguishes `ai_candidate` from `researcher_entered`; neither means expert approval. Human anatomy review is always reported as not performed by this tool.

## Commands

Validate the schema:

```sh
python3 atlas-data/sources/source_research.py --check-schema
```

Run an explicitly prepared manifest and write local reports:

```sh
python3 atlas-data/sources/source_research.py \
  --manifest path/to/source-manifest.json \
  --output-dir path/to/local-output \
  --cache-file path/to/local-output/.source-research-cache.json
```

The manifest is capped at six individual muscle IDs and canonical IDs must resolve in `canonical-catalog.json`. Synthetic fixtures require the explicit `--allow-synthetic-fixtures` switch and remain marked `fixtureOnly`; they are never imported into learner data.

Outputs are `access-ledger.json`, `field-observations.json`, `comparison-table.csv`, `run-summary.json`, and `exceptions.json`. Project-local output is limited to `work/evidence/`; other project paths and `OpenSim_Models/` are refused. A project-local cache must remain inside the selected output directory and cannot replace one of its reports. `unavailable`, index-only, abstract/metadata-only, and comparison exceptions remain distinct. Summary labels are workflow outcomes, not T16 evidence-state promotions. Cache keys include the canonical whole-manifest fingerprint; any source, access, field value, reference, or comparison change invalidates the cached artifacts.
