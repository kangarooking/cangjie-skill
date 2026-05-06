# Stage -1 Book Fit Test Results

- **Eval mode**: dry_run
- **Date**: 2026-05-07
- **Cases**: 《三体》,《茶经》
- **Decision**: keep

## Summary

| Case | Expected | Actual | Result |
|---|---|---|---|
| 《三体》 | `alternate_artifact` | `alternate_artifact` | PASS |
| 《茶经》 | `partial_skill_pack` | `partial_skill_pack` | PASS |

## What This Validates

- Stage -1 can distinguish "high-value but not skill-fit" fiction from practical method-bearing texts.
- It recommends alternate artifacts for novels instead of forcing a full skill pack.
- It preserves a path for practical classics like 《茶经》 while limiting scope to executable methods and explicit boundaries.

## Residual Risk

- 《三体》 was evaluated without local source text, so this is a genre-level dry run rather than a full evidence-backed fit assessment.
- 《茶经》 uses an existing downstream skill pack, so it is a stronger regression sample than 《三体》.
