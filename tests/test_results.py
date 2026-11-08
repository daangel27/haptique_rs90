"""Readable macro/sequence execution results with name, action and history."""

from homeassistant.const import Platform
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import (
    async_capture_events,
    async_fire_mqtt_message,
)

from custom_components.haptique_rs90.targets import RESULT_EVENT

from .test_coordinator import ROOT, inventory, message

MACROS = [
    {"id": "m1", "name": "CANAL", "type": "macro", "supportsOff": True},
    {"id": "m2", "name": "KODI", "type": "macro", "supportsOff": True},
]


async def test_result_records_name_action_and_fires_event(
    hass, coordinator, publish
):
    events = async_capture_events(hass, RESULT_EVENT)
    await inventory(hass, "macro", MACROS)
    await coordinator.async_trigger_target("macro", "m1", "off")
    await message(
        hass,
        "macro/m1/result",
        '{"status":"skipped","error":"already_in_requested_state"}',
    )
    record = coordinator.data["last_target_result"]
    assert record["target_name"] == "CANAL"
    assert record["target_id"] == "m1"
    assert record["target_kind"] == "macro"
    assert record["action"] == "off"
    assert record["status"] == "skipped"
    assert record["error"] == "already_in_requested_state"
    assert len(events) == 1
    assert events[0].data["target_name"] == "CANAL"
    assert events[0].data["remote_id"] == "remote-1"

    # A result for a run started elsewhere (RS90 screen) has no known action.
    await message(hass, "macro/m2/result", '{"status":"executed"}')
    record = coordinator.data["last_target_result"]
    assert record["target_name"] == "KODI"
    assert record["action"] is None
    assert record["error"] is None
    assert len(events) == 2


async def test_retained_result_is_not_a_new_run(hass, coordinator, publish):
    events = async_capture_events(hass, RESULT_EVENT)
    await inventory(hass, "macro", MACROS)
    async_fire_mqtt_message(
        hass, f"{ROOT}/macro/m1/result", '{"status":"executed"}', retain=True
    )
    await hass.async_block_till_done()
    assert coordinator.targets.result("macro", "m1") == {"status": "executed"}
    assert coordinator.data["last_target_result"] is None
    assert events == []


async def test_invalid_result_is_ignored(hass, coordinator, publish):
    events = async_capture_events(hass, RESULT_EVENT)
    await inventory(hass, "macro", MACROS)
    await message(hass, "macro/m1/result", "Canal - Off 200")
    await message(hass, "macro/m1/result", '{"status":"weird"}')
    assert coordinator.data["last_target_result"] is None
    assert events == []


async def test_last_macro_result_sensor_state(hass, coordinator, publish):
    platforms = [Platform.SENSOR]
    await hass.config_entries.async_forward_entry_setups(coordinator.entry, platforms)
    try:
        sensor_id = er.async_get(hass).async_get_entity_id(
            "sensor", "haptique_rs90", "remote-1_last_macro_result"
        )
        assert sensor_id
        assert hass.states.get(sensor_id).state == "unknown"
        await inventory(hass, "macro", MACROS)
        await coordinator.async_trigger_target("macro", "m1", "off")
        await message(
            hass,
            "macro/m1/result",
            '{"status":"skipped","error":"already_in_requested_state"}',
        )
        state = hass.states.get(sensor_id)
        assert state.state == "CANAL · OFF · skipped (already_in_requested_state)"
        assert state.attributes["target_name"] == "CANAL"
        assert state.attributes["action"] == "off"
        await message(hass, "macro/m2/result", '{"status":"executed"}')
        assert hass.states.get(sensor_id).state == "KODI · executed"
    finally:
        await hass.config_entries.async_unload_platforms(coordinator.entry, platforms)


async def test_setup_clears_stale_firmware_version(hass, coordinator):
    from homeassistant.helpers import device_registry as dr

    registry = dr.async_get(hass)
    registry.async_get_or_create(
        config_entry_id=coordinator.entry.entry_id,
        identifiers={("haptique_rs90", "remote-1")},
        sw_version="1.0",
    )
    device = registry.async_get_or_create(
        config_entry_id=coordinator.entry.entry_id,
        identifiers={("haptique_rs90", "remote-1")},
        manufacturer="Haptique",
        model="RS90",
        sw_version=None,
    )
    assert device.sw_version is None


async def test_logbook_describes_every_result(hass, coordinator, publish):
    """Repeated identical results each get their own logbook entry."""
    from custom_components.haptique_rs90.logbook import (
        async_describe_events,
        result_message,
    )

    described = {}
    async_describe_events(
        hass, lambda domain, event_type, fn: described.update({event_type: fn})
    )
    describe = described[RESULT_EVENT]

    registry = er.async_get(hass)
    switch = registry.async_get_or_create(
        "switch",
        "haptique_rs90",
        "remote-1_macro_m1",
        config_entry=coordinator.entry,
        capabilities={"haptique_target_kind": "macro"},
    )
    events = async_capture_events(hass, RESULT_EVENT)
    await inventory(hass, "macro", MACROS)
    for _ in range(2):
        await coordinator.async_trigger_target("macro", "m1", "off")
        await message(
            hass,
            "macro/m1/result",
            '{"status":"skipped","error":"already_in_requested_state"}',
        )
    assert len(events) == 2
    for event in events:
        entry = describe(event)
        assert entry["name"] == "RS90 CANAL"
        assert entry["message"] == "→ OFF: skipped (already_in_requested_state)"
        assert entry["entity_id"] == switch.entity_id

    # Unknown target switch and no action (run started on the RS90 screen).
    await message(hass, "macro/m2/result", '{"status":"executed"}')
    entry = describe(events[-1])
    assert entry["name"] == "RS90 KODI"
    assert entry["message"] == "→ result: executed"
    assert "entity_id" not in entry
    assert result_message({}) == "result: unknown"
