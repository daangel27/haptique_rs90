"""Use Home Assistant's real coordinator with a simulated MQTT broker."""

from unittest.mock import Mock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState, current_entry
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.haptique_rs90.coordinator import HaptiqueRS90Coordinator


@pytest.fixture(autouse=True)
def custom_integrations(enable_custom_integrations):
    """Allow loading this custom integration."""


@pytest.fixture
async def coordinator(hass, mqtt_mock, mqtt_client_mock):
    entry = MockConfigEntry(
        domain="haptique_rs90",
        unique_id="remote-1",
        data={"remote_id": "remote-1", "name": "Living room"},
        state=ConfigEntryState.SETUP_IN_PROGRESS,
    )
    entry.add_to_hass(hass)
    token = current_entry.set(entry)
    try:
        coordinator = HaptiqueRS90Coordinator(hass, entry)
    finally:
        current_entry.reset(token)
    await coordinator.async_config_entry_first_refresh()
    entry.mock_state(hass, ConfigEntryState.LOADED)
    hass.data.setdefault("haptique_rs90", {})[entry.entry_id] = coordinator
    yield coordinator
    await coordinator.async_shutdown()
    await hass.async_block_till_done()
    await mqtt_mock.async_disconnect()
    # The simulated paho client does not close a real socket on disconnect.
    mqtt_client_mock.on_socket_close(mqtt_client_mock, None, Mock(fileno=lambda: -1))
    await hass.async_block_till_done()


@pytest.fixture
def publish():
    with patch("homeassistant.components.mqtt.async_publish") as mock:
        yield mock
