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

    def store(self, signal: RoutingSignal) -> None:
        key = self._key(signal.pair_key())
        payload = signal.model_dump_json()
        self._client.setex(key, self._ttl, payload)

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
