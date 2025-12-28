"""Button platform for Haptique RS90 Remote integration."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_REMOTE_ID
from .coordinator import HaptiqueRS90Coordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Haptique RS90 button platform."""
    coordinator: HaptiqueRS90Coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        HaptiqueRS90RGBButton(coordinator, entry),
    ]
    
    async_add_entities(entities)


class HaptiqueRS90RGBButton(CoordinatorEntity, ButtonEntity):
    """Button to trigger RGB Ring Light animation."""

    def __init__(
        self,
        coordinator: HaptiqueRS90Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the RGB button."""
        super().__init__(coordinator)
        self._entry = entry
        self._remote_id = entry.data[CONF_REMOTE_ID]
        
        # Entity configuration
        self._attr_has_entity_name = True
        self._attr_name = "• RGB Ring Light"
        self._attr_unique_id = f"{self._remote_id}_rgb_button"
        self._attr_icon = "mdi:lightbulb-on"
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._remote_id)},
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.data.get("status") == "online"

    async def async_press(self) -> None:
        """Handle button press - trigger RGB with default 5 seconds."""
        _LOGGER.debug("RGB Ring Light button pressed (default 5 seconds)")
        await self.coordinator.async_control_led_light("on", duration=5)
