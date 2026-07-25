# Cangjie Skill Official Site Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Turn the existing Astro MVP into a distinctive, production-ready Cangjie Skill official site with complete discovery, Agent installation, and GitHub contribution flows.

**Architecture:** Keep the existing static Astro architecture and GitHub Pages deployment. Registry YAML remains the only content source; build-time loaders feed static pages, while small browser scripts handle filtering, clipboard, drafts, and local ZIP generation. The standalone vinext site is a visual reference only.

**Tech Stack:** Astro 7, TypeScript, YAML Registry, JSON Schema/Ajv, JSZip, Fuse.js, Vitest, GitHub Pages.

---

### Task 1: Freeze the product and visual contract

**Files:**
- Create: `docs/plans/2026-07-25-cangjie-skill-official-site-redesign-design.md`
- Create: `docs/plans/2026-07-25-cangjie-skill-official-site-redesign.md`
- Reference: `docs/requirements/2026-07-21-cangjie-skill-website-prd.md`

**Step 1:** Record the canonical repository, Registry source, install-guide URL, visual direction, route set, and explicit non-goals.

**Step 2:** Review the plan against the PRD and confirm every P0 journey has a task and verification step.

**Step 3:** Run `git diff --check`.

Expected: no whitespace errors.

**Step 4:** Commit.

```bash
git add docs/plans/2026-07-25-cangjie-skill-official-site-redesign*
git commit -m "docs: plan official site redesign"
```

### Task 2: Harden catalog behavior and P1 URL state

**Files:**
- Modify: `website/src/lib/catalog.ts`
- Modify: `website/src/lib/catalog.test.ts`
- Modify: `website/src/pages/skills/index.astro`
- Test: `website/src/lib/catalog.test.ts`

**Step 1:** Add failing tests for archived-entry visibility, source filtering, combined filters, and normalized query state.

**Step 2:** Run `npm test -- --run src/lib/catalog.test.ts`.

Expected: new tests fail before implementation.

**Step 3:** Extend `filterCatalog` with source and archived behavior while keeping the Registry loader as the single data source.

**Step 4:** Update the directory script so `q`, `domain`, `quality`, and `source` are restored from and written to the URL.

**Step 5:** Run `npm test -- --run src/lib/catalog.test.ts`.

Expected: catalog tests pass.

**Step 6:** Commit.

```bash
git add website/src/lib/catalog.ts website/src/lib/catalog.test.ts website/src/pages/skills/index.astro
git commit -m "feat: harden skill catalog filtering"
```

### Task 3: Build the design system, shell, and redesigned home

**Files:**
- Modify: `website/src/styles/global.css`
- Modify: `website/src/layouts/BaseLayout.astro`
- Modify: `website/src/pages/index.astro`
- Modify: `website/src/components/SkillCard.astro`
- Create: `website/src/components/CinematicJourney.astro`
- Copy: selected optimized assets into `website/public/brand/`, `website/public/stills/`, and `website/public/media/`
- Modify: `website/src/lib/catalog.test.ts`

**Step 1:** Add a rendered-output assertion that the home includes dynamic Registry stats, the primary routes, and the cinematic journey fallback content.

**Step 2:** Run the focused test and confirm the new assertion fails.

**Step 3:** Implement the “Eastern Knowledge Engineering Archive” design tokens, typography, global shell, focus styles, reduced-motion rules, header, and footer.

**Step 4:** Implement `CinematicJourney.astro` using progressive enhancement: useful static content first, optional scroll-synced video on capable desktop browsers, and still-image cards on mobile or reduced-motion devices.

**Step 5:** Rebuild the home with dynamic statistics, three-step usage, featured Packs, and contribution CTA.

**Step 6:** Redesign `SkillCard.astro` as an archival catalog card shared by home and directory.

**Step 7:** Run `npm test`, `npm run check`, and `npm run build`.

Expected: all pass; built home contains dynamic counts and links.

**Step 8:** Commit.

```bash
git add website/src website/public
git commit -m "feat: redesign official site home"
```

### Task 4: Redesign the Skills directory

**Files:**
- Modify: `website/src/pages/skills/index.astro`
- Modify: `website/src/components/SkillCard.astro`
- Modify: `website/src/styles/global.css`
- Test: `website/src/lib/catalog.test.ts`

**Step 1:** Add tests covering query, domain, quality, source, empty state, and archived-item behavior.

**Step 2:** Implement the archive-index layout, filter summary, URL restoration, clear-all action, and accessible live result count.

**Step 3:** Verify keyboard operation and 390px responsive layout.

**Step 4:** Run catalog tests, Astro check, and build.

**Step 5:** Commit with `feat: redesign skill discovery`.

### Task 5: Redesign Pack detail and Agent installation

**Files:**
- Modify: `website/src/pages/skills/[slug].astro`
- Modify: `website/src/lib/install.ts`
- Modify: `website/src/lib/install.test.ts`
- Modify: `website/src/styles/global.css`

**Step 1:** Add failing tests for GitHub and bundled install prompts and the fixed canonical guide URL.

**Step 2:** Build the content archive plus sticky Agent installation desk.

**Step 3:** Add clipboard failure handling with selectable-text fallback and screen-reader status.

**Step 4:** Verify external source links, mobile install-card priority, and Registry metadata.

**Step 5:** Run install tests, Astro check, and build.

**Step 6:** Commit with `feat: refine agent installation flow`.

### Task 6: Redesign the learning journey

**Files:**
- Modify: `website/src/pages/learn.astro`
- Modify: `website/src/styles/global.css`

**Step 1:** Preserve the five required steps, fixed install example, verification prompt, and P0 troubleshooting topics.

**Step 2:** Apply the editorial handbook layout, sticky desktop table of contents, mobile anchors, instruction cards, and risk callouts.

**Step 3:** Add the missing “new session or rescan” FAQ.

**Step 4:** Run Astro check and build.

**Step 5:** Commit with `feat: redesign skill learning guide`.

### Task 7: Complete the contribution workflow

**Files:**
- Modify: `website/src/pages/submit.astro`
- Modify: `website/src/lib/submission.ts`
- Modify: `website/src/lib/submission.test.ts`
- Modify: `website/src/styles/global.css`

**Step 1:** Add failing tests for normalized GitHub URLs, sensitive files, folder size, ignored files, slug handling, YAML output, and both source modes.

**Step 2:** Implement draft clearing, multi-language restoration, mode-preserving state, folder-picker compatibility messaging, and explicit errors.

**Step 3:** Add clipboard fallback and preserve local-only ZIP generation.

**Step 4:** Redesign the form and sticky YAML preview without changing privacy boundaries.

**Step 5:** Run submission tests, Astro check, and build.

**Step 6:** Commit with `feat: complete skill submission workflow`.

### Task 8: Add SEO, trust, and production metadata

**Files:**
- Modify: `website/src/layouts/BaseLayout.astro`
- Create: `website/public/robots.txt`
- Create: `website/src/pages/sitemap.xml.ts`
- Modify: `website/src/pages/skills/[slug].astro`
- Create or modify: `website/public/og.png`

**Step 1:** Add canonical, Open Graph, X Card, and absolute URL helpers.

**Step 2:** Add sitemap and robots output.

**Step 3:** Add JSON-LD for Skill Pack detail pages.

**Step 4:** Create and validate one site-specific social preview image.

**Step 5:** Run build and inspect generated metadata.

**Step 6:** Commit with `feat: add site discovery metadata`.

### Task 9: Full verification and release readiness

**Files:**
- Modify as needed: `.github/workflows/registry-check.yml`
- Modify as needed: `.github/workflows/deploy-pages.yml`
- Modify: `docs/requirements/2026-07-21-cangjie-skill-website-prd.md` only for confirmed state changes

**Step 1:** Run `npm run verify` in `website/`.

Expected: Registry validation, tests, Astro check, and build all pass.

**Step 2:** Start the production preview and verify `/`, `/learn`, `/skills`, one detail page, `/submit`, and `/install/cangjie-skill.md` return 200.

**Step 3:** Inspect desktop, tablet, and 390px mobile views; verify keyboard navigation and reduced motion.

**Step 4:** Run Lighthouse and fix material regressions until desktop Performance is at least 90.

**Step 5:** Run `git diff --check` and confirm unrelated user files are untouched.

**Step 6:** Update implementation-state checkboxes only with verified facts.

**Step 7:** Commit with `chore: verify official site release`.

