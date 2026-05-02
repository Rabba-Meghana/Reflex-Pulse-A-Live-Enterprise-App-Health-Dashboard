"""
Root state for Reflex Pulse.
Uses rx.State with background polling to keep all metrics live.
"""

import asyncio
from typing import Any

import reflex as rx

from reflex_pulse.core import queries


class PulseState(rx.State):

    # summary cards
    total_calls: int = 0
    total_errors: int = 0
    avg_latency_ms: float = 0.0
    frontend_errors: int = 0
    active_connections: int = 0
    error_rate_pct: float = 0.0

    # time series charts
    latency_series: list[dict] = []
    connection_series: list[dict] = []
    state_growth_series: list[dict] = []
    error_rate_series: list[dict] = []

    # leaderboard tables
    handler_leaderboard: list[dict] = []
    var_leaderboard: list[dict] = []

    # error explorer
    recent_errors: list[dict] = []
    selected_error: dict = {}
    error_panel_open: bool = False

    # ui controls
    time_window: int = 60
    is_loading: bool = False
    active_tab: str = "overview"

    @rx.event(background=True)
    async def start_polling(self):
        """Polls all metrics every 5 seconds."""
        while True:
            async with self:
                await self.refresh_all()
            await asyncio.sleep(5)

    @rx.event
    async def refresh_all(self):
        self.is_loading = True
        yield

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
        self.selected_error = {}
