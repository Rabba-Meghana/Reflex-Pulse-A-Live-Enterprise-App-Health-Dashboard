"""
Sample Reflex app that wires up PulseCollector.

This is the monitored app. Run it alongside Reflex Pulse to see live data.

    cd sample_app
    reflex run --port 3001 --backend-port 8001
"""

import asyncio
import random

import reflex as rx

from reflex_pulse.core.collector import PulseCollector


class DemoState(rx.State):

    count: int = 0
    items: list[str] = []
    query: str = ""
    results: list[dict] = []
    heavy_list: list[str] = []

    @rx.event
    async def increment(self):
        """Fast handler."""
        await PulseCollector.emit_connection(self.router.session.client_token, "connect", "/")
        self.count += 1

    @rx.event
    async def slow_search(self):
        """Simulates a slow database query."""
        await asyncio.sleep(random.uniform(0.1, 0.8))
        self.results = [
            {"id": i, "title": f"Result {i} for {self.query}"}
            for i in range(random.randint(5, 20))
        ]
        await PulseCollector.emit_state_snapshot(
            self.router.session.client_token,
            {"count": self.count, "results": self.results, "items": self.items},
            ["results"],
        )

    @rx.event
    async def add_items(self):
        """Simulates state growth."""
        new_items = [f"item_{random.randint(1000, 9999)}" for _ in range(50)]
        self.items.extend(new_items)
        self.heavy_list.extend([f"x" * 100 for _ in range(10)])

    @rx.event
    async def buggy_handler(self):
        """Sometimes raises an error."""
        if random.random() < 0.4:
            raise ValueError("Simulated database timeout")
        self.count += 10


def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Sample monitored app", size="6"),
            rx.text(
                "This app is being observed by Reflex Pulse.",
                color="#6B7280",
            ),
            rx.hstack(
                rx.button("Increment", on_click=DemoState.increment),
                rx.button("Slow search", on_click=DemoState.slow_search, color_scheme="amber"),
                rx.button("Grow state", on_click=DemoState.add_items, color_scheme="blue"),
                rx.button("Maybe error", on_click=DemoState.buggy_handler, color_scheme="red"),
                wrap="wrap",
                gap="0.5rem",
            ),
            rx.text(f"Count: {DemoState.count}", size="4", weight="bold"),
            rx.text(f"Items in state: {DemoState.items.length()}"),
            rx.text(f"Results: {DemoState.results.length()}"),
            spacing="4",
            padding="2rem",
        )
    )


app = rx.App()
app.add_page(index, route="/")
