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


async def _commands_form(hass, entry, device="d1"):
    result = await _open(hass, entry, "dashboard_device")
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"device": device}
    )
    assert result["step_id"] == "dashboard_commands"
    return result


def _default(result, key):
    for field in result["data_schema"].schema:
        if str(field) == key:
            return field.default()
    raise KeyError(key)


async def test_choose_hide_and_reset_commands(hass, coordinator, remote):
    entry = coordinator.entry
    await _devices(hass)

    # Choose: the list starts unticked when every command was shown.
    result = await _commands_form(hass, entry)
    assert _default(result, "mode") == "all"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"mode": "choose"}
    )
    assert result["step_id"] == "dashboard_pick"
    assert _default(result, "commands") == []

    # Shortcuts redisplay the list ticked or unticked, without saving.
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"shortcut": "tick_all", "commands": []}
    )
    assert result["step_id"] == "dashboard_pick"
    assert _default(result, "commands") == ["UP", "DOWN", "OK"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"shortcut": "untick_all", "commands": ["UP"]}
    )
    assert _default(result, "commands") == []

    # Nothing ticked is an error, not a silent hide.
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"shortcut": "none", "commands": []}
    )
    assert result["errors"] == {"base": "no_commands"}

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"shortcut": "none", "commands": ["OK", "UP"]}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_DASHBOARD_COMMANDS] == {"d1": ["UP", "OK"]}
    kodi = _remote_layout(hass, coordinator)["devices"][0]
    assert kodi["commands"] == ["UP", "OK"]

    # Reopening shows the current choice.
    result = await _commands_form(hass, entry)
    assert _default(result, "mode") == "choose"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"mode": "choose"}
    )
    assert _default(result, "commands") == ["UP", "OK"]

    # Hide: the device view disappears.
    result = await _commands_form(hass, entry)
    await hass.config_entries.options.async_configure(
        result["flow_id"], {"mode": "hide"}
    )
    assert entry.options[CONF_DASHBOARD_COMMANDS] == {"d1": []}
    assert _remote_layout(hass, coordinator)["devices"][0]["commands"] == []

    # All again: the selection is removed, new commands appear by themselves.
    result = await _commands_form(hass, entry)
    assert _default(result, "mode") == "hide"
    await hass.config_entries.options.async_configure(
        result["flow_id"], {"mode": "all"}
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
