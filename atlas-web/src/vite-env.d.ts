/// <reference types="vite/client" />

declare module "virtual:human-atlas-catalog" {
  const value: unknown;
  export default value;
}

declare module "virtual:human-atlas-mesh-manifest" {
  const value: unknown;
  export default value;
}

declare module "*.glb?url" {
  const value: string;
  export default value;
}
