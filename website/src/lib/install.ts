import type { RegistryEntry } from "./catalog";

export const INSTALL_GUIDE_URL = "https://cangjie-skill.pages.dev/install/cangjie-skill.md";

export function getAgentInstallPrompt(entry: RegistryEntry, guideUrl = INSTALL_GUIDE_URL): string {
  const source = entry.source_type === "bundled" && entry.skill_path
    ? `${entry.source_url} 中的 ${entry.skill_path}`
    : entry.source_url;

  return `请根据 ${guideUrl}，从 ${source} 安装 ${entry.slug}。`;
}
