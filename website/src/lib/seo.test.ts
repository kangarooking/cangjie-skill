import { describe, expect, it } from "vitest";

import {
  buildSitemap,
  canonicalUrl,
  serializeJsonLd,
  socialImageUrl,
} from "./seo";

describe("SEO helpers", () => {
  it("normalizes canonical URLs onto the official domain", () => {
    expect(canonicalUrl("/")).toBe("https://cangjie-skill.com/");
    expect(canonicalUrl("/skills/example/?source=test#install")).toBe(
      "https://cangjie-skill.com/skills/example/",
    );
    expect(canonicalUrl("/sitemap.xml")).toBe("https://cangjie-skill.com/sitemap.xml");
  });

  it("keeps social images on the crawlable canonical origin", () => {
    expect(socialImageUrl("/brand/kangarooking-logo.jpg")).toBe(
      "https://cangjie-skill.com/brand/kangarooking-logo.jpg",
    );
  });

  it("escapes markup in JSON-LD script content", () => {
    expect(serializeJsonLd({ name: "</script>" })).toContain("\\u003c/script>");
  });

  it("builds a deduplicated canonical XML sitemap", () => {
    const sitemap = buildSitemap(["/", "/learn", "/learn/"]);

    expect(sitemap).toContain("<loc>https://cangjie-skill.com/</loc>");
    expect(sitemap).toContain("<loc>https://cangjie-skill.com/learn/</loc>");
    expect(sitemap.match(/cangjie-skill\.com\/learn/g)).toHaveLength(1);
  });
});
