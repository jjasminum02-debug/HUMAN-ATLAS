# HUMAN ATLAS local text explorer

This is a private, local study interface for the six T05 pilot muscle concepts and the two recorded gastrocnemius head concepts. It reads the project catalog at Vite startup/build time; the selected IDs come from `atlas-data/catalog/catalog-status.json`. Display terms, attachment descriptions, evidence locators, and source records are projected from `canonical-catalog.json`.

The catalog is partial. Korean Hangul/Hanja terms are held as missing, English/Latin terms still need review, and historical-source anatomy claims remain `needs_review`. The interface presents those states and does not imply that content has been anatomically reviewed. No 3D viewer, assessment, patient function, or public deployment is included.

FIPAT terminology and Gray source summaries have project-recorded internal-use constraints. Keep this app and generated bundles local; do not publish or redistribute them. Source links and recorded locators are shown alongside the associated records.

## Run locally

Requirements: Node.js 20.19+ or 22.12+ and pnpm.

On this workspace machine, `node` and `pnpm` are provided by the Codex bundled runtime and are not on the default shell `PATH`. To use the same runtime used for verification:

```sh
export PATH="/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback:$PATH"
```

On another machine, use its installed Node.js and pnpm. See the [Vite Node.js requirements](https://vite.dev/guide/) before selecting a runtime.

```sh
pnpm install --frozen-lockfile
pnpm dev
```

Open the local URL printed by Vite. To create and inspect a production build locally:

```sh
pnpm typecheck
pnpm build
pnpm preview
```

The selected record is saved in the URL as `?muscle=<stable-id>`. Search and list navigation use English/Latin terms and catalog IDs.
