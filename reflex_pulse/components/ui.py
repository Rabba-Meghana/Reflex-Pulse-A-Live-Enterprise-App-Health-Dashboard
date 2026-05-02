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
    value,
    sub: str = "",
    color: str = ACCENT,
    icon: str = "",
) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(label, size="1", color=TEXT_MUTED, weight="medium"),
                rx.spacer(),
                rx.icon(icon, size=16) if icon else rx.fragment(),
                width="100%",
            ),
            rx.text(value, size="7", weight="bold", color=TEXT_PRIMARY),
            rx.text(sub, size="1", color=TEXT_MUTED) if sub else rx.fragment(),
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
        rx.text(subtitle, size="2", color=TEXT_MUTED) if subtitle else rx.fragment(),
        spacing="0",
        align="start",
        margin_bottom="1rem",
    )


def card(content: rx.Component, **kwargs) -> rx.Component:
    # Only set padding if caller did not pass one
    base = {
        "border_radius": "12px",
        "border": f"1px solid {BORDER}",
        "background": "white",
        "box_shadow": "0 1px 3px rgba(0,0,0,0.06)",
    }
    if "padding" not in kwargs:
        base["padding"] = "1.5rem"
    base.update(kwargs)
    return rx.box(content, **base)


def loading_overlay() -> rx.Component:
    return rx.cond(
        PulseState.is_loading,
        rx.box(
            rx.spinner(size="3"),
            position="fixed",
            top="1rem",
            right="1rem",
            z_index="999",
        ),
        rx.fragment(),
    )
