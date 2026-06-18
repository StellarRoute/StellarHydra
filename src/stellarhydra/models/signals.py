# Pydantic models for routing signals ingested from StellarRoute.
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class VenueType(str, Enum):
    SDEX = "sdex"
    AMM = "amm"


class PathStep(BaseModel):
    venue_type: VenueType | str
    selling_asset: str
    buying_asset: str
    price: float | None = None


class RoutingSignal(BaseModel):
    """Normalized snapshot from StellarRoute quote/route/orderbook APIs."""

    base: str
    quote: str
    amount: str
    slippage_bps: int
    price: float | None = None
    total: float | None = None
    price_impact_bps: int | None = None
    path: list[PathStep] = Field(default_factory=list)
    route_count: int = 0
    orderbook_bid_depth: float | None = None
    orderbook_ask_depth: float | None = None
    excluded_venue_count: int = 0
    stellarroute_healthy: bool = True
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def pair_key(self) -> str:
        return f"{self.base}:{self.quote}"
