"""
SQLModel schemas for Reflex Pulse.
Alembic manages migrations. All tables are append-only for audit integrity.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlmodel import Field, SQLModel


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uid() -> str:
    return str(uuid4())


class HandlerEvent(SQLModel, table=True):
    """One row per event handler invocation."""

    __tablename__ = "handler_events"

    id: str = Field(default_factory=_uid, primary_key=True)
    ts: datetime = Field(default_factory=_now, index=True)
    handler: str = Field(index=True)
    duration_ms: float
    had_error: bool = False
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None


class ConnectionEvent(SQLModel, table=True):
    """WebSocket connect / disconnect events."""

    __tablename__ = "connection_events"

    id: str = Field(default_factory=_uid, primary_key=True)
    ts: datetime = Field(default_factory=_now, index=True)
    token: str = Field(index=True)
    event: str
    page: str = ""


class StateSnapshot(SQLModel, table=True):
    """State size snapshots for memory leak detection."""

    __tablename__ = "state_snapshots"

    id: str = Field(default_factory=_uid, primary_key=True)
    ts: datetime = Field(default_factory=_now, index=True)
    token: str = Field(index=True)
    total_bytes: int
    var_sizes_json: str
    dirty_vars_json: str


class FrontendError(SQLModel, table=True):
    """Errors reported from the browser."""

    __tablename__ = "frontend_errors"

    id: str = Field(default_factory=_uid, primary_key=True)
    ts: datetime = Field(default_factory=_now, index=True)
    token: str = Field(index=True)
    page: str = ""
    message: str
    stack: str = ""


class DeployMarker(SQLModel, table=True):
    """Records when a new version was deployed, used to annotate charts."""

    __tablename__ = "deploy_markers"

    id: str = Field(default_factory=_uid, primary_key=True)
    ts: datetime = Field(default_factory=_now, index=True)
    version: str
    config_hash: str
    notes: str = ""
