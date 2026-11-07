"""Dashboard strategy registration."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.haptique_rs90.frontend import (
    STRATEGY_FILE,
    STRATEGY_URL,
    async_register_frontend,
)


async def test_strategy_file_is_shipped():
    """The strategy script exists and registers its custom element."""
    script = Path(STRATEGY_FILE).read_text(encoding="utf-8")
    assert "ll-strategy-dashboard-haptique-rs90" in script
    assert "window.customStrategies" in script


async def test_not_registered_without_frontend(hass):
    """Headless installs (no frontend) are left alone."""
    assert "frontend" not in hass.config.components
    with patch("homeassistant.components.frontend.add_extra_js_url") as add_js:
        await async_register_frontend(hass)
    add_js.assert_not_called()


async def test_registered_once_with_frontend(hass):
    """The script is served and loaded once, with a cache-busting version."""
    hass.config.components.add("frontend")
    hass.http = MagicMock()
    hass.http.async_register_static_paths = AsyncMock()
    with patch("homeassistant.components.frontend.add_extra_js_url") as add_js:
        await async_register_frontend(hass)
        await async_register_frontend(hass)
    hass.http.async_register_static_paths.assert_awaited_once()
    add_js.assert_called_once()
    assert add_js.call_args.args[1].startswith(f"{STRATEGY_URL}?v=")
