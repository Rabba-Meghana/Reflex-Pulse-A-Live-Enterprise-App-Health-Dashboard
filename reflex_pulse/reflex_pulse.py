"""
Reflex Pulse app entry point.
Defines the layout, sidebar, and page routing.
"""

import asyncio
import reflex as rx

from reflex_pulse.state.pulse_state import PulseState
from reflex_pulse.pages.overview import overview_page
from reflex_pulse.pages.state_inspector import state_inspector_page
from reflex_pulse.pages.errors import errors_page
from reflex_pulse.components.ui import (
    loading_overlay, ACCENT, BORDER, TEXT_MUTED, TEXT_PRIMARY, SURFACE
)
from reflex_pulse.core.ingest import run_ingestion_worker


NAV_ITEMS = [
    ("overview", "layout-dashboard", "Overview"),
    ("state", "cpu", "State inspector"),
    ("errors", "bug", "Error explorer"),
]


def nav_item(tab_id: str, icon_name: str, label: str) -> rx.Component:
    is_active = PulseState.active_tab == tab_id
    return rx.button(
        rx.hstack(
            rx.icon(icon_name, size=16),
            rx.text(label, size="2", weight="medium"),
            gap="0.6rem",
            align="center",
        ),
        on_click=PulseState.set_active_tab(tab_id),
        variant="ghost",
        width="100%",
        justify="start",
        padding="0.6rem 1rem",
        border_radius="8px",
        background=rx.cond(is_active, ACCENT + "15", "transparent"),
        color=rx.cond(is_active, ACCENT, TEXT_MUTED),
        _hover={"background": ACCENT + "10", "color": ACCENT},
        cursor="pointer",
    )


def sidebar() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon("activity", size=18, color="white"),
                    padding="6px",
                    border_radius="8px",
                    background=ACCENT,
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
                rx.vstack(
                    rx.text(
                        "Reflex Pulse",
                        size="3",
                        weight="bold",
                        color=TEXT_PRIMARY,
                    ),
                    rx.text(
                        "Live observability",
                        size="1",
                        color=TEXT_MUTED,
                    ),
                    spacing="0",
                    align="start",
                ),
                gap="0.6rem",
                align="center",
                padding="1.5rem 1rem 1rem",
                width="100%",
            ),
            rx.divider(color=BORDER),
            rx.vstack(
                *[nav_item(t, i, l) for t, i, l in NAV_ITEMS],
                padding="0.5rem",
                width="100%",
                spacing="1",
            ),
            rx.spacer(),
            rx.box(
                rx.hstack(
                    rx.icon("refresh-cw", size=12, color=TEXT_MUTED),
                    rx.text("Auto-refresh: 5s", size="1", color=TEXT_MUTED),
                    gap="0.4rem",
                    align="center",
                ),
                padding="1rem",
            ),
            height="100%",
            width="100%",
        ),
        width="220px",
        min_height="100vh",
        border_right=f"1px solid {BORDER}",
        background="white",
        position="fixed",
        top="0",
        left="0",
        z_index="100",
    )


def page_content() -> rx.Component:
    return rx.cond(
        PulseState.active_tab == "overview",
        overview_page(),
        rx.cond(
            PulseState.active_tab == "state",
            state_inspector_page(),
            errors_page(),
        ),
    )


def layout() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.box(
            loading_overlay(),
            rx.vstack(
                rx.hstack(
                    rx.heading(
                        rx.match(
                            PulseState.active_tab,
                            ("overview", "Overview"),
                            ("state", "State inspector"),
                            ("errors", "Error explorer"),
                            "Dashboard",
                        ),
                        size="5",
                        weight="bold",
                        color=TEXT_PRIMARY,
                    ),
                    rx.spacer(),
                    rx.select(
                        ["15", "30", "60", "120"],
                        default_value="60",
                        on_change=PulseState.set_time_window,
                        size="2",
                    ),
                    rx.text("min window", size="2", color=TEXT_MUTED),
                    rx.button(
                        rx.icon("refresh-cw", size=14),
                        on_click=PulseState.refresh_all,
                        variant="outline",
                        size="2",
                        color_scheme="violet",
                    ),
                    width="100%",
                    align="center",
                    padding_bottom="1.5rem",
                    border_bottom=f"1px solid {BORDER}",
                    margin_bottom="1.5rem",
                ),
                page_content(),
                padding="2rem",
                width="100%",
            ),
            margin_left="220px",
            min_height="100vh",
            background=SURFACE,
        ),
        on_mount=PulseState.start_polling,
    )


app = rx.App(
    theme=rx.theme(appearance="light", accent_color="violet"),
)

app.add_page(layout, route="/", title="Reflex Pulse")
