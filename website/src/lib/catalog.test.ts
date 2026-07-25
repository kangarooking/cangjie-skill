import { describe, expect, it } from "vitest";
import {
  filterCatalog,
  getCatalogStats,
  loadCatalog,
  normalizeCatalogFilters,
  type RegistryEntry,
} from "./catalog";

describe("registry catalog", () => {
  it("loads all seeded packs and totals", async () => {
    const entries = await loadCatalog();
    expect(entries).toHaveLength(22);
    expect(getCatalogStats(entries)).toMatchObject({ packs: 22, skills: 300 });
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
    expect(filterCatalog(entries, { quality: "community" })).toHaveLength(6);
  });

  it("combines query, domain, quality and source filters", async () => {
    const entries = await loadCatalog();
    const results = filterCatalog(entries, {
      query: "1957",
      domain: "投资",
      quality: "verified",
      source: "github",
    });

    expect(results.map((entry) => entry.slug)).toEqual(["buffett-letters-skill"]);
  });

  it("filters bundled and GitHub sources independently", async () => {
    const entries = await loadCatalog();
    const githubEntries = filterCatalog(entries, { source: "github" });
    const bundledEntries = filterCatalog(entries, { source: "bundled" });

    expect(githubEntries.every((entry) => entry.source_type === "github")).toBe(true);
    expect(bundledEntries.every((entry) => entry.source_type === "bundled")).toBe(true);
    expect(githubEntries.length + bundledEntries.length).toBe(entries.length);
  });

  it("hides archived entries unless explicitly requested", async () => {
    const entries = await loadCatalog();
    const archived: RegistryEntry = {
      ...entries[0],
      slug: "archived-example",
      status: "archived",
    };

    expect(filterCatalog([...entries, archived], {}).some((entry) => entry.slug === archived.slug)).toBe(false);
    expect(
      filterCatalog([...entries, archived], { includeArchived: true }).some(
        (entry) => entry.slug === archived.slug,
      ),
    ).toBe(true);
  });

  it("normalizes filter values before matching or URL state", () => {
    expect(
      normalizeCatalogFilters({
        query: "  巴菲特  ",
        domain: " 投资 ",
        quality: "invalid",
        source: "github",
      }),
    ).toEqual({
      query: "巴菲特",
      domain: "投资",
      quality: "",
      source: "github",
      includeArchived: false,
    });
  });
});
