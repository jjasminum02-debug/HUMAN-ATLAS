import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import { atlasV2Plugin } from "./plugins/atlasV2.ts";
import { motionAssetsPlugin } from "./plugins/motionAssets.ts";

const projectRoot = fileURLToPath(new URL("../", import.meta.url));

export default defineConfig({
  root: projectRoot + "atlas-web",
  plugins: [atlasV2Plugin(projectRoot), motionAssetsPlugin(projectRoot)],
  server: { strictPort: true, fs: { allow: [projectRoot] } },
  preview: { strictPort: true },
  build: { manifest: true },
});
