"""Waking a sleeping RS90 up over the network."""

import asyncio
import json
from unittest.mock import patch

import pytest
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import HomeAssistantError

from custom_components.haptique_rs90 import wake
from custom_components.haptique_rs90.const import CONF_WAKE_AUTO, CONF_WAKE_HOST

from .test_coordinator import message

MACROS = [{"id": "m1", "name": "CANAL", "type": "macro", "supportsOff": True}]


async def _options(hass, entry, data):
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "wake"}
    )
    return await hass.config_entries.options.async_configure(result["flow_id"], data)


async def test_options_validate_and_store(hass, coordinator):
    entry = coordinator.entry
    result = await _options(hass, entry, {CONF_WAKE_HOST: "rs90.lan"})
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_WAKE_HOST: "invalid_ip"}

    result = await _options(
        hass, entry, {CONF_WAKE_HOST: " 192.168.10.245 ", CONF_WAKE_AUTO: True}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_WAKE_HOST] == "192.168.10.245"
    assert coordinator.wake_host == "192.168.10.245"
    assert coordinator.auto_wake

    # Auto-wake makes no sense without an address.
    await _options(hass, entry, {CONF_WAKE_HOST: "", CONF_WAKE_AUTO: True})
    assert coordinator.wake_host is None
    assert not coordinator.auto_wake


async def test_wake_retries_until_online(hass):
    online = asyncio.Event()
    sent = []

    def burst(host):
        sent.append(host)
        if len(sent) == 2:
            hass.loop.call_soon_threadsafe(online.set)

    with (
        patch.object(wake, "_send_burst", burst),
        patch.object(wake, "WAIT_PER_ATTEMPT", 0.05),
        patch.object(wake, "BURST_GAP", 0),
    ):
        assert await wake.async_wake(hass, "192.168.10.245", online, timeout=2)
    assert sent == ["192.168.10.245", "192.168.10.245"]


async def test_wake_gives_up(hass):
    with (
        patch.object(wake, "_send_burst", lambda host: None),
        patch.object(wake, "WAIT_PER_ATTEMPT", 0.02),
        patch.object(wake, "BURST_GAP", 0),
    ):
        assert not await wake.async_wake(hass, "10.0.0.1", asyncio.Event(), 0.1)


async def test_wake_without_address(hass, coordinator):
    with pytest.raises(HomeAssistantError):
        await coordinator.async_wake()


async def test_auto_wake_before_command(hass, coordinator, publish):
    hass.config_entries.async_update_entry(
        coordinator.entry,
        options={CONF_WAKE_HOST: "192.168.10.245", CONF_WAKE_AUTO: True},
    )
    await message(hass, "macro/list", json.dumps(MACROS))
    await message(hass, "status", "offline")

    def burst(host):
        hass.loop.call_soon_threadsafe(
            lambda: hass.async_create_task(message(hass, "status", "online"))
        )

    with (
        patch.object(wake, "_send_burst", burst),
        patch("custom_components.haptique_rs90.coordinator.asyncio.sleep"),
    ):
        await coordinator.async_trigger_target("macro", "m1", "on")
    triggers = [c for c in publish.call_args_list if c.args[1].endswith("/trigger")]
    assert len(triggers) == 1
    assert coordinator.data["status"] == "online"


async def test_no_auto_wake_by_default(hass, coordinator, publish):
    await message(hass, "macro/list", json.dumps(MACROS))
    await message(hass, "status", "offline")
    with patch.object(wake, "_send_burst") as burst:
        await coordinator.async_trigger_target("macro", "m1", "on")
    burst.assert_not_called()
