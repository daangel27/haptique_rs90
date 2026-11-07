"""Serve the Haptique RS90 dashboard strategy to the Home Assistant frontend."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STRATEGY_FILE = Path(__file__).parent / "frontend" / "haptique-rs90-strategy.js"
STRATEGY_URL = f"/{DOMAIN}/haptique-rs90-strategy.js"
_REGISTERED = f"{DOMAIN}_frontend_registered"


def _version() -> str:
    manifest = Path(__file__).parent / "manifest.json"
    return json.loads(manifest.read_text(encoding="utf-8"))["version"]


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Serve the strategy script and load it on every frontend page, once."""
    if hass.data.get(_REGISTERED) or "frontend" not in hass.config.components:
        return
    # Imported here: the frontend is optional (headless installs, tests).
    from homeassistant.components.frontend import add_extra_js_url
    from homeassistant.components.http import StaticPathConfig

    hass.data[_REGISTERED] = True
    version = await hass.async_add_executor_job(_version)
    await hass.http.async_register_static_paths(
        [StaticPathConfig(STRATEGY_URL, str(STRATEGY_FILE), True)]
    )
    # The version query string makes browsers fetch the new file after an update.
    add_extra_js_url(hass, f"{STRATEGY_URL}?v={version}")
    _LOGGER.debug("Dashboard strategy served at %s", STRATEGY_URL)
