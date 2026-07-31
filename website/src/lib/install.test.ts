import { describe, expect, it } from "vitest";
import type { RegistryEntry } from "./catalog";
import { getAgentInstallPrompt, INSTALL_GUIDE_URL } from "./install";

const baseEntry: RegistryEntry = {
  schema_version: 1,
  slug: "example-skill",
  name: "Example Skill",
  summary: "A sufficiently descriptive example skill summary.",
  source_type: "github",
  source_url: "https://github.com/example/example-skill",
  skill_count: 1,
  domains: ["测试"],
  language: ["zh-CN"],
  status: "active",
  quality: "community",
  use_cases: ["完成一个测试任务"],
};

describe("Agent install prompt", () => {
  it("uses the live Cloudflare install guide", () => {
    expect(INSTALL_GUIDE_URL).toBe(
      "https://cangjie-skill.pages.dev/install/cangjie-skill.md",
    );
  });

  it("generates a copy-ready prompt for GitHub skills", () => {
    expect(getAgentInstallPrompt(baseEntry)).toBe(
      `请根据 ${INSTALL_GUIDE_URL}，从 https://github.com/example/example-skill 安装 example-skill。`,
    );
  });

  it("includes the exact bundled path when the skill lives in this repository", () => {
    expect(getAgentInstallPrompt({
      ...baseEntry,
      source_type: "bundled",
      source_url: "https://github.com/kangarooking/cangjie-skill",
      skill_path: "registry/example-skill/skill",
    })).toContain("registry/example-skill/skill");
  });

  it("can use the local guide while the site is in development", () => {
    expect(getAgentInstallPrompt(baseEntry, "http://localhost:4321/install/cangjie-skill.md"))
      .toContain("http://localhost:4321/install/cangjie-skill.md");
  });
});
