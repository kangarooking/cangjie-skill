import { describe, expect, it } from "vitest";
import type { RegistryEntry } from "./catalog";
import { buildLlmsFullText, buildLlmsText, buildRegistryPayload } from "./geo";

const entries: RegistryEntry[] = [
  {
    schema_version: 1,
    slug: "example-skill",
    name: "示例 Skill",
    summary: "用于验证 GEO 机器可读输出的示例条目。",
    source_type: "github",
    source_url: "https://github.com/example/example-skill",
    skill_count: 3,
    domains: ["测试"],
    language: ["zh-CN"],
    status: "active",
    quality: "verified",
    use_cases: ["验证机器数据"],
  },
];
const stats = { packs: 1, skills: 3, domains: 1, contributors: 1 };

describe("GEO machine-readable outputs", () => {
  it("builds a Registry payload from the same catalog entries", () => {
    const payload = buildRegistryPayload(entries, stats);
    expect(payload.totals.skill_packs).toBe(1);
    expect(payload.totals.atomic_skills).toBe(3);
    expect(payload.packs[0]).toMatchObject({
      slug: "example-skill",
      canonical_url: "https://www.cangjie-skill.com/skills/example-skill/",
      source_url: "https://github.com/example/example-skill",
    });
  });

  it("publishes core facts and canonical discovery links in llms.txt", () => {
    const output = buildLlmsText(stats);
    expect(output).toContain("1 Skill Packs and 3 atomic Skills");
    expect(output).toContain("https://www.cangjie-skill.com/about/");
    expect(output).toContain("https://www.cangjie-skill.com/registry.json");
  });

  it("includes FAQ answers and every catalog source in the full snapshot", () => {
    const output = buildLlmsFullText(entries, stats);
    expect(output).toContain("仓颉 Skill 是什么？");
    expect(output).toContain("### 示例 Skill");
    expect(output).toContain("https://github.com/example/example-skill");
  });
});
