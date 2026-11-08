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


async def test_removed_targets_and_apps_left_out(hass, coordinator, remote):
    await _seed(hass, coordinator)
    registry = er.async_get(hass)
    registry.async_get_or_create(
        "switch",
        "haptique_rs90",
        "remote-1_macro_gone",
        config_entry=coordinator.entry,
        capabilities={"haptique_target_kind": "macro"},
    )
    # Before the inventory arrives, nothing is hidden.
    assert len(_remote_layout(hass, coordinator)["macros"]) == 2

    await message(
        hass,
        "macro/list",
        json.dumps([{"id": "m1", "name": "CANAL", "type": "macro"}]),
    )
    await message(hass, "app/list", json.dumps([{"id": "other.app", "name": "X"}]))
    layout = _remote_layout(hass, coordinator)
    assert layout["macros"] == [
        registry.async_get_entity_id("switch", "haptique_rs90", "remote-1_macro_m1")
    ]
    assert layout["apps"] == []  # Kore is no longer installed


async def test_refresh_button_and_reconnect_catch_up(hass, coordinator, publish):
    from custom_components.haptique_rs90.button import HaptiqueRS90RefreshButton

    button = HaptiqueRS90RefreshButton(coordinator, coordinator.entry)
    await button.async_press()
    topics = [call.args[1] for call in publish.call_args_list]
    assert topics[0].endswith("/discovery/refresh")

    def refreshes():
        return sum(
            call.args[1].endswith("/discovery/refresh")
            for call in publish.call_args_list
        )

    before = refreshes()
    for status in ("offline", "online", "offline", "online"):
        await message(hass, "status", status)
    # Only the first reconnection within 5 minutes asks for a new snapshot.
    assert refreshes() == before + 1


async def test_switch_icons_tell_sequences_from_macros(hass, coordinator):
    """Sequences use playlist icons, macros play/stop circles."""
    from custom_components.haptique_rs90.switch import HaptiqueRS90MacroSwitch

    macro = HaptiqueRS90MacroSwitch.__new__(HaptiqueRS90MacroSwitch)
    sequence = HaptiqueRS90MacroSwitch.__new__(HaptiqueRS90MacroSwitch)
    for switch, kind in ((macro, "macro"), (sequence, "sequence")):
        switch._target_kind = kind
        switch._switch_id = "x"
        switch.coordinator = coordinator
    assert macro.icon == "mdi:play-circle"
    assert sequence.icon == "mdi:playlist-play"
