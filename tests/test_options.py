"""Options flow: rename and dashboard command buttons."""

import json

from homeassistant.data_entry_flow import FlowResultType

from custom_components.haptique_rs90.const import CONF_DASHBOARD_COMMANDS
from custom_components.haptique_rs90.websocket import _remote_layout

from .test_coordinator import message


async def _devices(hass):
    await message(hass, "device/list", json.dumps([{"id": "d1", "name": "KODI"}]))
    await message(
        hass,
        "device/KODI/commands",
        json.dumps([{"id": "UP"}, {"id": "DOWN"}, {"id": "OK"}, {"id": "UP"}]),
    )


async def _open(hass, entry, step):
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.MENU
    return await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": step}
    )


async def test_rename_keeps_dashboard_options(hass, coordinator):
    entry = coordinator.entry
    hass.config_entries.async_update_entry(
        entry, options={CONF_DASHBOARD_COMMANDS: {"d1": ["OK"]}}
    )
    result = await _open(hass, entry, "name")
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"name": "Salon"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.data["name"] == "Salon"
    assert entry.options[CONF_DASHBOARD_COMMANDS] == {"d1": ["OK"]}


async def test_choose_hide_and_reset_commands(hass, coordinator, remote):
    entry = coordinator.entry
    await _devices(hass)

    result = await _open(hass, entry, "dashboard_device")
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"device": "d1"}
    )
    assert result["step_id"] == "dashboard_commands"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"show_all": False, "commands": ["OK", "UP"]}
    )
    assert entry.options[CONF_DASHBOARD_COMMANDS] == {"d1": ["UP", "OK"]}
    kodi = _remote_layout(hass, coordinator)["devices"][0]
    assert kodi["commands"] == ["UP", "OK"]

    # Untick everything: the device view is hidden (no commands).
    result = await _open(hass, entry, "dashboard_device")
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"device": "d1"}
    )
    await hass.config_entries.options.async_configure(
        result["flow_id"], {"show_all": False, "commands": []}
    )
    assert entry.options[CONF_DASHBOARD_COMMANDS] == {"d1": []}
    assert _remote_layout(hass, coordinator)["devices"][0]["commands"] == []

    # Show all again: the selection is removed, new commands appear by themselves.
    result = await _open(hass, entry, "dashboard_device")
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"device": "d1"}
    )
    await hass.config_entries.options.async_configure(
        result["flow_id"], {"show_all": True, "commands": []}
    )
    assert entry.options[CONF_DASHBOARD_COMMANDS] == {}
    assert _remote_layout(hass, coordinator)["devices"][0]["commands"] == [
        "UP",
        "DOWN",
        "OK",
    ]


async def test_no_device_yet(hass, coordinator):
    result = await _open(hass, coordinator.entry, "dashboard_device")
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "no_devices"
