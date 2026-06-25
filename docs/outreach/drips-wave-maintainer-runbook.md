# Drips Wave maintainer runbook

This runbook helps StellarHydra maintainers prepare Wave-eligible issues, apply GitHub labels consistently, and preserve the roadmap budget across Phase 0 through Phase 3 work.

External reference: [Drips Wave maintainer docs](https://docs.drips.network/wave/maintainers/participating-in-a-wave) and [points budgets](https://docs.drips.network/wave/maintainers/points-budgets).

## Issue selection flow

1. Pick work that maps to the current roadmap phase in [docs/ROADMAP.md](../ROADMAP.md).
2. Use a clear title prefix such as `[backend]`, `[integrations]`, `[documentation]`, `[security]`, or `[infra]`.
3. Add the `Drip Wave` label only when the issue is ready for contributors.
4. Add exactly one complexity label: `complexity:low`, `complexity:medium`, or `complexity:high`.
5. Assign the accepted contributor in GitHub during an active Wave cycle so ownership is visible.
6. Resolve, merge, or close completed issues before the Wave end when possible so contributor points can be counted cleanly.

## Complexity and points budget guidance

Use complexity labels to keep the issue queue balanced. Do not spend the Wave budget only on trivial docs tasks, and do not mark production or security work as low complexity just to make it look approachable.

| Complexity label | Example issue types | Budget guidance |
|------------------|---------------------|-----------------|
| `complexity:low` | README or CONTRIBUTING updates, small doc links, typo-safe config notes, narrow unit test additions | Good for onboarding and quick review. Keep scope under one focused PR. |
| `complexity:medium` | StellarRoute client retries, Drips dry-run payload shaping, Redis cache behavior, FastAPI endpoint tests, Celery task wiring | Use for Phase 1 and Phase 2 work that touches one subsystem and requires tests. |
| `complexity:high` | Production security controls, policy caps for live drip execution, multi-agent graph changes, observability across workers and API | Reserve budget for work with real operational or fund-movement risk. Require deeper review. |

## Phase 2 Drips dependency

The roadmap marks Phase 2 as feature-complete work and depends on PRD OQ1, which asks which Drips Wave endpoints and auth model are canonical for stream CRUD. Until that dependency is resolved:

- keep implementation paths compatible with dry-run mode;
- avoid hardcoding undocumented Drips payloads;
- record assumptions in the issue or PR;
- prefer tests that validate internal plans and policy caps without live credentials.

## Review checklist for Wave issues

- The PR links the issue and states whether it is docs-only, dry-run logic, or live execution logic.
- The selected complexity label still matches the final diff.
- Production, security, or fund-movement behavior has matching tests and reviewer attention.
- The change does not replace StellarRoute routing or quote logic, in line with PRD NG1.
- Documentation links are updated when a new top-level or outreach guide is added.
