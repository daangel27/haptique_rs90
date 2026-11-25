"""RS90 settings published by firmware 4.4 (settings/<name>)."""

from custom_components.haptique_rs90 import select as select_platform
from custom_components.haptique_rs90 import switch as switch_platform

from .test_coordinator import message


async def _entities(hass, coordinator, platform):
    added = []
    await platform.async_setup_entry(hass, coordinator.entry, added.extend)
    return added


def _settings(entities):
    return {e._setting: e for e in entities if hasattr(e, "_setting")}


async def test_no_setting_entity_before_the_topic(hass, coordinator):
    """Firmware 4.3 publishes no settings: nothing is created."""
    assert _settings(await _entities(hass, coordinator, switch_platform)) == {}
    assert _settings(await _entities(hass, coordinator, select_platform)) == {}


async def test_settings_follow_the_rs90(hass, coordinator, publish):
    switches = await _entities(hass, coordinator, switch_platform)
    selects = await _entities(hass, coordinator, select_platform)
    await message(hass, "status", "online")
    await message(hass, "settings/autodisplay", "on")
    await message(hass, "settings/backlight", "off")
    await message(hass, "settings/stay_ready", "30")
    # The RS90 echo on settings/<name>/set is not a value.
    await message(hass, "settings/backlight/set", "on")

    autodisplay = _settings(switches)["autodisplay"]
    backlight = _settings(switches)["backlight"]
    stay_ready = _settings(selects)["stay_ready"]
    assert autodisplay.unique_id == "remote-1_setting_autodisplay"
    assert autodisplay.available and autodisplay.is_on is True
    assert backlight.is_on is False
    assert stay_ready.current_option == "30"
    assert stay_ready.options == ["5", "30", "always"]

    # Changed on the RS90 screen.
    await message(hass, "settings/stay_ready", "5")
    assert stay_ready.current_option == "5"
    # A value a later firmware adds is listed as published.
    await message(hass, "settings/stay_ready", "15")
    assert stay_ready.options == ["5", "30", "always", "15"]

    # Created once only.
    await message(hass, "settings/autodisplay", "off")
    assert len(_settings(switches)) == 2


async def test_changing_a_setting_publishes_set(hass, coordinator, publish):
    switches = await _entities(hass, coordinator, switch_platform)
    selects = await _entities(hass, coordinator, select_platform)
    await message(hass, "status", "online")
    await message(hass, "settings/backlight", "off")
    await message(hass, "settings/stay_ready", "30")

    await _settings(switches)["backlight"].async_turn_on()
    await _settings(selects)["stay_ready"].async_select_option("always")
    sent = [
        (c.args[1], c.args[2], c.kwargs.get("retain")) for c in publish.call_args_list
    ]
    assert ("haptique/remote-1/settings/backlight/set", "on", False) in [
        (t.lower(), p, r) for t, p, r in sent
    ]
    assert ("haptique/remote-1/settings/stay_ready/set", "always", False) in [
        (t.lower(), p, r) for t, p, r in sent
    ]
    # Nothing is assumed: the switch waits for the RS90's answer.
    assert _settings(switches)["backlight"].is_on is False
