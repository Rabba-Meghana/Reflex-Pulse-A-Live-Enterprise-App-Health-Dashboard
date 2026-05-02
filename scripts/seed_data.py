"""
Seed script. Populates the SQLite database with realistic data
so the dashboard looks live in screenshots without needing a running app.

    python scripts/seed_data.py
"""

import json
import random
import sys
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlmodel import Session, create_engine, SQLModel
from reflex_pulse.core.models import (
    HandlerEvent,
    ConnectionEvent,
    StateSnapshot,
    FrontendError,
    DeployMarker,
)

DB_URL = "sqlite:///pulse.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SQLModel.metadata.create_all(engine)

HANDLERS = [
    "DemoState.slow_search",
    "DemoState.increment",
    "DemoState.add_items",
    "DemoState.buggy_handler",
    "AppState.load_dashboard",
    "AppState.fetch_user",
    "ReportState.generate_pdf",
]

PAGES = ["/", "/dashboard", "/reports", "/settings", "/users"]
TOKENS = [str(uuid4())[:8] for _ in range(20)]


def random_ts(minutes_ago_max: int = 90) -> datetime:
    offset = random.uniform(0, minutes_ago_max * 60)
    return datetime.now(timezone.utc) - timedelta(seconds=offset)


def seed(n_handler: int = 800, n_connections: int = 200, n_snapshots: int = 300, n_errors: int = 25):
    with Session(engine) as s:

        # handler events
        for _ in range(n_handler):
            handler = random.choice(HANDLERS)
            base_ms = {
                "DemoState.slow_search": random.uniform(80, 900),
                "DemoState.increment": random.uniform(1, 15),
                "DemoState.add_items": random.uniform(5, 40),
                "DemoState.buggy_handler": random.uniform(10, 200),
                "AppState.load_dashboard": random.uniform(120, 600),
                "AppState.fetch_user": random.uniform(20, 80),
                "ReportState.generate_pdf": random.uniform(400, 2000),
            }.get(handler, random.uniform(10, 300))

            had_error = random.random() < 0.06
            s.add(HandlerEvent(
                ts=random_ts(),
                handler=handler,
                duration_ms=round(base_ms + random.gauss(0, base_ms * 0.1), 2),
                had_error=had_error,
                error_message="ValueError: Simulated database timeout" if had_error else None,
                error_traceback=(
                    'Traceback (most recent call last):\n'
                    '  File "/app/sample_app/sample_app.py", line 52, in buggy_handler\n'
                    '    raise ValueError("Simulated database timeout")\n'
                    'ValueError: Simulated database timeout'
                ) if had_error else None,
            ))

        # connection events
        for token in TOKENS:
            s.add(ConnectionEvent(
                ts=random_ts(4),
                token=token,
                event="connect",
                page=random.choice(PAGES),
            ))
            if random.random() < 0.4:
                s.add(ConnectionEvent(
                    ts=random_ts(10),
                    token=token,
                    event="disconnect",
                    page=random.choice(PAGES),
                ))

        # state snapshots
        base_sizes = {
            "count": 4,
            "query": random.randint(10, 80),
            "results": random.randint(500, 8000),
            "items": random.randint(1000, 50000),
            "heavy_list": random.randint(5000, 100000),
        }
        for i in range(n_snapshots):
            growth_factor = 1 + (i / n_snapshots) * 0.8
            var_sizes = {
                k: int(v * growth_factor * random.uniform(0.9, 1.1))
                for k, v in base_sizes.items()
            }
            s.add(StateSnapshot(
                ts=random_ts(),
                token=random.choice(TOKENS),
                total_bytes=sum(var_sizes.values()),
                var_sizes_json=json.dumps(var_sizes),
                dirty_vars_json=json.dumps(random.sample(list(var_sizes.keys()), k=random.randint(1, 3))),
            ))

        # frontend errors
        frontend_error_msgs = [
            ("TypeError: Cannot read property 'map' of undefined", "/dashboard"),
            ("ChunkLoadError: Loading chunk 4 failed", "/reports"),
            ("Uncaught RangeError: Maximum call stack size exceeded", "/"),
            ("NetworkError: Failed to fetch /api/data", "/users"),
        ]
        for _ in range(n_errors):
            msg, page = random.choice(frontend_error_msgs)
            s.add(FrontendError(
                ts=random_ts(),
                token=random.choice(TOKENS),
                page=page,
                message=msg,
                stack=(
                    "at Array.map (<anonymous>)\n"
                    "at DataTable.render (DataTable.jsx:42)\n"
                    "at renderWithHooks (react-dom.development.js:14985)\n"
                    "at updateFunctionComponent (react-dom.development.js:17356)"
                ),
            ))

        # deploy marker
        s.add(DeployMarker(
            ts=random_ts(45),
            version="v1.2.4",
            config_hash="abc123",
            notes="Deployed report generator performance fix",
        ))

        s.commit()

    print(f"Seeded: {n_handler} handler events, {n_connections} connections, "
          f"{n_snapshots} snapshots, {n_errors} errors")


if __name__ == "__main__":
    seed()
    print("Database ready at pulse.db")
