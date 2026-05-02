import reflex as rx

config = rx.Config(
    app_name="reflex_pulse",
    db_url="sqlite:///pulse.db",
    telemetry_enabled=False,
    loglevel="info",
)
