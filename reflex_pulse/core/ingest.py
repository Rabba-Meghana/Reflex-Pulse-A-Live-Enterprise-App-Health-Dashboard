"""
Ingestion worker.

Subscribes to the Redis pub/sub channel that PulseCollector publishes to
and persists events into SQLite via SQLModel. Runs as a background task
inside the Reflex Pulse app.
"""

import asyncio
import json
import logging

import redis.asyncio as aioredis
from sqlmodel import Session, create_engine, SQLModel

from reflex_pulse.core.models import (
    ConnectionEvent,
    DeployMarker,
    FrontendError,
    HandlerEvent,
    StateSnapshot,
)

logger = logging.getLogger("pulse.ingest")

REDIS_URL = "redis://localhost:6379"
CHANNEL = "reflex_pulse"
DB_URL = "sqlite:///pulse.db"

_engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SQLModel.metadata.create_all(_engine)


def _handle_handler_profile(data: dict) -> None:
    error = data.get("error") or {}
    row = HandlerEvent(
        ts=data.get("ts"),
        handler=data.get("handler", ""),
        duration_ms=float(data.get("duration_ms", 0)),
        had_error=error is not None and bool(error),
        error_message=error.get("message") if error else None,
        error_traceback=error.get("traceback") if error else None,
    )
    with Session(_engine) as s:
        s.add(row)
        s.commit()


def _handle_ws_connection(data: dict) -> None:
    row = ConnectionEvent(
        ts=data.get("ts"),
        token=data.get("token", ""),
        event=data.get("event", ""),
        page=data.get("page", ""),
    )
    with Session(_engine) as s:
        s.add(row)
        s.commit()


def _handle_state_snapshot(data: dict) -> None:
    row = StateSnapshot(
        ts=data.get("ts"),
        token=data.get("token", ""),
        total_bytes=int(data.get("total_bytes", 0)),
        var_sizes_json=json.dumps(data.get("var_sizes", {})),
        dirty_vars_json=json.dumps(data.get("dirty_vars", [])),
    )
    with Session(_engine) as s:
        s.add(row)
        s.commit()


def _handle_frontend_error(data: dict) -> None:
    row = FrontendError(
        ts=data.get("ts"),
        token=data.get("token", ""),
        page=data.get("page", ""),
        message=data.get("message", ""),
        stack=data.get("stack", ""),
    )
    with Session(_engine) as s:
        s.add(row)
        s.commit()


HANDLERS = {
    "handler_profile": _handle_handler_profile,
    "ws_connection": _handle_ws_connection,
    "state_snapshot": _handle_state_snapshot,
    "frontend_error": _handle_frontend_error,
}


async def run_ingestion_worker() -> None:
    """Continuously reads from Redis and persists to SQLite."""
    logger.info("Pulse ingestion worker starting")
    client = aioredis.from_url(REDIS_URL, decode_responses=True)
    pubsub = client.pubsub()
    await pubsub.subscribe(CHANNEL)

    async for message in pubsub.listen():
        if message["type"] != "message":
            continue
        try:
            data = json.loads(message["data"])
            event_type = data.get("type")
            handler = HANDLERS.get(event_type)
            if handler:
                handler(data)
            else:
                logger.debug("Unknown event type: %s", event_type)
        except Exception as exc:
            logger.warning("Ingestion error: %s", exc)
