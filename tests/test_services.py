"""The public action boundary resolves IDs and rejects invalid requests."""

import pytest
from homeassistant.exceptions import HomeAssistantError

from custom_components.haptique_rs90.sensor import RS90InfoSummarySensor

from .test_coordinator import ROOT, inventory


async def call(hass, service, data):
    await hass.services.async_call("haptique_rs90", service, data, blocking=True)


async def test_trigger_macro_compatibility_with_migrated_sequence(
    hass, coordinator, remote, publish
):
    await inventory(hass, "sequence", [{"id": "s1", "name": "Movie"}])
    await call(
        hass,
        "trigger_macro",
        {"rs90_id": remote, "rs90_macro_id": "s1", "action": "off"},
    )
    publish.assert_called_with(
        hass, f"{ROOT}/sequence/s1/trigger", "off", qos=1, retain=False
    )


async def test_explicit_sequence_and_query_actions(hass, coordinator, remote, publish):
    await inventory(hass, "macro", [{"id": "m1", "name": "Movie", "type": "macro"}])
    await inventory(hass, "sequence", [{"id": "s1", "name": "Movie"}])
    await call(hass, "trigger_sequence", {"rs90_id": remote, "rs90_sequence_id": "s1"})
    publish.assert_called_with(
        hass, f"{ROOT}/sequence/s1/trigger", "on", qos=1, retain=False
    )
    await call(
        hass,
        "query_status",
        {"rs90_id": remote, "target_kind": "macro", "target_id": "m1"},
    )
    publish.assert_called_with(
        hass, f"{ROOT}/macro/m1/currentstatus", "", qos=0, retain=False
    )


@pytest.mark.parametrize(
    "service,extra",
    [
        ("trigger_macro", {"rs90_macro_id": "missing"}),
        ("trigger_sequence", {"rs90_sequence_id": "missing"}),
        ("query_status", {"target_kind": "macro", "target_id": "missing"}),
    ],
)
async def test_unknown_targets_raise_without_publishing(
    hass, coordinator, remote, publish, service, extra
):
    publish.reset_mock()
    with pytest.raises(HomeAssistantError):
        await call(hass, service, {"rs90_id": remote, **extra})
    publish.assert_not_called()


async def test_unknown_remote_raises(hass, remote, publish):
    with pytest.raises(HomeAssistantError):
        await call(hass, "refresh_lists", {"rs90_id": "missing"})
    publish.assert_not_called()


async def test_invalid_actions_are_rejected(hass, coordinator, remote, publish):
    import voluptuous as vol

    await inventory(hass, "macro", [{"id": "m1", "name": "Movie"}])
    publish.reset_mock()
    with pytest.raises((HomeAssistantError, vol.Invalid)):
        await call(
            hass,
            "trigger_macro",
            {"rs90_id": remote, "rs90_macro_id": "m1", "action": "toggle"},
        )
    publish.assert_not_called()


async def test_summary_keeps_duplicate_names_representable(hass, coordinator):
    await inventory(
        hass, "macro", [{"id": "a", "name": "Movie"}, {"id": "b", "name": "Movie"}]
    )
    await inventory(hass, "sequence", [{"id": "s1", "name": "Movie"}])
    sensor = RS90InfoSummarySensor(coordinator, coordinator.entry)
    sensor.hass = hass
    attributes = sensor.extra_state_attributes
    assert attributes["macros_by_id"] == {"a": "Movie", "b": "Movie"}
    assert attributes["sequences_by_id"] == {"s1": "Movie"}
    assert attributes["macros"] == {"Movie": "b"}


async def test_conflict_resolution_requests_new_state(hass, coordinator, publish):
    await inventory(hass, "macro", [{"id": "x", "name": "Real", "type": "macro"}])
    await inventory(hass, "sequence", [{"id": "x", "name": "Sequence"}])
    publish.reset_mock()
    await inventory(hass, "sequence", [])
    assert any(
        c.args[1] == f"{ROOT}/macro/x/currentstatus" for c in publish.call_args_list
    )


async def test_sequence_name_alias_cannot_change_real_macro(hass, coordinator):
    from .test_coordinator import message

    await inventory(hass, "macro", [{"id": "m1", "name": "Movie", "type": "macro"}])
    await inventory(hass, "sequence", [{"id": "s1", "name": "Movie"}])
    # Firmware also publishes sequence status under the historical macro alias.
    await message(hass, "macro/Movie/status", "ON")
    assert coordinator.targets.state("macro", "m1") is None
