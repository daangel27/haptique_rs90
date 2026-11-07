"""Dashboard layout served to the frontend strategy."""

import json

from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component

from custom_components.haptique_rs90.websocket import (
    WS_DASHBOARD,
    _remote_layout,
    async_register_websocket,
)

from .test_coordinator import message


async def _seed(hass, coordinator):
    await message(
        hass,
        "device/list",
        json.dumps([{"id": "d1", "name": "KODI"}, {"id": "d2", "name": "AMPLI"}]),
    )
    await message(
        hass,
        "device/KODI/commands",
        json.dumps([{"id": "UP"}, {"id": "OK"}, {"id": "UP"}]),
    )
    registry = er.async_get(hass)
    entry = coordinator.entry
    for domain, unique_id, caps in (
        ("switch", "remote-1_macro_m1", {"haptique_target_kind": "macro"}),
        ("switch", "remote-1_sequence_s1", {"haptique_target_kind": "sequence"}),
        ("button", "remote-1_app_org.xbmc.kore", None),
        ("button", "remote-1_rgb_button", None),
        ("sensor", "remote-1_commands_d1", None),
        ("sensor", "remote-1_info_summary", None),
        ("sensor", "remote-1_battery", None),
    ):
        registry.async_get_or_create(
            domain, "haptique_rs90", unique_id, config_entry=entry, capabilities=caps
        )
    disabled = registry.async_get_or_create(
        "button", "haptique_rs90", "remote-1_app_com.android.chrome", config_entry=entry
    )
    registry.async_update_entity(
        disabled.entity_id, disabled_by=er.RegistryEntryDisabler.USER
    )


async def test_layout_from_registry_and_inventory(hass, coordinator, remote):
    await _seed(hass, coordinator)
    layout = _remote_layout(hass, coordinator)
    assert layout["device_id"] == remote
    assert len(layout["macros"]) == 1 and layout["macros"][0].startswith("switch.")
    assert len(layout["sequences"]) == 1
    assert len(layout["apps"]) == 1  # the disabled app is left out
    # RGB button and battery are status; commands and info summary are not.
    assert len(layout["status"]) == 2
    assert [d["name"] for d in layout["devices"]] == ["AMPLI", "KODI"]
    kodi = layout["devices"][1]
    assert kodi == {"name": "KODI", "rs90_device_id": "d1", "commands": ["UP", "OK"]}
    assert layout["devices"][0]["commands"] == []


async def test_websocket_command(hass, coordinator, remote, hass_ws_client):
    assert await async_setup_component(hass, "websocket_api", {})
    async_register_websocket(hass)
    async_register_websocket(hass)  # registering twice is harmless
    await _seed(hass, coordinator)
    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": WS_DASHBOARD})
    reply = await client.receive_json()
    assert reply["success"]
    remotes = reply["result"]["remotes"]
    assert len(remotes) == 1
    assert remotes[0]["devices"][1]["commands"] == ["UP", "OK"]
