import reflex as rx
from reflex_base.plugins.sitemap import SitemapPlugin

config = rx.Config(
    app_name="reflex_pulse",
    db_url="sqlite:///pulse.db",
    telemetry_enabled=False,
    plugins=[SitemapPlugin()],
)
