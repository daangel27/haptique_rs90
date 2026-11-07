"""Websocket API used by the Haptique RS90 dashboard strategy."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from .const import CONF_DASHBOARD_COMMANDS, DOMAIN

WS_DASHBOARD = f"{DOMAIN}/dashboard"
_REGISTERED = f"{DOMAIN}_websocket_registered"


@callback
def async_register_websocket(hass: HomeAssistant) -> None:
    """Register the websocket commands once."""
    if hass.data.get(_REGISTERED):
        return
    hass.data[_REGISTERED] = True
    websocket_api.async_register_command(hass, ws_dashboard)


def _remote_layout(hass: HomeAssistant, coordinator: Any) -> dict[str, Any]:
    """Describe one RS90 from the registry and the last known inventory.

    Uses the entity registry and the coordinator data rather than entity
    states, so the layout stays the same while the remote sleeps (offline
    entities lose their attributes).
    """
    entry = coordinator.entry
    remote_id = entry.data["remote_id"]
    data = coordinator.data or {}
    layout: dict[str, Any] = {
        "device_id": coordinator.device_id,
        "name": entry.title,
        "macros": [],
        "sequences": [],
        "apps": [],
        "status": [],
        "devices": [],
    }
    if device := dr.async_get(hass).async_get(coordinator.device_id or ""):
        layout["name"] = device.name_by_user or device.name or entry.title

    for item in er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id):
        if item.disabled_by:
            continue
        unique_id = item.unique_id or ""
        if item.domain == "switch":
            kind = (item.capabilities or {}).get("haptique_target_kind", "macro")
            layout["sequences" if kind == "sequence" else "macros"].append(
                item.entity_id
            )
        elif item.domain == "button" and unique_id.startswith(f"{remote_id}_app_"):
            layout["apps"].append(item.entity_id)
        elif unique_id.startswith(f"{remote_id}_commands_") or unique_id.endswith(
            "_info_summary"
        ):
            continue
        else:
            layout["status"].append(item.entity_id)

    commands = data.get("device_commands", {})
    selection = entry.options.get(CONF_DASHBOARD_COMMANDS, {})
    for device in data.get("devices", []):
        name = device.get("name")
        ids = [cmd.get("id") for cmd in commands.get(name, []) if cmd.get("id")]
        # The firmware can list the same command twice.
        ids = list(dict.fromkeys(ids))
        if (chosen := selection.get(device.get("id"))) is not None:
            ids = [cmd for cmd in ids if cmd in chosen]
        layout["devices"].append(
            {"name": name, "rs90_device_id": device.get("id"), "commands": ids}
        )
    layout["devices"].sort(key=lambda device: str(device["name"]).lower())
    return layout


@websocket_api.websocket_command({vol.Required("type"): WS_DASHBOARD})
@callback
def ws_dashboard(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    """Return the layout of every configured RS90."""
    remotes = [
        _remote_layout(hass, coordinator)
        for coordinator in hass.data.get(DOMAIN, {}).values()
        if hasattr(coordinator, "entry") and hasattr(coordinator, "device_id")
    ]
    connection.send_result(msg["id"], {"remotes": remotes})
