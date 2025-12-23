"""Unit tests for Haptique RS90 coordinator."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.haptique_rs90.coordinator import HaptiqueRS90Coordinator


@pytest.fixture
def mock_mqtt_client():
    """Mock MQTT client."""
    client = MagicMock()
    client.async_subscribe = AsyncMock()
    client.async_publish = AsyncMock()
    return client


@pytest.fixture
def mock_config_entry():
    """Mock config entry."""
    entry = MagicMock()
    entry.data = {
        "mqtt_topic": "haptique/test",
        "rs90_id": "test_rs90",
        "name": "Test RS90"
    }
    entry.entry_id = "test_entry_id"
    return entry


@pytest.mark.unit
@pytest.mark.asyncio
async def test_coordinator_initialization(hass: HomeAssistant, mock_config_entry, mock_mqtt_client):
    """Test coordinator initialization."""
    with patch("custom_components.haptique_rs90.coordinator.mqtt.async_subscribe"):
        coordinator = HaptiqueRS90Coordinator(hass, mock_config_entry, mock_mqtt_client)
        
        assert coordinator.name == "Test RS90"
        assert coordinator.rs90_id == "test_rs90"
        assert coordinator.data == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_update_data(hass: HomeAssistant, mock_config_entry, mock_mqtt_client):
    """Test data update."""
    coordinator = HaptiqueRS90Coordinator(hass, mock_config_entry, mock_mqtt_client)
    
    # Mock successful data fetch
    coordinator.data = {
        "devices": [{"name": "TV", "id": "device1"}],
        "macros": [{"name": "Movie", "id": "macro1"}]
    }
    
    result = await coordinator._async_update_data()
    
    assert "devices" in result
    assert "macros" in result
    assert len(result["devices"]) == 1
    assert result["devices"][0]["name"] == "TV"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_trigger_macro(hass: HomeAssistant, mock_config_entry, mock_mqtt_client):
    """Test triggering a macro."""
    coordinator = HaptiqueRS90Coordinator(hass, mock_config_entry, mock_mqtt_client)
    
    # Test successful macro trigger
    await coordinator.async_trigger_macro("Movie", "on")
    
    # Verify MQTT publish was called
    mock_mqtt_client.async_publish.assert_called_once()
    call_args = mock_mqtt_client.async_publish.call_args
    
    assert "Movie" in str(call_args)
    assert "on" in str(call_args).lower()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_trigger_device_command(hass: HomeAssistant, mock_config_entry, mock_mqtt_client):
    """Test triggering a device command."""
    coordinator = HaptiqueRS90Coordinator(hass, mock_config_entry, mock_mqtt_client)
    
    # Test successful command trigger
    await coordinator.async_trigger_device_command("TV", "POWER")
    
    # Verify MQTT publish was called
    mock_mqtt_client.async_publish.assert_called_once()
    call_args = mock_mqtt_client.async_publish.call_args
    
    assert "TV" in str(call_args)
    assert "POWER" in str(call_args)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_mqtt_message_callback(hass: HomeAssistant, mock_config_entry, mock_mqtt_client):
    """Test MQTT message handling."""
    coordinator = HaptiqueRS90Coordinator(hass, mock_config_entry, mock_mqtt_client)
    
    # Simulate receiving MQTT message
    test_payload = {
        "devices": [{"name": "TV", "id": "dev1"}],
        "macros": [{"name": "Movie", "id": "mac1"}]
    }
    
    coordinator._handle_mqtt_message(test_payload)
    
    assert coordinator.data["devices"] == test_payload["devices"]
    assert coordinator.data["macros"] == test_payload["macros"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_error_handling(hass: HomeAssistant, mock_config_entry, mock_mqtt_client):
    """Test error handling in coordinator."""
    coordinator = HaptiqueRS90Coordinator(hass, mock_config_entry, mock_mqtt_client)
    
    # Simulate MQTT error
    mock_mqtt_client.async_publish.side_effect = Exception("MQTT Error")
    
    with pytest.raises(Exception):
        await coordinator.async_trigger_macro("Movie", "on")


@pytest.mark.unit
def test_parse_macro_state(hass: HomeAssistant, mock_config_entry, mock_mqtt_client):
    """Test macro state parsing."""
    coordinator = HaptiqueRS90Coordinator(hass, mock_config_entry, mock_mqtt_client)
    
    # Test various state inputs
    assert coordinator._parse_state("on") == "on"
    assert coordinator._parse_state("off") == "off"
    assert coordinator._parse_state("ON") == "on"
    assert coordinator._parse_state("OFF") == "off"
    assert coordinator._parse_state(True) == "on"
    assert coordinator._parse_state(False) == "off"
