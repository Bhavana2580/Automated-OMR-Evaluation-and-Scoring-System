"""
backend/main.py

Launcher for the FastAPI backend.

Usage examples (from project root):
  python -m backend.main
  python -m backend.main --host 0.0.0.0 --port 8000 --reload
  python -m backend.main --host 0.0.0.0 --port 8080 --log-level debug
"""

import argparse
import logging
import uvicorn
import os
import sys

# Ensure the backend package is importable when run as module
# (When you run python -m backend.main Python's import path already includes project root.)
try:
    # import the FastAPI app instance from backend/app.py
    from app import app  # relative import internal to backend package
except Exception as e:
    # Helpful error if import fails
    print("Failed to import FastAPI app from backend/app.py:", file=sys.stderr)
    raise

def build_arg_parser():
    p = argparse.ArgumentParser(description="Run the OMR evaluation FastAPI backend (uvicorn).")
    p.add_argument("--host", type=str, default=os.getenv("OMR_HOST", "127.0.0.1"),
                   help="Host to bind to (default: 127.0.0.1)")
    p.add_argument("--port", type=int, default=int(os.getenv("OMR_PORT", "8000")),
                   help="Port to listen on (default: 8000)")
    p.add_argument("--reload", action="store_true",
                   help="Enable uvicorn autoreload (development only)")
    p.add_argument("--log-level", type=str, default=os.getenv("OMR_LOG_LEVEL", "info"),
                   choices=["critical", "error", "warning", "info", "debug", "trace"],
                   help="Log level for uvicorn")
    p.add_argument("--workers", type=int, default=int(os.getenv("OMR_WORKERS", "1")),
                   help="Number of worker processes (only effective with --reload False)")
    return p

def configure_logging(level: str):
    lvl = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=lvl,
        format="%(asctime)s | %(levelname)7s | %(name)s | %(message)s",
    )
    # Lower verbosity for uvicorn.access if you prefer
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING if lvl > logging.INFO else lvl)

def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    configure_logging(args.log_level)

    # Logging some startup info
    logging.info("Starting OMR Evaluation Backend")
    logging.info("Host: %s  Port: %s  Reload: %s  Workers: %s  LogLevel: %s",
                 args.host, args.port, args.reload, args.workers, args.log_level)

    # uvicorn.run accepts either an ASGI app object or an import string.
    # Using the app object directly keeps it simple.
    # Note: 'workers' is ignored when reload=True.
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,
    )

if __name__ == "__main__":
    main()