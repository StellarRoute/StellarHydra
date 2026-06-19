# Application settings loaded from environment and optional YAML config.
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    stellarroute_api_url: str = Field(default="http://localhost:8080", alias="STELLARROUTE_API_URL")
    stellarroute_timeout_seconds: float = Field(default=15.0, alias="STELLARROUTE_TIMEOUT_SECONDS")

    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    hydra_redis_key_prefix: str = Field(default="hydra:", alias="HYDRA_REDIS_KEY_PREFIX")
    hydra_signal_ttl_seconds: int = Field(default=300, alias="HYDRA_SIGNAL_TTL_SECONDS")

    drips_api_url: str = Field(default="https://api.drips.network", alias="DRIPS_API_URL")
    drips_api_key: str = Field(default="", alias="DRIPS_API_KEY")
    drips_dry_run: bool = Field(default=True, alias="DRIPS_DRY_RUN")

    hydra_max_drip_xlm_per_hour: float = Field(default=1000.0, alias="HYDRA_MAX_DRIP_XLM_PER_HOUR")
    hydra_slippage_alert_bps: int = Field(default=100, alias="HYDRA_SLIPPAGE_ALERT_BPS")
    hydra_prediction_horizon_minutes: int = Field(
        default=30, alias="HYDRA_PREDICTION_HORIZON_MINUTES"
    )
    hydra_watchlist: str = Field(default="native:USDC", alias="HYDRA_WATCHLIST")
    hydra_checkpoint_thread_prefix: str = Field(
        default="cycle-", alias="HYDRA_CHECKPOINT_THREAD_PREFIX"
    )

    hydra_api_host: str = Field(default="0.0.0.0", alias="HYDRA_API_HOST")
    hydra_api_port: int = Field(default=8090, alias="HYDRA_API_PORT")
    hydra_admin_api_key: str = Field(default="change-me-in-production", alias="HYDRA_ADMIN_API_KEY")

    hydra_log_level: str = Field(default="INFO", alias="HYDRA_LOG_LEVEL")
    hydra_enable_otel: bool = Field(default=False, alias="HYDRA_ENABLE_OTEL")
    otel_exporter_otlp_endpoint: str = Field(default="", alias="OTEL_EXPORTER_OTLP_ENDPOINT")

    celery_broker_url: str = Field(default="redis://localhost:6379/1", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2", alias="CELERY_RESULT_BACKEND"
    )

    hydra_kill_switch_fail_closed: bool = Field(
        default=False, alias="HYDRA_KILL_SWITCH_FAIL_CLOSED"
    )

    config_path: Path = Field(default=Path("config/settings.yaml"))

    def watchlist_pairs(self) -> list[tuple[str, str]]:
        """Merge env HYDRA_WATCHLIST with optional YAML watchlist.pairs."""
        seen: set[tuple[str, str]] = set()
        pairs: list[tuple[str, str]] = []

        def _add(base: str, quote: str) -> None:
            key = (base.strip(), quote.strip())
            if key not in seen and key[0] and key[1]:
                seen.add(key)
                pairs.append(key)

        try:
            from stellarhydra.integrations.signal_cache import SignalCache

            cached = SignalCache(self).get_watchlist()
            if cached:
                for item in cached:
                    if ":" in item:
                        base, quote = item.split(":", 1)
                        _add(base, quote)
                if pairs:
                    return pairs
        except Exception:
            pass

        for item in self.hydra_watchlist.split(","):
            item = item.strip()
            if not item or ":" not in item:
                continue
            base, quote = item.split(":", 1)
            _add(base, quote)

        yaml_cfg = self.yaml_config()
        for entry in yaml_cfg.get("watchlist", {}).get("pairs") or []:
            if isinstance(entry, dict):
                _add(str(entry.get("base", "")), str(entry.get("quote", "")))

        return pairs

    def allowed_assets(self) -> set[str]:
        yaml_cfg = self.yaml_config()
        assets = yaml_cfg.get("policy", {}).get("allowed_assets") or []
        return {str(a).strip() for a in assets if str(a).strip()}

    def yaml_config(self) -> dict[str, Any]:
        if not self.config_path.exists():
            return {}
        with self.config_path.open(encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}


@lru_cache
def get_settings() -> Settings:
    return Settings()
