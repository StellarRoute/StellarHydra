# Structured logging setup for Hydra services.
from __future__ import annotations

import logging

import structlog

from stellarhydra.config import get_settings


def configure_logging() -> None:
    level = getattr(logging, get_settings().hydra_log_level.upper(), logging.INFO)
    logging.basicConfig(level=level)
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
    )
