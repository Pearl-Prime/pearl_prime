#!/usr/bin/env python3
"""
Phoenix Omega — Server entry point.

Usage:
    python scripts/run_server.py
    python scripts/run_server.py --port 9000 --reload
    PHOENIX_API_KEY=secret python scripts/run_server.py

Authority: docs/SERVER_INFRASTRUCTURE_SPEC.md
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Ensure repo root is on sys.path
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))


def main():
    parser = argparse.ArgumentParser(description="Phoenix Omega API Server")
    parser.add_argument("--host", default=None, help="Bind host (default: from config)")
    parser.add_argument("--port", type=int, default=None, help="Bind port (default: from config)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--workers", type=int, default=None, help="Number of worker processes")
    parser.add_argument("--log-level", default=None, help="Log level (debug/info/warning/error)")
    args = parser.parse_args()

    # Load config first to get defaults
    from server.config import ServerConfig
    cfg = ServerConfig.load()

    host = args.host or cfg.host
    port = args.port or cfg.port
    workers = args.workers or cfg.workers
    log_level = args.log_level or cfg.log_level

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    try:
        import uvicorn
    except ImportError:
        print("ERROR: uvicorn not installed. Run: pip install -r requirements-server.txt", file=sys.stderr)
        sys.exit(1)

    uvicorn.run(
        "server.app:create_app",
        factory=True,
        host=host,
        port=port,
        workers=workers if not args.reload else 1,
        reload=args.reload,
        log_level=log_level,
    )


if __name__ == "__main__":
    main()
