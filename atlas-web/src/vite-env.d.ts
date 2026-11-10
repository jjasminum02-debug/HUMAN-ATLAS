/// <reference types="vite/client" />

declare module "*.glb?url" {
  const value: string;
  export default value;
}
