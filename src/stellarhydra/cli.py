# CLI entry point for running a single Hydra cycle from the command line.
from __future__ import annotations

import argparse
import logging

from stellarhydra.config import get_settings
from stellarhydra.graph.hydra_graph import run_cycle


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one StellarHydra liquidity cycle")
    parser.add_argument("--thread-id", default=None, help="LangGraph checkpoint thread id")
    args = parser.parse_args()

    logging.basicConfig(level=get_settings().hydra_log_level)
    result = run_cycle(thread_id=args.thread_id)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
