"""
Query helpers.
All database reads go through here so state classes stay clean.
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlmodel import Session, create_engine, select, func, text

from reflex_pulse.core.models import (
    ConnectionEvent,
    FrontendError,
    HandlerEvent,
    StateSnapshot,
    DeployMarker,
)

DB_URL = "sqlite:///pulse.db"
_engine = create_engine(DB_URL, connect_args={"check_same_thread": False})


def _window(minutes: int = 60) -> datetime:
    return datetime.now(timezone.utc) - timedelta(minutes=minutes)


def get_handler_latency_series(minutes: int = 60) -> list[dict]:
    """Returns p50 latency per handler over the last N minutes, bucketed by minute."""
    since = _window(minutes)
    with Session(_engine) as s:
        rows = s.exec(
            select(HandlerEvent)
            .where(HandlerEvent.ts >= since)
            .order_by(HandlerEvent.ts)
        ).all()

    if not rows:
        return []

    buckets: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        minute = row.ts.strftime("%H:%M")
        buckets[minute].append(row.duration_ms)

    return [
        {
            "minute": minute,
            "p50": round(sorted(vals)[len(vals) // 2], 2),
            "p95": round(sorted(vals)[int(len(vals) * 0.95)], 2),
            "count": len(vals),
        }
        for minute, vals in sorted(buckets.items())
    ]


def get_handler_leaderboard(minutes: int = 60) -> list[dict]:
    """Returns handlers ranked by average duration descending."""
    since = _window(minutes)
    with Session(_engine) as s:
        rows = s.exec(
            select(
                HandlerEvent.handler,
                func.avg(HandlerEvent.duration_ms).label("avg_ms"),
                func.max(HandlerEvent.duration_ms).label("max_ms"),
                func.count(HandlerEvent.id).label("calls"),
                func.sum(HandlerEvent.had_error).label("errors"),
            )
            .where(HandlerEvent.ts >= since)
            .group_by(HandlerEvent.handler)
            .order_by(text("avg_ms DESC"))
        ).all()

    return [
        {
            "handler": r.handler,
            "avg_ms": round(r.avg_ms, 2),
            "max_ms": round(r.max_ms, 2),
            "calls": r.calls,
            "errors": int(r.errors or 0),
        }
        for r in rows
    ]


def get_active_connections() -> dict:
    """Returns count of currently active WebSocket connections."""
    since = _window(minutes=5)
    with Session(_engine) as s:
        connects = s.exec(
            select(func.count(ConnectionEvent.id))
            .where(ConnectionEvent.event == "connect")
            .where(ConnectionEvent.ts >= since)
        ).one()
        disconnects = s.exec(
            select(func.count(ConnectionEvent.id))
            .where(ConnectionEvent.event == "disconnect")
            .where(ConnectionEvent.ts >= since)
        ).one()

    return {
        "active": max(0, int(connects) - int(disconnects)),
        "total_connects": int(connects),
    }


def get_connection_series(minutes: int = 60) -> list[dict]:
    since = _window(minutes)
    with Session(_engine) as s:
        rows = s.exec(
            select(ConnectionEvent)
            .where(ConnectionEvent.ts >= since)
            .order_by(ConnectionEvent.ts)
        ).all()

    buckets: dict[str, dict] = defaultdict(lambda: {"connects": 0, "disconnects": 0})
    for row in rows:
        minute = row.ts.strftime("%H:%M")
        if row.event == "connect":
            buckets[minute]["connects"] += 1
        else:
            buckets[minute]["disconnects"] += 1

    return [
        {"minute": m, **v}
        for m, v in sorted(buckets.items())
    ]


def get_state_growth(minutes: int = 60) -> list[dict]:
    """Returns total state size over time to surface memory leaks."""
    since = _window(minutes)
    with Session(_engine) as s:
        rows = s.exec(
            select(StateSnapshot)
            .where(StateSnapshot.ts >= since)
            .order_by(StateSnapshot.ts)
        ).all()

    buckets: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        minute = row.ts.strftime("%H:%M")
        buckets[minute].append(row.total_bytes)

    return [
        {"minute": m, "avg_bytes": round(sum(v) / len(v))}
        for m, v in sorted(buckets.items())
    ]


def get_var_leaderboard() -> list[dict]:
    """Returns state vars ranked by average size to identify large vars."""
    with Session(_engine) as s:
        rows = s.exec(
            select(StateSnapshot)
            .order_by(StateSnapshot.ts.desc())
            .limit(50)
        ).all()

    var_totals: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        var_sizes = json.loads(row.var_sizes_json)
        for var, size in var_sizes.items():
            var_totals[var].append(size)

    return sorted(
        [
            {
                "var": var,
                "avg_bytes": round(sum(vals) / len(vals)),
                "max_bytes": max(vals),
            }
            for var, vals in var_totals.items()
        ],
        key=lambda x: x["avg_bytes"],
        reverse=True,
    )[:20]


def get_recent_errors(limit: int = 50) -> list[dict]:
    with Session(_engine) as s:
        rows = s.exec(
            select(FrontendError)
            .order_by(FrontendError.ts.desc())
            .limit(limit)
        ).all()

    return [
        {
            "id": r.id,
            "ts": r.ts.strftime("%Y-%m-%d %H:%M:%S"),
            "page": r.page,
            "message": r.message,
            "stack": r.stack,
            "token": r.token[:8] + "...",
        }
        for r in rows
    ]


def get_error_rate_series(minutes: int = 60) -> list[dict]:
    since = _window(minutes)
    with Session(_engine) as s:
        rows = s.exec(
            select(HandlerEvent)
            .where(HandlerEvent.ts >= since)
            .order_by(HandlerEvent.ts)
        ).all()

    buckets: dict[str, dict] = defaultdict(lambda: {"total": 0, "errors": 0})
    for row in rows:
        minute = row.ts.strftime("%H:%M")
        buckets[minute]["total"] += 1
        if row.had_error:
            buckets[minute]["errors"] += 1

    return [
        {
            "minute": m,
            "error_rate": round(v["errors"] / v["total"] * 100, 1) if v["total"] else 0,
            "total": v["total"],
        }
        for m, v in sorted(buckets.items())
    ]


def get_summary_stats() -> dict:
    since = _window(60)
    with Session(_engine) as s:
        total_calls = s.exec(
            select(func.count(HandlerEvent.id)).where(HandlerEvent.ts >= since)
        ).one()
        total_errors = s.exec(
            select(func.count(HandlerEvent.id))
            .where(HandlerEvent.ts >= since)
            .where(HandlerEvent.had_error == True)
        ).one()
        avg_latency = s.exec(
            select(func.avg(HandlerEvent.duration_ms)).where(HandlerEvent.ts >= since)
        ).one()
        frontend_errors = s.exec(
            select(func.count(FrontendError.id)).where(FrontendError.ts >= since)
        ).one()

    connections = get_active_connections()

    return {
        "total_calls": int(total_calls or 0),
        "total_errors": int(total_errors or 0),
        "avg_latency_ms": round(float(avg_latency or 0), 1),
        "frontend_errors": int(frontend_errors or 0),
        "active_connections": connections["active"],
        "error_rate_pct": round(
            int(total_errors or 0) / max(int(total_calls or 1), 1) * 100, 1
        ),
    }


def get_deploy_markers(minutes: int = 60) -> list[dict]:
    since = _window(minutes)
    with Session(_engine) as s:
        rows = s.exec(
            select(DeployMarker)
            .where(DeployMarker.ts >= since)
            .order_by(DeployMarker.ts)
        ).all()
    return [
        {"minute": r.ts.strftime("%H:%M"), "version": r.version, "notes": r.notes}
        for r in rows
    ]
