"""
Overview page: summary stats, key charts, handler leaderboard.
"""

import reflex as rx
from reflex_pulse.state.pulse_state import PulseState
from reflex_pulse.components.ui import (
    stat_card, section_header, card, ACCENT, RED, GREEN, AMBER, BLUE, TEXT_MUTED, TEXT_PRIMARY, BORDER
)
from reflex_pulse.components.charts import (
    latency_chart, connection_chart, error_rate_chart
)


def summary_row() -> rx.Component:
    return rx.flex(
        stat_card(
            "Active connections",
            PulseState.active_connections,
            "live WebSocket sessions",
            color=BLUE,
            icon="wifi",
        ),
        stat_card(
            "Handler calls",
            PulseState.total_calls,
            "last 60 minutes",
            color=ACCENT,
            icon="zap",
        ),
        stat_card(
            "Avg latency",
            rx.text(PulseState.avg_latency_ms, " ms"),
            "across all handlers",
            color=GREEN,
            icon="timer",
        ),
        stat_card(
            "Error rate",
            rx.text(PulseState.error_rate_pct, "%"),
            "handler exceptions",
            color=rx.cond(PulseState.error_rate_pct > 5, RED, GREEN),
            icon="alert-triangle",
        ),
        stat_card(
            "Frontend errors",
            PulseState.frontend_errors,
            "browser exceptions",
            color=rx.cond(PulseState.frontend_errors > 0, RED, GREEN),
            icon="bug",
        ),
        wrap="wrap",
        gap="1rem",
        width="100%",
    )


def handler_leaderboard_table() -> rx.Component:
    return card(
        rx.vstack(
            section_header(
                "Slowest event handlers",
                "Ranked by average duration over the last 60 minutes",
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Handler", width="45%"),
                        rx.table.column_header_cell("Avg ms", width="15%"),
                        rx.table.column_header_cell("Max ms", width="15%"),
                        rx.table.column_header_cell("Calls", width="12%"),
                        rx.table.column_header_cell("Errors", width="13%"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        PulseState.handler_leaderboard,
                        lambda row: rx.table.row(
                            rx.table.cell(
                                rx.text(
                                    row["handler"],
                                    size="2",
                                    font_family="monospace",
                                    color=TEXT_PRIMARY,
                                )
                            ),
                            rx.table.cell(
                                rx.cond(
                                    row["avg_ms"] > 500,
                                    rx.text(row["avg_ms"], size="2", color=RED, weight="bold"),
                                    rx.cond(
                                        row["avg_ms"] > 100,
                                        rx.text(row["avg_ms"], size="2", color=AMBER, weight="medium"),
                                        rx.text(row["avg_ms"], size="2", color=GREEN),
                                    ),
                                )
                            ),
                            rx.table.cell(rx.text(row["max_ms"], size="2", color=TEXT_MUTED)),
                            rx.table.cell(rx.text(row["calls"], size="2", color=TEXT_MUTED)),
                            rx.table.cell(
                                rx.cond(
                                    row["errors"] > 0,
                                    rx.text(row["errors"], size="2", color=RED, weight="bold"),
                                    rx.text("0", size="2", color=GREEN),
                                )
                            ),
                        ),
                    )
                ),
                width="100%",
                size="2",
            ),
            spacing="0",
            width="100%",
        ),
        width="100%",
    )


def overview_page() -> rx.Component:
    return rx.vstack(
        summary_row(),
        rx.grid(
            latency_chart(),
            connection_chart(),
            columns="2",
            gap="1rem",
            width="100%",
        ),
        rx.grid(
            error_rate_chart(),
            handler_leaderboard_table(),
            columns="2",
            gap="1rem",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )
