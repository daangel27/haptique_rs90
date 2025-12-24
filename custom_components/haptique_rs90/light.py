"""Light platform for Haptique RS90 Remote integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_EFFECT,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
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
    """Set up Haptique RS90 light platform."""
    coordinator: HaptiqueRS90Coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        HaptiqueRS90RGBLight(coordinator, entry),
    ]
    
    async_add_entities(entities)


class HaptiqueRS90RGBLight(CoordinatorEntity, LightEntity):
    """RGB Ring Light control for Haptique RS90."""

    def __init__(
        self,
        coordinator: HaptiqueRS90Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the RGB light."""
        super().__init__(coordinator)
        self._entry = entry
        self._remote_id = entry.data[CONF_REMOTE_ID]
        
        # Entity configuration
        self._attr_has_entity_name = True
        self._attr_name = "• RGB Ring Light"
        self._attr_unique_id = f"{self._remote_id}_rgb_light"
        
        # Light features
        self._attr_supported_color_modes = {ColorMode.ONOFF}
        self._attr_color_mode = ColorMode.ONOFF
        self._attr_supported_features = LightEntityFeature.EFFECT
        
        # Effect list: durations from 1 to 10 seconds
        self._attr_effect_list = [
            "1 second",
            "2 seconds",
            "3 seconds",
            "4 seconds",
            "5 seconds (default)",
            "6 seconds",
            "7 seconds",
            "8 seconds",
            "9 seconds",
            "10 seconds",
        ]
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._remote_id)},
        }

    @property
    def is_on(self) -> bool:
        """Return True if the light is on."""
        return self.coordinator.data.get("led_light_state") == "on"

    @property
    def effect(self) -> str | None:
        """Return the current effect (duration)."""
        duration = self.coordinator.data.get("led_light_duration", 5)
        if duration == 5:
            return "5 seconds (default)"
        return f"{duration} second{'s' if duration > 1 else ''}"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.data.get("status") == "online"

    @property
    def icon(self) -> str:
        """Return icon based on state."""
        return "mdi:lightbulb" if self.is_on else "mdi:lightbulb-outline"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the RGB ring light."""
        # Get duration from effect parameter
        duration = 5  # Default
        
        if ATTR_EFFECT in kwargs:
            effect = kwargs[ATTR_EFFECT]
            # Extract number from effect string (e.g., "5 seconds (default)" -> 5)
            try:
                duration = int(effect.split()[0])
            except (ValueError, IndexError):
                _LOGGER.warning("Invalid effect format: %s, using default duration", effect)
        
        _LOGGER.debug("Turning on RGB light with duration: %d seconds", duration)
        await self.coordinator.async_control_led_light("on", duration=duration)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the RGB ring light."""
        _LOGGER.debug("Turning off RGB light")
        await self.coordinator.async_control_led_light("off")
