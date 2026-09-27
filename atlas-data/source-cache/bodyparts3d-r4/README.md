# BodyParts3D Release 4.0 local source cache (T51)

The six official source TSV indexes under `metadata/` are versioned with this
T51 inventory and are covered by the attribution below. In the active
workspace, the cache also contains byte-identical copies of the 20 OBJ files
that were already present in the T50/T15g sample inventory under `mesh/IS-A/`.
Those duplicates and the generated GLB remain local-only: a fresh checkout can
re-create them from the historical source paths by running
`python3 atlas-data/tools/ingest_bodyparts3d_r4.py --all`. The OBJ copies are
recorded in `work/evidence/T51/source-cache-file-inventory.json` by source FJ
ID, original path, header identity, byte length and SHA-256. `converted/` holds
one generated 20-mesh static QA sample; it is reproducible with the T51 ingest
script.

Official source pages:

- README and data description: https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/README_e.html
- Release 4.0 data update: https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/release_4.0_e.html
- Official download list: https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html
- Current database license: https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html

The six TSV files were retrieved over HTTPS from the official `LATEST` data
directory on 2026-09-27. Source metadata hashes and row counts are in
`atlas-data/manifests/bodyparts3d-r4-source-manifest-t51.json`.

The original OBJ duplicates and GLB are deliberately excluded from Git because
their file headers claim CC BY-SA 2.1 Japan while the current official license
page states CC BY 4.0; compatibility is unresolved in T51.

The official site describes the two mesh bundles as 99%-reduced OBJ data and
lists approximate compressed sizes of 136 MB (IS-A) and 62 MB (PART-OF). Those
archives were not downloaded in T51. The local cache has 20 existing sample
OBJ files only; their reduction profile is unverified. Missing local
FJ files are `not acquired / not attempted`, not download failures.

The official license page now lists CC BY 4.0 and the attribution below. Local
sample OBJ headers retain an older CC BY-SA 2.1 Japan claim. Preserve both
observations; distribution of the cached OBJs and derived GLB remains held
until file-level rights reconciliation.

Required attribution under the current official page:

> BodyParts3D, © The Database Center for Life Science licensed under CC
> Attribution 4.0 International
