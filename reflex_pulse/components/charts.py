"""
Chart components built on rx.recharts.
Each chart reads directly from PulseState.
"""

import reflex as rx
from reflex_pulse.state.pulse_state import PulseState
from reflex_pulse.components.ui import ACCENT, RED, AMBER, GREEN, BLUE, BORDER, TEXT_MUTED, card, section_header


def latency_chart() -> rx.Component:
    return card(
        rx.vstack(
            section_header(
                "Event handler latency",
                "p50 and p95 response time per minute",
            ),
            rx.recharts.responsive_container(
                rx.recharts.line_chart(
                    rx.recharts.line(
                        data_key="p50",
                        stroke=GREEN,
                        stroke_width=2,
                        dot=False,
                        name="p50 ms",
                    ),
                    rx.recharts.line(
                        data_key="p95",
                        stroke=AMBER,
                        stroke_width=2,
                        dot=False,
                        name="p95 ms",
                    ),
                    rx.recharts.x_axis(data_key="minute", tick={"fontSize": 11}),
                    rx.recharts.y_axis(tick={"fontSize": 11}),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", stroke=BORDER),
                    rx.recharts.graphing_tooltip(),
                    rx.recharts.legend(),
                    data=PulseState.latency_series,
                ),
                width="100%",
                height=260,
            ),
            spacing="0",
            width="100%",
        ),
        width="100%",
    )


def connection_chart() -> rx.Component:
    return card(
        rx.vstack(
            section_header(
                "WebSocket connections",
                "Connects and disconnects per minute",
            ),
            rx.recharts.responsive_container(
                rx.recharts.bar_chart(
                    rx.recharts.bar(
                        data_key="connects",
                        fill=BLUE,
                        name="connects",
                        radius=[4, 4, 0, 0],
                    ),
                    rx.recharts.bar(
                        data_key="disconnects",
                        fill=AMBER,
                        name="disconnects",
                        radius=[4, 4, 0, 0],
                    ),
                    rx.recharts.x_axis(data_key="minute", tick={"fontSize": 11}),
                    rx.recharts.y_axis(tick={"fontSize": 11}),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", stroke=BORDER),
                    rx.recharts.graphing_tooltip(),
                    rx.recharts.legend(),
                    data=PulseState.connection_series,
                ),
                width="100%",
                height=260,
            ),
            spacing="0",
            width="100%",
        ),
        width="100%",
    )


def state_growth_chart() -> rx.Component:
    return card(
        rx.vstack(
            section_header(
                "State memory usage",
                "Total serialized state size per session over time",
            ),
            rx.recharts.responsive_container(
                rx.recharts.area_chart(
                    rx.recharts.area(
                        data_key="avg_bytes",
                        fill=ACCENT + "33",
                        stroke=ACCENT,
                        stroke_width=2,
                        name="avg bytes",
                    ),
                    rx.recharts.x_axis(data_key="minute", tick={"fontSize": 11}),
                    rx.recharts.y_axis(tick={"fontSize": 11}),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", stroke=BORDER),
                    rx.recharts.graphing_tooltip(),
                    data=PulseState.state_growth_series,
                ),
                width="100%",
                height=260,
            ),
            spacing="0",
            width="100%",
        ),
        width="100%",
    )


def error_rate_chart() -> rx.Component:
    return card(
        rx.vstack(
            section_header(
                "Error rate",
                "Backend handler errors as a percentage of total calls",
            ),
            rx.recharts.responsive_container(
                rx.recharts.area_chart(
                    rx.recharts.area(
                        data_key="error_rate",
                        fill=RED + "22",
                        stroke=RED,
                        stroke_width=2,
                        name="error %",
                    ),
                    rx.recharts.x_axis(data_key="minute", tick={"fontSize": 11}),
                    rx.recharts.y_axis(tick={"fontSize": 11}),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", stroke=BORDER),
                    rx.recharts.graphing_tooltip(),
                    data=PulseState.error_rate_series,
                ),
                width="100%",
                height=260,
            ),
            spacing="0",
            width="100%",
        ),
        width="100%",
    )
