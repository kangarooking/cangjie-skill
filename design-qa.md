# Contact QR menus — Design QA

## Evidence

- Source visual truth: `/var/folders/hr/bjd54z9s0sx7mq1dgj_lbqtc0000gp/T/codex-clipboard-76bb4461-4b09-4c72-90a4-8689f2a92dab.png`
- Source pixels: `644 × 690`
- Desktop contact implementation: `/tmp/cangjie-contact-desktop-open.png`
- Desktop group implementation: `/tmp/cangjie-group-desktop-open.png`
- Mobile contact implementation: `/tmp/cangjie-contact-mobile-400.png`
- Mobile group implementation: `/tmp/cangjie-group-mobile-400.png`
- Focused normalized comparison: `/tmp/cangjie-group-card-comparison.png`
- Desktop CSS viewport: `1440 × 778`, device scale factor `2`
- Mobile CSS viewport: `400 × 691`, device scale factor `2`
- Full-screen capture pixels: `2880 × 1800`
- States checked: contact open, group open, one-menu-at-a-time switching, outside-click close, Escape close, footer-trigger open

For the focused comparison, the source card and implementation card were cropped from their surrounding page chrome, scaled to `700px` width with Lanczos resampling, and vertically padded to a shared `700 × 840` frame before being placed side by side.

## Full-view comparison

The desktop captures show both menus anchored directly under their navigation labels without changing the header height or covering the browser edge. The mobile captures show the card constrained to the `400px` viewport with no horizontal overflow (`body.scrollWidth === innerWidth === 400`). The original landing-page hierarchy and cinematic section remain unchanged.

## Focused comparison

The normalized group-card comparison confirms the requested visual grammar: a white rounded card, dark framed QR area, offset color shadow, mono English label, and bold Chinese scan instruction. The implementation keeps the source QR asset undistorted and increases surrounding breathing room. The contact card intentionally uses the repository's complete portrait QR image rather than cropping the personal name or scan instruction.

## Required fidelity surfaces

- Fonts and typography: existing rounded display and body families are preserved; mono eyebrow, bold Chinese title, and secondary copy maintain the reference hierarchy.
- Spacing and layout rhythm: card padding, QR-to-caption gap, rounded corners, and offset shadow match the source's proportions. Desktop and mobile states stay inside the viewport.
- Colors and visual tokens: dark navy frame and white card match the website; coral contact and sky-blue group shadows adapt the reference's lime accent to the existing Pixar-style palette.
- Image quality and asset fidelity: both files are byte-identical copies of the current repository assets. Images use their original aspect ratios with no generated replacements, stretching, or QR cropping.
- Copy and content: labels distinguish personal contact from the community group and explain each channel's purpose.

## Findings

- No actionable P0, P1, or P2 differences.
- P3, accepted: the source uses a lime offset shadow while the implementation uses the website's coral/sky tokens to keep the new menus visually integrated with the existing brand.

## Interaction and console checks

- Opening one menu closes the other.
- Clicking outside and pressing Escape close the open card; Escape restores focus to the summary control.
- Both footer triggers open the correct menu.
- Contact and group controls remain available at `400px`; optional tutorial/submit header links collapse to avoid crowding.
- Chrome Console showed no page errors. Visible console messages came from installed browser extensions and Chromium's built-in language-detection notice.

## Comparison history

- Pass 1: the visual comparison found no P0/P1/P2 mismatch. During interaction review, the footer trigger's click bubbled into the outside-click handler; the handler was updated to exempt footer triggers.
- Pass 2: both footer triggers opened the intended menu, one-menu-at-a-time behavior held, desktop/mobile screenshots remained visually consistent, and no new P0/P1/P2 findings appeared.

## Implementation checklist

- [x] Use repository-owned personal and group QR assets
- [x] Add two accessible navigation menus
- [x] Add footer entry points
- [x] Support outside click, Escape, and one-menu-at-a-time behavior
- [x] Verify desktop and `400 × 691` mobile states
- [x] Verify no horizontal overflow
- [x] Check browser console
- [x] Run Astro check, Vitest, Registry validation, and production build

final result: passed
