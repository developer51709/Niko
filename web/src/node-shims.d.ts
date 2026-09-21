declare module "node:fs" {
  const fs: any;
  export default fs;
}

declare module "node:path" {
  const path: any;
  export default path;
}

declare module "node:url" {
  export function fileURLToPath(url: string | URL): string;
}

declare module "fontkit" {
  export function create(data: Uint8Array): any;
}

declare module "@resvg/resvg-js" {
  type ResvgOptions = {
    fitTo?: { mode: "width" | "height" | "zoom" | "original"; value?: number };
    font?: { fontFiles?: string[]; loadSystemFonts?: boolean };
  };
  type RenderedImage = { asPng(): Uint8Array };
  export class Resvg {
    constructor(svg: string, options?: ResvgOptions);
    render(): RenderedImage;
  }
}

