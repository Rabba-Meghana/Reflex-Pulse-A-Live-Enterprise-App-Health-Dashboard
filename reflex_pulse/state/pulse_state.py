"""
Root state for Reflex Pulse.
"""

import asyncio
from typing import TypedDict

import reflex as rx

from reflex_pulse.core import queries


class HandlerRow(TypedDict):
    handler: str
    avg_ms: float
    max_ms: float
    calls: int
    errors: int


class VarRow(TypedDict):
    var: str
    avg_bytes: int
    max_bytes: int


class ErrorRow(TypedDict):
    id: str
    ts: str
    page: str
    message: str
    stack: str
    token: str


class LatencyPoint(TypedDict):
    minute: str
    p50: float
    p95: float
    count: int


class ConnectionPoint(TypedDict):
    minute: str
    connects: int
    disconnects: int


class StatePoint(TypedDict):
    minute: str
    avg_bytes: int


class ErrorRatePoint(TypedDict):
    minute: str
    error_rate: float
    total: int


class PulseState(rx.State):

    total_calls: int = 0
    total_errors: int = 0
    avg_latency_ms: float = 0.0
    frontend_errors: int = 0
    active_connections: int = 0
    error_rate_pct: float = 0.0

    latency_series: list[LatencyPoint] = []
    connection_series: list[ConnectionPoint] = []
    state_growth_series: list[StatePoint] = []
    error_rate_series: list[ErrorRatePoint] = []

    handler_leaderboard: list[HandlerRow] = []
    var_leaderboard: list[VarRow] = []

    recent_errors: list[ErrorRow] = []
    selected_error: ErrorRow = {"id": "", "ts": "", "page": "", "message": "", "stack": "", "token": ""}
    error_panel_open: bool = False

    time_window: int = 60
    is_loading: bool = False
    active_tab: str = "overview"

    def _load_data(self):
        """Synchronously load all data from SQLite."""
        stats = queries.get_summary_stats()
        self.total_calls = stats["total_calls"]
        self.total_errors = stats["total_errors"]
        self.avg_latency_ms = stats["avg_latency_ms"]
        self.frontend_errors = stats["frontend_errors"]
        self.active_connections = stats["active_connections"]
        self.error_rate_pct = stats["error_rate_pct"]

        self.latency_series = queries.get_handler_latency_series(self.time_window)
        self.connection_series = queries.get_connection_series(self.time_window)
        self.state_growth_series = queries.get_state_growth(self.time_window)
        self.error_rate_series = queries.get_error_rate_series(self.time_window)
        self.handler_leaderboard = queries.get_handler_leaderboard(self.time_window)
        self.var_leaderboard = queries.get_var_leaderboard()
        self.recent_errors = queries.get_recent_errors()

    @rx.event(background=True)
    async def start_polling(self):
        """Poll every 5 seconds using background task pattern."""
        while True:
            async with self:
                self.is_loading = True
            await asyncio.sleep(0.1)
            async with self:
                self._load_data()
                self.is_loading = False
            await asyncio.sleep(5)

    @rx.event
    def refresh_all(self):
        self.is_loading = True
        self._load_data()
        self.is_loading = False

    @rx.event
    def set_time_window(self, value: str):
        self.time_window = int(value)

    @rx.event
    def set_active_tab(self, tab: str):
        self.active_tab = tab

    @rx.event
    def open_error(self, error_id: str):
        for err in self.recent_errors:
            if err["id"] == error_id:
                self.selected_error = err
                self.error_panel_open = True
                break

    @rx.event
    def close_error_panel(self):
        self.error_panel_open = False
        self.selected_error = {"id": "", "ts": "", "page": "", "message": "", "stack": "", "token": ""}
