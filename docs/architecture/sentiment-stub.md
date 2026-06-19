# Sentiment stub

Sentiment-driven volume shift detection is a Phase 2+ item. The codebase ships a neutral stub only.

## SentimentSignal model

| Field | Default |
|-------|---------|
| `source` | `"stub"` |
| `score` | `0.0` |
| `asset` | caller-provided |
| `note` | explains stub status |

## fetch_sentiment_stub

Returns `SentimentSignal(asset=asset, note="Returning neutral stub sentiment")` with no external API calls.

## Graph integration

The LangGraph cycle does **not** call `fetch_sentiment_stub` today. Predictor input is StellarRoute routing signals only. Wire this module into `collect_signals` or a dedicated node when NLP sources are available.

See `src/stellarhydra/agents/sentiment.py` and `docs/PRD.md` for roadmap context.
