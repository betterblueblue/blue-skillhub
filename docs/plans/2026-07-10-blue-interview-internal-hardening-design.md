# Blue Interview Internal Hardening Design

## Scope

This pass targets author-only internal use. It fixes rules and validators that can produce a false success result. Public-product concerns such as accounts, encryption, multi-user isolation, and a runtime-enforced asset write gate are out of scope.

## Changes

1. Remove the resume total score and fixed score thresholds. Keep five readiness dimensions with observable states and explicit blockers.
2. Make analysis-to-practice transitions consistent: analysis output must ask before starting practice.
3. Require project evidence reports to record ownership and the basis for attribution. Repository existence alone cannot support first-person claims.
4. Remove the invalid Chinese JD keyword comparison from the resume static checker. Keep only explainable structure and risky-term checks.
5. Require scenario reports to reference existing, non-empty local artifacts; reject duplicate scenario IDs and passing results with P0 or P1 issues.
6. Make extended validation self-contained by validating frontmatter without the external PyYAML-based validator.

## Verification

- Add standard-library `unittest` coverage for the three scripts.
- Run the script test file directly with the bundled Python runtime.
- Run `extended_validate.py` against the skill directory.
- Run `scenario_validate.py --list` and negative structured-report cases through tests.
- Search the runtime skill for removed score thresholds, automatic practice transitions, and legacy JD keyword output.

## Deferred

- Runtime-enforced writes for session/progress assets.
- Audio-level delivery assessment.
- Public Beta behavior matrices and multi-model forward tests.
