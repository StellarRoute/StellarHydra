# Redis-backed signal cache with TTL following hydra: key naming conventions.
from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

import redis

from stellarhydra.config import Settings, get_settings
from stellarhydra.models.signals import RoutingSignal

if TYPE_CHECKING:
    from redis import Redis

logger = logging.getLogger(__name__)


class SignalCache:
    def __init__(self, settings: Settings | None = None, client: Redis | None = None) -> None:
        self._settings = settings or get_settings()
        self._prefix = self._settings.hydra_redis_key_prefix
        self._ttl = self._settings.hydra_signal_ttl_seconds
        self._client = client or redis.from_url(self._settings.redis_url, decode_responses=True)

    def _key(self, pair: str) -> str:
        return f"{self._prefix}signals:{pair}"

    def _history_key(self, pair: str) -> str:
        return f"{self._prefix}signals:history:{pair}"

    def store(self, signal: RoutingSignal) -> None:
        key = self._key(signal.pair_key())
        payload = signal.model_dump_json()
        self._client.setex(key, self._ttl, payload)
        history_key = self._history_key(signal.pair_key())
        self._client.lpush(history_key, payload)
        self._client.ltrim(history_key, 0, 9)
        self._client.expire(history_key, self._ttl * 4)

    def get_history(self, pair: str, limit: int = 5) -> list[RoutingSignal]:
        raw_items = self._client.lrange(self._history_key(pair), 0, max(0, limit - 1))
        signals: list[RoutingSignal] = []
        for raw in raw_items:
            try:
                signals.append(RoutingSignal.model_validate(json.loads(raw)))
            except (json.JSONDecodeError, ValueError):
                continue
        return signals

    def get(self, pair: str) -> RoutingSignal | None:
        raw = self._client.get(self._key(pair))
        if not raw:
            return None
        return RoutingSignal.model_validate(json.loads(raw))

    def ping(self) -> bool:
        try:
            return bool(self._client.ping())
        except redis.RedisError as exc:
            logger.warning("Redis ping failed: %s", exc)
            return False

    def store_cycle(self, cycle_id: str, payload: str, ttl_seconds: int | None = None) -> None:
        key = f"{self._prefix}cycle:{cycle_id}"
        self._client.setex(key, ttl_seconds or self._ttl * 2, payload)

    def get_cycle(self, cycle_id: str) -> str | None:
        return self._client.get(f"{self._prefix}cycle:{cycle_id}")

    def store_watchlist(self, pairs: list[str], ttl_seconds: int = 3600) -> None:
        key = f"{self._prefix}watchlist:pairs"
        self._client.setex(key, ttl_seconds, json.dumps(pairs))

    def get_watchlist(self) -> list[str] | None:
        raw = self._client.get(f"{self._prefix}watchlist:pairs")
        if not raw:
            return None
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [str(p) for p in parsed]
        except json.JSONDecodeError:
            return None
        return None
