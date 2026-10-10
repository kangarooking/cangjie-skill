import { describe, expect, it } from "vitest";
import { filterCatalog, getCatalogStats, loadCatalog } from "./catalog";

describe("registry catalog", () => {
  it("loads all seeded packs and totals", async () => {
    const entries = await loadCatalog();
    expect(entries).toHaveLength(23);
    expect(getCatalogStats(entries)).toMatchObject({ packs: 23, skills: 301 });
  });

  it("has unique slugs and valid GitHub sources", async () => {
    const entries = await loadCatalog();
    expect(new Set(entries.map((entry) => entry.slug)).size).toBe(entries.length);
    expect(entries.every((entry) => entry.source_url.startsWith("https://github.com/"))).toBe(true);
  });

  it("filters across Chinese metadata, domains and quality", async () => {
    const entries = await loadCatalog();
    expect(filterCatalog(entries, { query: "巴菲特" }).length).toBe(2);
    expect(filterCatalog(entries, { domain: "数学" })).toHaveLength(1);
    expect(filterCatalog(entries, { quality: "community" })).toHaveLength(7);
  });
});
