# HTTP client for StellarRoute REST API (quotes, routes, orderbooks, health).
from __future__ import annotations

import logging
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from stellarhydra.config import Settings, get_settings
from stellarhydra.models.signals import PathStep, RoutingSignal

logger = logging.getLogger(__name__)


class StellarRouteError(Exception):
    """Raised when StellarRoute API returns an error or is unreachable."""


class StellarRouteClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._base = self._settings.stellarroute_api_url.rstrip("/")
        self._timeout = self._settings.stellarroute_timeout_seconds

    def _client(self) -> httpx.Client:
        return httpx.Client(base_url=self._base, timeout=self._timeout)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    def health_check(self) -> dict[str, Any]:
        with self._client() as client:
            response = client.get("/health")
            response.raise_for_status()
            return response.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    def fetch_signal(
        self,
        base: str,
        quote: str,
        amount: str = "100",
        slippage_bps: int = 50,
    ) -> RoutingSignal:
        with self._client() as client:
            quote_resp = client.get(
                f"/api/v1/quote/{base}/{quote}",
                params={"amount": amount, "slippage_bps": slippage_bps},
            )
            routes_resp = client.get(
                f"/api/v1/routes/{base}/{quote}",
                params={"amount": amount, "slippage_bps": slippage_bps},
            )
            orderbook_resp = client.get(f"/api/v1/orderbook/{base}/{quote}")

            if quote_resp.status_code >= 500:
                raise StellarRouteError(f"quote API error: {quote_resp.status_code}")

            quote_data = _unwrap_envelope(quote_resp.json()) if quote_resp.is_success else {}
            routes_data = _unwrap_envelope(routes_resp.json()) if routes_resp.is_success else {}
            orderbook_data = (
                _unwrap_envelope(orderbook_resp.json()) if orderbook_resp.is_success else {}
            )

            path = _parse_path(quote_data.get("path") or [])
            route_count = len(routes_data.get("routes") or routes_data.get("paths") or [])
            excluded = len(quote_data.get("excluded_venues") or [])

            return RoutingSignal(
                base=base,
                quote=quote,
                amount=amount,
                slippage_bps=slippage_bps,
                price=_to_float(quote_data.get("price")),
                total=_to_float(quote_data.get("total")),
                price_impact_bps=_to_int(quote_data.get("price_impact_bps")),
                path=path,
                route_count=route_count,
                orderbook_bid_depth=_sum_levels(orderbook_data.get("bids")),
                orderbook_ask_depth=_sum_levels(orderbook_data.get("asks")),
                excluded_venue_count=excluded,
                stellarroute_healthy=quote_resp.is_success,
            )

    def fetch_watchlist_signals(self) -> list[RoutingSignal]:
        signals: list[RoutingSignal] = []
        yaml_cfg = self._settings.yaml_config()
        quote_amount = str(yaml_cfg.get("stellarroute", {}).get("quote_amount", "100"))
        slippage = int(yaml_cfg.get("stellarroute", {}).get("default_slippage_bps", 50))

        pairs = self._settings.watchlist_pairs()
        if not pairs:
            pairs = [("native", "USDC")]

        for base, quote in pairs:
            try:
                signals.append(
                    self.fetch_signal(base, quote, amount=quote_amount, slippage_bps=slippage)
                )
            except (httpx.HTTPError, StellarRouteError) as exc:
                logger.warning("Failed to fetch signal for %s/%s: %s", base, quote, exc)
                signals.append(
                    RoutingSignal(
                        base=base,
                        quote=quote,
                        amount=quote_amount,
                        slippage_bps=slippage,
                        stellarroute_healthy=False,
                    )
                )
        return signals


def _unwrap_envelope(payload: dict[str, Any]) -> dict[str, Any]:
    if "data" in payload and isinstance(payload["data"], dict):
        return payload["data"]
    return payload


def _parse_path(raw_path: list[Any]) -> list[PathStep]:
    steps: list[PathStep] = []
    for item in raw_path:
        if isinstance(item, dict):
            steps.append(
                PathStep(
                    venue_type=item.get("venue_type") or item.get("venue") or "unknown",
                    selling_asset=str(item.get("selling_asset") or item.get("sell") or ""),
                    buying_asset=str(item.get("buying_asset") or item.get("buy") or ""),
                    price=_to_float(item.get("price")),
                )
            )
    return steps


def _sum_levels(levels: list[Any] | None) -> float | None:
    if not levels:
        return None
    total = 0.0
    for level in levels:
        if isinstance(level, dict):
            total += float(level.get("amount") or level.get("size") or 0)
        elif isinstance(level, (list, tuple)) and len(level) >= 2:
            total += float(level[1])
    return total


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
