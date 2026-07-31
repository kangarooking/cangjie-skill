export const CANONICAL_ORIGIN = "https://cangjie-skill.com";
export const SITE_NAME = "仓颉 Skill";
export const DEFAULT_SOCIAL_IMAGE = "/stills/scene-01.jpg";

export interface SeoNode {
  "@type": string | string[];
  "@id"?: string;
  [key: string]: unknown;
}

export function canonicalUrl(path = "/"): string {
  const url = new URL(path, CANONICAL_ORIGIN);
  url.search = "";
  url.hash = "";

  if (url.pathname !== "/" && !hasFileExtension(url.pathname)) {
    url.pathname = `${url.pathname.replace(/\/+$/, "")}/`;
  }

  return url.toString();
}

export function socialImageUrl(path = DEFAULT_SOCIAL_IMAGE): string {
  return new URL(path, CANONICAL_ORIGIN).toString();
}

export function serializeJsonLd(value: unknown): string {
  return JSON.stringify(value).replace(/</g, "\\u003c");
}

export function buildSitemap(paths: string[]): string {
  const urls = [...new Set(paths.map((path) => canonicalUrl(path)))];
  const body = urls
    .map((url) => `  <url><loc>${escapeXml(url)}</loc></url>`)
    .join("\n");

  return [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    body,
    "</urlset>",
    "",
  ].join("\n");
}

function escapeXml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}

function hasFileExtension(pathname: string): boolean {
  return /\/[^/]+\.[^/]+$/.test(pathname);
}
