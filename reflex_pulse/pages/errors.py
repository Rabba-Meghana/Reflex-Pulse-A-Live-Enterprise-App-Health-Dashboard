"""
Error explorer page.
Lists frontend and backend errors with full stack trace replay.
"""

import reflex as rx
from reflex_pulse.state.pulse_state import PulseState
from reflex_pulse.components.ui import (
    section_header, card, RED, GREEN, TEXT_MUTED, TEXT_PRIMARY, BORDER, SURFACE
)


def error_row(row) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(
                    row["message"],
                    size="2",
                    weight="medium",
                    color=TEXT_PRIMARY,
                ),
                rx.hstack(
                    rx.text(row["ts"], size="1", color=TEXT_MUTED),
                    rx.text(row["page"], size="1", color=TEXT_MUTED),
                    rx.text(row["token"], size="1", color=TEXT_MUTED),
                    gap="1rem",
                ),
                spacing="1",
                align="start",
                flex="1",
            ),
            rx.button(
                "View trace",
                on_click=PulseState.open_error(row["id"]),
                size="1",
                variant="outline",
                color_scheme="violet",
            ),
            width="100%",
            align="center",
            justify="between",
        ),
        padding="1rem 1.25rem",
        border_bottom=f"1px solid {BORDER}",
        _hover={"background": SURFACE},
        cursor="pointer",
    )


def stack_trace_panel() -> rx.Component:
    return rx.cond(
        PulseState.error_panel_open,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.heading("Stack trace", size="4", weight="bold", color=TEXT_PRIMARY),
                    rx.spacer(),
                    rx.icon_button(
                        rx.icon("x", size=16),
                        on_click=PulseState.close_error_panel,
                        variant="ghost",
                        size="2",
                    ),
                    width="100%",
                    align="center",
                ),
                rx.box(
                    rx.text(
                        PulseState.selected_error["message"],
                        size="2",
                        weight="medium",
                        color=RED,
                    ),
                    padding="0.75rem",
                    border_radius="8px",
                    background="#FEF2F2",
                    border="1px solid #FECACA",
                    width="100%",
                ),
                rx.scroll_area(
                    rx.code_block(
                        PulseState.selected_error["stack"],
                        language="python",
                        width="100%",
                    ),
                    max_height="400px",
                    width="100%",
                ),
                rx.hstack(
                    rx.text("Page: ", size="2", color=TEXT_MUTED),
                    rx.text(PulseState.selected_error["page"], size="2", color=TEXT_PRIMARY),
                    rx.spacer(),
                    rx.text("Session: ", size="2", color=TEXT_MUTED),
                    rx.text(PulseState.selected_error["token"], size="2", font_family="monospace"),
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            padding="1.5rem",
            border_radius="12px",
            border=f"1px solid {BORDER}",
            background="white",
            box_shadow="0 4px 24px rgba(0,0,0,0.1)",
            width="100%",
        ),
        rx.fragment(),
    )


def empty_state() -> rx.Component:
    return rx.cond(
        PulseState.recent_errors,
        rx.fragment(),
        rx.vstack(
            rx.icon("circle-check", size=40, color=GREEN),
            rx.text("No errors in the last 60 minutes", size="3", color=TEXT_MUTED),
            align="center",
            padding="3rem",
            width="100%",
        ),
    )


def errors_page() -> rx.Component:
    return rx.vstack(
        stack_trace_panel(),
        card(
            rx.vstack(
                section_header(
                    "Recent errors",
                    "Frontend browser exceptions and backend handler failures",
                ),
                empty_state(),
                rx.foreach(PulseState.recent_errors, error_row),
                spacing="0",
                width="100%",
            ),
            width="100%",
            padding="0",
            overflow="hidden",
        ),
        spacing="4",
        width="100%",
    )
