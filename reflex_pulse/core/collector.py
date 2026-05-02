"""
PulseCollector patches into any Reflex app and streams telemetry
to the Pulse dashboard via Redis pub/sub.

Usage in the target app:
    from reflex_pulse.core.collector import PulseCollector
    PulseCollector.attach(app)
"""

import asyncio
import functools
import json
import time
import traceback
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4

import redis.asyncio as aioredis


REDIS_URL = "redis://localhost:6379"
CHANNEL = "reflex_pulse"


async def _publish(client: aioredis.Redis, event_type: str, payload: dict) -> None:
    payload["type"] = event_type
    payload["ts"] = datetime.now(timezone.utc).isoformat()
    payload["id"] = str(uuid4())
    await client.publish(CHANNEL, json.dumps(payload))


def _wrap_handler(handler: Callable, handler_name: str) -> Callable:
    """Wraps an async event handler to capture latency and errors."""

    @functools.wraps(handler)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        error = None
        result = None
        try:
            client = await aioredis.from_url(REDIS_URL, decode_responses=True)
            gen = handler(*args, **kwargs)
            if hasattr(gen, "__aiter__"):
                results = []
                async for item in gen:
                    results.append(item)
                result = results
            else:
                result = await gen
        except Exception as exc:
            error = {
                "message": str(exc),
                "traceback": traceback.format_exc(),
            }
            raise
        finally:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            try:
                await _publish(client, "handler_profile", {
                    "handler": handler_name,
                    "duration_ms": elapsed_ms,
                    "error": error,
                })
                await client.aclose()
            except Exception:
                pass
        return result

    return wrapper


class PulseCollector:
    """Attach to a Reflex app instance to enable live telemetry collection."""

    _redis: aioredis.Redis | None = None

    @classmethod
    async def _get_redis(cls) -> aioredis.Redis:
        if cls._redis is None:
            cls._redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
        return cls._redis

    @classmethod
    def attach(cls, app: Any) -> None:
        """
        Patches the Reflex app's state class to intercept event handlers
        and emit telemetry. Call this after app = rx.App().
        """
        import reflex as rx

        state_cls = app.state_manager.state if hasattr(app, "state_manager") else None
        if state_cls is None:
            return

        for name in dir(state_cls):
            if name.startswith("_"):
                continue
            attr = getattr(state_cls, name, None)
            if callable(attr) and asyncio.iscoroutinefunction(attr):
                wrapped = _wrap_handler(attr, f"{state_cls.__name__}.{name}")
                setattr(state_cls, name, wrapped)

    @classmethod
    async def emit_connection(cls, token: str, event: str, page: str = "") -> None:
        client = await cls._get_redis()
        await _publish(client, "ws_connection", {
            "token": token,
            "event": event,
            "page": page,
        })

    @classmethod
    async def emit_state_snapshot(
        cls,
        token: str,
        state_dict: dict,
        dirty_vars: list[str],
    ) -> None:
        client = await cls._get_redis()
        var_sizes = {k: len(json.dumps(v)) for k, v in state_dict.items()}
        await _publish(client, "state_snapshot", {
            "token": token,
            "var_sizes": var_sizes,
            "dirty_vars": dirty_vars,
            "total_bytes": sum(var_sizes.values()),
        })

    @classmethod
    async def emit_frontend_error(
        cls,
        token: str,
        message: str,
        stack: str,
        page: str,
    ) -> None:
        client = await cls._get_redis()
        await _publish(client, "frontend_error", {
            "token": token,
            "message": message,
            "stack": stack,
            "page": page,
        })
