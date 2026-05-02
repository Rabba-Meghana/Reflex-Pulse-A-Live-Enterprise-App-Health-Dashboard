"""
Reusable UI primitives for Reflex Pulse.
"""

import reflex as rx
from reflex_pulse.state.pulse_state import PulseState


ACCENT = "#7C3AED"
ACCENT_LIGHT = "#EDE9FE"
SURFACE = "#F9FAFB"
BORDER = "#E5E7EB"
TEXT_MUTED = "#6B7280"
TEXT_PRIMARY = "#111827"
RED = "#EF4444"
GREEN = "#10B981"
AMBER = "#F59E0B"
BLUE = "#3B82F6"


def stat_card(
    label: str,
    value: rx.Component,
    sub: str = "",
    color: str = ACCENT,
    icon: str = "",
) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(label, size="1", color=TEXT_MUTED, weight="medium"),
                rx.spacer(),
                rx.cond(
                    icon != "",
                    rx.icon(icon, size=16, color=color),
                    rx.fragment(),
                ),
                width="100%",
            ),
            rx.text(value, size="7", weight="bold", color=TEXT_PRIMARY),
            rx.cond(
                sub != "",
                rx.text(sub, size="1", color=TEXT_MUTED),
                rx.fragment(),
            ),
            spacing="1",
            align="start",
        ),
        padding="1.25rem",
        border_radius="12px",
        border=f"1px solid {BORDER}",
        background="white",
        box_shadow="0 1px 3px rgba(0,0,0,0.06)",
        flex="1",
        min_width="160px",
    )


def section_header(title: str, subtitle: str = "") -> rx.Component:
    return rx.vstack(
        rx.heading(title, size="4", weight="bold", color=TEXT_PRIMARY),
        rx.cond(
            subtitle != "",
            rx.text(subtitle, size="2", color=TEXT_MUTED),
            rx.fragment(),
        ),
        spacing="0",
        align="start",
        margin_bottom="1rem",
    )


def status_badge(label: str, color: str = GREEN) -> rx.Component:
    bg = color + "20"
    return rx.box(
        rx.text(label, size="1", weight="medium", color=color),
        padding="2px 10px",
        border_radius="999px",
        background=bg,
        display="inline-flex",
        align_items="center",
    )


def latency_badge(ms: float) -> rx.Component:
    return rx.cond(
        ms > 500,
        status_badge(f"{ms}ms", RED),
        rx.cond(
            ms > 100,
            status_badge(f"{ms}ms", AMBER),
            status_badge(f"{ms}ms", GREEN),
        ),
    )


def error_count_badge(count: int) -> rx.Component:
    return rx.cond(
        count > 0,
        status_badge(f"{count} errors", RED),
        status_badge("clean", GREEN),
    )


def card(content: rx.Component, **kwargs) -> rx.Component:
    return rx.box(
        content,
        padding="1.5rem",
        border_radius="12px",
        border=f"1px solid {BORDER}",
        background="white",
        box_shadow="0 1px 3px rgba(0,0,0,0.06)",
        **kwargs,
    )


def divider_line() -> rx.Component:
    return rx.divider(color=BORDER, margin_y="1rem")


def tab_button(label: str, tab_id: str) -> rx.Component:
    is_active = PulseState.active_tab == tab_id
    return rx.button(
        label,
        on_click=PulseState.set_active_tab(tab_id),
        variant="ghost",
        size="2",
        color=rx.cond(is_active, ACCENT, TEXT_MUTED),
        border_bottom=rx.cond(
            is_active,
            f"2px solid {ACCENT}",
            "2px solid transparent",
        ),
        border_radius="0",
        padding_x="1rem",
        padding_y="0.5rem",
        cursor="pointer",
    )


def loading_overlay() -> rx.Component:
    return rx.cond(
        PulseState.is_loading,
        rx.box(
            rx.spinner(size="3", color=ACCENT),
            position="fixed",
            top="1rem",
            right="1rem",
            z_index="999",
        ),
        rx.fragment(),
    )
