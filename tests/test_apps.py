"""Installed app discovery, truthful launch feedback and stable buttons."""

import pytest
from homeassistant.const import Platform
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er

from .test_coordinator import ROOT, inventory, message
from .test_services import call


async def test_app_inventory_normalizes_and_rejects_bad_snapshots(hass, coordinator):
    await inventory(hass, "app", [{"Id": "com.spotify.music", "name": "Spotify"}])
    assert coordinator.data["apps"] == [{"id": "com.spotify.music", "name": "Spotify"}]
    await message(hass, "app/list", '[{"id":"missing_name"}]')
    assert len(coordinator.data["apps"]) == 1
    await inventory(hass, "app", [])
    assert coordinator.data["apps"] == []


async def test_launch_uses_package_and_does_not_invent_active_app(
    hass, coordinator, publish
):
    await inventory(
        hass,
        "app",
        [
            {"id": "com.spotify.music", "name": "Music"},
            {"id": "com.example.music", "name": "Music"},
        ],
    )
    await coordinator.async_launch_app("com.spotify.music")
    publish.assert_called_with(
        hass, f"{ROOT}/app/com.spotify.music/open", "open", qos=1, retain=False
    )
    assert coordinator.data["active_app"] is None
    assert coordinator.data["app_results"] == {}
    await message(hass, "app/com.spotify.music/status", "launched")
    assert coordinator.data["app_results"]["com.spotify.music"] == {
        "status": "launched"
    }
    assert coordinator.data["active_app"] is None
    await message(hass, "active_app", "com.spotify.music")
    assert coordinator.data["active_app"] == "com.spotify.music"


async def test_immediate_launch_reply_is_received(hass, coordinator):
    from unittest.mock import patch

    from pytest_homeassistant_custom_component.common import async_fire_mqtt_message

    await inventory(hass, "app", [{"id": "com.spotify.music", "name": "Spotify"}])

    async def reply(_hass, topic, _payload, **kwargs):
        async_fire_mqtt_message(
            hass, topic.removesuffix("/open") + "/status", "launched"
        )

    with patch("homeassistant.components.mqtt.async_publish", side_effect=reply):
        await coordinator.async_launch_app("com.spotify.music")
    await hass.async_block_till_done()
    assert coordinator.data["app_results"]["com.spotify.music"]["status"] == "launched"


async def test_launch_error_preserves_last_reported_app(hass, coordinator, publish):
    await inventory(hass, "app", [{"id": "com.spotify.music", "name": "Spotify"}])
    await message(hass, "active_app", "com.other.player")
    await coordinator.async_launch_app("com.spotify.music")
    await message(hass, "app/com.spotify.music/status", "ERROR:launch_failed")
    assert coordinator.data["active_app"] == "com.other.player"
    assert coordinator.data["app_results"]["com.spotify.music"] == {
        "status": "error",
        "error": "launch_failed",
    }
    await message(hass, "app/com.unknown/status", "launched")
    assert "com.unknown" not in coordinator.data["app_results"]


async def test_missing_removed_and_label_references_cannot_launch(
    hass, coordinator, publish
):
    await inventory(hass, "app", [{"id": "com.spotify.music", "name": "Spotify"}])
    publish.reset_mock()
    with pytest.raises(HomeAssistantError):
        await coordinator.async_launch_app("Spotify")
    await inventory(hass, "app", [])
    with pytest.raises(HomeAssistantError):
        await coordinator.async_launch_app("com.spotify.music")
    publish.assert_not_called()


async def test_launch_app_action(hass, coordinator, remote, publish):
    await inventory(hass, "app", [{"id": "com.spotify.music", "name": "Spotify"}])
    await call(
        hass, "launch_app", {"rs90_id": remote, "app_package_id": "com.spotify.music"}
    )
    publish.assert_called_with(
        hass, f"{ROOT}/app/com.spotify.music/open", "open", qos=1, retain=False
    )


async def test_registered_app_button_rename_remove_readd_and_active_sensor(
    hass, coordinator, publish
):
    platforms = [Platform.BUTTON, Platform.SENSOR]
    await hass.config_entries.async_forward_entry_setups(coordinator.entry, platforms)
    try:
        await message(hass, "status", "online")
        await inventory(hass, "app", [{"id": "com.spotify.music", "name": "Spotify"}])
        registry = er.async_get(hass)
        button_id = registry.async_get_entity_id(
            "button", "haptique_rs90", "remote-1_app_com.spotify.music"
        )
        sensor_id = registry.async_get_entity_id(
            "sensor", "haptique_rs90", "remote-1_active_app"
        )
        assert button_id is not None
        assert hass.states.get(sensor_id).state == "unknown"
        await hass.services.async_call(
            "button", "press", {"entity_id": button_id}, blocking=True
        )
        assert publish.call_args.args[1:] == (
            f"{ROOT}/app/com.spotify.music/open",
            "open",
        )
        await message(hass, "active_app", "com.spotify.music")
        assert hass.states.get(sensor_id).state == "com.spotify.music"
        assert hass.states.get(sensor_id).attributes["app_name"] == "Spotify"
        await inventory(hass, "app", [{"id": "com.spotify.music", "name": "Renamed"}])
        assert (
            registry.async_get_entity_id(
                "button", "haptique_rs90", "remote-1_app_com.spotify.music"
            )
            == button_id
        )
        assert hass.states.get(button_id).attributes["app_name"] == "Renamed"
        await inventory(hass, "app", [])
        assert hass.states.get(button_id).state == "unavailable"
        assert hass.states.get(sensor_id).state == "com.spotify.music"
        await inventory(hass, "app", [{"id": "com.spotify.music", "name": "Returned"}])
        assert hass.states.get(button_id).state != "unavailable"
        await message(hass, "status", "offline")
        assert hass.states.get(button_id).state == "unavailable"
    finally:
        await hass.config_entries.async_unload_platforms(coordinator.entry, platforms)
