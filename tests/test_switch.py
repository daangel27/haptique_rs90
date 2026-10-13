"""Preserve automation identities across firmware inventory changes."""

import pytest
from homeassistant.helpers import entity_registry as er

from custom_components.haptique_rs90 import switch

from .test_coordinator import inventory, message


async def setup_switches(hass, coordinator):
    entities = []
    await switch.async_setup_entry(
        hass, coordinator.entry, lambda new: entities.extend(new)
    )
    return entities


@pytest.mark.parametrize("sequence_first", [False, True])
async def test_registry_migration_preserves_old_macro_unique_id(
    hass, coordinator, sequence_first
):
    registry = er.async_get(hass)
    old = registry.async_get_or_create(
        "switch", "haptique_rs90", "remote-1_macro_s1", config_entry=coordinator.entry
    )
    entities = await setup_switches(hass, coordinator)
    if sequence_first:
        await inventory(hass, "sequence", [{"id": "s1", "name": "Movie"}])
        assert not entities
        await inventory(hass, "macro", [])
    else:
        await inventory(hass, "macro", [])
        await inventory(hass, "sequence", [{"id": "s1", "name": "Movie"}])
    assert len(entities) == 1
    assert entities[0].unique_id == "remote-1_macro_s1"
    assert entities[0].extra_state_attributes["target_kind"] == "sequence"
    assert registry.async_get(old.entity_id) is not None


async def test_in_session_legacy_migration_and_reappearance(hass, coordinator, publish):
    entities = await setup_switches(hass, coordinator)
    await message(hass, "status", "online")
    await inventory(hass, "macro", [{"id": "s1", "name": "Movie"}])
    entity = entities[0]
    await message(hass, "macro/Movie/status", "ON")
    assert entity.is_on is True
    await inventory(hass, "macro", [])
    assert entity.available is False
    await inventory(hass, "sequence", [{"id": "s1", "name": "Renamed"}])
    assert len(entities) == 1
    assert entity.name == "Renamed"
    assert entity.available is True
    assert entity.is_on is None
    await entity.async_turn_off()
    assert publish.call_args.args[1:] == (
        "Haptique/remote-1/sequence/s1/trigger",
        "off",
    )
    await inventory(hass, "sequence", [])
    assert entity.available is False
    await inventory(hass, "sequence", [{"id": "s1", "name": "Returned"}])
    assert len(entities) == 1
    assert entity.name == "Returned"


async def test_new_sequences_have_distinct_identity_and_unknown_state(
    hass, coordinator
):
    entities = await setup_switches(hass, coordinator)
    await inventory(hass, "macro", [{"id": "m1", "name": "Movie", "type": "macro"}])
    await inventory(hass, "sequence", [{"id": "s1", "name": "Movie"}])
    assert {e.unique_id for e in entities} == {
        "remote-1_macro_m1",
        "remote-1_sequence_s1",
    }
    assert all(e.is_on is None for e in entities)


async def test_conflict_does_not_transfer_macro_identity(hass, coordinator):
    entities = await setup_switches(hass, coordinator)
    await message(hass, "status", "online")
    await inventory(hass, "macro", [{"id": "x", "name": "Real", "type": "macro"}])
    await inventory(hass, "sequence", [{"id": "x", "name": "Sequence"}])
    assert len(entities) == 2
    assert all(not e.available for e in entities)
    assert {e.unique_id: e.extra_state_attributes["target_kind"] for e in entities} == {
        "remote-1_macro_x": "macro",
        "remote-1_sequence_x": "sequence",
    }


async def test_migrated_identity_does_not_transfer_during_later_conflict(
    hass, coordinator
):
    entities = await setup_switches(hass, coordinator)
    await message(hass, "status", "online")
    await inventory(hass, "macro", [{"id": "s1", "name": "Legacy"}])
    migrated = entities[0]
    await inventory(hass, "macro", [])
    await inventory(hass, "sequence", [{"id": "s1", "name": "Sequence"}])
    assert migrated.extra_state_attributes["target_kind"] == "sequence"
    await inventory(hass, "macro", [{"id": "s1", "name": "Real", "type": "macro"}])
    assert migrated.extra_state_attributes["target_kind"] == "sequence"
    assert not migrated.available
    assert len(entities) == 2
    await inventory(hass, "macro", [])
    assert migrated.available
    assert len(entities) == 2
    await inventory(hass, "macro", [{"id": "s1", "name": "Real", "type": "macro"}])
    await inventory(hass, "sequence", [])
    assert not migrated.available
    assert migrated.extra_state_attributes["target_kind"] == "sequence"


async def test_persisted_migration_ownership_survives_platform_restart(
    hass, coordinator
):
    registry = er.async_get(hass)
    registry.async_get_or_create(
        "switch",
        "haptique_rs90",
        "remote-1_macro_s1",
        config_entry=coordinator.entry,
        capabilities={"haptique_target_kind": "sequence"},
    )
    entities = await setup_switches(hass, coordinator)
    await inventory(hass, "macro", [{"id": "s1", "name": "Real", "type": "macro"}])
    await inventory(hass, "sequence", [{"id": "s1", "name": "Sequence"}])
    assert {e.unique_id: e.extra_state_attributes["target_kind"] for e in entities} == {
        "remote-1_macro_s1": "sequence",
        "remote-1_real_macro_s1": "macro",
    }


async def test_pending_new_sequence_keeps_identity_when_legacy_alias_arrives(
    hass, coordinator
):
    entities = await setup_switches(hass, coordinator)
    await inventory(hass, "sequence", [{"id": "s1", "name": "Sequence"}])
    # Entity registration can lag behind independent inventory callbacks.
    await inventory(hass, "macro", [{"id": "s1", "name": "Legacy alias"}])
    assert len(entities) == 1
    assert entities[0].unique_id == "remote-1_sequence_s1"
