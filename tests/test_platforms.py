"""Exercise actual Home Assistant platform registration and state writes."""

from homeassistant.const import Platform
from homeassistant.helpers import entity_registry as er

from .test_coordinator import inventory, message


async def test_registered_switch_survives_sequence_migration(
    hass, coordinator, publish
):
    platforms = [
        Platform.SWITCH,
        Platform.SENSOR,
        Platform.BUTTON,
        Platform.BINARY_SENSOR,
    ]
    await hass.config_entries.async_forward_entry_setups(coordinator.entry, platforms)
    try:
        await message(hass, "status", "online")
        await inventory(hass, "macro", [{"id": "s1", "name": "Movie"}])
        await hass.async_block_till_done()
        registry = er.async_get(hass)
        entity_id = registry.async_get_entity_id(
            "switch", "haptique_rs90", "remote-1_macro_s1"
        )
        assert hass.states.get(entity_id).state == "unknown"
        await message(hass, "macro/s1/status", "ON")
        assert hass.states.get(entity_id).state == "on"
        await inventory(hass, "macro", [])
        assert hass.states.get(entity_id).state == "unavailable"
        await inventory(hass, "sequence", [{"id": "s1", "name": "Renamed"}])
        assert registry.async_get(entity_id).unique_id == "remote-1_macro_s1"
        assert (
            registry.async_get(entity_id).capabilities["haptique_target_kind"]
            == "sequence"
        )
        assert hass.states.get(entity_id).attributes["target_kind"] == "sequence"
        await message(hass, "sequence/s1/status", "OFF")
        assert hass.states.get(entity_id).state == "off"
        await hass.services.async_call(
            "switch", "turn_on", {"entity_id": entity_id}, blocking=True
        )
        assert publish.call_args.args[1:] == (
            "Haptique/remote-1/sequence/s1/trigger",
            "on",
        )
        assert hass.states.get(entity_id).state == "off"
    finally:
        await hass.config_entries.async_unload_platforms(coordinator.entry, platforms)
