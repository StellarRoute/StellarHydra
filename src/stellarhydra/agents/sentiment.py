# Sentiment stub hook for future NLP-based volume shift signals (Phase 2+).
from __future__ import annotations

from pydantic import BaseModel


class SentimentSignal(BaseModel):
    source: str = "stub"
    score: float = 0.0
    asset: str = ""
    note: str = "Sentiment integration not yet implemented"


def fetch_sentiment_stub(asset: str) -> SentimentSignal:
    return SentimentSignal(asset=asset, note="Returning neutral stub sentiment")
