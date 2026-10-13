"""Standard MQTT inventory, feedback, and execution routing."""

import asyncio
import json
from unittest.mock import patch

import pytest
from homeassistant.exceptions import HomeAssistantError
from pytest_homeassistant_custom_component.common import async_fire_mqtt_message

ROOT = "Haptique/remote-1"


async def message(hass, topic, payload):
    async_fire_mqtt_message(hass, f"{ROOT}/{topic}", payload)
    await hass.async_block_till_done()


async def inventory(hass, kind, items):
    await message(hass, f"{kind}/list", json.dumps(items))


async def test_separate_inventories_and_metadata(hass, coordinator, publish):
    await inventory(
        hass,
        "macro",
        [{"id": "m1", "name": "Movie", "type": "macro", "supportsOff": True}],
    )
    await inventory(hass, "sequence", [{"Id": "s1", "name": "Movie"}])
    assert coordinator.data["macros"][0]["type"] == "macro"
    assert coordinator.data["sequences"] == [{"id": "s1", "name": "Movie"}]
    assert any(
        c.args[1:] == (f"{ROOT}/sequence/s1/currentstatus", "")
        for c in publish.call_args_list
    )


@pytest.mark.parametrize(
    "payload",
    [
        "{}",
        "[1]",
        '[{"id":"m1"}]',
        '[{"id":"m1","name":"A"},{"id":"m1","name":"B"}]',
        "null",
        '[{"id":"bad/id","name":"A"}]',
    ],
)
async def test_invalid_inventory_preserves_last_snapshot(hass, coordinator, payload):
    await inventory(hass, "macro", [{"id": "m1", "name": "Movie"}])
    await message(hass, "macro/list", payload)
    assert coordinator.data["macros"] == [{"id": "m1", "name": "Movie"}]


async def test_state_queries_subscribe_before_publish(hass, coordinator):
    async def reply(_hass, topic, payload, **kwargs):
        if topic.endswith("/currentstatus"):
            async_fire_mqtt_message(
                hass, topic.replace("/currentstatus", "/status"), "ON"
            )

    with patch("homeassistant.components.mqtt.async_publish", side_effect=reply):
        await inventory(hass, "macro", [{"id": "m1", "name": "Movie"}])
    assert coordinator.targets.state("macro", "m1") == "on"


async def test_commands_wait_for_feedback_and_unknown(hass, coordinator, publish):
    await inventory(hass, "macro", [{"id": "m1", "name": "Movie"}])
    assert coordinator.targets.state("macro", "m1") is None
    await coordinator.async_trigger_target("macro", "m1", "on")
    publish.assert_called_with(
        hass, f"{ROOT}/macro/m1/trigger", "on", qos=1, retain=False
    )
    assert coordinator.targets.state("macro", "m1") is None
    await message(hass, "macro/m1/status", "ON")
    await message(
        hass, "macro/m1/result", '{"status":"rejected","error":"execution_busy"}'
    )
    assert coordinator.targets.state("macro", "m1") == "on"
    assert coordinator.targets.result("macro", "m1")["error"] == "execution_busy"
    await message(hass, "macro/m1/status", "UNKNOWN")
    assert coordinator.targets.state("macro", "m1") is None


async def test_duplicate_names_and_id_alias_precedence(hass, coordinator):
    await inventory(
        hass,
        "macro",
        [
            {"id": "a", "name": "Same"},
            {"id": "b", "name": "Same"},
            {"id": "c", "name": "a"},
        ],
    )
    await message(hass, "macro/Same/status", "ON")
    assert coordinator.targets.state("macro", "a") is None
    assert coordinator.targets.state("macro", "b") is None
    await message(hass, "macro/a/status", "OFF")
    assert coordinator.targets.state("macro", "a") == "off"
    assert coordinator.targets.state("macro", "c") is None
    await inventory(hass, "macro", [{"id": "a", "name": "Movie", "type": "macro"}])
    await message(hass, "macro/a/status", "ON")
    await message(hass, "macro/Movie/status", "OFF")
    assert coordinator.targets.state("macro", "a") == "on"


async def test_conflicting_modern_ids_reject_execution(hass, coordinator, publish):
    await inventory(hass, "macro", [{"id": "x", "name": "Real", "type": "macro"}])
    await inventory(hass, "sequence", [{"id": "x", "name": "Sequence"}])
    publish.reset_mock()
    with pytest.raises(HomeAssistantError, match="conflict"):
        await coordinator.async_trigger_target("sequence", "x", "on")
    publish.assert_not_called()
    await message(hass, "sequence/x/status", "ON")
    assert coordinator.targets.state("sequence", "x") is None


async def test_rename_remove_readd_and_repeated_snapshot(hass, coordinator, publish):
    items = [{"id": "m1", "name": "Movie"}]
    await inventory(hass, "macro", items)
    first = len(publish.call_args_list)
    await inventory(hass, "macro", items)
    assert len(publish.call_args_list) == first
    await inventory(hass, "macro", [{"id": "m1", "name": "Renamed"}])
    await message(hass, "macro/Movie/status", "ON")
    assert coordinator.targets.state("macro", "m1") is None
    await message(hass, "macro/Renamed/status", "OFF")
    assert coordinator.targets.state("macro", "m1") == "off"
    await inventory(hass, "macro", [])
    await message(hass, "macro/m1/status", "ON")
    assert coordinator.targets.target("macro", "m1") is None
    await inventory(hass, "macro", items)
    assert coordinator.targets.state("macro", "m1") is None


async def test_refresh_and_reconnect_query_existing_targets(hass, coordinator, publish):
    await inventory(hass, "sequence", [{"id": "s1", "name": "Sequence"}])
    publish.reset_mock()
    await coordinator.async_force_refresh_lists()
    topics = [c.args[1] for c in publish.call_args_list]
    assert f"{ROOT}/discovery/refresh" in topics
    assert f"{ROOT}/sequence/s1/currentstatus" in topics
    publish.reset_mock()
    await message(hass, "status", "online")
    assert any(
        c.args[1] == f"{ROOT}/sequence/s1/currentstatus" for c in publish.call_args_list
    )


async def test_unload_during_subscription_releases_callbacks(hass, coordinator):
    from homeassistant.components import mqtt

    original = mqtt.async_subscribe
    entered = asyncio.Event()
    release = asyncio.Event()

    async def delayed(*args, **kwargs):
        if "/macro/" in args[1]:
            entered.set()
            await release.wait()
        return await original(*args, **kwargs)

    with patch("homeassistant.components.mqtt.async_subscribe", side_effect=delayed):
        async_fire_mqtt_message(
            hass, f"{ROOT}/macro/list", '[{"id":"m1","name":"Movie"}]'
        )
        await asyncio.wait_for(entered.wait(), 1)
        await coordinator.async_shutdown()
        release.set()
    await message(hass, "macro/m1/status", "ON")
    assert coordinator.targets.state("macro", "m1") is None


async def test_existing_monitoring_and_device_rgb_controls(hass, coordinator, publish):
    await message(hass, "battery_level", "85%")
    events = []
    hass.bus.async_listen("haptique_rs90_key_pressed", events.append)
    await message(hass, "keys", "button:7")
    await message(hass, "keys", "button:7")
    assert coordinator.data["battery_level"] == 85
    assert len(events) == 2
    await coordinator.async_trigger_device_command("Receiver", "POWER")
    publish.assert_called_with(
        hass, f"{ROOT}/device/Receiver/trigger", "POWER", qos=1, retain=False
    )
    await coordinator.async_control_led_light("on", 5)
    publish.assert_called_with(hass, f"{ROOT}/ledlight/on", "5", qos=1, retain=False)


async def test_remove_readd_before_reconciliation_queries_again(
    hass, coordinator, publish
):
    await inventory(hass, "macro", [{"id": "m1", "name": "Movie"}])
    await message(hass, "macro/m1/status", "ON")
    publish.reset_mock()
    async_fire_mqtt_message(hass, f"{ROOT}/macro/list", "[]")
    async_fire_mqtt_message(hass, f"{ROOT}/macro/list", '[{"id":"m1","name":"Movie"}]')
    await hass.async_block_till_done()
    assert coordinator.targets.state("macro", "m1") is None
    assert any(
        c.args[1] == f"{ROOT}/macro/m1/currentstatus" for c in publish.call_args_list
    )


async def test_legacy_execution_name_feedback_follows_id_query(hass, coordinator):
    await inventory(hass, "macro", [{"id": "s1", "name": "Movie"}])
    await message(hass, "macro/s1/status", "OFF")
    await message(hass, "macro/Movie/status", "ON")
    assert coordinator.targets.state("macro", "s1") == "on"


async def test_sequence_name_cannot_spoof_canonical_macro_feedback(hass, coordinator):
    await inventory(hass, "macro", [{"id": "m1", "name": "Real", "type": "macro"}])
    await inventory(hass, "sequence", [{"id": "s1", "name": "m1"}])
    await message(hass, "macro/m1/status", "ON")
    await message(hass, "macro/m1/result", '{"status":"executed"}')
    assert coordinator.targets.state("macro", "m1") is None
    assert coordinator.targets.result("macro", "m1") is None
    await message(hass, "sequence/s1/status", "OFF")
    assert coordinator.targets.state("sequence", "s1") == "off"
