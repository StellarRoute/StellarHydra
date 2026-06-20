# Drips Wave Maintainer Runbook

For maintainers participating in a Drips Wave. Covers repo sync, issue selection, labeling, and application responses.

## Quick Start

1. **Sync repos** — Ensure your repo is listed in the Wave dashboard and `main` is up to date.
2. **Select issues** — Review open issues, apply `Drip Wave` label to approved ones.
3. **Assign complexity** — Label each issue with `complexity:low`, `complexity:medium`, or `complexity:high`.
4. **Respond to applications** — Check `/attempt` comments and review submissions promptly.

## Applying Labels

### `Drip Wave` label

Apply this label to issues/repos that are approved for the current Wave. This signals to contributors that the issue is part of the Wave scope and eligible for points.

Via GitHub UI: Issues > Labels > + Label > type "Drip Wave"

### Complexity labels

Map `complexity:*` labels to Wave dashboard expectations:

| Label | Points expectation | Description |
|-------|-------------------|-------------|
| `complexity:low` | Small (5-15 min fix) | Typos, doc updates, simple bug fixes |
| `complexity:medium` | Medium (1-2 hours) | Feature additions, refactors, new endpoints |
| `complexity:high` | Large (half day+) | Architecture changes, new modules, security work |

The Wave dashboard expects these labels to match the complexity assessment. Reviewers should verify the label before approving submissions.

## Assignment via GitHub Assignee

1. When a contributor comments `/attempt #<number>`, review their approach.
2. If approved, assign the issue to them via GitHub's assignee field.
3. If multiple people attempt, pick the first quality submission.
4. Unassign if the contributor goes silent for >48 hours during an active Wave.

## Resolving Issues Before Wave End

Contributors earn points for issues resolved **before the Wave deadline**. Key actions:

- **Prioritize low-complexity issues** first — they complete faster and guarantee points.
- **Review submissions promptly** — delayed reviews cost contributors points.
- **Merge and close** — ensure the PR is merged and issue closed before Wave end.
- **Communicate delays** — if an issue can't be completed in time, re-label for the next Wave.

Track progress against the Wave end date in the Drips dashboard.

## Linking to ROADMAP

This Wave runbook connects to the project roadmap:

- **[Phase 2: Feature Complete](../ROADMAP.md#phase-2-feature-complete)** — Drips API integration (OQ1 dependency). Issues in this phase are high-priority for Waves since they unlock core functionality.
- **[Phase 3: Production Hardening](../ROADMAP.md#phase-3-production-hardening)** — HITL + cap policy for live drips (OQ4). Security-related issues here should be flagged `complexity:high`.

When selecting Wave issues, prefer items that unblock ROADMAP Phase 2 dependencies first.

## FAQ

**Q: Can I apply `Drip Wave` to issues I haven't reviewed?**
A: No. Only apply the label after confirming the issue is in-scope and has clear acceptance criteria.

**Q: What if an issue has no complexity label?**
A: Assign one before marking as Wave-eligible. Contributors need to know the expected effort.

**Q: Should I close issues that are out of scope?**
A: Label them `out-of-scope` and add a comment explaining why. Don't close without communication.
