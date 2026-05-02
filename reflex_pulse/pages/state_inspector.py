"""
State inspector page.
Shows which rx.State vars are growing and flags potential memory leaks.
"""

import reflex as rx
from reflex_pulse.state.pulse_state import PulseState
from reflex_pulse.components.ui import (
    section_header, card, ACCENT, RED, GREEN, AMBER, TEXT_MUTED, TEXT_PRIMARY, BORDER
)
from reflex_pulse.components.charts import state_growth_chart


def var_bar_row(row) -> rx.Component:
    return rx.hstack(
        rx.text(
            row["var"],
            size="2",
            font_family="monospace",
            color=TEXT_PRIMARY,
            width="40%",
        ),
        rx.box(
            rx.box(
                height="10px",
                border_radius="4px",
                background=rx.cond(
                    row["avg_bytes"] > 50000,
                    RED,
                    rx.cond(row["avg_bytes"] > 10000, AMBER, ACCENT),
                ),
                width=rx.cond(
                    row["avg_bytes"] > 100000,
                    "100%",
                    rx.cond(row["avg_bytes"] > 10000, "60%", "25%"),
                ),
            ),
            flex="1",
            background=BORDER,
            border_radius="4px",
            height="10px",
        ),
        rx.text(
            row["avg_bytes"],
            " B",
            size="1",
            color=TEXT_MUTED,
            width="80px",
            text_align="right",
        ),
        width="100%",
        align="center",
        gap="0.75rem",
        margin_bottom="0.6rem",
    )


def var_size_bars() -> rx.Component:
    return card(
        rx.vstack(
            section_header(
                "State var sizes",
                "Average serialized size per var across recent sessions",
            ),
            rx.foreach(PulseState.var_leaderboard, var_bar_row),
            spacing="0",
            width="100%",
        ),
        width="100%",
    )


def leak_warning_banner() -> rx.Component:
    return rx.cond(
        PulseState.avg_latency_ms > 0,
        rx.box(
            rx.hstack(
                rx.icon("triangle-alert", size=16, color=AMBER),
                rx.vstack(
                    rx.text(
                        "Memory leak detection is active",
                        size="2",
                        weight="medium",
                        color="#92400E",
                    ),
                    rx.text(
                        "State vars growing consistently across sessions are flagged red.",
                        size="1",
                        color="#B45309",
                    ),
                    spacing="0",
                    align="start",
                ),
                gap="0.75rem",
                align="start",
            ),
            padding="1rem 1.25rem",
            border_radius="10px",
            background="#FFFBEB",
            border="1px solid #FDE68A",
            width="100%",
        ),
        rx.fragment(),
    )


def state_inspector_page() -> rx.Component:
    return rx.vstack(
        leak_warning_banner(),
        rx.grid(
            state_growth_chart(),
            var_size_bars(),
            columns="2",
            gap="1rem",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )
