# StellarHydra documentation

Index of guides for the Agentic Liquidity Balancer (ALB).

## Product

| Doc | Description |
|-----|-------------|
| [PRD.md](PRD.md) | Product requirements and guardrails |
| [ROADMAP.md](ROADMAP.md) | Phase 0-3 exit criteria |

## Architecture

| Doc | Description |
|-----|-------------|
| [architecture/overview.md](architecture/overview.md) | System components and data flow |
| [architecture/langgraph-workflow.md](architecture/langgraph-workflow.md) | Graph nodes and routing |
| [architecture/agents.md](architecture/agents.md) | Predictor, strategist, executor |
| [architecture/state-model.md](architecture/state-model.md) | `HydraState` fields |

## Development

| Doc | Description |
|-----|-------------|
| [development/SETUP.md](development/SETUP.md) | Local install and first cycle |
| [development/testing.md](development/testing.md) | pytest, lint, CI |
| [configuration/env-vars.md](configuration/env-vars.md) | Environment reference |

## Integrations

| Doc | Description |
|-----|-------------|
| [integrations/stellarroute-client.md](integrations/stellarroute-client.md) | StellarRoute HTTP client |
| [integrations/drips-client.md](integrations/drips-client.md) | Drips Wave API and dry-run |
| [integrations/redis-signal-cache.md](integrations/redis-signal-cache.md) | Signal cache keys and TTL |

## Operations

| Doc | Description |
|-----|-------------|
| [api/admin-api.md](api/admin-api.md) | FastAPI endpoints |
| [workers/celery.md](workers/celery.md) | Background cycle tasks |
| [observability/metrics-and-logging.md](observability/metrics-and-logging.md) | Prometheus and structured logs |
| [security/audit-and-secrets.md](security/audit-and-secrets.md) | Audit trail and secret validation |
| [troubleshooting/common-issues.md](troubleshooting/common-issues.md) | Frequent local dev problems |
| [deploy/render.md](deploy/render.md) | Render deployment |
| [deployment/docker-compose.md](deployment/docker-compose.md) | Compose services |
